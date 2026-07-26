# `backlog/` — the definition phase

Where a spec is **captured, proposed, designed, and refined** — everything before it is ready to
build. A spec lands here in seconds as a raw problem and leaves, by a gated `promote`, only once
it can be built.

This is one of the three phase folders of the `specs/` tree, **outside** the `docs/` OKF bundle.
Its siblings are `ready/` (execution) and `archive/` (done or abandoned).

**One spec is ONE file for its whole lifecycle.** There is no separate task inbox and no plan
folder: the thing you park and the thing you build are the same file, enriched section by section
and moved between folders. That is why there is no Completed ledger here — a finished spec is in
`archive/`, told apart by its `outcome:` frontmatter, and `git log --follow` is its history.

## Organization

```
backlog/
  index.md                        # this listing (frontmatter-free, generated zone below)
  YYYY-MM-DD-<slug>.md            # one spec per file — flat, no subfolders
```

The date prefix is stamped **once, at capture**, and never rewritten — `promote` moves a file
without renaming it. So a plain `ls` is chronological, and *how long has this sat here?* is
answered by the listing itself rather than by a tool.

## Derived stages

A spec's stage inside this folder is **computed from section completeness**, never declared —
declared state is forgotten on edit and goes stale.

| Stage | Reached when |
| --- | --- |
| `captured` | only `## Problem` is filled |
| `proposed` | `## Proposal` is filled |
| `designed` | `## Design` is filled |
| `refined` | a `refined` record is in the frontmatter |

## Leaving this folder

`specs.py promote <slug>` moves a spec to `ready/`, and **refuses (exit 2)** unless the ten
definition-gate sections are filled — the nine `## Problem` … `## Risks` plus `## Tasks`. An empty
section is filled with an explicit `- none — <reason>`; a heading present with an empty body is
malformed and refuses.

**That promote IS the human OK to build.** It is one auditable `git mv`, not a checkbox.

A spec that will **not** be built is promoted straight to `archive/` with `outcome: abandoned` —
no ceremony, and its `## Outcome` records why.

## What does NOT go here

- A spec being built right now (→ `ready/`).
- A finished or dropped spec (→ `archive/`, with `outcome:`).
- Settled direction with no deadline (→ `docs/vision/`).

## Current specs

<!-- BEGIN GENERATED: rebuilt from the spec files' headings and frontmatter by
     `specs.py backlog reindex` — DO NOT edit by hand. Content, in order:
       **N specs** · X captured · Y proposed · Z designed · W refined
       one table per DERIVED STAGE (Refined → Designed → Proposed → Captured; empty groups
       omitted), columns `Spec | Title | Since` (Since = the filename's date prefix), rows
       OLDEST-FIRST within each group so stale specs surface.
-->
_(no specs captured — this listing is regenerated deterministically from `backlog/*.md`)_
<!-- END GENERATED -->

## Frontmatter

A spec file carries the lifecycle schema, **not** an OKF `type:` — it is not a concept doc, it
lives outside the bundle, and `specs.py validate` is what checks it:

```yaml
---
slug: <the identity key every command names>
title: <one line>
verification: per-task            # per-task | per-section | end-of-plan
refined: {mode: premortem, date: 2026-07-25}   # once refined
---
```

There is no `created` field (the filename prefix is that fact) and no `phase` field (the folder is
that fact). `okf-validate.py backlog --listing-root` checks **this listing**; the spec files are
`specs.py validate`'s business.
