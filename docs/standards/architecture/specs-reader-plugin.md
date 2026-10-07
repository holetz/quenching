---
type: standard
title: The specs reader is a generated, read-only sibling plugin
description: A target that only reads another project's specs enables quenching-specs-reader alone — one command, one read-only entry point that refuses write verbs at the argument boundary and disables every backend write path at runtime, and a payload and version generated from plugins/quenching and held in lockstep by the repository gate
resource: plugins/quenching-specs-reader/**, scripts/sync_specs_reader_plugin.py, scripts/verify_repo.sh, .claude-plugin/marketplace.json
tags: [architecture, plugin, specs, read-only, marketplace]
timestamp: 2026-09-28
audience: both
authority: current
source: spec 1139 — an Obsidian vault needed to read another project's specs as its to-do list without enabling 54 commands, and install-profiles.md had already measured that a profile changes no residency
maintainer: quenching
---

# The specs reader is a generated, read-only sibling plugin

<!-- rules -->

A target that needs to read another project's provider-owned specs, and nothing else, enables
`quenching-specs-reader` instead of `quenching`. That target pays for one command description,
and it has no path to write the tracker.

## Why a plugin and not a profile

<!-- rationale -->

Plugin enablement is the only unit a target can switch on. A profile narrows what `/align`
conducts, not what the host registers, as [install-profiles.md](install-profiles.md) records from
a measured session. The reader is therefore its own marketplace entry. Its `source` is its own
directory, because a second entry pointing at `plugins/quenching` would register the same 54
commands.

## What is hand-owned and what is generated

| Path under `plugins/quenching-specs-reader/` | Owner |
| --- | --- |
| `commands/read.md` | hand-owned — the only command |
| `bin/cq-specs-read` | hand-owned — the read-only entry point |
| `README.md` | hand-owned |
| `assets/bin/quenching/{common,specs}/**`, `assets/specs/**`, `assets/portal/**` | generated from `plugins/quenching/`; the other pillars and the `cq` router are not copied |
| `VERSION`, `.claude-plugin/plugin.json`, `.generated-from.json` | generated |

`scripts/sync_specs_reader_plugin.py --write` regenerates the generated set, and `--check` runs
in `scripts/verify_repo.sh`. The editable source of the package stays `plugins/quenching/`: a fix
made in the copy is overwritten, and a fix made in the source that nobody regenerates fails the
gate.

**The version is derived, never bumped.** The release verb moves four artifacts of the main
plugin, and its marketplace pattern replaces only the first `"version"`. The reader's
`plugin.json` and `VERSION` are therefore generated from `plugins/quenching/VERSION`, and the
reader's marketplace entry carries no `version`. After a release, the reader's `--check` fails
until `--write` runs, which is the intended signal.

## Read-only is a property of the code

`bin/cq-specs-read` enforces read-only access in two layers. Both layers refuse with exit 2 and
code `sp-read-only`.

1. **An allowlist at the argument boundary.** Only `list`, `status`, `show`, `section`, `next` and
   `config` pass. `section --write` and `--fold` are refused in every prefix argparse would expand
   to them.
2. **A runtime write block.** Before dispatch, the tool imports every module of the backends
   package and replaces each write path (the three write primitives and the provider-private
   writers) with a refusal. The import has to come first: a class defined after the patch escapes
   it, and the first test of this block caught exactly that.

<!-- rationale -->

The allowlist keeps the refusal cheap and legible. The runtime block covers a read verb that
someday grows a side effect. A command body that says "never write" without either layer is a
promise that no grant enforces, which is the failure [read-only-views.md](read-only-views.md)
rules out. The reader's one command therefore pre-grants `Bash(cq-specs-read:*)` and nothing
else, not a broad `python3`. That grant covers the default permission mode only. Measured on
Claude Code 2.1.284, a `dontAsk` session did not admit the call through the command's
`allowed-tools`, so a target that never prompts adds the same pattern to its own
`permissions.allow`.

## Selecting the project to read

`--root <checkout>` wins, then `QUENCHING_SPECS_ROOT`, then the working directory. The provider
and repository come from that checkout's remote, as they do for `cq specs`. A target that is not a
repository sets the variable once, in the `env` block of its `.claude/settings.json`. Reading a
provider without a local checkout is outside this contract: it needs a repository resolution that
the backend does not have.

The entry point is named `cq-specs-read`, not `cq`, because Claude Code puts every enabled
plugin's `bin/` on `PATH` ([plugin-layout.md](plugin-layout.md)). With both plugins enabled, a
second `cq` would shadow the one that writes.
