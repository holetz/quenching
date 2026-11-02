---
description: >-
  Run an epic or a list of specs through the orchestrator agent. Use for "orchestrate this epic", "run these specs in waves". Not for: ONE spec → /quenching-specs:specs:execute; ranking → /quenching-specs:specs:triage; rounds → /quenching-specs:specs:autopilot.
argument-hint: [composite-id | spec-id ...] [--autonomous]
allowed-tools: Bash(cq:*), Bash(cq.cmd:*), Read, Agent, Task
---

# /quenching-specs:specs:orchestrate — typed shortcut

Typed shortcut to the `orchestrate` flow of [/quenching-specs:specs:specs](${CLAUDE_PLUGIN_ROOT}/commands/specs/specs.md).
Input: `$ARGUMENTS`.

```bash
.agents/quenching/bin/cq components read ${CLAUDE_PLUGIN_ROOT}/assets/references/specs-flows/orchestrate.md
```
Read the flow whole, once, and follow it from its own `## Workflow` with `$ARGUMENTS` as its input:
its steps, `Done when:` lines and invariants bind this run as they would the flow itself.
**Done when:** the flow ran to its own `Done when:`, or stopped on its own stop condition.
