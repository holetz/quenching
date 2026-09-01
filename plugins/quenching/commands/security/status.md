---
description: Read the security pillar and report workflow permissions, secret and ignore coverage, advisory dependency configuration and access ownership without writing. Triggers on "security status", "security audit", or "check repository security coverage". Not for: changing permissions, secrets, dependencies or access policy — those remain target-owner decisions.
argument-hint: [optional-target-root]
allowed-tools: Read, Grep, Glob, Bash(python3:*)
---

# /quenching:security:status — read the security pillar

**Input**: `$ARGUMENTS` (an optional target repository root; omit to use the current repository).

This command is the read-only status/audit view of the security pillar. It reports live evidence
without owning a security tree, selecting a target policy or repairing a finding. Resolve `cq` per
[tool-resolution.md](${CLAUDE_PLUGIN_ROOT}/assets/references/align/tool-resolution.md)
§Resolving the tool. Set `TARGET_ROOT` to `$ARGUMENTS`, or `.` when omitted, and run:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/assets/bin/cq" --root "$TARGET_ROOT" security --json
```

Branch on the JSON and exit code: `0` is a measured report, `1` carries reported observations, and
`2` is a refusal. On exit `2`, preserve the refusal and affected path exactly; never guess a root,
provider policy or missing security declaration. On exit `0` or `1`, use the returned payload as the
complete read model and do not invoke a write-capable command.

## Report

Report one compact table:

| Question | State | Evidence |
| --- | --- | --- |
| `workflow-permissions` | `present`/`missing`/`refused` | workflow paths and workflow/job declaration counts |
| `secret-ignore-coverage` | `present`/`missing`/`refused` | ignore path and recognized secret classes, never secret values |
| `advisory-dependency-configuration` | `present`/`missing`/`refused` | recognized advisory configuration paths |
| `access-ownership` | `present`/`missing` | recognized ownership declaration paths, never owner values |

Preserve every question key, state, evidence path and detail returned by the route. Distinguish a
missing declaration from a source that was not measurable or was refused. Preserve the payload's
`readOnly` and `writePolicy` values: the pillar read workflow permissions, ignore patterns,
advisory configuration and ownership declarations only; it did not expose secret or owner values.

State that this command wrote nothing and did not change workflows, ignore rules, dependencies,
configuration, access policy or generated files. Security has no align, doctor, bands file or
conductor row; status names no repair command because the target owner decides any action.

## Invariants

- Read only: no permission, secret, dependency, configuration or access-policy edit.
- The payload's `present`, `missing`, `not-measured` and `refused` states remain distinct.
- The pillar reports evidence and ownership boundaries; it never chooses or applies target policy.
- No secret or access-owner value is copied into the report.
