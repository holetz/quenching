---
description: >-
  Drain the project's Claude Code memory into the OKF bundle, then clear it. Use for "convert the memory into docs", "flush the memory into docs". Not for: external sources → /quenching-align:knowledge:import.
argument-hint: [optional-scope]
allowed-tools: Bash(cq:*), Bash(cq.cmd:*), Read, Grep, Glob, Bash(python3:*), Bash(py:*), Bash(rm:*), Write, Edit, Task, AskUserQuestion
disable-model-invocation: true
---

# /quenching-align:knowledge:import-memory — typed shortcut

Typed shortcut to the `import-memory` flow of [/quenching-align:knowledge:knowledge](${CLAUDE_PLUGIN_ROOT}/commands/knowledge/knowledge.md).
Input: `$ARGUMENTS`.

```bash
cq components read ${CLAUDE_PLUGIN_ROOT}/assets/references/knowledge-flows/import-memory.md
```
Read the flow whole, once, and follow it from its own `## Workflow` with `$ARGUMENTS` as its input:
its steps, `Done when:` lines and invariants bind this run as they would the flow itself.
**Done when:** the flow ran to its own `Done when:`, or stopped on its own stop condition.
