---
description: >-
  Insert ONE new concept doc into the OKF bundle with the right home, type and stamp. Use for "add a standard/table/announcement". Not for: glossary terms → /quenching-align:knowledge:define; batches → /quenching-align:knowledge:import.
argument-hint: [the-knowledge-to-add]
allowed-tools: Bash(cq:*), Bash(cq.cmd:*), Read, Grep, Glob, Write, Edit, AskUserQuestion
disable-model-invocation: true
---

# /quenching-align:knowledge:add — typed shortcut

Typed shortcut to the `add` flow of [/quenching-align:knowledge:knowledge](${CLAUDE_PLUGIN_ROOT}/commands/knowledge/knowledge.md).
Input: `$ARGUMENTS`.

```bash
cq components read ${CLAUDE_PLUGIN_ROOT}/assets/references/knowledge-flows/add.md
```
Read the flow whole, once, and follow it from its own `## Workflow` with `$ARGUMENTS` as its input:
its steps, `Done when:` lines and invariants bind this run as they would the flow itself.
**Done when:** the flow ran to its own `Done when:`, or stopped on its own stop condition.
