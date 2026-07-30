---
slug: reduce-execute-conclude-cost
title: Re-evaluate /specs:execute and /specs:conclude runs for cost reduction
verification: per-section
priority: {level: 3, criticality: high, date: 2026-07-29}
---

# Re-evaluate /specs:execute and /specs:conclude runs for cost reduction

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

`/specs:execute` and `/specs:conclude` are the two most expensive commands on the specs front, and
nobody has ever looked at what that cost is actually buying. Both run long — execute walks task by
task, conclude reviews a whole branch — and neither declares which of its steps genuinely need the
session's model and which would survive on a weaker one.

Re-evaluate both commands' runs for cost reduction: look at the transcripts of sessions that have
already executed them for evidence of where the money went, and use that evidence to say which
steps (sub-agent calls, per-task verification, the branch review) could drop to a cheaper model or
a lower effort without weakening what the command guarantees.
