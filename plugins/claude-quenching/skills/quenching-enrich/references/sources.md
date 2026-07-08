# Sources — scoping, bounded ingestion, unit extraction, attribution, dedup

The ingestion-specific detail `quenching-enrich` owns. The **per-doc** procedure (classify →
stamp → index → log → glossary → self-check) is **not** here — it lives once in
[`quenching-insert/references/homes.md`](../../quenching-insert/references/homes.md), which
this skill cites. This file covers only how a *source* becomes the list of units that
procedure then mints.

## What a source can be

- **Local files/folders** — read with `Read`/`Glob`/`Grep`. A markdown/notes tree, a README,
  a design doc, an exported wiki, a spec, a schema dump. Anchor each unit to `path:line`.
- **URLs** — fetched with `WebFetch`. A doc page, an API reference, a spec, an article.
  Anchor each unit to the URL (+ heading/anchor when addressable).

Out of scope (route elsewhere): ONE fact the human states → `quenching-insert`; the project's
`~/.claude` memory → `quenching-memory-to-docs`; installing/aligning the tree →
`quenching-align`.

## Bounded ingestion (discipline, not code)

A source — especially a web source — is bounded **before** the first fetch. This echoes the
caps the upstream `enrich` enforced in code; here it is operator discipline:

- **Seed list.** The explicit set of files/URLs the user named. Nothing is ingested that is
  not on the seed list or reached from it under the rules below.
- **Host allowlist.** For web sources, the set of hosts a link may be followed to. Default:
  the hosts of the seed URLs only. A link to any other host is recorded, never fetched.
- **Page cap.** A hard maximum number of pages/files to fetch this run (state it in the plan).
  When the cap is hit, stop and **report what was left unfetched** — never silently truncate.
- **One hop by default.** Follow links only one level from a seed, and only within the
  allowlist, up to the cap. Deeper crawls are a fresh, re-scoped run.
- **No auth walls, no downloads of binaries.** A binary (PDF/slide deck) becomes a `sidecar`
  extract per homes.md, not an ingested body.

State the seed list, allowlist, cap, and hop depth in the Step-3 plan so the user sees the
blast radius before the one OK.

## Extracting knowledge units

A **unit** is one concept — the granularity homes.md files as a single doc. Split the source
along its natural concept boundaries (a heading section, a table, a defined term, one rule,
one decision), not by page. Heuristics:

- One **rule / convention** → a `standards/` unit (unproven in the target's code ⇒
  `authority: background`).
- One **decision with alternatives** → a `decisions/` ADR unit.
- One **explanation / concept / term** → a `knowledge/` unit (+ a glossary entry if it names a
  repo-specific term).
- One **fact about a named external tool/lib/regulation** → a `reference/` unit.
- One **how-to / procedure** → a `documentation/how-to/` unit.
- **Data objects** (systems/schemas/tables) → `catalog/` units in the catalog path shape.

Keep units atomic — if a section carries two concepts, emit two units. Prefer **fewer,
well-scoped** units over shredding prose into fragments.

## Attribution

Every minted doc records where it came from — the source path/URL in the frontmatter
`source:` field (and a link in the body when the source is a stable URL). This keeps the
bundle honest about what is imported vs authored, and lets a later run re-sync the source.
Never present imported material as proven local practice: that is the `authority: background`
rule.

## Dedup — within the source and against the bundle

1. **Within the source.** Two sections describing the same concept collapse into one unit
   (merge their detail); do not mint duplicates.
2. **Against the existing bundle.** Before minting, `Grep` the bundle for an existing doc on
   the same concept (by title, slug, and any repo-specific term). If one exists, the unit is a
   **MERGE** target — enrich that doc (fill missing keys, add detail, add the source link),
   never a second doc for the same concept. Record every MERGE-vs-mint decision in the plan.
3. **Glossary.** A term the source defines that the glossary already lists is a MERGE into the
   existing entry (sharpen/keep the link), per homes.md §Enriching the glossary.

## Fan-out for scale

For a large source, one `Task` sub-agent per **source slice** (a folder, a URL group)
returns **compact unit candidates** — `{home, type, path, one-line, source-anchor}`, never
full bodies. The orchestrator merges the candidate lists, runs the cross-slice dedup above,
and builds the single plan. Extraction/executor sub-agents may run on a **cheap
model/effort**: enrich deletes nothing, so a misclassification only misfiles a doc (a
correctable move), unlike `quenching-memory-to-docs` where a misclassification deletes a
memory. See the model policy in [../../../README.md](../../../README.md#cost-model).
