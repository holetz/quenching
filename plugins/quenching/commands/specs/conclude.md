---
description: Close ONE spec out — review the whole branch, write the /.knowledge/ the work revealed, archive, distil, and merge LAST. Triggers on "conclude this spec", "close it out", "wrap up the plan", "review the branch", "merge this plan", "archive this spec", "abandon this spec", "it will not be built". Everything lands on the work branch, so one merge carries the code, the emergent docs, the archived spec and the distillation, and nothing is ever committed to the base after it. Settles pre-merge release obligations. Resumable: the reviewed, merge and outcome records plus git say which stages already ran. Archiving as done refuses while boxes are open unless forced; abandoned is always allowed and distils at most a background note. Never infers the outcome or treats staleness as abandonment. Not for: building a spec's tasks → /quenching:specs:execute; sharpening or interrogating one → /quenching:specs:develop; creating one → /quenching:specs:create; taking a branch or worktree → /quenching:specs:execute; ranking the whole front → /quenching:specs:triage.
argument-hint: [slug] [--outcome done|abandoned]
allowed-tools: Bash, Read, Glob, Grep, Write, Edit, AskUserQuestion, Skill
model: opus
---

# /quenching:specs:conclude — review, archive, distil, merge

**Input**: `$ARGUMENTS` — the spec slug, and optionally its outcome.

Closes ONE spec out. Four things happen, in this order, and each is a separate decision: the whole
branch is **reviewed**, the `/.knowledge/` the work *revealed* is **written**, the spec is **archived and
distilled** into the OKF bundle, and only then is the branch **merged**.

**The merge is the last action, without exception.** Everything above it happens on the work
branch, so a single merge carries the code, the emergent docs, the archived spec and the
distillation together — and reverting that merge reverts the spec's whole footprint. What used to
make this impossible was the `merge:` record itself: a merge sha exists only *after* the merge, so
the stamp and the distillation were stranded on the base branch behind it. Recording the merge
**subject** instead — known before the merge — leaves nothing that must be written afterwards.

**Why this is not part of `/quenching:specs:execute`.** Every step here is a different scale of judgment from
building a task: the branch review reads the whole diff rather than one task's, the merge is
irreversible and needs its own confirmation, and the distillation is the single bridge into
`/.knowledge/`. Bolting them onto the end of the build meant a run that died after task nine had to redo
tasks one through eight to reach them.

**This command is resumable, and that is a property of the data, not of a session.** Frontmatter
records the human judgments (`reviewed`, `merge`, `outcome`); git and the filesystem record
everything else. A second call reads both and skips what already happened — see §Resuming.

The distillation doctrine — what crosses into `/.knowledge/`, what stays, and how it is graded — lives in
[specs-conclude/distill.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-conclude/distill.md)
§What crosses, what stays. The merge strategies, the squash caveat and the **read-if-present**
rule for a target's `/.knowledge/standards/git/**` live in
[specs-execute/git.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-execute/git.md)
§Merge strategies §The squash caveat §The read-if-present rule. The layout, the gates and the
`cq specs` surface live in
[specs-develop/spec-driven.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-develop/spec-driven.md)
§The `specs/` layout §The gates and the stage-scoped explicit-none rule §The `cq specs` tool
surface §The report mold, which owns the shape step 7 prints in.
All three are cited, never restated.

## Resolving the tool

Resolve `cq specs` per
[align/tool-resolution.md](${CLAUDE_PLUGIN_ROOT}/assets/references/align/tool-resolution.md)
§Resolving the tool. Branch on the **exit code** (0 ok · 1 findings · 2 refusal) and the `--json`,
never on prose.

**Why `Bash` is unrestricted here.** Like `/quenching:specs:execute`, this command drives the target repo's
`git` — the branch diff, the merge, the branch cleanup — and re-runs the repo's own checks to
gate the merge. Its read-only siblings are scoped to `python3`/`py`.

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
- **An abandoned spec's branch is never merged on this command's initiative.** Partial work on a
  branch nobody adopted is history, not a change; offer to keep it or delete it, and default to
  keeping.
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
| PR opened, not merged | a `pr:` record present, `merge:` absent | never re-open a second PR — read `gh pr view <number> --json state` for the number `pr:` names; `MERGED` → stamp `merge:` now with the strategy step 4 would have chosen and continue from step 7; still `OPEN` → report the link and stop again, exactly the minimal-gear stopping point, unless the human now asks to merge it |
| merge stamp | a `merge:` record in frontmatter | skip the stamp; the merge itself may still be pending |
| validation gate | no record — it is a verdict on the tree as it stands *now* | always re-run it; a green run from before the last commit proves nothing |
| merge | `git branch --merged` lists the work branch | skip; never merge twice |

The last two rows are **separate signals** now that the stamp precedes the merge: a run interrupted
between them leaves `merge:` recorded and the branch unmerged, which is recoverable — re-read the
recorded subject and perform the merge with it. The reverse (merged but unstamped) can only come
from a merge this command did not make, and is a finding to report.

`reviewed` is `writeOnce: false` on purpose: a diff that changed and was read again is a new fact.
`merge` and `outcome` are `writeOnce: true` — if either is already set and reality disagrees, that
is a **finding to report**, never a value to overwrite.

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
Read task progress, the `## Outcome` state, and the records — `branch`, `reviewed`, `merge`,
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
one too (`git.md` §Where a branch comes from). No record, `work` equal to `base`, or no git → say
so and skip to step 4; there is no branch diff to read.
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

These land **on the branch**, in their own commit, so the rule ships with the code that proved it.
A `## Discoveries` line that gets a doc is resolved in place. No OKF bundle → skip silently.
**Done when:** the emergent docs are written and committed, or the offer was declined, or there is
no bundle.

### 4. Choose the merge strategy and route, then write `## Outcome` and archive
For `done` with a work ref of its own (`branch.work != branch.base` — in place there is nothing to merge), offer the strategies in
[git.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-execute/git.md) §Merge strategies with
**AskUserQuestion**, and state the trade in one line each. **When squash is chosen, offer NOT to
delete the branch** — a squash collapses every per-section commit, so each task's recorded
`subject:` resolves only while the branch survives. Say that plainly rather than deleting and
discovering it later.

**Then, separately, offer the route** — pull request, or local — per
[git.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-execute/git.md) §The pull-request route.
Offer it only where `gh` resolves the repository (`gh repo view` exits 0); with no route to offer,
say nothing and proceed local, silently — a repo with no GitHub remote is the ordinary case, not a
finding. **Under `fast-forward`, do not ask** — `gh pr merge` has no fast-forward mode, so the
route question answers itself; say so in one line and proceed local.

The choices come **before** `## Outcome` because the Outcome has to state them, and before the
`merge:` stamp in step 5 because that stamp records both. Nothing is merged yet — choosing the PR
route here is not the consent to push or open one; that lives in its own block in step 6.

`## Outcome` is the archive gate — the spec cannot move without it. Draft it, confirm it, write it:
```bash
cq specs section "<slug>" Outcome --write     # body on stdin
cq specs promote "<slug>" --to archive --outcome done|abandoned [--force]
```
For `done`: what shipped, what was left out, what the next reader needs — **including the merge
strategy and, when the PR route was taken, the PR itself**, because a squash changes what a future
reader can resolve and a merged PR is where the review and the checks still live. For `abandoned`:
the reason it will not be built is the whole content.

A refusal (exit 2) lists exactly what is missing or which boxes are open — surface it verbatim and
let the human decide; **never pass `--force` on your own initiative.** Commit the move on the
branch.
**Done when:** the strategy is chosen, the file is in `archive/` with its `outcome:` stamped and
committed, or the run stopped at a refusal the human declined to override.

### 5. Distil, settle the release obligations, and stamp the merge record — all on the work branch
This is the last writing step, and everything it writes lands on the **work branch**, before any
merge. Three things happen here, in this order.

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
silently. Commit what it writes **on the work branch**.

**Then settle the release obligations the repo's standards attach to the merge itself.** With an
OKF bundle present, read the `/.knowledge/standards/` subjects the branch diff touched and apply what they
require *of the merge* rather than of any one task — a version bumped across artifacts a standard
says must move together, a changelog entry, a manifest re-stamped. This is the only correct moment
for that class of edit: the whole branch is written, so what the release *is* is finally knowable,
and a bump made here starts from the base the branch is actually merging into rather than colliding
with a sibling spec that bumped to the same number days ago.

Nothing is invented. A repo whose standards attach nothing to a merge gets nothing, silently, and
so does a repo with no bundle. What a standard *does* require is presented as ONE plan with the
standard quoted, taken on one confirmation, and committed on the branch. A requirement the diff
already satisfies is reported as already done, never redone.

**Finally, stamp the merge record — on the local route only.** `merge:` is write-once, and the PR
route cannot know `pr:` until the PR exists, which happens after the gate in step 6; stamping here
with `pr` still unknown would burn the one write this record gets. **Local route, stamp it now**,
still on the branch, naming the subject the merge commit is about to carry:

```bash
cq specs record "<slug>" merge --set strategy=<chosen in step 4> \
  --set subject="plan/<slug>: merge (<strategy>)"
```

**PR route, stamp nothing here** — step 6 stamps `pr:` the moment the PR exists, then `merge:` if
that same run merges. `merge` is write-once: a spec already carrying one refuses (exit 2) with the
value it holds — the finding §Resuming describes, never a value to edit past.

Under `fast-forward` and `rebase` there is no merge commit to name, so the subject is an explicit
none — see
[git.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-execute/git.md)
§When there is no merge commit to name. `cq specs validate` reports a record that gets this
backwards either way (`sp-bad-merge`).

The archived spec now lives in `archive/`, so stamping it is one of the three edits this command
makes to a file already there — §Invariants names all three. Each touches *this* spec, closing
*this* run, and the alternative is a write on the base after the merge. Commit them on the branch.

For `abandoned` nothing is merged, so nothing is stamped **and no release obligation is settled** —
a version nobody adopted is a claim the history should not carry. The distillation above still runs.
**Done when:** the distillation offer was made and applied or declined, the release obligations were
applied, reported as already satisfied, or reported as none, and — for a `done` outcome on the local
route — `merge` is stamped, committed on the work branch. On the PR route, this step ends with
`merge` still unstamped; step 6 stamps it.

### 6. Prove it on the branch, then merge — the last action of this command
Nothing after this point writes anything.

**First the gate: re-run whatever the repo's `## Validation` names — on the WORK BRANCH, before
merging.** Run it from the checkout that carries the work (the worktree or branch this run is
standing on), so what it grades is the change being proposed.

**A failing check stops the merge.** Report which check failed and what it printed, leave the
branch unmerged, and let the human fix it *on the branch* — then this command is re-run. Never
merge past a red check, and never repair one with a commit: a fix belongs on the branch, where it
rides the same merge as everything else.

This is why the gate sits *before* the merge rather than after it. A check that runs afterwards can
only narrate — the base already carries the change, and the only repair left is a commit on the
base, which is the exact thing this ordering exists to prevent. Run on the branch, a red check
still has somewhere to be fixed.

**Nothing is stranded by stopping here.** On the local route `merge:` was already stamped in step
5; on the PR route it is stamped a few paragraphs below, immediately before the PR merges. Either
way, §Resuming names *stamped but unmerged* as the recoverable state: the next run re-reads the
recorded subject and merges with it — a gate failure before that point leaves nothing stamped at
all, which §Resuming also covers.

**The gate grades the branch, so the branch must already carry the base.** If the base moved since
the branch was cut, the merge produces a tree *neither* side ever validated, and a green gate says
nothing about it:

```bash
git rev-list --count plan/<slug>..<base>      # commits on the base the branch does not have
```

Non-zero → **say so and stop before the gate**, naming the count. Bringing the branch up to date is
a write, and it is the human's call which way (merge the base in, or rebase — the recorded task
subjects survive a rebase, the `merge:` stamp does not describe one). Never do it unasked, and
never run the gate over a branch you know is behind: that is a verdict about a tree that is not
being merged.

**An inconclusive result is not a green one.** A check that cannot tell "this failed" from "this
could not be measured" has returned no verdict — say which it was, and ask, rather than merging on
it. Where the repo keeps `standards/quality/surface-verification.md`, its §The five preconditions a
check must satisfy is where that distinction is defined for the command surface.

**Run the scope the diff justifies.** A harness that spawns fresh agent sessions bills for every
one, so a check with a `--only`-style selector gets the subset this branch can actually break — the
whole suite by reflex is the expensive way to learn nothing. When the repo's `## Validation` names
the scope, follow it; when it does not, run what it says and report the cost as a finding worth a
selector.

The gate passed. What happens next branches on the route chosen in step 4.

**Local route.** Find **which checkout holds the base**, and merge into it in place, using exactly
the subject recorded in step 5:

```bash
git worktree list --porcelain                    # which checkout has <base> checked out
git -C <that path> merge --no-ff plan/<slug> -m "plan/<slug>: merge (merge-commit)"
```

**Never `git checkout <base>`.** From inside a worktree that is
`fatal: '<base>' is already used by worktree at …` (exit 128) — so the form this command used to
carry was broken for exactly the isolation it recommends. `git -C` is one path, not two: from a
worktree it points at the main checkout, and from the main checkout it points at itself.

**When no checkout holds the base**, say which base was wanted, that nothing has it checked out,
and what would fix it (`git checkout <base>` in the main checkout, or a worktree of the base) —
then **stop without merging**. Never invent a checkout and never create a temporary one. `merge:`
was stamped in step 5, *before* the merge, so the run is resumable with nothing lost; refusing here
is the same refusal this command already makes over open boxes.

Then, **reading only**, the one assertion that can only be made afterwards: compare
`git -C <that path> log -1 --format=%s` against the recorded subject — from the same checkout the
merge landed in, since this run is not standing on the base. A mismatch is **reported as a
finding** — never repaired with another commit, because a commit on the base after the merge is the
exact thing this ordering exists to prevent. If something must be fixed, say so and let the human
start a new change.

**PR route.** Push and open the PR, stamping `pr:` the moment it exists. Under the orchestrator's
minimal-gear authorization this part asks nothing — irreversible cycle actions do not gate under
that gear. Every other run asks first, in the **same consented block** as the merge below, per
[git.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-execute/git.md) §The pull-request route:
show the remote, the name the branch pushes under, and the PR's title and body, and ask there —
choosing the PR route in step 4 was not this consent.

**On backend `github`, the body always ends with a `Refs #<issue>` line** — the spec's own locator
names the issue. The cross-reference puts both the PR and its branch in the issue's Development
panel at zero extra calls, which a branch alone can never buy (`spec-backend.md` §A record renders
onto a native surface too). Other backends have no issue to reference.

```bash
git push -u origin plan/<slug>
gh pr create --base <base> --title "<title>" --body "<body>

Refs #<issue-number>"
cq specs record "<slug>" pr --set number=<the PR's number> --set url=<the PR's URL> --set date=<today>
```

**Running under `/quenching:specs:orchestrate`'s minimal-gear authorization → stop here.** Do not
call `gh pr merge` and do not stamp `merge:` — report the PR link and end the run. The merge waits
on human review, exactly as convergence.md §The PR route promises; a later `conclude` run, or a
human merging by hand, finishes it — §Resuming's "PR opened, not merged" row is the resume path.

**Every other run → merge now**, in the same consented block as the push and the PR above:

```bash
cq specs record "<slug>" merge --set strategy=<chosen in step 4> \
  --set subject="plan/<slug>: merge (<strategy>)" --set pr=<the PR's URL>
gh pr merge <number> --merge|--squash|--rebase --subject "plan/<slug>: merge (<strategy>)"
```

**`--base <base>` is never omitted.** `gh pr create` without it targets the repository's GitHub
default branch, which in a repo running the develop/main flow deliberately stays `main`. `<base>` is
this spec's own resolved base — the one the local route merges into — so a spec cut from the
declared integration branch opens its PR there, never against the publication one, with no GitHub
setting having to change.

`fast-forward` never reaches this block — step 4 already ruled the PR route out under it, so
`gh pr merge`'s missing fast-forward mode is never a live gap. `cq specs record` refuses `pr:` set
under `fast-forward` regardless (`sp-merge-pr-no-route`), so a slip here is caught rather than
silently written.

Then, **reading only**, the assertion this route makes instead of comparing a local log line — the
base's local checkout has no reason to know about a merge that happened on the remote until told:

```bash
git -C <the base's checkout> pull --ff-only
gh pr view <number> --json state,mergeCommit
```

`state` must read `MERGED`. Anything else — `OPEN` after `gh pr merge` returned, a network error
mid-sequence — is **reported as a finding**, never repaired by re-running `gh pr merge` blind: read
the PR's actual state on GitHub first, because a repeated merge call against one already merged is
the failure mode this assertion exists to catch before it compounds.

**`## Validation` is not re-run here, on either route.** It gated the merge above, on the branch,
with the base already in it — so a second full run grades the same tree and buys a restatement at
full price. Where that price is a fleet of fresh agent sessions, it was the largest recurring cost
this command had.

**Then, when the merge exited 0 and this spec was isolated in a worktree, remove it** — run from
the checkout that holds the base, because nobody removes the tree they are standing in:

```bash
git -C <the base's checkout> worktree remove <the worktree path>
```

**Never `--force`, under any circumstance.** `git worktree remove` refuses a tree with modified or
untracked files on its own (`contains modified or untracked files`, exit 128), which is precisely
the irreversibility worth fearing — so the safety is already git's, and no prompt would buy more
than it costs. A clean tree leaves the disk silently; a refusal is **reported with the path and
git's own output verbatim**, and the worktree stays. Never retry it forced, and never offer to.

This runs only after a merge verified at exit 0 — a merge that failed or was refused above leaves
the worktree exactly where it is. Removing the worktree does not delete the branch: that stays the
separate offer it already was.

For `abandoned`, do not merge and do not remove the worktree. Offer to keep the branch (default) or
delete it, and record the choice in the report.
**Done when:** the gate ran green on the branch and the merge landed with its subject asserted, any
worktree was removed or its refusal reported, or the run recorded why nothing was merged — a red
gate among them, or (PR route, minimal-gear authorization) the PR opened and `pr:` was stamped with
the merge deliberately left for later.

### 7. Report

```bash
cq components read ${CLAUDE_PLUGIN_ROOT}/assets/references/specs-develop/spec-driven.md \
  --sections "§The report mold" --rules-only
```

Emit §The report mold. The single-spec header line carries the archived locator and the outcome; four
body blocks:

1. **At close** — fixed. Task progress, `reviewed` / `pr` / `merge` / `branch` as they now stand,
   and — for an abandonment — that nothing was adopted.
2. **The review** — fixed. What it found and what was done about it, the docs written in step 3 and
   step 5, and what the pre-merge gate returned. §Quoting a tool's own output governs the gate's
   result, which means **a check that came back inconclusive is named as such, never counted as
   passed**.
3. **The worktree** — fixed when there was one. Removed, or kept with git's refusal quoted. It left
   a directory on disk, and this report is the only place the human learns it is gone — an
   unreported removal is indistinguishable from one that never ran.
4. **Unresolved `## Discoveries`** — optional, each line named. They are
   `/quenching:specs:develop`'s discoveries bank to close, and they are easiest to lose at exactly
   this moment.

Close on §The next-step block. `/quenching:specs:develop <slug>` when block 4 has rows,
`/quenching:specs:continue` to be handed the next spec — the front has moved on, and this is the
moment a human most needs telling where.
**Done when:** path, outcome, records, the worktree's fate, both `/.knowledge/` passes and the next-step
block are all reported.

## Invariants to never violate

- Never infer the outcome. `done` and `abandoned` are the human's word, always.
- Never treat staleness as evidence of abandonment.
- Never pass `--force` unprompted — a refusal is information, not an obstacle. On
  `git worktree remove` never pass it **at all**: git's refusal over modified or untracked files is
  the safety, and forcing past it destroys uncommitted work at the moment the human is least
  watching.
- Never merge an abandoned spec's branch, and never merge without the human choosing the strategy.
- **Never `git checkout <base>` to merge.** Merge into the checkout that already holds the base with
  `git -C`; when none does, stop and say so rather than manufacturing one.
- **Never write anything after the merge.** The merge is the last action; anything the post-merge
  assertion catches is a finding to report, not a commit on the base.
- **Never merge past a red `## Validation` gate**, and never count an inconclusive check as a green
  one. The gate runs on the branch precisely so that a failure still has somewhere to be fixed —
  merging anyway spends that.
- **Never run the gate over a branch that is behind its base.** Report the count and stop; bringing
  it up to date is a write, and which way is the human's call.
- Never delete a branch after a **squash** without saying what it costs: each task's recorded
  `subject:` stops resolving.
- Never overwrite a `writeOnce` record (`merge`, `outcome`) to make reality fit — report the
  disagreement instead. Every record here is stamped with `cq specs record`, which refuses on its
  own; editing the frontmatter to get past that refusal is the thing the refusal exists to stop.
- Never re-run a stage whose signal is already set without saying so and being asked to.
- Never re-write a rule a task already wrote into `/.knowledge/standards/` during execution — concluding
  syncs nothing.
- Never settle a release obligation for an **abandoned** spec, and never invent one no standard
  states — a bump nobody asked for is a release claim this command had no authority to make.
- Never bulk-copy a spec into `/.knowledge/`; only what outlives it crosses.
- Never distil an abandoned spec's decisions as adopted knowledge; `background` is the ceiling.
- Never edit or delete anything already in `archive/`, with exactly three exceptions, all onto the
  spec this run is closing: the distillation's `## Outcome` append and the `merge:` stamp in step
  5, and the `pr:` stamp in step 6 on the PR route. Each records a fact that did not exist at the
  archive move and has nowhere earlier to live — the two-clause test a further exception is argued
  against, never assumed into. None revises what the spec claimed. Never touch a spec other than that one, nor an archived spec from an earlier run.
- Never rewrite history: no amend of a task commit, no force-push, no `--no-verify` and no
  `--no-gpg-sign` on the commits this command makes.
