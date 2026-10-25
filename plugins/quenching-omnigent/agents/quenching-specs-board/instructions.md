---
allowed-tools: Bash(cq:*)
---

<!-- GENERATED FROM plugins/quenching/commands/specs/board.md -->

<!-- OMNIGENT RUNTIME START -->
## Omnigent runtime

This bundle runs on whatever harness and model the caller passes (`omnigent run --harness X --model Y`); it pins neither and names no vendor CLI. Delegate only through Omnigent's own session tools, and only when this bundle's `config.yaml` sets `spawn: true`; protocol copies of the subagents live under `~/.omnigent/quenching/agents/`. Source model tiers and effort are not switches: a declared tier or effort below is a preference to report. Token usage comes from host telemetry when it exists, otherwise it is `not measured`; `cq components session cost` and `context` read no Omnigent log and refuse (exit 2, unmeasured). A tool the permission policy denies stays denied: report it, never route around it. If delegation is unavailable, report the limitation; never replace a required independent verification with self-review.

<!-- OMNIGENT RUNTIME END -->


# quenching-specs-board — start the local spec portal

**Input**: `$ARGUMENTS` — optional `--read-only` and `--port N`, passed through unchanged.

A launcher. The server, its token and its security rules live in `cq specs serve`; do not restate
them.

## Workflow

### 1. Start the server
Resolve `cq` per [align/tool-resolution.md](~/.omnigent/quenching/references/align/tool-resolution.md)
§Resolving the tool; branch on the exit code. Run `cq specs serve --json $ARGUMENTS` with
`run_in_background: true`, then read its first output line.
**Done when:** the first line is the JSON with `url`, or a refusal with its `code` is reported.

### 2. Print the URL
Print the `url` as given, with its token, and whether the portal is read-write or read-only and why.
Say that Ctrl-C or stopping the background task ends it, and that execution stays in Omnigent
(`quenching-specs-execute <id>`).
**Done when:** the URL and its mode are shown.
