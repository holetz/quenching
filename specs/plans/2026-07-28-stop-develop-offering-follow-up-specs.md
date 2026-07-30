---
slug: stop-develop-offering-follow-up-specs
title: /specs:develop should not offer to create a follow-up spec
verification: per-section
priority: {level: 7, criticality: medium, complexity: 1, date: 2026-07-29}
---

# /specs:develop should not offer to create a follow-up spec

<!-- ONE spec is ONE file for its whole lifecycle. Phases enrich it; they never split it.

     `specs.py new` stamps the frontmatter and `## Problem` ALONE — a captured spec is four
     lines of body, not a fourteen-heading skeleton. Every other heading below is created on
     first write by `specs.py section <slug> "<Heading>" --write`, which inserts it in the
     canonical position with the guidance comment kept here.

     THE STAGE-SCOPED EXPLICIT-NONE RULE. A heading is required — and required to carry
     `- none — <reason>` when it has nothing in it — only once ITS OWN gate is reached:

       new (capture)        `## Problem`
       ready (derived)      the nine definition sections (`## Problem` .. `## Risks`)
                            AND `## Tasks`
       ready (warn only)    `## Overview` non-empty, `## Handoff` non-empty
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

     AUDIENCE. Each section names who reads it. `## Overview`/`## Problem`/`## Proposal`/
     `## Design` are for the human — examples and plain language belong there.
     `## Handoff`/`## Tasks` are for agents — terse, with `files:`/`verify:`/`pattern:`
     metadata. An orchestrator never sends the human sections to an executor; that is what
     lets one file serve both audiences without bloating agent context. -->

## Overview

- none — only `## Problem` is filled; nothing else exists yet to connect.

## Problem

`/specs:develop` currently ends a pass by offering to create a follow-up spec for anything that
turned out to belong outside the spec. Its invariants say so directly: "an out-of-scope follow-up
to `/specs:create` — **offered, never auto-written**".

That offer duplicates work `/specs:conclude` already owns. Its distillation harvest table in
`specs-conclude/distill.md` carries the row "a **follow-up** the spec surfaced but did not pursue →
a fresh spec in `specs/plans/` via `/specs:create`", and `conclude.md` names "a follow-up worth its
own spec" as one of the four things the `done` pass harvests. So the front already has one
designed place where follow-ups become specs, at the point where it is known whether the parent
spec shipped at all.

Offering it during `develop` costs a prompt in one of the two most-run commands, and creates specs
in `plans/` that cannot be built until their parent merges — competing for attention in
`/specs:triage` and `/specs:continue` on the way.
