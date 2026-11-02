---
description: >-
  Rank the open specs front into ONE ordered list the human confirms. Use for "triage the specs", "prioritize the front", "which of these first". Not for: building → /quenching-specs:specs:execute.
argument-hint: [optional-id]
allowed-tools: Bash(cq:*), Bash(cq.cmd:*), Read, Grep, Glob, Bash(python3:*), Bash(py:*), AskUserQuestion
disable-model-invocation: true
---

# /quenching-specs:specs:triage — typed shortcut

Typed shortcut to the `triage` flow of [/quenching-specs:specs:specs](${CLAUDE_PLUGIN_ROOT}/commands/specs/specs.md).
Input: `$ARGUMENTS`.

```bash
.agents/quenching/bin/cq components read ${CLAUDE_PLUGIN_ROOT}/assets/references/specs-flows/triage.md
```
Read the flow whole, once, and follow it from its own `## Workflow` with `$ARGUMENTS` as its input:
its steps, `Done when:` lines and invariants bind this run as they would the flow itself.
**Done when:** the flow ran to its own `Done when:`, or stopped on its own stop condition.
