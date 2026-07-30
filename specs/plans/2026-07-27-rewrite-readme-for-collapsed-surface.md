---
slug: rewrite-readme-for-collapsed-surface
title: Rewrite README.md for the collapsed command surface
verification: per-section
priority: {level: 20, criticality: high, date: 2026-07-29}
---

# Rewrite README.md for the collapsed command surface

<!-- ONE spec is ONE file for its whole lifecycle. Phases enrich it; they never split it.

     `specs.py new` stamps the frontmatter and `## Problem` ALONE — a captured spec is four
     lines of body, not a fourteen-heading skeleton. Every other heading below is created on
     first write by `specs.py section <slug> "<Heading>" --write`, which inserts it in the
     canonical position with the guidance comment kept here.

     THE PHASE-SCOPED EXPLICIT-NONE RULE. A heading is required — and required to carry
     `- none — <reason>` when it has nothing in it — only once ITS OWN phase gate is reached:

       new (capture)        `## Problem`
       promote -> ready/    the nine definition sections (`## Problem` .. `## Risks`)
                            AND `## Tasks`
       ready/  (warn only)  `## Handoff` non-empty
       promote -> archive/  `## Outcome`

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

`plugins/quenching/README.md` still documents the two-file architecture the
`collapse-skills-into-commands` spec deleted. That spec's task 5.3 scoped only to §Cost model,
which was rewritten; **the other ~131 lines were not** — §The thirty skills, the `.claude/skills/`
layout, the `skills/*/references/` citation paths, and the wrapper prose all describe a shape the
plugin no longer has.

A blanket rename over the full file was **attempted and reverted** during that spec: it mangled 28
link paths into forms like `skills//docs:add/references/homes.md`. That is the evidence this needs
authoring rather than substitution, which is why it was left out of a migration whose diff had to
stay reviewable.

This is the most public stale artefact the collapse left behind — the README is what a prospective
adopter reads first, and it currently describes 30 skills, a `skills/` tree that does not exist,
and citation paths that resolve nowhere.

Recorded in the archived spec's `## Discoveries`:
[/specs/archive/2026-07-26-collapse-skills-into-commands.md](/specs/archive/2026-07-26-collapse-skills-into-commands.md)
