---
description: "Capture or create a spec. Use for \"convert to a spec\", \"add to the backlog\", \"create a spec\". Not for: refining → /quenching-specs-develop; executing → /quenching-specs-execute."
argument-hint: "[what to capture, a plan path, or a plan from this session]"
allowed-tools: Bash(.agents/quenching/bin/cq:*), Bash(.agents/quenching/bin/cq.cmd:*), Read, Grep, Glob, Bash(python3:*), Bash(py:*), AskUserQuestion, Skill
disable-model-invocation: true
---

# /quenching-specs-create — typed shortcut

Typed shortcut to the `create` flow of [/quenching-specs-specs](.agents/quenching/commands/specs/specs.md).
Input: `$ARGUMENTS`.

```bash
.agents/quenching/bin/cq components read .agents/quenching/assets/references/specs-flows/create.md
```
Read the flow whole, once, and follow it from its own `## Workflow` with `$ARGUMENTS` as its input:
its steps, `Done when:` lines and invariants bind this run as they would the flow itself.
**Done when:** the flow ran to its own `Done when:`, or stopped on its own stop condition.
