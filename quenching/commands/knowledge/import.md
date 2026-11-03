---
description: >-
  Import an external source (files, folders, URLs) into the OKF bundle as many docs. Use for "ingest a source into the base", "generate OKF docs from these files". Not for: one item → /quenching-align:knowledge:add.
argument-hint: [source-paths-or-urls]
allowed-tools: Bash(cq:*), Bash(cq.cmd:*), Read, Grep, Glob, WebFetch, Bash(python3:*), Write, Edit, Task, AskUserQuestion
disable-model-invocation: true
---

# /quenching-align:knowledge:import — typed shortcut

Typed shortcut to the `import` flow of [/quenching-align:knowledge:knowledge](${CLAUDE_PLUGIN_ROOT}/commands/knowledge/knowledge.md).
Input: `$ARGUMENTS`.

```bash
cq components read ${CLAUDE_PLUGIN_ROOT}/assets/references/knowledge-flows/import.md
```
Read the flow whole, once, and follow it from its own `## Workflow` with `$ARGUMENTS` as its input:
its steps, `Done when:` lines and invariants bind this run as they would the flow itself.
**Done when:** the flow ran to its own `Done when:`, or stopped on its own stop condition.
