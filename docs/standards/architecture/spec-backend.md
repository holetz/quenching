---
type: standard
title: Spec backend interface
description: Where a repo's specs live is configurable, and the interface that makes every backend behave identically — five primitives over the canonical document rather than one method per CLI verb, a single shared derivation, the selected backend as sole source of truth, hybrid serialisation confined to each external implementation with the whole document (not just the parts it models) as its reassembly obligation, and the in-memory fake that turns "identical" into a checked property
resource: plugins/quenching/assets/bin/specs.py, plugins/quenching/assets/references/specs-develop/spec-driven.md
tags: [architecture, specs, backend, interface, serialization]
timestamp: 2026-08-03
audience: both
authority: current
source: configurable-spec-backend plan (task 2.5); §What "the canonical document" covers added by fix-github-backend-tasks-fidelity (task 3.2), after the `github` backend was measured dropping every `### N.` group heading it stored; the `## Tasks`→sub-issue mapping retired by migrate-this-repo-to-github-backend, after 689 task sub-issues against 68 spec issues were measured serving a projection nothing ever read back
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

An external backend is free to use its host's native constructs where a mapping exists, and to fall
back to serialised markdown where none does. The one obligation is that it **reassembles the
canonical document on read**.

That obligation is not a restriction on native storage; it is what makes native storage safe. The
mapping is confined to the one implementation that owns it, and it can never leak into the JSON the
CLI prints, because the CLI never sees the storage.

### A native mapping earns its cost only if something reads it back

The permission above is not an invitation. Both external backends took it up for `## Tasks` — one
sub-issue per task on `github`, one child work item on `azure-boards` — because `## Tasks` is the
one section with a native counterpart carrying its own state and identity. That is true, and it was
not the question. The question is whether anything ever **read** the native state, and nothing did:
`parse_tasks` takes a task's checked/blocked from its raw block text on both ends, never from the
issue. A construct written on every save and never consulted is a **projection**, and a projection
belongs wherever it is free — the issue title is one, rewritten from the frontmatter on every write
at no extra call — never wherever it costs a call per item per write.

The price of putting it where it was not free, measured on this repository on 2026-08-03 mid-migration:

- **68 spec issues against 689 task sub-issues.** 91% of the tracker's volume was the projection;
  43 specs were open, and 332 sub-issues with them.
- **The full listing every specs command pays was 8 pages, 4.4 MB and 8.4 seconds.** Collapsed, it
  is one page.
- **`write_spec` on a ten-task spec spent twelve round trips where one now does** — one PATCH on the
  parent, one GET of the sub-issues, one PATCH per task. A newly created task cost three of its own
  (POST, POST to link it as a child, PATCH to close it when the box was already ticked).
- **`read_spec` paid one GET of sub-issues per spec read.** A one-part spec now costs nothing beyond
  the listing, which already carries every body.

So the mapping is retired. On both external backends the **whole canonical document is the issue
body / the work item description**, and there are no sub-issues and no child work items.

What is given up, stated plainly, is **per-task addressability** — an assignee, labels, a comment
thread of its own, a PR that closes a task issue. Nothing in quenching used any of it; `/specs:execute`
anchors a task to its commit by the sha recorded in the document. What is kept is the part that
renders: `- [ ]` in an issue body is a native GitHub task list, with a checkbox and a progress count,
and ticking it in the web UI **edits the document** — which closing a sub-issue never did.

### What "the canonical document" covers, and how the obligation is checked

**The whole document, byte for byte** — not the fields a backend happens to model. The obligation
reads as obvious and was not: the `github` backend shipped mapping `## Tasks` to sub-issues by
emptying that section and concatenating the blocks back, which loses every `### N. <Section>` group
heading and every line of prose the section carried. Nothing failed. The write succeeded, the read
returned a well-formed document, and the loss was visible only by comparing it to what went in.
Measured across this repository's own specs, 49 of 68 carry groups.

That loss was the sub-issue mapping's, and the mapping is retired (above) along with the per-task
keys, indices and anchors its reassembly ran on. **The obligation did not go with it.** It is now
close to free on both external backends — the document is what is *stored*, not what is rebuilt — and
it is checked exactly as before, because these three rules hold for any backend, including the next
one to take the native-construct permission up:

- **Structure a backend does not model is structure it must carry, not structure it may drop.** A
  section's grouping, its prose and the blank lines between its items are content. A mapping that
  keeps only the parts with a native counterpart is a lossy projection wearing a serialisation's
  name.
- **The check is equality on the document, never an assertion about the pieces.** "The headings are
  still there" passes with them reordered and the prose gone. `specs.py selftest` runs a grouped
  fixture through store-and-reload — including the CRLF round trip a tracker really performs — and
  compares the result to the original with `==`.
- **A store's own ceilings are the backend's problem, not the caller's.** A title that a tracker
  will not accept is cut by the backend, because a title is a projection of the document and cutting
  it loses nothing. A **document** over the ceiling is not cut and is no longer refused: a GitHub
  issue body holds 65,536 characters, and of this repository's 69 specs **two exceed that as whole
  documents — 69,498 and 74,180 — one of them an active plan**. Refusing would mean refusing to
  store a spec somebody is building, so an over-size document spills into **continuation comments on
  its own issue**, cut on line boundaries and joined back on read. The refusal survives as a
  backstop at the one point every write passes through, so no later caller can hand the tracker a
  body it will answer 422 to; and a declared part the comments no longer hold is its own **refusal
  (`sp-gh-parts-missing`, exit 2)** — returning the shorter document would let the next write
  persist that truncation as the new truth.

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

The interface and the equality are proved for `files` and `memory`, and the reassembly obligation is
proved offline for the hybrid serialisation both external backends share.

**`azure-boards` has never been exercised end to end.** What it must satisfy is stated here, and for
that backend the statement is a contract to meet rather than a report of one met.

`github` has been exercised end to end once, against a throwaway test spec. That is worth less than
it sounds, and the gap is the reason this section stays: the test spec had no `### N.` groups and no
over-long task line, so the run proved the transport and not the shape of real documents — which is
exactly where the loss described above was hiding. **A backend is proved by the documents it will
actually be given, not by the ones written to exercise it.**

That sentence has since been earned a second time by the same test spec: it was also nowhere near
the 65,536-character body ceiling, and two of this repository's 69 real specs are over it. So the
retirement was paid for the way the sentence asks — **all 69 real documents were run through the new
serialisation offline**, split, wrapped, put through the CRLF round trip a tracker performs,
unwrapped and joined, and every one came back byte for byte, the two that spill included.

A finding that an external implementation cannot satisfy some rule above is a reason to revisit this
document, not to work around it quietly.
