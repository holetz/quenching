---
type: standard
title: Task execution contract
description: How a spec's task is executed — the verification policies, the failure budget, commit-per-task, the two-level review split, the four-event Handoff refresh cadence, and the delegation and [P] disjunction rules
resource: plugins/quenching/commands/specs/execute.md, plugins/quenching/commands/specs/conclude.md, plugins/quenching/commands/specs/isolate.md, plugins/quenching/assets/references/specs-execute/execution.md, plugins/quenching/assets/references/specs-develop/artifacts.md, plugins/quenching/assets/references/specs-isolate/git.md, plugins/quenching/assets/bin/specs.py, plugins/quenching/assets/specs/templates/spec.md
tags: [workflows, specs, execution, verification, commits, delegation, handoff]
timestamp: 2026-07-31
audience: both
authority: current
source: refine-and-execute-specs-flow plan (sections 5-6); the review split re-homed by the specs-flow-consolidation plan; the tick-before-commit ordering by the move-conclude-merge-last plan (task 5.3); the falsifiable-verify rule measured by the verify-allowed-tools-enforcement spec (2026-07-28); the four-event Handoff cadence by the cut-specs-execute-turns spec, measured on a 13-task run (transcript 985b372b, 2026-07-30)
maintainer: quenching
---

# Task execution contract

A task is not done when the code is written. It is done when it **ran**, its diff was
**reviewed**, and it is **committed on its own, with its own checkbox inside that commit**. This standard is the contract;
`assets/references/specs-execute/execution.md` is the procedure that implements it, and
[plan-git-record.md](plan-git-record.md) is what the resulting commits are recorded as.

## The precondition: a clean tree

Implementation refuses to start while `git status --porcelain` is non-empty. Commits are per task,
and a commit cannot separate the task's diff from an unrelated edit already sitting in the tree.
The human may override, in which case the first commit carries the pre-existing changes **and the
report says so**. Not a git repo → no isolation and no commits, stated once; never `git init` on
the human's behalf.

## Verification is declared per spec, never decided mid-implementation

The spec's frontmatter carries `verification`, written at creation by `specs.py new --verification`:

| Policy | Runs each task's `verify:` | Fits |
| --- | --- | --- |
| `per-task` | after every task | a fast suite, or tasks where each step can break the last |
| `per-section` *(default)* | after each `## N.` section's last task | most repos — a section is the smallest independently shippable unit |
| `end-of-plan` | once, after the final task | a slow suite, or work that is meaningless until the whole plan lands |

A single global policy would be right for a fast suite and wrong for a slow one, and the spec's
author is the only party who knows which this repo has. Declaring it up front means execution
never guesses and never interrupts the human mid-task to ask.

A task with no `verify:` falls back to the spec's `## Validation`, then to the repo's own
checks. **No verification available at all is reported, never silently passed** — a checkbox must
not imply a proof that never happened.

### A `verify:` that cannot fail proves nothing when it passes

A declared check is a claim about what it would catch, and that claim is itself unverified until
someone runs it against the tree **before** the fix. Run it there first: it must **exit non-zero**.
Only then does its later exit 0 mean the task did something.

The failure is not hypothetical and does not look like a failure. A task declared
`verify: ! grep -rn "is the enforcement" …` to prove three sentences were deleted. Two of the three
lived in files where the phrase wraps across a line break, and `grep` matches within a line — so
against the pre-fix tree the pattern found **1 of 3**, and the task would have ticked green with two
of its three targets untouched. Replaced with a multiline check, proven to exit 1 before the fix and
0 after.

This is the sibling of [../quality/parse-honesty.md](../quality/parse-honesty.md) from the other
side: there, a tool misread its input and reported a confident finding about a string it never held.
Here nothing is misread — the matcher simply cannot express the thing being proven, and a check that
cannot express its claim reports success indistinguishable from the real one. **Falsify the check
before trusting it**, and treat "it passed" as evidence only once "it failed on purpose" is on the
record.

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

The earlier contract kept an attempt count in a `.specs.json` sidecar and hard-stopped at five. The
count was machine state a human never saw: a task went quiet after five failures with **no trace of
why**, and the only way to resume was a `--reset-attempts` incantation that bought five more
attempts at the same wrong approach.

The objection to a third glyph was that `- [!]` would break consumers of `CHECKBOX_RE` and would not
survive hand-editing. Both were answered rather than argued away: the regex admits the glyph
explicitly, and a marker a human can read is *more* likely to survive hand-editing than a sidecar
they never open — because the reason is right there in the line they are already looking at.

## Review splits by cost into two levels, owned by two commands

| | Per-task self-review | Branch review |
| --- | --- | --- |
| Scope | one task's diff | the whole branch, `<base>...HEAD` |
| Owner | `/specs:execute`, inside the task | `/specs:conclude`, step 2 |
| When | before every commit | once, before the merge |
| Looks for | reuse · useless defense · obvious comment · dead code | coherence, layering, whether the parts add up |

The four-item check is cheap enough to run every time; a full-diff read is not, and running it per
task would triple the cost of a three-line change. Only the whole diff can show what no single
task could — two tasks that solved the same problem differently, an abstraction that wanted
extracting once the third caller appeared, a declared `## Impact` path nothing ever wrote, a
standard the diff contradicts.

The second level is a **separate command**, not an offer at the end of the first: it reads a
different scale of diff, it precedes an irreversible merge, and bolting it onto the build meant a
run that died after task nine had to redo tasks one through eight to reach it. That it ran is
recorded as `reviewed`, per [plan-git-record.md](plan-git-record.md).

## One commit per task — literally one

```
plan/<slug>: <task-id> <task title>
```

`git revert` then undoes exactly one task, `git log` reads as the spec's task list, and a review can
walk it step by step. N tasks piled into one uncommitted blob gives none of that, and makes the
isolation taken at the start buy nothing.

The heading is now literally true. The anchor written back onto the task line is the commit's
**subject**, not its sha — [plan-git-record.md](plan-git-record.md) §The task→commit link is the
commit's own subject — and a subject is known *before* the commit exists. So the box is ticked
first and the commit carries it:

```bash
specs.py task --spec <slug> --check <id> --subject "<subject>"
git add <the task's files> <the spec file> && git commit -m "<subject>"
```

Under the sha anchor this was impossible: the tick had to follow the commit it recorded, so every
task cost a second, bookkeeping commit and "one commit per task" was an aspiration the mechanism
contradicted. Those commits no longer exist.

If the commit fails, **undo the tick** so no box claims a commit that does not exist. If a
`commit-msg` hook *replaced* the subject, report the drift as a finding and write nothing —
repairing the record after the commit is the ordering this contract exists to prevent.

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

## The Handoff refresh cadence is four events

`## Handoff` carries the state of play a fresh executor would need and **cannot derive**: a parallel
session in the checkout, an unversioned hook, a design flaw found mid-build. Everything a resumed
run *can* derive — which tasks are done, which commit carried each one — already lives in `git log`
and in the `subjects` `specs.py status` returns, so the Handoff is not the resumption trail and
must not be rewritten as though it were.

It is refreshed on exactly four events:

| Event | Why it changes what nothing derives |
| --- | --- |
| the run **pauses** | the reason for stopping exists nowhere else |
| a **blocked task** is written | the attempts and why they stopped converging are not in the diff |
| a **discovery recorded** | a discovery is by definition a finding nothing else holds yet |
| the run's **last commit** | that commit is where the next run picks up |

The cadence it replaced was *after each committed task*. Measured on a 13-task run, four rewrites of
~400 words each were **~90% identical** to one another: the section is sent with every task, so the
cost is paid on both sides, and near-identical rewrites buy nothing on either.

### A cadence trigger can never be a judgment

The rule *that* one replaced was "rewrite it when it goes stale", and it failed for a structural
reason: an unattended run never judges that something has gone stale. "Rewrite it when the
underivable state changed" is the same failure wearing a different name — it asks the run to
*evaluate* rather than to *observe*.

The four triggers above are all moments the body has **just finished doing something**, never
moments it appraises something. That is the property to preserve under any future edit: a trigger
must name an act, not an assessment.

Refreshing per `## N.` section, riding on the `verification` policy, was the strongest alternative —
mechanical, judgment-free, and five rewrites instead of thirteen. It loses because it still rewrites
when nothing changed.

## Delegation is permitted; the orchestrator never is

A per-task executor sub-agent is permitted when the task **declares `files:`** and **touches no
`docs/`**, pinned to the session model — never `haiku`, which writes production code here.

The orchestrator keeps, without exception: spec selection, the isolation offer, every
confirmation, every `specs.py task --check` flip, every block marker, every `docs/standards/`
write, the commit, and the decision to pause.

### This is not `context: fork`, and that rule is untouched

The standing rule forbids `context: fork` **on these commands**, because a forked context cannot
present the mid-flow confirmations every sweep depends on — the conversation carrying the human's
OK would be out of reach.

Dispatching a sub-agent for a bounded, file-scoped unit of work does the opposite: the
orchestrator **stays in the live conversation**, exactly as `/docs:glossary-backfill` and
`/docs:import` already dispatch. One moves the decision-maker out of reach; the other
sends a worker out and keeps the decision-maker in place. They are different mechanisms about
different things, and no future sweep may "fix" one into the other.

## Parallelism must be earned

Two tasks run concurrently only when all three hold:

1. a `[P]` marker was set on both **when the tasks were written** — never inferred while building;
2. their declared `files:` sets are **provably disjoint**;
3. neither writes into `docs/`.

Serial is the default and needs no marker. Without proven disjunction, parallel execution trades
wall-clock for merge conflicts and loses on both.

The disjunction is **checked mechanically, not judged in prose**: `specs.py parallel --spec <n>`
reports each group and exits **0** when every marked group is eligible, **1** when any overlaps or
lacks `files:`. Two paths conflict when they are the same file or when one is a directory
containing the other. A group is bounded to one `## N.` section, so a run never straddles two
independently shippable units.
