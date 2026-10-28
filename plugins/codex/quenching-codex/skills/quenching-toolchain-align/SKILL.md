---
name: quenching-toolchain-align
description: "Converge a repository's toolchain surface from manifests, locks, language pins and tool config, preserving build policy. Use for \"align the toolchain front\", \"fix toolchain drift\". Not for: read-only → quenching-toolchain-status."
---

<!-- GENERATED FROM plugins/quenching/commands/toolchain/align.md -->

<!-- CODEX RUNTIME START -->
## Codex runtime

Use Codex host sub-agents only. Never launch Claude CLI, request Claude models, or fall back to Claude during a Codex run. The Claude source may separately delegate development to Codex. Read each named agent protocol and pass its role, prohibitions, model and effort to the host's spawn-agent tool; protocol files are not automatically registered agent types. Use host messaging, completion notifications and interrupt tools for lifecycle management. If delegation is unavailable, report the limitation; do not silently replace required independent verification with self-review.

Tier mapping: opus → `gpt-6-astra`; sonnet → `gpt-6.1-sol`; haiku → `gpt-6-luna`. Preserve declared effort. Pass model explicitly; when the host requires a fresh context for model overrides, use that mode and include the necessary brief and protocol. Use gpt-6-luna for product code only on ONE task whose `cq specs estimate --task` reports `oracleProtected` and `smallTierEligible` (an executable `verify:` whose tests sit outside the task's `files:`, nothing under `/docs/`, projected context at or under 80k); a failed `verify:` returns it to the session model. Never use gpt-6-luna for judgment roles or for import-memory classification/executor roles. Report tokens per model and role only when host telemetry provides them; otherwise `not measured`. Claude session logs and `cq components session cost` do not measure this Codex run.

<!-- CODEX RUNTIME END -->


# quenching-toolchain-align — converge the toolchain front

**Input**: `$ARGUMENTS` (an optional target repository root; omit to use the current repository).

This command owns the toolchain front's convergence pass. It reads manifests, locks, language pins
and tool configuration, applies only deterministic or contract-bounded repairs, and leaves build
policy with the target owner. The common front floor is in
[front-align/mold.md](../../references/front-align/mold.md), and the
toolchain finding bands and closure boundary are in
[toolchain-align/bands.md](../../references/toolchain-align/bands.md).

Set `TARGET_ROOT` to the supplied argument, or to `.` when the argument is omitted. Resolve `cq`
per [tool-resolution.md](../../references/align/tool-resolution.md)
§Resolving the tool, pass the same root to every call, and branch on the JSON and exit code:
`0` is a clean answer, `1` carries findings, and `2` is a refusal.

## Workflow

### 1. Probe applicability before interpreting artifacts

Run the route before reading or editing a target:

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
cq --root "$TARGET_ROOT" toolchain doctor --json
```

The probe establishes applicability from recognized toolchain artifacts. `not-applicable` is an
explicit capability state, not drift; report it and stop. An applicable result with no findings is
conformant; report it and stop. On exit `2`, report the refusal exactly and do not invent a
manifest, lock, language version, tool pin or configuration namespace.

**Done when:** applicability and the first finding payload are fixed, or a clean/not-applicable
result has stopped the pass without an inventory read or a write.

### 2. Read the one inventory and its contracts

Only after exit `1`, use the `inventory`, `manifests`, `locks`, `languagePins` and
`toolConfigurations` rows already returned by the doctor payload. Do not walk the target again or
launch a package manager. Read the front contract and the bands reference before classifying a
row; `.claude/quenching.json` remains configuration, never a toolchain artifact.

**Done when:** the applicable artifacts, parsed declarations, configuration blocks and findings are
in hand from one read model.

### 3. Classify every finding by disposition

Keep severity separate from who may close the finding:

| Band | Finding codes | Disposition |
| --- | --- | --- |
| Mechanical | `tc-lock-stale`, `tc-config-duplicate`, `tc-generated-stale` | regenerate or normalize from the deterministic source, then re-run the doctor |
| Structural | `tc-runtime-drift`, `tc-tool-unpinned`, `tc-build-backend-missing`, `tc-key-unarbitered` | apply one bounded contract repair only when the target declaration identifies the answer, then re-run the doctor |
| Judgement | none in the initial vocabulary | report the evidence and the target owner's closing action; never choose a version, tool, backend, lock policy or owner |

Never turn an absent policy into a finding by guessing. A lock that the ecosystem does not require,
a language version with no chosen source, and a tool with no target-owned pin remain decisions for
the owner of the build.

**Done when:** each finding has its code, band, evidence, affected artifact and a permitted closing
shape.

### 4. Present one plan and ask once

Show the complete plan: every mechanical regeneration, every structural edit, every residual
judgement hand-off, the exact target files and the closing `toolchain doctor` command. Ask once for
authorization of the routine batch. A version choice, tool choice, backend choice, lock adoption or
ownership arbitration remains an individual target-owner decision and is not absorbed by the batch
authorization.

If authorization is rejected, write nothing and report the findings unchanged.

**Done when:** one complete plan has been presented and either authorized or rejected without a
target edit.

### 5. Apply only authorized mechanical and structural closures

Under the authorization, edit only the affected manifest, lock, pin or tool-configuration block
named by the evidence. Preserve authored text outside generated regions. Do not run a package
manager, upgrade a dependency, select a language version, add a pin whose value is unknown, or
choose an arbiter from file order. Those are target-owner decisions unless the target contract has
already made them deterministic.

Re-run the same closing verifier:

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
cq --root "$TARGET_ROOT" toolchain doctor --json
```

If findings remain, distinguish unresolved judgement residue from a failed mechanical or structural
repair. Do not repeat an empty pass or broaden the target surface.

**Done when:** authorized closures are applied, no target policy was selected, and the closing
verifier has been run.

### 6. Report the front

Report the target root, applicability state and signal, every manifest/lock/pin/tool-configuration
row, applied changes, the closing verifier result and all residual findings with their evidence and
owner action. State explicitly when the front was not applicable, already conformant, refused
configuration, or remains non-conformant. This command's report is the run record; do not append a
log file to the target.

**Done when:** the report distinguishes applicability, evidence, applied closures, verifier state
and every residual owner action.

## Invariants

- Applicability is probed before inventory and before any confirmation.
- `not-applicable` and refusal are explicit states, never guessed healthy configuration.
- The doctor payload is the authoritative finding and inventory source for this pass.
- Mechanical and bounded structural findings may be applied; build policy and judgement remain report-only.
- The closing verifier is the same `cq toolchain doctor --json` program as the probe.
- The command never rewrites `.claude/quenching.json` into a toolchain artifact or creates a second configuration home.
