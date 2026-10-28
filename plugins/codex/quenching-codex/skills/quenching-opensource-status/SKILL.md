---
name: quenching-opensource-status
description: "Report the open source front: every owner's catalog answers and the baseline level, read-only. Use for \"opensource status\", \"which baseline level do we reach\". Not for: writing artifacts → quenching-opensource-align."
---

<!-- GENERATED FROM plugins/quenching/commands/opensource/status.md -->

<!-- CODEX RUNTIME START -->
## Codex runtime

Use Codex host sub-agents only. Never launch Claude CLI, request Claude models, or fall back to Claude during a Codex run. The Claude source may separately delegate development to Codex. Read each named agent protocol and pass its role, prohibitions, model and effort to the host's spawn-agent tool; protocol files are not automatically registered agent types. Use host messaging, completion notifications and interrupt tools for lifecycle management. If delegation is unavailable, report the limitation; do not silently replace required independent verification with self-review.

Tier mapping: opus → `gpt-6-astra`; sonnet → `gpt-6.1-sol`; haiku → `gpt-6-luna`. Preserve declared effort. Pass model explicitly; when the host requires a fresh context for model overrides, use that mode and include the necessary brief and protocol. Use gpt-6-luna for product code only on ONE task whose `cq specs estimate --task` reports `oracleProtected` and `smallTierEligible` (an executable `verify:` whose tests sit outside the task's `files:`, nothing under `/docs/`, projected context at or under 80k); a failed `verify:` returns it to the session model. Never use gpt-6-luna for judgment roles or for import-memory classification/executor roles. Report tokens per model and role only when host telemetry provides them; otherwise `not measured`. Claude session logs and `cq components session cost` do not measure this Codex run.

<!-- CODEX RUNTIME END -->


# quenching-opensource-status — read the open source front

**Input**: `$ARGUMENTS` (an optional target repository root; omit to use the current repository).

This command is the read-only view of the open source front. The common front contract is in
[front-align/mold.md](../../references/front-align/mold.md), the catalog
contract is in
[opensource-controls/catalog.md](../../references/opensource-controls/catalog.md),
and the finding-to-owner map is in
[opensource-align/bands.md](../../references/opensource-align/bands.md).
It aggregates what each owning front already answers; it never probes another owner's control and
never writes an artifact.

Resolve `cq` per
[tool-resolution.md](../../references/align/tool-resolution.md)
§Resolving the tool. Set `TARGET_ROOT` to the supplied argument, or to `.` when omitted, and run:

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
cq --root "$TARGET_ROOT" opensource status --json
```

Branch on the JSON and exit code: `0` is a clean report, `1` carries findings, and `2` is a
refusal. On exit `2`, preserve the refusal exactly; never guess a root, license, maintainer or
owner. On `0` or `1`, use the returned payload as the complete read model and do not invoke a
write-capable command.

## Workflow

### 1. Read the status payload

Re-read the status payload using the `cq opensource status --json` invocation above. Branch on its
exit code and preserve its baseline, owner blocks, findings and advisories.

**Done when:** the payload is captured, or the refusal is preserved with its reason.

### 2. Classify and report the front

Report one compact table:

| Band | Evidence |
| --- | --- |
| Baseline | `baseline.version`, the attained `level`, and per level its `met`/`unmet`/`unknown` state with the `blocking` requirement ids |
| Owners | one row per `owners[]` block — owner, `summary`, and the `command` that closes its residue |
| Opensource controls | each control of the `opensource` block, its requirement ids with `present`, `missing`, `not-measured`, `refused` or `retired`, and the evidence paths |
| Artifacts | each `artifacts[]` row — artifact, target path, present or absent |
| Findings | every `os-*` finding with its control, requirements and severity |
| Advisories | every optional or artifact-only `os-*` code; advisories never change `ok` or the exit code |

`present` is candidate evidence, never conformance: keep `humanRequired` as returned. A level that
is `unknown` stays unknown — a requirement only a provider answers is `not-measured`, never met.
A requirement of another owner appears in its owner row with that owner's command, never as an
`os-*` finding. Preserve every code, path and message returned by the route.

**Done when:** every returned field has an evidence row, every finding keeps its code and
disposition, and an unmeasured requirement remains unmeasured.

### 3. Hand back control

State that this command wrote nothing. For an `os-*` finding or advisory, name
`quenching-opensource-align` as the closing command. For another owner's residue, name
the `command` its owner block returned; status never runs it.

**Done when:** the report states its read-only boundary and observed exit code.

## Invariants

- Read only: no artifact written, no license, maintainer, contact or funding chosen.
- The aggregate never re-measures another owner's control; it reports that owner's own answer.
- The baseline level is the route's; it is never rounded up past an `unknown` level.
- Findings retain their stable `os-*` code, severity, evidence and disposition band.
