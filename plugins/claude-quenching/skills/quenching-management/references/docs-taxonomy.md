# Canonical taxonomy of `docs/` — the single source of the tree

> **Path back:** [../SKILL.md](../SKILL.md) (agent roadmap) ·
> human overview & architecture: the project docs site ·
> [README.md](README.md) (`references/` index).

> **This is the CANONICAL specification of `docs/`.** Dimension 2
> ([dimensions-template.md](dimensions-template.md)), detection
> ([detection-and-smells.md](detection-and-smells.md)) and the baseline-payload
> (`../assets/docs/`) **point here** — they do not repeat the tree. Keep this
> file navigable: it is the single source of the canonical taxonomy.

## Prescriptive rule

The skill defines a **canonical taxonomy** of `docs/` with **fixed names**. The repo
**converges to the skill**, not the other way around: **every repo converges to the SAME
tree of identical names**, and a variant name (`docs/arquitetura/` instead of
`docs/standards/`) is a **non-convergence smell** — a candidate for migration, not a
convention to preserve.

Portability comes from this convergence: anyone moving between repos sees the tree
**literally identical** — `docs/standards/`, `docs/decisions/`, `docs/reference/`
in the same place in all of them. This is "a predictable place… the nearest file" taken to
the **whole set** of `docs/`, not just the repo root.

**Language:** folder names in **English kebab-case** (stable across repos,
independent of the project's language); the **content** inside each home follows the
repo's language. The current/active layer index is called **`INDEX.md`** (not
`INDICE.md`).

**Content × home:** the **homes** are by **subject** (subject-first — GitLab
*"primarily follow the structure of the GitLab UI or API"*, "put files for a
specific product area into the related folder"); the **content inside each home**
follows **Diátaxis** (tutorial / how-to / reference / explanation). Home = subject;
text form within the home = Diátaxis.

## The canonical tree (locked)

```
docs/
  standards/          # CURRENT/ACTIVE reference — OUR contracts/conventions
    architecture/     # system structure + architectural patterns (patterns dissolve HERE)
    code/             # code conventions, imports, lint, pins, SYMBOL naming
    naming/           # DATA naming (tables/columns/descriptions) — globally unique name
    data-modeling/    # grain, key, joins, catalog/schema choice (the "database")
    ci-cd/            # build/deploy, "code defines YAML", manifest generation
    workflows/        # job/task/schema framework, job parameters
    mlops/            # model lifecycle, lineage, regulatory interface (Res. 4.966)
    quality/          # data quality (per row), data drift/stability, model monitoring
    platform/         # deploy targets, permissions/governance, external services
  decisions/          # ADR — OPEN decision; upon implementation, distills to standards/ and LEAVES
  vision/             # direction SEGMENTED by area — empty shells + comment, no deadline
  backlog/            # what is missing, by pillar
  guides/             # how-to + tutorials; the REPO organizes (preferably in subfolders by subject). onboarding is just one example of a guide, not a fixed home
  reference/          # EXTERNAL reference material (factual, background) — via sidecar
    tools/            # tool docs
    libraries/        # library docs
    regulations/      # regulatory rules (PDFs via sidecar)
  catalog/            # data catalog / domain (generated + curated, SEPARATE)
    <system>/         # physical origin (postgres/sqlserver/databricks-uc/bigquery); README.md = access + scripts
      <catalog>/      # catalog(UC)/database/project → <schema>.md (consolidated) + <schema>/<table>.md (detailed)
  communications/     # DIRECTED/outbound communication — announcements to an audience (incident/change/deploy/outage/migration/news)
    templates/        # one template PER CHANNEL (email/chat/wiki/markdown) — STRUCTURE that the package ships
    archive/          # concrete announcements already issued (repo content, dated) — the repo creates
  presentations/      # HUMAN deliverables (via sidecar; the LLM never opens the binary)
    slides/
    diagrams/
    reports/
```

## The homes, one by one

For each home: **purpose**, **Diátaxis type** of content, **`audience:`**,
**`authority:`** and the **boundary** that separates it from its neighbors.

### `standards/` — current/active reference, OUR contracts
- **Purpose:** the current/active standard/contract (how it should be and why),
  versioned — the shared source of truth. Has an **`INDEX.md`** index in
  sync + one standard per file.
- **Diátaxis:** reference (and explanation of the *why* behind each standard).
- **`audience: both`** (human + LLM) or **`agent`** (LLM-first norm/spec).
- **`authority: current`** (contract; edited only by the owning skill).
- **Boundary:** `standards/` = "how **WE** do it (current/active)". Distinct from
  `reference/` (facts about what we **consume**, external) and from `catalog/`
  (our data). Direction does not live here (→ `vision/`); open decisions do not live
  here (→ `decisions/`).
- **Subfolders** (by subject, not type): `architecture/` (structure + architectural
  patterns — **`patterns` dissolves here**, there is no `docs/patterns/`);
  `code/` (code conventions, imports, lint, pins, **symbol** naming); `naming/`
  (**data** naming — tables/columns/descriptions, globally unique name);
  `data-modeling/` (grain, key, joins, catalog/schema choice); `ci-cd/`
  (build/deploy, "code defines YAML", manifest generation); `workflows/`
  (job/task/schema framework, job parameters); `mlops/` (model lifecycle, lineage,
  regulatory interface); `quality/` (data quality per row, drift/stability, model
  monitoring); `platform/` (deploy targets, permissions/governance, external
  services).
- **Internal boundary `code/` × `naming/`:** `code/` governs **symbols** (code);
  `naming/` governs **data** (tables/columns).

### `decisions/` — ADR, open decision
- **Purpose:** a decision **not yet implemented**, under debate, with weighed
  alternatives. One `NNNN-slug/` folder per ADR.
- **Diátaxis:** explanation ("why we decided, alternatives").
- **`audience: both`** · **`authority: background`** while open.
- **Boundary:** `decisions/` → becomes `standards/` **upon implementation** (distills and
  **leaves** the tree; history stays in git + in a "Distilled" ledger).
  A current/active decision does not stay here.
- **Canonical name:** `decisions/` — MADR recommends **verbatim**
  *"Create folder `docs/decisions` in your project"* and *"Decisions are placed in
  the subfolder `decisions/`"*.

### `vision/` — direction, segmented by area
- **Purpose:** where the platform is headed (target state, "what and why"),
  **without a schedule**. **Segmented by area** (one shell per pillar/area), not a
  single `VISION.md`.
- **Diátaxis:** explanation (of the direction).
- **`audience: both`** · **`authority: background`** (aspiration, not contract).
- **Boundary:** direction **carries no deadline/milestone/order**; "what is missing" → `backlog/`;
  what has already become reality → distills to `standards/`. Empty shells are created with
  a comment declaring the pillar.
- **Canonical name:** `vision/` — folder segmented by area, not a single `VISION.md`.

### `backlog/` — what is missing
- **Purpose:** trackable items of what is still missing, **by pillar/area**.
- **Diátaxis:** how-to of pending work.
- **`audience: both`** · **`authority: background`**.
- **Boundary:** completed item **leaves** the tree (history in git); references
  the direction (`vision_refs`); no deadline/order; does not duplicate an ADR.

### `guides/` — how-to + tutorials
- **Purpose:** step-by-step procedures (how-to) and learning material
  (tutorial) for team members.
- **Diátaxis:** how-to + tutorial.
- **`audience: both`** · **`authority: background`** (procedure, not contract).
- **Boundary:** how-to ("how do I do X") ≠ reference ("what it is / how it is today", →
  `standards/`) ≠ explanation ("why", → `decisions/`/`vision/`).
- **How to organize (the REPO decides):** `guides/` is the **home for guides** — the skill
  does not prescribe which guides exist nor ships any ready-made ones. **Prefer
  a folder/subfolder structure by subject/area** (subject-first), defined by the
  repo as it makes sense (e.g.: `guides/deploy/`, `guides/pipelines/`); standalone guides
  live as `.md` files directly in `guides/`. An *onboarding* guide (entry track for
  new devs) is just **one example** of a guide — the repo creates it if it wants,
  it is not a fixed file or fixed home.
- **Subfolders by SUBJECT are welcome; silos by AUDIENCE are not.** Subfolders that
  the repo creates by subject/area are encouraged (subject-first). What the skill
  does **not** prescribe is a fixed silo by **audience** — there is no reserved
  `guides/onboarding/`, because "onboarding" is an audience slice (and almost every
  how-to already serves as onboarding), not a distinct subject. Organization by folders:
  yes; reserving a folder by audience: no.

### `reference/` — EXTERNAL reference material
- **Purpose:** **factual material about what WE CONSUME** — tool docs,
  library docs, regulatory rules. External to what we produce.
- **Diátaxis:** reference (factual).
- **`audience: agent`** (consumed via sidecar) · **`authority: background`**
  (background/reference, **never** our contract).
- **Boundary (the most subtle):** `reference/` = "facts about what we **CONSUME**
  (external)" — distinct from `standards/` ("how **WE** do it", current/active) and from
  `catalog/` ("our **data**/domain"). A regulatory rule (PDF) lives
  in `reference/regulations/` with a **sidecar** (the LLM reads the extract, not the binary);
  **our** interface to the rule (how we implement Res. 4.966) lives in
  `standards/mlops/`.
- **Subfolders:** `tools/`, `libraries/`, `regulations/`.

### `catalog/` — data catalog / domain
- **Purpose:** table/model metadata (**generated**) + editorial curation
  (**curated**), **separate** — to **direct the LLM** to understand the data and
  find where to look for more.
- **Diátaxis:** reference (of domain).
- **`audience: both`** · generated `authority: current` (mirrors the source) / curated
  `authority: current`.
- **4-level hierarchy:** `<system>/<catalog>/<schema>/<table>` — `system`
  is the physical origin (PostgreSQL, SQL Server, Databricks/UC, BigQuery…), and its
  `README.md` holds **how to access it** (type, connection, **secret by
  reference**, never the credential) and **where the scripts are** that build the
  tables.
- **Two granularities:** **consolidated** (`<schema>.md`, one row per table,
  **without** columns — when the source does not expose descriptions) × **detailed**
  (`<schema>/<table>.md`, with columns + **Build**/scripts + Related).
  Promoted from consolidated to detailed when there is a description; no empty detailed
  page is created.
- **Boundary:** AUTO-GENERATED and curation **separate** (generated is never edited by
  hand — "X defines Y" rule; system without a generator has entirely curated pages).
  `catalog/` = "the **data** we produce/consume" — distinct from `reference/`
  (external) and `standards/` (our code/process contracts).
- **Templates** (in `assets/templates/docs/catalog/`): `system.md` (access sheet +
  scripts), `schema.md` (consolidated index), `table.md` (detailed page).

### `communications/` — directed communication (outbound)
- **Purpose:** **announcements to an audience** — *outbound* messages directed to
  an audience (business, team, stakeholders): incident, change, deploy,
  outage/maintenance, migration, news, status update. They are
  **scannable** (the reader decides in seconds whether it matters), **dated** and
  **archivable** (ephemeral at issuance, but preserved for audit).
- **Diátaxis:** **outside the four types** — directed communication is a **form
  of text of its own** (message to an audience), just as `presentations/` is binary
  material. It is not tutorial/how-to/reference/explanation.
- **`audience: human`** (the announcement speaks to a human audience) ·
  **`authority: background`** (it is a message/record, **never** a current/active contract).
- **Structure (what the package ships) × content (what the repo creates):** the package
  carries the **structure** — the home + one **template per channel** in `templates/`
  (generic placeholders) + the **generic skill** that reads them. The **content** (the
  actual scopes, status values, the concrete audience, each issued announcement)
  is the REPO's decision — same boundary of structure-installer-not-content-installer
  as `guides/`. A concrete issued announcement lives in `archive/` (dated).
- **Scannable header (form invariant):** every announcement opens with a
  **fixed header** of high-signal fields — **scope · status · impact ·
  audience · validity · required action · last updated** — followed by
  **summary (one sentence)** + short description. The reader decides **by reading only the
  header** whether to continue.
- **Template PER CHANNEL:** each channel has **its own** template in
  `communications/templates/` (same logical header, form adapted to the channel):
  `email.md` (key fields in the **subject line**), `chat.md` (Slack/Teams — **edit the
  original message** on each update, pin while open), `wiki.md`
  (Confluence/Notion — header becomes a filterable **properties table**),
  `markdown.md` (neutral, works in any renderer — the default when the
  channel has not been specified). The repo adds a template when adopting a new
  channel (channel without template = smell).
- **Boundary:** `communications/` = "**messages we send to an audience**"
  (transient, dated) — distinct from `guides/` (how-to: "how do I do X", not
  directed at an announcement), from `decisions/` (ADR: "why we decided"), from
  `standards/` (current/active contract) and from `presentations/` (visual **binary**
  deliverable, consumed via sidecar — an announcement is **text**, read directly). An
  announcement that becomes a permanent rule **distills to `standards/`**; the
  communication itself stays in `archive/` as a historical record.

### `presentations/` — human deliverables (binary)
- **Purpose:** our **visual deliverables** — slides, source diagrams,
  reports. Binaries that belong in `docs/` but **not** in the normative layer.
- **Diátaxis:** outside the four types (human material, not a technical doc).
- **`audience: human`** (the binary) · **`authority: background`**; the **sidecar**
  is `audience: agent`/`authority: background`.
- **Boundary:** the LLM **never opens the binary** — it reads the **sidecar `.md`** alongside
  (summary + key points + `binary:` pointing to the source). `presentations/` =
  "our **visual** deliverables" — distinct from `reference/` (external factual reference).
  Content that has become current/active **distills** to `standards/`.
- **Subfolders:** `slides/`, `diagrams/`, `reports/`.

## Boundary rules (memorable summary)

- `standards/` = "how **WE** do it (current/active)".
- `reference/` = "facts about what we **CONSUME** (external, background)".
- `catalog/` = "our **data**/domain".
- `communications/` = "**messages we send to an audience**" (directed, dated; template per channel).
- `presentations/` = "our **visual** deliverables".
- `decisions/` → `standards/` **upon implementation** (distills and leaves).
- **`patterns` IS NOT a silo** — it dissolves into `standards/architecture/`.

## Variant migration doctrine

In an **existing** repo with variant names, the skill **proposes convergence to the
canonical name** — in a **deterministic and prescriptive** manner, but **safely**:

1. **Map variant → canonical.** Via Step 0 ([detection-and-smells.md](detection-and-smells.md)),
   each existing section matches a canonical home by function:
   `docs/arquitetura/` → `docs/standards/`; `docs/adr/` or `docs/decisions` →
   `docs/decisions/`; `VISION.md` / `ROADMAP.md` → `docs/vision/`;
   `docs/catalogo_dados/` / `docs/dominio/` → `docs/catalog/`;
   `docs/apresentacoes/` / `docs/diagramas/` / `docs/normativos/` →
   `docs/presentations/` or `docs/reference/regulations/` depending on content.
2. **Flag the variant as DEPRECATABLE.** A variant name is a **non-convergence smell**
   — it enters the "Deprecatable" section of the report with the proposed canonical destination.
3. **PROPOSE the migration; NEVER rename/delete without OK.** Human confirmation and
   the "do not delete without OK" rule from the deprecation doctrine ([installation.md](installation.md))
   **remain in effect**. Deterministic ≠ automatic: the mapping is repeatable, but
   each migration goes through Step 5 confirmation.
4. **Install only the missing canonical homes that apply.** A repo without data does not
   receive `catalog/`; the baseline is completeness **of what fits**, not a blind checklist.
