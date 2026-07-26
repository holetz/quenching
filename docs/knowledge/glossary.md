---
type: knowledge
title: Glossary
description: The repo's single A–Z lookup of terms, acronyms, and domain vocabulary — one entry per term, each linking to its full concept doc when one exists.
resource: docs/**
tags: [glossary, vocabulary, terminology]
timestamp: 2026-07-25
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

- [**Failure budget**](../standards/workflows/task-execution.md) — the five attempts a single task
  gets before implementation stops retrying it and reports it blocked, with a re-read of the
  touched files at two consecutive failures.
- [**`[P]` marker**](../standards/workflows/task-execution.md) — the opt-in flag set on a task at
  propose time declaring it may run concurrently with its group, honoured only when
  `specs.py parallel` proves the group's `files:` sets disjoint; never inferred while applying.
- [**Refinement record**](../standards/workflows/plan-artifacts.md) — the `refined: {mode, date}`
  entry a plan's `.specs.json` gains once it has been interrogated, whose absence raises the
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
