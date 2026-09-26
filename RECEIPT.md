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
$ command -v opencli                 # found on PATH
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

### Price table corrected after Stage D

The `claude-api` skill was loaded to check the price table rather than trust memory, and the
built-in table was wrong. It carried opus at $15 input and $75 output per million tokens, which
is a previous generation's Opus pricing, and sonnet at $3 / $15, which is Sonnet 4.6 rather than
Sonnet 5. It also had no row for `claude-opus-5-5`, so those turns were priced as `claude-opus-5`.

Corrected, list prices as of 2026-09-26:

| key | input | output | cache write 5m | cache write 1h | cache read |
|---|---|---|---|---|---|
| opus-5-5 | 4.00 | 20.00 | 5.00 | 8.00 | 0.20 |
| opus | 5.00 | 25.00 | 6.25 | 10.00 | 0.50 |
| sonnet-5 | 2.00 | 10.00 | 2.50 | 4.00 | 0.20 |
| sonnet | 3.00 | 15.00 | 3.75 | 6.00 | 0.30 |
| haiku | 1.00 | 5.00 | 1.25 | 2.00 | 0.10 |

Input and output are published rates. The cache columns are derived from the documented
multipliers: cache read 0.1x input, 5-minute write 1.25x, 1-hour write 2x. The published
exception is Opus 5.5, whose cache read is $0.20, which is 0.05x its input rate. Rows are
matched by substring in the order listed, so `claude-opus-5-5` takes the first row and
`claude-opus-5` the second; a new assert in `demo()` covers that ordering.

Effect on the figures quoted earlier in this receipt: the same three session files now total
**$71.0011**, not $142.9043, and the most expensive single task is **$31.58**, not $49.94. Every
figure on the landing page and in the README was regenerated from the corrected table. The
earlier numbers in the Stage C section above are left as they were recorded at the time; they
were computed with the wrong table and should not be used.

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
$ git rev-parse HEAD
e7d323b52de6c17a4c532a233bdb7afbc086781b

$ git ls-remote origin main
e7d323b52de6c17a4c532a233bdb7afbc086781b

$ gh api repos/az9713/skill-chaining/pages/builds/latest --jq '.status + " " + .commit'
built e7d323b52de6c17a4c532a233bdb7afbc086781b

$ curl -s -o /dev/null -w "%{http_code}" https://az9713.github.io/skill-chaining/
200
```

Local and remote point at the same commit, and the Pages build was produced from that same
commit.

The served page and the committed file differ by line endings only: the working copy is CRLF
on Windows, git stores LF, and GitHub serves the LF blob (live 9,538 bytes, working copy 9,751
bytes). Compared with carriage returns stripped, the two are **identical**, and the live page
carries the corrected figures `31.5785` and `71.0011` and none of the superseded ones.

This receipt was written before its own commit, so the hash of the commit that adds this
section is not in the list above. Everything the acceptance test names is.

### What was not done

1. **The raw Last30Days scan and the raw Reddit and X scrape dumps are not in the repository.**
   Two attempts to copy them in were refused by the auto mode classifier, first as
   `Sensitive-Source Provenance` and then as `Out-of-Place Publication`. Both dumps are bulk
   third-party post text, and committing them to a public repository would republish other
   people's content. The refusals were not worked around. `research/notes.md` carries the
   findings, the counts and the direct links instead.
2. **Assessment A's sections 6 to 8** (the ranked P0 to P3 issue list, the persona red flags
   and the provocative questions) were truncated in transit and never arrived. This is stated
   in `research/impeccable-critique-2026-09-26.md`. The rebuild was driven from sections 1 to 5
   and from Assessment B.
3. **The 1-hour cache write multiplier of 2x** is the documented convention, not a figure read
   off a published page for each model. The two published numbers that were checked, the Opus
   5.5 cache read of $0.20 and the general 0.1x read and 1.25x 5-minute write multipliers, are
   applied as found. Verify against the pricing page before trusting any figure.
