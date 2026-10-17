---
name: quenching-handoff
description: "Compact the current conversation into a handoff document for another agent to continue. Use for \"generate a handoff\" or \"prepare a handoff for the next session\". Not for: implementing → the owning command."
---

<!-- GENERATED FROM plugins/quenching/commands/handoff.md -->

<!-- CODEX RUNTIME START -->
## Codex runtime

Use Codex host sub-agents only. Never launch Claude CLI, request Claude models, or fall back to Claude during a Codex run. The Claude source may separately delegate development to Codex. Read each named agent protocol and pass its role, prohibitions, model and effort to the host's spawn-agent tool; protocol files are not automatically registered agent types. Use host messaging, completion notifications and interrupt tools for lifecycle management. If delegation is unavailable, report the limitation; do not silently replace required independent verification with self-review.

Tier mapping: opus → `gpt-6-astra`; sonnet → `gpt-6.1-sol`; haiku → `gpt-6-luna`. Preserve declared effort. Pass model explicitly; when the host requires a fresh context for model overrides, use that mode and include the necessary brief and protocol. Never use gpt-6-luna for product code or import-memory classification/executor roles. Report tokens per model and role only when host telemetry provides them; otherwise `not measured`. Claude session logs and `cq components session cost` do not measure this Codex run.

<!-- CODEX RUNTIME END -->


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
