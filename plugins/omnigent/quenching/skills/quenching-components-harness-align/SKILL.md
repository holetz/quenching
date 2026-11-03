---
name: quenching-components-harness-align
description: "Refactor AGENTS.md into thin pointers over the /docs/ bundle, with no AGENTS.md. Use for \"slim down AGENTS.md\", \"move AGENTS.md content into docs\". Not for: command bodies → quenching-components-command-new."
allowed-tools: "Bash(cq:*), Bash(cq.cmd:*), Read, Grep, Glob, Bash(find:*), Bash(git grep:*), Bash(git check-ignore:*), Bash(grep:*), Bash(python3:*), Bash(py:*), Write, Edit, Task, AskUserQuestion"
---

<!-- GENERATED FROM plugins/quenching/commands/components/harness/align.md -->

<!-- OMNIGENT RUNTIME START -->
## Omnigent runtime

This runs inside the `quenching` operator agent on whatever model the server's policy selects; it pins none and names no vendor CLI. The bundle carries no payload: read a reference through the `quenching` MCP server's resources (`quenching://references/<path>`), and prefer its tools (`<pillar>_<verb>`) to a shell `cq`, which resolves only where a local install sits under `$QUENCHING_OMNIGENT_ROOT`. Delegate only to the operator's declared sub-agents. Source model tiers and effort are not switches: a declared tier or effort below is a preference to report. Token usage comes from host telemetry when it exists, otherwise it is `not measured`. A tool the permission policy denies stays denied: report it, never route around it. If delegation is unavailable, report the limitation; never replace a required independent verification with self-review.

<!-- OMNIGENT RUNTIME END -->


# quenching-components-harness-align — typed shortcut

Typed shortcut to the `harness-align` flow of [quenching-components-components](~/.omnigent/quenching/commands/components/components.md).
Input: `$ARGUMENTS`.

```bash
# Read the quenching MCP resource: quenching://references/components-flows/harness-align.md
```
Read the flow whole, once, and follow it from its own `## Workflow` with `$ARGUMENTS` as its input:
its steps, `Done when:` lines and invariants bind this run as they would the flow itself.
**Done when:** the flow ran to its own `Done when:`, or stopped on its own stop condition.
