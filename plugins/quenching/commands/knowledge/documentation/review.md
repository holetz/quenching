---
description: >-
  Score documentation pages against the eleven-dimension quality gate, read-only. Use for "review the documentation", "score the docs pages". Not for: fixing gaps → /quenching-align:knowledge:documentation:write.
argument-hint: [optional-page-slice-or-plan-path]
allowed-tools: Bash(cq:*), Bash(cq.cmd:*), Read, Grep, Glob, Task
disable-model-invocation: true
---

# /quenching-align:knowledge:documentation:review — typed shortcut

Typed shortcut to the `documentation-review` flow of [/quenching-align:knowledge:knowledge](${CLAUDE_PLUGIN_ROOT}/commands/knowledge/knowledge.md).
Input: `$ARGUMENTS`.

```bash
cq components read ${CLAUDE_PLUGIN_ROOT}/assets/references/knowledge-flows/documentation-review.md
```
Read the flow whole, once, and follow it from its own `## Workflow` with `$ARGUMENTS` as its input:
its steps, `Done when:` lines and invariants bind this run as they would the flow itself.
**Done when:** the flow ran to its own `Done when:`, or stopped on its own stop condition.
