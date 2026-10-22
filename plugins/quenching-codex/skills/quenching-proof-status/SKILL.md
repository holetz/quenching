---
name: quenching-proof-status
description: "Report the proof front: layers, fixtures, floors, CI evidence and findings, read-only. Use for \"proof status\", \"check the verification surface\". Not for: converging → quenching-proof-align."
---

<!-- GENERATED FROM plugins/quenching/commands/proof/status.md -->

<!-- CODEX RUNTIME START -->
## Codex runtime

Use Codex host sub-agents only. Never launch Claude CLI, request Claude models, or fall back to Claude during a Codex run. The Claude source may separately delegate development to Codex. Read each named agent protocol and pass its role, prohibitions, model and effort to the host's spawn-agent tool; protocol files are not automatically registered agent types. Use host messaging, completion notifications and interrupt tools for lifecycle management. If delegation is unavailable, report the limitation; do not silently replace required independent verification with self-review.

Tier mapping: opus → `gpt-6-astra`; sonnet → `gpt-6.1-sol`; haiku → `gpt-6-luna`. Preserve declared effort. Pass model explicitly; when the host requires a fresh context for model overrides, use that mode and include the necessary brief and protocol. Use gpt-6-luna for product code only on ONE task whose `cq specs estimate --task` reports `oracleProtected` and `smallTierEligible` (an executable `verify:` whose tests sit outside the task's `files:`, nothing under `/docs/`, projected context at or under 80k); a failed `verify:` returns it to the session model. Never use gpt-6-luna for judgment roles or for import-memory classification/executor roles. Report tokens per model and role only when host telemetry provides them; otherwise `not measured`. Claude session logs and `cq components session cost` do not measure this Codex run.

<!-- CODEX RUNTIME END -->


# quenching-proof-status — read the verification surface

**Input**: `$ARGUMENTS` (an optional target repository root; omit to use the current repository).

The common front contract is in
[front-align/mold.md](../../references/front-align/mold.md), and the proof
disposition map is in
[proof-align/bands.md](../../references/proof-align/bands.md). This
read-only view preserves proof's layer, fixture, measurement, floor, CI and order deltas.

This command is the read-only view of the proof front. It reports the declared proof root, layers
with reach, budgets and test counts, fixture-library health, measured roots and floors, CI
definitions and invocation evidence, and findings grouped by the disposition bands. It reports an
absent floor or artifact as absent, never as healthy, and states plainly that the target suite was
not run.

The payload is produced by `cq proof status`; the finding and disposition rules live in
[proof-align/bands.md](../../references/proof-align/bands.md),
[proof-align/gate-contract.md](../../references/proof-align/gate-contract.md),
and [proof-align/layer-contract.md](../../references/proof-align/layer-contract.md).
Resolve `cq` per
[tool-resolution.md](../../references/align/tool-resolution.md) and branch
on exit code and JSON: `0` is a clean report, `1` carries findings, and `2` is a refusal.

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
cq --root "$TARGET_ROOT" proof status --json
```

On exit `2`, report the refusal and every missing or invalid declaration exactly as returned. Do
not guess a proof root, layer, floor, coverage result, CI provider, or operations applicability.
On exit `0` or `1`, use the payload as the complete read model and do not invoke a write-capable
subcommand.

**Done when:** the status payload is captured, or a refusal has been reported, and nothing has
been written.

### 2. Classify and report the front

Report one compact table:

| Band | Evidence |
| --- | --- |
| Configuration | target root, declared proof root, layer declarations and any refusal state |
| Layers | every declared layer's reach, budget, required state and collected test count; empty means empty, not healthy |
| Fixtures | fixture-library count and health, loose copies, and conftest ownership |
| Measurement | measured roots, their floor and last achieved value when the payload has one; absent or stale artifacts remain explicit |
| CI and order | each discovered provider and invocation, whether it runs the gate, and whether order is randomized |
| Mechanical | `pf-unmarked` and any future generated-proof finding, reported by code |
| Structural | `pf-stop-first`, `pf-loose-fixture`, `pf-fat-conftest`, `pf-no-floor`, and applicable `pf-order-unproven` findings |
| Judgement | `pf-unlayered`, `pf-empty-layer`, `pf-unmeasured-surface`, `pf-no-ci`, `pf-untested-entrypoint`, and non-structural order findings |
| Catalog controls | the `controls` block — each catalog control id, its requirement ids with `present`, `missing`, `not-measured`, `refused` or `retired`, and the evidence paths. `present` is candidate evidence, never conformance; the block never changes `ok` or the exit code |

Preserve each finding code, path, severity, evidence and disposition. If no layers are declared,
say so and report the unlayered modules without inferring a taxonomy. If `ops` is absent, include
the explicit not-applicable note for `pf-untested-entrypoint`; if the suite was not run, say that
in the report even when the static surface is conformant. A floor or last-achieved value is only
reported when the payload or an existing artifact supplies it; status never runs the suite to
produce one.

**Done when:** every returned field has an authoritative row or an explicit missing state, every
finding keeps its code and band, and the report distinguishes static evidence from run evidence.

### 3. Hand back control

State that this command wrote nothing and that the suite was not run. For a structural finding,
name `quenching-proof-align` as the command that can converge it. For a judgement finding,
retain its evidence and name the target owner's closing command from `bands.md`; status never
runs that command. For a missing layer, name `quenching-proof-layer-new`; for a missing CI gate,
name the target owner's reviewed CI change.

**Done when:** the report ends with the appropriate owner for each finding and no repair or test
execution has been attempted.

## Invariants

- Read only: no layer, fixture, gate, measured-root, floor, CI, or operations declaration is
  created or changed.
- An absent floor, artifact, layer, CI definition, or optional operations front remains explicit;
  nothing is called healthy because it is missing.
- Findings come from `bands.md` and retain their severity and code.
- The target suite is never run; status reports this explicitly.
- Status names `quenching-proof-align` for bounded repair and `quenching-proof-layer-new` for
  layer creation, without invoking either.
