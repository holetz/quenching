---
description: >-
  Run an epic or a list of specs through the orchestrator agent. Use for "orchestrate this epic", "run these specs in waves". Not for: ONE spec → /quenching:specs:execute; ranking → /quenching:specs:triage.
argument-hint: [epic-id | spec-id ...]
allowed-tools: Bash(cq:*), Read, Agent, Task
---

# /quenching:specs:orchestrate — conduct an epic or a queue

**Input**: `$ARGUMENTS` — an epic id or a list of spec ids. Empty or ambiguous → run
`cq specs list --json` and ask which with **AskUserQuestion**.

This command is a launcher. The protocol (waves, routing, budgets, acceptance, audit) lives in the
`orchestrator` agent definition, `plugins/quenching/agents/orchestrator.md`; do not restate it.

## Workflow

### 1. Resolve the set
Resolve `cq` per [align/tool-resolution.md](${CLAUDE_PLUGIN_ROOT}/assets/references/align/tool-resolution.md)
§Resolving the tool; branch on the exit code. Confirm each id exists with `cq specs show --spec <id> --json`.
**Done when:** the epic id or the list of spec ids is verified to exist.

### 2. Launch the orchestrator
Start the `quenching:orchestrator` agent with a prompt of at most 1,500 characters: the epic id or
the spec ids, and the base branch. Pass nothing else; it carries its own protocol.
**Done when:** the orchestrator has returned its fixed report.

### 3. Relay
Show its per-spec blocks and totals line unchanged. A spec in state `blocked`, `failed` or
`continue` is named with its note and left for the human; never retry it here.
**Done when:** the report is shown and every non-`done` spec is named.
