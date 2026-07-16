---
name: quenching-insert
description: >-
  Inserts ONE new piece of knowledge into a repo's OKF docs/ bundle — right home, right
  type, complete conformant OKF frontmatter stamp. Use when the user asks to "insert new
  information into the base", "add a standard/convention", "write an ADR", "add a catalog
  table", "record a domain decision", "draft an announcement", "add a reference doc", or
  "register knowledge in the OKF docs". Classifies into home + type + mold, derives the
  concept path, writes the doc, updates the folder's index.md, appends a log.md entry, and
  self-checks. Not for: installing/aligning the whole docs/ structure → quenching-align;
  parking a task in the backlog → quenching-backlog.
when_to_use: >-
  adding ONE new concept doc into an existing OKF bundle. The content half; the
  structural install/migration half is quenching-align.
allowed-tools: Read, Grep, Glob, Write, Edit
---

# quenching-insert — add new knowledge, OKF-conformant

Files one new piece of knowledge into the canonical OKF bundle so it lands in the right home
with a complete stamp. Assumes the bundle already exists (run `quenching-align` first if not). The
molds live at `${CLAUDE_PLUGIN_ROOT}/assets/templates/`; the routing table and the index/log
procedure are in [references/homes.md](references/homes.md). The home boundaries, `type`
vocabulary, and conformance rules are shared with `quenching-align`
(`../quenching-align/references/taxonomy.md`, `.../conformance.md`).

## Doctrine

- **One concept per file; the path is the identity.** The folder carries the subject, so the
  filename does not repeat it (`naming/columns.md`, not `naming/naming-columns.md`).
  Kebab-case, no accents. If the subject already holds a **cluster** of siblings, file the new
  concept **inside that subfolder** (`code/symbol-naming/enums.md`), never as a `symbol-naming-*`
  flat file — extend the folder the aligner would have folded.
- **English slug on technical homes; identifier slugs verbatim.** The file slug is canonical
  English on `standards/`·`decisions/`·`vision/`·`backlog/`·`documentation/`·`reference/` (as are
  folder names, frontmatter keys, and enum values). **Exception:** an identifier-derived name is
  verbatim — a catalog `<schema>`/`<table>` mirrors the real object, `reference/repositories/<repo>`
  the real repo, an ADR keeps its `NNNN-` prefix. Body prose may be the repo's language.
- **`type` mandatory; `resource` derived, never invented.** For a standard, `resource` comes
  from the doc's `file:line` anchors; for catalog/reference, the asset URI. Empty or
  self-pointing is disallowed.
- **Anti-fabrication.** A standard that is **not yet proven** in the code enters as
  `authority: background` (a proposal), never `authority: current`. Never invent evidence.
- **MERGE, never clobber.** If the target file exists, fill missing keys, preserve filled and
  third-party ones.
- **Keep the listing honest.** Every insert updates the folder's `index.md`; a lying index is
  drift.
- **Feed the glossary.** A capture that introduces a repo-specific term ends by adding its entry
  to `knowledge/glossary.md` (the fixed A–Z term lookup) — the tail step every knowledge skill
  shares, so the term is resolvable the moment the doc lands.

## Workflow

### 1. Classify → home + `type` + mold
Apply the boundary rules ([references/homes.md](references/homes.md)):
`standards` = "how **we** do it" · `reference` = "what we **consume**" · `catalog` = "our
**data**" · `decisions` → distills to `standards` when implemented. Pick the home, its
`type`, and the matching mold.

### 2. Determine identity (path)
Concept ID = the path without `.md`. Place it under the home's subject folder; one concept per
file; kebab-case; **English slug on the technical homes** (identifier-derived names verbatim, see
Doctrine). If the subject already carries a **cluster subfolder**, nest the new doc inside it. For
homes with a fixed shape, follow it (`decisions/NNNN-slug.md`,
`catalog/<system>/<catalog>/<schema>/<table>.md`).

### 3. Fill the mold
Copy the mold from `${CLAUDE_PLUGIN_ROOT}/assets/templates/...` and complete the frontmatter:
non-empty `type` + the OKF recommended fields (`title`/`description`/`resource`/`timestamp`) +
the method labels (`audience`/`authority`/`source`/`maintainer`). Derive `resource`; an
unproven standard is `authority: background`.

### 4. Write the concept doc
Write the file with `Write`. Favor structural markdown (headings, lists, tables). Cross-home
links absolute (`/docs/...`); within-home links relative.

### 5. Update the folder's `index.md`
Add a bullet-link with the doc's `description` (`* [<title>](<rel-path>.md) — <description>`).
For `standards/**`, the layer index's **Current docs** tables are a DERIVED zone — regenerate
only what is between `<!-- BEGIN GENERATED -->` / `<!-- END GENERATED -->` from disk; never
hand-edit inside the markers. For `backlog/`, the index's task listing is likewise a DERIVED
zone — regenerate it from the tasks' frontmatter per the `backlog/index.md` bullet in
[references/homes.md](references/homes.md); never hand-edit inside the markers. Never add
frontmatter to an `index.md`.

### 6. Append to `log.md`
Per **Appending to `log.md`** in [references/homes.md](references/homes.md), with the entry:
`**Creation**: [<title>](/docs/<path>.md) — <one line>`.

### 7. Enrich the glossary
If the new concept introduced a **repo-specific term**, add or sharpen its entry in
`knowledge/glossary.md` per **Enriching the glossary** in [references/homes.md](references/homes.md)
(the tail step every capture runs; on-demand counterpart `quenching-glossary`, bulk counterpart
`quenching-knowledge-scan`).

### 8. Self-check against the conformance core
Verify every file you touched against
[../quenching-align/references/conformance.md](../quenching-align/references/conformance.md) —
the same checks the installed `okf-validate.py` hook (if wired) machine-verifies on write;
`quenching-align` re-validates the whole bundle on demand.

## Special cases
- **Standard** → mold `standard-front.md`; anchor rules to `file:line`; derive `resource`;
  consider the subject's **candidate sub-standards** and record any deferral in that subject's
  coverage ledger.
- **ADR implemented** → this is a *distill*: move the content into `standards/` (`type:
  standard`, `authority: current`), remove the ADR, and record it in the decisions "Distilled
  ledger".
- **Catalog table with descriptions** → detailed `table.md`; without → keep it a row in the
  consolidated `<schema>.md`. Never create an empty detailed page.
- **Binary (a regulation PDF we consume)** → write a `sidecar.md` extract under
  `reference/regulations/` (`type: sidecar`), never ingest the binary.
