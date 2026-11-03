---
description: >-
  Commit what is already staged under the repo's commit convention. Use for "commit this", "make a commit", "wrap this up in a commit". Not for: staging, merging or pushing → /quenching-specs:git:merge.
argument-hint: [subject]
allowed-tools: Bash(cq git commit:*), Bash(cq git conventions:*), Bash(cq git specs:*), Bash(cq git state:*), Bash(cq specs next:*), Bash(cq components read:*), Read
disable-model-invocation: true
hooks:
  PreToolUse:
    - matcher: Bash
      hooks:
        - type: command
          command: test -f "${CLAUDE_PLUGIN_ROOT}/assets/hooks/warn-git-add-all.sh" || exit 0; bash "${CLAUDE_PLUGIN_ROOT}/assets/hooks/warn-git-add-all.sh"
          timeout: 5
---

# /quenching-specs:git:commit — typed shortcut

Typed shortcut to the `commit` flow of [/quenching-specs:git:git](${CLAUDE_PLUGIN_ROOT}/commands/git/git.md).
Input: `$ARGUMENTS`.

```bash
cq components read ${CLAUDE_PLUGIN_ROOT}/assets/references/git-flows/commit.md
```
Read the flow whole, once, and follow it from its own `## Workflow` with `$ARGUMENTS` as its input:
its steps, `Done when:` lines and invariants bind this run as they would the flow itself.
**Done when:** the flow ran to its own `Done when:`, or stopped on its own stop condition.
