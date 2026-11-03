---
description: "Insert ONE new concept doc into the OKF bundle with the right home, type and stamp. Use for \"add a standard/table/announcement\". Not for: glossary terms → /quenching-knowledge-define; batches → /quenching-knowledge-import."
argument-hint: "[the-knowledge-to-add]"
allowed-tools: Bash(.agents/quenching/bin/cq:*), Bash(.agents/quenching/bin/cq.cmd:*), Read, Grep, Glob, Write, Edit, AskUserQuestion
disable-model-invocation: true
---

# /quenching-knowledge-add — typed shortcut

Typed shortcut to the `add` flow of [/quenching-knowledge-knowledge](.agents/quenching/commands/knowledge/knowledge.md).
Input: `$ARGUMENTS`.

```bash
.agents/quenching/bin/cq components read .agents/quenching/assets/references/knowledge-flows/add.md
```
Read the flow whole, once, and follow it from its own `## Workflow` with `$ARGUMENTS` as its input:
its steps, `Done when:` lines and invariants bind this run as they would the flow itself.
**Done when:** the flow ran to its own `Done when:`, or stopped on its own stop condition.
