---
name: quenching-git-merge
description: "Merge a branch into its base with one of four strategies, offered to the human. Use for \"merge this branch\", \"land this work\". Not for: opening a PR → quenching-git-pr-create; pruning → quenching-git-cleanup."
---

<!-- GENERATED FROM plugins/quenching/commands/git/merge.md -->

<!-- CODEX RUNTIME START -->
## Codex runtime

Use Codex host sub-agents only. Never launch Claude CLI, request Claude models, or fall back to Claude during a Codex run. The Claude source may separately delegate development to Codex. Read each named agent protocol and pass its role, prohibitions, model and effort to the host's spawn-agent tool; protocol files are not automatically registered agent types. Use host messaging, completion notifications and interrupt tools for lifecycle management. If delegation is unavailable, report the limitation; do not silently replace required independent verification with self-review.

Tier mapping: opus → `gpt-6-astra`; sonnet → `gpt-6.1-sol`; haiku → `gpt-6-luna`. Preserve declared effort. Pass model explicitly; when the host requires a fresh context for model overrides, use that mode and include the necessary brief and protocol. Use gpt-6-luna for product code only on ONE task whose `cq specs estimate --task` reports `oracleProtected` and `smallTierEligible` (an executable `verify:` whose tests sit outside the task's `files:`, nothing under `/docs/`, projected context at or under 80k); a failed `verify:` returns it to the session model. Never use gpt-6-luna for judgment roles or for import-memory classification/executor roles. Report tokens per model and role only when host telemetry provides them; otherwise `not measured`. Claude session logs and `cq components session cost` do not measure this Codex run.

<!-- CODEX RUNTIME END -->


# quenching-git-merge — bring a branch home, on the human's own strategy

**Input**: `$ARGUMENTS` — a spec id (its `branch.work`/`branch.base` records name the branch and
target) or a bare branch name to merge into the resolved base. Omitted → ask.

The four strategies, the squash caveat and the post-merge worktree removal are in
[git/merge.md](../../references/git/merge.md).

## Workflow

### 1. Load the rules and resolve branch, base and checkout
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
cq components read ../../references/git/merge.md \
  --sections "§Merge strategies" --sections "§The squash caveat" \
  --sections "§The worktree is removed after a successful merge"
cq components read ../../references/git/conventions.md \
  --sections "§The declared-directive layer"
cq git conventions --json   # `config.mergeSubject`, or absent
cq git base --json
git worktree list --porcelain
```
An ID in `$ARGUMENTS` → `cq specs status --spec "<id>" --json`, its `branch.work` is the branch
to merge and `branch.base` the target (falling back to `cq git base`'s answer where absent). A bare
branch name → merge it into `cq git base`'s answer. No checkout in the worktree list holds the base
→ **stop without merging**, naming the base and the fix (provide a checkout or add a worktree of it
outside this command). Never check out the base here.
**Done when:** the branch, the base, and the checkout that holds it are all resolved, or the run has
stopped for lack of one.

### 2. Offer the strategy, and the branch's fate under squash
Show the trade in one line each, from §Merge strategies, and put it on ONE decision sheet ([specs-develop/questions.md](../../references/specs-develop/questions.md) §1) that ends the turn; the options
of `D1`, with A the recommended one:

- **A (recommended) merge commit** — every per-task commit stays on the base, one extra commit.
- **B squash** — one commit on the base; the per-task commits survive only on the branch itself.
- **C rebase** — linear history, per-task commits preserved through the rewrite.
- **D fast-forward** — nothing rewritten or added; only possible when the base has not moved.

**Squash chosen → offer, separately, not to delete the branch** — deleting it strands every commit
subject the archived record resolves against. The offer records the human's preference, but this
command never deletes the branch. **Done when:** the strategy is chosen, and, under squash, the
branch-survival preference is recorded.

### 3. Run it in the base's own checkout
The subject the strategy writes follows §The declared-directive layer's table:
`config.mergeSubject` from step 1 where declared, else the target's docs, else
`plan/<id>-<handle>: merge (<strategy>)` from [git/commit.md](../../references/git/commit.md)
§Commit messages. `fast-forward` writes no commit, so it has no subject to govern.
```bash
git -C <the checkout from step 1> <the chosen strategy's command>
```
Never `git checkout <base>` — from inside a worktree it fails outright
(`fatal: '<base>' is already used by worktree at …`, exit 128). A failure is reported verbatim; nothing downstream runs. **Done when:** the
merge command exits 0, or the run has stopped on its failure.

### 4. Stamp, with an ID
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
cq specs record "<id>" merge --set strategy=<strategy> --set subject=<the merge commit's subject, or "none — <why>" under fast-forward/rebase>
```
Write-once — a record already present is read, never overwritten. No ID → nothing to stamp.
**Done when:** the record is stamped (with an ID) or explicitly skipped (without one).

### 5. Remove the worktree, only after a verified merge
Only when step 1's worktree list held a **separate** worktree for the merged branch (not the base's
own checkout) and step 3 exited 0:
```bash
git -C <the base's checkout> worktree remove <the worktree path>
```
**Never `--force`.** `git worktree remove` refuses a tree holding modified or untracked files on its
own; report the refusal and leave the worktree standing. Never deletes the branch itself. **Done when:** the worktree is removed, refused with
its own error reported, or the step was skipped because there was none to remove.

### 6. Report
State the strategy, the merge commit (or the explicit none) and **which layer governed its
subject**, what was stamped, and the worktree's fate. **Done when:** all four are named.

## Invariants

- Never `git checkout <base>` to reach the checkout that merges — always `git -C`.
- Never merge without a checkout that already holds the base; never manufacture one or check it out
  from this command.
- Never `--force` a worktree removal, and never remove one before a merge verified at exit 0.
- Offer the strategy; never choose it for the human.
- Never install `docs/standards/git/**` into the target, and never write `gitConventions` into its
  `.claude/quenching.json`; a declared convention is read here, never written back.
