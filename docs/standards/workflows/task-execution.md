---
type: standard
title: Task execution contract
description: How a spec's task is executed — the verification policies, the failure budget, commit-per-task, the two-level review split, and the delegation and [P] disjunction rules
resource: plugins/claude-quenching/skills/quenching-specs-apply/, plugins/claude-quenching/assets/bin/specs.py, plugins/claude-quenching/assets/specs/templates/spec.md
tags: [workflows, specs, execution, verification, commits, delegation]
timestamp: 2026-07-26
audience: both
authority: current
source: refine-and-execute-specs-flow plan (sections 5-6)
maintainer: claude-quenching
---

# Task execution contract

A task is not done when the code is written. It is done when it **ran**, its diff was
**reviewed**, and it is **committed on its own**. This standard is the contract;
`quenching-specs-apply/references/execution.md` is the procedure that implements it.

## The precondition: a clean tree

Implementation refuses to start while `git status --porcelain` is non-empty. Commits are per task,
and a commit cannot separate the task's diff from an unrelated edit already sitting in the tree.
The human may override, in which case the first commit carries the pre-existing changes **and the
report says so**. Not a git repo → no isolation and no commits, stated once; never `git init` on
the human's behalf.

## Verification is declared per spec, never decided mid-implementation

the spec's frontmatter carries `verification`, written at propose time by `specs.py new --verification`:

| Policy | Runs each task's `verify:` | Fits |
| --- | --- | --- |
| `per-task` | after every task | a fast suite, or tasks where each step can break the last |
| `per-section` *(default)* | after each `## N.` section's last task | most repos — a section is the smallest independently shippable unit |
| `end-of-plan` | once, after the final task | a slow suite, or work that is meaningless until the whole plan lands |

A single global policy would be right for a fast suite and wrong for a slow one, and the spec's
author is the only party who knows which this repo has. Declaring it at propose time means
implementation never guesses and never interrupts the human mid-task to ask.

A task with no `verify:` falls back to the spec's `## Validation`, then to the repo's own
checks. **No verification available at all is reported, never silently passed** — a checkbox must
not imply a proof that never happened.

## A blocked task is a visible marker, not a hidden counter

On failure the code is fixed and the check is run again. Two bounds:

- **Re-read from scratch after two consecutive failures** — the task text, its declared files, and
  the *current* diff. Two failures in a row nearly always means the third attempt is repairing a
  mental model that was already wrong at the first, and each further patch compounds it.
- **Stop when attempts stop converging**, and write the reason into the file:

  ```bash
  specs.py task --spec <slug> --block <id> --reason "<why, one line>"
  ```

  which produces `- [!] <id> <title> — blocked: <reason>` in `## Tasks`. Not a sixth try, not a
  different approach, not a weaker check.

A blocked task is **distinguishable from an untried one**: `specs.py next` skips `[!]` and offers
the following task, so one bad task never stalls a spec. A human resumes it by fixing the cause and
returning it to `- [ ]` (`specs.py task --uncheck <id>`) — never merely to retry the same approach.

**`--block` requires `--reason`**; the tool refuses without one.

### Why the marker replaced the counter

The earlier contract kept an attempt count in a the spec's frontmatter sidecar and hard-stopped at five. The
count was machine state a human never saw: a task went quiet after five failures with **no trace of
why**, and the only way to resume was a `--reset-attempts` incantation that bought five more
attempts at the same wrong approach.

The objection to a third glyph was that `- [!]` would break consumers of `CHECKBOX_RE` and would not
survive hand-editing. Both were answered rather than argued away: the regex admits the glyph
explicitly, and a marker a human can read is *more* likely to survive hand-editing than a sidecar
they never open — because the reason is right there in the line they are already looking at.

## Review splits by cost into two levels

| | Per-task self-review | End-of-plan review |
| --- | --- | --- |
| Scope | one task's diff | the whole plan's diff |
| When | before every commit | once, after the last task, **offered** |
| Looks for | reuse · useless defense · obvious comment · dead code | coherence, layering, whether the parts add up |

The four-item check is cheap enough to run every time; a full-diff read is not, and running it per
task would triple the cost of a three-line change. Only the whole diff can show what no single
task could — two tasks that solved the same problem differently, an abstraction that wanted
extracting once the third caller appeared, a declared `## Impact` path nothing ever wrote.

## One commit per task

```
plan/<plan-name>: <task-id> <task title>
```

`git revert` then undoes exactly one task, `git log` reads as the spec's task list, and a review
can walk it step by step. N tasks piled into one uncommitted blob gives none of that, and makes
the branch isolation offered at the start buy nothing.

### Hard rules

These are the ways an implementation ships a lie behind a green checkbox. Each is absolute, with
no "just this once":

- Never disable, skip, `xfail`, or delete a test to make a task pass.
- Never edit the `verify:` command, the test, or the assertion so it stops failing. Change the
  code, or report the task blocked.
- Never `git commit --no-verify`. A failing hook is a finding to report, not an obstacle to route
  around. Same for `--no-gpg-sign`.
- Never amend or rewrite an earlier task's commit; never force-push.
- Never tick a checkbox for work that was not verified.

## Delegation is permitted; the orchestrator never is

A per-task executor sub-agent is permitted when the task **declares `files:`** and **touches no
`docs/`**, pinned to the session model — never `haiku`, which writes production code here.

The orchestrator keeps, without exception: plan selection, the isolation offer, every
confirmation, every `specs.py task --check` flip, every attempt record, every `docs/standards/`
write, the commit, and the decision to pause.

### This is not `context: fork`, and that rule is untouched

The standing rule forbids `context: fork` **on these skills**, because a forked context cannot
present the mid-flow confirmations every sweep depends on — the conversation carrying the human's
OK would be out of reach.

Dispatching a sub-agent for a bounded, file-scoped unit of work does the opposite: the
orchestrator **stays in the live conversation**, exactly as `quenching-docs-glossary-backfill` and
`quenching-docs-import` already dispatch. One moves the decision-maker out of reach; the other
sends a worker out and keeps the decision-maker in place. They are different mechanisms about
different things, and no future sweep may "fix" one into the other.

## Parallelism must be earned

Two tasks run concurrently only when all three hold:

1. a `[P]` marker was set on both **at propose time** — never inferred while applying;
2. their declared `files:` sets are **provably disjoint**;
3. neither writes into `docs/`.

Serial is the default and needs no marker. Without proven disjunction, parallel execution trades
wall-clock for merge conflicts and loses on both.

The disjunction is **checked mechanically, not judged in prose**: `specs.py parallel --spec <n>`
reports each group and exits **0** when every marked group is eligible, **1** when any overlaps or
lacks `files:`. Two paths conflict when they are the same file or when one is a directory
containing the other. A group is bounded to one `## N.` section, so a run never straddles two
independently shippable units.
