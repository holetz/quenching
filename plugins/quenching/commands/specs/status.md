---
description: >-
  Report the specs front and store configuration, read-only. Use for "specs status", "store configuration". Not for: developing or executing → /quenching-specs:specs:develop; ranking → /quenching-specs:specs:triage.
allowed-tools: Bash(cq:*), Bash(cq.cmd:*), Bash(python3:*), Read
disable-model-invocation: true
---

# /quenching-specs:specs:status — typed shortcut

Typed shortcut to the `status` flow of [/quenching-specs:specs:specs](${CLAUDE_PLUGIN_ROOT}/commands/specs/specs.md).
Input: `$ARGUMENTS`.

```bash
.agents/quenching/bin/cq components read ${CLAUDE_PLUGIN_ROOT}/assets/references/specs-flows/status.md
```
Read the flow whole, once, and follow it from its own `## Workflow` with `$ARGUMENTS` as its input:
its steps, `Done when:` lines and invariants bind this run as they would the flow itself.
**Done when:** the flow ran to its own `Done when:`, or stopped on its own stop condition.
