---
name: quenching-define
description: >-
  Adds or refines ONE entry in the repo's fixed glossary — knowledge/glossary.md, the A–Z
  lookup of repo-specific terms, acronyms, and domain vocabulary. Use when the user asks
  to "add a term to the glossary", "define this term", "add this acronym / jargon /
  codename to the glossary", "put this word in the glossary", or "update the glossary".
  Confirms the term is repo-specific, inserts it in alphabetical position with a
  one-sentence definition and a derived (never invented) link, MERGEs into an existing
  entry, and logs the update. Not for: a full concept doc → quenching-learn;
  whole-bundle term backfill → quenching-glossary-backfill.
when_to_use: >-
  adding or refining ONE term entry in knowledge/glossary.md. A full concept doc is
  quenching-learn; a bundle-wide backfill sweep is quenching-glossary-backfill.
allowed-tools: Read, Grep, Glob, Write, Edit
user-invocable: false
effort: low
---

# quenching-define — add/refine one glossary term

Files ONE term into the canonical OKF bundle's fixed glossary,
[`knowledge/glossary.md`](../../assets/docs/knowledge/glossary.md) — the repo's single A–Z lookup
of what a term means **here**. The glossary is a flat, alphabetically sorted bullet list in the
same syntax every `index.md` uses (`* [<Term>](<path>.md) — <definition>`, or `* **<Term>** —
<definition>` when no doc exists yet): an *index* of vocabulary, the one deliberate exception to
"one concept per file" (a glossary is inherently a multi-term aggregate). The home boundaries, the
glossary format, and the shared **Enriching the glossary** procedure live with `quenching-add`
([../quenching-add/references/homes.md](../quenching-add/references/homes.md)); the `type`
vocabulary and conformance rules with `quenching-align`
([../quenching-align/references/taxonomy.md](../quenching-align/references/taxonomy.md),
[.../conformance.md](../quenching-align/references/conformance.md)). For a whole-bundle bulk
backfill instead of one term, see `quenching-glossary-backfill`.

## Doctrine

- **The glossary is an index, not a home for depth.** An entry is a **one-sentence** meaning plus
  a link to the concept doc that explains the term in full. If the term needs more than a
  sentence, the depth belongs in a `knowledge/` concept doc (`quenching-learn`) and the entry
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
`quenching-align` to install the skeleton (it ships the fixed glossary), then resume. Read the
current list so you can place the entry and detect an existing one.

### 2. Confirm the term belongs
Confirm the term is **repo-specific** (not generic English) and not already listed. If it is
already present, this becomes a **refine** (Step 4 MERGE). If it needs a full explanation rather
than a one-liner, say so and hand off to `quenching-learn` for the concept doc — then add the
entry here pointing at it.

### 3. Derive the link
Look for the concept doc that defines the term (`Grep`/`Glob` `docs/**`). If one exists, link it
(`/docs/<path>.md`). If none exists, leave the entry unlinked — never invent a target; optionally
note that a `quenching-learn` capture would give the term a home.

### 4. Write the entry (MERGE, alphabetical)
Edit `knowledge/glossary.md`: insert `* [<Term>](<path>.md) — <one-sentence meaning in this
repo's sense>` (or `* **<Term>** — <one-sentence meaning>` if unlinked) in its **alphabetical**
position under `## Terms`. If an entry for the term exists, add a missing link or sharpen the
definition — never clobber a filled definition or link. Keep the list sorted. Definitions may
follow the repo's language; the term itself is verbatim as the repo writes it.

### 5. Append to `log.md`
Per **Appending to `log.md`** in
[../quenching-add/references/homes.md](../quenching-add/references/homes.md), with the entry:
`**Update**: [Glossary](/docs/knowledge/glossary.md) — added term "<Term>"` (or `refined`). This
is the one case where a glossary edit logs on its own — it is the only thing written.

### 6. Self-check against the conformance core
Verify every file you touched against
[../quenching-align/references/conformance.md](../quenching-align/references/conformance.md),
plus this skill's own gate: the list is still sorted and its links resolve.

## Invariants to never violate

- Never fold a full explanation into a glossary entry — one sentence + a link; depth goes to
  a `knowledge/` concept doc.
- Never invent a link target; link only a doc that exists, else leave the entry unlinked.
- Never clobber a filled definition or link on merge; never leave the list unsorted.
- Never create a per-term file or add a term outside `knowledge/glossary.md`; never give the
  glossary frontmatter beyond its shipped stamp, and never add frontmatter to `knowledge/index.md`.
