---
description: "Run an epic or a list of specs through the orchestrator agent. Use for \"orchestrate this epic\", \"run these specs in waves\". Not for: ONE spec → quenching-specs-execute; ranking → quenching-specs-triage; rounds → quenching-specs-autopilot."
---

<!-- GENERATED FROM plugins/quenching/commands/specs/orchestrate.md -->

<!-- OPENCODE RUNTIME START -->
## OpenCode runtime

Delegate only through OpenCode's task tool, to the registered subagents named `quenching-<agent>` (protocol copies live under `~/.opencode/quenching/agents/`). Never launch the Claude CLI and never request a Claude model during an OpenCode run. Source model tiers are not pinned here: every command and subagent runs on the model the OpenCode session configures; a declared tier or effort below is a preference to report, not a switch. Token usage comes from host telemetry when it exists, otherwise it is `not measured`; `cq components session cost` reads no OpenCode log and refuses (exit 2, unmeasured), while `cq components session context` and `cache` read the OpenCode database. If delegation is unavailable, report the limitation; never replace a required independent verification with self-review.

<!-- OPENCODE RUNTIME END -->


# quenching-specs-orchestrate — typed shortcut

Typed shortcut to the `orchestrate` flow of [quenching-specs-specs](~/.opencode/quenching/commands/specs/specs.md).
Input: `$ARGUMENTS`.

```bash
cq() { python3 "${QUENCHING_OPENCODE_ROOT:-$HOME/.opencode/quenching}/scripts/cq" "$@"; }
cq components read ~/.opencode/quenching/references/specs-flows/orchestrate.md
```
Read the flow whole, once, and follow it from its own `## Workflow` with `$ARGUMENTS` as its input:
its steps, `Done when:` lines and invariants bind this run as they would the flow itself.
**Done when:** the flow ran to its own `Done when:`, or stopped on its own stop condition.
