---
allowed-tools: Bash(cq:*), Bash(cq.cmd:*), Bash(git status:*), Bash(git diff:*), Bash(git log:*), Bash(git show:*), Bash(git add:*), Bash(git commit:*), Bash(git merge:*), Bash(git rebase:*), Bash(git rev-parse:*), Bash(git merge-base:*), Bash(python3:*), Read, Edit, AskUserQuestion
---

# /quenching-git conflict-resolve — finish a merge or rebase stopped on a conflict

**Input**: `$ARGUMENTS` — optionally the checkout (a worktree path) where the merge or rebase is
stopped. Omitted → the current checkout.

For a merge or rebase **already in progress**. `sync` and `merge` stop on a conflict and name this
flow; it is the only place a conflict is resolved on the human's behalf, and only when asked for.
It reads what each side meant, resolves hunk by hunk keeping both intentions, proves the result
with the target's own gate, and ends the operation. It never starts a merge or rebase, and it
never invents behaviour neither side had.

## Workflow

### 1. Read the state
```bash
git status
git diff --name-only --diff-filter=U
git rev-parse -q --verify MERGE_HEAD
git rev-parse -q --verify REBASE_HEAD
```
```text
git_read(verb="state")
```
Name the operation (merge or rebase), the files in conflict, and the two sides: for a merge,
`HEAD` is ours and `MERGE_HEAD` is theirs; **for a rebase the sides are inverted** — `HEAD` is the
base being rebased onto and the commit being replayed (`REBASE_HEAD`) is the work. No operation in
progress, or no conflicted file → report that and stop; a conflict-free tree is not this flow's
business. **Done when:** the operation, the conflicted files and what "ours" and "theirs" mean in
it are stated.

### 2. Find each side's intention in the sources
```bash
git merge-base HEAD <the other side>
git log --oneline <merge-base>..HEAD -- <file>
git log --oneline <merge-base>..<the other side> -- <file>
```
Per conflicted file, read the commits that touched it on each side, then the spec that owns them:
`cq specs find --commit <sha> --json` (or `--branch`, `--pr`) and its `## Proposal`/`## Design`.
The intention is what the commit subjects, the PR and the spec say, never what the diff alone
suggests. A side with no recoverable intention is stated as such. **Done when:** each conflicted
file has the intention of both sides in one line, or the absence of one is stated.

### 3. Resolve hunk by hunk
Open each file and edit its conflict markers — never a whole-file `--ours`/`--theirs`. For every
hunk, the result carries **both** intentions. Where they are incompatible, keep the one that
matches the declared goal of the operation (the branch's spec, or the base's behaviour for a
sync), and record the trade-off in one line for step 5. Behaviour new to both sides is never
written: if the resolution needs it, stop and ask on a decision sheet (a sub-agent returns
`STATE: blocked` with `NOTE: needs-human:`). Remove every marker; `git add` each file only once
no marker remains in it. **Done when:** no conflicted file holds a marker, each hunk keeps both
intentions or carries a recorded trade-off, and the files are staged.

### 4. Run the gate before concluding
Run the target's own gate — the command its configuration declares (`shared.ci`), else the gate its
docs name — over the resolved tree, in the foreground. A failure that the resolution caused
(the failing test or check touches a resolved hunk) **stops the run before any commit**: report
the failure, the hunk and the intentions in tension, and leave the operation in progress for the
human. A failure already present on the base is reported as such and is not this flow's to fix.
**Done when:** the gate is green, or the run has stopped uncommitted with the cause.

### 5. Conclude the operation
A merge: `git commit` with the subject git prepared, adding a line per recorded trade-off. A
rebase: `git rebase --continue`, and when the next commit stops on a conflict too, go back to
step 1 for it, until the rebase ends. Never `--skip` a commit, never `--abort` on the human's
behalf. Report the files resolved, each trade-off, the gate's outcome and the final `git status`.
A published branch whose history a rebase rewrote belongs to `/quenching-git push`'s confirmed
lease path; this flow does not publish. **Done when:** the operation has ended (`git status`
reports none in progress), or it is stopped on a conflict that step 3 sent to the human.

## Invariants

- Never start a merge or rebase here, and never `--skip` or `--abort` one.
- Never resolve a whole file with `--ours` or `--theirs`; every hunk is read.
- Never write behaviour neither side had; incompatible intentions are decided by the operation's
  declared goal and recorded, or asked.
- Never commit or continue over a gate that failed because of the resolution.
- Never publish; a rewritten branch's push is its own flow.
