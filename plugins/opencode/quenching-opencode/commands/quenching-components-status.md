---
description: "Report the automation surface: command count, fronts and findings, read-only. Use for \"components status\", \"check the automation surface\". Not for: repairs → quenching-components-align."
---

<!-- GENERATED FROM plugins/quenching/commands/components/status.md -->

<!-- OPENCODE RUNTIME START -->
## OpenCode runtime

Delegate only through OpenCode's task tool, to the registered subagents named `quenching-<agent>` (protocol copies live under `~/.opencode/quenching/agents/`). Never launch the Claude CLI and never request a Claude model during an OpenCode run. Source model tiers are not pinned here: every command and subagent runs on the model the OpenCode session configures; a declared tier or effort below is a preference to report, not a switch. Token usage comes from host telemetry when it exists, otherwise it is `not measured`; `cq components session cost` and `context` read no OpenCode log and refuse (exit 2, unmeasured). If delegation is unavailable, report the limitation; never replace a required independent verification with self-review.

<!-- OPENCODE RUNTIME END -->


# quenching-components-status — read the automation surface

**Input**: `$ARGUMENTS` (an optional target repository root; omit to use the current repository).

This command is the read-only view of the target's automation surface: `.agents/skills/` as the
source, `.opencode/skills/` as its generated OpenCode bridge. The common
front contract is in [front-align/mold.md](~/.opencode/quenching/references/front-align/mold.md).
The components doctor owns the mechanical surface invariant; status adds the compact inventory of
commands, fronts and finding codes without choosing an axis or repairing a body.

## Workflow

### 1. Read the status payload

Set `TARGET_ROOT` to `$ARGUMENTS`, or to `.` when the argument is omitted, and run:

```bash
cq() { python3 "${QUENCHING_OPENCODE_ROOT:-$HOME/.opencode/quenching}/scripts/cq" "$@"; }
cq --root "$TARGET_ROOT" components status --json
cq components migrate --target "$TARGET_ROOT" --json
cq components bridge --target "$TARGET_ROOT" --check --json
```

`migrate` without `--write` and `bridge --check` only plan: neither writes.

Branch on the JSON and exit code: `0` is a clean report, `1` carries findings, and `2` is a
refusal. Preserve a missing or not-applicable surface as returned; do not guess a root or create
one. On exit `0` or `1`, use the three payloads as the complete read model and never add
`--write` to either.

**Done when:** the payload is captured, or a refusal is preserved with its reason.

### 2. Report the surface

Report one compact table with the target root and applicability state, command count, counts by
front, finding codes with their error/warning totals, and the overall `ok` state; then one
conformance line: the migrate plan (`conformant: true`, or its operation and conflict counts) and
the bridge (in step, or its change count). Conformant is both: an empty plan and `bridge --check`
exit 0; anything else routes to `quenching-components-align`. Preserve every
returned code and message; an empty surface is an explicit state, not a reason to invent commands.
For an actionable finding, name `quenching-components-align` as the bounded repair route; for a
single command body or description, name `quenching-components-command-new` as the focused edit
route. Status itself does not invoke either route.

**Done when:** every returned field is represented, and each finding keeps its code, severity and
closing route.

### 3. Self-check

State that the command wrote nothing, changed no command or registry, and did not run a target
workflow or test suite. Confirm that the report matches the status payload and its exit code.

**Done when:** the report ends with the read-only boundary and the observed exit code.

## Invariants

- Read only: no command, description, registry or generated surface is edited.
- Applicability, missing state, command count, front counts and findings come from `cq components status`;
  migration and bridge state come from `migrate` and `bridge --check`, never from a guess.
- Findings retain their emitted code and severity; status never softens a finding into a clean state.
- The report names a closing command but never invokes a repair.
