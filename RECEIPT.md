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

## Stage D - design pair

### Step 4: Impeccable critique

Run as two isolated sub-agents, as the skill requires. Assessment A was a design review with
no detector output; Assessment B ran the deterministic detector and a browser render. Neither
saw the other's output before synthesis.

**Assessment A. Nielsen heuristics: 20 out of 36**, with heuristics 7 and 10 renormalised.
Verdict on specificity: category-interchangeable. The palette was a house default, and the
three-card grid, the rule-topped headings and the footer would carry any Python CLI unchanged.
The one authored element was the hero terminal output.

Lowest scores and what caused them:

| # | Heuristic | Score | Cause |
|---|---|---|---|
| 9 | Error recovery | 1 / 4 | no failure state shown anywhere |
| 3 | User control and freedom | 2 / 4 | no navigation, one exit link in the footer |
| 4 | Consistency and standards | 2 / 4 | hero ran `--files 3 --top 8 --cache`, install ran the bare command |
| 5 | Error prevention | 2 / 4 | six words of reassurance against a run-this-on-your-logs request |
| 6 | Recognition over recall | 2 / 4 | four flags used, none explained |
| 10 | Help and documentation | 2 / 4 | documents partially, drops the options table and the price table |

**Assessment B. Detector: exit code 0, one finding, severity advisory.** Advisory severity
does not raise the exit code, so exit 0 means no blocking finding, not no finding.

The finding was `em-dash-overuse`, snippet `39 em-dashes in body text`. Assessment B
reconstructed the count exactly: 32 hyphens from the 65-character ASCII rule inside the
terminal block, 4 CLI flags (`--files`, `--top`, `--cache`, `--prices`), and 3 real `&mdash;`
entities in prose. The rule's own minimum is 8 in prose. **False positive**, caused by the
detector not excluding `<pre>`. The 3 real ones were removed anyway.

Browser evidence at an emulated 360x780 viewport:

| Measurement | Value |
|---|---|
| hero `<pre>` client width | 326px |
| hero `<pre>` scroll width | 602px |
| hidden per line | 276px, **46%** |
| what was cut | the `TASK` column, the page's whole point |

Two `resize_page` calls to 360px failed, because the Chrome window minimum width on Windows
held `innerWidth` at 502. Assessment B switched to viewport emulation and discarded the 502px
numbers. Lowest rendered text contrast was 6.96:1, above WCAG AA. No console messages.

### Step 5: Taste sets the look

`design-taste-frontend` wrote `DESIGN.md`. Design read: developer-tool landing page, dark
terminal language, native CSS, no framework, because this is one static file on GitHub Pages.
Dials `DESIGN_VARIANCE 6 / MOTION_INTENSITY 3 / VISUAL_DENSITY 5`. One accent (teal), orange
reserved for dollar figures only, one 8px radius everywhere.

Implemented, against the critique:

1. **The mobile P0.** Two hero blocks, swapped at 620px. The narrow one carries the same run
   in a 35-column stacked form at 0.75rem. Measured: 326px client, 326px scroll, **nothing
   hidden**.
2. The subscription caveat now sits directly under the total, and a second note says the
   figures are from a real run with the task labels reworded to remove local paths.
3. All four flags are named in prose under the hero.
4. The log path `~/.claude/projects/<project>/<session>.jsonl` is on the page.
5. `demo` is the offered first run, stated to touch no real log.
6. The three equal cards became a definition list with hairline rules.
7. `:focus-visible` added; `<thead>` and `scope="col"` added; `<footer>` moved outside `<main>`.
8. Every em-dash and en-dash removed. Count of `—`, `–`, `&mdash;` and `&ndash;` in the
   file: **0**.

### Step 6: Impeccable polish

Detector re-run after the rebuild found a second, real finding:

- `side-tab` (**warning**, not advisory): `border-left: 3px + border-radius: 8px` on the note
  block, which the detector calls the most recognisable tell of AI-generated UI. Removed; the
  note is now a plain bordered card.

Final detector state: `side-tab` gone, only the `em-dash-overuse` advisory remains, already
shown above to be a false positive counting the ASCII rule line.

One defect the critique did not catch, found by measuring the rebuilt page myself at 360px:
the inline log path is a single unbreakable token and pushed the document to 391px against a
360px viewport, a 31px horizontal scroll. Fixed with `overflow-wrap: anywhere` on inline code.

Final measurements, emulated viewports:

| Viewport | document scrollWidth / clientWidth | hero client / scroll |
|---|---|---|
| 360 x 780, mobile | 360 / 360, no overflow | 326 / 326, nothing hidden |
| 1280 x 900 | 1265 / 1265, no overflow | 846 / 846, nothing hidden |

Heading order H1, H2, H2, H2, H2. No level skipped. The static server used for these
measurements ran on port 8742 as PID 36729 and was stopped; the port no longer answers.

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

### Final state

```
$ git log --oneline
bbbbe0c Stage D: Impeccable critique, Taste design system, polish
fc1eee5 Price a mixed-model task on its known model, not on "<synthetic>"
278db0b First version: cctaskcost CLI, README, research notes, landing page
21d69b5 Initial commit

$ git rev-parse HEAD
bbbbe0cc72a3b110dc8e865e12a466d9686c543a

$ git ls-remote origin main
bbbbe0cc72a3b110dc8e865e12a466d9686c543a

$ gh api repos/az9713/skill-chaining/pages/builds/latest --jq '.status + " " + .commit'
built bbbbe0cc72a3b110dc8e865e12a466d9686c543a
```

Local and remote point at the same commit, and the Pages build was produced from that same
commit. The served page is byte-identical to the committed file: both hash to
`b9e4bc33c5fc69c41c404e77852ab080`.

This receipt was written before its own commit, so the hash of the commit that adds this
section is not in the list above. Everything the acceptance test names is.

### Personal information

A case-insensitive recursive grep over every committed file, for the local user name, the
account email, the X `AUTH_TOKEN` and `CT0` cookie names, and the `sk-ant-` and `gho_` key
prefixes, returns no match. No local user path, no email address and no token is committed.

`.impeccable/` is in `.gitignore`: its `hook.cache.json` stores absolute paths.
