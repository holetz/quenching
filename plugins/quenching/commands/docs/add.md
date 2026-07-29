---
description: Insert ONE new concept doc into the OKF bundle — right home, type, and stamp
argument-hint: [the-knowledge-to-add]
allowed-tools: Read, Grep, Glob, Write, Edit
hooks:
  PostToolUse:
    - matcher: "Write|Edit"
      hooks:
        - type: command
          command: 'test -f "${CLAUDE_PROJECT_DIR}/.claude/hooks/okf-validate.py" || exit 0; python3 "${CLAUDE_PROJECT_DIR}/.claude/hooks/okf-validate.py"'
          timeout: 10
---

# /docs:add — add new knowledge, OKF-conformant

**Input**: `$ARGUMENTS` (the piece of information to file — a standard, catalog table, announcement, reference, …).

Files one new piece of knowledge into the canonical OKF bundle so it lands in the right home
with a complete stamp. Assumes the bundle already exists (run `/docs:align` first if not). The
molds live at `${CLAUDE_PLUGIN_ROOT}/assets/templates/`; the routing table and the index/log
procedure are in [docs-add/homes.md](${CLAUDE_PLUGIN_ROOT}/assets/references/docs-add/homes.md). The home boundaries, `type`
vocabulary, and conformance rules are shared with `/docs:align`
(`${CLAUDE_PLUGIN_ROOT}/assets/references/docs-align/taxonomy.md`,
`${CLAUDE_PLUGIN_ROOT}/assets/references/docs-align/conformance.md`).

## Doctrine

- **One concept per file; the path is the identity.** The folder carries the subject, so the
  filename does not repeat it (`naming/columns.md`, not `naming/naming-columns.md`).
  Kebab-case, no accents. If the subject already holds a **cluster** of siblings, file the new
  concept **inside that subfolder** (`code/symbol-naming/enums.md`), never as a `symbol-naming-*`
  flat file — extend the folder the aligner would have folded.
- **English slug on technical homes; identifier slugs verbatim.** The file slug is canonical
  English on `standards/`·`vision/`·`documentation/`·`reference/` (as are
  folder names, frontmatter keys, and enum values). **Exception:** an identifier-derived name is
  verbatim — a catalog `<schema>`/`<table>` mirrors the real object, `reference/repositories/<repo>`
  the real repo. Body prose may be the repo's language.
- **`type` mandatory; `resource` derived, never invented.** For a standard, `resource` is the
  **glob set** naming what the doc governs — comma-separated, `*`/`**` only, repo-root-relative;
  for catalog/reference, the asset URI. Empty is disallowed, and so is self-pointing
  (`resource-self`) — except a bundle-level aggregate like `knowledge/glossary.md`. A glob says
  *what this doc governs* and is what the staleness check reads; a `file:line` says only where a
  rule was written, and rots on the next insertion above it.
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
Apply the boundary rules ([docs-add/homes.md](${CLAUDE_PLUGIN_ROOT}/assets/references/docs-add/homes.md)):
`standards` = "how **we** do it" (an agreed-but-unproven rule is a `standard` with
`authority: background`) · `reference` = "what we **consume**" · `catalog` = "our
**data**". Pick the home, its `type`, and the matching mold.

### 2. Determine identity (path)
Concept ID = the path without `.md`. Place it under the home's subject folder; one concept per
file; kebab-case; **English slug on the technical homes** (identifier-derived names verbatim, see
Doctrine). If the subject already carries a **cluster subfolder**, nest the new doc inside it. For
homes with a fixed shape, follow it
(`catalog/<system>/<catalog>/<schema>/<table>.md`).

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
hand-edit inside the markers. Never add frontmatter to an `index.md`.

### 6. Enrich the glossary
If the new concept introduced a **repo-specific term**, add or sharpen its entry in
`knowledge/glossary.md` per **Enriching the glossary** in [docs-add/homes.md](${CLAUDE_PLUGIN_ROOT}/assets/references/docs-add/homes.md)
(the tail step every capture runs; on-demand counterpart `/docs:define`, bulk counterpart
`/docs:glossary-backfill`).

### 7. Self-check against the conformance core
Verify every file you touched against
[docs-align/conformance.md](${CLAUDE_PLUGIN_ROOT}/assets/references/docs-align/conformance.md) —
the same checks the installed `okf-validate.py` hook (if wired) machine-verifies on write;
`/docs:align` re-validates the whole bundle on demand.

## Special cases
- **Standard** → mold `standard-front.md`; anchor rules to the code they govern; derive
  `resource` as a glob set;
  consider the subject's **candidate sub-standards** and record any deferral in that subject's
  coverage ledger. An **agreed-but-not-yet-proven** rule enters as `authority: background`
  (a proposal), graduating to `authority: current` once proven — there is no separate ADR home.
- **Catalog table with descriptions** → detailed `table.md`; without → keep it a row in the
  consolidated `<schema>.md`. Never create an empty detailed page.
- **Binary (a regulation PDF we consume)** → write a `sidecar.md` extract under
  `reference/regulations/` (`type: sidecar`), never ingest the binary.
