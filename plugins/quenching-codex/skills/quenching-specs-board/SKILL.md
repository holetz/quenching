---
name: quenching-specs-board
description: "Open the local spec portal: board, ranking and detail in the browser over the same backend. Use for \"open the spec board\", \"show the specs visually\". Not for: ranking by chat → quenching-specs-triage; reading → quenching-specs-status."
---

<!-- GENERATED FROM plugins/quenching/commands/specs/board.md -->

<!-- CODEX RUNTIME START -->
## Codex runtime

Use Codex host sub-agents only. Never launch Claude CLI, request Claude models, or fall back to Claude during a Codex run. The Claude source may separately delegate development to Codex. Read each named agent protocol and pass its role, prohibitions, model and effort to the host's spawn-agent tool; protocol files are not automatically registered agent types. Use host messaging, completion notifications and interrupt tools for lifecycle management. If delegation is unavailable, report the limitation; do not silently replace required independent verification with self-review.

Tier mapping: opus → `gpt-6-astra`; sonnet → `gpt-6.1-sol`; haiku → `gpt-6-luna`. Preserve declared effort. Pass model explicitly; when the host requires a fresh context for model overrides, use that mode and include the necessary brief and protocol. Never use gpt-6-luna for product code or import-memory classification/executor roles. Report tokens per model and role only when host telemetry provides them; otherwise `not measured`. Claude session logs and `cq components session cost` do not measure this Codex run.

<!-- CODEX RUNTIME END -->


# quenching-specs-board — start the local spec portal

**Input**: `$ARGUMENTS` — optional `--read-only` and `--port N`, passed through unchanged.

A launcher. The server, its token and its security rules live in `cq specs serve`; do not restate
them.

## Workflow

### 1. Start the server
Resolve `cq` per [align/tool-resolution.md](../../references/align/tool-resolution.md)
§Resolving the tool; branch on the exit code. Run `cq specs serve --json $ARGUMENTS` with
`run_in_background: true`, then read its first output line.
**Done when:** the first line is the JSON with `url`, or a refusal with its `code` is reported.

### 2. Print the URL
Print the `url` as given, with its token, and whether the portal is read-write or read-only and why.
Say that Ctrl-C or stopping the background task ends it, and that execution stays in Codex
(`quenching-specs-execute <id>`).
**Done when:** the URL and its mode are shown.
