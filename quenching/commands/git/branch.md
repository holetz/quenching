---
description: >-
  Take isolation for a piece of work: a worktree by default, unasked, stamped; a plain branch only when the human asks. Use for "isolate this work", "cut a branch for this", "take a worktree". Not for: pruning → /quenching-git-cleanup.
argument-hint: [id-or-branch-name]
allowed-tools: Bash(cq git base:*), Bash(cq git conventions:*), Bash(cq git specs:*), Bash(cq git state:*), Bash(cq git worktree add:*), Bash(cq specs config:*), Bash(cq specs status:*), Bash(cq components read:*), Read, AskUserQuestion
disable-model-invocation: true
---

# /quenching-git-branch — typed shortcut

Typed shortcut to the `branch` flow of [/quenching-git-git](.agents/quenching/commands/git/git.md).
Input: `$ARGUMENTS`.

```bash
.agents/quenching/bin/cq components read .agents/quenching/assets/references/git-flows/branch.md
```
Read the flow whole, once, and follow it from its own `## Workflow` with `$ARGUMENTS` as its input:
its steps, `Done when:` lines and invariants bind this run as they would the flow itself.
**Done when:** the flow ran to its own `Done when:`, or stopped on its own stop condition.
