---
description: "Commit what is already staged under the repo's commit convention. Use for \"commit this\", \"make a commit\", \"wrap this up in a commit\". Not for: staging, merging or pushing → /quenching-git-merge."
argument-hint: "[subject]"
allowed-tools: Bash(.agents/quenching/bin/cq git commit:*), Bash(.agents/quenching/bin/cq git conventions:*), Bash(.agents/quenching/bin/cq git specs:*), Bash(.agents/quenching/bin/cq git state:*), Bash(.agents/quenching/bin/cq specs next:*), Bash(.agents/quenching/bin/cq components read:*), Read
disable-model-invocation: true
hooks: 
PreToolUse: 
- matcher: Bash
- type: command
command: test -f "${CLAUDE_PLUGIN_ROOT}/assets/hooks/warn-git-add-all.sh" || exit 0; bash "${CLAUDE_PLUGIN_ROOT}/assets/hooks/warn-git-add-all.sh"
timeout: 5
---

# /quenching-git-commit — typed shortcut

Typed shortcut to the `commit` flow of [/quenching-git-git](.agents/quenching/commands/git/git.md).
Input: `$ARGUMENTS`.

```bash
.agents/quenching/bin/cq components read .agents/quenching/assets/references/git-flows/commit.md
```
Read the flow whole, once, and follow it from its own `## Workflow` with `$ARGUMENTS` as its input:
its steps, `Done when:` lines and invariants bind this run as they would the flow itself.
**Done when:** the flow ran to its own `Done when:`, or stopped on its own stop condition.
