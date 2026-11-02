---
description: >-
  Capture or create a spec. Use for "convert to a spec", "add to the backlog", "create a spec". Not for: refining → /quenching-specs:specs:develop; executing → /quenching-specs:specs:execute.
argument-hint: [what to capture, a plan path, or a plan from this session]
allowed-tools: Bash(cq:*), Bash(cq.cmd:*), Read, Grep, Glob, Bash(python3:*), Bash(py:*), AskUserQuestion, Skill
disable-model-invocation: true
---

# /quenching-specs:specs:create — typed shortcut

Typed shortcut to the `create` flow of [/quenching-specs:specs:specs](${CLAUDE_PLUGIN_ROOT}/commands/specs/specs.md).
Input: `$ARGUMENTS`.

```bash
.agents/quenching/bin/cq components read ${CLAUDE_PLUGIN_ROOT}/assets/references/specs-flows/create.md
```
Read the flow whole, once, and follow it from its own `## Workflow` with `$ARGUMENTS` as its input:
its steps, `Done when:` lines and invariants bind this run as they would the flow itself.
**Done when:** the flow ran to its own `Done when:`, or stopped on its own stop condition.
