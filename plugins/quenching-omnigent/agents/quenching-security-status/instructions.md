<!-- GENERATED FROM plugins/quenching/commands/security/status.md -->

<!-- OMNIGENT RUNTIME START -->
## Omnigent runtime

This bundle runs on whatever harness and model the caller passes (`omnigent run --harness X --model Y`); it pins neither and names no vendor CLI. Delegate only through Omnigent's own session tools, and only when this bundle's `config.yaml` sets `spawn: true`; protocol copies of the subagents live under `~/.omnigent/quenching/agents/`. Source model tiers and effort are not switches: a declared tier or effort below is a preference to report. Token usage comes from host telemetry when it exists, otherwise it is `not measured`; `cq components session cost` and `context` read no Omnigent log and refuse (exit 2, unmeasured). A tool the permission policy denies stays denied: report it, never route around it. If delegation is unavailable, report the limitation; never replace a required independent verification with self-review.

<!-- OMNIGENT RUNTIME END -->


# quenching-security-status — read the security pillar

**Input**: `$ARGUMENTS` (an optional target repository root; omit to use the current repository).

This command is the read-only status/audit view of the security pillar. It reports live evidence
without owning a security tree, selecting a target policy or repairing a finding. Resolve `cq` per
[tool-resolution.md](~/.omnigent/quenching/references/align/tool-resolution.md)
§Resolving the tool. Set `TARGET_ROOT` to `$ARGUMENTS`, or `.` when omitted, and run:

```bash
cq() { python3 "${QUENCHING_OMNIGENT_ROOT:-$HOME/.omnigent/quenching}/scripts/cq" "$@"; }
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
