---
description: >-
  Build a sourced documentation plan for the OKF bundle with reader journeys. Use for "plan the documentation", "design the documentation architecture". Not for: pages → /quenching-align:knowledge:documentation:write.
argument-hint: [optional-source-paths-or-scope]
allowed-tools: Bash(cq:*), Bash(cq.cmd:*), Read, Grep, Glob, Bash(python3:*), Bash(py:*), Bash(rg:*), Write, AskUserQuestion
disable-model-invocation: true
---

# /quenching-align:knowledge:documentation:plan — typed shortcut

Typed shortcut to the `documentation-plan` flow of [/quenching-align:knowledge:knowledge](${CLAUDE_PLUGIN_ROOT}/commands/knowledge/knowledge.md).
Input: `$ARGUMENTS`.

```bash
cq components read ${CLAUDE_PLUGIN_ROOT}/assets/references/knowledge-flows/documentation-plan.md
```
Read the flow whole, once, and follow it from its own `## Workflow` with `$ARGUMENTS` as its input:
its steps, `Done when:` lines and invariants bind this run as they would the flow itself.
**Done when:** the flow ran to its own `Done when:`, or stopped on its own stop condition.
