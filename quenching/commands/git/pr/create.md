---
description: >-
  Push the branch and open a PR on GitHub or Azure DevOps against the resolved base. Use for "open a PR", "create a pull request", "submit this for review". Not for: merging → /quenching-specs:git:merge.
argument-hint: [id-or-title] [remote:<name>]
allowed-tools: Bash(cq git base:*), Bash(cq git conventions:*), Bash(cq git state:*), Bash(cq git push:*), Bash(cq git pr create:*), Bash(cq git pr probe:*), Bash(cq git pr record:*), Bash(cq specs config:*), Bash(cq specs status:*), Bash(cq specs show:*), Bash(cq components read:*), Bash(gh repo view:*), Read, AskUserQuestion
disable-model-invocation: true
---

# /quenching-specs:git:pr:create — typed shortcut

Typed shortcut to the `pr-create` flow of [/quenching-specs:git:git](${CLAUDE_PLUGIN_ROOT}/commands/git/git.md).
Input: `$ARGUMENTS`.

```bash
cq components read ${CLAUDE_PLUGIN_ROOT}/assets/references/git-flows/pr-create.md
```
Read the flow whole, once, and follow it from its own `## Workflow` with `$ARGUMENTS` as its input:
its steps, `Done when:` lines and invariants bind this run as they would the flow itself.
**Done when:** the flow ran to its own `Done when:`, or stopped on its own stop condition.
