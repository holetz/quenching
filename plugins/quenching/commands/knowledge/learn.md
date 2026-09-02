---
description: Capture ONE piece of generic knowledge into the bundle's concepts/ home. Triggers on "add this knowledge", "record what we learned", "put this in the knowledge base". Not for: a repo contract or procedure → /quenching:knowledge:add; one glossary term → /quenching:knowledge:define.
argument-hint: [the-knowledge]
allowed-tools: Read, Grep, Glob, Write, Edit, AskUserQuestion
---

# /quenching:knowledge:learn — capture generic knowledge, OKF-conformant

**Input**: `$ARGUMENTS` (the generic understanding to capture — a concept, mental model, explanation, or learning).

Files one piece of understanding the human gives you into the canonical OKF bundle's
[`concepts/`](${CLAUDE_PLUGIN_ROOT}/assets/knowledge/concepts/index.md) home. Assumes the bundle already exists (run `/quenching:knowledge:align` first if not). The home boundaries are shared with `/quenching:knowledge:add`
([knowledge-add/homes.md](${CLAUDE_PLUGIN_ROOT}/assets/references/knowledge-add/homes.md)); the `type` vocabulary
and conformance rules with `/quenching:knowledge:align`
([knowledge-align/taxonomy.md](${CLAUDE_PLUGIN_ROOT}/assets/references/knowledge-align/taxonomy.md),
[knowledge-align/conformance.md](${CLAUDE_PLUGIN_ROOT}/assets/references/knowledge-align/conformance.md)).

## Workflow

### 1. Confirm the home
Read the knowledge the human stated. Confirm it is **generic understanding** (not a contract /
decision / procedure / external-asset fact). If it belongs in another home, say so and hand off
to `/quenching:knowledge:add`. Otherwise proceed under `concepts/`. **Done when:** the home is
confirmed or the item is routed away.

### 2. Determine identity (path)
Pick (or create) the `concepts/<subject>/` subfolder for the concept — e.g. `domain/`,
`glossary/`, `concepts/`. Concept ID = the path without `.md`; one concept per file; kebab-case;
**English slug**. If the subject already carries a cluster subfolder, nest inside it. If the
concept creates a **new** subfolder, that subfolder needs its own `index.md`. **Done when:** the
canonical concept path and any new subject index are fixed.

### 3. Fill the mold
Copy `${CLAUDE_PLUGIN_ROOT}/assets/templates/concept-front.md` and complete the frontmatter:
`type: concept` + the OKF recommended fields (`title`/`description`/`resource`/`timestamp`)
+ the method labels (`audience` — usually `both`; `authority` — usually `background`;
`source` — who supplied it; `maintainer`). Derive `resource`; use today's date for `timestamp`.
**Done when:** the complete stamp is evidence-backed.

### 4. Write the concept doc
Write the file with `Write`. Favor structural markdown (headings, lists, tables). Cross-home
links absolute (`/docs/...`); within-home links relative. Body prose MAY be the repo's language.
**Done when:** the concept body is written without overwriting filled content.

### 5. Update `concepts/index.md`
Add a bullet-link with the doc's `description`
(`* [<title>](<rel-path>.md) — <description>`) under the right subject. If you created a new
subfolder, create its frontmatter-free `index.md` and link it from `concepts/index.md`. Never
add frontmatter to an `index.md`. **Done when:** the concept and all required index links are in
place.

### 6. Enrich the glossary
If the concept introduced a **repo-specific term**, add or sharpen its entry in
`glossary.md` per **Enriching the glossary** in
[knowledge-add/homes.md](${CLAUDE_PLUGIN_ROOT}/assets/references/knowledge-add/homes.md) (the tail step
every capture runs; on-demand counterpart `/quenching:knowledge:define`, bulk counterpart
`/quenching:knowledge:glossary-backfill`). **Done when:** every repo-specific term is linked or
explicitly left for a glossary command.

### 7. Self-check against the conformance core
Verify every file you touched against
[knowledge-align/conformance.md](${CLAUDE_PLUGIN_ROOT}/assets/references/knowledge-align/conformance.md) —
the same checks `cq knowledge validate` machine-verifies. **Done when:** validation and the touched
file list are reported.

## Invariants to never violate

- Never file a **contract / decision / procedure / external-asset fact** under `concepts/` —
  route it to its home via `/quenching:knowledge:add`.
- Never write an empty or self-pointing `resource`, and never fabricate a `source`.
- Never add frontmatter to an `index.md`; never leave a new subfolder without one.
- Never overwrite a filled key on merge; never leave the index un-updated.
- Never skip the glossary tail step when the concept names a repo-specific term — but never
  clobber a filled glossary entry, and never fold a term's full explanation into the glossary
  (it holds the one-liner + the link; the depth stays in the concept doc).
