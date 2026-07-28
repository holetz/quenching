---
slug: restore-routing-info-on-docs-commands
title: Restore trigger phrases and boundaries on the nine bare /docs:* descriptions
verification: per-section
---

# Restore trigger phrases and boundaries on the nine bare /docs:* descriptions

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

The collapse into one file per entry point deleted the half of each pair that carried the quoted
trigger phrases and the `Not for:` boundary. Restoring them was called affordable, and it happened
— on `/specs:*` and on most of `/skill:*`. It never reached `/docs:*`.

Measured on `main` at 4.1.0, `skills.py lint` reports `sk-trigger-position` **and**
`sk-no-boundary` on nine of the eleven `/docs:*` commands: `add`, `define`, `documentation:build`,
`glossary-backfill`, `harness`, `import`, `import-memory`, `learn`, `status`. Only `/docs:align`
carries a full description. `/skill:eval` carries both findings too, and `/skill:new`
`sk-trigger-position` — so the command that measures routing and the command that mints commands
are themselves among the least routable on the surface.

Both are warnings, so the surface reports clean while the routing information is absent from the
only text that is always in context. A user who says "capture this thought" reaches `/specs:create`
because that description quotes the phrase; a user who says "write this down in the docs" has
nothing to route to.

**The constraint that makes this a spec rather than an edit.** The always-on ceiling is 11,565 and
has **no headroom by construction** — it equals the surface's current total. Restoring nine
descriptions to the size `/specs:*` carries will cross it, and crossing it is the signal working,
not a failure: it forces a measured re-set rather than an unpriced expansion. So this spec must
buy the routing information and re-measure the ceiling from a run, in that order, and state both
numbers.

Discovered by `instrument-and-extend-skill-front` (task 3.x territory, recorded in its
`## Discoveries` as two commands) and re-measured during its conclude, where it turned out to be
eleven.
