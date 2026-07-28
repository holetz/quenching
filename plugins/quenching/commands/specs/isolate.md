---
description: Take or report git isolation for ONE spec — a branch or a worktree, at any stage of its life. Triggers on "isolate this spec", "cut a branch for this spec", "work on this in a worktree", "put this spec on its own branch", "am I isolated?", "which branch is this spec on", "is anything in flight". Records branch: {base, work}, the one git fact no derivation recovers once the branch is merged. Not for: building a spec's tasks → /specs:execute; merging, reviewing or archiving → /specs:conclude; creating a spec → /specs:create; interrogating one → /specs:develop; choosing which spec to work on → /specs:continue.
argument-hint: [spec slug, or nothing to infer it]
allowed-tools: Read, Grep, Glob, Edit, Bash(git:*), Bash(python3:*), Bash(py:*), AskUserQuestion
---

# /specs:isolate — one spec, one branch

**Input**: `$ARGUMENTS` — optionally a spec slug. Omitted → infer from the conversation or from the
branch already checked out; vague or ambiguous → you MUST prompt.

Takes **or reports** isolation for ONE spec. Isolation used to be a privilege of building, created
inside `/specs:execute` and available nowhere else — but creating and developing a spec also write
into `specs/plans/` and dirty the tree, and a spec sometimes ought to be born on the branch that
will carry its work.

Every git convention this command applies — the `plan/<slug>` name, the worktree placement, the
`branch: {base, work}` record and its write-once rule, the read-if-present contract for a target's
own `docs/standards/git/**` — lives in
[specs-isolate/git.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-isolate/git.md), which this
body owns and never restates.

The spec-driven facts — the layout, the derived stages, the record vocabulary, the `specs.py`
surface — live in
[specs-develop/spec-driven.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-develop/spec-driven.md).

**This command never merges.** The merge stays inside `/specs:conclude`, behind that command's
review and archive gates. A merge invocable on its own could run against a spec nobody reviewed and
nothing archived, and would have to duplicate every refusal `conclude` already owns. There is no
single verb covering "take isolation" and "merge", which is the evidence they are two actions.

**This command never writes code and never touches `## Tasks`.** It moves a spec onto a branch and
records that it did; building is `/specs:execute`.

## Resolving the tool

Resolve `specs.py` by the fallback in
[specs-create/plans-zone.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-create/plans-zone.md)
§Resolving the tool. Invoke with `python3`/`py`; branch on the **exit code** (0 ok · 1 findings ·
2 refusal) and the `--json`, never on prose.

## Workflow

### 1. Select the spec
A slug was given → use it. Otherwise infer from the conversation, or from the checked-out branch
when it matches `plan/<slug>`; failing both, run `specs.py next --front --json` and pick with
**AskUserQuestion** — its `branch: {work, live, current}` already says which specs are in flight.
**Done when:** one spec is resolved, or the run stops because none could be.

### 2. Read the git state, and answer the read-only question first
```bash
specs.py status --spec "<slug>" --json
git rev-parse --is-inside-work-tree
git branch --list "plan/<slug>"
git worktree list
git branch --show-current
```
Four facts decide everything below: whether this is a git repo, whether the spec carries a `branch`
record, whether its ref is **alive**, and whether it is checked out here.

| State | What this command does |
| --- | --- |
| ref alive and checked out here | **reports it and stops** — already isolated, nothing to take |
| ref alive elsewhere (branch or worktree) | reports where, offers to check it out or add a worktree; never a second branch |
| record present, ref gone | reports the record as **stale history** — the branch was merged or deleted. Never rewrite it |
| no record, no ref | the offer in step 4 |
| not a git repo | say so once and stop. Never `git init` on the human's behalf |

**Asking is a legitimate whole use of this command.** "Am I isolated?" is answered here, writes
nothing, and costs the calls above.
**Done when:** the state is in hand and a read-only question has been answered, or the run
continues to step 3.

### 3. Check the tree, and see where the spec file currently lives
```bash
git status --porcelain
git log --oneline -1 -- "<the spec's path>"
```
A dirty tree is **not** refused here — this command commits nothing but the spec file, and a
half-finished edit elsewhere is the human's business. Report it, and never sweep it onto the branch
with `git add -A`.

Whether the spec file is already committed on the base decides what step 5 can do:

- **uncommitted** → cutting the branch carries it, and the base keeps no trace of it;
- **already committed on the base** → it is part of the base's history and stays there. The branch
  simply starts from it. **Never rewrite the base branch to move it**, and say plainly that the
  base already carries the spec.

**Done when:** the tree state and the spec file's git status are known and reported.

### 4. Offer the form — one plan, one OK
State in one block: the spec, the base branch, the branch name that will be created, whether the
spec file rides along, and what will be stamped. Then ask with **AskUserQuestion**:

- **Branch** *(default)* — `git checkout -b plan/<slug>`, work continues in this checkout;
- **Worktree** — `git worktree add ../<repo>-<slug> -b plan/<slug>`, a separate checkout beside the
  repo, leaving this one where it is;
- **In place** — declines isolation. Nothing is created and **nothing is stamped**.

Recommend isolation before building, and never impose it. A human who declines gets no branch, no
record, and no second prompt.
**Done when:** the human has chosen, or declined and the run has stopped.

### 5. Take it
Run the one command for the chosen form. Then, when the spec file was uncommitted, commit **that
file alone** on the new branch so the base is left exactly as it was:

```bash
git add "<the spec's path>" && git commit -m "plan/<slug>: record the spec on its own branch"
```

Nothing else is staged, and no other file is committed. If the checkout or the worktree fails —
a name already taken, a dirty path, a locked worktree — report the git error verbatim and stop
without stamping.
**Done when:** the branch or worktree exists, or the failure is reported and nothing was stamped.

### 6. Stamp the record
```yaml
branch: {base: <what was checked out>, work: plan/<slug>}
```
`base` is captured **now**, while it is still true: after the merge git cannot say what the branch
was cut from, which is the whole reason the record exists. Stamp nothing for work done in place.

The record is write-once. One already present is **read, never rewritten** — and a current branch
that disagrees with `work` is a finding to report, not a value to correct.
**Done when:** the record is stamped, or the reason it was deliberately not stamped is stated.

### 7. Report, and hand off
Show the spec, the form taken, the base and work branches, the worktree path when there is one,
whether the spec file was carried onto the branch, and the record as stamped. Then name the command
that comes next — `/specs:develop` for a spec still being shaped, `/specs:execute` for one ready to
build — and stop.
**Done when:** the summary is shown and the next command has been named.

## Doctrine

- **The ref is the signal, never the record.** A human may cut `plan/<slug>` by hand and stamp
  nothing, and a record outlives the branch it names. Anything asking "is this in flight?" asks git
  for a live ref; the record only supplies the ref's name when it is not the default.
- **One branch per spec, ever.** A spec whose ref is already alive is never given a second one. The
  offer becomes "check it out" or "add a worktree over the existing branch".
- **Never rewrite history to relocate a spec.** No amend, no rebase of the base, no force-push, no
  `git reset` on a shared branch. A spec already committed to the base stays committed to the base.
- **Never `git add -A`.** This command commits at most one file — the spec — and a dirty tree
  belongs to whoever dirtied it.
- **Never `git init`, and never force isolation.** In place is a legitimate answer, and it stamps
  nothing precisely because a record whose `base` equals its `work` states no fact.
- **`create` and `develop` forward here on request and never offer unprompted.** A new prompt in
  the two most-run commands would cost friction for everyone to serve the minority isolating early;
  that stays open until the command has been used in anger.

## Invariants to never violate

- Report before writing: the read-only answer is a complete use of this command.
- One plan → one OK before anything is created. Creating a branch is cheap; creating it unasked is
  not.
- Stamp `branch:` only when isolation was actually taken, and never over an existing record.
- Never merge, never review, never archive — those are `/specs:conclude`, with their own gates.
- Never write code, never touch `## Tasks`, never tick a box.
- Drive off `specs.py status` and git's own output, branching on exit codes rather than prose.
