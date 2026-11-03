---
description: "Build a sourced documentation plan for the OKF bundle with reader journeys. Use for \"plan the documentation\", \"design the documentation architecture\". Not for: pages → /quenching-knowledge-documentation-write."
argument-hint: "[optional-source-paths-or-scope]"
allowed-tools: Bash(.agents/quenching/bin/cq:*), Bash(.agents/quenching/bin/cq.cmd:*), Read, Grep, Glob, Bash(python3:*), Bash(py:*), Bash(rg:*), Write, AskUserQuestion
disable-model-invocation: true
---

# /quenching-knowledge-documentation-plan — typed shortcut

Typed shortcut to the `documentation-plan` flow of [/quenching-knowledge-knowledge](.agents/quenching/commands/knowledge/knowledge.md).
Input: `$ARGUMENTS`.

```bash
.agents/quenching/bin/cq components read .agents/quenching/assets/references/knowledge-flows/documentation-plan.md
```
Read the flow whole, once, and follow it from its own `## Workflow` with `$ARGUMENTS` as its input:
its steps, `Done when:` lines and invariants bind this run as they would the flow itself.
**Done when:** the flow ran to its own `Done when:`, or stopped on its own stop condition.
