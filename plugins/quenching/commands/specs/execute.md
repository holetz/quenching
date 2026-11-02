---
description: >-
  Build ONE spec task by task: write, verify, self-review, tick, commit. Use for "execute this spec", "build it", "implement the tasks", "continue building". Not for: sharpening → /quenching-specs:specs:develop; closing → /quenching-specs:specs:conclude.
argument-hint: [id]
allowed-tools: Bash(cq:*), Bash(cq.cmd:*), Bash, Read, Glob, Grep, Write, Edit, AskUserQuestion, Task, Skill
disable-model-invocation: true
---

# /quenching-specs:specs:execute — typed shortcut

Typed shortcut to the `execute` flow of [/quenching-specs:specs:specs](${CLAUDE_PLUGIN_ROOT}/commands/specs/specs.md).
Input: `$ARGUMENTS`.

**Why `Bash` is unrestricted here.** The flow runs the verification, `cq specs` and Git commands resolved from the live spec; this shortcut grants what the flow was granted.

```bash
.agents/quenching/bin/cq components read ${CLAUDE_PLUGIN_ROOT}/assets/references/specs-flows/execute.md
```
Read the flow whole, once, and follow it from its own `## Workflow` with `$ARGUMENTS` as its input:
its steps, `Done when:` lines and invariants bind this run as they would the flow itself.
**Done when:** the flow ran to its own `Done when:`, or stopped on its own stop condition.
