---
description: "Rebase the work branch onto the latest base with `--update-refs`. Use for \"sync this branch with main\", \"rebase onto the base\", \"catch this branch up\". Not for: conflicts → the human."
---

<!-- GENERATED FROM plugins/quenching/commands/git/sync.md -->

<!-- OPENCODE RUNTIME START -->
## OpenCode runtime

Delegate only through OpenCode's task tool, to the registered subagents named `quenching-<agent>` (protocol copies live under `~/.config/opencode/quenching/agents/`). Never launch the Claude CLI and never request a Claude model during an OpenCode run. Source model tiers are not pinned here: every command and subagent runs on the model the OpenCode session configures; a declared tier or effort below is a preference to report, not a switch. Token usage comes from host telemetry when it exists, otherwise it is `not measured`; `cq components session cost` and `context` read no OpenCode log and refuse (exit 2, unmeasured). If delegation is unavailable, report the limitation; never replace a required independent verification with self-review.

<!-- OPENCODE RUNTIME END -->


# quenching-git-sync — rebase onto the latest base, refs and all

**Input**: `$ARGUMENTS` — the branch to sync. Omitted → the current branch.

Moves every commit unique to the work branch onto the base's current tip, carrying along stacked
local refs with `git rebase --update-refs`.

## Workflow

### 1. Confirm a clean tree, and snapshot the refs before rewriting
```bash
cq() { python3 "${QUENCHING_OPENCODE_ROOT:-${XDG_CONFIG_HOME:-$HOME/.config}/opencode/quenching}/scripts/cq" "$@"; }
git status --porcelain
cq git base --json
git for-each-ref --format='%(refname:short) %(objectname)' refs/heads
```
Non-empty `git status --porcelain` → refuse and name the paths. **Done when:** the
tree is confirmed clean, the base is resolved, and every local branch's tip is recorded for the
comparison in step 4.

### 2. Update the base from its remote, where one exists
```bash
if git remote get-url origin >/dev/null 2>&1; then
  git fetch origin <base>
else
  echo "NO-REMOTE"
fi
```
No persistent fetch configuration is changed. A missing `origin` emits `NO-REMOTE` and uses the local
`<base>` as it stands. A fetch error is reported and stops the run; it is not treated as no remote.
**Done when:** the base is fetched successfully or the absence of `origin` is reported.

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
one `--update-refs` carried along; name each. State whether a remote was available and whether the
base fetch succeeded. If the synced branch had a remote tip before the rebase, report that its next
publication belongs to `quenching-git-push`'s confirmed `--force-with-lease` path; do not publish
from this command. **Done when:** the moved-refs list (possibly empty), the fetch outcome and any
required lease publication are stated alongside the rebase's own outcome.

## Invariants

- Never rebase over a dirty tree.
- Do not persist fetch configuration as a side effect; remote pruning is outside this command's
  scope.
- Never resolve a conflict or `--skip` a commit on the human's behalf — report and hand back the
  two git commands that end the rebase.
- Never rebase onto a base this checkout has not just tried to freshen from its remote.
