---
description: >-
  Read a PR's checks, reviews, threads and mergeability, read-only. Use for "check the PR status", "show the review state". Not for: opening → /quenching-specs:git:pr:create; threads → /quenching-specs:git:pr:review; merging → /quenching-specs:git:merge.
argument-hint: [spec-id|pr-number|pr-url]
allowed-tools: Bash(cq:*), Bash(cq.cmd:*), Bash(python3:*), Bash(git remote get-url:*), Bash(git branch:*), Bash(gh repo view:*), Bash(gh pr view:*), Bash(gh api graphql:*), Bash(az repos pr:*), Bash(az devops invoke:*), Read
disable-model-invocation: true
---

# /quenching-specs:git:pr:status — typed shortcut

Typed shortcut to the `pr-status` flow of [/quenching-specs:git:git](${CLAUDE_PLUGIN_ROOT}/commands/git/git.md).
Input: `$ARGUMENTS`.

```bash
cq components read ${CLAUDE_PLUGIN_ROOT}/assets/references/git-flows/pr-status.md
```
Read the flow whole, once, and follow it from its own `## Workflow` with `$ARGUMENTS` as its input:
its steps, `Done when:` lines and invariants bind this run as they would the flow itself.
**Done when:** the flow ran to its own `Done when:`, or stopped on its own stop condition.
