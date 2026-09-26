#!/usr/bin/env python3
"""cctaskcost — token cost per task, from local Claude Code session logs.

Existing monitors total a session, a day or a 5-hour block. This one totals a
single prompt, so you can see which task spent the budget.

How the grouping works: in a session .jsonl, every `user` record carries a
`promptId`, and every tool result in the same turn repeats it. `assistant`
records carry `message.usage` but no `promptId`, so each one is charged to the
most recent promptId seen in file order.

Read-only. Nothing leaves the machine.
"""

import argparse
import json
import os
import sys
from pathlib import Path

# List prices in US dollars per million tokens.
# cw5 = cache write, 5-minute TTL. cw1h = cache write, 1-hour TTL. cr = cache read.
# Override the whole table with --prices prices.json when prices change.
PRICES = {
    "opus":   {"in": 15.0, "out": 75.0, "cw5": 18.75, "cw1h": 30.0, "cr": 1.50},
    "sonnet": {"in": 3.0,  "out": 15.0, "cw5": 3.75,  "cw1h": 6.0,  "cr": 0.30},
    "haiku":  {"in": 1.0,  "out": 5.0,  "cw5": 1.25,  "cw1h": 2.0,  "cr": 0.10},
}
UNKNOWN_MODEL_RATE = PRICES["sonnet"]  # ponytail: mid-tier guess, flagged in output


def rate_for(model, prices):
    """Pick a price row by substring. Returns (rate, matched) so the caller can flag guesses."""
    name = (model or "").lower()
    for key, row in prices.items():
        if key in name:
            return row, True
    return UNKNOWN_MODEL_RATE, False


class Task:
    __slots__ = ("prompt_id", "text", "session", "started", "turns",
                 "inp", "out", "cw5", "cw1h", "cr", "models", "guessed")

    def __init__(self, prompt_id, text, session, started):
        self.prompt_id = prompt_id
        self.text = text
        self.session = session
        self.started = started
        self.turns = 0
        self.inp = self.out = self.cw5 = self.cw1h = self.cr = 0
        self.models = set()
        self.guessed = False

    def add(self, usage, model):
        self.turns += 1
        self.models.add(model or "unknown")
        self.inp += usage.get("input_tokens", 0) or 0
        self.out += usage.get("output_tokens", 0) or 0
        self.cr += usage.get("cache_read_input_tokens", 0) or 0
        made = usage.get("cache_creation") or {}
        if made:
            self.cw5 += made.get("ephemeral_5m_input_tokens", 0) or 0
            self.cw1h += made.get("ephemeral_1h_input_tokens", 0) or 0
        else:
            self.cw5 += usage.get("cache_creation_input_tokens", 0) or 0

    def cost(self, prices):
        total = 0.0
        for model in self.models:
            rate, matched = rate_for(model, prices)
            if not matched:
                self.guessed = True
        # One model dominates a task in practice; price the whole task on the first.
        rate, _ = rate_for(sorted(self.models)[0] if self.models else "", prices)
        total += self.inp * rate["in"]
        total += self.out * rate["out"]
        total += self.cw5 * rate["cw5"]
        total += self.cw1h * rate["cw1h"]
        total += self.cr * rate["cr"]
        return total / 1_000_000

    def billed_tokens(self):
        return self.inp + self.out + self.cw5 + self.cw1h + self.cr

    def cache_read_share(self):
        charged = self.inp + self.cw5 + self.cw1h + self.cr
        return (self.cr / charged * 100) if charged else 0.0


def prompt_text(message):
    """First readable line of a user prompt, or '' when the record is a tool result."""
    content = message.get("content")
    if isinstance(content, str):
        text = content
    elif isinstance(content, list):
        parts = [b.get("text", "") for b in content
                 if isinstance(b, dict) and b.get("type") == "text"]
        if not parts:
            return ""  # tool_result / image only: same turn, not a new task
        text = "\n".join(parts)
    else:
        return ""
    for line in text.splitlines():
        line = line.strip()
        if line:
            return line
    return ""


def parse_file(path, tasks, order):
    """Fold one session .jsonl into `tasks`. Malformed lines are skipped."""
    session = Path(path).stem
    current = None
    with open(path, encoding="utf-8", errors="replace") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            kind = rec.get("type")
            if kind == "user":
                pid = rec.get("promptId")
                if not pid:
                    continue
                key = (session, pid)
                if key not in tasks:
                    tasks[key] = Task(pid, prompt_text(rec.get("message") or {}),
                                      session, rec.get("timestamp") or "")
                    order.append(key)
                elif not tasks[key].text:
                    tasks[key].text = prompt_text(rec.get("message") or {})
                current = key
            elif kind == "assistant" and current is not None:
                message = rec.get("message") or {}
                usage = message.get("usage")
                if usage:
                    tasks[current].add(usage, message.get("model"))
    return tasks


def find_logs(root, session=None, project=None):
    root = Path(root).expanduser()
    if root.is_file():
        return [root]
    files = sorted(root.glob("*/*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)
    if project:
        files = [f for f in files if project.lower() in f.parent.name.lower()]
    if session:
        files = [f for f in files if f.stem.startswith(session)]
    return files


def shorten(text, width):
    text = " ".join(text.split())
    return text if len(text) <= width else text[: width - 1] + "…"


def human(n):
    for unit, size in (("M", 1_000_000), ("k", 1_000)):
        if n >= size:
            return f"{n / size:.1f}{unit}"
    return str(n)


def report(rows, prices, width, show_cache):
    head = f"{'COST':>9}  {'TOKENS':>8}  {'TURNS':>5}"
    if show_cache:
        head += f"  {'CACHED':>6}"
    head += "  TASK"
    lines = [head, "-" * len(head)]
    for task in rows:
        cost = task.cost(prices)
        cell = f"${cost:>8.4f}  {human(task.billed_tokens()):>8}  {task.turns:>5}"
        if show_cache:
            cell += f"  {task.cache_read_share():>5.0f}%"
        label = shorten(task.text or "(no prompt text)", width)
        if task.guessed:
            label = "[?price] " + label
        lines.append(f"{cell}  {label}")
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(
        prog="cctaskcost",
        description="Token cost per task from Claude Code session logs.")
    ap.add_argument("--logs", default="~/.claude/projects",
                    help="log root, or one .jsonl file (default: ~/.claude/projects)")
    ap.add_argument("--project", help="only projects whose folder name contains this")
    ap.add_argument("--session", help="only sessions whose id starts with this")
    ap.add_argument("--files", type=int, default=5,
                    help="how many of the newest session files to read (default: 5)")
    ap.add_argument("--top", type=int, default=20, help="rows to print (default: 20)")
    ap.add_argument("--sort", choices=["cost", "time"], default="cost")
    ap.add_argument("--width", type=int, default=64, help="task column width")
    ap.add_argument("--cache", action="store_true",
                    help="add a column: share of charged input that was a cache read")
    ap.add_argument("--prices", help="JSON file replacing the built-in price table")
    ap.add_argument("--json", action="store_true", dest="as_json")
    args = ap.parse_args(argv)

    prices = PRICES
    if args.prices:
        prices = json.loads(Path(args.prices).read_text(encoding="utf-8"))

    files = find_logs(args.logs, args.session, args.project)
    if not files:
        print(f"no session logs under {args.logs}", file=sys.stderr)
        return 1
    files = files[: args.files]

    tasks, order = {}, []
    for path in files:
        parse_file(path, tasks, order)

    rows = [tasks[k] for k in order if tasks[k].turns]
    if args.sort == "cost":
        rows.sort(key=lambda t: t.cost(prices), reverse=True)
    else:
        rows.sort(key=lambda t: t.started)
    rows = rows[: args.top]

    if args.as_json:
        print(json.dumps([{
            "session": t.session,
            "prompt_id": t.prompt_id,
            "started": t.started,
            "prompt": t.text,
            "turns": t.turns,
            "input_tokens": t.inp,
            "output_tokens": t.out,
            "cache_write_5m_tokens": t.cw5,
            "cache_write_1h_tokens": t.cw1h,
            "cache_read_tokens": t.cr,
            "cost_usd": round(t.cost(prices), 6),
            "models": sorted(t.models),
        } for t in rows], indent=2))
        return 0

    print(f"{len(files)} session file(s), {len(rows)} task(s) shown\n")
    print(report(rows, prices, args.width, args.cache))
    total = sum(t.cost(prices) for t in rows)
    print(f"\ntotal shown: ${total:.4f}   (list prices; edit with --prices)")
    return 0


def demo():
    """Self-check: the one thing that breaks if the grouping logic breaks."""
    import tempfile

    lines = [
        # task 1: prompt, one assistant turn, a tool result, a second assistant turn
        {"type": "user", "promptId": "p1", "timestamp": "t0",
         "message": {"role": "user", "content": "fix the parser"}},
        {"type": "assistant", "message": {"model": "claude-opus-5", "usage": {
            "input_tokens": 10, "output_tokens": 100,
            "cache_read_input_tokens": 1000,
            "cache_creation": {"ephemeral_1h_input_tokens": 200,
                               "ephemeral_5m_input_tokens": 0}}}},
        {"type": "user", "promptId": "p1",
         "message": {"role": "user", "content": [{"type": "tool_result"}]}},
        {"type": "assistant", "message": {"model": "claude-opus-5", "usage": {
            "input_tokens": 0, "output_tokens": 50, "cache_read_input_tokens": 0}}},
        # task 2: a different prompt in the same file
        {"type": "user", "promptId": "p2", "timestamp": "t1",
         "message": {"role": "user", "content": "now write the docs"}},
        {"type": "assistant", "message": {"model": "claude-haiku-4-5", "usage": {
            "input_tokens": 1000, "output_tokens": 10}}},
        {"type": "nonsense"},
    ]
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "sess.jsonl"
        path.write_text("\n".join(json.dumps(x) for x in lines) + "\nnot json\n",
                        encoding="utf-8")
        tasks, order = {}, []
        parse_file(path, tasks, order)

    assert len(order) == 2, order
    one, two = tasks[order[0]], tasks[order[1]]

    # the tool result did NOT start a third task, and its turn stayed on task 1
    assert one.turns == 2, one.turns
    assert one.text == "fix the parser", one.text
    assert two.turns == 1, two.turns
    assert two.text == "now write the docs", two.text

    # token classes land in the right buckets
    assert (one.inp, one.out, one.cr, one.cw1h, one.cw5) == (10, 150, 1000, 200, 0)

    # opus list price: 10*15 + 150*75 + 200*30 + 1000*1.50 per million
    expected = (10 * 15.0 + 150 * 75.0 + 200 * 30.0 + 1000 * 1.50) / 1_000_000
    assert abs(one.cost(PRICES) - expected) < 1e-12, (one.cost(PRICES), expected)

    # haiku is priced as haiku, not as the default
    assert abs(two.cost(PRICES) - (1000 * 1.0 + 10 * 5.0) / 1_000_000) < 1e-12

    # an unknown model is priced, but flagged
    three = Task("p3", "x", "s", "t")
    three.add({"input_tokens": 1_000_000}, "some-other-model")
    three.cost(PRICES)
    assert three.guessed is True

    # cache share
    assert abs(one.cache_read_share() - (1000 / 1210 * 100)) < 1e-9

    print("demo: ok")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        demo()
    else:
        sys.exit(main())
