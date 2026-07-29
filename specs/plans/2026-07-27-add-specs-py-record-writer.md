---
slug: add-specs-py-record-writer
title: Give the frontmatter records a mechanical writer in specs.py
verification: per-section
priority: {level: 17, criticality: medium, date: 2026-07-28}
---

# Give the frontmatter records a mechanical writer in specs.py

<!-- ONE spec is ONE file for its whole lifecycle. Phases enrich it; they never split it.

     `specs.py new` stamps the frontmatter and `## Problem` ALONE — a captured spec is four
     lines of body, not a thirteen-heading skeleton. Every other heading below is created on
     first write by `specs.py section <slug> "<Heading>" --write`, which inserts it in the
     canonical position with the guidance comment kept here.

     THE STAGE-SCOPED EXPLICIT-NONE RULE. A heading is required — and required to carry
     `- none — <reason>` when it has nothing in it — only once ITS OWN gate is reached:

       new (capture)        `## Problem`
       ready (derived)      the nine definition sections (`## Problem` .. `## Risks`)
                            AND `## Tasks`
       ready (warn only)    `## Handoff` non-empty
       promote -> archive/  `## Outcome`

     `ready` is a DERIVED STAGE, not a folder: a spec lives in `plans/` for its whole active
     life, and filling those ten sections is what makes it ready. Nothing refuses on that
     gate — it is a floor `execute` reports against, and the human's go-ahead is the
     `approved:` frontmatter record, asked for inline.

     Before its gate, a heading's absence is NOT an omission — it is a not-yet. After its
     gate, three rules decide whether a section counts as filled:

       1. `- none — <reason>` counts as filled. An omission and a null are different facts.
       2. A heading present with an EMPTY body is malformed and refuses. It is neither an
          answer nor a not-yet.
       3. An absent heading before its gate is legal.

     Headings are a PARSED contract — canonical English, exactly as written here. Body prose
     follows the repo's language. A heading outside this set is a stray and validate flags it.

     AUDIENCE. Each section names who reads it. `## Problem`/`## Proposal`/`## Design` are for
     the human — examples and plain language belong there. `## Handoff`/`## Tasks` are for
     agents — terse, with `files:`/`verify:`/`pattern:` metadata. An orchestrator never sends
     the human sections to an executor; that is what lets one file serve both audiences
     without bloating agent context. -->

## Problem

`specs.py` owns every mutation a spec undergoes — `new` stamps it, `section --write` inserts a
heading, `task --check|--uncheck|--block` edits a task line, `discover` appends a line, `promote`
moves the file and stamps `outcome`. **Every frontmatter record except `outcome` is the
exception**: `priority`, `refined`, `approved`, `branch`, `reviewed` and `merge` are hand-written
with `Edit` by four different commands (`triage`, `develop`, `execute`, `conclude`).

That makes the records the one part of the contract with no mechanical writer, and it has two
consequences:

- **`writeOnce` is enforced by nothing.** `schema.json` marks `approved`, `branch`, `merge` and
  `outcome` write-once and states why each cannot be derived, but the only thing standing between
  a record and an overwrite is an invariant written in prose in four command bodies. A command that
  forgets it silently rewrites history — exactly the failure the write-once flag exists to prevent.
- **The shape is restated in four places.** `merge: {strategy, commit}` and `branch: {base, work}`
  are hand-formatted YAML flow mappings; a fifth caller writing `merge: {commit: …, strategy: …}`
  or quoting the sha produces something `parse_frontmatter` may still read but no schema check
  ever validated.

Surfaced by the `specs-flow-consolidation` branch review, and demonstrated twice by its own
conclude run: `reviewed` and `merge` were both stamped with `Edit` against the file directly, with
no tool able to refuse if the value had already been set.

A `specs.py record --spec <slug> <name> --field k=v …` subcommand would put the records under the
same contract as everything else: refuse (exit 2) on a `writeOnce` record that is already set,
validate the field names against `schema.json`, and render the mapping one way.
