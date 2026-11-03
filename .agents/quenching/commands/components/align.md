---
description: "Converge the .agents/skills surface and its Claude bridge, and review descriptions. Use for \"align the skills\", \"audit the command bodies\", \"shorten the descriptions\". Not for: one command → /quenching-components-command-new."
argument-hint: "[optional-scope]"
allowed-tools: Bash(.agents/quenching/bin/cq:*), Bash(.agents/quenching/bin/cq.cmd:*), Bash(python3:*), Bash(py:*), Bash(git grep:*), Bash(grep:*), Bash(mkdir:*), Bash(mv:*), Bash(rm:*), Read, Grep, Glob, Write, Edit, Task, AskUserQuestion
disable-model-invocation: true
---

# /quenching-components-align — typed shortcut

Typed shortcut to the `align` flow of [/quenching-components-components](.agents/quenching/commands/components/components.md).
Input: `$ARGUMENTS`.

```bash
.agents/quenching/bin/cq components read .agents/quenching/assets/references/components-flows/align.md
```
Read the flow whole, once, and follow it from its own `## Workflow` with `$ARGUMENTS` as its input:
its steps, `Done when:` lines and invariants bind this run as they would the flow itself.
**Done when:** the flow ran to its own `Done when:`, or stopped on its own stop condition.
