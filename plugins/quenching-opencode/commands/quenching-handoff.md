---
description: "Compact the current conversation into a handoff document for another agent to continue. Use for \"generate a handoff\" or \"prepare a handoff for the next session\". Not for: implementing → the owning command."
---

<!-- GENERATED FROM plugins/quenching/commands/handoff.md -->

<!-- OPENCODE RUNTIME START -->
## OpenCode runtime

Delegate only through OpenCode's task tool, to the registered subagents named `quenching-<agent>` (protocol copies live under `~/.config/opencode/quenching/agents/`). Never launch the Claude CLI and never request a Claude model during an OpenCode run. Source model tiers are not pinned here: every command and subagent runs on the model the OpenCode session configures; a declared tier or effort below is a preference to report, not a switch. Token usage comes from host telemetry when it exists, otherwise it is `not measured`; `cq components session cost` and `context` read no OpenCode log and refuse (exit 2, unmeasured). If delegation is unavailable, report the limitation; never replace a required independent verification with self-review.

<!-- OPENCODE RUNTIME END -->


**Input**: `$ARGUMENTS` (the focus of the next session).

## Workflow

### 1. Fix the next session's focus

Use `$ARGUMENTS` when provided. When it is omitted, use the main unfinished objective in the
current conversation as the focus. **Done when:** the handoff's focus is fixed.

### 2. Create and inspect the destination

Run:

```bash
mktemp -t handoff-XXXXXX.md
```

Read the returned path before writing to it. **Done when:** the destination path is captured and
the newly created file has been read.

### 3. Compose the handoff

Summarize the current conversation. Tailor it to the fixed
focus and include the objective, current status, decisions, completed work, open work, validation
evidence, blockers, and useful next actions. Suggest skills for the next session when they apply.
Reference existing PRDs, plans, ADRs, issues, commits, diffs, or other artifacts by path or URL
instead of duplicating their contents. **Done when:** the draft contains enough context to resume
the work and points to existing artifacts rather than copying them.

### 4. Write and verify

Write the handoff to the inspected temporary path, then read it back. Report the resulting path.
**Done when:** the file exists, is non-empty, and its read-back succeeds.

## Invariants

- Keep the handoff focused on the next session's work.
- Reference durable artifacts instead of duplicating their contents.
- Suggest only skills that are relevant to the recorded next actions.
