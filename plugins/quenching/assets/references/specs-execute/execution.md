# The execution contract — verify, review, commit, delegate

The owner of **how** `/specs:execute` builds one task. The command body owns the workflow
(select → isolate → read → loop → hand off); this file owns the mechanics of the loop, and the body
cites it rather than restating it.

Everything here exists for one reason: a spec's tasks used to be *written* and *ticked*, with
nothing in between and nothing after. A task that was never run, never reviewed, and never
committed leaves a checkbox that claims more than the repo can show.

**Where this contract stops.** It ends at the last task's commit. Reviewing the whole branch,
writing the `docs/` the work *revealed*, merging, and archiving belong to `/specs:conclude` — a
different scale of judgment, needing a different confirmation, and resumable on its own. This file
never reaches past the loop.

## Contents

- [The precondition: a clean tree](#the-precondition-a-clean-tree)
- [Recording the isolation](#recording-the-isolation)
- [The verification policy](#the-verification-policy)
- [The validation loop](#the-validation-loop)
- [The diff self-review — four items, before every commit](#the-diff-self-review--four-items-before-every-commit)
- [The commit — one per task](#the-commit--one-per-task)
- [Declared versus emergent `docs/`](#declared-versus-emergent-docs)
- [Delegating an executor — permitted, and bounded](#delegating-an-executor--permitted-and-bounded)

## The precondition: a clean tree

**Refuse to start the loop while `git status --porcelain` is non-empty**, and say why: this command
commits one task at a time, and a commit cannot separate the task's diff from an unrelated edit
that was already sitting in the tree. The offer is to commit or stash first; the human may also
override and proceed, in which case the first commit will carry the pre-existing changes and the
report must say so.

Not a git repo → no isolation, no commits. Say that once, run the rest of the loop normally, and
never `git init` a repo on the human's behalf.

## Recording the isolation

When the human takes a branch or a worktree, stamp it into frontmatter **once**, before the first
task:

```yaml
branch:
  base: main
  work: plan/session-tokens
```

`work` is derivable from `git branch --show-current` while the branch is checked out; `base` is
not — **after the merge, git cannot say what the branch was cut from.** That is the whole reason
the record exists, and it is why `base` is captured at the moment it is still true rather than
reconstructed at `conclude`.

Stamp nothing when the human declines isolation and works in place. There is no branch, nothing
will be merged, and a record whose `base` equals its `work` states no fact. Say in the report that
the spec carries no `branch` record and why.

The record is `writeOnce: true`. A second `execute` run on the same spec **reads** it rather than
rewriting it — and if the current branch disagrees with `work`, that is a finding to report, not a
value to correct.

## The verification policy

Declared per spec in the frontmatter (`verification`), written by `/specs:develop`, read by
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

## The validation loop

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

**Why a marker and not a counter.** v1 kept an attempt count in a sidecar `.specs.json` and
stopped at five. The count was machine state a human never saw: a task went quiet after five
failures with no trace of *why*, and the only way to resume was a `--reset-attempts` incantation
that bought five more attempts at the same wrong approach. A written reason serves the same
purpose — stopping unattended retry loops — while being legible to the person who has to unblock
it, and it lives in the file they are already reading.

**`--block` requires `--reason`** (the tool refuses without one). A blocked task with no reason is
exactly the hidden state this replaced.

A human resumes a blocked task by fixing the cause and un-blocking it —
`specs.py task --spec <slug> --uncheck <id>` returns it to `- [ ]` — after changing something,
never merely to try the same approach again.

## The diff self-review — four items, before every commit

Cheap, per task, over that task's diff only (`git diff`). Four questions, not a code review:

1. **Reuse** — does something in this repo already do this? A helper, a util, an existing pattern.
   Duplicating it is the most common cost of task-scoped work.
2. **Useless defense** — a try/except, a null guard, a fallback for a case that cannot occur here.
   Defensive code for an impossible state hides real failures.
3. **Obvious comment** — a comment restating what the line plainly says. Delete it; keep the ones
   explaining *why*.
4. **Dead code** — anything added and not reached, left behind by an approach that changed
   mid-task.

Fix what it finds **before** committing, so the commit is the reviewed version. This is
deliberately *not* a full code review: it runs per task, and a three-line change must not cost a
full-diff read. The whole-branch review runs once, and it belongs to `/specs:conclude`.

## The commit — one per task

After the self-review passes, commit that task alone. Stage the task's declared `files:` rather
than sweeping the tree — `git add -A` also picks up whatever an editor or a tool wrote while the
task ran, which is the same contamination §The precondition refuses at the start:

```bash
git add <the task's files> && git commit -m "<subject>"
```

The **subject line format** is the target repo's to declare. Read
[git.md](git.md) §Commit messages: a repo with `docs/standards/git/**` owns the format outright and
this contract defers to it; with nothing declared, the plugin's default is
`plan/<slug>: <task-id> <task title>`. Never install a git standard into a target to create the
answer.

One commit per task is what makes the branch worth having: `git revert` undoes exactly one task,
`git log` reads as the spec's task list, and a review can walk it step by step. N tasks piled into
one uncommitted blob gives none of that, and the isolation offer buys nothing.

**Hard rules, no exceptions and no "just this once":**

- **Never `--no-verify`.** A commit hook that fails is a finding to report, not an obstacle to
  route around. The same goes for `--no-gpg-sign`.
- **Never disable, skip, `xfail`, or delete a test to make a task pass.**
- **Never edit the `verify:` command, the test, or the assertion so it stops failing.** Change the
  code, or report the task as blocked. Editing the check is how a spec ships a lie with a green
  checkbox.
- **Never amend or rewrite an earlier task's commit**, and never force-push.
- If the repo has no git, skip committing entirely and say so once.

Then, and only then, tick the box **with the sha that implemented it**:

```bash
specs.py task --spec "<slug>" --check <id> --commit "$(git rev-parse --short HEAD)"
```

The sha lands on the task line as `commit: <sha>`, in the indented metadata grammar `files:` and
`verify:` already use. It is what links a checkbox to the code without a trailer inside the commit
message, leaving the target repo's message format entirely its own. It cannot go stale: the two
rules above forbid amending an earlier task's commit and forbid force-push, so a recorded sha
stays resolvable for the life of the branch.

**Squash is the one caveat, and `conclude` owns it.** A squashed merge leaves every per-task sha
reachable only from the branch — which is why `/specs:conclude` records `merge: {strategy, commit}`
and, on a squash, offers to keep the branch. Nothing in this loop needs to know; recording the sha
honestly is the whole job here.

With no git in the repo there is no sha: tick the box without `--commit` and say so once in the
report, rather than inventing a placeholder.

## Declared versus emergent `docs/`

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
are resolved by `/specs:develop`'s discoveries bank, and the doc an emergent finding deserves is
written by `/specs:conclude` at distillation.

Two failure modes this line exists to prevent, and they pull in opposite directions: a build that
stops to author a standard nobody asked for, and a build that silently loses what it learned.
Declared → write it. Emergent → record it in one line.

**The orchestrator writes every `docs/` file itself.** This is never delegated to a sub-agent (see
below), and a task that writes into `docs/` is not eligible for delegation at all.

## Delegating an executor — permitted, and bounded

A per-task executor sub-agent (`Task`) is **permitted** when both hold:

- the task declares `files:` — the sub-agent gets a bounded scope, not the whole repo;
- the task writes nothing under `docs/`.

Pin it to the session model. **Never `haiku`** — it is writing production code, and the model
policy for that is the same one that protects `/docs:import-memory`'s classifiers.

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
stays in the live conversation**, exactly where `/docs:glossary-backfill` and
`/docs:import` already dispatch from. One moves the decision-maker out of reach; the
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
