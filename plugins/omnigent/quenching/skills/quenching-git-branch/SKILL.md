---
name: quenching-git-branch
description: "Take isolation for a piece of work: a worktree by default, unasked, stamped; a plain branch only when the human asks. Use for \"isolate this work\", \"cut a branch for this\", \"take a worktree\". Not for: pruning → quenching-git-cleanup."
allowed-tools: "Bash(cq git base:*), Bash(cq git conventions:*), Bash(cq git specs:*), Bash(cq git state:*), Bash(cq git worktree add:*), Bash(cq specs config:*), Bash(cq specs status:*), Bash(cq components read:*), Read, AskUserQuestion"
---

<!-- GENERATED FROM plugins/quenching/commands/git/branch.md -->

<!-- OMNIGENT RUNTIME START -->
## Omnigent runtime

This runs inside the `quenching` operator agent on whatever model the server's policy selects; it pins none and names no vendor CLI. The bundle carries no payload: read a reference through the `quenching` MCP server's resources (`quenching://references/<path>`), and prefer its tools (`<pillar>_<verb>`) to a shell `cq`, which resolves only where a local install sits under `$QUENCHING_OMNIGENT_ROOT`. Delegate only to the operator's declared sub-agents. Source model tiers and effort are not switches: a declared tier or effort below is a preference to report. Token usage comes from host telemetry when it exists, otherwise it is `not measured`. A tool the permission policy denies stays denied: report it, never route around it. If delegation is unavailable, report the limitation; never replace a required independent verification with self-review.

<!-- OMNIGENT RUNTIME END -->


# quenching-git-branch — typed shortcut

Typed shortcut to the `branch` flow of [quenching-git-git](~/.omnigent/quenching/commands/git/git.md).
Input: `$ARGUMENTS`.

```bash
# Read the quenching MCP resource: quenching://references/git-flows/branch.md
```
Read the flow whole, once, and follow it from its own `## Workflow` with `$ARGUMENTS` as its input:
its steps, `Done when:` lines and invariants bind this run as they would the flow itself.
**Done when:** the flow ran to its own `Done when:`, or stopped on its own stop condition.
