---
slug: dedupe-specs-py-spec-reader
title: Fold the four copies of read-parse-derive in specs.py into one helper
verification: per-section
---

# Fold the four copies of read-parse-derive in specs.py into one helper

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

Four `specs.py` functions repeat the same sequence to turn a path into a usable spec:
`read_text` → `parse_frontmatter` → `parse_sections` → `parse_tasks` → `task_progress` →
`derive_stage`. They are `cmd_list`, `validate_spec`, `cmd_plans` and `_candidate`.

The duplication is not merely verbose — it is four independent chances for the *same* file to be
read into four slightly different views. `derive_stage` is the front's single most load-bearing
computation (it decides what `list` groups, what `plans reindex` renders, what `next --front` ranks
and what `validate` judges the `ready` gate against), and nothing structurally guarantees that all
four callers feed it the same inputs.

A shared `_read_spec(row)` returning one parsed record would remove three copies and give the four
consumers one definition of what a spec *is* when read from disk.

Recorded during `specs-flow-consolidation`, where it was deliberately not done: the four functions
were owned by different tasks in that spec, and a refactor spanning all of them inside any one task
would have put changes in the diff that the task's own `verify:` did not cover. It is its own
cleanup, with its own verification, which is what this spec is for.
