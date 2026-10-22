---
name: quenching-security-status
description: "Report workflow permissions, secret and ignore coverage, advisory dependency config and access ownership, read-only. Use for \"security status\", \"security audit\". Not for: changing policy."
---

<!-- GENERATED FROM plugins/quenching/commands/security/status.md -->

<!-- CODEX RUNTIME START -->
## Codex runtime

Use Codex host sub-agents only. Never launch Claude CLI, request Claude models, or fall back to Claude during a Codex run. The Claude source may separately delegate development to Codex. Read each named agent protocol and pass its role, prohibitions, model and effort to the host's spawn-agent tool; protocol files are not automatically registered agent types. Use host messaging, completion notifications and interrupt tools for lifecycle management. If delegation is unavailable, report the limitation; do not silently replace required independent verification with self-review.

Tier mapping: opus → `gpt-6-astra`; sonnet → `gpt-6.1-sol`; haiku → `gpt-6-luna`. Preserve declared effort. Pass model explicitly; when the host requires a fresh context for model overrides, use that mode and include the necessary brief and protocol. Use gpt-6-luna for product code only on ONE task whose `cq specs estimate --task` reports `oracleProtected` and `smallTierEligible` (an executable `verify:` whose tests sit outside the task's `files:`, nothing under `/docs/`, projected context at or under 80k); a failed `verify:` returns it to the session model. Never use gpt-6-luna for judgment roles or for import-memory classification/executor roles. Report tokens per model and role only when host telemetry provides them; otherwise `not measured`. Claude session logs and `cq components session cost` do not measure this Codex run.

<!-- CODEX RUNTIME END -->


# quenching-security-status — read the security pillar

**Input**: `$ARGUMENTS` (an optional target repository root; omit to use the current repository).

This command is the read-only status/audit view of the security pillar. It reports live evidence
without owning a security tree, selecting a target policy or repairing a finding. Resolve `cq` per
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
cq --root "$TARGET_ROOT" security --json
```

Branch on the JSON and exit code: `0` is a measured report, `1` carries reported observations, and
`2` is a refusal. On exit `2`, preserve the refusal and affected path exactly; never guess a root,
provider policy or missing security declaration. On exit `0` or `1`, use the returned payload as the
complete read model and do not invoke a write-capable command.

## Workflow

### 1. Read the status payload

Re-read the payload using the `cq security --json` invocation above. Branch on its exit code and
preserve its measured, refused or not-measured state.

**Done when:** the payload is captured, or the refusal is preserved with its reason.

### 2. Report the questions

Report one compact table:

| Question | State | Evidence |
| --- | --- | --- |
| `workflow-permissions` | `present`/`missing`/`refused` | workflow paths and workflow/job declaration counts |
| `secret-ignore-coverage` | `present`/`missing`/`refused` | ignore path and recognized secret classes, never secret values |
| `advisory-dependency-configuration` | `present`/`missing`/`refused` | recognized advisory configuration paths |
| `access-ownership` | `present`/`missing` | recognized ownership declaration paths, never owner values |

Then report the payload's `controls` block — each catalog control id, its requirement ids with `present`, `missing`, `not-measured`, `refused` or `retired`, and the evidence paths. `present` is candidate evidence, never conformance; the block never changes `ok` or the exit code.

Preserve every question key, state, evidence path and detail returned by the route. Distinguish a
missing declaration from a source that was not measurable or was refused. Preserve the payload's
`readOnly` and `writePolicy` values: the pillar read workflow permissions, ignore patterns,
advisory configuration and ownership declarations only; it did not expose secret or owner values.

**Done when:** every returned question has a state and evidence row, and no secret or owner value
has entered the report.

### 3. Hand back control

State that this command wrote nothing and did not change workflows, ignore rules, dependencies,
configuration, access policy or generated files. Security has no align, doctor, bands file or
conductor row; status names no repair command because the target owner decides any action.

**Done when:** the report states its read-only boundary and observed exit code.

## Invariants

- Read only: no permission, secret, dependency, configuration or access-policy edit.
- The payload's `present`, `missing`, `not-measured` and `refused` states remain distinct.
- The pillar reports evidence and ownership boundaries; it never chooses or applies target policy.
- No secret or access-owner value is copied into the report.
