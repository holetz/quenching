---
description: Import an external source (files/folders/URLs) into the OKF bundle as many docs
argument-hint: [source-paths-or-urls]
allowed-tools: Read, Grep, Glob, WebFetch, Write, Edit, Task
---

# /docs:import — import an external source into the OKF bundle

**Input**: `$ARGUMENTS` (the source to ingest — local file/folder paths, or URLs).

A Claude-native analogue of the OKF reference implementation's `enrich` command — **without**
BigQuery or heavy dependencies. It reads an external source (local files/folders, or URLs)
and mints **multiple** conformant OKF concept docs from it. It is a **batch fan-out of
`/docs:add`**: [`docs-add/homes.md`](${CLAUDE_PLUGIN_ROOT}/assets/references/docs-add/homes.md)
is the **single owner** of the per-doc procedure (classify → stamp → index → log → glossary →
self-check); this skill **cites** it and adds only the ingestion-safety deltas below. Source
scoping, the bounded-crawl rules, unit extraction, dedup, and attribution are in
[docs-import/sources.md](${CLAUDE_PLUGIN_ROOT}/assets/references/docs-import/sources.md). Requires an existing OKF bundle — run
`/docs:align` first if `docs/` is not one.

## Doctrine (own deltas; the per-doc procedure is homes.md)

- **Cite, don't restate.** Every per-doc step — home + `type` + mold classification, the
  frontmatter stamp, updating `index.md`, enriching the glossary, self-check — lives in
  homes.md. This skill restates none of it; it adds only these deltas.
- **Bounded ingestion (discipline, not code).** A web source is bounded **up front**: an
  explicit **seed list**, a **page cap**, and a **host allowlist** — never an open crawl
  (echoing the upstream enrich caps). Fetch only what the user named, plus links **within the
  allowed hosts** up to the cap; report everything you did **not** fetch.
- **Anti-fabrication.** Mint only what the source actually supports. A rule not proven in the
  **target's own** code enters as `authority: background` (a proposal), never
  `authority: current`. Never invent a `resource:` — derive it from the source (a glob set of
  what the doc governs, or the URL). Every minted doc is **attributed** to its source.
- **MERGE, never clobber.** A unit that maps to an existing doc/term is an **enrich** target —
  fill missing keys, sharpen the body — never overwrite a filled field or a filled body.
- **Never ingest transient / secret / PII.** Skip credentials, tokens, personal data, and
  ephemeral chatter — they are not durable knowledge. A secret is **referenced, never copied**
  (the catalog access-card rule).
- **Additive only.** Enrich never deletes a source or a bundle doc; it mints and merges.

## Workflow (force-with-1-confirmation, like `/docs:align`)

### 1. Scope the source (read-only)
Identify the inputs: local files/folders (`Read`/`Glob`/`Grep`) or URLs (`WebFetch`). For a
web source, fix the **seed list**, **page cap**, and **host allowlist** *before* fetching
anything, and fetch nothing outside them ([docs-import/sources.md](${CLAUDE_PLUGIN_ROOT}/assets/references/docs-import/sources.md)).
Read the source; write nothing yet.

### 2. Extract → classify → dedup
Break the source into **knowledge units** (one concept each). Classify every unit into
home + `type` + mold via homes.md §Classification.

Then **dedup** exactly as [sources.md](${CLAUDE_PLUGIN_ROOT}/assets/references/docs-import/sources.md)
§Dedup fixes it — within the source, then against the bundle, and against the bundle **by exact
`source_uri` before resemblance**. What this step owes step 3 is the verdict that ordering
produces: every unit leaves here labelled **new**, **already imported** (an exact URI hit — the
doc it hit is the MERGE target), or **resembles an existing doc** (a judgement, not a match),
carrying the URI or the term that decided it. For a large source, fan **one `Task` sub-agent per source
slice** out to return **compact unit candidates** (home / `type` / path / one-line + source
anchor + its `source_uri`), never full bodies; the orchestrator merges and judges. Extraction sub-agents may run
on a **cheap model/effort** — enrich **deletes nothing**, so a misclassification only misfiles
a doc (correctable), unlike `/docs:import-memory` (see the model policy in
[README.md §cost-model](${CLAUDE_PLUGIN_ROOT}/README.md#cost-model)).

### 3. Present ONE ingestion plan → gate on ONE OK
Show the **complete** plan: every doc to **mint** or **enrich** with its home, `type`, path,
one-line summary, and source anchor; and, for a web source, the seed/cap/allowlist and what was
left unfetched.

Every row also carries **why** it is a mint rather than an enrich — the step-2 verdict, with the
evidence under it: **new** (no URI hit and nothing resembling it); **already imported**, showing
the matching `source_uri:` and the doc it hit; or **resembles an existing doc**, showing the
title, slug or term that matched and the doc it matched. The last is the only one the human is
really being asked to check — an exact URI match needs no trust and a resemblance does, and
rendering the two identically is how a wrong MERGE hides inside a batch OK.

A single OK executes the whole batch. A
minted/edited doc whose change reaches the target's **product code** is its **own**
confirmation item (mirrors `/docs:align`) — never folded into the batch OK.

### 4. Execute on OK — mint each doc via the insert procedure
For each planned unit, run homes.md end to end: fill the mold (§The frontmatter stamp;
`authority: background` for an unproven standard), write the doc (cross-home links absolute,
within-home relative), update the folder's `index.md` (§Updating `index.md`), and enrich the
glossary if it introduced a repo-specific term (§Enriching the glossary). Fan **one `Task`
executor per slice** out for scale — the executors write docs; the **orchestrator alone** keeps
each `index.md` honest and resolves cross-slice dedup. Attribute each doc to its source.

### 5. Self-check + validate
Self-check every touched file against homes.md §Self-check /
[docs-align/conformance.md](${CLAUDE_PLUGIN_ROOT}/assets/references/docs-align/conformance.md),
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
