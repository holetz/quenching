# The execution contract — verify, review, commit, delegate

The owner of **how** `/quenching:specs:execute` builds one task. The command body owns the workflow
(select → isolate → read → loop → hand off); this file owns the mechanics of the loop, and the body
cites it rather than restating it.

Everything here exists for one reason: a spec's tasks used to be *written* and *ticked*, with
nothing in between and nothing after. A task that was never run, never reviewed, and never
committed leaves a checkbox that claims more than the repo can show.

**Where this contract stops.** It ends at the last task's commit. Reviewing the whole branch,
writing the `docs/` the work *revealed*, merging, and archiving belong to `/quenching:specs:conclude` — a
different scale of judgment, needing a different confirmation, and resumable on its own: a run that
dies after task nine must be resumable without redoing tasks one through eight. This file never
reaches past the loop.

## Contents

`skills.py read <this file>` returns the heading index; `--sections` addresses one.

## The precondition: a clean tree

<!-- rules -->

**Refuse to start the loop while `git status --porcelain` is non-empty**, and say why: this command
commits one task at a time, and a commit cannot separate the task's diff from an unrelated edit
that was already sitting in the tree. The offer is to commit or stash first; the human may also
override and proceed, in which case the first commit will carry the pre-existing changes and the
report must say so.

Not a git repo → no isolation, no commits. Say that once, run the rest of the loop normally, and
never `git init` a repo on the human's behalf.

## Isolation is offered inline, and only from the base

<!-- rules -->

Taking a branch or a worktree, naming it, and stamping `branch: {base, work}` all happen inline in
the command body's own step 2 — not a separate command it dispatches to. The convention it applies
lives in
[specs-execute/git.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-execute/git.md)
§Recording the isolation, cited rather than restated.

**The offer fires only when `HEAD` is on the repository's base branch.** Anywhere else, the human
already answered the question at checkout, and asking again is friction the loop does not need to
pay.

Two things the loop still needs, regardless of form:

- **A spec whose `plan/<slug>` ref is alive but checked out somewhere else is already being built
  there.** Starting a second run against it forks the work; say where it is and stop.
- **Work done in place carries no `branch` record**, so there is nothing to merge later and the
  report says so.

**Check before offering, every time.** A spec that is **already isolated** — its `plan/<slug>` ref
alive, or the `branch` record already stamped — has nothing left to take, and offering again buys
nothing but the turns it costs. Checking is `git branch --list "plan/<slug>"` plus the `branch`
record already inside the `status --json` the loop reads anyway, and it decides the question
without moving anything.

## The verification policy

<!-- rules -->

Declared per spec in the frontmatter (`verification`), written by `/quenching:specs:develop`, read by
`specs.py status --spec <slug> --json`. **Execute never decides when to test.**

| Policy | Run the `verify:` command |
| --- | --- |
| `per-task` | after every task |
| `per-section` *(default)* | after the last task of each `## N.` section |
| `end-of-plan` | once, after the final task |

A task with no `verify:` line falls back to the spec's own `## Validation` section, and failing
that, to whatever the repo's standards name as its check. **No verification available at all is a
finding to report, not a silent pass** — say plainly that the task was implemented but not proved.

**A check that spawns billed agent sessions does not belong in a `verify:` line.** A `verify:` runs
per task *and again on every retry of the loop below*, so a suite that costs money per invocation
is multiplied by exactly the thing this loop is for. Those belong in `## Validation`, which
`/quenching:specs:conclude` runs **once**, as its pre-merge gate. When a task's `verify:` names one anyway,
say so and run the narrowest scope the tool offers rather than the whole suite by reflex — and
report the substitution, because a narrowed check is a narrowed claim.

**A harness that proves the *command surface* loads belongs to neither.** It is owned by the
command that edits the surface — `/quenching:skill:new`, or `/quenching:skill:eval` for a description.

## The validation loop

<!-- rules -->

For each task the policy says to verify:

1. Run the task's `verify:` command.
2. **Passes** → the task is done; go to the diff self-review.
3. **Fails** → read the failure, change the code, and run it again.

Two rules bound the loop:

- **Re-read from scratch after two consecutive failures.** Discard the working theory, re-read the
  task text, the files it declares, and the *current* diff (`git diff`) as if arriving fresh.
- **Stop when you stop making progress, and say so in the file.** There is no attempt counter.
  When the orchestrator judges that further attempts are repeating rather than converging, it
  writes the task blocked, with the reason:
  ```bash
  specs.py task --spec "<slug>" --block <id> --reason "<why, one line>"
  ```
  That writes a **visible marker into `## Tasks`** — `- [!] <id> <title> — blocked: <reason>` —
  and `specs.py next` then skips it and offers the following task, so one bad task never stalls
  the whole spec.

**`--block` requires `--reason`** (the tool refuses without one).

A human resumes a blocked task by fixing the cause and un-blocking it —
`specs.py task --spec <slug> --uncheck <id>` returns it to `- [ ]` — after changing something,
never merely to try the same approach again.

## The diff self-review — four items, before every commit

<!-- rules -->

Cheap, per task, over that task's diff only (`git diff`). Four questions, not a code review:

1. **Reuse** — does something in this repo already do this? A helper, a util, an existing pattern.
2. **Useless defense** — a try/except, a null guard, a fallback for a case that cannot occur here.
3. **Obvious comment** — a comment restating what the line plainly says. Delete it; keep the ones
   explaining *why*.
4. **Dead code** — anything added and not reached, left behind by an approach that changed
   mid-task.

Fix what it finds **before** committing, so the commit is the reviewed version. The
whole-branch review runs once, and it belongs to `/quenching:specs:conclude`.

## The commit — one per task, carrying its own ticked box

<!-- rules -->

After the self-review passes, **decide the subject, then verify, tick the box with it, commit, and
assert the subject survived**.

Run it as **one chained call**, gate included:

```bash
<the task's verify:> \
  && specs.py task --check <id> --spec "<slug>" --subject "<subject>" \
  && git add <the task's files> <the spec file> \
  && git commit -m "<subject>" \
  && git log -1 --format=%s
```

**The `&&` is the ordering:** verify before the tick, the tick before the commit, and a broken link
short-circuits every link after it. When the spec's declared policy says this task is not a gate,
the chain simply starts at `specs.py task`.

Stage the task's declared `files:` **and the spec file**, never the whole tree — `git add -A` also
picks up whatever an editor or a tool wrote while the task ran, which is the same contamination
§The precondition refuses at the start.

If the commit **fails** — a rejecting hook, nothing staged — undo the tick
(`specs.py task --spec "<slug>" --uncheck <id>`) so no box claims a commit that does not exist, and
report the failure.

The **subject line format** is the target repo's to declare. Read
[specs-execute/git.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-execute/git.md)
§Commit messages: a repo with `docs/standards/git/**` owns the format outright and this contract defers to it; with nothing
declared, the plugin's default is `plan/<slug>: <task-id> <task title>`. Never install a git
standard into a target to create the answer.

**Hard rules, no exceptions and no "just this once":**

- **Never `--no-verify`.** A commit hook that fails is a finding to report, not an obstacle to
  route around. The same goes for `--no-gpg-sign`.
- **Never disable, skip, `xfail`, or delete a test to make a task pass.**
- **Never edit the `verify:` command, the test, or the assertion so it stops failing.** Change the
  code, or report the task as blocked. Editing the check is how a spec ships a lie with a green
  checkbox.
- **Never amend or rewrite an earlier task's commit**, and never force-push.
- If the repo has no git, skip committing entirely and say so once.

The chain's last link **asserts the subject survived**, and the rule is report rather than repair:
its `git log -1 --format=%s` must equal what was recorded.

The subject lands on the task line as `subject: <line>`, in the indented metadata grammar `files:`
and `verify:` already use, and resolves with `git log --grep=<subject> --fixed-strings`. A
`commit-msg` hook that only *adds* — a ticket prefix, a `Change-Id`, a sign-off — leaves it
matching as a substring and needs nothing. A hook that **replaces** the subject outright breaks the
link: **report it as a finding and write nothing.**

With no git in the repo there is nothing to anchor to: tick the box without `--subject` and say so
once in the report, rather than inventing a placeholder.

## Declared versus emergent `docs/`

<!-- rules -->

A task writes a `docs/standards/` doc **only when the task itself names it** — the path bulleted
under `## Impact`'s parsed `### Standards this spec will write into docs/standards/` sub-heading,
and named by that task. That doc is part of the task's deliverable: it is written before the
commit, reviewed in the same diff, and stamped `authority` honestly — `current` when the task
actually proved the rule, `background` when it is agreed but not yet proven.

Everything else the work reveals — a gotcha, a second-order consequence, a rule nobody had thought
of — costs **one line and no authoring**:

```bash
specs.py discover "<slug>" "<what was found, one line>"
```

It is captured **indiscriminately**. The lines are resolved by `/quenching:specs:develop`'s
discoveries bank, and the doc an emergent finding deserves is written by
`/quenching:specs:conclude` at distillation.

A task that writes into `docs/` is not delegated — §Delegating an executor.

## Delegating an executor — permitted, and bounded

<!-- rules -->

A per-task executor sub-agent (`Task`) is **permitted** when both hold:

- the task declares `files:` — the sub-agent gets a bounded scope, not the whole repo;
- the task writes nothing under `docs/`.

Pin it to the session model. **Never `haiku`** — it is writing production code, and the model
policy for that is the same one that protects `/quenching:docs:import-memory`'s classifiers.

**The orchestrator keeps, without exception:** spec selection, the isolation offer, every
confirmation, every `specs.py task --check` flip, every `specs.py task --block` marker, every
`docs/standards/` write, every `specs.py discover` line, the commit, and the decision to pause. The
sub-agent writes code inside its declared files and reports back — it never talks to the human and
never touches the spec's bookkeeping.

### The cost of delegating, and when it inverts

<!-- rules -->

**Permitted is not free, and the account runs the other way more often than it looks.**

- **Delegate by file, or by section of tasks — never task by task.** One sub-agent that owns six
  tasks over one file reads it once; six sub-agents read it six times.
- **Run the four-item self-review INSIDE the sub-agent**, and have it return a verdict. A
  sub-agent that hands its diff back for review puts the diff into the long context, which is the
  cost the delegation was for.
- **Where the tasks are small and the shared file is large, keep the work.** Reading once and
  re-reading from cache is the cheaper arm, and the loop is allowed to say so.

The delegation is a `Task`, not `context: fork` — §Tooling asides.

### Parallelism must be earned

<!-- rules -->

Two tasks run concurrently **only** when all three hold:

1. a `[P]` marker was set on both **at definition time** — never inferred while executing;
2. their declared `files:` sets are **provably disjoint** (`specs.py` checks this mechanically —
   see §The `[P]` check);
3. neither writes into `docs/`.

Serial is the default and needs no marker. Without proven file disjunction, parallel execution
trades wall-clock for merge conflicts and loses on both.

### The `[P]` check

<!-- rules -->

```bash
specs.py parallel --spec "<slug>" [--json]
```

Reports each `[P]` group and whether it is `eligible`. Exit **0** when every marked group is
eligible, **1** when any group overlaps or lacks `files:`. **Branch on that, never on judgment**:
a group reported ineligible runs serially, and the reason is stated in the report rather than
argued about.

## The Handoff cadence

<!-- rules -->

The four events are the command body's. Why four events rather than a threshold or a judgment:
§Tooling asides.

**The four events say when a rewrite happens; they do not say how much it touches.** Since
`## Handoff` gained per-section blocks — a small global block plus one `### N.` block per `## Tasks`
section — a rewrite at any of the four events targets ONE of the two:
`specs.py section <slug> Handoff --write --scope global` for the evergreen block, or `--scope
current` for the block of whichever `### N.` still has open work. A section's block closes — stops
being targeted — the moment its last task commits, but that close adds no fifth event: `--scope
current` always resolves to whichever section still has an open task, so once `### N.` has none
left, the NEXT of the four events to fire already writes `### (N+1).` instead, wherever in the run
that next event happens to land. A section whose every task commits between two rewrite events
never gets a block of its own at all — `--scope current` opens one on demand when the next event
finally fires, borrowing that section's own `## Tasks` heading as its title.

## The section boundary — where a run may stop

<!-- rules -->

A `## N.` section's last task committing, with another section still ahead, is a **clean boundary**:
the loop offers to stop there, names the command that resumes, and continues unless told otherwise.

- **The trigger is that event, never a window size.** No threshold, no token count, no "this is
  getting long".
- **Nothing extra is written.** `## Handoff`, `git log`, and the `subjects` `specs.py status`
  returns already carry everything a fresh session needs; the boundary adds no record and no fifth
  Handoff event. Accepted, the stop is a pause and a last commit — two events the cadence already
  has.
- **It offers and never imposes.** The loop does not end itself, and an unanswered offer means
  carry on.
- **The contract still ends at the last commit.** A stop here is not a close-out: the branch
  review, the merge and the archive remain `/quenching:specs:conclude`'s, exactly as they are for a
  run that goes to the end.

## Tooling asides, relocated

### Why `Bash` is unrestricted

<!-- rationale -->

`/quenching:specs:execute` is the one `/specs:*` command that runs the target repo's own toolchain
— build, tests, linters, migrations, and `git` — as part of implementing a task. Its siblings are
scoped to `python3`/`py` because they only ever talk to `specs.py`.

### Why the resolved-whole notice matters

<!-- rationale -->

When neither `skills.py` nor the target's `.claude/hooks/skills.py` resolves, the body falls back
to `Read`ing the cited file whole and says so in the report — because that is the run's context
cost changing, not a cosmetic difference.

### Why the declared files, never their folder

<!-- rationale -->

Measured, not assumed: on this repo, the four subject folders a spec touched held 19 files
(~31k tokens) against 5 files (~13k) for what `## Impact` declared, and that gap arrives at turn
one, where every later turn re-sends it.

### Why there is no mechanical net for an undeclared contract

<!-- rationale -->

The mirror image of the line above. `specs.py validate` already warns when a declared standard has
no task (`sp-impact-uncovered`); the inverse — a binding standard nobody declared — is not
derivable, because deciding a standard governs a task is reading, not parsing. Every approximation
of it has to re-read the folder to have something to warn about, which is the cost
`/quenching:specs:execute` step 4 removed by reading only the declared files.

### Why the spec's author declares the policy

<!-- rationale -->

The spec's author is the only party who knows whether this repo's suite takes four seconds or
forty minutes. What each policy fits:

- `per-task` — a fast suite, or a task set where each step can break the last.
- `per-section` — most repos — a section is the smallest independently shippable unit.
- `end-of-plan` — a slow suite, or an integration that is meaningless until the whole spec lands.

### Why the surface harness belongs to neither

<!-- rationale -->

Running it from the spec cycle charges every spec for a front most of them never touch.

### Why a marker and not a counter

<!-- rationale -->

v1 kept an attempt count in a sidecar `.specs.json` and stopped at five. The count was machine
state a human never saw: a task went quiet after five failures with no trace of *why*, and the only
way to resume was a `--reset-attempts` incantation that bought five more attempts at the same wrong
approach. A written reason serves the same purpose — stopping unattended retry loops — while being
legible to the person who has to unblock it, and it lives in the file they are already reading. A
blocked task with no reason is exactly the hidden state this replaced.

### Why re-read from scratch after two failures

<!-- rationale -->

Two failures in a row nearly always means the third attempt is repairing a mental model that was
wrong at attempt one, and each further patch is built on the same error.

### Why the self-review is four items and not a code review

<!-- rationale -->

This is deliberately *not* a full code review: it runs per task, and a three-line change must not
cost a full-diff read.

On item 1, reuse: duplicating it is the most common cost of task-scoped work. On item 2, useless
defense: defensive code for an impossible state hides real failures.

### Why the subject is decided before the commit exists

<!-- rationale -->

That order is the point: the subject is known before the commit exists, so the checkbox travels
*inside* the commit that implements it. Correcting the record after the fact would put a write
after the commit again, which is the whole thing this ordering removes.

### Why the commit chain is one call and not four

<!-- rationale -->

Written as four separate calls the sequence was a rule the body had to be obeyed to hold; chained,
it is enforced by the shell — verify before the tick, the tick before the commit, and a broken link
short-circuiting every link after it, which is exactly the failure behaviour the separate form
documented and the chained form gets for free. Nothing about what is guaranteed moved; only the
number of calls did.

### Why one commit per task, and why the subject rather than a sha

<!-- rationale -->

**There is no per-task bookkeeping commit any more.** It existed only because a sha cannot be known
before the commit that carries it, so the tick had to follow the commit and could not join it. One
task is now exactly one commit: code, docs the task named, and the ticked box.

One commit per task is what makes the branch worth having: `git revert` undoes exactly one task,
`git log` reads as the spec's task list, and a review can walk it step by step. N tasks piled into
one uncommitted blob gives none of that, and the isolation offer buys nothing.

The record cannot go stale: the rules above forbid amending an earlier task's commit and forbid
force-push. Unlike a sha it also **survives a rebase**, so the one merge strategy that used to
destroy every recorded link no longer does.

### Why squash is `conclude`'s caveat and not this loop's

<!-- rationale -->

**Squash is the one caveat, and `conclude` owns it.** A squashed merge leaves the per-task commits
reachable only from the branch — which is why `/quenching:specs:conclude` records `merge: {strategy, subject}`
and, on a squash, offers to keep the branch. Nothing in this loop needs to know; recording the
subject honestly is the whole job here.

### Why discoveries are captured indiscriminately

<!-- rationale -->

Whether it is worth acting on is a later judgment, and asking the executor to make it mid-task is
how a finding gets dropped for being inconvenient.

Two failure modes this line exists to prevent, and they pull in opposite directions: a build that
stops to author a standard nobody asked for, and a build that silently loses what it learned.
Declared → write it. Emergent → record it in one line.

### Why delegation is priced, not just permitted

<!-- rationale -->

A sub-agent starts on a cold context and does not share the session's prompt cache, so it pays the
full first read of every file it touches. Where N tasks declare the same large file, that is N
cold reads against the orchestrator's one warm one.

The account is **declared arithmetic over files on disk, not a measurement of any run** — the
distinction `docs/standards/automation/session-evidence.md` §The rule a counted claim must obey
imposes, and it is stated as an estimate here because that is what it is. On this repo's
`configurable-spec-backend`, 18 of 29 tasks are delegation-eligible and 13 of them declare the same
file: `specs.py`, ~37k tokens. Task-by-task that is ~13 × 37k ≈ 480k against roughly 150k for an
orchestrator reading it once and re-reading from cache — a delegation that reads as a saving and
is not one. Measured across the whole transcript archive, this permission had never once been
exercised, so nothing here revokes it; what was missing was the arithmetic that says when it pays.

### This is not `context: fork`, and the never-fork rule is untouched

<!-- rationale -->

The plugin's standing rule forbids `context: fork` **on these commands**, because a forked context
cannot present the mid-flow confirmations every sweep depends on — the conversation carrying the
human's OK would be out of reach.

Dispatching a `Task` for a bounded, file-scoped unit of work does the opposite: **the orchestrator
stays in the live conversation**, exactly where `/quenching:docs:glossary-backfill` and
`/quenching:docs:import` already dispatch from. One moves the decision-maker out of reach; the
other sends a worker out and keeps the decision-maker in place. They are different mechanisms
about different things, and no future sweep should "fix" one into the other.

### Why the Handoff cadence is four events, not a judgment

<!-- rationale -->

Two cadences were tried before the four-event list and both failed. Measured on a 13-task run,
rewriting `## Handoff` after every committed task produced revisions ~90% identical to one another.
Substituting a judgment — "rewrite it when the underivable state changed" — fails the same way a
threshold would: an unattended run never judges that something went stale, so a judgment-based
trigger never fires. Each of the four events names an act the loop just performed, never an
assessment it has to make, which is what lets the rule hold in an unattended run.

### Why a section is the boundary, and why no window size

<!-- rationale -->

A number invented before it is measured fixes the answer, which is why §The Handoff cadence is four
events rather than a judgment.

The run's cost is `tokens × turns remaining`, so it grows with the **square** of the turn count:
seven runs of ~45 turns cost roughly a seventh of one run of 300 for the same work. That figure is
declared arithmetic over the integral, not a measured run, and it assumes resumption costs about
nothing — which holds only because the trail above was already being maintained for other reasons.
A section is the unit because it is the smallest independently deliverable one the front already
defines; `per-section` is the default verification policy for the same reason, so a boundary is
also the point where the suite has just run.
