---
description: "Refactor AGENTS.md into thin pointers over the /docs/ bundle, with no AGENTS.md. Use for \"slim down AGENTS.md\", \"move AGENTS.md content into docs\". Not for: command bodies → /quenching-components-command-new."
argument-hint: "[optional-harness-file]"
allowed-tools: Bash(.agents/quenching/bin/cq:*), Bash(.agents/quenching/bin/cq.cmd:*), Read, Grep, Glob, Bash(find:*), Bash(git grep:*), Bash(git check-ignore:*), Bash(grep:*), Bash(python3:*), Bash(py:*), Write, Edit, Task, AskUserQuestion
disable-model-invocation: true
---

# /quenching-components-harness-align — typed shortcut

Typed shortcut to the `harness-align` flow of [/quenching-components-components](.agents/quenching/commands/components/components.md).
Input: `$ARGUMENTS`.

```bash
.agents/quenching/bin/cq components read .agents/quenching/assets/references/components-flows/harness-align.md
```
Read the flow whole, once, and follow it from its own `## Workflow` with `$ARGUMENTS` as its input:
its steps, `Done when:` lines and invariants bind this run as they would the flow itself.
**Done when:** the flow ran to its own `Done when:`, or stopped on its own stop condition.
