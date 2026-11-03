---
description: "Take isolation for a piece of work: a worktree by default, unasked, stamped; a plain branch only when the human asks. Use for \"isolate this work\", \"cut a branch for this\", \"take a worktree\". Not for: pruning → quenching-git-cleanup."
---

<!-- GENERATED FROM plugins/quenching/commands/git/branch.md -->

<!-- OPENCODE RUNTIME START -->
## OpenCode runtime

Delegate only through OpenCode's task tool, to the registered subagents named `quenching-<agent>` (protocol copies live under `~/.opencode/quenching/agents/`). Never launch the Claude CLI and never request a Claude model during an OpenCode run. Source model tiers are not pinned here: every command and subagent runs on the model the OpenCode session configures; a declared tier or effort below is a preference to report, not a switch. Token usage comes from host telemetry when it exists, otherwise it is `not measured`; `cq components session cost` reads no OpenCode log and refuses (exit 2, unmeasured), while `cq components session context` and `cache` read the OpenCode database. If delegation is unavailable, report the limitation; never replace a required independent verification with self-review.

<!-- OPENCODE RUNTIME END -->


# quenching-git-branch — typed shortcut

Typed shortcut to the `branch` flow of [quenching-git-git](~/.opencode/quenching/commands/git/git.md).
Input: `$ARGUMENTS`.

```bash
cq() { python3 "${QUENCHING_OPENCODE_ROOT:-$HOME/.opencode/quenching}/scripts/cq" "$@"; }
cq components read ~/.opencode/quenching/references/git-flows/branch.md
```
Read the flow whole, once, and follow it from its own `## Workflow` with `$ARGUMENTS` as its input:
its steps, `Done when:` lines and invariants bind this run as they would the flow itself.
**Done when:** the flow ran to its own `Done when:`, or stopped on its own stop condition.
