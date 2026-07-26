---
type: knowledge
title: Glossary
description: The repo's single A–Z lookup of terms, acronyms, and domain vocabulary — one entry per term, each linking to its full concept doc when one exists.
resource: docs/**
tags: [glossary, vocabulary, terminology]
timestamp: 2026-07-26
audience: both
authority: current
source: claude-quenching skeleton
maintainer: <the team>
---

# Glossary

The repository's **single source of truth for what a term means here**. One entry per
term, in the same bullet syntax every `index.md` uses: `* [<Term>](<path>.md) — <one-sentence
definition>` when a full concept doc exists, or `* **<Term>** — <one-sentence definition>`
when it doesn't — the glossary is the *index* of vocabulary, not the long-form home.

**Resolving a term.** When a repo-specific word, acronym, or piece of jargon is unclear,
**search this file first** (Ctrl-F, or `grep -i '<term>' docs/knowledge/glossary.md`). A
matching entry gives the local meaning and, when linked, points to the doc that explains
it in full. No entry means the term is not yet defined — capture it (see *How to enrich*).

**This file is the ONE deliberate exception to "one concept per file."** A glossary is
inherently a multi-term aggregate — a flat bullet list, not a concept doc per term. It is
also the one exception to an `index.md`'s "only list what exists" rule: an **unlinked**
entry (a term with no concept doc yet) is a normal, permanent, valid state, not a defect.
Keep the list **alphabetically sorted by Term**, keep each definition to a single
sentence, and **link out** rather than explaining in full here.

## Terms

- [**Blocked task marker**](../standards/workflows/task-execution.md) — the `- [!] <id> <title> —
  blocked: <reason>` line implementation writes when attempts stop converging, replacing the
  earlier hidden attempt counter; `specs.py next` skips it and the reason stays legible to whoever
  unblocks it.
- [**Derived stage**](../standards/workflows/plan-artifacts.md) — a spec's
  sub-stage (`captured`/`proposed`/`designed`/`refined`/`executing`), COMPUTED from which
  headings are filled rather than declared in a field, so it regresses on its own when a
  section empties instead of going stale.
- [**Phase gate**](../standards/workflows/plan-artifacts.md) — the set of
  sections a spec must have filled to ENTER a phase folder; `promote` refuses with exit 2 and
  the missing list rather than warning, and the per-phase sets live once in `schema.json`,
  read by both `promote` and `validate`.
- [**`[P]` marker**](../standards/workflows/task-execution.md) — the opt-in flag set on a task at
  propose time declaring it may run concurrently with its group, honoured only when
  `specs.py parallel` proves the group's `files:` sets disjoint; never inferred while applying.
- [**Promote**](../standards/workflows/plan-artifacts.md) — the gated `git mv` that
  moves a spec between phase folders without renaming it; promoting into `ready/` IS the human
  OK to build, which is what replaced v1's computed `applyReady` flag.
- [**Refinement record**](../standards/workflows/plan-artifacts.md) — the `refined: {mode, date}`
  entry a spec's **frontmatter** gains once it has been interrogated, whose absence raises the
  non-gating `sp-unrefined` warning.
- [**Verification policy**](../standards/workflows/task-execution.md) — the per-plan declaration
  (`per-task`, `per-section`, `end-of-plan`) written at propose time that decides when a task's
  `verify:` command runs, so implementation never guesses and never asks mid-task.

## How to enrich

Add a term whenever a repo-specific word, acronym, or piece of jargon surfaces that a
newcomer would not know. Three ways in:

- **Automatically, as a tail of a capture.** The `claude-quenching` knowledge skills
  (`quenching-docs-learn`, `quenching-docs-add`, `quenching-docs-import-memory`) each check, at
  the end of a capture, whether the new concept introduced a term that belongs here, and
  add or update the entry — linking it to the concept doc just written.
- **On demand, one term at a time.** Run `quenching-docs-define` to add or refine a single
  entry (inserted in alphabetical position, MERGE — never clobbering a filled definition).
- **In bulk, across the whole bundle.** Run `quenching-docs-glossary-backfill` to sweep every doc
  already in `docs/` for repo-specific terms that were never fed into the glossary and
  backfill them in one pass.

Keep entries honest: define the term as **this repo** uses it, not the dictionary sense,
and let the linked doc carry the depth.
