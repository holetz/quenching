---
description: >-
  Close ONE spec out: review the branch, write knowledge, archive, prove the gate, hand off to a PR or merge. Use for "conclude this spec", "close it out", "abandon this spec". Not for: building → /quenching:specs:execute.
argument-hint: [id] [--outcome done|abandoned]
allowed-tools: Bash(cq:*), Bash, Read, Glob, Grep, Write, Edit, AskUserQuestion, Skill
model: opus
---

# /quenching:specs:conclude — review, archive, distil — and hand off

**Input**: `$ARGUMENTS` — the spec id, and optionally its outcome.

Closes ONE spec out, short of the merge itself. Four things happen, in this order, and each is a
separate decision: the whole branch is **reviewed**, the `/docs/` the work *revealed* is
**written**, the spec is **archived and distilled** into the OKF bundle, and the pre-merge gate is
**proven green** — then the run **stops**, naming `/quenching:git:pr:create` or
`/quenching:git:merge` as the human's own next command — except that `low` gear chains directly
to `/quenching:git:pr:create` through `Skill` after the green gate.

**Done work ends on the work branch; abandoned close-out writes land in the checkout holding the
base.**

The distillation doctrine — what crosses into `/docs/`, what stays, and how it is graded — lives in
[specs-conclude/distill.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-conclude/distill.md)
§What crosses, what stays. The layout and the gates live in
[specs-develop/spec-driven.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-develop/spec-driven.md)
§The spec document §The gates and the stage-scoped explicit-none rule. The `cq specs`
surface lives in
[specs-surface.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-develop/specs-surface.md)
§The `cq specs` tool surface; the report shape lives in
[report-mold.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-develop/report-mold.md)
§The report mold.
## Resolving the tool

Resolve `cq specs` per
[align/tool-resolution.md](${CLAUDE_PLUGIN_ROOT}/assets/references/align/tool-resolution.md)
§Resolving the tool. Branch on the **exit code** (0 ok · 1 findings · 2 refusal) and the `--json`,
never on prose.

## Doctrine

- **The outcome is stated, never inferred.** `done` and `abandoned` are opposite claims about the
  same file, and nothing — not task progress, not staleness, not a sweep — may decide which was
  meant. If the human has not said, ask.
- **Concluding as `done` refuses to lie.** Open `- [ ]` boxes with `--outcome done` is exit 2 with
  the list. `--force` exists for the case where the human knows why — the work was descoped, or
  proven elsewhere — and says so.
- **Abandoning is always allowed.** `--outcome abandoned` never refuses and never needs `--force`.
- **`done` distils; `abandoned` does not.** Concluding as done mints by-products into `/docs/` as
  knowledge the product **adopted**. An abandoned spec harvests at most what was learned by *not*
  building it, as
  `authority: background`; a decision it *would* have made never crosses.
- **An abandoned spec's branch is offered for deletion, never handed off toward a merge.** Partial
  work on a branch nobody adopted is history, not a change; offer to keep it or delete it, and
  default to keeping. This is the one branch-disposal decision that stays inline here rather than
  in `/quenching:git:cleanup`.
- **Everything `abandoned` writes lands in the checkout holding `<base>`, never this branch** — see
  [specs-conclude/abandoned.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-conclude/abandoned.md)
  §Locating the checkout and writing into it §The branch-delete offer, informed rather than defensive.
- **Declared rules were already written.** The `/docs/standards/` a task explicitly named went in
  during execution, honestly graded. What lands here is what the work *revealed*.
- **What a standard attaches to the *merge* is settled at step 5, not built as a task** — a version
  bump, a changelog entry, a manifest re-stamp.

## Resuming

Read this before deciding what to run. Each stage has one durable signal, and a stage whose signal
is already set is **reported and skipped**, not repeated:

| Stage | Signal it already ran | On resume |
| --- | --- | --- |
| review | `reviewed: {date}` in frontmatter | skip; offer a re-read only if the diff grew since |
| emergent `/docs/` | it rides with the review — same stage, same commit | skipped with the review |
| archive | the file is in `archive/` with `outcome:` stamped | skip the move; go to distil |
| distil | no record — it is offered once per conclude | offer it; an empty harvest is a valid answer |
| release obligations | the branch diff already carries what the standard requires | report it satisfied; re-read the standard only if the diff grew |
| validation gate | no record — it is a verdict on the tree as it stands *now* | always re-run it; a green run from before the last commit proves nothing |
| already merged | `git branch --merged <base>` lists the work branch, or a `merge`/`pr` record already exists | report that a later `/quenching:git:merge` or `/quenching:git:pr:create` run already finished this — there is nothing left to hand off |

`reviewed` is `writeOnce: false`: a diff read again is a new fact. `outcome` is `writeOnce: true` —
if it is already set and reality disagrees, that is a **finding to report**, never a value to
overwrite. `merge` and `pr` are read only to answer the "already merged" row above, and for
`abandoned` from the base checkout (Doctrine).

## Workflow

### 1. Resolve the spec, the outcome, and what already happened
An ID in the input → use it. **No ID given → try auto-discovery first**, off the current
branch's own marking:
[auto-discover.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-conclude/auto-discover.md)
§Reading the marking §Filtering to valid IDs §Resolving what remains, cited rather than
restated. One valid id resolves it silently, naming the marking as the source; more than one asks
which, via **AskUserQuestion**. No valid marking → §The fallback there measures the diff and always
asks whether to materialize a minimal spec — accepted, its new id is used from here on exactly
like a marked one. **Declined, headless completion — closing with no spec file at all — is not
built**: say so, record it with `cq specs discover`, and fall back to `cq specs list --json` and
ask. Establish the outcome — **ask if it was not stated**, via
**AskUserQuestion**: *done* (it shipped) or *abandoned* (it will not be built).
```bash
cq specs status --spec "<id>" --json
```
Read task progress, the `## Outcome` state, and the records — `branch`, `reviewed`, `merge`, `pr`,
`outcome` — from that payload. Then, for the `## Discoveries` lines themselves, the one body this
step needs: `cq specs section "<id>" Discoveries --json`. Then read git: the
current branch, whether the work branch exists, and whether it is already merged. Announce the
outcome and, per §Resuming, which stages this run will actually perform.

Open tasks under a `done` outcome are surfaced **now**, before anything is written, so the human
can choose between finishing them, forcing, or switching to `abandoned`.
**Done when:** one spec, one outcome, and the list of stages still to run are all settled.

### 2. Review the whole branch diff
```bash
git diff <base>...HEAD          # <base> is the branch record's `base`
```
This reads the whole change for **coherence**, beyond execute's per-task self-review — two tasks that solved the same problem differently, an abstraction that wanted
extracting once the third caller appeared, a `## Impact` path nothing ever wrote, a standard the
diff contradicts.

Present the findings. Fixes go in as ordinary commits on the branch, before the merge. Then stamp
the record — `cq specs record "<id>" reviewed --set date=<today>`, never by editing the
frontmatter.

**The test is `branch.work != branch.base`, never the record's presence** — in-place work stamps
one too (`/docs/standards/workflows/plan-git-record.md` §Three frontmatter records carry the
underivable git facts). No record, `work` equal to `base`, or no git → say so and skip to step 4;
there is no branch diff to read.
**Done when:** the diff was read and `reviewed` is stamped, or the run recorded why there was
nothing to review.

### 3. Write the `/docs/` the work revealed
The `/docs/standards/` a task explicitly named is already in — execute wrote it as part of that
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
cq specs section "<id>" Outcome --write     # body on stdin
cq specs promote "<id>" --to archive --outcome done|abandoned [--force]
```
For `done`: what shipped, what was left out, what the next reader needs — **reviewed, distilled,
ready for merge**; name neither a merge strategy nor a PR. For `abandoned`: the reason it will not be built is the
whole content.

A refusal (exit 2) lists exactly what is missing or which boxes are open — surface it verbatim and
let the human decide; **never pass `--force` on your own initiative.** Commit the move on the
branch — or, for `abandoned`, computed here but committed into the base checkout (Doctrine).
**Done when:** the file is in `archive/` with its `outcome:` stamped and committed, or the run
stopped at a refusal the human declined to override.

### 5. Distil, and settle the release obligations
This is the last writing step, and everything it writes lands on the **work branch** for `done` — or, for
`abandoned`, the base checkout (Doctrine above). Two things happen here, in this order.

**First, the distillation pass** — the single bridge into `/docs/`, per
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
the shell, never a walk of `/docs/standards/<subject>/` — and read exactly those, per
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
off past a red check, and never repair one with a commit that isn't the fix itself.

**The gate grades the branch, so the branch must already carry the base.** If the base moved since
the branch was cut, a green gate says nothing about the merged tree:

```bash
git rev-list --count plan/<id>-<handle>..<base>      # commits on the base the branch does not have
```

Non-zero → **say so and stop before the gate**, naming the count. Bringing the branch up to date is
a write, and it is the human's call which way — merging the base in, or `/quenching:git:sync`'s own
rebase, which carries the recorded task subjects through the rewrite. Never do it unasked, and
never run the gate over a branch you know is behind.

**An inconclusive result is not a green one.** A check that cannot tell "this failed" from "this
could not be measured" has returned no verdict — say which it was, and ask, rather than merging on
it. Where the repo keeps `/docs/standards/quality/surface-verification.md`, its §The five
preconditions a check must satisfy is where that distinction is defined for the command surface.

**Run the scope the diff justifies.** A check with a `--only`-style selector gets the subset this
branch can actually break, because a harness that spawns fresh agent sessions bills for every one.
When the repo's `## Validation` names
the scope, follow it; when it does not, run what it says and report the cost as a finding worth a
selector.

The gate passed — the branch is reviewed, distilled, archived, and proven. For a `done` outcome,
read the complexity from the status payload already in hand. **`low` chains the provider handoff
now:**

```text
Skill("quenching:git:pr:create", "<id>")
```

Invoke it with the spec id; `/quenching:git:pr:create` owns its own confirmation, push and PR
record. Do not offer a second handoff or invoke `/quenching:git:merge` on the low path. **For
`medium`, `high` and `xhigh`, name the handoff and stop:**

Use the provider configuration already read in step 1 to name the next command: recommend
`/quenching:git:pr:create` when the configured provider supports the PR route, otherwise
`/quenching:git:merge`. The human picks, and neither is invoked from here. Name the branch and the
base so the recommendation is copy-pasteable. For an `abandoned` outcome, skip this handoff and
follow the branch-disposal path below.

For `abandoned`, there is nothing to hand off toward — do not remove any worktree; frame and make
the branch-delete offer per
[specs-conclude/abandoned.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-conclude/abandoned.md)
§The branch-delete offer, informed rather than defensive, default **keep**, and record the choice
and fate in the report.
**Done when:** the gate ran green on the branch and the handoff was named, or the run recorded why
nothing could be handed off — a red gate, or (abandoned) the branch's own fate decided instead.

### 7. Report

```bash
cq components read ${CLAUDE_PLUGIN_ROOT}/assets/references/specs-develop/report-mold.md \
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
   `/quenching:specs:develop`'s discoveries stage to close, and they are easiest to lose at exactly
   this moment.

Close on §The next-step block, its recommended line naming step 6's handoff — `/quenching:git:pr:create`
or `/quenching:git:merge`, whichever was recommended, or `/quenching:specs:develop <id>` when
block 3 has rows and that needs settling first.
**Done when:** path, outcome, records, both `/docs/` passes and the next-step block are all
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
  green one.
- **Never run the gate over a branch that is behind its base.** Report the count and stop; bringing
  it up to date is a write, and which way is the human's call.
- **This command's own commits end at step 5.** Nothing it does writes to the branch after the gate
  in step 6 — the merge, the PR, and whatever they each commit belong entirely to
  `/quenching:git:merge` and `/quenching:git:pr:create`, run separately, on the human's own word.
- Never overwrite the `writeOnce` `outcome` record to make reality fit — report the disagreement
  instead, and never edit the frontmatter to get past `cq specs record`'s refusal.
- Never re-run a stage whose signal is already set without saying so and being asked to.
- Never re-write a rule a task already wrote into `/docs/standards/` during execution — concluding
  syncs nothing.
- Never settle a release obligation for an **abandoned** spec, and never invent one no standard
  states.
- Never bulk-copy a spec into `/docs/`; only what outlives it crosses.
- Never distil an abandoned spec's decisions as adopted knowledge; `background` is the ceiling.
- Never edit or delete anything already in `archive/`, with exactly one exception, onto the spec
  this run is closing: the distillation's `## Outcome` append, which records a fact that did not
  exist at the archive move and revises nothing the spec claimed. Never touch a spec other than
  that one, nor an archived spec from an earlier run.
- Never rewrite history: no amend of a task commit, no force-push, no `--no-verify` and no
  `--no-gpg-sign` on the commits this command makes.
