---
description: "Force /docs/ into the canonical OKF v0.2 bundle and absorb out-of-band content until stable. Use for \"align the docs\", \"set up /docs/\", \"converge the knowledge base\". Not for: one item → /quenching-knowledge-add."
argument-hint: "[optional-docs-path]"
allowed-tools: Bash(.agents/quenching/bin/cq:*), Bash(.agents/quenching/bin/cq.cmd:*), Read, Grep, Glob, Bash, Write, Edit, Task, Skill, AskUserQuestion
disable-model-invocation: true
---

# /quenching-knowledge-align — typed shortcut

Typed shortcut to the `align` flow of [/quenching-knowledge-knowledge](.agents/quenching/commands/knowledge/knowledge.md).
Input: `$ARGUMENTS`.

```bash
.agents/quenching/bin/cq components read .agents/quenching/assets/references/knowledge-flows/align.md
```
Read the flow whole, once, and follow it from its own `## Workflow` with `$ARGUMENTS` as its input:
its steps, `Done when:` lines and invariants bind this run as they would the flow itself.
**Done when:** the flow ran to its own `Done when:`, or stopped on its own stop condition.
