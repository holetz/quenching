# The execution contract — verify, review, commit, delegate

The owner of **how** `/quenching:specs:execute` builds one task. The command body owns the workflow
(select → isolate → read → loop → hand off); this file owns the mechanics of the loop, and the body
cites it rather than restating it.

Everything here exists for one reason: a spec's tasks used to be *written* and *ticked*, with
nothing in between and nothing after. A task that was never run, never reviewed, and never
committed leaves a checkbox that claims more than the repo can show.

**Where this contract stops.** It ends at the last task's commit. Reviewing the whole branch,
writing the `docs/` the work *revealed*, merging, and archiving belong to `/quenching:specs:conclude` — a
different scale of judgment, needing a different confirmation, and resumable on its own. This file
never reaches past the loop.

## Contents

- [The precondition: a clean tree](#the-precondition-a-clean-tree)
- [Isolation is somebody else's job](#isolation-is-somebody-elses-job)
- [The verification policy](#the-verification-policy)
- [The validation loop](#the-validation-loop)
- [The diff self-review — four items, before every commit](#the-diff-self-review--four-items-before-every-commit)
- [The commit — one per task, carrying its own ticked box](#the-commit--one-per-task-carrying-its-own-ticked-box)
- [Declared versus emergent `docs/`](#declared-versus-emergent-docs)
- [Delegating an executor — permitted, and bounded](#delegating-an-executor--permitted-and-bounded)

## The precondition: a clean tree

<!-- rules -->

**Refuse to start the loop while `git status --porcelain` is non-empty**, and say why: this command
commits one task at a time, and a commit cannot separate the task's diff from an unrelated edit
that was already sitting in the tree. The offer is to commit or stash first; the human may also
override and proceed, in which case the first commit will carry the pre-existing changes and the
report must say so.

Not a git repo → no isolation, no commits. Say that once, run the rest of the loop normally, and
never `git init` a repo on the human's behalf.

## Isolation is somebody else's job

<!-- rules -->

Taking a branch or a worktree, naming it, and stamping `branch: {base, work}` all belong to
**`/quenching:specs:isolate`** and its reference,
[specs-isolate/git.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-isolate/git.md)
§Recording the isolation. `/quenching:specs:execute` delegates to that command and never reimplements it, because isolation is not a privilege of
building: a spec can be isolated at creation or during development just as legitimately.

Two things the loop below still needs from it:

- **A spec whose `plan/<slug>` ref is alive but checked out somewhere else is already being built
  there.** Starting a second run against it forks the work; say where it is and stop.
- **Work done in place carries no `branch` record**, so there is nothing to merge later and the
  report says so.

Nothing in this file stamps that record, reads it as authoritative, or corrects it.

### Delegating is owed; dispatching unconditionally is not

<!-- rules -->

Delegation and dispatch are not the same act. A spec that is **already isolated** — its
`plan/<slug>` ref alive, or the `branch` record already stamped — has nothing left to take, and
`/specs:isolate` invoked against it does exactly what it promises: it reports the existing branch
and stamps nothing. **Check first, and skip the call in that case.** Checking is `git branch --list
"plan/<slug>"` plus the `branch` record already inside the `status --json` the loop reads anyway,
and it decides the question without moving anything.

<!-- rationale -->

The saving is not only turns. Dispatching a stage also costs the run its own **attribution**: the
transcript's pointer moves to the stage and, measured, almost never comes back, so the conducting
run's remaining work is filed under the command it dispatched. What that does to a later count is
owned by `docs/standards/automation/session-evidence.md` §What a command's run cost — the stage
comes back `closed: false`, its counts become an upper bound, and `mayIncludeTurnsFrom` names the
misread. Cite that rule; never restate it.

**The residual case is real and is paid, not avoided.** When there genuinely is something to
isolate, `/specs:isolate` is still the only thing that takes it — the branch form, the
`plan/<slug>` name and the `branch: {base, work}` stamp stay entirely its own, and the invariant
"delegate isolation … never reimplement it here" is untouched. That run loses its own attribution
and is measured as an upper bound. That is the honest cost of a real delegation, written here so it
is not rediscovered at each retro.

## The verification policy

<!-- rules -->

Declared per spec in the frontmatter (`verification`), written by `/quenching:specs:develop`, read by
`specs.py status --spec <slug> --json`. **Execute never decides when to test** — the spec's author
is the only party who knows whether this repo's suite takes four seconds or forty minutes.

| Policy | Run the `verify:` command | Fits |
| --- | --- | --- |
| `per-task` | after every task | a fast suite, or a task set where each step can break the last |
| `per-section` *(default)* | after the last task of each `## N.` section | most repos — a section is the smallest independently shippable unit |
| `end-of-plan` | once, after the final task | a slow suite, or an integration that is meaningless until the whole spec lands |

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
command that edits the surface — `/quenching:skill:new`, or `/quenching:skill:eval` for a description — and running it
from the spec cycle charges every spec for a front most of them never touch.

## The validation loop

<!-- rules -->

For each task the policy says to verify:

1. Run the task's `verify:` command.
2. **Passes** → the task is done; go to the diff self-review.
3. **Fails** → read the failure, change the code, and run it again.

Two rules bound the loop:

- **Re-read from scratch after two consecutive failures.** Discard the working theory, re-read the
  task text, the files it declares, and the *current* diff (`git diff`) as if arriving fresh. Two
  failures in a row nearly always means the third attempt is repairing a mental model that was
  wrong at attempt one, and each further patch is built on the same error.
- **Stop when you stop making progress, and say so in the file.** There is no attempt counter.
  When the orchestrator judges that further attempts are repeating rather than converging, it
  writes the task blocked, with the reason:
  ```bash
  specs.py task --spec "<slug>" --block <id> --reason "<why, one line>"
  ```
  That writes a **visible marker into `## Tasks`** — `- [!] <id> <title> — blocked: <reason>` —
  and `specs.py next` then skips it and offers the following task, so one bad task never stalls
  the whole spec.

**`--block` requires `--reason`** (the tool refuses without one). A blocked task with no reason is
exactly the hidden state this replaced.

A human resumes a blocked task by fixing the cause and un-blocking it —
`specs.py task --spec <slug> --uncheck <id>` returns it to `- [ ]` — after changing something,
never merely to try the same approach again.

<!-- rationale -->

**Why a marker and not a counter.** v1 kept an attempt count in a sidecar `.specs.json` and
stopped at five. The count was machine state a human never saw: a task went quiet after five
failures with no trace of *why*, and the only way to resume was a `--reset-attempts` incantation
that bought five more attempts at the same wrong approach. A written reason serves the same
purpose — stopping unattended retry loops — while being legible to the person who has to unblock
it, and it lives in the file they are already reading.

## The diff self-review — four items, before every commit

<!-- rules -->

Cheap, per task, over that task's diff only (`git diff`). Four questions, not a code review:

1. **Reuse** — does something in this repo already do this? A helper, a util, an existing pattern.
   Duplicating it is the most common cost of task-scoped work.
2. **Useless defense** — a try/except, a null guard, a fallback for a case that cannot occur here.
   Defensive code for an impossible state hides real failures.
3. **Obvious comment** — a comment restating what the line plainly says. Delete it; keep the ones
   explaining *why*.
4. **Dead code** — anything added and not reached, left behind by an approach that changed
   mid-task.

Fix what it finds **before** committing, so the commit is the reviewed version. The
whole-branch review runs once, and it belongs to `/quenching:specs:conclude`.

<!-- rationale -->

This is deliberately *not* a full code review: it runs per task, and a three-line change must not
cost a full-diff read.

## The commit — one per task, carrying its own ticked box

<!-- rules -->

After the self-review passes, **decide the subject, then verify, tick the box with it, commit, and
assert the subject survived**. That order is the point: the subject is known before the commit
exists, so the checkbox travels *inside* the commit that implements it.

Run it as **one chained call**, gate included:

```bash
<the task's verify:> \
  && specs.py task --check <id> --spec "<slug>" --subject "<subject>" \
  && git add <the task's files> <the spec file> \
  && git commit -m "<subject>" \
  && git log -1 --format=%s
```

**The `&&` is the ordering.** Written as four separate calls the sequence was a rule the body had
to be obeyed to hold; chained, it is enforced by the shell — verify before the tick, the tick
before the commit, and a broken link short-circuiting every link after it, which is exactly the
failure behaviour the separate form documented and the chained form gets for free. Nothing about
what is guaranteed moved; only the number of calls did. When the spec's declared policy says this
task is not a gate, the chain simply starts at `specs.py task`.

Stage the task's declared `files:` **and the spec file**, never the whole tree — `git add -A` also
picks up whatever an editor or a tool wrote while the task ran, which is the same contamination
§The precondition refuses at the start.

If the commit **fails** — a rejecting hook, nothing staged — undo the tick
(`specs.py task --spec "<slug>" --uncheck <id>`) so no box claims a commit that does not exist, and
report the failure. Never route around it with `--no-verify`.

The **subject line format** is the target repo's to declare. Read
[specs-isolate/git.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-isolate/git.md)
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
link: **report it as a finding and write nothing.** Correcting the record here would put a write
after the commit again, which is the whole thing this ordering removes.

**Squash is the one caveat, and `conclude` owns it.** A squashed merge leaves the per-task commits
reachable only from the branch — which is why `/quenching:specs:conclude` records `merge: {strategy, subject}`
and, on a squash, offers to keep the branch. Nothing in this loop needs to know; recording the
subject honestly is the whole job here.

With no git in the repo there is nothing to anchor to: tick the box without `--subject` and say so
once in the report, rather than inventing a placeholder.

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

It is captured **indiscriminately**: whether it is worth acting on is a later judgment, and asking
the executor to make it mid-task is how a finding gets dropped for being inconvenient. The lines
are resolved by `/quenching:specs:develop`'s discoveries bank, and the doc an emergent finding deserves is
written by `/quenching:specs:conclude` at distillation.

<!-- rationale -->

Two failure modes this line exists to prevent, and they pull in opposite directions: a build that
stops to author a standard nobody asked for, and a build that silently loses what it learned.
Declared → write it. Emergent → record it in one line.

**The orchestrator writes every `docs/` file itself.** This is never delegated to a sub-agent (see
below), and a task that writes into `docs/` is not eligible for delegation at all.

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

### This is not `context: fork`, and the never-fork rule is untouched

The plugin's standing rule forbids `context: fork` **on these commands**, because a forked context
cannot present the mid-flow confirmations every sweep depends on — the conversation carrying the
human's OK would be out of reach.

Dispatching a `Task` for a bounded, file-scoped unit of work does the opposite: **the orchestrator
stays in the live conversation**, exactly where `/quenching:docs:glossary-backfill` and
`/quenching:docs:import` already dispatch from. One moves the decision-maker out of reach; the
other sends a worker out and keeps the decision-maker in place. They are different mechanisms
about different things, and no future sweep should "fix" one into the other.

### Parallelism must be earned

Two tasks run concurrently **only** when all three hold:

1. a `[P]` marker was set on both **at definition time** — never inferred while executing;
2. their declared `files:` sets are **provably disjoint** (`specs.py` checks this mechanically —
   see §The `[P]` check);
3. neither writes into `docs/`.

Serial is the default and needs no marker. Without proven file disjunction, parallel execution
trades wall-clock for merge conflicts and loses on both.

### The `[P]` check

```bash
specs.py parallel --spec "<slug>" [--json]
```

Reports each `[P]` group and whether it is `eligible`. Exit **0** when every marked group is
eligible, **1** when any group overlaps or lacks `files:`. **Branch on that, never on judgment**:
a group reported ineligible runs serially, and the reason is stated in the report rather than
argued about.
