---
name: quenching-git-sync
description: "Rebase the current (or named) work branch onto the latest base, with `--update-refs` so any other local branch stacked on top moves along instead of being orphaned by the rewrite. Use when the user asks to \"sync this branch with develop/main\", \"rebase onto the base\", \"catch this branch up\", or \"update my branch before I keep working\". Not for: merging a finished branch home → quenching-git-merge."
---

<!-- GENERATED FROM plugins/quenching/commands/git/sync.md -->


# quenching-git-sync — rebase onto the latest base, refs and all

**Input**: `$ARGUMENTS` — the branch to sync. Omitted → the current branch.

Moves every commit unique to the work branch onto the base's current tip, and carries along any
other local branch pointing at a commit inside that range — `git rebase`'s own `--update-refs`,
which stops a stacked branch from being silently orphaned by a rewrite it was never told about.

## Workflow

### 1. Confirm a clean tree, and snapshot the refs before rewriting
```bash
git status --porcelain
python3 "$(find "${CODEX_HOME:-$HOME/.codex}" "$HOME/.codex" -type f -path '*/quenching-codex*/scripts/cq' -print -quit 2>/dev/null)" git base --json
git for-each-ref --format='%(refname:short) %(objectname)' refs/heads
```
Non-empty `git status --porcelain` → refuse and name the paths; a rebase on a dirty tree can turn
an unrelated edit into a conflict with no way to tell which commit caused it. **Done when:** the
tree is confirmed clean, the base is resolved, and every local branch's tip is recorded for the
comparison in step 4.

### 2. Update the base from its remote, where one exists
```bash
git fetch origin <base> 2>&1 || echo "NO-REMOTE"
```
`NO-REMOTE` (or no `origin`) → rebase onto the local `<base>` as it stands, silently; most work in
a single-checkout repo has no remote to fetch, and that is the ordinary case, never a finding.
**Done when:** the base is as fresh as this checkout can make it.

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
one `--update-refs` carried along; name each. **Done when:** the moved-refs list (possibly empty)
is stated alongside the rebase's own outcome.

## Invariants

- Never rebase over a dirty tree.
- Never resolve a conflict or `--skip` a commit on the human's behalf — report and hand back the
  two git commands that end the rebase.
- Never rebase onto a base this checkout has not just tried to freshen from its remote.
