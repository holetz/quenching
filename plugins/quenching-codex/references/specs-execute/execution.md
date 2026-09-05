# The execution contract — verify, review, commit

The owner of **how** `quenching-specs-execute` verifies and commits one task. The command body
owns the workflow (select → isolate → read → loop → hand off); this file owns the core mechanics,
while delegation and handoff cadence live in focused references.

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

## The commit — one per task

<!-- rules -->

After the self-review passes, **verify, stage the declared files, commit, assert the subject survived,
then tick the provider task with its subject and commit**. Every task with a diff gets its own commit
and stays resumable from it. The provider write is deliberately last: an external backend cannot
travel inside the local commit, and a failed write must leave the commit available for a retry.

Run it as **one chained call**, gate included:

```bash
<the task's verify:> \
  && git add <the task's files> \
  && Skill("quenching:git:commit", "<id>") \
  && python3 "$(find "${CODEX_HOME:-$HOME/.codex}" "$HOME/.codex" -type f -path '*/quenching-codex*/scripts/cq' -print -quit 2>/dev/null)" specs task --check <id> --spec "<id>" --subject "<subject reported by git:commit>" --commit "<sha reported by git:commit>"
```

**The `&&` is the ordering:** verify before staging, staging before the delegated commit, the
commit before the provider tick, and a broken link short-circuits every link after it. When the
spec's declared policy says this task is not a gate, the chain simply starts at `git add`.

Stage only the task's declared `files:`, never the whole tree and never an assumed spec file —
`git add -A` also picks up whatever an editor or a tool wrote while the task ran, which is the same
contamination §The precondition refuses at the start. The delegated `quenching-git-commit` owns
subject resolution and the existing index; execute passes its reported subject and sha to the
provider write.

If verification, staging or the commit **fails** — a rejecting hook or nothing staged — no provider
tick has happened; report the failure and leave the task unchecked. If the commit succeeds but the
provider tick **fails** — a network error, refusal or timeout — preserve the commit, report the
recoverable remote-write failure with its subject and sha, and retry the provider write without
rebuilding or amending the commit.

The **subject line format** is the target repo's to declare. Read
[git/commit.md](../../references/git/commit.md)
§Commit messages: a repo with `docs/standards/git/**` owns the format outright and this contract defers to it; with nothing
declared, the plugin's default is `plan/<id>-<handle>: <task-id> <task title>`. Never install a git
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

The subject lands on the task line as `subject: <line>` together with `commit: <sha>`, in the
indented metadata grammar `files:` and `verify:` already use. The subject resolves with
`git log --grep=<subject> --fixed-strings`; the commit sha is the stronger direct anchor. A
`commit-msg` hook that only *adds* — a ticket prefix, a `Change-Id`, a sign-off — leaves it
matching as a substring and needs nothing. A hook that **replaces** the subject outright breaks the
link: **report it as a finding and write nothing.**

With no git in the repo there is nothing to anchor to: tick the box without `--subject` and say so
once in the report, rather than inventing a placeholder.

**A task with no `files:` declared** — the line absent, or written `files: []` — is the same rule one
level down: it produces no diff of its own, so there is no commit to anchor to and no subject or
commit sha to record. Its chain ends at the provider tick:

```bash
<the task's verify:> && python3 "$(find "${CODEX_HOME:-$HOME/.codex}" "$HOME/.codex" -type f -path '*/quenching-codex*/scripts/cq' -print -quit 2>/dev/null)" specs task --check <id> --spec "<id>"
```

— no `--subject`, no `git add`, no `git commit`. The box still ticks. Where the backend keeps the
spec in the tree, that tick rides along in the next task's commit; under an external backend it is
never a local diff at all. Passing `--subject` here would write a
`subject:` onto the task line that `git log --grep` can never resolve, which is exactly the
placeholder the paragraph above refuses.
