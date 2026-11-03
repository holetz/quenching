---
description: "Wire ONE scoped hook with the narrowest scope and cheapest handler. Use for \"create a hook\", \"check this after every edit\", \"block that command\". Not for: command bodies → /quenching-components-command-new."
argument-hint: "[what-the-hook-should-catch]"
allowed-tools: Bash(.agents/quenching/bin/cq:*), Bash(.agents/quenching/bin/cq.cmd:*), Bash(python3:*), Bash(py:*), Read, Grep, Glob, Write, Edit, AskUserQuestion
disable-model-invocation: true
---

# /quenching-components-hook-new — typed shortcut

Typed shortcut to the `hook-new` flow of [/quenching-components-components](.agents/quenching/commands/components/components.md).
Input: `$ARGUMENTS`.

```bash
.agents/quenching/bin/cq components read .agents/quenching/assets/references/components-flows/hook-new.md
```
Read the flow whole, once, and follow it from its own `## Workflow` with `$ARGUMENTS` as its input:
its steps, `Done when:` lines and invariants bind this run as they would the flow itself.
**Done when:** the flow ran to its own `Done when:`, or stopped on its own stop condition.
