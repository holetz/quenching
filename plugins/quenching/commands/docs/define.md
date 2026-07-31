---
description: Add or refine ONE entry in the fixed glossary (knowledge/glossary.md)
argument-hint: [term]
allowed-tools: Read, Grep, Glob, Write, Edit
hooks:
  PostToolUse:
    - matcher: "Write|Edit"
      hooks:
        - type: command
          command: 'test -f "${CLAUDE_PROJECT_DIR}/.claude/hooks/okf-validate.py" || exit 0; python3 "${CLAUDE_PROJECT_DIR}/.claude/hooks/okf-validate.py"'
          timeout: 10
---

# /quenching:docs:define — add/refine one glossary term

**Input**: `$ARGUMENTS` (the term to add or refine, and optionally its one-sentence definition).

Files ONE term into the canonical OKF bundle's fixed glossary,
[`knowledge/glossary.md`](${CLAUDE_PLUGIN_ROOT}/assets/docs/knowledge/glossary.md) — the repo's single A–Z lookup
of what a term means **here**. The glossary is a flat, alphabetically sorted bullet list in the
same syntax every `index.md` uses (`* [<Term>](<path>.md) — <definition>`, or `* **<Term>** —
<definition>` when no doc exists yet): an *index* of vocabulary, the one deliberate exception to
"one concept per file" (a glossary is inherently a multi-term aggregate). The home boundaries, the
glossary format, and the shared **Enriching the glossary** procedure live with `/quenching:docs:add`
([docs-add/homes.md](${CLAUDE_PLUGIN_ROOT}/assets/references/docs-add/homes.md)); the `type`
vocabulary and conformance rules with `/quenching:docs:align`
([docs-align/taxonomy.md](${CLAUDE_PLUGIN_ROOT}/assets/references/docs-align/taxonomy.md),
[docs-align/conformance.md](${CLAUDE_PLUGIN_ROOT}/assets/references/docs-align/conformance.md)). For a whole-bundle bulk
backfill instead of one term, see `/quenching:docs:glossary-backfill`.

## Doctrine

- **The glossary is an index, not a home for depth.** An entry is a **one-sentence** meaning plus
  a link to the concept doc that explains the term in full. If the term needs more than a
  sentence, the depth belongs in a `knowledge/` concept doc (`/quenching:docs:learn`) and the entry
  just points to it. Never fold a full explanation into the glossary.
- **Repo-specific terms only.** Add a word a newcomer to *this* repo would not know — a domain
  entity, acronym, internal codename, or term of art. Skip generic English and dictionary senses;
  define the term as **this repo** uses it.
- **Alphabetical, always sorted.** Insert the entry in its alphabetical position by **Term**;
  leave the list sorted. A glossary that is not sorted is as much drift as a lying index.
- **Link derived, never invented.** The link targets a doc that actually exists (`/docs/<path>.md`,
  absolute across homes) — the concept doc that defines the term, or no link at all if none exists
  yet. Never fabricate a link to a doc that is not there. An unlinked entry is a **valid,
  permanent** state, not a defect to chase.
- **MERGE, never clobber.** If an entry for the term already exists, add a missing link or sharpen
  the definition; never overwrite a filled definition or a filled link.
- **One fixed file.** Everything lands in `knowledge/glossary.md`. Do not create a per-term file,
  do not touch `knowledge/index.md` (the glossary is already listed), and never add frontmatter to
  it beyond the shipped stamp.

## Workflow

### 1. Locate the glossary
Find `docs/knowledge/glossary.md` (the bundle root may be a variant — resolve it as the other
skills do). If the `knowledge/` home or the glossary seed is **missing**, stop and offer
`/quenching:docs:align` to install the skeleton (it ships the fixed glossary), then resume. Read the
current list so you can place the entry and detect an existing one.

### 2. Confirm the term belongs
Confirm the term is **repo-specific** (not generic English) and not already listed. If it is
already present, this becomes a **refine** (Step 4 MERGE). If it needs a full explanation rather
than a one-liner, say so and hand off to `/quenching:docs:learn` for the concept doc — then add the
entry here pointing at it.

### 3. Derive the link
Look for the concept doc that defines the term (`Grep`/`Glob` `docs/**`). If one exists, link it
(`/docs/<path>.md`). If none exists, leave the entry unlinked — never invent a target; optionally
note that a `/quenching:docs:learn` capture would give the term a home.

### 4. Write the entry (MERGE, alphabetical)
Edit `knowledge/glossary.md`: insert `* [<Term>](<path>.md) — <one-sentence meaning in this
repo's sense>` (or `* **<Term>** — <one-sentence meaning>` if unlinked) in its **alphabetical**
position under `## Terms`. If an entry for the term exists, add a missing link or sharpen the
definition — never clobber a filled definition or link. Keep the list sorted. Definitions may
follow the repo's language; the term itself is verbatim as the repo writes it.

### 5. Self-check against the conformance core
Verify every file you touched against
[docs-align/conformance.md](${CLAUDE_PLUGIN_ROOT}/assets/references/docs-align/conformance.md),
plus this skill's own gate: the list is still sorted and its links resolve.

## Invariants to never violate

- Never fold a full explanation into a glossary entry — one sentence + a link; depth goes to
  a `knowledge/` concept doc.
- Never invent a link target; link only a doc that exists, else leave the entry unlinked.
- Never clobber a filled definition or link on merge; never leave the list unsorted.
- Never create a per-term file or add a term outside `knowledge/glossary.md`; never give the
  glossary frontmatter beyond its shipped stamp, and never add frontmatter to `knowledge/index.md`.
