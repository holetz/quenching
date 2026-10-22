---
name: quenching-git-sync
description: "Rebase the work branch onto the latest base with `--update-refs`. Use for \"sync this branch with main\", \"rebase onto the base\", \"catch this branch up\". Not for: conflicts → the human."
---

<!-- GENERATED FROM plugins/quenching/commands/git/sync.md -->

<!-- CODEX RUNTIME START -->
## Codex runtime

Use Codex host sub-agents only. Never launch Claude CLI, request Claude models, or fall back to Claude during a Codex run. The Claude source may separately delegate development to Codex. Read each named agent protocol and pass its role, prohibitions, model and effort to the host's spawn-agent tool; protocol files are not automatically registered agent types. Use host messaging, completion notifications and interrupt tools for lifecycle management. If delegation is unavailable, report the limitation; do not silently replace required independent verification with self-review.

Tier mapping: opus → `gpt-6-astra`; sonnet → `gpt-6.1-sol`; haiku → `gpt-6-luna`. Preserve declared effort. Pass model explicitly; when the host requires a fresh context for model overrides, use that mode and include the necessary brief and protocol. Use gpt-6-luna for product code only on ONE task whose `cq specs estimate --task` reports `oracleProtected` and `smallTierEligible` (an executable `verify:` whose tests sit outside the task's `files:`, nothing under `/docs/`, projected context at or under 80k); a failed `verify:` returns it to the session model. Never use gpt-6-luna for judgment roles or for import-memory classification/executor roles. Report tokens per model and role only when host telemetry provides them; otherwise `not measured`. Claude session logs and `cq components session cost` do not measure this Codex run.

<!-- CODEX RUNTIME END -->


# quenching-git-sync — rebase onto the latest base, refs and all

**Input**: `$ARGUMENTS` — the branch to sync. Omitted → the current branch.

Moves every commit unique to the work branch onto the base's current tip, carrying along stacked
local refs with `git rebase --update-refs`.

## Workflow

### 1. Confirm a clean tree, and snapshot the refs before rewriting
```bash
cq() {
  local plugin_root="${CODEX_PLUGIN_ROOT:-${PLUGIN_ROOT:-}}"
  if [ -z "$plugin_root" ]; then
    plugin_root="$(set -o pipefail
codex plugin list --json | python3 -c '
import json, os, sys
from pathlib import Path
plugins = [p for p in json.load(sys.stdin)["installed"] if p.get("name") == "quenching-codex" and p.get("enabled")]
if len(plugins) != 1:
    sys.exit("quenching-codex: enable exactly one installation, or provide its plugin root")
p = plugins[0]
home = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex")))
print(p.get("installedPath") or home / "plugins/cache" / p["marketplaceName"] / p["name"] / p["version"])
')" || return 2
  fi
  if [ -z "$plugin_root" ] || [ ! -f "$plugin_root/scripts/cq" ]; then
    echo "quenching-codex: installed plugin root not found; enable the plugin first" >&2
    return 2
  fi
  python3 "$plugin_root/scripts/cq" "$@"
}
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
