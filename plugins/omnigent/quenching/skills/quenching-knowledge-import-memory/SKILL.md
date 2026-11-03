---
name: quenching-knowledge-import-memory
description: "Drain the project's Claude Code memory into the OKF bundle, then clear it. Use for \"convert the memory into docs\", \"flush the memory into docs\". Not for: external sources → quenching-knowledge-import."
allowed-tools: "Bash(cq:*), Bash(cq.cmd:*), Read, Grep, Glob, Bash(python3:*), Bash(py:*), Bash(rm:*), Write, Edit, Task, AskUserQuestion"
---

<!-- GENERATED FROM plugins/quenching/commands/knowledge/import-memory.md -->

<!-- OMNIGENT RUNTIME START -->
## Omnigent runtime

This runs inside the `quenching` operator agent on whatever model the server's policy selects; it pins none and names no vendor CLI. The bundle carries no payload: read a reference through the `quenching` MCP server's resources (`quenching://references/<path>`), and prefer its tools (`<pillar>_<verb>`) to a shell `cq`, which resolves only where a local install sits under `$QUENCHING_OMNIGENT_ROOT`. Delegate only to the operator's declared sub-agents. Source model tiers and effort are not switches: a declared tier or effort below is a preference to report. Token usage comes from host telemetry when it exists, otherwise it is `not measured`. A tool the permission policy denies stays denied: report it, never route around it. If delegation is unavailable, report the limitation; never replace a required independent verification with self-review.

<!-- OMNIGENT RUNTIME END -->


# quenching-knowledge-import-memory — typed shortcut

Typed shortcut to the `import-memory` flow of [quenching-knowledge-knowledge](~/.omnigent/quenching/commands/knowledge/knowledge.md).
Input: `$ARGUMENTS`.

```bash
# Read the quenching MCP resource: quenching://references/knowledge-flows/import-memory.md
```
Read the flow whole, once, and follow it from its own `## Workflow` with `$ARGUMENTS` as its input:
its steps, `Done when:` lines and invariants bind this run as they would the flow itself.
**Done when:** the flow ran to its own `Done when:`, or stopped on its own stop condition.
