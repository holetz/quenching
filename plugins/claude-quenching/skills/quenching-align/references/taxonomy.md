# Canonical taxonomy — the tree, homes, `type` vocabulary, boundaries

The single source of the tree `quenching-align` installs and `quenching-insert` files into. Every repo
**converges to this same tree of identical names**; a variant name is a non-convergence smell
(→ [migration.md](migration.md)).

## The canonical tree (locked)

```
docs/                          # OKF bundle root
  index.md                     # ONLY index.md with frontmatter — okf_version: "0.1" + home listing
  log.md                       # bundle change history (## YYYY-MM-DD, newest first)
  standards/                   # "how WE do it" (current) — a conformant sub-bundle
    index.md                   # reserved listing + DERIVED "Current docs" tables (BEGIN/END GENERATED)
    log.md                     # standards change history
    CLAUDE.md                  # thin agent-facing pointer (auto-loaded; harness file, not a concept)
    architecture/ code/ naming/ data-modeling/ ci-cd/ workflows/ mlops/ quality/ platform/
                               #   each: index.md + one standard per file (type: standard)
  catalog/                     # our data — <system>/{index.md, access.md} · <catalog>/<schema>.md · <schema>/<table>.md
  decisions/                   # ADRs — NNNN-slug.md (type: decision)
  vision/                      # direction by area — <area>.md (type: vision)
  backlog/                     # raw idea inbox (pre-brainstorming) — <idea-slug>.md (type: idea)
  documentation/               # product docs (Diátaxis prose) — getting-started/ how-to/ reference/ concepts/ (type: documentation)
  knowledge/                   # generic knowledge we hold — subject subfolders (type: knowledge)
                               #   ships one FIXED file: glossary.md (the A–Z term lookup)
  reference/                   # what we consume — tools/ libraries/ regulations/ (type: reference; PDFs via sidecar)
  communications/              # outbound — templates/ (type: communication-template) · archive/ (type: communication)
  presentations/               # human deliverables — slides/ diagrams/ reports/ (binary via sidecar, type: sidecar)
```

## The `type` vocabulary (the greppable signature)

`type` is mandatory and non-empty on every concept doc. Fixed per home:

| Home | `type` | Identity (path) |
| --- | --- | --- |
| `standards/**` | `standard` | `standards/<subject>/<concept>.md` |
| `catalog/<system>/access.md` | `system` | the access card |
| `catalog/**/<schema>.md` | `schema` | consolidated index |
| `catalog/**/<schema>/<table>.md` | `table` | detailed page |
| `decisions/` | `decision` | `NNNN-slug.md` |
| `vision/` | `vision` | `<area>.md` |
| `backlog/` | `idea` | `<idea-slug>.md` |
| `documentation/**` | `documentation` | `getting-started/`·`how-to/`·`reference/`·`concepts/` |
| `knowledge/` | `knowledge` | subject subfolders |
| `reference/` | `reference` | `tools/`·`libraries/`·`regulations/` |
| `communications/templates/` | `communication-template` | one per channel |
| `communications/archive/` | `communication` | `YYYY-MM-DD-<scope>-<slug>.md` |
| `presentations/` · `reference/regulations/` (extracts) | `sidecar` | one per binary |

Reserved `index.md`/`log.md` carry **no** `type`; `CLAUDE.md`/`AGENTS.md` are exempt.

## Boundary rules (memorable summary)

- `standards/` = "how **WE** do it (current/active)".
- `knowledge/` = "generic **understanding** we hold" (concepts/explanations; non-binding, background).
- `documentation/` = "**prose docs for humans**, Diátaxis-structured (the published site)".
- `reference/` = "facts about what **WE CONSUME** (external, background)".
- `catalog/` = "our **data** / domain".
- `communications/` = "**messages we send to an audience**" (directed, dated; template per channel).
- `presentations/` = "our **visual** deliverables" (LLM reads the sidecar, never the binary).
- `decisions/` → `standards/` **on implementation** (distills and leaves).
- **`patterns` is not a silo** — it dissolves into `standards/architecture/`.

## The homes, one by one

- **`standards/`** — current/active contracts, one standard per file, subject subfolders.
  `type: standard` + a `resource:` **derived from `file:line` anchors** (never invented).
  Two front-doors: `index.md` (listing, with a DERIVED "Current docs" zone) and `CLAUDE.md`
  (thin agent pointer). Each subject carries a **candidate sub-standards** catalog and a
  **coverage/deferral ledger** — a consideration checklist, evidence-gated generation,
  recorded deferral (not a blind generate list). Internal boundary: `code/` governs
  **symbols**, `naming/` governs **data**.
- **`decisions/`** — an ADR is a decision **not yet implemented**; one per file
  (`NNNN-slug.md`, `type: decision`). On implementation it **distills into `standards/`** and
  leaves the tree (git + the "Distilled ledger" keep the trail).
- **`vision/`** — direction segmented by area (`<area>.md`, `type: vision`), **no deadline**.
  A raw idea toward it → `backlog/`; what became reality → `standards/`.
- **`backlog/`** — the **raw idea inbox** (`type: idea`): fast, low-ceremony capture of a
  thought before its scope/direction is decided, feeding `superpowers:brainstorming`. Flat
  (`<idea-slug>.md`, no pillar subfolders); no `vision_refs`/done-criteria. Once brainstorming
  develops an idea into an approved spec, the idea **leaves** the tree (Developed ledger in
  `backlog/index.md` keeps the trail).
- **`documentation/`** — prose documentation for human readers, Diátaxis-structured; the
  home rendered as the product's documentation site (`type: documentation`). Four fixed
  subfolders: `getting-started/` (tutorial), `how-to/` (task recipes — absorbs the former
  `guides/`), `reference/` (our product's own reference), `concepts/` (explanation).
  Boundary: a published-site page → here; internal team understanding → `knowledge/`; a
  current contract → `standards/`. `audience: human`, `authority: current` by default. The
  plugin ships a mkdocs-material site setup (config + awesome-pages nav) that
  `quenching-align` installs at the repo root.
- **`knowledge/`** — generic, cross-cutting understanding the team holds (`type: knowledge`):
  domain concepts, glossaries, mental models, explanations, learnings — the Diátaxis
  **explanation** quadrant raised to a home, subject subfolders welcome. Non-binding and
  usually `authority: background`. Boundary: it is **not** a contract (→ `standards/`), **not**
  a fact about a named external asset we consume (→ `reference/`), and **not** a procedure
  (→ `documentation/how-to/`). If understanding hardens into a rule for how we build, it distills into
  `standards/` and leaves. Ships **one fixed file** — `knowledge/glossary.md`, the repo's A–Z
  term lookup (a flat, alphabetically sorted bullet list in the same syntax every `index.md`
  uses — the one deliberate exception to "one concept per file", and the one place an
  unlinked entry is a valid permanent state). `quenching-align` installs the seed;
  `quenching-glossary` enriches one term on demand, `quenching-knowledge-scan` backfills the
  whole bundle in one sweep, and the other knowledge skills enrich it as a tail step.
- **`reference/`** — external facts we consume (`type: reference`); a regulation's PDF lives
  here via a **sidecar**, while *our* implementation of it lives in `standards/`.
- **`catalog/`** — the data: `system → catalog → schema → table`. `<system>/index.md` is a
  listing; `<system>/access.md` is the access card (`type: system`, secret by reference).
  Two granularities (consolidated `<schema>.md` × detailed `<schema>/<table>.md`);
  generated × curated kept separate ("X defines Y").
- **`communications/`** — outbound announcements with a fixed **scannable header**; one
  **template per channel** (`type: communication-template`) ships as structure; issued
  announcements go to `archive/` (`type: communication`, dated). A message that becomes a rule
  distills to `standards/`.
- **`presentations/`** — human visual deliverables; the LLM reads the **sidecar**
  (`type: sidecar`), never the binary.

## Authoring conventions (all homes)

- **The folder carries the subject — the filename does not repeat it.** In `naming/`, the doc
  is `columns.md`, not `naming-columns.md`. Kebab-case, no accents, one concept per file. **The
  one exception is `knowledge/glossary.md`** — a glossary is inherently a multi-term aggregate, so
  it is a single fixed file holding many term entries, not a concept doc per term.
- **Folders over prefix-clusters — favor a folder when it earns its keep.** A run of sibling
  files sharing a subject prefix (`nomenclatura-classes.md`, `nomenclatura-funcoes.md`,
  `nomenclatura-modulos.md`, …) is the same "filename repeats the subject" smell one level up:
  the prefix is the folder. Fold the cluster into a subfolder named for the subject
  (`symbol-naming/{classes,functions,modules,…}.md`) with its own `index.md`. Keep files flat
  when the folder would be ceremony — a lone doc, an incoherent prefix, two short siblings on an
  axis unlikely to grow. Rule of thumb: **≥3 siblings on a coherent axis → folder; ≤2 → judge by
  whether the axis is real and expected to grow.**
- **Structure is canonical English; content may be local.** Folder names **and file slugs**,
  frontmatter keys, enum values, and the `type` vocabulary are English (cross-repo greppable) —
  `nomenclatura-variaveis.md` → `naming/variables.md`. Frontmatter stays English; **body prose
  MAY follow the repo's language.** **Identifier-derived slugs are verbatim, never translated:**
  a catalog `<schema>`/`<table>` mirrors the real object, `reference/repositories/<repo>` the
  real repo, an ADR keeps its `NNNN-` prefix — translating them would break the greppable tie to
  the asset. `audience: human` homes (`presentations/`, `communications/`) may use the repo's
  language for slugs and free-text.
- **Links:** relative **within** a home; absolute from the bundle root (`/docs/...`) when
  leaving for another home — so cross-links survive a home move/migration.
- **Every knowledge-holding folder has an `index.md`.** A directory that holds concept docs
  carries a reserved, frontmatter-free `index.md` listing its real children (the validator's
  `dir-no-index`/`index-broken-link`/`index-orphan` checks enforce this deterministically).
- **Content × home:** homes are by **subject** (subject-first); content **within** a home
  follows **Diátaxis** (tutorial / how-to / reference / explanation).
