---
slug: name-the-scaffolded-stage
title: Decide whether a spec with an unwritten Problem gets a named stage
verification: per-section
priority: {level: 17, criticality: low, complexity: 2, date: 2026-07-28}
---

# Decide whether a spec with an unwritten Problem gets a named stage

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

`specs.py new` stamps the frontmatter and the `## Problem` heading with its guidance comment, and
nothing else — a captured spec is deliberately four lines of body. But scaffold content is
invisible to `has_real_content()` by design, so a spec whose `## Problem` is *still* the scaffold
comment has **no filled section at all** and therefore matches no derived stage: not even
`captured`, whose rule is `filled: [Problem]`.

`derive_stage` then falls back to the phase name, and the listing renders a `### Plans` group
inside `plans/index.md` — a heading that names a folder where every other heading names a stage.
It reads as a bug in the renderer, and it is really an unnamed state in the model.

The state itself is legitimate and worth distinguishing: *a spec exists and nobody has written the
problem yet* is a different fact from *the problem is written*, and it is the one moment where a
nudge is useful.

Naming it (e.g. a `scaffolded` stage sorting before `captured`) is not a local change: the stage
list lives in `assets/specs/schema.json`, is duplicated in `specs.py` as `DEFAULT_SCHEMA` for
installed copies with no adjacent assets, and is ordered by `STAGE_ORDER` — all three must move
together, and `plans reindex`, `next --front` and `status` all read the result.

Recorded during `specs-flow-consolidation`, which documented the state in the plans seed's zone
comment rather than modelling it, because the schema change was out of that spec's scope. The
decision this spec owes is whether the state earns a name or the fallback should simply render
something better than a folder name.
