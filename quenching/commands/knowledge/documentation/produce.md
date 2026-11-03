---
description: >-
  Run the complete documentation pipeline: site setup, sourced pages, review, strict build. Use for "produce the documentation", "generate the complete docs site". Not for: one stage → its own command.
argument-hint: [optional-source-scope] [--desde <git-ref>]
allowed-tools: Bash(cq:*), Bash(cq.cmd:*), Read, Grep, Glob, Bash(python3:*), Bash(py:*), Skill
disable-model-invocation: true
---

# /quenching-align:knowledge:documentation:produce — typed shortcut

Typed shortcut to the `documentation-produce` flow of [/quenching-align:knowledge:knowledge](${CLAUDE_PLUGIN_ROOT}/commands/knowledge/knowledge.md).
Input: `$ARGUMENTS`.

```bash
cq components read ${CLAUDE_PLUGIN_ROOT}/assets/references/knowledge-flows/documentation-produce.md
```
Read the flow whole, once, and follow it from its own `## Workflow` with `$ARGUMENTS` as its input:
its steps, `Done when:` lines and invariants bind this run as they would the flow itself.
**Done when:** the flow ran to its own `Done when:`, or stopped on its own stop condition.
