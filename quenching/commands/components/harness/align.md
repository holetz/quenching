---
description: >-
  Refactor AGENTS.md into thin pointers over the /docs/ bundle, with no CLAUDE.md. Use for "slim down AGENTS.md", "move AGENTS.md content into docs". Not for: command bodies → /quenching-align:components:command:new.
argument-hint: [optional-harness-file]
allowed-tools: Bash(cq:*), Bash(cq.cmd:*), Read, Grep, Glob, Bash(find:*), Bash(git grep:*), Bash(git check-ignore:*), Bash(grep:*), Bash(python3:*), Bash(py:*), Write, Edit, Task, AskUserQuestion
disable-model-invocation: true
---

# /quenching-align:components:harness:align — typed shortcut

Typed shortcut to the `harness-align` flow of [/quenching-align:components:components](${CLAUDE_PLUGIN_ROOT}/commands/components/components.md).
Input: `$ARGUMENTS`.

```bash
cq components read ${CLAUDE_PLUGIN_ROOT}/assets/references/components-flows/harness-align.md
```
Read the flow whole, once, and follow it from its own `## Workflow` with `$ARGUMENTS` as its input:
its steps, `Done when:` lines and invariants bind this run as they would the flow itself.
**Done when:** the flow ran to its own `Done when:`, or stopped on its own stop condition.
