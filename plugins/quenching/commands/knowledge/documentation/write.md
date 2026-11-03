---
description: >-
  Write sourced Diátaxis pages from a documentation plan. Use for "write the documentation pages", "draft the docs from the plan". Not for: planning → /quenching-align:knowledge:documentation:plan; scoring → /quenching-align:knowledge:documentation:review.
argument-hint: [optional-page-slice-or-plan-path]
allowed-tools: Bash(cq:*), Bash(cq.cmd:*), Read, Grep, Glob, Write, Edit, Task, Bash(python3:*), Bash(py:*), AskUserQuestion
disable-model-invocation: true
---

# /quenching-align:knowledge:documentation:write — typed shortcut

Typed shortcut to the `documentation-write` flow of [/quenching-align:knowledge:knowledge](${CLAUDE_PLUGIN_ROOT}/commands/knowledge/knowledge.md).
Input: `$ARGUMENTS`.

```bash
cq components read ${CLAUDE_PLUGIN_ROOT}/assets/references/knowledge-flows/documentation-write.md
```
Read the flow whole, once, and follow it from its own `## Workflow` with `$ARGUMENTS` as its input:
its steps, `Done when:` lines and invariants bind this run as they would the flow itself.
**Done when:** the flow ran to its own `Done when:`, or stopped on its own stop condition.
