---
slug: make-sk-unscoped-bash-read-the-body
title: sk-unscoped-bash cannot read the body its own remedy points at
verification: per-section
priority: {level: 15, criticality: medium, complexity: 3, date: 2026-07-28}
---

# sk-unscoped-bash cannot read the body its own remedy points at

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

## Overview

- none — only `## Problem` is filled; nothing else exists yet to connect.

## Problem

`sk-unscoped-bash`'s own remedy text offers two ways to clear it: *"scope it to the commands the
workflow runs, **or state the reason in the body**"*. The check never reads a body.

After `instrument-and-extend-skill-front` task 3.2, the finding went 8 → 5 and **all five
survivors now state their reason** in a `**Why Bash is unrestricted here.**` section —
`/docs:align`, `/docs:documentation:build`, `/docs:import-memory`, `/specs:execute` and
`/specs:conclude`. All five still warn, identically to how they warned when five of the original
eight stated nothing at all.

So the finding cannot distinguish a **priced** grant from an **unpriced** one, which is the only
distinction it exists to draw. A reader working the list down has no way to tell which rows were
considered and which were merely never touched, and the honest work of pricing a grant earns
exactly nothing in the report.

Discovered by `instrument-and-extend-skill-front`, confirmed against `main` at 4.1.0 during its
conclude.
