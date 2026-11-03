---
description: >-
  Merge a branch into its base with one of four strategies, offered to the human. Use for "merge this branch", "land this work". Not for: opening a PR → /quenching-specs:git:pr:create; pruning → /quenching-specs:git:cleanup.
argument-hint: [id-or-branch]
allowed-tools: Bash(cq:*), Bash(cq.cmd:*), Bash(git worktree:*), Bash(git merge:*), Bash(git rebase:*), Bash(git branch:*), Bash(python3:*), Read, AskUserQuestion
disable-model-invocation: true
---

# /quenching-specs:git:merge — typed shortcut

Typed shortcut to the `merge` flow of [/quenching-specs:git:git](${CLAUDE_PLUGIN_ROOT}/commands/git/git.md).
Input: `$ARGUMENTS`.

```bash
cq components read ${CLAUDE_PLUGIN_ROOT}/assets/references/git-flows/merge.md
```
Read the flow whole, once, and follow it from its own `## Workflow` with `$ARGUMENTS` as its input:
its steps, `Done when:` lines and invariants bind this run as they would the flow itself.
**Done when:** the flow ran to its own `Done when:`, or stopped on its own stop condition.
