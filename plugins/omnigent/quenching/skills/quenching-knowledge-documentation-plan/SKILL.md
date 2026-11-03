---
name: quenching-knowledge-documentation-plan
description: "Build a sourced documentation plan for the OKF bundle with reader journeys. Use for \"plan the documentation\", \"design the documentation architecture\". Not for: pages → quenching-knowledge-documentation-write."
allowed-tools: "Bash(cq:*), Bash(cq.cmd:*), Read, Grep, Glob, Bash(python3:*), Bash(py:*), Bash(rg:*), Write, AskUserQuestion"
---

<!-- GENERATED FROM plugins/quenching/commands/knowledge/documentation/plan.md -->

<!-- OMNIGENT RUNTIME START -->
## Omnigent runtime

This runs inside the `quenching` operator agent on whatever model the server's policy selects; it pins none and names no vendor CLI. The bundle carries no payload: read a reference through the `quenching` MCP server's resources (`quenching://references/<path>`), and prefer its tools (`<pillar>_<verb>`) to a shell `cq`, which resolves only where a local install sits under `$QUENCHING_OMNIGENT_ROOT`. Delegate only to the operator's declared sub-agents. Source model tiers and effort are not switches: a declared tier or effort below is a preference to report. Token usage comes from host telemetry when it exists, otherwise it is `not measured`. A tool the permission policy denies stays denied: report it, never route around it. If delegation is unavailable, report the limitation; never replace a required independent verification with self-review.

<!-- OMNIGENT RUNTIME END -->


# quenching-knowledge-documentation-plan — typed shortcut

Typed shortcut to the `documentation-plan` flow of [quenching-knowledge-knowledge](~/.omnigent/quenching/commands/knowledge/knowledge.md).
Input: `$ARGUMENTS`.

```bash
# Read the quenching MCP resource: quenching://references/knowledge-flows/documentation-plan.md
```
Read the flow whole, once, and follow it from its own `## Workflow` with `$ARGUMENTS` as its input:
its steps, `Done when:` lines and invariants bind this run as they would the flow itself.
**Done when:** the flow ran to its own `Done when:`, or stopped on its own stop condition.
