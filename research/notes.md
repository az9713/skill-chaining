# Research notes — why this tool exists

Two-step research, run 2026-09-25 and 2026-09-26.
Step 1 was a wide scan (Last30Days, 6 sources, window 2026-08-27 → 2026-09-26).
Step 2 was a targeted fetch from Reddit, X and GitHub (Agent Reach).

The raw scan and scrape dumps are **not** committed here. They contain bulk third-party
post text. This file keeps the findings, the counts and the direct links instead.

## Step 1 — wide scan

Topic: *AI coding agents, token cost and context limits*.
Sources that answered: Reddit, X, Hacker News, GitHub, Digg, Techmeme.
arXiv timed out; Polymarket and YouTube returned nothing.

Volume: 117 evidence items.
Reddit 35 items (6,973 upvotes, 2,210 comments) · Hacker News 25 · GitHub 21 ·
X 17 (674 likes) · Digg 11 · Techmeme 8.

Highest-scoring clusters:

1. **Context cost inside one long agent turn.** A pull request compares agent turns that
   consume 18M tokens against turns that consume 1.5M, and argues for cache reuse, context
   elision markers and a live context gauge.
   <https://github.com/octos-org/octos/pull/2465>
2. **Price pressure drives model switching.** A repo owner records that clients refuse to
   depend on one vendor after Claude subscription pricing rose, and asks for model-agnostic
   CLIs plus a *cost-per-ticket baseline*.
   <https://github.com/zbynekdrlik/airuleset/issues/1062>
3. **Per-token price claims are contested.** A widely-shared post claims Opus 5.5 is "40%
   cheaper … costs less per token and uses fewer tokens per task".
   <https://x.com/rakeshgohel01/status/2103494374583623729>
4. **Large test suites blow the context window.**
   <https://www.reddit.com/r/ChatGPTCoding/comments/1wq4wlk/how_do_you_keep_large_test_suites_from/>

## Step 2 — targeted fetch

### What people actually say

The same complaint appears in four different subreddits within one month: people cannot
verify the token savings that tools claim.

- "I benchmarked 5 token saving tools across Codex and Claude Code. 60-90% token-saving
  claims didn't hold up." — 41 points, 27 comments
  <https://www.reddit.com/r/ClaudeCode/comments/1vilwwm/i_benchmarked_5_token_saving_tools_across_codex/>
  Reposted to r/LLMDevs (26 pts),
  <https://www.reddit.com/r/LLMDevs/comments/1vgdwfz/i_benchmarked_5_codebase_tools_across_claude_code/>
  r/codex (34 pts),
  <https://www.reddit.com/r/codex/comments/1vixb6k/i_benchmarked_5_token_saving_tools_across_codex/>
  and r/ClaudeAI (22 pts).
  <https://www.reddit.com/r/ClaudeAI/comments/1viyokr/i_benchmarked_5_token_saving_tools_across_codex/>

The second recurring phrase is *cost of one task*, not cost of a day or a session.

- "Claude Code Cloud Sessions: one 58-minute task showed $34.38 cost on $20/month Pro plan —
  what exactly is …"
  <https://www.reddit.com/r/ClaudeCode/comments/1wqjjcf/claude_code_cloud_sessions_one_58minute_task/>
- "[FrontierHarness] Same model, same pass rate. Why did Claude Code cost 5.6× more than
  DSH?" — 29 points, 20 comments
  <https://www.reddit.com/r/ClaudeCode/comments/1wbpxzm/frontierharness_same_model_same_pass_rate_why_did/>
- "Spent 1,156,308,524 input tokens in May — sharing what …" — 1,343 points, 167 comments
  <https://www.reddit.com/r/ClaudeAI/comments/1tqx8q5/spent_1156308524_input_tokens_in_may_sharing_what/>
- "Per-turn token and cost tracking for Claude Code" — the request stated plainly
  <https://www.reddit.com/r/ClaudeCode/comments/1vhjxrw/perturn_token_and_cost_tracking_for_claude_code/>
- "I woke this morning and found out Anthropic started stealing my money." — 1,566 points,
  456 comments. The thread is about cost that appeared without a visible cause.
  <https://www.reddit.com/r/claude/comments/1vf48yc/i_woke_this_morning_and_found_out_anthropic/>

On X the same window shows the limit hitting mid-task, which is the moment people want the
per-task number.

- "Claude Code will now try to find a graceful stopping point when you hit your 5-hour limit
  mid-task, instead of cutting off mid-edit."
  <https://x.com/i/status/2103561342057943314>

### Does a tool already do this?

Existing tools report **per session, per day or live**. None of them attribute cost to one
prompt. GitHub search, sorted by stars:

| Repo | Stars | Last push | What it reports |
|---|---|---|---|
| `long-910/vscode-claude-status` | 37 | 2026-07-28 | usage and cost in the VS Code status bar |
| `miferco97/claude-monitor-gnome-extension` | 6 | 2026-04-16 | usage, cost, burn rate, live |
| `ramon-webdevpro-nl/cctokmon` | 5 | 2026-04-19 | live usage, cost, context window |
| `Miku3w3/ClaudeCodeUsage` | 3 | 2026-09-11 | real-time usage and cost |
| `evanokeefe39/loc-dock` | 2 | 2026-08-16 | daily dev metrics widget |
| `nhannt315/tokei` | 1 | 2026-08-31 | menu-bar usage, cost, quota |
| `DisposableByDefault/claude-code-monitoring` | 1 | 2026-06-02 | OpenTelemetry pipeline |

`ccusage` is the best known of this family. Reddit shows its releases: a live monitoring
dashboard (481 points), statusline integration (539 points) and Codex support (27 points).
It aggregates by day, by session and by 5-hour block.

<https://www.reddit.com/r/ClaudeAI/comments/1lh71x0/ccusage_v1500_live_monitoring_dashboard_is_here/>
<https://www.reddit.com/r/ClaudeAI/comments/1mlweli/ccusage_now_integrates_with_claude_codes_new/>

Three GitHub searches returned **zero** repositories:

- `claude code session cost per task`
- `claude code per prompt token attribution`
- `claude code compare token savings before after`

GitHub repository search matches on keywords, so zero results is weak evidence on its own.
Read together with the seven repos above — every one of which describes itself as a session,
day or live monitor — the gap is real.

## Decision

Build a CLI that attributes token cost to **one prompt**, from the local session logs.

The log format supports it exactly. In `~/.claude/projects/<project>/<session>.jsonl`:

- every `type: "user"` record carries a `promptId`;
- every tool result inside the same turn repeats that same `promptId`;
- `type: "assistant"` records carry `message.usage` but **no** `promptId`.

So each assistant record is attributed to the most recent `promptId` seen in file order.
That grouping is what turns a session total into a per-task total. It is the one step the
existing tools skip.

The tool prints, per prompt: the first line of the prompt, the four token classes
(input, cache write, cache read, output), and the cost in US dollars.

It also prints what the cache actually saved, because cluster 1 and the "60-90% didn't hold
up" thread are both about savings claims nobody can check.
