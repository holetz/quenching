---
description: >-
  Create or update the Zensical site layer with extensions, CSS, navigation and strict-build QA. Use for "build the docs site", "fix the docs nav". Not for: prose → /quenching-align:knowledge:documentation:write.
argument-hint: [optional-section-or-config-path]
allowed-tools: Bash(cq:*), Bash(cq.cmd:*), Read, Grep, Glob, Bash, Write, Edit, AskUserQuestion
disable-model-invocation: true
---

# /quenching-align:knowledge:documentation:build — typed shortcut

Typed shortcut to the `documentation-build` flow of [/quenching-align:knowledge:knowledge](${CLAUDE_PLUGIN_ROOT}/commands/knowledge/knowledge.md).
Input: `$ARGUMENTS`.

```bash
cq components read ${CLAUDE_PLUGIN_ROOT}/assets/references/knowledge-flows/documentation-build.md
```
Read the flow whole, once, and follow it from its own `## Workflow` with `$ARGUMENTS` as its input:
its steps, `Done when:` lines and invariants bind this run as they would the flow itself.
**Done when:** the flow ran to its own `Done when:`, or stopped on its own stop condition.
