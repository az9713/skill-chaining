# RECEIPT — Stages A to E

Run 2026-09-26. Every command below was run as written; local paths are shortened to `~`.
Raw scrape dumps from Stage B are **not** committed: they are bulk third-party post text,
and publishing them here would republish other people's content. `research/notes.md` keeps
the findings, the counts and the direct links instead.

---

## Stage A — compression pair on

`headroom wrap claude` was already active for this session, started as
`HEADROOM_TPM=2000000 headroom wrap claude --1m`. `/i-have-adhd` was typed by the user as
the first message of the session.

```
$ curl -s http://127.0.0.1:8787/stats
```

Evidence from that response:

| field | value |
|---|---|
| `requests.rate_limited_by_source.headroom` | `0` |
| `requests.rate_limited_by_source.upstream` | `1` |
| `rate_limiter.tokens_per_minute` | `2000000` |
| `summary.primary_model` | `claude-opus-5` |
| `persistent_savings.lifetime.requests` | `132` |
| `persistent_savings.lifetime.tokens_saved` | `105809` |

Zero Headroom rate-limit refusals. The 2,000,000 tokens-per-minute setting is the fix for
the 2026-09-25 stall, where the default 100,000 refused every request.

---

## Stage B — research pair

### Wide scan (Last30Days)

Not re-run. The 2026-09-25 output was reused, as the handoff directed:
`~/Documents/Last30Days/ai-coding-agents-token-cost-and-context-limits-raw-v3.md`,
14,068 bytes, 191 lines. Window 2026-08-27 → 2026-09-26. 117 evidence items across six
sources (Reddit 35, Hacker News 25, GitHub 21, X 17, Digg 11, Techmeme 8). arXiv timed out.

### Targeted fetch (Agent Reach)

Backend check:

```
$ agent-reach doctor --json          # ran; OpenCLI adapters present
$ command -v opencli                 # ~/AppData/Roaming/npm/opencli
$ command -v twitter                 # MISSING
$ command -v bird                    # MISSING
```

The `twitter` and `bird` CLIs named in the handoff are not installed. X was reached through
the OpenCLI `twitter` adapter instead, which uses the logged-in browser session. Reddit was
reached through the OpenCLI `reddit` adapter.

```
$ opencli reddit search "Claude Code token usage per task cost" -f md --limit 25   # exit 0, 25 rows
$ opencli reddit search "which task used my tokens Claude Code" -f md --limit 25   # exit 0, 25 rows
$ opencli reddit search "ccusage token cost tracking Claude Code" -f md --limit 25 # exit 0, 25 rows
$ opencli twitter search "Claude Code token cost per task" -f md --limit 20        # exit 0, 20 rows
```

No platform failed. Nothing was retried.

### Existence check (GitHub)

```
$ gh search repos "claude code token usage cost" --sort stars --limit 15
$ gh search repos "claude code session cost per task" --limit 15
$ gh search repos "claude code per prompt token attribution" --limit 10
$ gh search repos "claude code compare token savings before after" --limit 10
```

The first search returned 15 repositories, the top seven of which are in the table in
`research/notes.md`. Every one is a session, day or live monitor. The other three searches
returned **zero** repositories.

Decision: build per-prompt cost attribution. Written up in `research/notes.md`.

---

## Stage C — repository and tool

```
$ rmdir ~/Downloads/skill-chaining/research && rmdir ~/Downloads/skill-chaining
stray removed

$ gh repo create az9713/skill-chaining --public --clone --add-readme --license mit
https://github.com/az9713/skill-chaining
Cloning into 'skill-chaining'...
```

Log format confirmed first-hand before writing any code, by reading a real session file:

- `user` records carry `promptId`; tool results repeat the same `promptId`.
- `assistant` records carry `message.usage` and **no** `promptId`.
- `usage` splits into `input_tokens`, `output_tokens`, `cache_read_input_tokens` and
  `cache_creation.ephemeral_5m_input_tokens` / `ephemeral_1h_input_tokens`.

Built: `cctaskcost.py` (one file, standard library only), `README.md`, `docs/index.html`,
`research/notes.md`.

Self-check:

```
$ python cctaskcost.py demo
demo: ok
```

It asserts that a tool result does not open a new task, that the five token classes land in
the right buckets, that each model is priced from its own row, and that an unknown model is
priced but flagged.

Real run against local logs:

```
$ python cctaskcost.py --files 3 --top 8 --cache --width 52
3 session file(s), 8 task(s) shown
...
total shown: $142.9043   (list prices; edit with --prices)
```

The most expensive single task in three session files cost $49.94 and used 8.9M billed
tokens across 42 assistant turns, with 86% of its charged input served from cache. That is
the number a per-session total hides.

---

## Stage D — design pair

<!-- filled in below -->

---

## Stage E — publish

```
$ git add -A && git commit   # "First version: cctaskcost CLI, README, research notes, landing page"
278db0b

$ git push origin main
   21d69b5..278db0b  main -> main

$ gh api repos/az9713/skill-chaining/pages -X POST -f "source[branch]=main" -f "source[path]=/docs"
{"html_url":"https://az9713.github.io/skill-chaining/","source":{"branch":"main","path":"/docs"},"public":true,"https_enforced":true}

$ gh api repos/az9713/skill-chaining/pages/builds/latest --jq '{status,error:.error.message}'
{"error":null,"status":"built"}

$ curl -s -o /dev/null -w "%{http_code}" https://az9713.github.io/skill-chaining/
200
```

The served page is byte-identical to the committed file: both hash to
`10f409876c6cf710ececea8a2f0c8ca9`.

### Personal information

```
$ grep -rniE 'NAME|az9713@|yahoo|AUTH_TOKEN|CT0|sk-ant|gho_' --exclude-dir=.git .
(no matches)
```

No local user path, no email address, no token in any committed file.
