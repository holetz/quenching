---
name: quenching-git-cleanup
description: "Prune merged or gone branches and orphan worktrees from `cq git stale`. Use for \"clean up old branches\", \"prune stale branches\". Not for: isolation → quenching-git-branch."
---

<!-- GENERATED FROM plugins/quenching/commands/git/cleanup.md -->

<!-- CODEX RUNTIME START -->
## Codex runtime

Use Codex host sub-agents only. Never launch Claude CLI, request Claude models, or fall back to Claude during a Codex run. The Claude source may separately delegate development to Codex. Read each named agent protocol and pass its role, prohibitions, model and effort to the host's spawn-agent tool; protocol files are not automatically registered agent types. Use host messaging, completion notifications and interrupt tools for lifecycle management. If delegation is unavailable, report the limitation; do not silently replace required independent verification with self-review.

Tier mapping: opus → `gpt-6-astra`; sonnet → `gpt-6.1-sol`; haiku → `gpt-6-luna`. Preserve declared effort. Pass model explicitly; when the host requires a fresh context for model overrides, use that mode and include the necessary brief and protocol. Use gpt-6-luna for product code only on ONE task whose `cq specs estimate --task` reports `oracleProtected` and `smallTierEligible` (an executable `verify:` whose tests sit outside the task's `files:`, nothing under `/docs/`, projected context at or under 80k); a failed `verify:` returns it to the session model. Never use gpt-6-luna for judgment roles or for import-memory classification/executor roles. Report tokens per model and role only when host telemetry provides them; otherwise `not measured`. Claude session logs and `cq components session cost` do not measure this Codex run.

<!-- CODEX RUNTIME END -->


# quenching-git-cleanup — prune what `cq git stale` already found

**Input**: `$ARGUMENTS` — optional `remote:<name>`; omitted → `origin`. This command always starts
from a fresh report for the selected remote.

## Workflow

### 1. Ask the tool for the current report
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
cq git stale --remote <remote> --json
```
The report contains local `staleBranches` (removable), `keptBranches` (staying, with reasons), fetched `remoteBranches` from `<remote>`, registered
`orphanWorktrees`, assessed `worktrees`, the `manifest` and its `groups`, and unregistered `unregisteredWorktrees` siblings with their path, branch and
size. `manifest` empty → say so and stop; there is nothing to prune. The `manifest` is the complete list, so a candidate that sits in no legacy list (a detached worktree) still keeps the run going. Do not fetch or run `git
remote prune` here: if the caller needs newer remote facts, it must fetch explicitly and start a
fresh cleanup run. The report's `remote` must equal the selected remote. **Done when:** the manifest and the selected remote are in hand.

### 2. Let the human pick what to prune
The report's `manifest` is the complete list: every entry carries a stable `id`, `kind`, `ref`, the
observed `tip`, `tipDate` (the committer date of that tip, never creation or last use; `null` when
unknown) with its `dateSource`, `status` (`candidate` or `preserved`), `reasons`, the exact
`action` and a `recommended` flag. Show every `preserved` entry (kept branches, ineligible
worktrees) with its reasons as information under "kept — not removable", and do not include it in the
prune choices. Show each `unregisteredWorktrees` finding with its path, branch and size as
information too.

Present concise choices, not one line per entry: summarize the report's `groups` (homogeneous
candidates by scope, kind, reasons and date provenance) with their count and `oldest`–`newest` tip
date, and expand an entry only when it stands alone. A group resolves to the `ids` it displays —
never to a target discovered later — and every selected item has its exact action available on
request (`git branch -d <branch>`, `git worktree remove <path>`; `cq git prune` runs them).

Put ONE decision sheet ([specs-develop/questions.md](../../references/specs-develop/questions.md) §1) that ends the turn; its decision lists the local
groups and items as numbered choices and accepts several in the reply (`D1 1,3`), or `none`.
Option A (recommended) is the `recommended` subset when the report marks one, else `none`; never
"all". A recommendation never authorizes anything. An unclear reply is asked again. **Done when:**
the local selection is settled.

A live `worktrees` candidate is eligibility only: it is merged, clean and unlocked, which is not
evidence that nobody uses it. Ask for the owner's explicit confirmation that each selected worktree
is inactive, separate from the local selection; without it, drop that worktree.

For any remote branch in the fresh `remoteBranches` list, show its exact destructive action
`git push <remote> --delete <branch>`, which `cq git prune --remote-branch` runs, and put it as its own decision on the sheet (`D2`, same recommendation rule). A remote branch is never
included in the local confirmation. **Done when:** the remote selection is settled and every selected
item has one explicit action.

### 3. Delete the chosen branches
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
cq git prune --branch <branch> --id <id> --expect-tip <tip> --json
```
`<id>` and `<tip>` are the ones the manifest displayed. The verb re-reads the stale report and acts only on a branch it still lists at that tip (exit 2 otherwise, and a moved tip means a fresh run);
git refusing (`error: the branch '<branch>' is not fully merged`, exit 1) → report why and leave it standing;
this command never escalates to `-D`. **Done when:** every chosen branch is deleted, or its refusal
is reported.

### 4. Remove the chosen worktrees
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
cq git prune --worktree <path> --id <id> --expect-tip <tip> --confirm-inactive --json
```
`--confirm-inactive` is passed only for a worktree the owner confirmed inactive. Orphan worktrees (directory missing) take neither flag. Worktree removal is **never --force**. A refusal (modified or untracked files inside) is reported with git's own
message, and that worktree is left standing. **Done when:** every chosen worktree is
removed, or its refusal is reported.

### 5. Delete the chosen remote branches
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
cq git prune --remote-branch <branch> --remote <remote> --id <id> --expect-tip <tip> --json
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
- Never offer `keptBranches` or `preserved` manifest entries for pruning: each is listed with the reason it stays.
- Never remove a live worktree without the owner's explicit inactivity confirmation, the displayed `id` and the approved tip.
- Never offer `unregisteredWorktrees` for pruning: `git worktree remove` does not act on an
  unregistered directory, and this class carries no action.
- Never delete a remote branch that `cq git stale` did not report in `remoteBranches`.
- Use only the selected remote (`origin` when omitted); a branch reported by another remote is not
  a candidate for this run.
- Never pre-select "all" in the prune offer — every item is the human's own pick.
- Never fetch or run `git remote prune` implicitly; the report is the fresh fact this run acts on.
- Never `git branch -D`, `git push --force`, or `git worktree remove --force`; a refusal is
  reported and the target is left standing for that specific refusal.
