---
slug: wire-the-overview-consumers
title: "Wire the three consumers to read `## Overview`"
verification: per-section
priority: {level: 5, criticality: high, complexity: 4, date: 2026-07-29}
---

# Wire the three consumers to read `## Overview`

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

## Problem

`/specs:triage`, `/specs:continue` and `/specs:develop`'s approval bank each need a short
rendering of what a spec is about, and each regenerates its own on every invocation — from the
spec's `## Problem` and `## Proposal`, per command, per run. Three renderings of the same spec,
produced independently, that can and do disagree with each other, and none of which is written
down anywhere a human can correct.

`## Overview` now exists for exactly this: one human-authored orientation, first in the file,
refreshed by every `/specs:develop` bank. Every active spec in `plans/` carries it as of the
add-eli5-section-to-specs spec (2026-07-29) — 30 as an explicit `- none — <reason>`, 3 with real
prose — so the precondition is met and the consumers are still not wired.

That spec ruled the wiring out of its own scope deliberately: backfill *enables* the work but
establishes ordering, not membership, and the wiring answers a different problem than the one it
was solving. This is that different problem.

What needs deciding: what each consumer does when a spec's `## Overview` is an explicit none or
absent — fall back to regenerating, show nothing, or route to `/specs:develop` — and whether
reading it is worth the tokens for `/specs:continue`, which is near-free by construction today and
makes exactly one tool call.
