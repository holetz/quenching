---
type: decision
title: Spec backend measurements and history
description: The measured costs and false-for-a-year sentences behind the spec backend interface rules, moved out of the standard
resource: plugins/quenching/assets/bin/quenching/specs/backends/**
tags: [decision, history, architecture]
timestamp: 2026-10-07
audience: both
authority: current
source: abandonar-slug-por-id-nativo; spec-backend standard (history moved 2026-10-07)
maintainer: quenching
---

# Spec backend measurements and history

History and measurements moved out of [spec-backend](../standards/architecture/spec-backend.md) so the standard keeps the rule. Each section below is the original evidence, verbatim.

## Identity cost, measured 2026-08-22

The measurement made the boundary concrete on 2026-08-22, against 154 GitHub spec issues:

- `cq specs status --spec X` cost **3.81 s** when it downloaded the tracker to find a spec; a direct
  provider-ID read costs **0.39 s / 7.7 KB**.
- `cq specs list --json` cost **4.82 s / 5.25 MB**, with 4.2 MB of bodies against 10 KB of titles —
  **420:1** bytes transported over bytes useful to the listing.
- `cq specs list --lean --json` returned the same verified set of 154 specs in **1.59 s / 70 KB**.
  GitHub filters the discovery marker server-side; Azure Boards has the equivalent WIQL filter on
  its discovery tag. The full listing remains authoritative because the lean index is eventually
  consistent and document-derived fields are not available in it.

## Task projection cost, measured 2026-08-03

The price of putting it where it was not free, measured on this repository on 2026-08-03,
mid-migration:

- **68 spec issues against 689 task sub-issues.** 91% of the tracker's volume was the projection;
  43 specs were open, and 332 sub-issues with them.
- **The full listing every specs command pays was 8 pages, 4.4 MB and 8.4 seconds.** Collapsed, it
  is one page.
- **`write_spec` on a ten-task spec spent twelve round trips where one now does** — one PATCH on
  the parent, one GET of the sub-issues, one PATCH per task. A newly created task cost three of its
  own (POST, POST to link it as a child, PATCH to close it when the box was already ticked).
- **`read_spec` paid one GET of sub-issues per spec read.** A one-part spec now costs nothing
  beyond the listing, which already carries every body.

## created_at is not the capture date

- **The capture date fails.** An issue's `created_at` is when the ISSUE was created, not when the
  spec was captured. On this repository, on 2026-08-03, issue #776 carried `created_at
  2026-08-03T03:32:51Z` for a spec captured on **2026-07-25**: the numbers jump from 7 to 776
  because a migration created ~769 issues in one afternoon. Deriving the date natively would have
  rewritten **68 of 70** capture dates to the migration's own day, destroying the one thing the
  field records.

## Label rendering cost, measured live 2026-08-05

SAME `--fields` update `_update` already sends. MEASURED live, 2026-08-05, against this
  repository's own issue #877: a write that changes no record and no stage costs exactly
  the one `PATCH` it always did. The first cut did not — it compared the desired label set
  against the issue's current one as ORDERED lists, and GitHub returns a listing's labels
  alphabetically, never in the schema's own order, so a same-set reorder read as a change
  on every write and cost an extra `GET` fixing colors that were already right. Comparing
  the two as sets was the fix.

## One request per write

That sentence was written as a description
and was false for a year — measured on `azure-boards`, one section edit spent nine `az` calls and
8,5s, of which four writes went to the same work item: the document, then the parent, then the
board column, then the tags. The cost was never the reaffirmation. It was spending one process per
field, on a CLI whose startup is the floor (0,45s for `az rest` against 0,9s for `az boards
work-item update`, measured on the same org).

