---
name: quenching-knowledge-documentation-write
description: "Write sourced Diátaxis pages from a documentation plan. Use for \"write the documentation pages\", \"draft the docs from the plan\". Not for: planning → quenching-knowledge-documentation-plan; scoring → quenching-knowledge-documentation-review."
allowed-tools: "Bash(cq:*), Bash(cq.cmd:*), Read, Grep, Glob, Write, Edit, Task, Bash(python3:*), Bash(py:*), AskUserQuestion"
---

<!-- GENERATED FROM plugins/quenching/commands/knowledge/documentation/write.md -->

<!-- OMNIGENT RUNTIME START -->
## Omnigent runtime

This runs inside the `quenching` operator agent on whatever model the server's policy selects; it pins none and names no vendor CLI. The bundle carries no payload: read a reference through the `quenching` MCP server's resources (`quenching://references/<path>`), and prefer its tools (`<pillar>_<verb>`) to a shell `cq`, which resolves only where a local install sits under `$QUENCHING_OMNIGENT_ROOT`. Delegate only to the operator's declared sub-agents. Source model tiers and effort are not switches: a declared tier or effort below is a preference to report. Token usage comes from host telemetry when it exists, otherwise it is `not measured`. A tool the permission policy denies stays denied: report it, never route around it. If delegation is unavailable, report the limitation; never replace a required independent verification with self-review.

<!-- OMNIGENT RUNTIME END -->


# quenching-knowledge-documentation-write — typed shortcut

Typed shortcut to the `documentation-write` flow of [quenching-knowledge-knowledge](~/.omnigent/quenching/commands/knowledge/knowledge.md).
Input: `$ARGUMENTS`.

```bash
# Read the quenching MCP resource: quenching://references/knowledge-flows/documentation-write.md
```
Read the flow whole, once, and follow it from its own `## Workflow` with `$ARGUMENTS` as its input:
its steps, `Done when:` lines and invariants bind this run as they would the flow itself.
**Done when:** the flow ran to its own `Done when:`, or stopped on its own stop condition.
