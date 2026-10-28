---
name: quenching-git-pr-review
description: "Fetch a PR's unresolved review threads and address each on the human's confirmation. Use for \"resolve PR comments\", \"address the review feedback\". Not for: opening a PR → quenching-git-pr-create."
---

<!-- GENERATED FROM plugins/quenching/commands/git/pr/review.md -->

<!-- CODEX RUNTIME START -->
## Codex runtime

Use Codex host sub-agents only. Never launch Claude CLI, request Claude models, or fall back to Claude during a Codex run. The Claude source may separately delegate development to Codex. Read each named agent protocol and pass its role, prohibitions, model and effort to the host's spawn-agent tool; protocol files are not automatically registered agent types. Use host messaging, completion notifications and interrupt tools for lifecycle management. If delegation is unavailable, report the limitation; do not silently replace required independent verification with self-review.

Tier mapping: opus → `gpt-6-astra`; sonnet → `gpt-6.1-sol`; haiku → `gpt-6-luna`. Preserve declared effort. Pass model explicitly; when the host requires a fresh context for model overrides, use that mode and include the necessary brief and protocol. Use gpt-6-luna for product code only on ONE task whose `cq specs estimate --task` reports `oracleProtected` and `smallTierEligible` (an executable `verify:` whose tests sit outside the task's `files:`, nothing under `/docs/`, projected context at or under 80k); a failed `verify:` returns it to the session model. Never use gpt-6-luna for judgment roles or for import-memory classification/executor roles. Report tokens per model and role only when host telemetry provides them; otherwise `not measured`. Claude session logs and `cq components session cost` do not measure this Codex run.

<!-- CODEX RUNTIME END -->


# quenching-git-pr-review — work through a PR's unresolved threads

**Input**: `$ARGUMENTS` — a provider PR number/id. Omitted → the active PR open for the current
branch.

Reads **unresolved review threads** specifically — not every comment, and not ones already marked
resolved.

## Workflow

### 1. Resolve the provider, PR and repository
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
# Read `backend` from this result before choosing a host CLI.
cq specs config --json
git remote get-url origin
# github
gh repo view --json owner,name -q '.owner.login + " " + .name'
gh pr view <$ARGUMENTS, or the current branch's PR> --json number -q .number
# azure-boards
az repos pr list --status all --top 1 --detect true --output json
az repos pr show --id <id> --detect true --output json
az repos pr list --source-branch "$(git branch --show-current)" --status active \
  --detect true --output json
```
Run only the probe for the configured provider, after confirming the origin host matches it. On
Azure, an explicit argument goes to `show`; with no argument, `list` is filtered to the current
branch. No PR resolves for the current branch and none was given → say so and stop. More than one
active Azure PR → show the ids and ask which one to work. **Done when:** the provider, repository
and PR number/id are known.

### 2. Fetch every unresolved thread
```bash
gh api graphql -f query='
  query($owner:String!,$repo:String!,$n:Int!,$after:String){
    repository(owner:$owner,name:$repo){
      pullRequest(number:$n){
        reviewThreads(first:100, after:$after){
          pageInfo{hasNextPage endCursor}
          nodes{ id isResolved path line
            comments(first:10){ pageInfo{hasNextPage endCursor} nodes{ body author{login} } } } } } }' \
  -F owner=<owner> -F repo=<repo> -F n=<number> -F after=null
# azure-boards — use the repository/project ids from `az repos pr show`.
az devops invoke --area git --resource pullRequestThreads \
  --route-parameters project=<project-id> repositoryId=<repository-id> pullRequestId=<pr-id> \
  --api-version 7.1 --output json
```
For GitHub filter to `isResolved: false`; if `hasNextPage` is true, paginate until it is false, and
report any truncated comment connection (`comments(first:10)`) rather than calling it complete. For Azure filter to non-terminal thread `status` values
(normally `active`/`pending`; omit `fixed`, `closed`, `wontFix` and `byDesign`). None → report the
PR is clear and stop. Preserve each thread's id, file/line context and comment chain. **Done
when:** the list of unresolved threads is in hand.
**Done when:** every provider page was fetched or its pagination/truncation is reported.

### 3. Work each thread, on its own confirmation
For each unresolved thread, in the order returned: show the file, line, and comment chain, propose
a fix (or ask what the human wants instead), and apply it only on a yes. **Done when:** every
thread has either been fixed and staged, or explicitly skipped with a stated reason.

### 4. Commit and resolve
Once at least one thread's fix is staged, invoke `quenching-git-commit` to commit it (the command
must be available; otherwise stop before resolving anything). Then, per
thread actually fixed:
```bash
gh api graphql -f query='mutation($id:ID!){resolveReviewThread(input:{threadId:$id}){thread{isResolved}}}' -F id=<thread id>
# azure-boards — `repository.url` comes from the PR JSON returned in step 1.
az rest --method patch \
  --url "<repository.url>/pullRequests/<pr-id>/threads/<thread-id>?api-version=7.1" \
  --body '{"status":"fixed"}' --output json
```
A thread that was skipped stays unresolved. Verify GitHub's `isResolved: true` or Azure's `status: fixed` after the update.
**Done when:** every fixed thread reads back resolved/fixed, and every skipped one is named in the
report as still open.
**Done when:** every fixed thread is verified resolved, and every skipped thread remains named.

### 5. Report
State how many threads were unresolved at the start, how many were fixed and resolved, how many
were skipped and why, and the commit(s) that carried the fixes. **Done when:** all four are named.

## Invariants

- Never resolve a thread that was skipped rather than fixed.
- Never batch-apply every thread's fix before any confirmation — one thread, one yes.
- Never invent a fix for a thread whose ask is unclear — ask the human instead.
- Never route an Azure PR through GitHub GraphQL, or a GitHub PR through Azure REST.
