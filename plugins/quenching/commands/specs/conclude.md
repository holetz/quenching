---
description: Close ONE spec out — review the whole branch, write the /.knowledge/ the work revealed, archive, distil, prove the pre-merge gate green — and stop, handing off to /quenching:git:pr:create or /quenching:git:merge. Triggers on "conclude this spec", "close it out", "wrap up the plan", "review the branch", "archive this spec", "abandon this spec", "it will not be built". Everything lands on the work branch; nothing is ever committed to the base by this command. Settles pre-merge release obligations. Resumable: the reviewed and outcome records plus git say which stages already ran. Archiving as done refuses while boxes are open unless forced; abandoned is always allowed and distils at most a background note. Never infers the outcome or treats staleness as abandonment.
argument-hint: [slug] [--outcome done|abandoned]
allowed-tools: Bash, Read, Glob, Grep, Write, Edit, AskUserQuestion, Skill
model: opus
---

# /quenching:specs:conclude — review, archive, distil — and hand off

**Input**: `$ARGUMENTS` — the spec slug, and optionally its outcome.

Closes ONE spec out, short of the merge itself. Four things happen, in this order, and each is a
separate decision: the whole branch is **reviewed**, the `/.knowledge/` the work *revealed* is
**written**, the spec is **archived and distilled** into the OKF bundle, and the pre-merge gate is
**proven green** — then the run **stops**, naming `/quenching:git:pr:create` or
`/quenching:git:merge` as the human's own next command.

**Nothing is ever committed to the base by this run, because this run never touches the base at
all.** The old contract held that property by running the merge itself, last, so that nothing could
follow it. The new one holds the same property by a shorter argument: this command's footprint ends
on the work branch, at the reviewed, distilled, gate-proven commit — everything after that point
belongs to whichever command the human runs next, on their own word.

**Why `## Outcome` no longer names a merge strategy or a PR.** Both used to be choices made here, so
the archived spec could state them. Neither is knowable at archive time anymore: the strategy is
`/quenching:git:merge`'s own offer, the PR is `/quenching:git:pr:create`'s. `## Outcome` now asserts
what THIS run delivered — reviewed, distilled, ready for merge — and the merge itself becomes a
fact of the host (a commit on the base, a merged PR), legible from there whenever a later reader
needs it.

**Why this is not part of `/quenching:specs:execute`.** Every step here is a different scale of judgment from
building a task: the branch review reads the whole diff rather than one task's, and the
distillation is the single bridge into `/.knowledge/`. Bolting them onto the end of the build meant
a run that died after task nine had to redo tasks one through eight to reach them.

**This command is resumable, and that is a property of the data, not of a session.** Frontmatter
records the human judgments (`reviewed`, `outcome`); git and the filesystem record everything else.
A second call reads both and skips what already happened — see §Resuming.

The distillation doctrine — what crosses into `/.knowledge/`, what stays, and how it is graded — lives in
[specs-conclude/distill.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-conclude/distill.md)
§What crosses, what stays. The layout, the gates and the
`cq specs` surface live in
[specs-develop/spec-driven.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-develop/spec-driven.md)
§The `specs/` layout §The gates and the stage-scoped explicit-none rule §The `cq specs` tool
surface §The report mold, which owns the shape step 7 prints in.
Both are cited, never restated.

## Resolving the tool

Resolve `cq specs` per
[align/tool-resolution.md](${CLAUDE_PLUGIN_ROOT}/assets/references/align/tool-resolution.md)
§Resolving the tool. Branch on the **exit code** (0 ok · 1 findings · 2 refusal) and the `--json`,
never on prose.

**Why `Bash` is unrestricted here.** Like `/quenching:specs:execute`, this command drives the target
repo's `git` — the branch diff, the archive commit, the distillation commit — and re-runs the
repo's own checks to prove the pre-merge gate. Its read-only siblings are scoped to `python3`/`py`.

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
- **`done` distils; `abandoned` does not.** Concluding as done mints by-products into `/.knowledge/` as
  knowledge the product **adopted**. That is wrong for dropped work — it would enshrine a rule
  nobody kept. An abandoned spec harvests at most what was learned by *not* building it, as
  `authority: background`; a decision it *would* have made never crosses.
- **An abandoned spec's branch is offered for deletion, never handed off toward a merge.** Partial
  work on a branch nobody adopted is history, not a change; offer to keep it or delete it, and
  default to keeping. This is the one branch-disposal decision that stays inline here rather than
  moving to `/quenching:git:cleanup` — it is this run's own report of what became of the work it
  just closed, not a later sweep over branches nobody is thinking about right now.
- **Everything `abandoned` writes lands in the checkout holding `<base>`, never this branch** — see
  [specs-conclude/abandoned.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-conclude/abandoned.md).
  There is no merge to carry a branch commit home, so a record left on the branch would depend on a
  branch nobody adopted still existing.
- **Declared rules were already written.** The `/.knowledge/standards/` a task explicitly named went in
  during execution, honestly graded. What lands here is what the work *revealed* — and there is no
  delta and no second store to sync either way.
- **What a standard attaches to the *merge* is settled here, not built as a task.** A version bump,
  a changelog entry, a manifest re-stamp: none of them is knowable at task 1, because what the
  release turns out to be depends on what the last task turned out to be. Scheduled as work they
  also collide — two branches bump from the same base to the same number and the second one merges
  into a conflict. Settled at step 5 they start from the base being merged into, and ride the same
  merge as the code that earned them.
- **Abandonment is never inferred.** No sweep, no conductor and no age threshold triggers it — a
  spec untouched for a year may be waiting on a vendor. Only the human concludes with
  `--outcome abandoned`.

## Resuming

Read this before deciding what to run. Each stage has one durable signal, and a stage whose signal
is already set is **reported and skipped**, not repeated:

| Stage | Signal it already ran | On resume |
| --- | --- | --- |
| review | `reviewed: {date}` in frontmatter | skip; offer a re-read only if the diff grew since |
| emergent `/.knowledge/` | it rides with the review — same stage, same commit | skipped with the review |
| archive | the file is in `archive/` with `outcome:` stamped | skip the move; go to distil |
| distil | no record — it is offered once per conclude | offer it; an empty harvest is a valid answer |
| release obligations | the branch diff already carries what the standard requires | report it satisfied; re-read the standard only if the diff grew |
| validation gate | no record — it is a verdict on the tree as it stands *now* | always re-run it; a green run from before the last commit proves nothing |
| already merged | `git branch --merged <base>` lists the work branch, or a `merge`/`pr` record already exists | report that a later `/quenching:git:merge` or `/quenching:git:pr:create` run already finished this — there is nothing left to hand off |

`reviewed` is `writeOnce: false` on purpose: a diff that changed and was read again is a new fact.
`outcome` is `writeOnce: true` — if it is already set and reality disagrees, that is a **finding to
report**, never a value to overwrite. `merge` and `pr` are no longer this command's to write at
all — reading either is only ever to answer the "already merged" row above, and for `abandoned`
that read happens from the base checkout (Doctrine), never wherever this run stands.

## Workflow

### 1. Resolve the spec, the outcome, and what already happened
A slug in the input → use it. **No slug given → try auto-discovery first**, off the current
branch's own marking:
[auto-discover.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-conclude/auto-discover.md)
§Reading the marking §Filtering to valid slugs §Resolving what remains, cited rather than
restated. One valid slug resolves it silently, naming the marking as the source; more than one asks
which, via **AskUserQuestion**. No valid marking → §The fallback there measures the diff and always
asks whether to materialize a minimal spec — accepted, its new slug is used from here on exactly
like a marked one. **Declined, headless completion — closing with no spec file at all — is not yet
built**: say so, record it with `cq specs discover`, and fall back to `cq specs list --json` and
ask, exactly as before this spec. Establish the outcome — **ask if it was not stated**, via
**AskUserQuestion**: *done* (it shipped) or *abandoned* (it will not be built).
```bash
cq specs status --spec "<slug>" --json
```
Read task progress, the `## Outcome` state, and the records — `branch`, `reviewed`, `merge`, `pr`,
`outcome` — from that payload. Then, for the `## Discoveries` lines themselves, the one body this
step needs: `cq specs section "<slug>" Discoveries --json`. Then read git: the
current branch, whether the work branch exists, and whether it is already merged. Announce the
outcome and, per §Resuming, which stages this run will actually perform.

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
the record — `cq specs record "<slug>" reviewed --set date=<today>`, never by editing the
frontmatter.

**The test is `branch.work != branch.base`, never the record's presence** — in-place work stamps
one too (`/.knowledge/standards/workflows/plan-git-record.md` §Three frontmatter records carry the
underivable git facts). No record, `work` equal to `base`, or no git → say so and skip to step 4;
there is no branch diff to read.
**Done when:** the diff was read and `reviewed` is stamped, or the run recorded why there was
nothing to review.

### 3. Write the `/.knowledge/` the work revealed
The `/.knowledge/standards/` a task explicitly named is already in — execute wrote it as part of that
task. What lands **here** is what the work revealed and nobody declared: the `## Discoveries` lines
worth a doc, and whatever the branch review just surfaced.

Decide what crosses with the table in
[distill.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-conclude/distill.md)
§What crosses, what stays; write each through the insert procedure in
[knowledge-add/homes.md](${CLAUDE_PLUGIN_ROOT}/assets/references/knowledge-add/homes.md)
§The frontmatter stamp §Updating `index.md` §Enriching the glossary §Self-check, stamping
`authority` honestly. Present them as ONE plan and take one confirmation.

These land on the branch, in their own commit — or, for `abandoned`, the base checkout (Doctrine).
A `## Discoveries` line that gets a doc is resolved in place. No OKF bundle → skip silently.
**Done when:** the emergent docs are written and committed, or the offer was declined, or there is
no bundle.

### 4. Write `## Outcome` and archive
`## Outcome` is the archive gate — the spec cannot move without it. Draft it, confirm it, write it:
```bash
cq specs section "<slug>" Outcome --write     # body on stdin
cq specs promote "<slug>" --to archive --outcome done|abandoned [--force]
```
For `done`: what shipped, what was left out, what the next reader needs — **reviewed, distilled,
ready for merge**. Neither the strategy nor a PR is named here: both are `/quenching:git:merge`'s
and `/quenching:git:pr:create`'s own choices, made after this run ends, and a value written here
before either exists would only be a guess. For `abandoned`: the reason it will not be built is the
whole content.

A refusal (exit 2) lists exactly what is missing or which boxes are open — surface it verbatim and
let the human decide; **never pass `--force` on your own initiative.** Commit the move on the
branch — or, for `abandoned`, computed here but committed into the base checkout (Doctrine).
**Done when:** the file is in `archive/` with its `outcome:` stamped and committed, or the run
stopped at a refusal the human declined to override.

### 5. Distil, and settle the release obligations — all on the work branch
This is the last writing step, and everything it writes lands on the **work branch** — or, for
`abandoned`, the base checkout (Doctrine above). Two things happen here, in this order.

**First, the distillation pass** — the single bridge into `/.knowledge/`, per
[distill.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-conclude/distill.md)
§The procedure (one confirmation), **branching on the outcome**:

- **`done`** — the full pass over what is *left*: a decision still sitting in `## Design`, a generic
  understanding, a term the spec coined, a follow-up worth its own spec. Most of the harvest was
  already written in step 3 or during execution; **zero to a few is the normal result**.
- **`abandoned`** — **only** a narrow harvest of what was learned by not building it, as
  `authority: background`. Never mint a decision the spec *would* have made. Most abandonments
  distil nothing, and that is the correct result.

One plan, one OK. Every write goes through
[knowledge-add/homes.md](${CLAUDE_PLUGIN_ROOT}/assets/references/knowledge-add/homes.md)
§The frontmatter stamp §Updating `index.md` §Enriching the glossary §Self-check. No bundle → skip
silently, landing per Doctrine: the work branch for `done`, the base checkout for `abandoned`.

**Then settle the release obligations the repo's standards attach to the merge itself.** With an
OKF bundle present, derive which standards the branch diff's own paths answer to — an aggregate in
the shell, never a walk of `/.knowledge/standards/<subject>/` — and read exactly those, per
[align/evidence-doctrine.md](${CLAUDE_PLUGIN_ROOT}/assets/references/align/evidence-doctrine.md)
§1 §2. Apply what they require *of the merge* rather than of any one task — a version bumped across
artifacts a standard says must move together, a changelog entry, a manifest re-stamped. This is the
only correct moment for it: the whole branch is written, so what the release *is* is knowable.

Nothing is invented. A repo whose standards attach nothing to a merge gets nothing, silently, and
so does a repo with no bundle. What a standard *does* require is presented as ONE plan with the
standard quoted, taken on one confirmation, and committed on the branch. A requirement the diff
already satisfies is reported as already done, never redone.

For `abandoned`, **no release obligation is settled** — a version nobody adopted is a claim the
history should not carry. The distillation above still runs.
**Done when:** the distillation offer was made and applied or declined, and the release obligations
were applied, reported as already satisfied, or reported as none.

### 6. Prove the gate green, then hand off
Nothing after this point writes anything — the last commit this run makes is step 5's.

**First the gate: re-run whatever the repo's `## Validation` names — on the WORK BRANCH, before
merging.** Run it from the checkout that carries the work (the worktree or branch this run is
standing on), so what it grades is the change being proposed.

**A failing check stops the handoff.** Report which check failed and what it printed, leave the
branch unmerged, and let the human fix it *on the branch* — then this command is re-run. Never hand
off past a red check, and never repair one with a commit that isn't the fix itself: whatever lands
rides the same eventual merge as everything else.

This is why the gate sits *before* the merge rather than after it. A check that runs afterwards can
only narrate — the base already carries the change, and the only repair left is a commit on the
base, which is the exact thing this ordering exists to prevent. Run on the branch, a red check
still has somewhere to be fixed.

**Nothing is stranded by stopping here.** A gate failure leaves nothing archived-and-unmerged
behind it that a later run cannot re-derive: `## Outcome` and the archive move already happened in
step 4, on the branch, and a red gate found here is reported and fixed on that same branch before
anyone hands off toward a merge.

**The gate grades the branch, so the branch must already carry the base.** If the base moved since
the branch was cut, the merge produces a tree *neither* side ever validated, and a green gate says
nothing about it:

```bash
git rev-list --count plan/<slug>..<base>      # commits on the base the branch does not have
```

Non-zero → **say so and stop before the gate**, naming the count. Bringing the branch up to date is
a write, and it is the human's call which way — merging the base in, or `/quenching:git:sync`'s own
rebase, which carries the recorded task subjects through the rewrite. Never do it unasked, and
never run the gate over a branch you know is behind: that is a verdict about a tree that is not
being merged.

**An inconclusive result is not a green one.** A check that cannot tell "this failed" from "this
could not be measured" has returned no verdict — say which it was, and ask, rather than merging on
it. Where the repo keeps `/.knowledge/standards/quality/surface-verification.md`, its §The five
preconditions a check must satisfy is where that distinction is defined for the command surface.

**Run the scope the diff justifies.** A harness that spawns fresh agent sessions bills for every
one, so a check with a `--only`-style selector gets the subset this branch can actually break — the
whole suite by reflex is the expensive way to learn nothing. When the repo's `## Validation` names
the scope, follow it; when it does not, run what it says and report the cost as a finding worth a
selector.

The gate passed — the branch is reviewed, distilled, archived, and proven. **Name the handoff and
stop:**

```bash
gh repo view --json name 2>&1 || echo "NO-ROUTE"
```

`NO-ROUTE` (or `gh` unauthenticated) → recommend `/quenching:git:merge`. Otherwise recommend
**both**, in this order: `/quenching:git:pr:create` first where a PR is the house style, or
`/quenching:git:merge` directly for a local merge — the human picks, and neither is invoked from
here. Name the branch and the base so the recommendation is copy-pasteable.

For `abandoned`, there is nothing to hand off toward — do not remove any worktree; frame and make
the branch-delete offer per
[specs-conclude/abandoned.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-conclude/abandoned.md)
§The branch-delete offer, informed rather than defensive, default **keep**, and record the choice
and fate in the report.
**Done when:** the gate ran green on the branch and the handoff was named, or the run recorded why
nothing could be handed off — a red gate, or (abandoned) the branch's own fate decided instead.

### 7. Report

```bash
cq components read ${CLAUDE_PLUGIN_ROOT}/assets/references/specs-develop/spec-driven.md \
  --sections "§The report mold" --rules-only
```

Emit §The report mold. The single-spec header line carries the archived locator and the outcome; three
body blocks:

1. **At close** — fixed. Task progress, `reviewed` / `branch` as they now stand, and — for an
   abandonment — that nothing was adopted and what became of the branch.
2. **The review** — fixed. What it found and what was done about it, the docs written in step 3 and
   step 5, and what the pre-merge gate returned. §Quoting a tool's own output governs the gate's
   result, which means **a check that came back inconclusive is named as such, never counted as
   passed**.
3. **Unresolved `## Discoveries`** — optional, each line named. They are
   `/quenching:specs:develop`'s discoveries bank to close, and they are easiest to lose at exactly
   this moment.

Close on §The next-step block, its recommended line naming step 6's handoff — `/quenching:git:pr:create`
or `/quenching:git:merge`, whichever was recommended, or `/quenching:specs:develop <slug>` when
block 3 has rows and that needs settling first.
**Done when:** path, outcome, records, both `/.knowledge/` passes and the next-step block are all
reported.

## Invariants to never violate

- Never infer the outcome. `done` and `abandoned` are the human's word, always.
- Never treat staleness as evidence of abandonment.
- Never pass `--force` unprompted — a refusal is information, not an obstacle.
- Never hand off an abandoned spec's branch toward a merge — offer to keep or delete it instead.
- **Never `git branch -D`, at all**, when framing the abandoned branch-delete offer — git's own
  refusal over a not-fully-merged branch is the safety, and forcing past it destroys the only copy
  of work nobody adopted.
- **Never hand off past a red `## Validation` gate**, and never count an inconclusive check as a
  green one. The gate runs on the branch precisely so that a failure still has somewhere to be
  fixed — recommending a merge command anyway spends that.
- **Never run the gate over a branch that is behind its base.** Report the count and stop; bringing
  it up to date is a write, and which way is the human's call.
- **This command's own commits end at step 5.** Nothing it does writes to the branch after the gate
  in step 6 — the merge, the PR, and whatever they each commit belong entirely to
  `/quenching:git:merge` and `/quenching:git:pr:create`, run separately, on the human's own word.
- Never overwrite the `writeOnce` `outcome` record to make reality fit — report the disagreement
  instead. It is stamped with `cq specs record`, which refuses on its own; editing the frontmatter
  to get past that refusal is the thing the refusal exists to stop.
- Never re-run a stage whose signal is already set without saying so and being asked to.
- Never re-write a rule a task already wrote into `/.knowledge/standards/` during execution — concluding
  syncs nothing.
- Never settle a release obligation for an **abandoned** spec, and never invent one no standard
  states — a bump nobody asked for is a release claim this command had no authority to make.
- Never bulk-copy a spec into `/.knowledge/`; only what outlives it crosses.
- Never distil an abandoned spec's decisions as adopted knowledge; `background` is the ceiling.
- Never edit or delete anything already in `archive/`, with exactly one exception, onto the spec
  this run is closing: the distillation's `## Outcome` append. It records a fact that did not exist
  at the archive move and has nowhere earlier to live — the two-clause test a further exception is
  argued against, never assumed into. It revises nothing the spec claimed. Never touch a spec other
  than that one, nor an archived spec from an earlier run.
- Never rewrite history: no amend of a task commit, no force-push, no `--no-verify` and no
  `--no-gpg-sign` on the commits this command makes.
