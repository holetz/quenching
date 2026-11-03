---
description: >-
  Mint or edit ONE subagent definition in .claude/agents/. Use for "create an agent", "add a subagent", "make a verifier agent". Not for: commands → /quenching-align:components:command:new; hooks → /quenching-align:components:hook:new.
argument-hint: [agent-name-or-description]
allowed-tools: Bash(cq:*), Bash(cq.cmd:*), Bash(python3:*), Bash(py:*), Read, Grep, Glob, Write, Edit, AskUserQuestion
disable-model-invocation: true
---

# /quenching-align:components:agent:new — typed shortcut

Typed shortcut to the `agent-new` flow of [/quenching-align:components:components](${CLAUDE_PLUGIN_ROOT}/commands/components/components.md).
Input: `$ARGUMENTS`.

```bash
cq components read ${CLAUDE_PLUGIN_ROOT}/assets/references/components-flows/agent-new.md
```
Read the flow whole, once, and follow it from its own `## Workflow` with `$ARGUMENTS` as its input:
its steps, `Done when:` lines and invariants bind this run as they would the flow itself.
**Done when:** the flow ran to its own `Done when:`, or stopped on its own stop condition.
