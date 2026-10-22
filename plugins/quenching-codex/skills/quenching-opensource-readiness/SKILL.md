---
name: quenching-opensource-readiness
description: "Assess whether a repository is ready to become public: secrets in tree and history, internal identifiers, attribution, license and consent evidence, read-only. Use for \"can we open this repo\", \"pre-publication readiness\", \"scan before making it public\". Not for: writing artifacts → quenching-opensource-align; the baseline level → quenching-opensource-status."
---

<!-- GENERATED FROM plugins/quenching/commands/opensource/readiness.md -->

<!-- CODEX RUNTIME START -->
## Codex runtime

Use Codex host sub-agents only. Never launch Claude CLI, request Claude models, or fall back to Claude during a Codex run. The Claude source may separately delegate development to Codex. Read each named agent protocol and pass its role, prohibitions, model and effort to the host's spawn-agent tool; protocol files are not automatically registered agent types. Use host messaging, completion notifications and interrupt tools for lifecycle management. If delegation is unavailable, report the limitation; do not silently replace required independent verification with self-review.

Tier mapping: opus → `gpt-6-astra`; sonnet → `gpt-6.1-sol`; haiku → `gpt-6-luna`. Preserve declared effort. Pass model explicitly; when the host requires a fresh context for model overrides, use that mode and include the necessary brief and protocol. Use gpt-6-luna for product code only on ONE task whose `cq specs estimate --task` reports `oracleProtected` and `smallTierEligible` (an executable `verify:` whose tests sit outside the task's `files:`, nothing under `/docs/`, projected context at or under 80k); a failed `verify:` returns it to the session model. Never use gpt-6-luna for judgment roles or for import-memory classification/executor roles. Report tokens per model and role only when host telemetry provides them; otherwise `not measured`. Claude session logs and `cq components session cost` do not measure this Codex run.

<!-- CODEX RUNTIME END -->


# quenching-opensource-readiness — assess a repository before it goes public

**Input**: `$ARGUMENTS` (an optional target repository root, and an optional `--evidence <path>`
to the owner's reviewed license and consent evidence; omit the root to use the current repository).

This command is the read-only pre-publication assessment of the open source front. It runs
**before** `quenching-opensource-align` when the owner wants to open a private
repository. It reports blockers, warnings and the coverage it could not measure; it never
publishes, never writes an artifact, never rewrites history and never changes visibility. The
evidence contract, the finding classes and the disposition of each are in
[opensource-readiness/report.md](../../references/opensource-readiness/report.md).

Resolve `cq` per
[tool-resolution.md](../../references/align/tool-resolution.md)
§Resolving the tool. Set `TARGET_ROOT` to the supplied root, or to `.` when omitted, and run:

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
cq --root "$TARGET_ROOT" opensource readiness --json [--evidence "<path>"]
```

Branch on the exit code: `0` is a complete measured assessment with no finding, `1` carries
measured findings, and `2` means at least one category was not measured or was refused — any
finding already measured is still in the payload. Exit `0` describes the assessed scope only; it is
never an approval to publish.

## Workflow

### 1. Read the readiness payload

Run the invocation above once. Preserve `scope`, `scanners`, `coverage`, `blockers`, `warnings`
and `truncated` as returned. Never re-run a scanner yourself, never print a file the payload names
and never open a commit it names: the payload is deliberately free of values, and reading the
location back is how a secret reaches the transcript.

**Done when:** the payload and its exit code are captured.

### 2. Report blockers, warnings and coverage separately

Report three tables, in this order, per
[opensource-readiness/report.md](../../references/opensource-readiness/report.md)
§The report:

| Table | Rows |
| --- | --- |
| Blockers | every `blockers[]` row — class, code, location, commit, owner remediation |
| Warnings | every `warnings[]` row — class, code, location, owner remediation |
| Coverage | one row per class — state, code, scanner; then the history scope (`refs`, `shallow`, `historyComplete`) and the `untracked`/`ignored` counts that were not scanned |

A class that is `not-measured`, `partial` or `refused` stays so in the report and is named as the
reason the assessment is incomplete; never round it to clean. A missing scanner is named with the
install the owner may choose, never installed here.

**Done when:** every class has a coverage row and every finding keeps its code and remediation.

### 3. Hand back control

State that this command wrote nothing and that remediation and publication are the owner's: the
`remediation` of each row is a route for the owner, never an action this command takes. After the
owner clears the blockers, name `quenching-opensource-align` for the community
artifacts and this command again to reassess.

**Done when:** the report states its read-only boundary, the observed exit code and that no
result is a publication approval.

## Invariants

- Read only: no target write, no fetch, no ref change, no scanner install, no remote credential
  verification.
- No secret value, snippet, scanner message, personal address or absolute path is ever echoed.
- An unmeasured category is never reported as clean, and no exit is an approval to publish.
