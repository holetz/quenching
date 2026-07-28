---
description: Close ONE spec out — review the whole branch, write the docs/ the work revealed, merge, archive, distil. Triggers on "conclude this spec", "close it out", "wrap up the plan", "review the branch", "merge this plan", "archive this spec", "abandon this spec", "it will not be built". Resumable: the reviewed, merge and outcome records plus git say which stages already ran, so a second call picks up where the first stopped instead of redoing it. Archiving as done refuses while boxes are open unless forced; abandoned is always allowed and distils at most a background note. Never infers the outcome, and never treats staleness as abandonment. Not for: building a spec's tasks → /specs:execute; sharpening or interrogating one → /specs:develop; creating one → /specs:create; ranking the whole front → /specs:triage.
argument-hint: [slug] [--outcome done|abandoned]
allowed-tools: Bash, Read, Glob, Grep, Write, Edit, AskUserQuestion, Skill
---

# /specs:conclude — review, merge, archive, distil

**Input**: `$ARGUMENTS` — the spec slug, and optionally its outcome.

Closes ONE spec out. Four things happen, in this order, and each is a separate decision: the whole
branch is **reviewed**, the `docs/` the work *revealed* is **written**, the branch is **merged**,
and the spec is **archived and distilled** into the OKF bundle.

**Why this is not part of `/specs:execute`.** Every step here is a different scale of judgment from
building a task: the branch review reads the whole diff rather than one task's, the merge is
irreversible and needs its own confirmation, and the distillation is the single bridge into
`docs/`. Bolting them onto the end of the build meant a run that died after task nine had to redo
tasks one through eight to reach them.

**This command is resumable, and that is a property of the data, not of a session.** Frontmatter
records the human judgments (`reviewed`, `merge`, `outcome`); git and the filesystem record
everything else. A second call reads both and skips what already happened — see §Resuming.

The distillation doctrine — what crosses into `docs/`, what stays, and how it is graded — lives in
[specs-conclude/distill.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-conclude/distill.md).
The merge strategies, the squash caveat and the **read-if-present** rule for a target's
`docs/standards/git/**` live in
[specs-isolate/git.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-isolate/git.md).
The layout, the gates and the `specs.py` surface live in
[specs-develop/spec-driven.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-develop/spec-driven.md).
All three are cited, never restated.

## Resolving the tool

Resolve `specs.py` by the fallback in
[specs-create/plans-zone.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-create/plans-zone.md)
§Resolving the tool. Branch on the **exit code** (0 ok · 1 findings · 2 refusal) and the `--json`,
never on prose.

**Why `Bash` is unrestricted here.** Like `/specs:execute`, this command drives the target repo's
`git` — the branch diff, the merge, the branch cleanup — and re-runs the repo's own checks after
the merge. Its read-only siblings are scoped to `python3`/`py`.

## Doctrine

- **The outcome is stated, never inferred.** `done` and `abandoned` are opposite claims about the
  same file, and nothing — not task progress, not staleness, not a sweep — may decide which was
  meant. If the human has not said, ask.
- **Concluding as `done` refuses to lie.** Open `- [ ]` boxes with `--outcome done` is exit 2 with
  the list. That refusal is the point: a spec archived as done with half its boxes unticked is a
  green checkbox over work nobody did. `--force` exists for the case where the human knows why —
  the work was descoped, or proven elsewhere — and says so.
- **Abandoning is always allowed.** Open tasks are precisely what you expect when closing out work
  that will not be built, so `--outcome abandoned` never refuses and never needs `--force`.
- **`done` distils; `abandoned` does not.** Concluding as done mints by-products into `docs/` as
  knowledge the product **adopted**. That is wrong for dropped work — it would enshrine a rule
  nobody kept. An abandoned spec harvests at most what was learned by *not* building it, as
  `authority: background`; a decision it *would* have made never crosses.
- **An abandoned spec's branch is never merged on this command's initiative.** Partial work on a
  branch nobody adopted is history, not a change; offer to keep it or delete it, and default to
  keeping.
- **Declared rules were already written.** The `docs/standards/` a task explicitly named went in
  during execution, honestly graded. What lands here is what the work *revealed* — and there is no
  delta and no second store to sync either way.
- **Abandonment is never inferred.** No sweep, no conductor and no age threshold triggers it — a
  spec untouched for a year may be waiting on a vendor. Only the human concludes with
  `--outcome abandoned`.

## Resuming

Read this before deciding what to run. Each stage has one durable signal, and a stage whose signal
is already set is **reported and skipped**, not repeated:

| Stage | Signal it already ran | On resume |
| --- | --- | --- |
| review | `reviewed: {date}` in frontmatter | skip; offer a re-read only if the diff grew since |
| emergent `docs/` | it rides with the review — same stage, same commit | skipped with the review |
| merge | `merge: {strategy, commit}`, or `git branch --merged` lists the work branch | skip; never merge twice |
| archive | the file is in `archive/` with `outcome:` stamped | skip the move; go to distil |
| distil | no record — it is offered once per conclude | offer it; an empty harvest is a valid answer |

`reviewed` is `writeOnce: false` on purpose: a diff that changed and was read again is a new fact.
`merge` and `outcome` are `writeOnce: true` — if either is already set and reality disagrees, that
is a **finding to report**, never a value to overwrite.

## Workflow

### 1. Resolve the spec, the outcome, and what already happened
Take the slug from the input, or run `specs.py list --json` and ask. Establish the outcome —
**ask if it was not stated**, via **AskUserQuestion**: *done* (it shipped) or *abandoned* (it will
not be built).
```bash
specs.py status --spec "<slug>" --json
```
Read task progress, the `## Outcome` state, the `## Discoveries` lines, and the records —
`branch`, `reviewed`, `merge`, `outcome`. Then read git: the current branch, whether the work
branch exists, and whether it is already merged. Announce the outcome and, per §Resuming, which
stages this run will actually perform.

Open tasks under a `done` outcome are surfaced **now**, before anything is written, so the human
can choose between finishing them, forcing, or switching to `abandoned`.
**Done when:** one spec, one outcome, and the list of stages still to run are all settled.

### 2. Review the whole branch diff
```bash
git diff <base>...HEAD          # <base> is the branch record's `base`
```
This is a different thing at a different scale from execute's per-task self-review, and does not
replace it: that one asks four cheap questions of one task's diff, this one reads the whole change
for **coherence** — two tasks that solved the same problem differently, an abstraction that wanted
extracting once the third caller appeared, a `## Impact` path nothing ever wrote, a standard the
diff contradicts.

Present the findings. Fixes go in as ordinary commits on the branch, before the merge. Then stamp
`reviewed: {date}`.

No `branch` record (the work was done in place), or no git → say so and skip to step 4; there is no
branch diff to read.
**Done when:** the diff was read and `reviewed` is stamped, or the run recorded why there was
nothing to review.

### 3. Write the `docs/` the work revealed
The `docs/standards/` a task explicitly named is already in — execute wrote it as part of that
task. What lands **here** is what the work revealed and nobody declared: the `## Discoveries` lines
worth a doc, and whatever the branch review just surfaced.

Decide what crosses with the table in
[distill.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-conclude/distill.md) §What crosses, what
stays; write each through the insert procedure in
[docs-add/homes.md](${CLAUDE_PLUGIN_ROOT}/assets/references/docs-add/homes.md), stamping `authority`
honestly. Present them as ONE plan and take one confirmation.

These land **on the branch**, in their own commit, so the rule ships with the code that proved it.
A `## Discoveries` line that gets a doc is resolved in place. No OKF bundle → skip silently.
**Done when:** the emergent docs are written and committed, or the offer was declined, or there is
no bundle.

### 4. Write `## Outcome` and archive
`## Outcome` is the archive gate — the spec cannot move without it. Draft it, confirm it, write it:
```bash
specs.py section "<slug>" Outcome --write     # body on stdin
specs.py promote "<slug>" --to archive --outcome done|abandoned [--force]
```
For `done`: what shipped, what was left out, what the next reader needs — **including the merge
strategy**, because a squash changes what a future reader can resolve. For `abandoned`: the reason
it will not be built is the whole content.

A refusal (exit 2) lists exactly what is missing or which boxes are open — surface it verbatim and
let the human decide; **never pass `--force` on your own initiative.** Commit the move on the
branch, so one merge carries the code, the docs and the closed spec together.
**Done when:** the file is in `archive/` with its `outcome:` stamped and committed, or the run
stopped at a refusal the human declined to override.

### 5. Merge — the strategy is offered, and the squash caveat is honoured
For `done` with a `branch` record, offer the strategies in
[git.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-isolate/git.md) §Merge strategies with
**AskUserQuestion**, and state the trade in one line each. **When squash is chosen, offer NOT to
delete the branch** — a squash collapses every per-task commit, so the `commit:` sha on each task
line resolves only while the branch survives. Say that plainly rather than deleting and discovering
it later.

Merge, then stamp `merge: {strategy, commit}` into the archived spec on the base branch and commit
that bookkeeping. Re-run whatever the repo's `## Validation` names, on the merged base.

For `abandoned`, do not merge. Offer to keep the branch (default) or delete it, and record the
choice in the report.
**Done when:** the merge landed and `merge` is stamped, or the run recorded why nothing was merged.

### 6. Offer ONE distillation pass — the single bridge
Per [distill.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-conclude/distill.md), **branching on
the outcome**:

- **`done`** — the full pass over what is *left*: a decision still sitting in `## Design`, a generic
  understanding, a term the spec coined, a follow-up worth its own spec. Most of the harvest was
  already written in step 3 or during execution; **zero to a few is the normal result**.
- **`abandoned`** — **only** a narrow harvest of what was learned by not building it, as
  `authority: background`. Never mint a decision the spec *would* have made. Most abandonments
  distil nothing, and that is the correct result.

One plan, one OK. Every write goes through
[docs-add/homes.md](${CLAUDE_PLUGIN_ROOT}/assets/references/docs-add/homes.md). No bundle → skip
silently.
**Done when:** the offer was made, and either applied or declined.

### 7. Report
The archived path, the outcome, task progress at close, `reviewed` / `merge` / `branch` as they now
stand, what the review found and what was done about it, the docs written in step 3 and step 6, and
— for an abandonment — that nothing was adopted and what became of the branch.

Name any `## Discoveries` line still unresolved: those are `/specs:develop`'s discoveries bank to
close, and they are easiest to lose at exactly this moment.
**Done when:** path, outcome, records, and both `docs/` passes are all reported.

## Invariants to never violate

- Never infer the outcome. `done` and `abandoned` are the human's word, always.
- Never treat staleness as evidence of abandonment.
- Never pass `--force` unprompted — a refusal is information, not an obstacle.
- Never merge an abandoned spec's branch, and never merge without the human choosing the strategy.
- Never delete a branch after a **squash** without saying what it costs: the per-task `commit:`
  shas stop resolving.
- Never overwrite a `writeOnce` record (`merge`, `outcome`) to make reality fit — report the
  disagreement instead.
- Never re-run a stage whose signal is already set without saying so and being asked to.
- Never re-write a rule a task already wrote into `docs/standards/` during execution — concluding
  syncs nothing.
- Never bulk-copy a spec into `docs/`; only what outlives it crosses.
- Never distil an abandoned spec's decisions as adopted knowledge; `background` is the ceiling.
- Never edit or delete anything already in `archive/`, and never touch a spec other than the one
  being closed.
- Never rewrite history: no amend of a task commit, no force-push, no `--no-verify` and no
  `--no-gpg-sign` on the commits this command makes.
