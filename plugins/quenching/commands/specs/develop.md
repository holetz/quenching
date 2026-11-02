---
description: >-
  Develop an existing spec to ready, argue with it, approve it. Use for "develop this spec", "refine the spec", "approve this spec". Not for: new specs → /quenching-specs:specs:create; building → /quenching-specs:specs:execute.
argument-hint: [id-or-description]
allowed-tools: Bash(cq:*), Bash(cq.cmd:*), Read, Grep, Glob, Edit, Bash(python3:*), Bash(py:*), AskUserQuestion, Task
model: opus
---

# /quenching-specs:specs:develop — typed shortcut

Typed shortcut to the `develop` flow of [/quenching-specs:specs:specs](${CLAUDE_PLUGIN_ROOT}/commands/specs/specs.md).
Input: `$ARGUMENTS`.

```bash
.agents/quenching/bin/cq components read ${CLAUDE_PLUGIN_ROOT}/assets/references/specs-flows/develop.md
```
Read the flow whole, once, and follow it from its own `## Workflow` with `$ARGUMENTS` as its input:
its steps, `Done when:` lines and invariants bind this run as they would the flow itself.
**Done when:** the flow ran to its own `Done when:`, or stopped on its own stop condition.
