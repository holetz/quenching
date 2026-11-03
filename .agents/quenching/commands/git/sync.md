---
description: "Rebase the work branch onto the latest base with `--update-refs`. Use for \"sync this branch with main\", \"rebase onto the base\", \"catch this branch up\". Not for: conflicts → the human."
argument-hint: "[branch]"
allowed-tools: Bash(.agents/quenching/bin/cq:*), Bash(.agents/quenching/bin/cq.cmd:*), Bash(git status:*), Bash(git remote get-url:*), Bash(git fetch:*), Bash(git rebase:*), Bash(git for-each-ref:*), Bash(python3:*), Read
disable-model-invocation: true
---

# /quenching-git-sync — typed shortcut

Typed shortcut to the `sync` flow of [/quenching-git-git](.agents/quenching/commands/git/git.md).
Input: `$ARGUMENTS`.

```bash
.agents/quenching/bin/cq components read .agents/quenching/assets/references/git-flows/sync.md
```
Read the flow whole, once, and follow it from its own `## Workflow` with `$ARGUMENTS` as its input:
its steps, `Done when:` lines and invariants bind this run as they would the flow itself.
**Done when:** the flow ran to its own `Done when:`, or stopped on its own stop condition.
