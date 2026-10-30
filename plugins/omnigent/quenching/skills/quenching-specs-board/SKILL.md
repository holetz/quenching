---
name: quenching-specs-board
description: "Open the local spec portal: board, ranking and detail in the browser over the same backend. Use for \"open the spec board\", \"show the specs visually\". Not for: ranking by chat → quenching-specs-triage; reading → quenching-specs-status."
allowed-tools: "Bash(cq:*), Bash(cq.cmd:*)"
---

<!-- GENERATED FROM plugins/quenching/commands/specs/board.md -->

<!-- OMNIGENT RUNTIME START -->
## Omnigent runtime

This runs inside the `quenching` operator agent on whatever model the server's policy selects; it pins none and names no vendor CLI. The bundle carries no payload: read a reference through the `quenching` MCP server's resources (`quenching://references/<path>`), and prefer its tools (`<pillar>_<verb>`) to a shell `cq`, which resolves only where a local install sits under `$QUENCHING_OMNIGENT_ROOT`. Delegate only to the operator's declared sub-agents. Source model tiers and effort are not switches: a declared tier or effort below is a preference to report. Token usage comes from host telemetry when it exists, otherwise it is `not measured`. A tool the permission policy denies stays denied: report it, never route around it. If delegation is unavailable, report the limitation; never replace a required independent verification with self-review.

<!-- OMNIGENT RUNTIME END -->


# quenching-specs-board — start the local spec portal

**Input**: `$ARGUMENTS` — optional `--read-only` and `--port N`, passed through unchanged.

A launcher. The server, its token and its security rules live in `cq specs serve`; do not restate
them.

## Workflow

### 1. Start the server
Resolve `cq` per [align/tool-resolution.md](quenching://references/align/tool-resolution.md)
§Resolving the tool; branch on the exit code. Run `cq specs serve --json $ARGUMENTS` with
`run_in_background: true`, then read its first output line.
**Done when:** the first line is the JSON with `url`, or a refusal with its `code` is reported.

### 2. Print the URL
Print the `url` as given, with its token, and whether the portal is read-write or read-only and why.
Say that Ctrl-C or stopping the background task ends it, and that execution stays in Omnigent
(`quenching-specs-execute <id>`).
**Done when:** the URL and its mode are shown.
