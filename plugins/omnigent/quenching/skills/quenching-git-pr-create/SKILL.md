---
name: quenching-git-pr-create
description: "Push the branch and open a PR on GitHub or Azure DevOps against the resolved base. Use for \"open a PR\", \"create a pull request\", \"submit this for review\". Not for: merging → quenching-git-merge."
allowed-tools: "Bash(cq git base:*), Bash(cq git conventions:*), Bash(cq git state:*), Bash(cq git push:*), Bash(cq git pr create:*), Bash(cq git pr probe:*), Bash(cq git pr record:*), Bash(cq specs config:*), Bash(cq specs status:*), Bash(cq specs show:*), Bash(cq components read:*), Bash(gh repo view:*), Read, AskUserQuestion"
---

<!-- GENERATED FROM plugins/quenching/commands/git/pr/create.md -->

<!-- OMNIGENT RUNTIME START -->
## Omnigent runtime

This runs inside the `quenching` operator agent on whatever model the server's policy selects; it pins none and names no vendor CLI. The bundle carries no payload: read a reference through the `quenching` MCP server's resources (`quenching://references/<path>`), and prefer its tools (`<pillar>_<verb>`) to a shell `cq`, which resolves only where a local install sits under `$QUENCHING_OMNIGENT_ROOT`. Delegate only to the operator's declared sub-agents. Source model tiers and effort are not switches: a declared tier or effort below is a preference to report. Token usage comes from host telemetry when it exists, otherwise it is `not measured`. A tool the permission policy denies stays denied: report it, never route around it. If delegation is unavailable, report the limitation; never replace a required independent verification with self-review.

<!-- OMNIGENT RUNTIME END -->


# quenching-git-pr-create — typed shortcut

Typed shortcut to the `pr-create` flow of [quenching-git-git](~/.omnigent/quenching/commands/git/git.md).
Input: `$ARGUMENTS`.

```bash
# Read the quenching MCP resource: quenching://references/git-flows/pr-create.md
```
Read the flow whole, once, and follow it from its own `## Workflow` with `$ARGUMENTS` as its input:
its steps, `Done when:` lines and invariants bind this run as they would the flow itself.
**Done when:** the flow ran to its own `Done when:`, or stopped on its own stop condition.
