---
allowed-tools: Bash(cq:*), Bash(cq.cmd:*), Bash, Read, Glob, Grep, Write, Edit, AskUserQuestion, Skill
---


# /quenching-specs conclude — review, distil, sweep, hand off — and archive after the merge

**Input**: `$ARGUMENTS` — the spec id, and optionally its outcome. A conductor launched with
`--autonomous` adds the word `autonomous`; for a `done` outcome the run then opens the PR itself
after the green gate, and the `spec-orchestrator` adopts that PR on the `spec-verifier` PASS
instead of opening a second.

Closes ONE spec out in two moments, split by the merge. **Before the merge**, five things happen,
in this order, and each is a separate decision: the whole branch is **reviewed**, the `/docs/` the
work *revealed* is **written**, `## Outcome` is **written** and the spec **distilled** into the OKF
bundle, the project's own automation is **swept** for what the run revealed about it — every real
defect captured as its own spec, for another session — and the pre-merge gate is **proven green** —
then the run **stops**, naming `/quenching-git pr-create` or `/quenching-git merge` as the human's
own next command — except that a spec recorded at `low` complexity chains directly to
`/quenching-git pr-create` through `Skill` after the green gate; under `autonomous` that same
invocation carries the word `autonomous` and runs unasked. **After the merge**, and only then, the
spec is **archived** and its worktree released (step 8).

**A `done` spec is archived after its merge, never before.** The spec store is a git ref, not a
folder inside the PR: an archive is visible to every reader the moment it is written, while the PR
it describes can still stall, fail its checks or be closed. `specs_write(verb="promote", spec=<id>, to="archive",
outcome="done")` refuses while the work ref is not in `origin/<base>`, and the CLI's `--force` does
not reach that refusal. The post-merge close is one verb, `specs_write(verb="reconcile", write=true)`, and every route to a
merge ends in it: this command resumed after the merge, `/quenching-git merge`, the
`spec-orchestrator` after `git_external(verb="pr_merge")`, and the reconciliation at the open of
`/quenching-specs execute`, `orchestrate` and this command.

**Done work ends on the work branch; abandoned close-out writes land in the checkout holding the
base.**

**One file per step.** Each step below keeps its `**Done when:**` here; how to run it lives in the
step's own file, which a run loads when that step runs and not before. The references a step cites
(distillation, the spec layout and gates, the tool surface, the report mold, tool resolution) are
cited by that step's file, never here. Each step file also carries the doctrine, the resume signal
and the `autonomous` answer that belong to it.

## Resuming

Each stage has one durable signal (`reviewed`, `## Outcome` filled, the diff, a merge record); a
stage whose signal is already set is **reported and skipped**, not repeated, and a gate is always
re-run. Never re-run a stage whose signal is set without saying so and being asked to.

## Under `autonomous`

A run whose input carries `autonomous` has no human and no decision sheet: it asks nothing. Every
point where a step would ask takes the one answer written in that step, the narrowest that lets it
run, and nothing outside it is granted. A case a step sends to `needs-human` stops the run with
`STATE: blocked` and `NOTE: needs-human: <the question>`; a red gate is `STATE: failed`.

## Workflow

### 1. Resolve the spec, the outcome, and what already happened

Run it from [step 1](.claude/skills/quenching-specs/references/specs-conclude/step-1-resolve.md), read whole.

**Done when:** one spec, one outcome, and the list of stages still to run are all settled.

### 2. Review the whole branch diff

Run it from [step 2](.claude/skills/quenching-specs/references/specs-conclude/step-2-review.md), read whole.

**Done when:** the diff was read and `reviewed` is stamped, or the run recorded why there was
nothing to review.

### 3. Write the `/docs/` the work revealed

Run it from [step 3](.claude/skills/quenching-specs/references/specs-conclude/step-3-docs.md), read whole.

**Done when:** the emergent docs are written and committed, or the offer was declined, or there is
no bundle.

### 4. Write `## Outcome`

Run it from [step 4](.claude/skills/quenching-specs/references/specs-conclude/step-4-outcome.md), read whole.

**Done when:** `## Outcome` is written — and, for `abandoned`, the spec is in `archive/` with its
`outcome:` stamped — or the run stopped at a refusal the human declined to override.

### 5. Distil, and settle the release obligations

Run it from [step 5](.claude/skills/quenching-specs/references/specs-conclude/step-5-distil.md), read whole.

**Done when:** the distillation offer was made and applied or declined, and the release obligations
were applied, reported as already satisfied, or reported as none.

### 6. Sweep the flow itself, and capture what it owes

Run it from [step 6](.claude/skills/quenching-specs/references/specs-conclude/step-6-sweep.md), read whole.

**Done when:** every evidenced candidate is captured as its own spec or declined in the report, and
none was developed in this run.

### 7. Prove the gate green, then hand off

Run it from [step 7](.claude/skills/quenching-specs/references/specs-conclude/step-7-gate.md), read whole.

**Done when:** the gate ran green on the branch and the handoff was named, or the run recorded
why nothing could be handed off — a red gate, or (abandoned) the branch's own fate decided instead;
and the reservation of a finished build was released.

### 8. After the merge: archive and release the worktree

Run it from [step 8](.claude/skills/quenching-specs/references/specs-conclude/step-8-archive.md), read whole.

**Done when:** the spec is in `archive/` with `outcome: done`, or its `needs-human` row is reported;
and its slot was released, its legacy worktree retired, or the refusal reported.

### 9. Report

Run it from [step 9](.claude/skills/quenching-specs/references/specs-conclude/step-9-report.md), read whole.

**Done when:** path, outcome, records, both `/docs/` passes, what the sweep captured, the target
acceptance line and the next-step block are all reported.

## Invariants to never violate

- Never infer the outcome. `done` and `abandoned` are the human's word, always — under `autonomous`,
  the explicit `--outcome` the caller passed, and nothing else (§Under `autonomous`).
- Never treat staleness as evidence of abandonment.
- Never pass `--force` unprompted — a refusal is information, not an obstacle.
- Never hand off an abandoned spec's branch toward a merge — offer to keep or delete it instead.
- **Never `git branch -D`, at all**, when framing the abandoned branch-delete offer — git's own
  refusal over a not-fully-merged branch is the safety, and forcing past it destroys the only copy
  of work nobody adopted.
- **Never hand off past a red `## Validation` gate**, and never count an inconclusive check as a
  green one.
- **Never run the gate over a branch that is behind its base.** Report the count and stop; bringing
  it up to date is a write, and which way is the human's call. Under `autonomous` the call is made:
  the base is merged in (step 7), never rebased.
- **Never archive a `done` spec before its merge.** Step 4 writes `## Outcome`; only step 8, after
  the merge, archives — and `promote`'s own refusal is the second barrier, not the first.
- **This command's own commits end at step 5.** Nothing it does writes to the branch after the gate
  in step 7, except the base merge `autonomous` runs before that gate — the merge, the PR, and whatever they each commit belong entirely to
  `/quenching-git merge` and `/quenching-git pr-create`, run separately, on the human's own word.
- **A pre-existing red is never waved off nor muted**: a contained fix is a declared `[fix-preexistente]`
  commit, anything else is a captured spec, and the gate stays red until one of them lands.
- **Never develop a swept candidate in the run that found it.** Step 6 captures; the design and the
  go belong to the session that takes the spec, and only the human asking for that improvement in
  this same run makes it a new `create`. Never open a sweep spec without the evidence that named
  it, and never open a second one for a defect an open spec already covers.
- **Never let the sweep judge the delivered change.** The product's defects are the branch's, and
  the review already owns them; a candidate that is really the change's own defect belongs to
  `## Discoveries`, not to a new spec.
- Never overwrite the `writeOnce` `outcome` record to make reality fit — report the disagreement
  instead, and never edit the frontmatter to get past `specs_write(verb="record")`'s refusal.
- Never re-run a stage whose signal is already set without saying so and being asked to.
- Never re-write a rule a task already wrote into `/docs/standards/` during execution — concluding
  syncs nothing.
- Never settle a release obligation for an **abandoned** spec, and never invent one no standard
  states.
- Never bulk-copy a spec into `/docs/`; only what outlives it crosses.
- Never distil an abandoned spec's decisions as adopted knowledge; `background` is the ceiling.
- Never edit or delete anything already in `archive/`. The distillation's `## Outcome` append
  lands before the archive, on the spec this run is closing; never touch a spec other than that
  one, nor an archived spec from an earlier run.
- Never rewrite history: no amend of a task commit, no force-push, no `--no-verify` and no
  `--no-gpg-sign` on the commits this command makes.
