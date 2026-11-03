---
description: >-
  Sweep the whole bundle to backfill glossary.md with missing terms. Use for "backfill the glossary", "find terms we never added". Not for: one term → /quenching-align:knowledge:define.
argument-hint: [optional-home-scope]
allowed-tools: Bash(cq:*), Bash(cq.cmd:*), Read, Grep, Glob, Bash(python3:*), Bash(py:*), Write, Edit, Task, AskUserQuestion
disable-model-invocation: true
---

# /quenching-align:knowledge:glossary-backfill — typed shortcut

Typed shortcut to the `glossary-backfill` flow of [/quenching-align:knowledge:knowledge](${CLAUDE_PLUGIN_ROOT}/commands/knowledge/knowledge.md).
Input: `$ARGUMENTS`.

```bash
cq components read ${CLAUDE_PLUGIN_ROOT}/assets/references/knowledge-flows/glossary-backfill.md
```
Read the flow whole, once, and follow it from its own `## Workflow` with `$ARGUMENTS` as its input:
its steps, `Done when:` lines and invariants bind this run as they would the flow itself.
**Done when:** the flow ran to its own `Done when:`, or stopped on its own stop condition.
