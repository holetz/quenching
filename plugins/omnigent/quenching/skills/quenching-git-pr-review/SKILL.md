---
name: quenching-git-pr-review
description: "Fetch a PR's unresolved review threads and address each on the human's confirmation. Use for \"resolve PR comments\", \"address the review feedback\". Not for: opening a PR → quenching-git-pr-create."
allowed-tools: "Bash(cq:*), Bash(cq.cmd:*), Bash(gh pr view:*), Bash(gh repo view:*), Bash(gh api graphql:*), Bash(az repos pr:*), Bash(az devops invoke:*), Bash(az rest:*), Bash(git branch:*), Bash(git remote get-url:*), Bash(git add:*), Bash(python3:*), Read, Edit, AskUserQuestion, Skill"
---

<!-- GENERATED FROM plugins/quenching/commands/git/pr/review.md -->

<!-- OMNIGENT RUNTIME START -->
## Omnigent runtime

This runs inside the `quenching` operator agent on whatever model the server's policy selects; it pins none and names no vendor CLI. The bundle carries no payload: read a reference through the `quenching` MCP server's resources (`quenching://references/<path>`), and prefer its tools (`<pillar>_<verb>`) to a shell `cq`, which resolves only where a local install sits under `$QUENCHING_OMNIGENT_ROOT`. Delegate only to the operator's declared sub-agents. Source model tiers and effort are not switches: a declared tier or effort below is a preference to report. Token usage comes from host telemetry when it exists, otherwise it is `not measured`. A tool the permission policy denies stays denied: report it, never route around it. If delegation is unavailable, report the limitation; never replace a required independent verification with self-review.

<!-- OMNIGENT RUNTIME END -->


# quenching-git-pr-review — typed shortcut

Typed shortcut to the `pr-review` flow of [quenching-git-git](~/.omnigent/quenching/commands/git/git.md).
Input: `$ARGUMENTS`.

```bash
# Read the quenching MCP resource: quenching://references/git-flows/pr-review.md
```
Read the flow whole, once, and follow it from its own `## Workflow` with `$ARGUMENTS` as its input:
its steps, `Done when:` lines and invariants bind this run as they would the flow itself.
**Done when:** the flow ran to its own `Done when:`, or stopped on its own stop condition.
