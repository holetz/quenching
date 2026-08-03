---
type: standard
title: Spec backend interface
description: Where a repo's specs live is configurable, and the interface that makes every backend behave identically — five primitives over the canonical document rather than one method per CLI verb, a single shared derivation, the selected backend as sole source of truth, hybrid serialisation confined to each external implementation, and the in-memory fake that turns "identical" into a checked property
resource: plugins/quenching/assets/bin/specs.py, plugins/quenching/assets/references/specs-develop/spec-driven.md
tags: [architecture, specs, backend, interface, serialization]
timestamp: 2026-07-31
audience: both
authority: current
source: configurable-spec-backend plan (task 2.5)
maintainer: quenching
---

# Spec backend interface

Where a repository's specs live is a choice it declares — markdown files on a dedicated branch,
GitHub issues, Azure Boards work items. This standard is the interface that lets that choice change
nothing else: the conceptual model, the fourteen sections, the frontmatter records and the derived
stages are the same on every backend, and only the serialisation moves.

## The interface is the document, not the verbs

The CLI exposes eight verbs — `list`, `status`, `show`, `section`, `task`, `discover`, `promote`,
`validate`. **A backend implements none of them.** It implements five primitives over the canonical
markdown document:

| Primitive | Answers |
| --- | --- |
| `list_specs(phase=None)` | which specs exist, as descriptors |
| `read_spec(slug)` | the document for one spec, plus everything derived from it |
| `write_spec(info, text)` | replace one spec's whole document |
| `create_spec(phase, filename, text)` | store a new spec |
| `move_spec(info, dest_phase)` | the one lifecycle hop, `plans/` → `archive/` |

The eight verbs are shared code layered on those five.

**This is what makes "every backend behaves identically" a property of the code rather than a
promise.** One method per verb reads like the obvious design, and it is the wrong one: each backend
would re-derive stages, gates, records and task state from its own storage, three parsers would be
free to disagree, and the only thing standing between them would be a test suite exercising every
combination. With the document as the contract there is nothing to disagree about — `resolve_one`
picks the spec, `derive_info` derives everything, and both are pure and shared.

A corollary worth stating: **a backend that starts deriving anything is broken**, even if its answer
happens to be right today.

## The selected backend is the source of truth

There is no canonical local store shadowing an external one. When a repository declares `github`,
its specs live in GitHub, with no authoritative local copy — losing access to the tool is losing the
specs, which is the accepted cost of choosing it. `specs.py export` dumps the canonical markdown on
demand; nothing reads it back and nothing keeps it in sync, which is exactly what keeps it from
being a second store.

A backend named in the configuration but not implemented by the running copy of `specs.py`
**refuses with exit 2** and neither reads nor writes. It never falls back to `files`: silently
writing to the local filesystem for a repository that asked for GitHub loses work instead of
reporting it.

**No backend lets a spec share a branch with the code.** That is the property the whole design
exists for — the `files` backend puts its documents on a dedicated branch, an external backend puts
them outside git entirely — and it is why the task→commit anchor could move from the commit subject
to the sha.

## Hybrid serialisation lives inside each external implementation

An external backend is free to use its host's native constructs where a mapping exists — `## Tasks`
as sub-issues or child work items — and to fall back to serialised markdown where none does. The one
obligation is that it **reassembles the canonical document on read**.

That obligation is not a restriction on native storage; it is what makes native storage safe. The
mapping is confined to the one implementation that owns it, and it can never leak into the JSON the
CLI prints, because the CLI never sees the storage.

## Granular reading is about context, not I/O

`show` returns an **index** by default — the fourteen headings with their state, and the task ids.
One task comes back on request; the whole document only under `--full`, which refuses to combine
with a selector. Section **bodies** are `section`'s, which already reads N headings in one call and
resolves a `--moment` to its declared set: two ways to ask for a heading would be two spellings of
the same measured answer, and they would drift.

The cost this addresses is the **agent's context**, not disk or network. An agent handed all fourteen
sections in order to edit one pays for the other thirteen on every call. Whether the backend had to
fetch the whole document to answer is an implementation detail — a local cache inside `specs.py` is
free to exist and is **not** a store: it is not authoritative, nothing outside the CLI reads it, and
the backend remains the source of truth.

## The fake is how "identical" stays true

A second backend holding specs in a dict — no disk, no network, no fixture — is not a convenience.
It is the other side of an equality the selftest asserts: a canonical case list runs against `files`
and against `memory`, and every field must match except the locator (`path`) and the document text
echoed back.

Two backends sharing nothing but the interface is the only arrangement in which a command that
reaches around the interface to a filesystem path shows up immediately, with no repository to stage.

The check earns its place on history rather than on argument: the first time it ran it caught the
fake deriving a spec's date from frontmatter while `files` reads it from the filename, where `new`
stamps it once and never again. The same document, two dates. Left alone, an external backend would
have inherited the asymmetry.

The fake is deliberately **not selectable from configuration**. A store that forgets on exit must
never be somewhere real work can land.

## What this standard does not yet cover

The interface and the equality are proved for `files` and `memory`. **No external backend has been
exercised end to end at the time of writing** — what a GitHub or Azure Boards implementation must
satisfy is stated here, but the statement is a contract to meet, not a report of one met. A finding
that an external implementation cannot satisfy some rule above is a reason to revisit this document,
not to work around it quietly.
