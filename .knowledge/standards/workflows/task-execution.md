---
type: standard
title: Task execution contract
description: How a spec's task is executed — the verification policies, `verify:` scoped at authoring, the failure budget, one commit per task while a section is open squashed to one commit per section at its boundary, the two-level review split, the four-event Handoff refresh cadence, and the delegation and [P] disjunction rules
resource: plugins/quenching/commands/specs/execute.md, plugins/quenching/commands/specs/conclude.md, plugins/quenching/assets/references/specs-execute/execution.md, plugins/quenching/assets/references/specs-develop/artifacts.md, plugins/quenching/assets/references/specs-execute/git.md, plugins/quenching/assets/bin/quenching/specs/**, plugins/quenching/assets/specs/templates/spec.md
tags: [workflows, specs, execution, verification, commits, delegation, handoff]
timestamp: 2026-08-11
audience: both
authority: current
source: refine-and-execute-specs-flow plan (sections 5-6); the review split re-homed by the specs-flow-consolidation plan; the tick-before-commit ordering by the move-conclude-merge-last plan (task 5.3), with the task→commit anchor moved from the subject to the sha by the configurable-spec-backend plan (task 4.4); the falsifiable-verify rule measured by the verify-allowed-tools-enforcement spec (2026-07-28); the four-event Handoff cadence by the cut-specs-execute-turns spec, measured on a 13-task run (transcript 985b372b, 2026-07-30); the inline-markup arm of the falsifiable-verify rule found twice while building that same spec (2026-07-31); the zero-errors-not-warnings arm measured on the stop-develop-offering-follow-up-specs branch (2026-08-03); the declared `cwd:` key by the declarar-o-cwd-de-uma-linha-verify spec (2026-08-05), proved by that same spec's own mixed-cwd `verify:` lines; the closed `files:` grammar by the fix-the-files-field-parser-splitting-on-commas-inside-parentheses spec (2026-08-06), whose repro was found in the route-commands-without-always-on-descriptions archive (2026-08-02); the failing-exit arm of the zero-errors rule added by reduzir-as-chamadas-az-por-escrita-no-azure-boards at its conclude, after a `verify:` asserting `cq specs validate` exit 0 was measured unsatisfiable on the day it was authored — the target workspace already carried seven warnings, and `validate` exits 1 on any finding; the section squash — one commit per section, the per-task chain and its retry safety net unchanged while the section is open — by the reduzir-commits-por-secao spec (2026-08-11)
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

### Dispatching a stage mid-flow costs the run its attribution

A command that hands a step to another command pays a price beyond the turns: the transcript's
`attributionSkill` pointer moves to the stage and, measured, almost never comes back — so the
conducting run's own remaining work is filed under the stage it dispatched. What that does to any
later count is owned by
[../automation/session-evidence.md](../automation/session-evidence.md) §What a command's run cost —
the stage is `closed: false`, its counts become an upper bound, and `mayIncludeTurnsFrom` names the
misread. **Cite that rule; never restate it here.**

The consequence for this contract is narrow and practical: **check before dispatching**. A step
whose delegate would report "nothing to do" is pure cost twice over — the turns, and the run's
attribution. Where there genuinely is something to delegate, dispatch anyway and accept the upper
bound; the delegate owns the work, and a measurement that says so is better than one that guesses.

## Verification is declared per spec, never decided mid-implementation

The spec's frontmatter carries `verification`, written at creation by `cq specs new --verification`:

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

### A task's `cwd:` says where `verify:` runs

A task MAY declare `cwd:`, the directory — relative to the repo root — its `verify:` runs from.
**Absent means exactly what it always meant**: the command runs from the session's root, or the
worktree's root under isolation. Write it only when the task's own check cannot resolve from
there — a plugin-internal tool that only resolves from its own subtree is the case that proves the
rule.

Declared at authoring time, on the task, next to `files:`/`pattern:`/`verify:` — never inferred by
the executor and never a spec-wide default, because one spec routinely needs two different answers
for two different tasks.

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

The line break is not the only way this happens, and the second way is worse because the phrase
looks contiguous. A check for `after\s+each\s+committed\s+task` found **3 of its 4** targets: in the
fourth the phrase read `after **each committed task**`, and the inline `**` sits between two words
that `\s+` expects to be adjacent. Same failure, no visible wrap. A third instance turned up in the
same run, inside a check written to *review* the first two.

**A check over prose normalizes before it matches** — strip `*`, `_` and backticks, collapse
whitespace, then look for the phrase. Read the whole file, never a line at a time. A matcher shaped
like the prose as it renders will keep missing the prose as it is written.

This is the sibling of [../quality/parse-honesty.md](../quality/parse-honesty.md) from the other
side: there, a tool misread its input and reported a confident finding about a string it never held.
Here nothing is misread — the matcher simply cannot express the thing being proven, and a check that
cannot express its claim reports success indistinguishable from the real one. **Falsify the check
before trusting it**, and treat "it passed" as evidence only once "it failed on purpose" is on the
record.

#### Three ways the falsification step is skipped, all measured on one spec

The rule above is old; what follows is what breaks when it is not applied, measured across the
`modularizar-specs-knowledge-components` spec's 59 tasks. Each form passes green, and each one
passes green for a *different* reason — so recognising one is not recognising the others.

**Inverted polarity — green means the work is NOT done.** Twelve tasks declared
`verify: git grep <the old pattern>` to prove a rename landed. `git grep` exits **0 when it finds**
and 1 when it does not, so that line passes exactly while the old name survives and fails the moment
the rename is complete. Under the `verify && task --check && commit` chain, none of those tasks
could commit once done correctly. The damage was not confined to the instrument: the spec's
`## Risks` named that same grep as the mitigation of its single largest risk — *"cada tarefa da
seção 7 só é ticável quando o grep da sua própria string antiga volta vazio"* — so the mitigation
was inverted at the same time, and nothing said so for nine sections. The correct form negates:
`! git grep …`, or `git grep …; test $? -eq 1`.

**A selector that matches nothing.** Seven tasks declared `python3 -m unittest discover -k <topic>`.
A `-k` filter with no matching test collects **zero** cases and exits **0**. Those seven proved
nothing about the pillars they named; the real coverage arrived two sections later, in the goldens
and the migrated suites. A selector-based check must assert its own case count, or name a test that
exists.

**Measuring an absence where the thing never was.** One task declared
`grep <marker> <the new package>; test $? -eq 1`, to prove a duplicated block had been deduplicated.
The marker had only ever existed in the two pre-refactor scripts, which that task could not touch —
so the check measured the absence of a string from a tree it was never in, and would have passed on
day one. The proof was a test exercising both readers against one shared case list; the grep was
decoration that read like evidence.

**The shared shape.** In all three, the check runs, exits 0, and reports nothing — the failure is
that it never had the power to say otherwise. `## Risks` mitigations get the same treatment as
`verify:` lines, because a mitigation is a check with a longer name.

### A task's `verify:` is scoped at authoring time, never filtered at the gate

What runs at a gate is decided by each task's `verify:`; the `verification` policy decides only
*when* the gate fires. So a gate that re-runs a check whose inputs the section could not have
touched is not a defect in the policy — it is a `verify:` that was written wider than its task.

Measured: on a 13-task run the same three selftests ran at the close of section 1 and again at
task 5.1, because tasks in two sections each declared all three, while the spec itself stated that
no script changed in between. The body obeyed exactly what the spec asked for.

The fix belongs at the origin. **Write each `verify:` scoped to what that task could break** — not
to what the repo can check. The alternative, a gate that skips a declared `verify:` because it
judges the inputs unchanged, is a judgment about correctness made at build time, and this contract
already refuses judgment as a trigger (§A cadence trigger can never be a judgment). Scoping at
authoring needs no judgment while building and holds for every future spec, not only the measured
one.

**A `verify:` naming a whole-bundle validator asserts zero *errors*, never a warning total.**
`stale-doc` rises structurally on any branch that edits a path some standard governs — the resource
moved, the rule did not — so a warning total is not a property of the change under test, and
[bundle-verification.md](../quality/bundle-verification.md) already says to read the gate as zero
errors for exactly that reason. A `verify:` written as `cq knowledge docs → 0 error(s), 0
warning(s)` is therefore false about any mature bundle *before the spec is written*, and it fails
at the gate having proved nothing about the task. Measured 2026-08-03: that assertion, authored
against the shipped `assets/docs` skeleton — conformant by construction — stopped a build whose
deliverable was correct, over 29 warnings the bundle already carried at the branch point. Assert
zero errors, and name the doc the task wrote.

**And a validator that folds warnings into a failing exit makes `exit 0` the same false
assertion, one step earlier.** Measured 2026-08-06: a task's `verify:` demanded `cq specs
validate` exit 0 against a real target workspace carrying seven pre-existing warnings —
`validate` exits 1 on any finding, error or warning alike, so that gate could not have passed on
the day it was authored, whatever the task did. It was verified instead by reading the error
count the tool prints. Same rule, one level down: **assert the count the tool reports, never the
exit code it happens to carry**, wherever a tool has no exit code that means "warnings only".

### The `files:` grammar is closed: `(new)` is the only reserved annotation

`files:` is comma-separated, and a comma inside parentheses **never** separates — a comment like
`a.md (descartável, revertido ao fim)` reads as ONE entry, not two. That split alone would still
hand the executor a path that exists nowhere with the same confidence as a real one, so the
grammar is closed on the other side too: a trailing parenthetical that is not exactly `(new)` is a
human comment the parser must not interpret, and it is **refused** — `validate` reports it as
`sp-files-annotation`, `next` refuses to hand the task out, and `parallel` refuses to prove
disjunction over it. `(new)` stays the one reserved annotation, meaning "a path this task will
create"; parentheses in the middle of a path are not an annotation. The failure this refuses is
silent by construction — an executor cannot tell an invented piece from a path the task will
create — which is exactly why it is refused instead of normalised or dropped.

## A blocked task is a visible marker, not a hidden counter

On failure the code is fixed and the check is run again. Two bounds:

- **Re-read from scratch after two consecutive failures** — the task text, its declared files, and
  the *current* diff. Two failures in a row nearly always means the third attempt is repairing a
  mental model that was already wrong at the first, and each further patch compounds it.
- **Stop when attempts stop converging**, and write the reason into the file:

  ```bash
  cq specs task --spec <slug> --block <id> --reason "<why, one line>"
  ```

  which produces `- [!] <id> <title> — blocked: <reason>` in `## Tasks`. Not a sixth try, not a
  different approach, not a weaker check.

A blocked task is **distinguishable from an untried one**: `cq specs next` skips `[!]` and offers
the following task, so one bad task never stalls a spec. A human resumes it by fixing the cause and
returning it to `- [ ]` (`cq specs task --uncheck <id>`) — never merely to retry the same approach.

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
| Owner | `/quenching:specs:execute`, inside the task | `/quenching:specs:conclude`, step 2 |
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

## One commit per section, squashed from its tasks

```
plan/<slug>: <section-number> <section title>
```

`git revert` then undoes exactly one section, `git log` reads as the spec's `## Tasks` sections, and
a review can walk it section by section. N tasks piled into one uncommitted blob gives none of
that, and neither does a standing commit per task once a section routinely runs to five or ten of
them — the unit worth reverting, reading and reviewing is the section that shipped together, not
each task that built it.

**Every task still gets its own commit while its section is open.** The chain that verifies, ticks
and commits it — [execution.md](/plugins/quenching/assets/references/specs-execute/execution.md)
§The commit — is unchanged: retrying, blocking and resuming a task mid-section reads off a real,
individual commit, exactly as before. Only once the section's last task commits clean, with none of
the section `[!]`, does it collapse — a local `git reset --soft` to the commit standing before the
section, plus one recommit, per
[execution.md](/plugins/quenching/assets/references/specs-execute/execution.md) §The section squash
— never touching a prior section's commits, never anything already shared. The isolation taken at
the start still buys everything it always did: what changes is which commit survives, never whether
the work was proved before it landed.

### The anchor is the sha, where no backend co-branches with the code

The anchor written back onto the task line is the commit's **sha** —
[plan-git-record.md](plan-git-record.md) §The task→commit link — recorded by
`cq specs task --check <id> --commit <sha>` **after** the commit exists:

```bash
git add <the task's files> <the spec file> && git commit -m "<subject>"
cq specs task --spec <slug> --check <id> --commit "$(git rev-parse HEAD)"
```

This is possible today because [the configurable spec backend](../architecture/spec-backend.md) guarantees no
backend lets a spec share a branch with the code being committed: the `files` backend writes to its
own dedicated specs branch (§Backend files below), and an external backend writes outside git
entirely. Neither needs the anchor to land in a file versioned on the code branch, which is the one
constraint that made a sha impossible before.

### What this reverses, and what it does not yet cover

**Subject-before-commit was the prior standard, for a reason that was real and is recorded here
rather than erased.** Under a sha anchor, the tick had to follow the commit it recorded, so every
task cost a second, bookkeeping commit, and "one commit per task" was an aspiration the mechanism
contradicted. Adopting the commit's **subject** instead — known before the commit exists — let the
tick land inside the same commit it describes:

```bash
cq specs task --spec <slug> --check <id> --subject "<subject>"
git add <the task's files> <the spec file> && git commit -m "<subject>"
```

**That mechanism did not go away, and is not deprecated.** `task --commit` is additive to
`task --subject`, never a replacement — both are accepted, together or alone, by the same command.
A repository whose specs still live on the code branch has not stopped needing the reason subject
was chosen for: this repository's own `plans/`/`archive/` remain on the code branch at the time of
writing — the migration of an already-populated `/.specs/` to the dedicated branch is explicitly
deferred, never automatic ([spec-backend.md](../architecture/spec-backend.md) §The selected backend is the source
of truth) — and every spec here still ticks
with `--subject`, before the commit, for exactly the reason this section used to give as the whole
rule. The sha anchor is the target for a backend that does not co-branch; it is not yet a fact
about every repository running this tool.

Whichever anchor a given commit is carrying, the discipline is the same: if the commit fails,
**undo the tick** so no box claims a commit that does not exist. If a `commit-msg` hook *replaced*
the subject, report the drift as a finding and write nothing — repairing the record after the
commit is the ordering this contract exists to prevent, under either anchor.

**The section squash narrows the anchor's granularity, never its resolvability.** The moment a
section's commits collapse into one, every task the section held is re-stamped onto that one
surviving commit's subject (or sha) — [execution.md](/plugins/quenching/assets/references/specs-execute/execution.md)
§The section squash. `git log --grep`, or the sha lookup, still resolves for every one of those
tasks; it resolves to the section's commit rather than a commit of that task's own.

### Hard rules

These are the ways an implementation ships a lie behind a green checkbox. Each is absolute, with
no "just this once":

- Never disable, skip, `xfail`, or delete a test to make a task pass.
- Never edit the `verify:` command, the test, or the assertion so it stops failing. Change the
  code, or report the task blocked.
- Never `git commit --no-verify`. A failing hook is a finding to report, not an obstacle to route
  around. Same for `--no-gpg-sign`.
- Never amend or rewrite an earlier task's commit; never force-push. §The section squash
  (execution.md) is the one narrow exception — and only ever a section's own just-made commits, at
  the moment that section closes, never a prior section's or anything already shared.
- Never tick a checkbox for work that was not verified.

## The Handoff refresh cadence is four events

`## Handoff` carries the state of play a fresh executor would need and **cannot derive**: a parallel
session in the checkout, an unversioned hook, a design flaw found mid-build. Everything a resumed
run *can* derive — which tasks are done, which commit carried each one — already lives in `git log`
and in the `subjects` `cq specs status` returns, so the Handoff is not the resumption trail and
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
`/.knowledge/`**, pinned to the session model — never `haiku`, which writes production code here.

The orchestrator keeps, without exception: spec selection, the isolation offer, every
confirmation, every `cq specs task --check` flip, every block marker, every `/.knowledge/standards/`
write, the commit, and the decision to pause.

### This is not `context: fork`, and that rule is untouched

The standing rule forbids `context: fork` **on these commands**, because a forked context cannot
present the mid-flow confirmations every sweep depends on — the conversation carrying the human's
OK would be out of reach.

Dispatching a sub-agent for a bounded, file-scoped unit of work does the opposite: the
orchestrator **stays in the live conversation**, exactly as `/quenching:knowledge:glossary-backfill` and
`/quenching:knowledge:import` already dispatch. One moves the decision-maker out of reach; the other
sends a worker out and keeps the decision-maker in place. They are different mechanisms about
different things, and no future sweep may "fix" one into the other.

## Parallelism must be earned

Two tasks run concurrently only when all three hold:

1. a `[P]` marker was set on both **when the tasks were written** — never inferred while building;
2. their declared `files:` sets are **provably disjoint**;
3. neither writes into `/.knowledge/`.

Serial is the default and needs no marker. Without proven disjunction, parallel execution trades
wall-clock for merge conflicts and loses on both.

The disjunction is **checked mechanically, not judged in prose**: `cq specs parallel --spec <n>`
reports each group and exits **0** when every marked group is eligible, **1** when any overlaps or
lacks `files:`. Two paths conflict when they are the same file or when one is a directory
containing the other. A group is bounded to one `## N.` section, so a run never straddles two
independently shippable units.
