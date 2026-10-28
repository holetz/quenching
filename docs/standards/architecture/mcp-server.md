---
type: standard
title: The quenching MCP server
description: A closed parser-derived tool catalog over the cq core, three tool classes, bounded reference resources and a stdio launcher packaged with the plugin layout intact
resource: plugins/quenching/assets/bin/quenching/mcp/**, plugins/quenching/assets/bin/quenching/specs/mcp.py, plugins/quenching/pyproject.toml, plugins/quenching/.mcp.json
tags: [architecture, mcp, distribution, tooling]
timestamp: 2026-10-27
audience: both
authority: current
source: spec 2110; protocol, catalog, resources and installed-launcher tests
maintainer: quenching
---

# The quenching MCP server

<!-- rules -->

## One protocol, two mounts

`cq mcp` serves the available pillars and plugin references over stdio as `quenching`.
`cq specs mcp` remains the specs-only mount. Both use `quenching/mcp/server.py` for JSON-RPC,
size guards, elicitation and in-process dispatch; the specs tool names and schemas stay compatible.
The plugin's `.mcp.json` registers `quenching` through its own `assets/bin/cq mcp`.
The `mcp` package belongs to `quenching-specs`, under [plugin-layout.md](plugin-layout.md).

The workspace is the launch cwd or launch-time `--root`. It is never a tool argument.
Each call isolates stdin and captures stdout/stderr, restores cwd and stdin in `finally`, and turns
`SystemExit` into an exit code. A verb without JSON output returns `{ok, exit, text}`.

## Closed catalog, parser-derived arguments

`quenching/mcp/catalog.py` owns the explicit `CATALOG`: each row names a pillar, fixed verb path
and class. Names are `<pillar>_<verb>[_<subverb>]`, replacing hyphens with underscores:
`components_read`, `knowledge_site_source`, `git_pr_create`, `components_session_context`.
Specs keep their existing names, including `specs_section_write` and `specs_record`.
`tools/list` is the authoritative available inventory; an absent pillar contributes no tools.

The schema comes from each pillar's `build_parser()`: flags become booleans, choices become enums,
repeated values become arrays, and positional arguments become properties. Required arguments stay
required. Every schema rejects additional properties. The server owns `--root` and `--json`;
there is no generic argv passthrough. `components` never receives the workspace as `--root`,
because its `--root` names the surface root holding `commands/`; it runs with the workspace as cwd
and finds the nearest `.claude/` from there. A new parser option on a catalogued verb is exposed without
editing the catalog; a new verb requires a new row. Interactive or long-running entry points,
including `specs serve`, `specs mcp`, `portal serve` and `codex implement`, are not catalogued.

| Class | Meaning | MCP annotation |
| --- | --- | --- |
| `read` | Reads the workspace | `readOnlyHint: true` |
| `write` | Can change the workspace or specs store | `readOnlyHint: false`; worktree retire also sets `destructiveHint: true` |
| `external` | Can act outside the machine | `openWorldHint: true`; destructive merge/prune also set `destructiveHint: true` |

Annotations describe capabilities; they grant no permission. The existing specs elicitation gate
still protects `approved`, `reviewed`, `merge`, `outcome` and promotion, so `git_pr_merge`
publishes no `spec` argument: the `merge` record goes through `specs_record`. Only a client acceptance
permits those moves; missing capability, decline or cancel refuses without a write.

## Bounded resources

`quenching://references` indexes the shipped references. A resource
`quenching://references/<path>.md` resolves only inside `assets/references/`, including after
symlink resolution. Documents at or below `DOC_WHOLE` (24,000 characters) can be returned whole;
larger documents return an outline. Repeated `?section=<heading>` parameters select sections
using the same section reader as `components read`. The shared 60,000-character response guard
marks oversized replies as truncated and supplies a narrower-read hint.

The specs resources remain available when the specs pillar is present: `quenching://config`,
`quenching://standards`, individual standards and `quenching://glossary`. Tool lists, spec listings
and document reads retain the existing specs size and pagination rules.

## Distribution and proof

`plugins/quenching/pyproject.toml` uses hatchling and reads the package version from the plugin's
`VERSION`. The wheel keeps the plugin tree under `quenching_plugin/`, so asset lookups using
`parents[N]` keep their meaning. Its `launch` module adds `assets/bin` to the import path and
exposes `quenching-mcp` and `cq`. Runtime dependencies are the Python standard library only;
Python 3.11 is the floor.

```bash
uvx --from "git+https://github.com/holetz/quenching@<tag>#subdirectory=plugins/quenching" quenching-mcp
```

Consumers pin a published tag; publishing that tag is a separate release decision. The local
packaging smoke is `bash plugins/quenching/assets/checks/functional-checks.sh --mcp-smoke`:
it builds the current committed HEAD through `git+file`, initializes the server and compares
its tool count with the in-process catalog. Missing uvx or unavailable network is inconclusive
(exit 2), never a pass. The MCP test families and repository gate prove the source and mirrors;
the target-host smoke after release remains a deployment check.
