# DESIGN.md

Visual system for `docs/index.html`, the cctaskcost landing page.
Written 2026-09-26, after the Impeccable critique scored the first version 20/36.

## Design read

Developer-tool landing page, for developers who already run Claude Code and already feel the
cost. Language: dark terminal. Leaning toward native CSS with a system monospace stack, no
framework, no build step.

No design system from the catalogue applies. This is a single static file served by GitHub
Pages, so Tailwind, React and Motion are all out. The honest label for the aesthetic family
is **dark tech / terminal**, built with native CSS. Nothing here is borrowed from an official
package.

## Dials

| Dial | Value | Reason |
|---|---|---|
| `DESIGN_VARIANCE` | 6 | Developer-portfolio preset. The content is a table of numbers. Asymmetry past 6 would fight it. |
| `MOTION_INTENSITY` | 3 | Static page. Hover and focus states only. Nothing animates, so nothing is claimed. |
| `VISUAL_DENSITY` | 5 | The product is a density argument: one line per task. The page should read the same way. |

`MOTION_INTENSITY` is 3, so no `prefers-reduced-motion` machinery is needed. There is no
motion to reduce.

## The one authored element

The hero is **real terminal output**, copied from one real run. It is not a mockup, and it is
not a `<div>` built to look like a terminal.

Every figure in it is from that run. The task labels were shortened and reworded, because the
originals held local file paths, and the page says so directly under the block. A hero that
claims to be real output has to carry that caveat or the claim is worth nothing.

This is why the page ships no photography. The skill's default is that a text-only page is
incomplete work. Here the single most persuasive artefact the product can show is its own
output, and a stock photograph beside it would weaken it. Recorded as a deliberate deviation,
not an oversight.

## Tokens

One palette, locked. Dark only, declared with `color-scheme: dark`.

| Token | Value | Use |
|---|---|---|
| `--bg` | `#0f172a` | page |
| `--panel` | `#0b1222` | terminal blocks |
| `--card` | `#1e293b` | raised surfaces |
| `--text` | `#e2e8f0` | headings |
| `--text2` | `#cbd5e1` | body |
| `--muted` | `#94a3b8` | captions |
| `--accent` | `#2dd4bf` | links, focus ring, the one accent |
| `--warn` | `#fb923c` | the cost figures, and nothing else |
| `--line` | `#334155` | rules and borders |

**Color consistency lock.** `--accent` teal is the only accent. `--warn` orange is reserved
for dollar figures, because a dollar figure is the product. It never appears on a link, a
border or a heading.

Measured contrast on the shipped page, lowest rendered text pair **6.96:1** (`--muted` on
`--bg`). Body text `--text2` on `--bg` is 12.02:1. All above WCAG AA.

## Type

System stacks only. No web font, no network request for type, which keeps the page
consistent with the product's "no network call" claim.

- Prose: `system-ui, -apple-system, "Segoe UI", sans-serif`
- Terminal and all numbers: `ui-monospace, "Cascadia Mono", Consolas, monospace`

Headline scale `clamp(1.9rem, 6vw, 2.4rem)`. Nothing screams; hierarchy comes from weight and
color, not from raw scale.

## Shape

One radius: **8px**, on every panel, block and table. No pills, no sharp corners mixed in.

## Layout

Single column, `max-width: 880px`, 16px side gutter. No navigation: the page is one screen of
argument plus an install block, and a nav bar would be one line of chrome for zero
destinations.

**No three-card grid.** The first version used three equal cards, which is a named AI tell
and was flagged. The same three facts now sit in a definition list with hairline rules, which
is denser and does not pretend three unequal facts are equal.

## The mobile rule that drove this revision

The critique's P0: the hero table is 65 columns wide, needs about 602px, and had 326px on a
360px phone. 46% of every line was hidden, and the hidden part was the `TASK` column, which is
the whole point. Readers arriving from a Reddit link are likely to be on a phone.

**Fix:** two hero blocks, one wide and one narrow, swapped at 620px by a media query. The
narrow block carries the same run in a 38-column stacked form, so no column is ever cut. Both
are real output from the same command. The duplication is marked in the source.

## Interaction states

- Links: `--accent`, underline offset 2px, underline thickens on hover.
- `:focus-visible`: 2px `--accent` outline, 2px offset, on every focusable element. The first
  version had no focus rule at all.
- No hover effect on anything that is not a link. Nothing moves.

## Em-dash ban

Zero `—` and zero `–` characters in any visible string. The first version used three
`&mdash;` entities, and the Impeccable detector's `em-dash-overuse` rule fired on the page,
though that specific finding was a false positive: it counted 32 hyphens from one ASCII rule
inside `<pre>` plus 4 CLI flags. The three real ones are gone regardless.

## Copy rules

- Every dollar figure on the page is followed, in the same block, by the sentence that a
  subscription plan does not bill per token. The critique found a reader on a $20 plan would
  see `$142.9043` and conclude the tool is broken.
- The log path `~/.claude/projects/<project>/<session>.jsonl` appears on the page, not only in
  the README. `promptId` is meaningless without it.
- Every flag shown in a command is named in the flag list below it.
- The page ends on the safe first run, not on a licence string.

## Accessibility

- `<thead>` and `scope="col"` on the attribution table.
- `<footer>` outside `<main>`, so it is a real `contentinfo` landmark.
- Heading order H1, H2, no level skipped.
- `lang="en"`, viewport meta, `color-scheme` meta.
