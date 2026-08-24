---
description: >-
  Prune branches already merged or gone and worktrees git still registers with no directory on disk,
  over `cq git stale`'s report.
  Use when the user asks to "clean up old branches", "prune stale branches", "remove finished
  worktrees", or "tidy up after merging". Not for: creating isolation → /quenching:git:branch;
  merging or opening a PR → /quenching:git:merge, /quenching:git:pr:create.
argument-hint: [none]
allowed-tools: Bash(python3:*), Bash(git branch:*), Bash(git worktree:*), Read, AskUserQuestion
---

# /quenching:git:cleanup — prune what `cq git stale` already found

**Input**: `$ARGUMENTS` — none; this command always starts from a fresh report.

## Workflow

### 1. Ask the tool for the current report
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/assets/bin/cq git stale --json
```
Both lists empty → say so and stop; there is nothing to prune. **Done when:** the stale-branches and
orphan-worktrees lists are in hand.

### 2. Let the human pick what to prune
Show every stale branch with its reason(s) and every orphan worktree with its path and branch, then
ask with **AskUserQuestion** (multi-select) which to prune — defaulting to none pre-selected, never
to "all". **Done when:** the human has chosen a subset (possibly empty) of each list.

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
**Never `--force`.** A refusal (modified or untracked files inside) is reported with git's own
message, and that worktree is left standing. **Done when:** every chosen worktree is
removed, or its refusal is reported.

### 5. Report
State what was deleted, what was refused (and why), and what was left untouched because it was
never chosen. **Done when:** the three are named.

## Invariants

- Never prune a branch or worktree `cq git stale` did not report.
- Never pre-select "all" in the prune offer — every item is the human's own pick.
- Never `git branch -D` or `git worktree remove --force`; a refusal is reported and the target is left standing.
  for that specific refusal.
