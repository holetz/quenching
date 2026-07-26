# Homes — routing table + the index/log procedure

How `quenching-docs-add` decides **where** a new concept goes, **which** `type` it carries, **which**
mold fills it, and **how** to keep the `index.md`/`log.md` honest. **This file is the single owner
of the insert procedure** — stamp (§The frontmatter stamp) → index (§Updating `index.md`) → log
(§Appending to `log.md`) → glossary (§Enriching the glossary) → self-check (§Self-check) — and
every skill that inserts a doc (`quenching-docs-add`, `quenching-docs-learn`, `quenching-docs-harness`,
`quenching-docs-import-memory`) cites these sections instead of restating them; only each skill's own
safety deltas stay inline in its SKILL.md. The full home boundaries and tree live in
`../../quenching-docs-align/references/taxonomy.md`; the checks in
`../../quenching-docs-align/references/conformance.md`.

## Contents

- [Classification — one question decides the home](#classification--one-question-decides-the-home)
- [The frontmatter stamp](#the-frontmatter-stamp)
- [Updating `index.md` (the listing)](#updating-indexmd-the-listing)
- [Appending to `log.md` (the history)](#appending-to-logmd-the-history)
- [Enriching the glossary (tail step, every capture)](#enriching-the-glossary-tail-step-every-capture)
- [Self-check before finishing](#self-check-before-finishing)

## Classification — one question decides the home

Ask **"what IS this, relative to us?"**:

| The information is… | Home | `type` | Mold (`${CLAUDE_PLUGIN_ROOT}/assets/templates/…`) | Path shape |
| --- | --- | --- | --- | --- |
| a rule for **how WE build** (proven, or agreed-but-unproven) | `standards/<subject>/` | `standard` | `standard-front.md` | `<subject>/<concept>.md` |
| **direction** for an area (no deadline) | `vision/` | `vision` | `vision/area.md` | `<area>.md` |
| a **how-to / task recipe** (product usage) | `documentation/how-to/` | `documentation` | `concept-front.md` | `how-to/<slug>.md` |
| a **tutorial** (learning-oriented) | `documentation/getting-started/` | `documentation` | `concept-front.md` | `getting-started/<slug>.md` |
| **product reference / explanation** (site page) | `documentation/{reference,concepts}/` | `documentation` | `concept-front.md` | `<section>/<slug>.md` |
| **generic understanding we hold** (concept / explanation / learning) | `knowledge/<subject>/` | `knowledge` | `concept-front.md` | `<subject>/<slug>.md` |
| a **fact about an external** tool/lib/regulation | `reference/{tools,libraries,regulations}/` | `reference` | `concept-front.md` | `<slug>.md` |
| **our data** — a system / schema / table | `catalog/<system>/…` | `system`/`schema`/`table` | `catalog/{system,schema,table}.md` | see below |
| a **regulation PDF / binary we consume** (extract) | `reference/regulations/` | `sidecar` | `sidecar.md` | `<slug>.md` (+ `binary:`) |

### Boundary tie-breakers
- **standards vs reference:** "how **WE** do it" (standards) vs "a fact about what **WE
  CONSUME**" (reference). Our implementation of a regulation is a `standard`; the regulation
  itself is a `reference` sidecar.
- **knowledge vs its neighbors:** `knowledge/` is **generic understanding** (a concept,
  glossary, mental model, learning) — non-binding. A binding rule for how we build is a
  `standard`; a fact about a **named** external dependency is `reference`; a set of steps for using the
  product is a `documentation` how-to. When understanding hardens into a rule, it distills
  into `standards/` and leaves
  `knowledge/`.
- **documentation vs knowledge:** a **published-site page** (narrative, for a human reading
  the docs) is `documentation/`; **internal team understanding** (mental model, learning,
  glossary) is `knowledge/`. Explanation that ships on the site → `documentation/concepts/`;
  explanation the team holds internally → `knowledge/`.
- **standards & agreed rules:** a **proven, current** rule for how we build is a `standard`
  (`authority: current`); an **agreed-but-not-yet-proven** rule is a `standard` with
  `authority: background` until proven. There is **no separate decision home** — a decision's
  rationale and considered alternatives are captured in a plan's `design.md` while
  the change is active, and its durable outcome lands as a `standard` at archive time.
- **task vs vision:** a **parked unit of work** is a `task` and does **not** belong in this
  bundle at all — the backlog lives at `specs/backlog/`, outside it, so route the capture to
  `quenching-specs-backlog-add`. A **settled direction** with no deadline is a `vision` and stays here. The
  full `specs/` ↔ `docs/` boundary — which tree answers which question, and why they never
  duplicate content — is owned once by
  [`../../quenching-specs-plan-propose/references/spec-driven.md`](../../quenching-specs-plan-propose/references/spec-driven.md)
  §Boundary; read it there rather than inferring it from this row.
- **standards vs catalog:** the *rule* for modeling data (grain/keys) is a `standard`
  (`data-modeling/`); the *actual tables* are `catalog/`.
- **code vs naming (inside standards):** `code/` governs **symbols**; `naming/` governs
  **data** (tables/columns).

### Catalog path shapes
- System access card → `catalog/<system>/access.md` (`type: system`); its sibling
  `catalog/<system>/index.md` is the reserved listing.
- Consolidated schema → `catalog/<system>/<catalog>/<schema>.md` (`type: schema`).
- Detailed table → `catalog/<system>/<catalog>/<schema>/<table>.md` (`type: table`) — only when
  descriptions exist; otherwise leave the table as a row in the consolidated `<schema>.md`.

## The frontmatter stamp

Fill from the mold; every concept gets:

```yaml
type: <from the table above — non-empty>
title: <short name>
description: <one sentence — the "Covers" cell an index renders>
resource: <derived — never invented; standards a comma-separated GLOB SET of what the doc governs (`*`/`**` only, repo-root-relative), catalog/reference the asset URI>
tags: [<...>]
timestamp: <today, ISO 8601>
audience: both | agent | human       # canonical English enum
authority: current | background      # unproven standard ⇒ background (anti-fabrication)
source: <origin/author>
maintainer: <owner>
```

## Updating `index.md` (the listing)

- Add `* [<title>](<relative-path>.md) — <description>` under the right section. Keep links
  relative within the home, absolute (`/docs/...`) across homes.
- If the doc **creates a new folder**, create that folder's `index.md` too (a frontmatter-free
  listing) and link it from the parent — a folder of concepts without one is a `dir-no-index`
  gap, and an unlisted doc is an `index-orphan`.
- **Never** add frontmatter to an `index.md` (the root's `okf_version` is the only exception,
  and `quenching-docs-align` owns it).
- **`standards/index.md`** has a DERIVED zone: rebuild only what is between
  `<!-- BEGIN GENERATED -->` / `<!-- END GENERATED -->` by scanning `standards/**/*.md`
  (`title`/`description`/`timestamp`/`type`), grouped by subject subfolder. Never hand-edit
  inside the markers.

(The `specs/backlog/index.md` DERIVED zone is **not** part of this OKF insert procedure —
the backlog lives outside the bundle; its zone spec is owned by the backlog skills, in
[`../../quenching-specs-backlog-add/references/backlog-zone.md`](../../quenching-specs-backlog-add/references/backlog-zone.md).)

## Appending to `log.md` (the history)

- Newest first. If today's `## YYYY-MM-DD` heading exists, add a line under it; else add the
  heading at the **top** of the entries.
- Prefix the kind: `**Creation**` (new doc) · `**Update**` (edit) · `**Deprecation**`
  (removed/superseded), each with a link: `**Creation**: [<title>](/docs/<path>.md) — <one line>`.
- The bundle `docs/log.md` records cross-home events; `docs/standards/log.md` records standards
  events. A per-home `log.md` is optional.

## Enriching the glossary (tail step, every capture)

The `knowledge/` home ships one fixed file, [`knowledge/glossary.md`](../../../assets/docs/knowledge/glossary.md):
the repo's A–Z term lookup, a flat alphabetical bullet list in the same syntax every
`index.md` uses (the one deliberate exception to "one concept per file") — `* [<Term>]
(<path>.md) — <one-sentence definition>` when a concept doc exists, or `* **<Term>** —
<one-sentence definition>` when it doesn't (an **unlinked entry is a valid, permanent
state**, not a defect). After a capture lands, **check whether the concept introduced a
term that belongs in the glossary** and, if so, enrich it:

- **When to add an entry.** The doc names a repo-specific word, acronym, or piece of
  jargon a newcomer would not know (a domain entity, an internal codename, a term of
  art). Skip generic English and terms already listed.
- **How to add it (MERGE, never clobber).** Insert the term in **alphabetical** position,
  in the linked bullet form, pointing at the concept doc you just wrote (`/docs/<path>.md`,
  absolute across homes). If an entry for the term already exists, sharpen its definition
  or add the link — never overwrite a filled definition or a filled link.
- **Only the entry.** The glossary is an index, not the long-form home — the depth stays in
  the concept doc; the glossary points to it. Do not touch `knowledge/index.md` for this
  (the glossary is already listed there) and do not log a separate glossary event unless
  the term entry is the only thing you wrote.

This is the same tail step `quenching-docs-learn`, `quenching-docs-add`, and
`quenching-docs-import-memory` each run; the on-demand single-term counterpart is the
`quenching-docs-define` skill, and the whole-bundle bulk counterpart — sweeping every doc
already in `docs/` for terms the glossary never caught — is `quenching-docs-glossary-backfill`.

## Self-check before finishing

Apply `../../quenching-docs-align/references/conformance.md`: the new concept has parseable frontmatter +
a non-empty `type`; every `index.md` you touched is still frontmatter-free; the new doc's folder
has an `index.md` that **links** it (no `dir-no-index`, no `index-orphan`, no `index-broken-link`);
the `log.md` is `## YYYY-MM-DD` newest-first. If the `okf-validate.py` hook is wired in the
target, it will confirm on write.
