---
name: quenching-delivery-status
description: "Report the delivery front (workflow inventory, pipeline findings), read-only. Use for \"delivery status\", \"check the delivery surface\". Not for: converging → quenching-delivery-align."
---

<!-- GENERATED FROM plugins/quenching/commands/delivery/status.md -->

<!-- CODEX RUNTIME START -->
## Codex runtime

Use Codex host sub-agents only. Never launch Claude CLI, request Claude models, or fall back to Claude during a Codex run. The Claude source may separately delegate development to Codex. Read each named agent protocol and pass its role, prohibitions, model and effort to the host's spawn-agent tool; protocol files are not automatically registered agent types. Use host messaging, completion notifications and interrupt tools for lifecycle management. If delegation is unavailable, report the limitation; do not silently replace required independent verification with self-review.

Tier mapping: opus → `gpt-6-astra`; sonnet → `gpt-6.1-sol`; haiku → `gpt-6-luna`. Preserve declared effort. Pass model explicitly; when the host requires a fresh context for model overrides, use that mode and include the necessary brief and protocol. Use gpt-6-luna for product code only on ONE task whose `cq specs estimate --task` reports `oracleProtected` and `smallTierEligible` (an executable `verify:` whose tests sit outside the task's `files:`, nothing under `/docs/`, projected context at or under 80k); a failed `verify:` returns it to the session model. Never use gpt-6-luna for judgment roles or for import-memory classification/executor roles. Report tokens per model and role only when host telemetry provides them; otherwise `not measured`. Claude session logs and `cq components session cost` do not measure this Codex run.

<!-- CODEX RUNTIME END -->


# quenching-delivery-status — read the delivery front

This command is the read-only view of a target repository's delivery surface. It reports the
applicability signal, provider-equivalent workflow artifacts, triggers, jobs, stages, setup and
runtime evidence, release reachability and findings. It never edits a workflow, selects a
provider or invokes a deployment.

The delivery finding map is in
[delivery-align/bands.md](../../references/delivery-align/bands.md); the common
front floor is in [front-align/mold.md](../../references/front-align/mold.md).
Resolve `cq` per
[tool-resolution.md](../../references/align/tool-resolution.md)
§Resolving the tool. Set `TARGET_ROOT` to `$ARGUMENTS`, or `.` when omitted, and run:

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
cq --root "$TARGET_ROOT" delivery status --json
```

Branch on the JSON and exit code: `0` is clean, `1` carries findings, and `2` is a refusal. On
exit `2`, preserve the refusal and the affected configuration exactly; do not guess a provider or
workflow tree. On exit `0` or `1`, use the returned payload as the complete read model and do not
invoke a write-capable command.

## Workflow

### 1. Read the status payload

Re-read the status payload using the `cq delivery status --json` invocation above. Branch on its
exit code and preserve its applicability, refusal or findings.

**Done when:** the payload is captured, or the refusal is preserved with its reason.

### 2. Classify and report the front

Report one compact table:

| Band | Evidence |
| --- | --- |
| Applicability | target root, applicable/not-applicable state, signal, provider and artifacts |
| Workflow | path, provider, kind, parse state, triggers, jobs, stages and job provenance |
| Structural | `delivery-trigger-unreachable`, `delivery-stage-unreachable`, `delivery-checkout-missing`, `delivery-setup-missing`, `delivery-runtime-drift`, `delivery-release-unreachable` |
| Judgement | `delivery-provider-policy`, `delivery-environment-policy`, `delivery-publish-scope`, `delivery-permission-policy` |
| Counts | errors, warnings and overall `ok` state |
| Catalog controls | the `controls` block — each catalog control id, its requirement ids with `present`, `missing`, `not-measured`, `refused` or `retired`, and the evidence paths. `present` is candidate evidence, never conformance; the block never changes `ok` or the exit code |

Preserve every finding's code, band, severity, message and path. Distinguish no delivery signal
(`not-applicable`) from an applicable provider whose workflow shape was not measured. For an
actionable mechanical or structural finding, name `quenching-delivery-align`; for a judgement
finding, retain the evidence and name the target owner's closing decision from `delivery-align/bands.md`.

**Done when:** every returned field has an evidence row, every finding keeps its code and band,
and no missing state is presented as healthy.

### 3. Hand back control

State that this command wrote nothing and that it did not run a workflow, test suite, release or
deployment.

**Done when:** the report states its read-only boundary and observed exit code.

## Invariants

- Read only: no workflow, configuration, permission, environment or release edit.
- Findings retain the delivery route's stable code, band, severity and evidence.
- Provider and target policy are never inferred from a workflow's mere presence.
- A missing or unsupported workflow shape remains explicit and is never reported as conformant.
