---
description: >-
  Read the target's automation surface and report its command count, fronts and findings without
  writing. Triggers on "components status", "check the automation surface", or "what is the state
  of the command surface". Not for: repairing findings → /quenching:components:align; minting one
  command → /quenching:components:command:new.
argument-hint: [optional-target-root]
allowed-tools: Read, Grep, Glob, Bash(python3:*)
---

# /quenching:components:status — read the automation surface

**Input**: `$ARGUMENTS` (an optional target repository root; omit to use the current repository).

This command is the read-only view of the target's `.claude/` automation surface. The common
front contract is in [front-align/mold.md](${CLAUDE_PLUGIN_ROOT}/assets/references/front-align/mold.md).
The components doctor owns the mechanical surface invariant; status adds the compact inventory of
commands, fronts and finding codes without choosing an axis or repairing a body.

## Workflow

### 1. Read the status payload

Set `TARGET_ROOT` to `$ARGUMENTS`, or to `.` when the argument is omitted, and run:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/assets/bin/cq" --root "$TARGET_ROOT" components status --json
```

Branch on the JSON and exit code: `0` is a clean report, `1` carries findings, and `2` is a
refusal. Preserve a missing or not-applicable surface as returned; do not guess a root or create
one. On exit `0` or `1`, use the payload as the complete read model and do not invoke a
write-capable subcommand.

**Done when:** the payload is captured, or a refusal is preserved with its reason.

### 2. Report the surface

Report one compact table with the target root and applicability state, command count, counts by
front, finding codes with their error/warning totals, and the overall `ok` state. Preserve every
returned code and message; an empty surface is an explicit state, not a reason to invent commands.
For an actionable finding, name `/quenching:components:align` as the bounded repair route; for a
single command body or description, name `/quenching:components:command:new` as the focused edit
route. Status itself does not invoke either route.

**Done when:** every returned field is represented, and each finding keeps its code, severity and
closing route.

### 3. Self-check

State that the command wrote nothing, changed no command or registry, and did not run a target
workflow or test suite. Confirm that the report matches the status payload and its exit code.

**Done when:** the report ends with the read-only boundary and the observed exit code.

## Invariants

- Read only: no command, description, registry or generated surface is edited.
- Applicability, missing state, command count, front counts and findings come from `cq components status`.
- Findings retain their emitted code and severity; status never softens a finding into a clean state.
- The report names a closing command but never invokes a repair.
