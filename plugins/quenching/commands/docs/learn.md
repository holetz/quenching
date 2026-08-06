---
description: Capture ONE piece of generic knowledge into the bundle's knowledge/ home. Triggers on "add this knowledge", "record what we learned", "put this in the knowledge base". Not for: a full contract/decision/procedure/external-asset doc → /docs:add; ONE glossary term → /docs:define.
argument-hint: [the-knowledge]
allowed-tools: Read, Grep, Glob, Write, Edit
---

# /quenching:docs:learn — capture generic knowledge, OKF-conformant

**Input**: `$ARGUMENTS` (the generic understanding to capture — a concept, mental model, explanation, or learning).

Files one piece of understanding the human gives you into the canonical OKF bundle's
[`knowledge/`](${CLAUDE_PLUGIN_ROOT}/assets/docs/knowledge/index.md) home — the Diátaxis **explanation**
quadrant raised to a home: domain concepts, glossaries, mental models, explanations, learnings.
Assumes the bundle already exists (run `/quenching:docs:align` first if not). The mold lives at
`${CLAUDE_PLUGIN_ROOT}/assets/templates/concept-front.md`; the home boundaries and the
index/log procedure are shared with `/quenching:docs:add`
([docs-add/homes.md](${CLAUDE_PLUGIN_ROOT}/assets/references/docs-add/homes.md)); the `type` vocabulary
and conformance rules with `/quenching:docs:align`
([docs-align/taxonomy.md](${CLAUDE_PLUGIN_ROOT}/assets/references/docs-align/taxonomy.md),
[docs-align/conformance.md](${CLAUDE_PLUGIN_ROOT}/assets/references/docs-align/conformance.md)).

## Doctrine

- **`knowledge/` is generic understanding, not a contract.** It holds what the team
  **understands** (a concept, glossary term, explanation, learning) — non-binding and usually
  `authority: background`. Before writing, confirm the home. If the information is really "how
  **WE** do it" it is a `standard` (an agreed-but-unproven rule or decision is a `standard` with
  `authority: background` — there is no separate ADR home); a set of steps for using the product
  is `documentation`; a fact about a **named** external tool/lib/regulation is `reference`. When it belongs elsewhere,
  **stop and route via `/quenching:docs:add`** rather than mis-filing it under `knowledge/`.
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
  `/quenching:docs:glossary-backfill` is the whole-bundle counterpart that backfills terms already sitting
  in `/.docs/` but never fed into the glossary — this skill only ever looks at the capture in hand.

## Workflow

### 1. Confirm the home
Read the knowledge the human stated. Confirm it is **generic understanding** (not a contract /
decision / procedure / external-asset fact). If it belongs in another home, say so and hand off
to `/quenching:docs:add`. Otherwise proceed under `knowledge/`.

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
links absolute (`/.docs/...`); within-home links relative. Body prose MAY be the repo's language.

### 5. Update `knowledge/index.md`
Add a bullet-link with the doc's `description`
(`* [<title>](<rel-path>.md) — <description>`) under the right subject. If you created a new
subfolder, create its frontmatter-free `index.md` and link it from `knowledge/index.md`. Never
add frontmatter to an `index.md`.

### 6. Enrich the glossary
If the concept introduced a **repo-specific term**, add or sharpen its entry in
`knowledge/glossary.md` per **Enriching the glossary** in
[docs-add/homes.md](${CLAUDE_PLUGIN_ROOT}/assets/references/docs-add/homes.md) (the tail step
every capture runs; on-demand counterpart `/quenching:docs:define`, bulk counterpart
`/quenching:docs:glossary-backfill`).

### 7. Self-check against the conformance core
Verify every file you touched against
[docs-align/conformance.md](${CLAUDE_PLUGIN_ROOT}/assets/references/docs-align/conformance.md) —
the same checks the installed `okf-validate.py` hook (if wired) machine-verifies on write.

## Invariants to never violate

- Never file a **contract / decision / procedure / external-asset fact** under `knowledge/` —
  route it to its home via `/quenching:docs:add`.
- Never write an empty or self-pointing `resource`, and never fabricate a `source`.
- Never add frontmatter to an `index.md`; never leave a new subfolder without one.
- Never overwrite a filled key on merge; never leave the index or log un-updated.
- Never skip the glossary tail step when the concept names a repo-specific term — but never
  clobber a filled glossary entry, and never fold a term's full explanation into the glossary
  (it holds the one-liner + the link; the depth stays in the concept doc).
