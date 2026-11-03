---
description: "Push the branch and open a PR on GitHub or Azure DevOps against the resolved base. Use for \"open a PR\", \"create a pull request\", \"submit this for review\". Not for: merging → /quenching-git-merge."
argument-hint: "[id-or-title] [remote:<name>]"
allowed-tools: Bash(.agents/quenching/bin/cq git base:*), Bash(.agents/quenching/bin/cq git conventions:*), Bash(.agents/quenching/bin/cq git state:*), Bash(.agents/quenching/bin/cq git push:*), Bash(.agents/quenching/bin/cq git pr create:*), Bash(.agents/quenching/bin/cq git pr probe:*), Bash(.agents/quenching/bin/cq git pr record:*), Bash(.agents/quenching/bin/cq specs config:*), Bash(.agents/quenching/bin/cq specs status:*), Bash(.agents/quenching/bin/cq specs show:*), Bash(.agents/quenching/bin/cq components read:*), Bash(gh repo view:*), Read, AskUserQuestion
disable-model-invocation: true
---

# /quenching-git-pr-create — typed shortcut

Typed shortcut to the `pr-create` flow of [/quenching-git-git](.agents/quenching/commands/git/git.md).
Input: `$ARGUMENTS`.

```bash
.agents/quenching/bin/cq components read .agents/quenching/assets/references/git-flows/pr-create.md
```
Read the flow whole, once, and follow it from its own `## Workflow` with `$ARGUMENTS` as its input:
its steps, `Done when:` lines and invariants bind this run as they would the flow itself.
**Done when:** the flow ran to its own `Done when:`, or stopped on its own stop condition.
