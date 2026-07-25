---
name: quenching-docs-import
description: >-
  Imports an external source into a repository's OKF docs/ bundle — reads arbitrary inputs
  (local files/folders via Read/Glob, or URLs via WebFetch) and mints MULTIPLE conformant
  OKF concept docs from them: a batch fan-out of the insert doctrine. Use when the user asks
  to "import/ingest a source into the base", "enrich the knowledge base from X", "generate
  OKF docs from these files/URLs", "pull this doc/site into docs/", "turn this source into
  the knowledge base", or "ingest this folder/page as OKF". Scopes the source read-only,
  extracts knowledge units and classifies each into its home + type + mold, dedupes within
  the source and against the existing bundle, presents ONE ingestion plan for one
  confirmation, then mints each doc (stamp → index → log → glossary) under the insert
  procedure. Requires an existing OKF bundle (run quenching-docs-align first). Not for: ONE doc
  the human states → quenching-docs-add; installing/aligning the docs structure →
  quenching-docs-align; draining ~/.claude project memory → quenching-docs-import-memory.
when_to_use: >-
  importing an external source (files/folders/URLs) into an existing OKF bundle as multiple
  minted concept docs. A batch fan-out of quenching-docs-add; one human-stated fact is
  quenching-docs-add, project-memory migration is quenching-docs-import-memory.
allowed-tools: Read, Grep, Glob, WebFetch, Write, Edit, Task
user-invocable: false
---

# quenching-docs-import — import an external source into the OKF bundle

A Claude-native analogue of the OKF reference implementation's `enrich` command — **without**
BigQuery or heavy dependencies. It reads an external source (local files/folders, or URLs)
and mints **multiple** conformant OKF concept docs from it. It is a **batch fan-out of
`quenching-docs-add`**: [`quenching-docs-add/references/homes.md`](../quenching-docs-add/references/homes.md)
is the **single owner** of the per-doc procedure (classify → stamp → index → log → glossary →
self-check); this skill **cites** it and adds only the ingestion-safety deltas below. Source
scoping, the bounded-crawl rules, unit extraction, dedup, and attribution are in
[references/sources.md](references/sources.md). Requires an existing OKF bundle — run
`quenching-docs-align` first if `docs/` is not one.

## Doctrine (own deltas; the per-doc procedure is homes.md)

- **Cite, don't restate.** Every per-doc step — home + `type` + mold classification, the
  frontmatter stamp, updating `index.md`, appending `log.md`, enriching the glossary,
  self-check — lives in homes.md. This skill restates none of it; it adds only these deltas.
- **Bounded ingestion (discipline, not code).** A web source is bounded **up front**: an
  explicit **seed list**, a **page cap**, and a **host allowlist** — never an open crawl
  (echoing the upstream enrich caps). Fetch only what the user named, plus links **within the
  allowed hosts** up to the cap; report everything you did **not** fetch.
- **Anti-fabrication.** Mint only what the source actually supports. A rule not proven in the
  **target's own** code enters as `authority: background` (a proposal), never
  `authority: current`. Never invent a `resource:` — derive it from the source (`file:line`,
  the URL). Every minted doc is **attributed** to its source.
- **MERGE, never clobber.** A unit that maps to an existing doc/term is an **enrich** target —
  fill missing keys, sharpen the body — never overwrite a filled field or a filled body.
- **Never ingest transient / secret / PII.** Skip credentials, tokens, personal data, and
  ephemeral chatter — they are not durable knowledge. A secret is **referenced, never copied**
  (the catalog access-card rule).
- **Additive only.** Enrich never deletes a source or a bundle doc; it mints and merges.

## Workflow (force-with-1-confirmation, like `quenching-docs-align`)

### 1. Scope the source (read-only)
Identify the inputs: local files/folders (`Read`/`Glob`/`Grep`) or URLs (`WebFetch`). For a
web source, fix the **seed list**, **page cap**, and **host allowlist** *before* fetching
anything, and fetch nothing outside them ([references/sources.md](references/sources.md)).
Read the source; write nothing yet.

### 2. Extract → classify → dedup
Break the source into **knowledge units** (one concept each). Classify every unit into
home + `type` + mold via homes.md §Classification. **Dedup** within the source *and* against
the existing bundle (`Grep` for an existing doc/term) — a unit that already has a home is a
**MERGE** target, not a new doc. For a large source, fan **one `Task` sub-agent per source
slice** out to return **compact unit candidates** (home / `type` / path / one-line + source
anchor), never full bodies; the orchestrator merges and judges. Extraction sub-agents may run
on a **cheap model/effort** — enrich **deletes nothing**, so a misclassification only misfiles
a doc (correctable), unlike `quenching-docs-import-memory` (see the model policy in
[../../README.md](../../README.md#cost-model)).

### 3. Present ONE ingestion plan → gate on ONE OK
Show the **complete** plan: every doc to **mint** or **enrich** with its home, `type`, path,
one-line summary, and source anchor; the dedup decisions; and, for a web source, the
seed/cap/allowlist and what was left unfetched. A single OK executes the whole batch. A
minted/edited doc whose change reaches the target's **product code** is its **own**
confirmation item (mirrors `quenching-docs-align`) — never folded into the batch OK.

### 4. Execute on OK — mint each doc via the insert procedure
For each planned unit, run homes.md end to end: fill the mold (§The frontmatter stamp;
`authority: background` for an unproven standard), write the doc (cross-home links absolute,
within-home relative), update the folder's `index.md` (§Updating `index.md`), append `log.md`
(§Appending to `log.md`), and enrich the glossary if it introduced a repo-specific term
(§Enriching the glossary). Fan **one `Task` executor per slice** out for scale — the
executors write docs; the **orchestrator alone** keeps each `index.md`/`log.md` honest and
resolves cross-slice dedup. Attribute each doc to its source.

### 5. Self-check + validate
Self-check every touched file against homes.md §Self-check /
[../quenching-docs-align/references/conformance.md](../quenching-docs-align/references/conformance.md),
then run `python3 "${CLAUDE_PLUGIN_ROOT}/assets/hooks/okf-validate.py" <docs-dir>` over the
bundle: **zero errors**, and the structural WARNs (`dir-no-index` / `index-broken-link` /
`index-orphan`) cleared. Report residue — units deferred, sources left unfetched, MERGE
targets skipped.

## Invariants to never violate
- **Never add `context: fork`.** This is a sweep skill: it gates on a mid-flow plan → OK,
  which a forked context cannot present (the [CLAUDE.md](../../../../CLAUDE.md) rule).
- Never mint beyond what the source supports; an unproven rule is `authority: background`,
  never `current`; never invent a `resource:`.
- Never overwrite a filled field or body — MERGE.
- Never ingest a secret/token/PII or transient chatter; **reference** a secret, never copy it.
- Never crawl unbounded — seed list + page cap + host allowlist, always; report what you
  skipped.
- Never delete a source or a bundle doc — enrich is mint-and-merge only.
