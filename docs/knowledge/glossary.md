---
type: knowledge
title: Glossary
description: The repo's single A–Z lookup of terms, acronyms, and domain vocabulary — one entry per term, each linking to its full concept doc when one exists.
resource: docs/**
tags: [glossary, vocabulary, terminology]
timestamp: 2026-07-26
audience: both
authority: current
source: quenching skeleton
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

- [**Always-on metadata**](../standards/automation/context-budget.md) — the frontmatter
  `description` of every command, resident in every session's context before anything fires and
  therefore the only surface cost paid whether or not a command runs; measured by
  `skills.py budget` from the parsed value, never the YAML source.
- [**Approved record**](../standards/workflows/plan-lifecycle.md) — the `approved: {date}`
  frontmatter entry recording that a human said go, the one fact the retired `backlog/` → `ready/`
  `git mv` carried that no derivation reproduces; `execute` asks inline and stamps it rather than
  refusing an unapproved spec.
- [**Blocked task marker**](../standards/workflows/task-execution.md) — the `- [!] <id> <title> —
  blocked: <reason>` line implementation writes when attempts stop converging, replacing the
  earlier hidden attempt counter; `specs.py next` skips it and the reason stays legible to whoever
  unblocks it.
- [**Commit record**](../standards/workflows/plan-git-record.md) — the `commit: <sha>` field on a
  completed task line, written mechanically by `specs.py task --check --commit`, that links the
  checkbox to the commit implementing it without inscribing anything into the commit message —
  which stays entirely the target repo's to format.
- [**Derived stage**](../standards/workflows/plan-lifecycle.md) — a spec's position in its life
  (`captured` → `proposed` → `designed` → `refined` → `ready` → `approved` → `executing`),
  COMPUTED from which headings are filled and which records frontmatter carries rather than
  declared in a field, so it regresses on its own when a section empties instead of going stale;
  resolution is last-match-wins, which is why `executing` sorts last.
- [**Entry point**](../standards/naming/command-surface.md) — one `commands/<path>.md` file, whose
  path IS its identity (`commands/docs/add.md` → `/docs:add`); since Claude Code merged commands
  into skills there is no second file to mirror, so there is nothing an entry point can drift from.
- [**Phantom command**](../standards/architecture/plugin-layout.md) — a non-entry-point file left
  under `commands/`, which registers as a real `/` entry that does nothing; it does not error, so
  the only thing that catches it is `sk-no-description`, and it is why shared procedure lives under
  `assets/`.
- [**Phase gate**](../standards/workflows/plan-artifacts.md) — the set of sections a spec must have
  filled before a heading counts as required, which is what makes the explicit-none rule
  stage-scoped rather than absolute. Two gates move a file (`new` into `plans/`, `promote` into
  `archive/`) and refuse with exit 2 and the missing list rather than warning; the `ready` gate is
  a derived stage that refuses nothing. All of them live once in `schema.json`, read by both
  `promote` and `validate`.
- [**`[P]` marker**](../standards/workflows/task-execution.md) — the opt-in flag set on a task when
  the tasks are written, declaring it may run concurrently with its group; honoured only when
  `specs.py parallel` proves the group's `files:` sets disjoint, and never inferred while building.
- [**Probe**](../standards/architecture/align-surface.md) — the opening run of a front's own
  verifier (`okf-validate.py`, `specs.py doctor`, `skills.py doctor`) whose exit code decides
  whether an align inventories anything at all, making a no-op align cost a couple of tool calls;
  the same programs run again as the closing verification.
- [**Promote**](../standards/workflows/plan-lifecycle.md) — the gated `git mv` that moves a spec
  from `plans/` to `archive/` without renaming it, stamping `outcome: done | abandoned`. Under v3
  it is the ONE hop a spec ever makes: the `backlog/` → `ready/` promote is retired, and the human
  OK it used to carry is the **Approved record** instead. Promoting as `done` refuses
  while `- [ ]` boxes remain unless forced; `abandoned` is always allowed.
- [**Refinement record**](../standards/workflows/plan-artifacts.md) — the `refined: {mode, date}`
  entry a spec's **frontmatter** gains once it has been interrogated, whose absence raises the
  non-gating `sp-unrefined` warning.
- [**Verification policy**](../standards/workflows/task-execution.md) — the per-spec declaration
  (`per-task`, `per-section`, `end-of-plan`) written at creation that decides when a task's
  `verify:` command runs, so execution never guesses and never asks mid-task.

## How to enrich

Add a term whenever a repo-specific word, acronym, or piece of jargon surfaces that a
newcomer would not know. Three ways in:

- **Automatically, as a tail of a capture.** The `quenching` knowledge skills
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
