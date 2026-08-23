# The execution contract — verify, review, commit, delegate

The owner of **how** `quenching-specs-execute` builds one task. The command body owns the workflow
(select → isolate → read → loop → hand off); this file owns the mechanics of the loop, and the body
cites it rather than restating it.

Everything here exists for one reason: a spec's tasks used to be *written* and *ticked*, with
nothing in between and nothing after. A task that was never run, never reviewed, and never
committed leaves a checkbox that claims more than the repo can show.

**Where this contract stops.** It ends at the last task's commit. Reviewing the whole branch,
writing the `knowledge/` the work *revealed*, merging, and archiving belong to `quenching-specs-conclude` — a
different scale of judgment, needing a different confirmation, and resumable on its own: a run that
dies after task nine must be resumable without redoing tasks one through eight. This file never
reaches past the loop.

## Contents

`cq components read <this file>` returns the heading index; `--sections` addresses one.

## The precondition: a clean tree

<!-- rules -->

**Refuse to start the loop while `git status --porcelain` is non-empty**, and say why: this command
commits one task at a time, and a commit cannot separate the task's diff from an unrelated edit
that was already sitting in the tree. The offer is to commit or stash first; the human may also
override and proceed, in which case the first commit will carry the pre-existing changes and the
report must say so.

Not a git repo → no isolation, no commits. Say that once, run the rest of the loop normally, and
never `git init` a repo on the human's behalf.

## The hook probe

<!-- rules -->

**Probe the environment before writing any code.** A hook wired in `.agents/settings.json` whose
script no longer exists on disk fails *every* commit the loop makes, and it fails as a hook error
rather than as a missing file — so it gets diagnosed at the first commit, ad hoc, in about ten
calls. Ask the question once instead, in the same call as the tree and state reads:

```bash
python3 -c "
import json, pathlib, re
p = pathlib.Path('.agents/settings.json')
d = json.loads(p.read_text()) if p.exists() else {}
cmds = [h.get('command','') for g in d.get('hooks',{}).values() for e in g for h in e.get('hooks',[])]
gone = sorted({t for c in cmds for t in re.findall(r'[\w./\$\{\}-]+\.(?:py|sh|js|ts)', c)
               if not pathlib.Path(re.sub(r'\\\$\{?CLAUDE_PROJECT_DIR\}?/?', '', t)).exists()})
print('unresolved hook targets:', gone or 'none')"
```

Anything other than `none` → **report it before the first task**, name the hook and the missing
path, and let the human decide: fix the wiring, or build knowing every commit will trip it. Never
route around it with `--no-verify`. No `.agents/settings.json`, or nothing wired → silent.

## Isolation is offered inline, and only from the base

<!-- rules -->

Taking a branch or a worktree, naming it, and stamping `branch: {base, work}` all happen inline in
the command body's own step 2 — not a separate command it dispatches to. The convention it applies
lives in
[git/isolation.md](../../references/git/isolation.md)
§Recording the isolation, cited rather than restated.

**The offer fires only when `HEAD` is on the repository's base branch.** Anywhere else, the human
already answered the question at checkout, and asking again is friction the loop does not need to
pay.

Two things the loop still needs, regardless of form:

- **A spec whose `plan/<id>-<handle>` ref is alive but checked out somewhere else is already being built
  there.** Starting a second run against it forks the work; say where it is and stop.
- **Work done in place carries no `branch` record**, so there is nothing to merge later and the
  report says so.

**Check before offering, every time.** A spec that is **already isolated** — its `plan/<id>-<handle>` ref
alive, or the `branch` record already stamped — has nothing left to take, and offering again buys
nothing but the turns it costs. Checking is `git branch --list "plan/<id>-<handle>"` plus the `branch`
record already inside the `status --json` the loop reads anyway, and it decides the question
without moving anything.

## The verification policy

<!-- rules -->

Declared per spec in the frontmatter (`verification`), written by `quenching-specs-develop`, read by
`cq specs status --spec <id> --json`. **Execute never decides when to test.**

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
`quenching-specs-conclude` runs **once**, as its pre-merge gate. When a task's `verify:` names one anyway,
say so and run the narrowest scope the tool offers rather than the whole suite by reflex — and
report the substitution, because a narrowed check is a narrowed claim.

**A harness that proves the *command surface* loads belongs to neither.** It is owned by the
command that edits the surface — `quenching-components-command-new`, or `quenching-components-command-eval` for a description.

## The validation loop

<!-- rules -->

For each task the policy says to verify:

1. Run the task's `verify:` command, from its declared `cwd:` — or, absent one, from the session's
   or worktree's root, exactly as before this key existed.
2. **Passes** → the task is done; go to the diff self-review.
3. **Fails** → read the failure, change the code, and run it again.

Two rules bound the loop:

- **Re-read from scratch after two consecutive failures.** Discard the working theory, re-read the
  task text, the files it declares, and the *current* diff (`git diff`) as if arriving fresh.
- **Stop when you stop making progress, and say so in the file.** There is no attempt counter.
  When the orchestrator judges that further attempts are repeating rather than converging, it
  writes the task blocked, with the reason:
  ```bash
  python3 "$(find "${CODEX_HOME:-$HOME/.codex}" "$HOME/.codex" -type f -path '*/quenching-codex*/scripts/cq' -print -quit 2>/dev/null)" specs task --spec "<id>" --block <id> --reason "<why, one line>"
  ```
  That writes a **visible marker into `## Tasks`** — `- [!] <id> <title> — blocked: <reason>` —
  and `cq specs next` then skips it and offers the following task, so one bad task never stalls
  the whole spec.

**`--block` requires `--reason`** (the tool refuses without one).

A human resumes a blocked task by fixing the cause and un-blocking it —
`cq specs task --spec <id> --uncheck <id>` returns it to `- [ ]` — after changing something,
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
whole-branch review runs once, and it belongs to `quenching-specs-conclude`.

## The commit — one per task, squashed to one per section

<!-- rules -->

After the self-review passes, **decide the subject, then verify, tick the box with it, commit, and
assert the subject survived**. This chain is unchanged by §The section squash below: every task
still gets its own commit here, and stays resumable from it, for as long as its section is still
open.

Run it as **one chained call**, gate included:

```bash
<the task's verify:> \
  && python3 "$(find "${CODEX_HOME:-$HOME/.codex}" "$HOME/.codex" -type f -path '*/quenching-codex*/scripts/cq' -print -quit 2>/dev/null)" specs task --check <id> --spec "<id>" --subject "<subject>" \
  && git add <the task's files> <the spec file> \
  && git commit -m "<subject>" \
  && git log -1 --format=%s
```

**The `&&` is the ordering:** verify before the tick, the tick before the commit, and a broken link
short-circuits every link after it. When the spec's declared policy says this task is not a gate,
the chain simply starts at `cq specs task`.

Stage the task's declared `files:` **and the spec file**, never the whole tree — `git add -A` also
picks up whatever an editor or a tool wrote while the task ran, which is the same contamination
§The precondition refuses at the start.

If the commit **fails** — a rejecting hook, nothing staged — undo the tick
(`cq specs task --spec "<id>" --uncheck <id>`) so no box claims a commit that does not exist, and
report the failure.

The **subject line format** is the target repo's to declare. Read
[git/commit.md](../../references/git/commit.md)
§Commit messages: a repo with `knowledge/standards/git/**` owns the format outright and this contract defers to it; with nothing
declared, the plugin's default is `plan/<id>-<handle>: <task-id> <task title>`. Never install a git
standard into a target to create the answer.

**Hard rules, no exceptions and no "just this once":**

- **Never `--no-verify`.** A commit hook that fails is a finding to report, not an obstacle to
  route around. The same goes for `--no-gpg-sign`.
- **Never disable, skip, `xfail`, or delete a test to make a task pass.**
- **Never edit the `verify:` command, the test, or the assertion so it stops failing.** Change the
  code, or report the task as blocked. Editing the check is how a spec ships a lie with a green
  checkbox.
- **Never amend or rewrite an earlier task's commit**, and never force-push. §The section squash
  is the one narrow exception, and only ever to the commits its OWN section just made — never a
  prior section's, never anything already shared.
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

**A task with no `files:` declared** — the line absent, or written `files: []` — is the same rule one
level down: it produces no diff of its own, so there is no commit to anchor to and no subject to
record. Its chain ends at the tick:

```bash
<the task's verify:> && python3 "$(find "${CODEX_HOME:-$HOME/.codex}" "$HOME/.codex" -type f -path '*/quenching-codex*/scripts/cq' -print -quit 2>/dev/null)" specs task --check <id> --spec "<id>"
```

— no `--subject`, no `git add`, no `git commit`. The box still ticks. Where the backend keeps the
spec in the tree, that tick rides along in the next task's commit or in the section's squash; under
an external backend it was never a local diff at all. Passing `--subject` here would write a
`subject:` onto the task line that `git log --grep` can never resolve, which is exactly the
placeholder the paragraph above refuses.

## The section squash

<!-- rules -->

At a section boundary (§The section boundary) with no `[!]` task in it, the section's own per-task
commits collapse into one — the unit a reviewer reads the branch by is the section, not the task,
while the retry safety net during the section stays exactly what §The commit above already gives
it.

```bash
git merge-base --is-ancestor <section-base-sha> HEAD \
  && git reset --soft <section-base-sha> \
  && git commit -m "plan/<id>-<handle>: <N> <section title>"
```

**`<section-base-sha>` is a sha — never a branch name, and never a `HEAD~n` counted by hand.** A ref
is resolved at the moment it is used, and the moment it is used is after everything that can move
it; a `HEAD~n` is a count that a retry or a fixup commit invalidates silently. The target of a
`reset` that rewrites history is always a sha.

**Capture it once, before the section's first task commits:**

```bash
git rev-parse HEAD^{commit}
```

That is the commit the section found. On a plan's first section it is the tip the branch already
carried before this run's first task.

**A run that resumed mid-section derives it** from the anchor the first task's line already carries,
rather than naming a commit by description again — `commit:` where the backend records a sha, else
the subject:

```bash
git log --grep "<the first task's recorded subject>" --fixed-strings --format=%H
```

and then that commit's parent (`<sha>^`). Capture and derivation answer the same commit; the
derivation exists because the capture lives in the session's head, and a section can be interrupted
mid-way — a blocked task, an interruption, a new session — while §The section boundary only
guarantees a clean stopping point at the section's *end*.

**The reset target is the commit before the section's first task — never that task's own commit.**
`git reset --soft <sha>` moves HEAD to `<sha>` while leaving the index exactly as it stands;
resetting to the first task's own commit would leave that task's changes already "consumed" by the
reset and out of the new commit.

**The ancestry guard runs before the reset, and its exit 0 is the reset's condition.** A target
outside the branch's own history is refused: `git merge-base --is-ancestor <section-base-sha> HEAD`
exiting non-zero is a finding, reported with the section's per-task commits left intact — the same
treatment a failed squash already gets below. The guard catches the whole class regardless of how
the target was named, which is why it is not merely a second opinion on the capture.

**Then repair every squashed task's commit record**, so `subject:` (or `commit:`, on a backend that
carries it) resolves to the commit that now actually exists rather than the one the squash just
replaced. The same `task --check` call, re-run per task, upserts the metadata in place:

```bash
python3 "$(find "${CODEX_HOME:-$HOME/.codex}" "$HOME/.codex" -type f -path '*/quenching-codex*/scripts/cq' -print -quit 2>/dev/null)" specs task --check <id> --spec "<id>" --subject "plan/<id>-<handle>: <N> <section title>"
```

Every task in the section ends up sharing that one subject — the anchor's granularity narrows from
task to section, which is exactly the trade this contract makes. `git log --grep` still resolves;
it now resolves to the section's commit for every task the section held.

**A `[!]` anywhere in the section skips both the squash and the repair, whole.** The section's
per-task commits stay exactly as they are — one per task — until the section closes for real; a
squash never runs partial.

**A squash that fails** — the `reset --soft` or the recommit rejected by a hook, nothing staged —
leaves the section's per-task commits untouched, the state before the squash was attempted. Report
it as a finding; never force past it (`--no-verify` is still forbidden here).

**Why this does not violate "never rewrite an earlier task's commit."** §The commit's hard rule
protects a section (or a session) that has already closed — reaching back into it would falsify a
record something else may already be resuming from. This squash reaches back only into the commits
its OWN section produced, at the exact moment that section closes, in the same run that made them.
"Earlier" in that rule means an earlier section or an earlier session, never the current section's
own just-made commits.

## Declared versus emergent `knowledge/`

<!-- rules -->

A task writes a `knowledge/standards/` doc **only when the task itself names it** — the path bulleted
under `## Impact`'s parsed `### Standards this spec will write into knowledge/standards/` sub-heading,
and named by that task. That doc is part of the task's deliverable: it is written before the
commit, reviewed in the same diff, and stamped `authority` honestly — `current` when the task
actually proved the rule, `background` when it is agreed but not yet proven.

Everything else the work reveals — a gotcha, a second-order consequence, a rule nobody had thought
of — costs **one line and no authoring**:

```bash
python3 "$(find "${CODEX_HOME:-$HOME/.codex}" "$HOME/.codex" -type f -path '*/quenching-codex*/scripts/cq' -print -quit 2>/dev/null)" specs discover "<id>" "<what was found, one line>"
```

It is captured **indiscriminately**. The lines are resolved by `quenching-specs-develop`'s
discoveries bank, and the doc an emergent finding deserves is written by
`quenching-specs-conclude` at distillation.

A task that writes into `knowledge/` is not delegated — §Delegating an executor.

## Delegating an executor — permitted, and bounded

<!-- rules -->

A per-task executor sub-agent (`Task`) is **permitted** when both hold:

- the task declares `files:` — the sub-agent gets a bounded scope, not the whole repo;
- the task writes nothing under `knowledge/`.

Pin it to the session model. **Never `haiku`** — it is writing production code, and the model
policy for that is the same one that protects `quenching-knowledge-import-memory`'s classifiers.

**The orchestrator keeps, without exception:** spec selection, the isolation offer, every
confirmation, every `cq specs task --check` flip, every `cq specs task --block` marker, every
`knowledge/standards/` write, every `cq specs discover` line, the commit, and the decision to pause. The
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
2. their declared `files:` sets are **provably disjoint** (`cq specs` checks this mechanically —
   see §The `[P]` check);
3. neither writes into `knowledge/`.

Serial is the default and needs no marker. Without proven file disjunction, parallel execution
trades wall-clock for merge conflicts and loses on both.

### The `[P]` check

<!-- rules -->

```bash
python3 "$(find "${CODEX_HOME:-$HOME/.codex}" "$HOME/.codex" -type f -path '*/quenching-codex*/scripts/cq' -print -quit 2>/dev/null)" specs parallel --spec "<id>" [--json]
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
`cq specs section <id> Handoff --write --scope global` for the evergreen block, or `--scope
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
- **Nothing extra is written.** `## Handoff`, `git log`, and the `subjects` `cq specs status`
  returns already carry everything a fresh session needs; the boundary adds no record and no fifth
  Handoff event. Accepted, the stop is a pause and a last commit — two events the cadence already
  has.
- **It offers and never imposes.** The loop does not end itself, and an unanswered offer means
  carry on.
- **The contract still ends at the last commit.** A stop here is not a close-out: the branch
  review, the merge and the archive remain `quenching-specs-conclude`'s, exactly as they are for a
  run that goes to the end.

## Tooling asides, relocated

### Why `Bash` is unrestricted

<!-- rationale -->

`quenching-specs-execute` is the one `quenching-specs-*` command that runs the target repo's own toolchain
— build, tests, linters, migrations, and `git` — as part of implementing a task. Its siblings are
scoped to `python3`/`py` because they only ever talk to `cq specs`.

### Why the resolved-whole notice matters

<!-- rationale -->

When `cq` does not resolve, the body falls back to `Read`ing the cited file whole and says so in
the report — because that is the run's context cost changing, not a cosmetic difference.

The only supported route above that fallback is the plugin's own per-call `cq` wrapper; it resolves
the installed plugin copy and nothing else. This sentence used to name a rung outside the
plugin, "the target's `.agents/hooks/cq`", which
[align/tool-resolution.md](../align/tool-resolution.md) §Resolving the tool forbids outright:
*there is no third rung*, never a copy under a target's `.agents/hooks/`. A copy that lives there is
never executed by anything the plugin runs, so a body that reached for it would have been reaching
for a file nobody keeps current.

### Why the declared files, never their folder

<!-- rationale -->

Measured, not assumed: on this repo, the four subject folders a spec touched held 19 files
(~31k tokens) against 5 files (~13k) for what `## Impact` declared, and that gap arrives at turn
one, where every later turn re-sends it.

### Why there is no mechanical net for an undeclared contract

<!-- rationale -->

The mirror image of the line above. `cq specs validate` already warns when a declared standard has
no task (`sp-impact-uncovered`); the inverse — a binding standard nobody declared — is not
derivable, because deciding a standard governs a task is reading, not parsing. Every approximation
of it has to re-read the folder to have something to warn about, which is the cost
`quenching-specs-execute` step 4 removed by reading only the declared files.

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

### Why one commit per task while a section is open, and why the subject rather than a sha

<!-- rationale -->

**There is no per-task bookkeeping commit any more.** It existed only because a sha cannot be known
before the commit that carries it, so the tick had to follow the commit and could not join it. One
task is one commit while its section is still open: code, docs the task named, and the ticked box.

One commit per task, while the section runs, is what makes retrying and resuming mid-section worth
having: a bad task can be blocked or undone without touching what already landed. §The section
squash then collapses the section's own commits into one once it closes — the unit the branch is
worth reading and reverting by is the section, and `git revert` undoes exactly one of those; the
per-task granularity is what buys the safety net getting there, not the shape the branch ends in.

The record cannot go stale: the rules above forbid amending an earlier *section's* commit and
forbid force-push — a section may only ever rewrite its own, at its own close. Unlike a sha it also
**survives a rebase**, so the one merge strategy that used to destroy every recorded link no longer
does.

### Why the squash target is a captured sha, and why ancestry is checked

<!-- rationale -->

**Measured on 2026-08-16**, branch `holetz/fast-status`, spec `listagem-ranqueada-nativa-no-cq-specs`.
The prose said *"the commit immediately BEFORE this section's first task"* and left the naming to
whoever executed it; on a first section that commit **is** the base's tip, so the executor reached
for the cheapest ref that satisfied the description — `develop`. Mid-run, another checkout
fast-forwarded `develop` by a whole front. Three section squashes resolved that ref to the **new**
tip, and the three commits went on to declare the removal of 17 files and the reversion of 45 more
the branch had never opened.

Nothing caught it: the tree was clean before and after, `cq specs validate` exited 0, and the suite
passed — the deleted files belonged to another front, with no test reaching them. Repair cost its
own commit and a manual re-application of the edits that collided.

The capture fixes the naming; the ancestry guard fixes the class. On that run the new tip of
`develop` was **not** an ancestor of the work branch, which is precisely why the reset carried the
branch onto a tree it had never built — so `git merge-base --is-ancestor` refuses it no matter how
the target was spelled. `assets/checks/section-squash-check.sh` is the fixture that holds the
property: history is not a claim any file's contents can carry, so it is proved by building one.

### Why squash is `conclude`'s caveat and not this loop's

<!-- rationale -->

**A squash-merge is the one caveat, and `conclude` owns it — a different squash from §The section
squash above.** A squashed *merge* leaves the section's own commits reachable only from the branch —
which is why `quenching-specs-conclude` records `merge: {strategy, subject}` and, on a squash,
offers to keep the branch. Nothing in this loop needs to know; recording the subject honestly is
the whole job here.

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
distinction `knowledge/standards/automation/session-evidence.md` §The rule a counted claim must obey
imposes, and it is stated as an estimate here because that is what it is. On this repo's
`configurable-spec-backend`, 18 of 29 tasks are delegation-eligible and 13 of them declare the same
file: the pre-refactor specs script (as it stood then, before this repo split it into a package), ~37k tokens.
Task-by-task that is ~13 × 37k ≈ 480k against roughly 150k for an
orchestrator reading it once and re-reading from cache — a delegation that reads as a saving and
is not one. Measured across the whole transcript archive, this permission had never once been
exercised, so nothing here revokes it; what was missing was the arithmetic that says when it pays.

### This is not `context: fork`, and the never-fork rule is untouched

<!-- rationale -->

The plugin's standing rule forbids `context: fork` **on these commands**, because a forked context
cannot present the mid-flow confirmations every sweep depends on — the conversation carrying the
human's OK would be out of reach.

Dispatching a `Task` for a bounded, file-scoped unit of work does the opposite: **the orchestrator
stays in the live conversation**, exactly where `quenching-knowledge-glossary-backfill` and
`quenching-knowledge-import` already dispatch from. One moves the decision-maker out of reach; the
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
