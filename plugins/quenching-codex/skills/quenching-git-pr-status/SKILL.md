---
name: quenching-git-pr-status
description: "Read a PR's checks, reviews, threads and mergeability, read-only. Use for \"check the PR status\", \"show the review state\". Not for: opening → quenching-git-pr-create; threads → quenching-git-pr-review; merging → quenching-git-merge."
---

<!-- GENERATED FROM plugins/quenching/commands/git/pr/status.md -->

<!-- CODEX RUNTIME START -->
## Codex runtime

Use Codex host sub-agents only. Never launch Claude CLI, request Claude models, or fall back to Claude during a Codex run. The Claude source may separately delegate development to Codex. Read each named agent protocol and pass its role, prohibitions, model and effort to the host's spawn-agent tool; protocol files are not automatically registered agent types. Use host messaging, completion notifications and interrupt tools for lifecycle management. If delegation is unavailable, report the limitation; do not silently replace required independent verification with self-review.

Tier mapping: opus → `gpt-6-astra`; sonnet → `gpt-6.1-sol`; haiku → `gpt-6-luna`. Preserve declared effort. Pass model explicitly; when the host requires a fresh context for model overrides, use that mode and include the necessary brief and protocol. Use gpt-6-luna for product code only on ONE task whose `cq specs estimate --task` reports `oracleProtected` and `smallTierEligible` (an executable `verify:` whose tests sit outside the task's `files:`, nothing under `/docs/`, projected context at or under 80k); a failed `verify:` returns it to the session model. Never use gpt-6-luna for judgment roles or for import-memory classification/executor roles. Report tokens per model and role only when host telemetry provides them; otherwise `not measured`. Claude session logs and `cq components session cost` do not measure this Codex run.

<!-- CODEX RUNTIME END -->


# quenching-git-pr-status — read one pull request snapshot

**Input**: `$ARGUMENTS` — `spec:<id>`, a provider PR number or URL, or omitted for the current
branch's PR.

Read the provider and field contract in
`../../references/git/pr.md`; it owns the query shapes, unknown-state
rules and recommendation vocabulary used below.

## Workflow

### 1. Resolve the provider and selector

Read the specs backend, the `origin` URL and the current branch. A `spec:<id>` selector reads the
spec status and its recorded PR; a provider URL or number selects that PR; an omitted selector
uses the PR for the current branch. Confirm the host matches the configured provider before using
`gh` or `az`. **Done when:** the provider route and one selector are known, or a refusal names the
missing, ambiguous, mismatched or unauthenticated route.

For the initial facts, use the bundled `cq` route and the local git identity:

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
cq specs config --json
git remote get-url origin
git branch --show-current
```

For `spec:<id>`, also read `cq specs status --spec <id> --json` and use only its recorded PR
number or URL. Do not substitute an issue number for a PR number. **Done when:** the provider
route and one selector are known, or a refusal names the missing, ambiguous, mismatched or
unauthenticated route.

### 2. Collect the provider snapshot

Read the GitHub or Azure section of the bundled reference and run only that provider's read-only
queries. Fetch PR identity, source/base, state, checks, reviewers, approvals, mergeability and
review threads. Follow pagination and record truncation. **Done when:** the provider response is
complete, or its not-found, authentication, permission or unknown cause is preserved.

### 3. Normalize the evidence

Build one report with `provider`, `pullRequest`, `source`, `base`, `checks`, `approvals`,
`unresolvedThreads`, `mergeability`, `spec` and `nextStep`. Keep provider-specific fields under
their provider section. Represent unavailable evidence as `unknown` plus its cause; do not infer
approval, green checks, clear threads or mergeability. **Done when:** every common field is present
with a fact or an explained unknown.

Within `pullRequest`, normalize the identity as `id`, `webUrl` and `apiUrl`. Render `webUrl` with
the label **Link para revisão** and `apiUrl` with **API URL**. The first is the browser address a
human opens; the second is the technical endpoint. A value containing `/_apis/` is never rendered
as Link para revisão; if no safe browser link can be derived, report it as `unknown` with its cause.

### 4. Choose the textual next step

Apply the reference's recommendation rules to the normalized facts. Point to
`quenching-git-pr-review`, `quenching-git-sync`, `quenching-git-merge` or no action as the facts
warrant; recommendations are prose only. **Done when:** one next step is stated with the fact that
caused it, or the refusal is the next step.

### 5. Self-check and report

Confirm that the output names the provider, PR id/URL, source, base, checks, approvals, unresolved
threads, mergeability, spec link and recommendation, and that no write-capable command was run.
Report pagination, unknown causes and provider errors alongside the snapshot. **Done when:** the
read-only snapshot is returned and its evidence boundaries are explicit.

## Invariants

- Use only the provider selected by `cq specs config --json` and the matching `origin` host.
- Keep the normalized **Link para revisão** and **API URL** labels distinct; never expose an
  Azure `/_apis/` endpoint as the human review link.
- Preserve not-found, authentication, permission and unknown states; none is a green result.
- Never push, create, edit, close, merge or resolve anything during this status read.
