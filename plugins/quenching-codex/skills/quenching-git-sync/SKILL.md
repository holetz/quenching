---
name: quenching-git-sync
description: "Rebase the current (or named) work branch onto the latest base, with `--update-refs`. Use when the user asks to \"sync this branch with develop/main\", \"rebase onto the base\", \"catch this branch up\", or \"update my branch before I keep working\". Not for: resolving conflicts → the human; creating a branch → quenching-git-branch."
---

<!-- GENERATED FROM plugins/quenching/commands/git/sync.md -->


# quenching-git-sync — rebase onto the latest base, refs and all

**Input**: `$ARGUMENTS` — the branch to sync. Omitted → the current branch.

Moves every commit unique to the work branch onto the base's current tip, carrying along stacked
local refs with `git rebase --update-refs`.

## Workflow

### 1. Confirm a clean tree, and snapshot the refs before rewriting
```bash
git status --porcelain
python3 "$(find "${CODEX_HOME:-$HOME/.codex}" "$HOME/.codex" -type f -path '*/quenching-codex*/scripts/cq' -print -quit 2>/dev/null)" git base --json
git for-each-ref --format='%(refname:short) %(objectname)' refs/heads
```
Non-empty `git status --porcelain` → refuse and name the paths. **Done when:** the
tree is confirmed clean, the base is resolved, and every local branch's tip is recorded for the
comparison in step 4.

### 2. Configure pruning and update the base from its remote, where one exists
```bash
git config fetch.prune true
if git remote get-url origin >/dev/null 2>&1; then
  git fetch origin <base>
else
  echo "NO-REMOTE"
fi
```
`fetch.prune=true` is persisted in this repository, so this and future fetches remove remote-tracking
refs. A missing `origin` emits `NO-REMOTE` and uses the local `<base>` as it stands. A fetch error is
reported and stops the run; it is not treated as no remote. **Done when:** pruning is configured and
the base is either fetched successfully or the absence of `origin` is reported.

### 3. Rebase, carrying stacked refs along
```bash
git rebase <base or origin/base> --update-refs <branch from $ARGUMENTS, or the current branch>
```
**Stops on conflict** → report the conflicting files and git's own message, and say plainly that
`git rebase --continue` (after resolving) or `git rebase --abort` are the human's own next move.
Never resolve a conflict on the human's behalf, and never `--skip` a commit silently — a skipped
commit is a silent loss the next read of `git log` would not reveal. **Done when:** the rebase
completes clean, or it is stopped on a conflict with the resolution path stated.

### 4. Report which refs moved
```bash
git for-each-ref --format='%(refname:short) %(objectname)' refs/heads
```
Diff against step 1's snapshot — every ref whose object changed besides the branch being synced is
one `--update-refs` carried along; name each. State that `fetch.prune=true` was configured in step
2. **Done when:** the moved-refs list (possibly empty) and the pruning configuration are stated
alongside the rebase's own outcome.

## Invariants

- Never rebase over a dirty tree.
- Always configure `fetch.prune=true` before fetching the base, so deleted remote branches do not
  remain as stale remote-tracking refs.
- Never resolve a conflict or `--skip` a commit on the human's behalf — report and hand back the
  two git commands that end the rebase.
- Never rebase onto a base this checkout has not just tried to freshen from its remote.
