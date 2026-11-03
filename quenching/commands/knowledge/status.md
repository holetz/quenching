---
description: >-
  Report where the OKF bundle stands in /docs/, read-only. Use for "status of the docs", "is the bundle conformant". Not for: repairs → /quenching-align:knowledge:align; additions → /quenching-align:knowledge:add.
argument-hint: [optional-home-or-path]
allowed-tools: Bash(cq:*), Bash(cq.cmd:*), Read, Grep, Glob, Bash(python3:*), Bash(py:*)
disable-model-invocation: true
---

# /quenching-align:knowledge:status — typed shortcut

Typed shortcut to the `status` flow of [/quenching-align:knowledge:knowledge](${CLAUDE_PLUGIN_ROOT}/commands/knowledge/knowledge.md).
Input: `$ARGUMENTS`.

```bash
cq components read ${CLAUDE_PLUGIN_ROOT}/assets/references/knowledge-flows/status.md
```
Read the flow whole, once, and follow it from its own `## Workflow` with `$ARGUMENTS` as its input:
its steps, `Done when:` lines and invariants bind this run as they would the flow itself.
**Done when:** the flow ran to its own `Done when:`, or stopped on its own stop condition.
