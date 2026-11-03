---
description: >-
  Fetch a PR's unresolved review threads and address each on the human's confirmation. Use for "resolve PR comments", "address the review feedback". Not for: opening a PR → /quenching-specs:git:pr:create.
argument-hint: [pr-number-or-id]
allowed-tools: Bash(cq:*), Bash(cq.cmd:*), Bash(gh pr view:*), Bash(gh repo view:*), Bash(gh api graphql:*), Bash(az repos pr:*), Bash(az devops invoke:*), Bash(az rest:*), Bash(git branch:*), Bash(git remote get-url:*), Bash(git add:*), Bash(python3:*), Read, Edit, AskUserQuestion, Skill
disable-model-invocation: true
---

# /quenching-specs:git:pr:review — typed shortcut

Typed shortcut to the `pr-review` flow of [/quenching-specs:git:git](${CLAUDE_PLUGIN_ROOT}/commands/git/git.md).
Input: `$ARGUMENTS`.

```bash
cq components read ${CLAUDE_PLUGIN_ROOT}/assets/references/git-flows/pr-review.md
```
Read the flow whole, once, and follow it from its own `## Workflow` with `$ARGUMENTS` as its input:
its steps, `Done when:` lines and invariants bind this run as they would the flow itself.
**Done when:** the flow ran to its own `Done when:`, or stopped on its own stop condition.
