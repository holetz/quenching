---
name: quenching-ops-status
description: "Report the operations front: root, router, entry points, lifecycle and findings, read-only. Use for \"ops status\", \"report operations drift\". Not for: converging → quenching-ops-align."
---

<!-- GENERATED FROM plugins/quenching/commands/ops/status.md -->

<!-- CODEX RUNTIME START -->
## Codex runtime

Use Codex host sub-agents only. Never launch Claude CLI, request Claude models, or fall back to Claude during a Codex run. The Claude source may separately delegate development to Codex. Read each named agent protocol and pass its role, prohibitions, model and effort to the host's spawn-agent tool; protocol files are not automatically registered agent types. Use host messaging, completion notifications and interrupt tools for lifecycle management. If delegation is unavailable, report the limitation; do not silently replace required independent verification with self-review.

Tier mapping: opus → `gpt-6-astra`; sonnet → `gpt-6.1-sol`; haiku → `gpt-6-luna`. Preserve declared effort. Pass model explicitly; when the host requires a fresh context for model overrides, use that mode and include the necessary brief and protocol. Use gpt-6-luna for product code only on ONE task whose `cq specs estimate --task` reports `oracleProtected` and `smallTierEligible` (an executable `verify:` whose tests sit outside the task's `files:`, nothing under `/docs/`, projected context at or under 80k); a failed `verify:` returns it to the session model. Never use gpt-6-luna for judgment roles or for import-memory classification/executor roles. Report tokens per model and role only when host telemetry provides them; otherwise `not measured`. Claude session logs and `cq components session cost` do not measure this Codex run.

<!-- CODEX RUNTIME END -->


# quenching-ops-status — read the operations front

**Input**: `$ARGUMENTS` (an optional target repository root; omit to use the current repository).

The common front contract is in
[front-align/mold.md](../../references/front-align/mold.md), and the ops
disposition map is in
[ops-align/bands.md](../../references/ops-align/bands.md). This read-only
view preserves the router, registry and entry-point deltas owned by the ops front.

This command is the read-only view of the operations front. It reports the configuration, router,
entry points by package, lifecycle states, findings by code and disposition band, and registry
freshness. It never repairs a finding, writes a registry, or turns an absent optional artifact into
a healthy one.

The payload and target tree are defined by
[ops-align/target-structure.md](../../references/ops-align/target-structure.md),
[ops-align/lifecycle.md](../../references/ops-align/lifecycle.md), and
[ops-align/bands.md](../../references/ops-align/bands.md). Resolve `cq` per
[tool-resolution.md](../../references/align/tool-resolution.md)
§Resolving the tool. Use the resolved path literally and branch on exit code and JSON:
`0` is a clean report, `1` carries findings, and `2` is a refusal.

## Workflow

### 1. Read the status payload

Set `TARGET_ROOT` to the supplied argument, or to `.` when the argument is omitted, and run:

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
cq --root "$TARGET_ROOT" ops status --json
```

On exit `2`, report the refusal and every missing configuration key exactly as returned. Do not
guess an operations root, router, registry, or optional file. On exit `0` or `1`, use the payload
as the complete read model; do not invoke a write-capable subcommand.

**Done when:** the status payload is captured, or a configuration refusal has been reported, and
nothing has been written.

### 2. Classify and report the front

Report one compact table:

| Band | Evidence |
| --- | --- |
| Configuration | declared operations root, configuration refusal state, and target root |
| Router | declared path, kind, existence, and `health`; missing is missing, never healthy |
| Surface | scanned count and entry points grouped by package |
| Lifecycle | active, archived, and undeclared counts |
| Mechanical | `op-undocumented` and `op-registry-stale` counts, with registry freshness state |
| Structural | `op-adhoc-root`, `op-untyped-exit`, and `op-no-router` counts |
| Judgement | `op-unarmed-write`, `op-disabled-check`, `op-orphan`, and `op-registry-malformed` counts, reported only |

Map findings to their bands through `bands.md`, preserve every finding code, and distinguish
errors from warnings using the payload's `errors` and `warnings`. A missing or stale registry is
reported with its emitted code; never create it or call it healthy because no rows were found.

**Done when:** every returned field has an authoritative row or an explicit missing/refused state,
and every finding keeps its code and disposition.

### 3. Hand back control

State that this command wrote nothing. For an actionable mechanical or structural finding, name
`quenching-ops-align` as the command that can converge it. For a judgement finding, retain its
evidence and name the target owner's closing command from `bands.md`; status never runs it.

**Done when:** the report ends with the appropriate owner for each finding and no repair has been
attempted.

## Invariants

- Read only: no registry generation, entry-point edit, router selection, or lifecycle move.
- A configuration refusal, missing router, and missing registry remain explicit states.
- Finding codes and their three disposition bands come from `bands.md`; none are invented or
  softened.
- The report distinguishes errors, warnings, and clean capability notes.
