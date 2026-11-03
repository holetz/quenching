---
name: quenching-git-sync
description: "Rebase the work branch onto the latest base with `--update-refs`. Use for \"sync this branch with main\", \"rebase onto the base\", \"catch this branch up\". Not for: conflicts → the human."
allowed-tools: "Bash(cq:*), Bash(cq.cmd:*), Bash(git status:*), Bash(git remote get-url:*), Bash(git fetch:*), Bash(git rebase:*), Bash(git for-each-ref:*), Bash(python3:*), Read"
---

<!-- GENERATED FROM plugins/quenching/commands/git/sync.md -->

<!-- OMNIGENT RUNTIME START -->
## Omnigent runtime

This runs inside the `quenching` operator agent on whatever model the server's policy selects; it pins none and names no vendor CLI. The bundle carries no payload: read a reference through the `quenching` MCP server's resources (`quenching://references/<path>`), and prefer its tools (`<pillar>_<verb>`) to a shell `cq`, which resolves only where a local install sits under `$QUENCHING_OMNIGENT_ROOT`. Delegate only to the operator's declared sub-agents. Source model tiers and effort are not switches: a declared tier or effort below is a preference to report. Token usage comes from host telemetry when it exists, otherwise it is `not measured`. A tool the permission policy denies stays denied: report it, never route around it. If delegation is unavailable, report the limitation; never replace a required independent verification with self-review.

<!-- OMNIGENT RUNTIME END -->


# quenching-git-sync — typed shortcut

Typed shortcut to the `sync` flow of [quenching-git-git](~/.omnigent/quenching/commands/git/git.md).
Input: `$ARGUMENTS`.

```bash
# Read the quenching MCP resource: quenching://references/git-flows/sync.md
```
Read the flow whole, once, and follow it from its own `## Workflow` with `$ARGUMENTS` as its input:
its steps, `Done when:` lines and invariants bind this run as they would the flow itself.
**Done when:** the flow ran to its own `Done when:`, or stopped on its own stop condition.
