---
description: >-
  Rebase the work branch onto the latest base with `--update-refs`. Use for "sync this branch with main", "rebase onto the base", "catch this branch up". Not for: conflicts → the human.
argument-hint: [branch]
allowed-tools: Bash(cq:*), Bash(cq.cmd:*), Bash(git status:*), Bash(git remote get-url:*), Bash(git fetch:*), Bash(git rebase:*), Bash(git for-each-ref:*), Bash(python3:*), Read
disable-model-invocation: true
---

# /quenching-specs:git:sync — typed shortcut

Typed shortcut to the `sync` flow of [/quenching-specs:git:git](${CLAUDE_PLUGIN_ROOT}/commands/git/git.md).
Input: `$ARGUMENTS`.

```bash
cq components read ${CLAUDE_PLUGIN_ROOT}/assets/references/git-flows/sync.md
```
Read the flow whole, once, and follow it from its own `## Workflow` with `$ARGUMENTS` as its input:
its steps, `Done when:` lines and invariants bind this run as they would the flow itself.
**Done when:** the flow ran to its own `Done when:`, or stopped on its own stop condition.
