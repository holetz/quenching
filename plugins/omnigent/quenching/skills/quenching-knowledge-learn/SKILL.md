---
name: quenching-knowledge-learn
description: "Capture ONE piece of generic knowledge into the bundle's concepts/ home. Use for \"add this knowledge\", \"record what we learned\". Not for: repo contracts → quenching-knowledge-add; terms → quenching-knowledge-define."
allowed-tools: "Bash(cq:*), Read, Grep, Glob, Write, Edit, AskUserQuestion"
---

<!-- GENERATED FROM plugins/quenching/commands/knowledge/learn.md -->

<!-- OMNIGENT RUNTIME START -->
## Omnigent runtime

This runs inside the `quenching` operator agent on whatever model the server's policy selects; it pins none and names no vendor CLI. The bundle carries no payload: read a reference through the `quenching` MCP server's resources (`quenching://references/<path>`), and prefer its tools (`<pillar>_<verb>`) to a shell `cq`, which resolves only where a local install sits under `$QUENCHING_OMNIGENT_ROOT`. Delegate only to the operator's declared sub-agents. Source model tiers and effort are not switches: a declared tier or effort below is a preference to report. Token usage comes from host telemetry when it exists, otherwise it is `not measured`. A tool the permission policy denies stays denied: report it, never route around it. If delegation is unavailable, report the limitation; never replace a required independent verification with self-review.

<!-- OMNIGENT RUNTIME END -->


# quenching-knowledge-learn — capture generic knowledge, OKF-conformant

**Input**: `$ARGUMENTS` (the generic understanding to capture — a concept, mental model, explanation, or learning).

Files one piece of understanding the human gives you into the canonical OKF bundle's
[`concepts/`](~/.omnigent/quenching/knowledge/concepts/index.md) home. Assumes the bundle already exists (run `quenching-knowledge-align` first if not). The home boundaries are shared with `quenching-knowledge-add`
([knowledge-add/homes.md](quenching://references/knowledge-add/homes.md)); the `type` vocabulary
and conformance rules with `quenching-knowledge-align`
([knowledge-align/taxonomy.md](quenching://references/knowledge-align/taxonomy.md),
[knowledge-align/conformance.md](quenching://references/knowledge-align/conformance.md)).

## Workflow

### 1. Confirm the home
Read the knowledge the human stated. Confirm it is **generic understanding** (not a contract /
decision / procedure / external-asset fact). If it belongs in another home, say so and hand off
to `quenching-knowledge-add`. Otherwise proceed under `concepts/`. **Done when:** the home is
confirmed or the item is routed away.

### 2. Determine identity (path)
Pick (or create) the `concepts/<subject>/` subfolder for the concept — e.g. `domain/`,
`glossary/`, `concepts/`. Concept ID = the path without `.md`; one concept per file; kebab-case;
**English slug**. If the subject already carries a cluster subfolder, nest inside it. If the
concept creates a **new** subfolder, that subfolder needs its own `index.md`. **Done when:** the
canonical concept path and any new subject index are fixed.

### 3. Fill the mold
Copy `~/.omnigent/quenching/templates/concept-front.md` and complete the frontmatter:
`type: concept` + the OKF recommended fields (`title`/`description`/`resource`/`generated`)
+ the method labels (`audience` — usually `both`; `authority` — usually `background`;
`source` — who supplied it; `maintainer`). Derive `resource`; set `generated` to
`{ by: human:<id>, at: <ISO 8601 UTC> }` (or a `process:`/`<producer>/<version>` actor when
that is what produced it).
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
[knowledge-add/homes.md](quenching://references/knowledge-add/homes.md) (the tail step
every capture runs; on-demand counterpart `quenching-knowledge-define`, bulk counterpart
`quenching-knowledge-glossary-backfill`). **Done when:** every repo-specific term is linked or
explicitly left for a glossary command.

### 7. Self-check against the conformance core
Verify every file you touched against
[knowledge-align/conformance.md](quenching://references/knowledge-align/conformance.md) —
the same checks `cq knowledge validate` machine-verifies. **Done when:** validation and the touched
file list are reported.

## Invariants to never violate

- Never file a **contract / decision / procedure / external-asset fact** under `concepts/` —
  route it to its home via `quenching-knowledge-add`.
- Never write an empty or self-pointing `resource`, and never fabricate a `source`.
- Never add frontmatter to an `index.md`; never leave a new subfolder without one.
- Never overwrite a filled key on merge; never leave the index un-updated.
- Never skip the glossary tail step when the concept names a repo-specific term — but never
  clobber a filled glossary entry, and never fold a term's full explanation into the glossary
  (it holds the one-liner + the link; the depth stays in the concept doc).
