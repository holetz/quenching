---
description: Close a spec out — promote to archive (done or abandoned) and distil
argument-hint: [slug] [--outcome done|abandoned]
allowed-tools: Bash(python3:*), Bash(py:*), Read, Glob, Grep, Write, Edit, AskUserQuestion, Skill
---

# /specs:archive — close a spec out, then distil

**Input**: `$ARGUMENTS` (the spec slug and optionally its outcome).

Promotes ONE spec into `archive/` and offers the **single bridge** into the OKF `docs/` bundle.

**This is one skill because v2 made it one command.** v1 had `plan-archive` and `plan-abandon`
because they were two CLI verbs with opposite distillation doctrine. In v2 both are
`specs.py promote <slug> --to archive --outcome done|abandoned`: the gate check, the `## Outcome`
requirement, and the file move are identical. What differs is what crosses into `docs/` afterwards
— and that difference is a branch in Step 4, not a second skill. Keeping it in one place is what
stops the two halves drifting apart.

The distillation doctrine — what crosses, what stays, and how it is graded — lives in
[specs-archive/distill.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-archive/distill.md). The layout, the gates, and the `specs.py` surface
live in
[specs-develop/spec-driven.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-develop/spec-driven.md).
Both are cited, never restated.

## Resolving the tool

Resolve `specs.py` by the fallback in
[specs-capture/backlog-zone.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-capture/backlog-zone.md)
§Resolving the tool. Branch on the **exit code** (0 ok · 1 findings · 2 refusal) and the `--json`,
never on prose.

## Doctrine

- **The outcome is stated, never inferred.** `done` and `abandoned` are opposite claims about the
  same file, and nothing — not task progress, not staleness, not a sweep — may decide which was
  meant. If the human has not said, ask.
- **Archiving as `done` refuses to lie.** Open `- [ ]` boxes with `--outcome done` is exit 2 with
  the list. That refusal is the point: a spec archived as done with half its boxes unticked is a
  green checkbox over work nobody did. `--force` exists for the case where the human knows why —
  the work was descoped, or proven elsewhere — and says so.
- **Abandoning is always allowed.** Open tasks are precisely what you expect when closing out work
  that will not be built, so `--outcome abandoned` never refuses and never needs `--force`.
- **`done` distils; `abandoned` does not.** Archiving as done mints by-products into `docs/` as
  knowledge the product **adopted**. That is wrong for dropped work — it would enshrine a rule
  nobody kept. An abandoned spec harvests at most what was learned by *not* building it, as
  `authority: background`; a decision it *would* have made never crosses.
- **The rule was already written.** A durable rule this spec proved went into `docs/standards/`
  during apply, honestly graded. Archiving **syncs nothing** — there is no delta and no second
  store. The distillation only catches what was not yet captured.
- **Abandonment is never inferred.** No sweep, no conductor, and no age threshold triggers it — a
  spec untouched for a year may be waiting on a vendor. Only the human runs this with
  `--outcome abandoned`.

## Workflow

### 1. Resolve the spec and the outcome
Take the slug from the user, or run `specs.py list --json` and ask. Then establish the outcome —
**ask if it was not stated**, via AskUserQuestion: *done* (it shipped) or *abandoned* (it will not
be built). Announce both.
**Done when:** one spec and one outcome are settled.

### 2. Read the state
```bash
specs.py status --spec <slug> --json
```
Report task progress and whether `## Outcome` is filled. Open tasks under a `done` outcome are
surfaced **now**, before anything is written, so the human can choose between finishing them,
forcing, or switching to `abandoned`.
**Done when:** progress and gate state are reported.

### 3. Write `## Outcome`, then promote
`## Outcome` is the archive gate — the spec cannot move without it. Draft it, confirm it, write it:
```bash
specs.py section <slug> Outcome --write     # body on stdin
specs.py promote <slug> --to archive --outcome done|abandoned [--force]
```
For `done`: what shipped, what was left out, what the next reader needs. For `abandoned`: the
reason it will not be built is the whole content.
A refusal (exit 2) lists exactly what is missing or which boxes are open — surface it verbatim and
let the human decide; never pass `--force` on your own initiative.
**Done when:** the file is in `archive/` with its `outcome:` stamped, or the run stopped at a
refusal the human declined to override.

### 4. Offer ONE distillation pass — the single bridge
Per [specs-archive/distill.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-archive/distill.md), and **branching on the outcome**:

- **`done`** — offer the full pass: a proven rule the spec did not already write →
  `docs/standards/` (`authority` graded honestly), a generic understanding → `docs/knowledge/`, a
  new term → the glossary, a follow-up → a fresh captured spec. Nothing is bulk-copied; the
  archived file remains the history, and only what outlives it crosses.
- **`abandoned`** — offer **only** a narrow harvest of what was learned by not building it, as
  `authority: background`. Never mint a decision the spec *would* have made. Most abandonments
  distil nothing, and that is the correct result.

Every write goes through the insert procedure in
[docs-add/homes.md](${CLAUDE_PLUGIN_ROOT}/assets/references/docs-add/homes.md). No OKF
bundle → skip silently.
**Done when:** the offer was made, and either applied or declined.

### 5. Report
Name the archived path, the outcome, task progress at close, anything distilled, and — for an
abandonment — that nothing was adopted. Mention any `## Discoveries` the spec still carries: those
are `/specs:triage`'s to resolve, and they are easy to lose at close.
**Done when:** path, outcome, and distillation results are all reported.

## Invariants to never violate

- Never infer the outcome. `done` and `abandoned` are the human's word, always.
- Never pass `--force` unprompted — a refusal is information, not an obstacle.
- Never distil an abandoned spec's decisions as adopted knowledge; `background` is the ceiling.
- Never bulk-copy a spec into `docs/`; only what outlives it crosses.
- Never re-write a rule the spec already wrote into `docs/standards/` during apply — archiving
  syncs nothing.
- Never touch a spec other than the one being closed, and never rewrite anything already in
  `archive/`.
- Never treat staleness as evidence of abandonment.
