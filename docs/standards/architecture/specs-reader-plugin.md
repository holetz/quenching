---
type: standard
title: The specs reader is a generated, read-only sibling plugin
description: A target that only reads another project's specs enables quenching-specs-reader alone — one command, one read-only entry point that refuses write verbs at the argument boundary and disables every backend write path at runtime, and a payload and version generated from plugins/quenching and held in lockstep by the repository gate
resource: plugins/quenching-specs-reader/**, plugins/quenching/assets/modules.json, scripts/generate_plugin_modules.py, scripts/sync_specs_reader_plugin.py, scripts/verify_repo.sh, .claude-plugin/marketplace.json
tags: [architecture, plugin, specs, read-only, marketplace]
timestamp: 2026-10-14
audience: both
authority: current
source: specs 1139 and 1634 — the standalone read-only reader, then manifest-driven generation and published lockstep
maintainer: quenching
---

# The specs reader is a generated, read-only sibling plugin

<!-- rules -->

A target that needs to read another project's specs, and nothing else, enables
`quenching-specs-reader` instead of `quenching`. That target pays for one command description,
and it has no path to write the specs store or a card.

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
| `assets/modules.json` | generated distribution contract, needed by the copied release module's compatibility export |
| `VERSION`, `.claude-plugin/plugin.json`, `.generated-from.json` | generated |

`plugins/quenching/assets/modules.json` declares the source, current published plugins, reader
copy trees and files, authored paths, and the planned eight-module ownership partition from
[ADR 0013](../../decisions/0013-plugin-module-split.md). Planned records do not create plugin
directories or marketplace entries. Production extraction and activation are a later change.

`python3 scripts/generate_plugin_modules.py --write` regenerates every published generated
consumer. `--check` compares file bytes, executable bits, missing and stale files without
writing, and checks published versions, marketplace membership and the single active PATH
`cq` owner. The repository gate runs that general check. Source paths and ownership are
validated before writes: traversing or symlink paths, missing copy sources and overlaps with
authored payload refuse. Stale cleanup is confined to declared generated trees; authored paths
are preserved. Python caches are excluded.

`scripts/sync_specs_reader_plugin.py` remains a compatibility entry point to the same generator,
with the same `--write` and `--check` options and no separate copying rules. The editable source
of the package stays `plugins/quenching/`: a fix made in the copy is overwritten, and an
unregenerated source fix fails the gate.

**The version is derived.** The release verb derives its surface list from the target repository's
published module records; `RELEASE_ARTIFACTS` in `release.py` is a derived compatibility export.
It rewrites the `version` of every marketplace entry, not only the first
([versioning-release.md](../ci-cd/versioning-release.md)). The reader's `plugin.json` and `VERSION`
are also generated from `plugins/quenching/VERSION`. Release moves the version surfaces first;
the general generator then refreshes copied assets, including the shared version constant. A
source change whose copy has not been refreshed is a lockstep failure.

## Read-only is a property of the code

`bin/cq-specs-read` enforces read-only access in two layers. Both layers refuse with exit 2 and
code `sp-read-only`.

1. **An allowlist at the argument boundary.** Only `list`, `status`, `show`, `section`, `next` and
   `config` pass. `section --write` and `--fold` are refused in every prefix argparse would expand
   to them.
2. **A runtime write block.** Before dispatch, the tool imports every module of the backends
   package and replaces each write path (the write primitives, the batch write, the card writers and the
   tracker-private writers) with a refusal. The import has to come first: a class defined after the patch escapes
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

`--root <checkout>` wins, then `QUENCHING_SPECS_ROOT`, then the working directory. The store and
its configuration come from that checkout. With the git store the reader fetches the `quenching`
branch into a bare mirror of its own and never touches the target's `.git`; with a deprecated
tracker backend it reads the tracker, as `cq specs` does. A target that is not a repository sets
the variable once, in the `env` block of its `.claude/settings.json`. Reading a store without a
local checkout is outside this contract: it needs a repository resolution that the backend does
not have.

The entry point is named `cq-specs-read`, not `cq`, because Claude Code puts every enabled
plugin's `bin/` on `PATH` ([plugin-layout.md](plugin-layout.md)). With both plugins enabled, a
second `cq` would shadow the one that writes.
