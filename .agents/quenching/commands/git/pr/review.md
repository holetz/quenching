---
description: "Fetch a PR's unresolved review threads and address each on the human's confirmation. Use for \"resolve PR comments\", \"address the review feedback\". Not for: opening a PR → /quenching-git-pr-create."
argument-hint: "[pr-number-or-id]"
allowed-tools: Bash(.agents/quenching/bin/cq:*), Bash(.agents/quenching/bin/cq.cmd:*), Bash(gh pr view:*), Bash(gh repo view:*), Bash(gh api graphql:*), Bash(az repos pr:*), Bash(az devops invoke:*), Bash(az rest:*), Bash(git branch:*), Bash(git remote get-url:*), Bash(git add:*), Bash(python3:*), Read, Edit, AskUserQuestion, Skill
disable-model-invocation: true
---

# /quenching-git-pr-review — typed shortcut

Typed shortcut to the `pr-review` flow of [/quenching-git-git](.agents/quenching/commands/git/git.md).
Input: `$ARGUMENTS`.

```bash
.agents/quenching/bin/cq components read .agents/quenching/assets/references/git-flows/pr-review.md
```
Read the flow whole, once, and follow it from its own `## Workflow` with `$ARGUMENTS` as its input:
its steps, `Done when:` lines and invariants bind this run as they would the flow itself.
**Done when:** the flow ran to its own `Done when:`, or stopped on its own stop condition.
