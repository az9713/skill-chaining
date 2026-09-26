# Impeccable critique of `docs/index.html`, 2026-09-26

Run as two isolated sub-agents, which is what the skill requires. Assessment A is a design
review with no detector output. Assessment B is the deterministic detector plus browser
evidence. Neither saw the other before synthesis.

Target at the time of the critique: the first version of `docs/index.html`, 101 lines.

**What is missing from this file.** Assessment A's sections 6 to 8, the ranked P0 to P3 issue
list, the persona red flags and the provocative questions, were truncated in transit and never
arrived. Sections 1 to 5 below are as received. The fixes were driven from sections 1 to 5 and
from Assessment B, so nothing in the rebuild depended on the missing part.

---

# Assessment A: design review, unanchored

Surface mode: Persuade. Reviewer role: design director. No detector was run.

## 1. Design specificity verdict

**Category-interchangeable, with one authored element.**

The colour tokens at `index.html:10-13` are the author's standing dark-mode defaults, copied
without change: `--bg: #0f172a`, `--card: #1e293b`, `--text: #e2e8f0`, `--text2: #cbd5e1`,
`--muted: #94a3b8`, `--orange: #fb923c`, `--teal: #2dd4bf`, `--line: #334155`. Line 6 adds
`<meta name="color-scheme" content="dark">`. These are house defaults, not choices made for a
cost tool.

The reusable parts are the three-card grid (`65-69`), the `h2` with `border-top` (`19-20`),
the table (`31-33`), and the footer (`95-98`). Replace the `<pre>` block and the Reddit list,
and this page ships as a landing page for any Python CLI.

The one authored element is the hero `<pre>` at `43-58`. It is real terminal output. Row `49`
states the whole product claim in one line. Nothing else on the page could only belong to
`cctaskcost`.

Answer to the question asked: yes. An unrelated dev tool could use this composition unchanged,
after swapping lines `43-58` and `72-79`.

## 2. Nielsen's 10 heuristics

| # | Heuristic | Score | Key issue |
|---|---|---|---|
| 1 | Visibility of system status | 3/4 | The hero shows real output, the clearest possible statement of what the tool does; the page never names the log path `~/.claude/projects` that it reads. |
| 2 | Match between system and the real world | 3/4 | Plain language throughout (`40-41`), but `total shown: $142.9043` at line `58` is not what a subscription holder pays. |
| 3 | User control and freedom | 2/4 | No navigation. The only exit is the GitHub link in the footer at line `97`. |
| 4 | Consistency and standards | 2/4 | The hero runs `--files 3 --top 8 --cache` (line `43`); Install runs bare `python cctaskcost.py` (line `93`). The two produce different output. |
| 5 | Error prevention | 2/4 | The page asks the reader to run a script against their own session logs (`91-93`), and offers 6 words of reassurance at line `67`. |
| 6 | Recognition rather than recall | 2/4 | Lines `43` and `58` use `--files`, `--top`, `--cache` and `--prices`; the page explains none of the four. |
| 7 | Flexibility and efficiency of use | n/a | Static page, no interaction, no state, no path to accelerate for a repeat visitor. |
| 8 | Aesthetic and minimalist design | 3/4 | 101 lines, no JavaScript, one idea per section, but the hero table overflows on a phone. |
| 9 | Help users recognise and recover from errors | 1/4 | The page shows no failure state: no logs found, unknown model, or wrong Python version. |
| 10 | Help and documentation | 2/4 | The page takes on documentation duty and drops most of it. |

**Renormalised total: 20 / 36.**

Note on heuristic 7: the page has no controls, no forms, and no persisted state. There is
nothing for a repeat visitor to do faster.

Note on heuristic 10, scored rather than n/a: the page chooses to document. It carries an
Install block (`90-93`) and an attribution table (`82-87`). It then drops, from a README that
contains them: the full option table, the `CACHED` column explanation, the price table, the
`python cctaskcost.py demo` self-check, and the Python 3.8 requirement. A page that documents
partially scores worse than a page that does not document at all, because the reader cannot
tell which part is missing.

## 3. Cognitive load

No decision point has more than 4 visible options. The page offers two actions in total: click
the GitHub link (line `97`), or copy the install block (`91-93`). That is correct for Persuade
mode. No over-choice problem.

**One scanability failure, at the most important element.** The hero `<pre>` at `43-58` is a
fixed-width table about 65 columns wide, at `.82rem` (line `27`) inside a container with
`overflow-x: auto` (line `26`). At a 16px root that is roughly 13.1px, and a monospace
character is about 0.6em wide, so the block needs about 510px. A 375px phone gives about 343px
inside the 16px page padding (line `17`).

The result: the `TASK` column falls off the right edge. The `TASK` column is the punchline. A
reader arriving from one of the three Reddit links (`74`, `76`, `78`) is likely to be on a
phone. That reader sees the cost, the tokens, the turns and the cached share, and no task name.
The page's single authored element fails silently on mobile.

Second, smaller load problem: the attribution table at `82-87` uses the term `promptId` three
times. The page never shows the log file path, so the reader cannot picture where a `promptId`
lives. The README states the path at `README.md:54` and the page drops it.

## 4. Emotional journey

**Peak:** line `49`. One row proves the thesis: a small-sounding task spent tens of dollars. No
prose on the page works as hard.

**First valley:** lines `81-88`, "How the attribution works". Mechanism arrives before action.
The reader is persuaded by line `63` and must then read a three-row table about record types
before reaching Install at line `90`.

**Second valley:** line `58`, the total. A reader on a $20 per month plan compares the total to
$20 and concludes the tool is wrong. The README states the correction plainly at
`README.md:115-116`: a subscription plan does not bill per token, so read the figure as what
the task would have cost on the API. The page omits that sentence.

**The high-stakes moment is under-served.** The ask is: clone a repo and run a Python script
against your own Claude Code session logs, which contain your prompts. The page's answer is one
card at line `67`, six words. Three available reassurances were dropped:

1. `README.md:27`, "no telemetry".
2. The `cctaskcost.py` docstring, "Read-only. Nothing leaves the machine."
3. `README.md:121`, `python cctaskcost.py demo`, a self-check that builds a session log in a
   temporary folder. It is a safe first run that touches no real log. It is the single best
   answer to "is this safe", and the page does not mention it.

**End:** line `96`, a licence string. The peak-end rule says the last thing read carries
disproportionate weight. The page should end on the install, or on the safety statement.

## 5. Strengths

1. **The hero is real output, not a mockup** (`43-58`). Every number is checkable against the
   tool's own code: the `CACHED` column is computed by `cache_read_share()`, and the `[?price]`
   flag exists in `report()`. Mockups do not survive that test; this does.
2. **The proof is third-party and linked** (`72-79`). Three quotes, three live Reddit URLs,
   somebody else's pain stated in their words, with links a sceptic can open. A landing page
   that praises itself is ignored. This one hands the reader the evidence.
3. **The page's restraint matches the product's claim** (whole file).

*(Sections 6 to 8 truncated in transit and never received.)*

---

# Assessment B: detector and browser evidence

## Detector

Command, run from the repository root:

```
impeccable detect --json docs/index.html
```

**Exit code 0. Finding count 1.** Advisory severity does not raise the exit code, so exit 0
means "no blocking findings", not "no findings".

| Severity | Count |
|---|---|
| critical | 0 |
| high | 0 |
| medium | 0 |
| low | 0 |
| advisory | 1 |
| **total** | **1** |

One rule fired: `em-dash-overuse` ("Em-dash overuse"), severity `advisory`, category `slop`,
`advisory: true`, line 0, snippet `39 em-dashes in body text`. The rule's stated threshold is
at least 8 em-dashes at a density near one per 500 characters of body text.

## False positive: `em-dash-overuse`

The count was reconstructed exactly.

- Total `--` pairs in the file: **59**
- Inside `<style>`, as CSS custom-property names: **23**. The detector strips these.
- Inside `<pre>`: **36**. Of those, **32** come from one ASCII rule line of 65 hyphens at
  `docs/index.html:48`. The other **4** are the CLI flags `--files`, `--top`, `--cache`,
  `--prices`.
- `&mdash;` entities in prose: **3**, at lines 73, 75, 77.
- Literal U+2014 characters: **0**.

36 + 3 = 39, which matches the snippet exactly. The real prose em-dash count is **3**, against
the rule's own minimum of 8. Body text measures about 2,097 characters, so 3 em-dashes is one
per 699 characters, below the stated trigger of one per 500. The rule would not fire if the
detector excluded `<pre>` content.

**Verdict: 1 of 1 findings is a false positive.** Zero actionable detector findings.

## Browser step

A browser automation tool was exposed, so it was used; no hand-rolled Playwright or Puppeteer.

1. Started a static server on `127.0.0.1:8731` from `docs/`, PID captured.
2. Opened the page, measured at 360x780 and at 1280x900.
3. Closed the page, stopped the captured PID, confirmed the process gone and the port closed.

**One failed sub-step, reported for accuracy.** Two `resize_page` calls to width 360 had no
effect: `window.innerWidth` stayed at **502** both times, which is the Chrome window minimum
width on Windows. Viewport emulation at `360x780x2,mobile,touch` set `innerWidth` to 360, and
all 360px numbers come from that path. The 502px measurements were discarded.

Console messages: **none**, at either width.

## Source-read observations

**Viewport meta:** present at line 5. `color-scheme: dark` at line 6, `lang="en"` at line 2.

**Horizontal scroll at 360px:** none. `documentElement.scrollWidth` 360, `clientWidth` 360,
`body.scrollWidth` 360.

**Fixed px width over 360:** none declared. Only `max-width: 900px` on `main` and
`minmax(220px, 1fr)` on the grid, which collapses to one 328px column. The two boxes measuring
over 360 (602px and 361px) are intrinsic `<code>` content, not declared widths.

**`<pre>` overflow on a phone:** yes, both blocks, contained by `overflow-x: auto`.

| Block | clientWidth | scrollWidth | hidden |
|---|---|---|---|
| hero, lines 43-58 | 326 | 602 | 276px, **46% of each line** |
| install, lines 91-93 | 326 | 361 | about 35px |

The screenshot shows the `TASK` column cut to "add a t", "run sta", "turn on". The clone URL
truncates mid-string.

**Contrast:** no text pair below 4.5:1. Computed on the live page: text on background 14.48,
secondary text on background 12.02, secondary on the panel 12.59, accent on background 9.59,
secondary on card 9.85, muted on background 6.96, muted on card 5.71 (not rendered). Lowest
rendered text pair is **6.96:1**.

Non-text pairs, numbers only, no verdict, since 1.4.11's 3:1 covers UI component boundaries and
a decorative border is exempt: line on background 1.72:1, line on card 1.41:1, card on
background 1.22:1.

`--orange #fb923c` is declared but never rendered: `code` sets it, `pre code` overrides it, and
both `<code>` elements sit inside `<pre>`. No inline code exists in the prose.

**Other:** heading order H1, H2, H2, H2, H2, no level skipped. 0 images. The table uses `<th>`
but has no `<thead>`, no `<caption>` and no `scope`. No `:focus` or `:focus-visible` rule
anywhere in the stylesheet. `<footer>` sits inside `<main>`, so it is not a top-level
`contentinfo` landmark. No `<nav>`.
