---
description: >-
  Wire ONE scoped hook with the narrowest scope and cheapest handler. Use for "create a hook", "check this after every edit", "block that command". Not for: command bodies → /quenching-align:components:command:new.
argument-hint: [what-the-hook-should-catch]
allowed-tools: Bash(cq:*), Bash(cq.cmd:*), Bash(python3:*), Bash(py:*), Read, Grep, Glob, Write, Edit, AskUserQuestion
disable-model-invocation: true
---

# /quenching-align:components:hook:new — typed shortcut

Typed shortcut to the `hook-new` flow of [/quenching-align:components:components](${CLAUDE_PLUGIN_ROOT}/commands/components/components.md).
Input: `$ARGUMENTS`.

```bash
cq components read ${CLAUDE_PLUGIN_ROOT}/assets/references/components-flows/hook-new.md
```
Read the flow whole, once, and follow it from its own `## Workflow` with `$ARGUMENTS` as its input:
its steps, `Done when:` lines and invariants bind this run as they would the flow itself.
**Done when:** the flow ran to its own `Done when:`, or stopped on its own stop condition.
