---
description: "Import an external source (files, folders, URLs) into the OKF bundle as many docs. Use for \"ingest a source into the base\", \"generate OKF docs from these files\". Not for: one item → /quenching-knowledge-add."
argument-hint: "[source-paths-or-urls]"
allowed-tools: Bash(.agents/quenching/bin/cq:*), Bash(.agents/quenching/bin/cq.cmd:*), Read, Grep, Glob, WebFetch, Bash(python3:*), Write, Edit, Task, AskUserQuestion
disable-model-invocation: true
---

# /quenching-knowledge-import — typed shortcut

Typed shortcut to the `import` flow of [/quenching-knowledge-knowledge](.agents/quenching/commands/knowledge/knowledge.md).
Input: `$ARGUMENTS`.

```bash
.agents/quenching/bin/cq components read .agents/quenching/assets/references/knowledge-flows/import.md
```
Read the flow whole, once, and follow it from its own `## Workflow` with `$ARGUMENTS` as its input:
its steps, `Done when:` lines and invariants bind this run as they would the flow itself.
**Done when:** the flow ran to its own `Done when:`, or stopped on its own stop condition.
