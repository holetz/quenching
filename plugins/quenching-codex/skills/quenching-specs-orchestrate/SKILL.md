---
name: quenching-specs-orchestrate
description: "Run an epic or a list of specs through the orchestrator agent. Use for \"orchestrate this epic\", \"run these specs in waves\". Not for: ONE spec → quenching-specs-execute; ranking → quenching-specs-triage; rounds → quenching-specs-autopilot."
---

<!-- GENERATED FROM plugins/quenching/commands/specs/orchestrate.md -->

<!-- CODEX RUNTIME START -->
## Codex runtime

Use Codex host sub-agents only. Never launch Claude CLI, request Claude models, or fall back to Claude during a Codex run. The Claude source may separately delegate development to Codex. Read each named agent protocol and pass its role, prohibitions, model and effort to the host's spawn-agent tool; protocol files are not automatically registered agent types. Use host messaging, completion notifications and interrupt tools for lifecycle management. If delegation is unavailable, report the limitation; do not silently replace required independent verification with self-review.

Tier mapping: opus → `gpt-6-astra`; sonnet → `gpt-6.1-sol`; haiku → `gpt-6-luna`. Preserve declared effort. Pass model explicitly; when the host requires a fresh context for model overrides, use that mode and include the necessary brief and protocol. Never use gpt-6-luna for product code or import-memory classification/executor roles. Report tokens per model and role only when host telemetry provides them; otherwise `not measured`. Claude session logs and `cq components session cost` do not measure this Codex run.

<!-- CODEX RUNTIME END -->


# quenching-specs-orchestrate — conduct an epic or a queue

**Input**: `$ARGUMENTS` — an epic id or a list of spec ids, and optionally `--autonomous`. Empty or ambiguous → run
`cq specs list --json` and ask which on a decision sheet ([questions.md](../../references/specs-develop/questions.md) §The four shared mechanics §1).

This command is a launcher. The protocol (waves, routing, budgets, acceptance, audit) lives in the
`orchestrator` agent definition, `../../agents/orchestrator.md`; do not restate it.

## Workflow

### 1. Resolve the set
Resolve `cq` per [align/tool-resolution.md](../../references/align/tool-resolution.md)
§Resolving the tool; branch on the exit code. Confirm each id exists with `cq specs show --spec <id> --json`.
**Done when:** the epic id or the list of spec ids is verified to exist.

### 2. Check who can run alone
Read each spec's metadata with `cq specs status --spec <id> --json`: `complexity` comes from
`records.priority.complexity` and `approved` from `records.approved`. Split the set from these
`status` payloads: **runs alone** is a spec with `approved` recorded or
`complexity: low`; **needs a human** is `medium` or above with no `approved`. Nothing needs a
human → go to step 3. Otherwise ask once on a decision sheet, naming the specs on each side:

- **Develop now** — run `quenching-specs-develop <id>` in this session, one spec after another,
  for the specs that need a human, then launch everything. A develop of a `medium` spec costs about
  40k tokens of this session (its body and references alone are about 17k), so this is offered
  only for **two specs or fewer**; for more, end the run by listing one
  `quenching-specs-develop <id>` line per spec and `quenching-specs-orchestrate` again after.
- **Launch the independent subset** — only the specs that run alone and depend on none of the
  ones that need a human.
- **Force it** — `--autonomous`: every spec runs, and the approval is stamped
  `by=orchestrator-forced`, never `by=human`.

`--autonomous` already given → skip the question. **Done when:** the set to launch is fixed.

### 3. Launch the orchestrator
Start the `quenching:orchestrator` agent with a prompt of at most 1,500 characters: the epic id or
the spec ids, the base branch, and the word `autonomous` when it was forced. Pass nothing else; it
carries its own protocol, and without `autonomous` it blocks a spec that still needs approval.
**Done when:** the orchestrator has returned its fixed report.

### 4. Relay
Show its per-spec blocks and totals line unchanged. A spec in state `blocked`, `failed` or
`continue` is named with its note and left for the human; never retry it here.
**Done when:** the report is shown and every non-`done` spec is named.
