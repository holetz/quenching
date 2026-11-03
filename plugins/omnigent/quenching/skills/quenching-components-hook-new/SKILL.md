---
name: quenching-components-hook-new
description: "Wire ONE scoped hook with the narrowest scope and cheapest handler. Use for \"create a hook\", \"check this after every edit\", \"block that command\". Not for: command bodies → quenching-components-command-new."
allowed-tools: "Bash(cq:*), Bash(cq.cmd:*), Bash(python3:*), Bash(py:*), Read, Grep, Glob, Write, Edit, AskUserQuestion"
---

<!-- GENERATED FROM plugins/quenching/commands/components/hook/new.md -->

<!-- OMNIGENT RUNTIME START -->
## Omnigent runtime

This runs inside the `quenching` operator agent on whatever model the server's policy selects; it pins none and names no vendor CLI. The bundle carries no payload: read a reference through the `quenching` MCP server's resources (`quenching://references/<path>`), and prefer its tools (`<pillar>_<verb>`) to a shell `cq`, which resolves only where a local install sits under `$QUENCHING_OMNIGENT_ROOT`. Delegate only to the operator's declared sub-agents. Source model tiers and effort are not switches: a declared tier or effort below is a preference to report. Token usage comes from host telemetry when it exists, otherwise it is `not measured`. A tool the permission policy denies stays denied: report it, never route around it. If delegation is unavailable, report the limitation; never replace a required independent verification with self-review.

<!-- OMNIGENT RUNTIME END -->


# quenching-components-hook-new — typed shortcut

Typed shortcut to the `hook-new` flow of [quenching-components-components](~/.omnigent/quenching/commands/components/components.md).
Input: `$ARGUMENTS`.

```bash
# Read the quenching MCP resource: quenching://references/components-flows/hook-new.md
```
Read the flow whole, once, and follow it from its own `## Workflow` with `$ARGUMENTS` as its input:
its steps, `Done when:` lines and invariants bind this run as they would the flow itself.
**Done when:** the flow ran to its own `Done when:`, or stopped on its own stop condition.
