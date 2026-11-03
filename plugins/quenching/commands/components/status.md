---
description: >-
  Report the automation surface: command count, fronts and findings, read-only. Use for "components status", "check the automation surface". Not for: repairs → /quenching-align:components:align.
argument-hint: [optional-target-root]
allowed-tools: Bash(cq:*), Bash(cq.cmd:*), Read, Grep, Glob, Bash(python3:*)
disable-model-invocation: true
---

# /quenching-align:components:status — typed shortcut

Typed shortcut to the `status` flow of [/quenching-align:components:components](${CLAUDE_PLUGIN_ROOT}/commands/components/components.md).
Input: `$ARGUMENTS`.

```bash
cq components read ${CLAUDE_PLUGIN_ROOT}/assets/references/components-flows/status.md
```
Read the flow whole, once, and follow it from its own `## Workflow` with `$ARGUMENTS` as its input:
its steps, `Done when:` lines and invariants bind this run as they would the flow itself.
**Done when:** the flow ran to its own `Done when:`, or stopped on its own stop condition.
