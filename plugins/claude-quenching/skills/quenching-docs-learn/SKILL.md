---
name: quenching-docs-learn
description: >-
  Captures ONE piece of generic knowledge the human states into the OKF docs/ bundle's
  knowledge/ home with a conformant `type: knowledge` stamp. Use when the user asks to
  "add this knowledge", "record what we learned", "capture this concept / glossary term /
  explanation", "save this domain understanding", "document this mental model", or "put
  this in the knowledge base". Confirms it is generic understanding, files it under
  knowledge/<subject>/, updates knowledge/index.md and log.md, enriches the glossary, and
  self-checks. Not for: a rule or decision for how WE build (a standard), a how-to, or an external
  tool/lib fact → quenching-docs-add; draining project memory → quenching-docs-import-memory.
when_to_use: >-
  filing ONE piece of generic understanding into knowledge/.
allowed-tools: Read, Grep, Glob, Write, Edit
user-invocable: false
---

# quenching-docs-learn — capture generic knowledge, OKF-conformant

Files one piece of understanding the human gives you into the canonical OKF bundle's
[`knowledge/`](../../assets/docs/knowledge/index.md) home — the Diátaxis **explanation**
quadrant raised to a home: domain concepts, glossaries, mental models, explanations, learnings.
Assumes the bundle already exists (run `quenching-docs-align` first if not). The mold lives at
`${CLAUDE_PLUGIN_ROOT}/assets/templates/concept-front.md`; the home boundaries and the
index/log procedure are shared with `quenching-docs-add`
([../quenching-docs-add/references/homes.md](../quenching-docs-add/references/homes.md)); the `type` vocabulary
and conformance rules with `quenching-docs-align`
([../quenching-docs-align/references/taxonomy.md](../quenching-docs-align/references/taxonomy.md),
[.../conformance.md](../quenching-docs-align/references/conformance.md)).

## Doctrine

- **`knowledge/` is generic understanding, not a contract.** It holds what the team
  **understands** (a concept, glossary term, explanation, learning) — non-binding and usually
  `authority: background`. Before writing, confirm the home. If the information is really "how
  **WE** do it" it is a `standard` (an agreed-but-unproven rule or decision is a `standard` with
  `authority: background` — there is no separate ADR home); a set of steps for using the product
  is `documentation`; a fact about a **named** external tool/lib/regulation is `reference`. When it belongs elsewhere,
  **stop and route via `quenching-docs-add`** rather than mis-filing it under `knowledge/`.
- **One concept per file; the path is the identity.** The subject subfolder carries the
  subject, so the filename does not repeat it (`domain/idempotency.md`, not
  `domain/domain-idempotency.md`). Kebab-case, no accents; **canonical English slug** (frontmatter
  keys and enums are English too — body prose MAY follow the repo's language). If the subject
  already holds a cluster of siblings, file the new concept **inside that subfolder**.
- **`type` mandatory; `resource` derived, never invented.** `type: knowledge`. `resource`
  points to **what the knowledge concerns** — a domain descriptor, a code glob, a source URL,
  or the origin the human cited. Empty or self-pointing is disallowed; never fabricate a source.
- **Attribute honestly.** `source` is who supplied the knowledge (the human, a named person,
  an external work). Default `authority: background`; use `authority: current` only for
  understanding the team treats as settled and foundational.
- **MERGE, never clobber.** If the target file exists, fill missing keys and preserve filled and
  third-party ones; extend the doc rather than overwrite it.
- **Keep the listing honest.** Every capture updates `knowledge/index.md`; a lying index is drift.
- **Feed the glossary.** `knowledge/` ships one fixed file — `glossary.md`, the repo's A–Z term
  lookup. A capture that introduces a repo-specific term ends by adding its entry there (MERGE,
  alphabetical, linked to the concept doc), so any agent can resolve the term the moment it lands.
  `quenching-docs-glossary-backfill` is the whole-bundle counterpart that backfills terms already sitting
  in `docs/` but never fed into the glossary — this skill only ever looks at the capture in hand.

## Workflow

### 1. Confirm the home
Read the knowledge the human stated. Confirm it is **generic understanding** (not a contract /
decision / procedure / external-asset fact). If it belongs in another home, say so and hand off
to `quenching-docs-add`. Otherwise proceed under `knowledge/`.

### 2. Determine identity (path)
Pick (or create) the `knowledge/<subject>/` subfolder for the concept — e.g. `domain/`,
`glossary/`, `concepts/`. Concept ID = the path without `.md`; one concept per file; kebab-case;
**English slug**. If the subject already carries a cluster subfolder, nest inside it. If the
concept creates a **new** subfolder, that subfolder needs its own `index.md`.

### 3. Fill the mold
Copy `${CLAUDE_PLUGIN_ROOT}/assets/templates/concept-front.md` and complete the frontmatter:
`type: knowledge` + the OKF recommended fields (`title`/`description`/`resource`/`timestamp`)
+ the method labels (`audience` — usually `both`; `authority` — usually `background`;
`source` — who supplied it; `maintainer`). Derive `resource`; use today's date for `timestamp`.

### 4. Write the concept doc
Write the file with `Write`. Favor structural markdown (headings, lists, tables). Cross-home
links absolute (`/docs/...`); within-home links relative. Body prose MAY be the repo's language.

### 5. Update `knowledge/index.md`
Add a bullet-link with the doc's `description`
(`* [<title>](<rel-path>.md) — <description>`) under the right subject. If you created a new
subfolder, create its frontmatter-free `index.md` and link it from `knowledge/index.md`. Never
add frontmatter to an `index.md`.

### 6. Append to `log.md`
Per **Appending to `log.md`** in
[../quenching-docs-add/references/homes.md](../quenching-docs-add/references/homes.md), with the entry:
`**Creation**: [<title>](/docs/knowledge/<path>.md) — <one line>`.

### 7. Enrich the glossary
If the concept introduced a **repo-specific term**, add or sharpen its entry in
`knowledge/glossary.md` per **Enriching the glossary** in
[../quenching-docs-add/references/homes.md](../quenching-docs-add/references/homes.md) (the tail step
every capture runs; on-demand counterpart `quenching-docs-define`, bulk counterpart
`quenching-docs-glossary-backfill`).

### 8. Self-check against the conformance core
Verify every file you touched against
[../quenching-docs-align/references/conformance.md](../quenching-docs-align/references/conformance.md) —
the same checks the installed `okf-validate.py` hook (if wired) machine-verifies on write.

## Invariants to never violate

- Never file a **contract / decision / procedure / external-asset fact** under `knowledge/` —
  route it to its home via `quenching-docs-add`.
- Never write an empty or self-pointing `resource`, and never fabricate a `source`.
- Never add frontmatter to an `index.md`; never leave a new subfolder without one.
- Never overwrite a filled key on merge; never leave the index or log un-updated.
- Never skip the glossary tail step when the concept names a repo-specific term — but never
  clobber a filled glossary entry, and never fold a term's full explanation into the glossary
  (it holds the one-liner + the link; the depth stays in the concept doc).
