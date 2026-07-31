# Homes — routing table + the index procedure

How `/quenching:docs:add` decides **where** a new concept goes, **which** `type` it carries, **which**
mold fills it, and **how** to keep the `index.md` honest. **This file is the single owner of
the insert procedure** — stamp (§The frontmatter stamp) → index (§Updating `index.md`) →
glossary (§Enriching the glossary) → self-check (§Self-check) — and every skill that inserts
a doc (`/quenching:docs:add`, `/quenching:docs:learn`, `/quenching:docs:harness`,
`/quenching:docs:import-memory`) cites these sections instead of restating them; only each skill's own
safety deltas stay inline in its SKILL.md. The full home boundaries and tree live in
`${CLAUDE_PLUGIN_ROOT}/assets/references/docs-align/taxonomy.md`; the checks in
`${CLAUDE_PLUGIN_ROOT}/assets/references/docs-align/conformance.md`.

## Contents

- [Classification — one question decides the home](#classification--one-question-decides-the-home)
- [The frontmatter stamp](#the-frontmatter-stamp)
- [Updating `index.md` (the listing)](#updating-indexmd-the-listing)
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
- **spec vs vision:** a **parked unit of work** is a **spec** and does **not** belong in this
  bundle at all — it lives at `specs/plans/`, outside it, so route the capture to
  `/quenching:specs:create`. A **settled direction** with no deadline is a `vision` and stays here. The
  full `specs/` ↔ `docs/` boundary — which tree answers which question, and why they never
  duplicate content — is owned once by
  [`specs-develop/spec-driven.md`](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-develop/spec-driven.md)
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

**Not in the mold, deliberately:** `source_uri:` — written by `/quenching:docs:import` alone, never invented
by the commands citing this block, and simply absent on a doc with no external origin. Its
contract is [sources.md](${CLAUDE_PLUGIN_ROOT}/assets/references/docs-import/sources.md)
§Attribution.

## Updating `index.md` (the listing)

- Add `* [<title>](<relative-path>.md) — <description>` under the right section. Keep links
  relative within the home, absolute (`/docs/...`) across homes.
- If the doc **creates a new folder**, create that folder's `index.md` too (a frontmatter-free
  listing) and link it from the parent — a folder of concepts without one is a `dir-no-index`
  gap, and an unlisted doc is an `index-orphan`.
- **Never** add frontmatter to an `index.md` (the root's `okf_version` is the only exception,
  and `/quenching:docs:align` owns it).
- **`standards/index.md`** has a DERIVED zone: rebuild only what is between
  `<!-- BEGIN GENERATED -->` / `<!-- END GENERATED -->` by scanning `standards/**/*.md`
  (`title`/`description`/`timestamp`/`type`), grouped by subject subfolder. Never hand-edit
  inside the markers.

(`specs/plans/` has no listing to update and is **not** part of this OKF insert procedure —
`specs/` lives outside the bundle, and `specs.py list` derives what the folder holds from disk on
demand. See
[`specs-create/specs-front.md`](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-create/specs-front.md).)

## Enriching the glossary (tail step, every capture)

The `knowledge/` home ships one fixed file, [`knowledge/glossary.md`](${CLAUDE_PLUGIN_ROOT}/assets/docs/knowledge/glossary.md):
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
  the concept doc; the glossary points to it. Do not touch `knowledge/index.md` for this —
  the glossary is already listed there.

This is the same tail step `/quenching:docs:learn`, `/quenching:docs:add`, and
`/quenching:docs:import-memory` each run; the on-demand single-term counterpart is the
`/quenching:docs:define` skill, and the whole-bundle bulk counterpart — sweeping every doc
already in `docs/` for terms the glossary never caught — is `/quenching:docs:glossary-backfill`.

## Self-check before finishing

Apply `${CLAUDE_PLUGIN_ROOT}/assets/references/docs-align/conformance.md`: the new concept has parseable frontmatter +
a non-empty `type`; every `index.md` you touched is still frontmatter-free; the new doc's folder
has an `index.md` that **links** it (no `dir-no-index`, no `index-orphan`, no
`index-broken-link`). If the `okf-validate.py` hook is wired in the target, it will confirm
on write.
