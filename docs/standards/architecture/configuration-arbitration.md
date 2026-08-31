---
type: standard
title: Configuration arbitration by key
description: A shared configuration artifact has one writer for each semantic key, separate reader metadata, and no arbiter row for a read-only pillar, with a generated declaration first applied to pyproject.toml
resource: pyproject.toml, plugins/quenching/assets/bin/quenching/ops/**, plugins/quenching/assets/bin/quenching/proof/**, .github/workflows/**
tags: [architecture, configuration, ownership, arbitration, ops, proof]
timestamp: 2026-08-31
audience: both
authority: background
source: declare-the-configuration-arbiter spec 1064 (2026-08-31), grounded in the shipped operations registry and the aligned-front boundary
maintainer: quenching
---

# Configuration arbitration by key

A shared configuration artifact is a file or directory read by more than one front or pillar. Its
ownership is not the whole file's: each mutable key or semantic section has one arbiter that may
define, write, or repair it. The declaration travels with the artifact so a stale or duplicated
owner is visible where the readers find the configuration.

## One arbiter per key

Ownership is assigned by semantic key path, not by the containing file. A key has exactly one
arbiter, or an explicit pending state while the future owner is not built. Two fronts must never
write the same key silently, and assigning every key in a shared file to one front recreates the
drift this rule is meant to prevent.

The arbiter owns the value and its repair. A reader may consume the value, report evidence about it,
or expose a finding when it is stale, but those actions do not make the reader an arbiter. The
ownership table is therefore a contract about who may mutate a key, not a list of every command
that happens to observe it.

## Readers are separate metadata

The standard records readers beside the arbiter so the evidence remains discoverable without
turning an observer into a writer. Reader metadata names the source paths and the semantic fact
they consume; it does not add another ownership row or authorize a repair.

The first application has these ownership rows:

| Configuration key or section | Arbiter | Evidence / readers | Status |
| --- | --- | --- | --- |
| `[project.scripts]` (`project.scripts`) | `ops` | `plugins/quenching/assets/bin/quenching/ops/inventory.py:32,140` | current owner |
| pytest configuration (`tool.pytest`) | `proof` | `plugins/quenching/assets/bin/quenching/proof/inventory.py:123-131,177-180` | current owner |
| coverage configuration (`tool.coverage`) | `proof` | `plugins/quenching/assets/bin/quenching/proof/inventory.py:123-131,177-180` | current owner |
| dependencies, lock, language version, lint and build backend | future `toolchain` front | admitted future boundary; no unbuilt front is claimed | pending future owner |

## Read-only pillars have no arbiter

A pillar that answers live questions without owning a tree this plugin converges does not receive an
arbiter row. It may read a shared key and report what it observes, but it never defines, writes, or
repairs that key. The `security` subject is such a pillar: workflow permissions, dependency advice,
secret and ignore-pattern observations remain evidence distributed across owners, and `security`
receives no configuration-arbiter row.

This boundary keeps classification separate from implementation. A named future front is not a
shipped owner; only a separate implementation spec can make its command surface, route, or verifier
current.

## The generated declaration in `pyproject.toml`

The first declaration is a generated comment block. The generator owns only the lines between the
delimiters and preserves every other TOML line:

```toml
# quenching-arbiters-start
# quenching-arbiters-sha256 <64 lowercase hexadecimal digits>
# quenching-arbiters-data {"artifact":"pyproject.toml","entries":[{"arbiter":"ops","key":"project.scripts"},{"arbiter":"proof","key":"tool.coverage"},{"arbiter":"proof","key":"tool.pytest"}]}
# quenching-arbiters-end
```

The digest is SHA-256 over the UTF-8 bytes of the canonical compact JSON object represented by the
`quenching-arbiters-data` value. Its object contains the artifact identity and the sorted
`{key, arbiter}` entries. Serialization uses sorted keys, compact separators, and no trailing
newline. Entries are sorted by `key`; their object keys are sorted by the serializer. The digest is
lowercase hexadecimal and must cover exactly the declaration's data, not the surrounding comment
markers.

The declaration is a record, not a second configuration language. A verifier may detect a duplicate
owner, a missing owner for a claimed mutable key, or a stale hash without deciding formatting,
ruleset, or upgrade policy. Those semantic decisions remain with the arbiter that owns the key.

## The workflow boundary

The same ownership test applies to `.github/workflows/**`, but this standard does not guess its
final partition without a real target's evidence:

| Workflow concern | Boundary |
| --- | --- |
| triggers, jobs, and stages | future `delivery` owner |
| CI configuration used as gate evidence | `proof` owner |
| workflow permissions observed as live facts | read-only `security` pillar; no arbiter row |

The exact key granularity and whether the workflow directory receives the same generated block stay
open until the target supplies that evidence. The future `toolchain`, `delivery`, and `security`
names record admitted boundaries, not surfaces that this repository claims to have shipped.

## What this standard does not decide

This contract does not rename or migrate `.claude/quenching.json`, extract its shared loader, or
define per-front configuration namespaces. It does not make consumer readers enforce ownership, mint
future command surfaces, or turn a read-only report into an align. Those decisions belong to the
configuration-home and consuming-front work that follows this first declaration.
