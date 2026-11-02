---
description: "Close ONE spec out: review the branch, write knowledge, archive, prove the gate, hand off to a PR or merge. Use for \"conclude this spec\", \"close it out\", \"abandon this spec\". Not for: building → /quenching-specs-execute."
argument-hint: "[id] [--outcome done|abandoned]"
allowed-tools: Bash(.agents/quenching/bin/cq:*), Bash(.agents/quenching/bin/cq.cmd:*), Bash, Read, Glob, Grep, Write, Edit, AskUserQuestion, Skill
disable-model-invocation: true
---

# /quenching-specs-conclude — typed shortcut

Typed shortcut to the `conclude` flow of [/quenching-specs-specs](.agents/quenching/commands/specs/specs.md).
Input: `$ARGUMENTS`.

**Why `Bash` is unrestricted here.** The flow runs the verification, `.agents/quenching/bin/cq specs` and Git commands resolved from the live spec; this shortcut grants what the flow was granted.

```bash
.agents/quenching/bin/cq components read .agents/quenching/assets/references/specs-flows/conclude.md
```
Read the flow whole, once, and follow it from its own `## Workflow` with `$ARGUMENTS` as its input:
its steps, `Done when:` lines and invariants bind this run as they would the flow itself.
**Done when:** the flow ran to its own `Done when:`, or stopped on its own stop condition.
