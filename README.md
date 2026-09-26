# cctaskcost

**Which task spent your token budget?** `cctaskcost` reads the Claude Code session logs
already on your disk and prints the cost of **one prompt at a time**.

```
python cctaskcost.py --files 3 --top 8 --cache
```

```
3 session file(s), 8 task(s) shown

     COST    TOKENS  TURNS  CACHED  TASK
-----------------------------------------------------------------
$ 31.5785     37.9M    186     97%  run stages A-E, output a receipt
$ 16.6463      8.9M     42     86%  add a timeout to the flaky test
$  7.2387      1.2M      5     40%  turn on Pages for the docs folder
$  6.8380      1.5M      7     57%  check the example is complete
$  3.6085      5.4M     19     99%  add two allow rules
$  2.4088    713.0k      8     72%  read the handoff and summarise it
$  1.4068    139.4k      2      0%  /i-have-adhd
$  1.2755      1.2M     14     90%  rename the repo, update the links

total shown: $71.0011   (list prices; edit with --prices)
```

Read-only. No API key, no network call, no telemetry.

Every figure above is from one real run. The task labels were shortened and reworded, because
the originals held local file paths.

## The problem, in the words of the people who have it

- **"Per-turn token and cost tracking for Claude Code"** is the request, stated plainly.
  [r/ClaudeCode](https://www.reddit.com/r/ClaudeCode/comments/1vhjxrw/perturn_token_and_cost_tracking_for_claude_code/)
- **"Claude Code Cloud Sessions: one 58-minute task showed $34.38 cost on $20/month Pro
  plan — what exactly is …"**
  [r/ClaudeCode](https://www.reddit.com/r/ClaudeCode/comments/1wqjjcf/claude_code_cloud_sessions_one_58minute_task/)
- **"I benchmarked 5 token saving tools across Codex and Claude Code. 60-90% token-saving
  claims didn't hold up."** 41 points, 27 comments, and reposted into three other
  subreddits inside one month.
  [r/ClaudeCode](https://www.reddit.com/r/ClaudeCode/comments/1vilwwm/i_benchmarked_5_token_saving_tools_across_codex/)

The full research, with counts and the rest of the links, is in
[`research/notes.md`](research/notes.md).

## Why another usage tool

`ccusage` and the other monitors total a **session**, a **day** or a **5-hour block**. That
answers "how much did today cost". It does not answer "which of today's eleven prompts cost
$50". Seven comparable repositories were checked on 2026-09-26; every one describes itself
as a session, day or live monitor. Three GitHub searches for per-prompt attribution returned
no repositories at all.

## How the attribution works

In `~/.claude/projects/<project>/<session>.jsonl`:

| record | carries `promptId` | carries `message.usage` |
|---|---|---|
| `user` (your prompt) | yes | no |
| `user` (a tool result) | yes, the **same** one | no |
| `assistant` | **no** | yes |

So each `assistant` record is charged to the most recent `promptId` seen in file order. A
tool result does not open a new task, because it repeats the `promptId` of the prompt that
caused it. That one grouping step is the whole tool.

## Install

Python 3.8 or later. No dependencies.

```
git clone https://github.com/az9713/skill-chaining
cd skill-chaining
python cctaskcost.py
```

## Options

| Flag | Effect |
|---|---|
| `--logs PATH` | log root, or one `.jsonl` file. Default `~/.claude/projects` |
| `--project NAME` | only projects whose folder name contains `NAME` |
| `--session ID` | only sessions whose id starts with `ID` |
| `--files N` | read the `N` newest session files. Default 5 |
| `--top N` | print `N` rows. Default 20 |
| `--sort cost\|time` | order the rows. Default `cost` |
| `--cache` | add the share of charged input that was a cache read |
| `--prices FILE` | replace the built-in price table with your own JSON |
| `--json` | print every token class as JSON instead of a table |
| `--width N` | task column width. Default 64 |

## The `CACHED` column

It is the share of charged input tokens that were cache **reads**. A cache read costs about
a tenth of a fresh input token, so a high number is a cheap task and a low number is an
expensive one. It is there because the loudest complaint in the research was that nobody can
check a token-saving claim. This column is checkable.

## Prices

The built-in table holds Anthropic first-party API list prices in US dollars per million
tokens, **as of 2026-09-26**. Check them against the pricing page before you trust a figure;
they change, and this table does not update itself.

| family | input | output | cache write 5m | cache write 1h | cache read |
|---|---|---|---|---|---|
| opus-5-5 | 4.00 | 20.00 | 5.00 | 8.00 | 0.20 |
| opus | 5.00 | 25.00 | 6.25 | 10.00 | 0.50 |
| sonnet-5 | 2.00 | 10.00 | 2.50 | 4.00 | 0.20 |
| sonnet | 3.00 | 15.00 | 3.75 | 6.00 | 0.30 |
| haiku | 1.00 | 5.00 | 1.25 | 2.00 | 0.10 |

Rows are matched by substring in the order listed, so `claude-opus-5-5` takes the first row
and `claude-opus-5` the second. Input and output are published rates. The cache columns are
derived from the documented multipliers: cache read 0.1x input, 5-minute write 1.25x, 1-hour
write 2x. The one published exception is Opus 5.5, whose cache read is $0.20, which is 0.05x
its input rate rather than 0.1x.

A model name that matches no row is priced at the Sonnet 5 rate and the row is marked
`[?price]`. When prices change, pass your own table:

```
python cctaskcost.py --prices my-prices.json
```

A subscription plan does not bill per token. On a plan, read the dollar figure as *what this
task would have cost on the API*, which is the number that tells you which task to change.

## Test

```
python cctaskcost.py demo
```

One self-check. It builds a session log in a temporary folder and asserts that a tool result
does not start a new task, that the token classes land in the right buckets, that each model
is priced by its own row, and that an unknown model is flagged.

## How this repo was built

Three pairs of open-source Claude Code skills, stacked, following
[Eric Michaud's video](https://www.youtube.com/watch?v=aM_Ta8WtAII):

| Stage | Pair | What it did |
|---|---|---|
| A | Headroom + I Have ADHD | compressed the input and the output of every later stage |
| B | Last30Days + Agent Reach | found the problem and checked nothing already solved it |
| C | none | created this repository and wrote the tool |
| D | Impeccable + Taste | audited and styled the landing page |
| E | none | published, and recorded [`RECEIPT.md`](RECEIPT.md) |

The stage-by-stage walkthrough, with before and after screenshots and what each stage
passed to the next: <https://az9713.github.io/skill-chaining/chain.html>

## Licence

MIT.
