---
type: standard
title: Work host contract
description: The `shared.workHost` block names the user's remote host for heavy processing once per user; `cq config host --plan` prints the dispatch steps with the known traps built in and runs nothing, so quenching holds no SSH grant
resource: plugins/quenching/assets/bin/quenching/config/**
tags: [workflows, configuration, ssh, work-host]
timestamp: 2026-10-17
audience: both
authority: current
source: spec 1878, work host per user
maintainer: quenching
---

# Work host contract

<!-- rules -->

Heavy work (image builds, cargo/npm/uv, heavy tests, container deploys, GPU loads) can run on a
host the user reaches over SSH instead of the development machine. The definition lives **once per
user**, not once per project.

## Where it is declared

`shared.workHost` in `~/.config/quenching/config.json` (the user layer, `$QUENCHING_USER_CONFIG`
overrides the path). A repository's `.agents/quenching.json` may declare the same block and then
replaces the user's block key by key as every `shared` key does; see
[plugin-configuration.md](plugin-configuration.md). Absent the block, the host is disabled.

| Key | Default | Meaning |
| --- | --- | --- |
| `target` | none | SSH alias or `user@host`; setting it is what enables the host |
| `dockerContext` | none | the Docker context that points at the host |
| `runner` | none | the user's own dispatch helper (for example `~/.local/bin/remote-run`); when set, it runs the command |
| `remoteRoot` | `~/work` | where projects are synced on the host |
| `syncFlags` | `["-az", "--checksum"]` | rsync flags; the checksum keeps the mtime from deciding what is resent |
| `syncExclude` | `.git`, `node_modules`, `.venv`, `target` | never sent |
| `pullBack` | `[]` | globs of generated files that return after the run |
| `protectedPaths` | `[]` | the host's personal services and paths; a command naming one is refused |
| `minFreeGb` | `10` | free disk required before the push |

A value of the wrong shape falls back to its default and is reported as a warning.

## The plan is text

`cq config host --plan -- <command>` prints, in order, the disk check, the push, the run and one
pull per `pullBack` glob. It executes nothing: **quenching never opens an SSH connection on its
own**, and an agent that runs the plan needs an SSH permission granted by the human, never assumed
from this block. It exits 2 when the host is disabled, the command is empty or the command names a
`protectedPaths` entry.

## The traps the plan embeds

- rsync decides by mtime and the checkout's mtimes lie: the push compares checksums.
- Generated files do not come back unless named: an empty `pullBack` is reported in the plan.
- A full disk fails a long run late: the plan checks free space first.
- The host's personal services are never touched: `protectedPaths` refuses the command.

<!-- rationale -->

The plan is inert because a verb that ran SSH would be a new grant on every machine that installs
the plugin; printing it keeps the definition shared and the authority local. The per-user home
follows the layer introduced for user-wide settings, so a second project needs no second
definition.
