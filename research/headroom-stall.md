# The Headroom stall, 2026-09-25

Stage A of this build ran every request through Headroom (`headroom wrap claude`). On
2026-09-25 the session stopped in Stage B. Stages C, D and E did not start. This file records
the cause, why no check found it first, and the fix, for anyone who chains Headroom with a long
Claude Code session.

## What happened

The last good request finished near 17:55 during the `/last30days` research. After that, every
request failed with:

```
API Error: Server temporarily limiting requests (not usage limit) · {"detail":"Token rate limited. Retry 0.8s"}
```

A reply of "please continue" got the same error with `Retry 0.9s`. The proxy log
(`~/.headroom/logs/proxy-8787.log`) shows 23 refusals from 17:55:31 to 18:12:44.

## Cause

The limit was inside Headroom. Anthropic did not cause it.

1. **Headroom has its own rate limit, and it is on by default.** `headroom proxy --help` lists
   `--tpm INTEGER  Max tokens per minute. Env: HEADROOM_TPM. Default: 100000` and
   `--rpm ... Default: 60`. `headroom wrap claude` starts the proxy with these defaults and
   does not show the limit on screen. The log says only `Rate Limiting: ENABLED`, with no
   number.
2. **It counts the tokens before it compresses them.** In
   `headroom/proxy/handlers/anthropic.py` (about lines 1447 to 1463), the proxy counts
   `original_tokens` over the full message list and calls
   `rate_limiter.check_tokens(rate_key, original_tokens)`. Compression runs after that check.
   So Headroom's own savings do not help a request pass its own limit.
3. **Claude Code sends the whole conversation on every turn.** Each request is the full size
   of the conversation. Each failed request body was 514,342 bytes.
4. **The limit can never let a large request through.** In
   `headroom/proxy/rate_limit_policy.py` the refill is
   `min(rate_per_minute, current_tokens + refill)`, so the bucket holds 100,000 tokens at most.
   A request of more than 100,000 tokens is larger than a full bucket. It fails however long
   the client waits.
5. **The error made the problem look temporary.** The wait value is
   (requested − available) × 60 / 100,000 seconds, so `0.8s` only shows that the bucket held
   about 1,333 tokens at that moment. Claude Code waited, sent the same large request again,
   and got the same answer.

The problem started when the Stage B research made the conversation larger than 100,000
tokens. Before that, every request was small enough to pass.

**Correction to the first diagnosis.** The first report named two causes: the Headroom limit
and an Anthropic rate limit. The second was wrong. The only upstream 429 errors in the log
were two 8-token requests when the proxy started (17:40:09 and 18:13:36). Normal requests
succeeded after the first one, at 17:40:27. They did not block work.

## How to tell which side refused

- The body `{"detail": "Token rate limited. Retry …"}` is Headroom's text
  (`anthropic.py:1461`). It is not the Anthropic error format.
- A local refusal returns in under about 100 ms.
- `curl -s http://127.0.0.1:8787/stats` has two separate counters:
  `requests.rate_limited_by_source.headroom` and `requests.rate_limited_by_source.upstream`.

## Why no check found it first

- **The install check** ran only `headroom --version` (0.39.0) and read the README. It did not
  read `headroom proxy --help`, which is the only place that shows `Default: 100000`.
- **The wrap banner** shows three caveats: Remote Control off, on-demand tool loading, and the
  1M context window. It does not show the token limit.
- **The handoff check** said "confirm Headroom active (`headroom perf` or
  `headroom dashboard`)". That proves the proxy runs. It does not prove a large request
  passes. At the start of a session the conversation is small, so everything passes.
- **The numbers were known.** The session before `/clear` was about 152,000 tokens, 1.52 times
  the limit. Nobody compared the expected session size with the limit.

## Fix

Used for the rest of this build (recommended): raise the limit above the largest conversation
you expect. For a 1M window, use 2,000,000.

```
# Git Bash
HEADROOM_TPM=2000000 headroom wrap claude --1m
# PowerShell
$env:HEADROOM_TPM = '2000000'; headroom wrap claude --1m
```

Before you start, make sure no old proxy is on port 8787:
`curl -s http://127.0.0.1:8787/health` must fail to connect. If it answers, stop that proxy by
its PID only.

Result, recorded in [`RECEIPT.md`](../RECEIPT.md) Stage A:
`rate_limited_by_source.headroom` `0`, `rate_limited_by_source.upstream` `1`,
`rate_limiter.tokens_per_minute` `2000000`.

Other fixes:

- **Turn the limiter off.** Run `headroom proxy --port 8787 --no-rate-limit` in one terminal
  and `headroom wrap claude --no-proxy --1m` in a second. For a single user the local limiter
  adds nothing, because Anthropic enforces the real limits.
- **Run without Headroom.** This is the most reliable path, but you lose the compression.
- **Not recommended:** keep the conversation under 100,000 tokens with frequent `/compact` or
  `/clear`. Research and build stages need more than that, so the stall comes back.

## Pre-flight check

Run this before a long session through Headroom:

```
headroom proxy --help | grep -E -- "--(tpm|rpm|no-rate-limit)"
```

If `--tpm` shows `Default: 100000` and you did not set `HEADROOM_TPM`, use one of the fixes
above.

## A smaller side effect

Headroom also compresses large tool outputs before the model reads them. The model then sees a
shortened text with a marker like `1453 words compressed to 935 ... hash=...`, and must ask for
the full text by that hash. This does not stop work, but the first read of a long file can be a
shortened version.
