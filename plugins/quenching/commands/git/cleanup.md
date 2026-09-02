---
description: >-
  Prune branches already merged or gone and worktrees git still registers with no directory on disk,
  over `cq git stale`'s report.
  Use when the user asks to "clean up old branches", "prune stale branches", "remove finished
  worktrees", or "tidy up after merging". Not for: creating isolation → /quenching:git:branch;
  merging or opening a PR → /quenching:git:merge, /quenching:git:pr:create.
argument-hint: [remote:<name>]
allowed-tools: >-
  Bash(python3:*), Bash(git branch:*), Bash(git push:*), Bash(git worktree:*),
  Read, AskUserQuestion
---

# /quenching:git:cleanup — prune what `cq git stale` already found

**Input**: `$ARGUMENTS` — optional `remote:<name>`; omitted → `origin`. This command always starts
from a fresh report for the selected remote.

## Workflow

### 1. Ask the tool for the current report
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/assets/bin/cq git stale --remote <remote> --json
```
The report contains local `staleBranches`, fetched `remoteBranches` from `<remote>`, registered
`orphanWorktrees`, and unregistered `unregisteredWorktrees` siblings with their path, branch and
size. All four lists empty → say so and stop; there is nothing to prune. Do not fetch or run `git
remote prune` here: if the caller needs newer remote facts, it must fetch explicitly and start a
fresh cleanup run. The report's `remote` must equal the selected remote. **Done when:** all four
lists and the selected remote are in hand.

### 2. Let the human pick what to prune
Show every local stale branch with its reason(s), every remote branch as `<remote>/<branch>` with
its reason(s), and every orphan worktree with its path and branch. Show each `unregisteredWorktrees`
finding with its path, branch and size as information, but do not include it in the prune choices.
Ask once with **AskUserQuestion** (multi-select) which local branches and live worktrees to prune —
defaulting to none pre-selected, never to "all". Show the exact local actions in those choices:
`git branch -d <branch>` or `git worktree remove <path>`. **Done when:** the local selection is
settled.

For any remote branch in the fresh `remoteBranches` list, show its exact destructive action `git
push <remote> --delete <branch>` and ask separately with **AskUserQuestion**. A remote branch is never
included in the local confirmation. **Done when:** the remote selection is settled and every selected
item has one explicit action.

### 3. Delete the chosen branches
```bash
git branch -d <branch>
```
Refused (`error: the branch '<branch>' is not fully merged`) → report why and leave it standing;
this command never escalates to `-D`. **Done when:** every chosen branch is deleted, or its refusal
is reported.

### 4. Remove the chosen worktrees
```bash
git worktree remove <path>
```
Worktree removal is **never --force**. A refusal (modified or untracked files inside) is reported with git's own
message, and that worktree is left standing. **Done when:** every chosen worktree is
removed, or its refusal is reported.

### 5. Delete the chosen remote branches
```bash
git push <remote> --delete <branch>
```
Run this only for a selected item from the fresh `remoteBranches` list, after the separate remote
confirmation. The command is an external write: report its exact remote/branch and its output. A
refusal leaves the server branch standing; never retry with another command or infer success from a
local remote-tracking ref. **Done when:** every selected remote branch was deleted, or its refusal
was reported.

### 6. Report
State what was deleted, what was refused (and why), and what was left untouched because it was
never chosen. Separate local branches, remote branches, and worktrees in the report. **Done when:**
the three outcome classes are named.

## Invariants

- Never prune a branch or worktree `cq git stale` did not report.
- Never offer `unregisteredWorktrees` for pruning: `git worktree remove` does not act on an
  unregistered directory, and this class carries no action.
- Never delete a remote branch that `cq git stale` did not report in `remoteBranches`.
- Use only the selected remote (`origin` when omitted); a branch reported by another remote is not
  a candidate for this run.
- Never pre-select "all" in the prune offer — every item is the human's own pick.
- Never fetch or run `git remote prune` implicitly; the report is the fresh fact this run acts on.
- Never `git branch -D`, `git push --force`, or `git worktree remove --force`; a refusal is
  reported and the target is left standing for that specific refusal.
