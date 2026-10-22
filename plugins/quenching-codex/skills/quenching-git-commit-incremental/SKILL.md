---
name: quenching-git-commit-incremental
description: "Turn pending worktree changes into small cohesive commits with one confirmation. Use for \"organize and commit my worktree\". Not for: the staged index → quenching-git-commit."
---

<!-- GENERATED FROM plugins/quenching/commands/git/commit-incremental.md -->

<!-- CODEX RUNTIME START -->
## Codex runtime

Use Codex host sub-agents only. Never launch Claude CLI, request Claude models, or fall back to Claude during a Codex run. The Claude source may separately delegate development to Codex. Read each named agent protocol and pass its role, prohibitions, model and effort to the host's spawn-agent tool; protocol files are not automatically registered agent types. Use host messaging, completion notifications and interrupt tools for lifecycle management. If delegation is unavailable, report the limitation; do not silently replace required independent verification with self-review.

Tier mapping: opus → `gpt-6-astra`; sonnet → `gpt-6.1-sol`; haiku → `gpt-6-luna`. Preserve declared effort. Pass model explicitly; when the host requires a fresh context for model overrides, use that mode and include the necessary brief and protocol. Use gpt-6-luna for product code only on ONE task whose `cq specs estimate --task` reports `oracleProtected` and `smallTierEligible` (an executable `verify:` whose tests sit outside the task's `files:`, nothing under `/docs/`, projected context at or under 80k); a failed `verify:` returns it to the session model. Never use gpt-6-luna for judgment roles or for import-memory classification/executor roles. Report tokens per model and role only when host telemetry provides them; otherwise `not measured`. Claude session logs and `cq components session cost` do not measure this Codex run.

<!-- CODEX RUNTIME END -->


# quenching-git-commit-incremental — turn the current worktree into atomic commits

**Input**: `$ARGUMENTS` — an optional subject prefix; absent → use the target convention or the
fallback below.

Operate on the current checkout only. Read the shared git rules from
`../../references/git/conventions.md` and
`../../references/git/commit.md`; those references own convention precedence,
subject anchoring and commit hygiene. The report is in the repository's declared conversation
language, while commit subjects and messages remain canonical English artifacts.

## Workflow

### 1. Snapshot the worktree and guard the run

Read the target's git conventions, then collect one initial snapshot:

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
cq git conventions --json
git status --short
git diff --name-status
git diff --cached --name-status
git ls-files --others --exclude-standard
```

Treat tracked edits, staged edits, deletions and untracked files as the pending worktree. A clean
snapshot reports a no-op and ends. An unmerged status (`UU`, `AA`, `DD`, `AU`, `UA`, `DU` or `UD`),
or a file that cannot be read safely is a pre-staging refusal: report the paths and keep every
pending change in place. Read the content of each eligible file before staging, with a ceiling of
1 MiB per file and 10 MiB total. Scan content, not only filenames, for private-key headers and
credential assignments (`api[_-]?key`, `token`, `secret`, `password`, `client[_-]?secret`); on a
match report only the path and pattern, never the value. A size, unreadable-file or secret match is
also a refusal.

**Done when:** the initial path lists, convention layer and safety disposition are reported, with
no `git add` run before every guard passes and no bypass path available.

### 2. Read and classify every pending path

Read the complete current content of every eligible file with `Read`; for a deletion, read its
complete staged or unstaged diff instead. Use the status and diff together when a path has both
staged and unstaged content, because this command commits the path's complete current state.
The per-file and total-byte ceilings and content scan from step 1 still apply to the bytes read
here.
Classify each path by the single concern its change serves. Keep the classification in the current
run; no external plan or confirmation is needed.

**Done when:** every eligible path has a recorded classification, and no sensitive value appears in
the report.

### 3. Form atomic groups and resolve subjects

Create the smallest coherent groups by logical affinity. Put every eligible path in exactly one
group, keep unrelated concerns apart, and give each group one short imperative subject. Apply an
explicit `$ARGUMENTS` prefix first, then `gitConventions.commitSubject`, then the target's declared
git standard, and finally the fallback `chore: <short English imperative>` when no target rule
applies. The subject describes the group's concern, not its file list.

**Done when:** every group has a disjoint explicit path list and one resolved English subject.

### 4. Confirm, then stage and commit each group

Before the first `git add`, show the full group table, paths, diffs, subjects and the two byte/secret
guards' clean result. Put one decision sheet ([specs-develop/questions.md](../../references/specs-develop/questions.md) §1; A carry out, B decline) on whether to carry out the listed commits, and end the turn;
decline leaves every pending path untouched. Then, for each group in dependency order, quote each
path and stage only that list:

```bash
git add -- <path-1> <path-2>
git commit -m "<resolved subject>"
git log -1 --format="%H %s"
```

Execute the sequence immediately after its group is resolved. Hooks stay enabled. If staging fails
or a commit fails, stop the sequence at that group, leave earlier commits intact, preserve the remaining
worktree changes, and report the command output. Continue only on a later invocation after the
failure has been fixed.

**Done when:** each successful group has one new commit whose logged subject and paths match the
resolved group, or the first failure has stopped the run with its residue named.

### 5. Report the result and final state

List the initial disposition, every created commit with its subject and paths, the failed group if
any, and the final `git status --short`. Report a clean final tree only when the final status proves
it; report remaining changes and the stopping reason otherwise.

**Done when:** the report accounts for every initial path and the final status has been collected
after the last commit or refusal.

## Invariants

- Stage paths explicitly with `git add --`; the command never uses `git add -A`, `git add .`, or an
  equivalent broad selector.
- Keep hooks and signing enabled; never use `--no-verify` or `--no-gpg-sign`.
- Create new commits only; never amend, reset, rewrite history or force-push.
- Keep secrets and credential values out of both commit messages and the report.
