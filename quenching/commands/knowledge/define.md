---
description: >-
  Add or refine ONE glossary.md entry. Use for "add a term to the glossary", "define this term". Not for: concept docs → /quenching-align:knowledge:learn; bulk sweeps → /quenching-align:knowledge:glossary-backfill.
argument-hint: [term]
allowed-tools: Bash(cq:*), Bash(cq.cmd:*), Read, Grep, Glob, Bash(python3:*), Write, Edit, AskUserQuestion
disable-model-invocation: true
---

# /quenching-align:knowledge:define — typed shortcut

Typed shortcut to the `define` flow of [/quenching-align:knowledge:knowledge](${CLAUDE_PLUGIN_ROOT}/commands/knowledge/knowledge.md).
Input: `$ARGUMENTS`.

```bash
cq components read ${CLAUDE_PLUGIN_ROOT}/assets/references/knowledge-flows/define.md
```
Read the flow whole, once, and follow it from its own `## Workflow` with `$ARGUMENTS` as its input:
its steps, `Done when:` lines and invariants bind this run as they would the flow itself.
**Done when:** the flow ran to its own `Done when:`, or stopped on its own stop condition.
