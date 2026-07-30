---
slug: route-commands-without-always-on-descriptions
title: Route a 10x command surface without per-command always-on descriptions
verification: per-section
priority: {level: 1, criticality: critical, date: 2026-07-29}
---

# Route a 10x command surface without per-command always-on descriptions

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

Every command's `description` is **always-on**: it is in context on every session in every repo
that installs the plugin, before a single command is selected.
[context-budget.md](/docs/standards/automation/context-budget.md) governs that cost and mandates
what a description carries — a leading concept, quoted trigger phrases, and a `Not for:` boundary
— on the premise that the model routes from prose.

**The surface is expected to grow ~10x, to roughly 250 commands.** At that size the per-command
always-on description does not survive in any variant. Scaled from the measured 12,726 characters
over 25 commands on 2026-07-28:

| Surface at ~250 commands | always-on chars | ~tokens |
| --- | ---: | ---: |
| typed-only (`disable-model-invocation: true`) | 0 | 0 |
| one routing entry point | ~150 | ~40 |
| today's bare `/`-menu labels (~73 each) | ~18,250 | ~4,560 |
| the mandated three parts at 400–650 each | ~131,250 | ~32,800 |
| `/specs:*` sizing (~842 each) | ~210,500 | ~52,600 |

Doing nothing still costs ~4,560 tokens per session. Obeying the standard costs ~32,800. The
standard is `authority: background` and its ceiling is "one surface's measurement" — it was
written for a 25-command surface and its economics fail one order of magnitude out.

**The short descriptions were deliberate, and the repo has been reading them as damage.** They are
recorded as collateral from the collapse — "the deleted skill description is where the quoted
trigger phrases and the `Not for:` boundary lived" — and restoring them is called *affordable*. A
spec was taken all the way to the ready gate on that reading
([restore-routing-info-on-docs-commands](/specs/plans/2026-07-28-restore-routing-info-on-docs-commands.md),
approval withheld 2026-07-28) before the 10x expectation surfaced. `skills.py lint` still reports
`sk-trigger-position` and `sk-no-boundary` against every short description, so the instruments
push toward the option that scales worst.

**The gating unknown, and it is cheap to settle.** `disable-model-invocation: true` drops a
description from context entirely — `skills.py` already models this, counting such commands at 0
and marking them `alwaysOn: false` (`budget_rows`). But this plugin's conductors reach their
stages **by name through the Skill tool** (`/align` → `quenching:docs:align`), which is why
`CLAUDE.md` forbids the flag outright. Nobody has established whether the flag blocks only
autonomous selection, or **also** an explicit by-name Skill call:

- blocks selection only → the whole surface can go typed-only at zero always-on cost, conductors
  intact;
- blocks by-name too → conductors break, typed-only is dead, and the per-command description is
  the only routing mechanism there is.

The registry `skills.py registry reindex` already generates into
`docs/documentation/reference/automation.md` is a complete, machine-maintained table of the
surface — so a single model-invocable entry point whose body is that registry is available as a
candidate answer, trading O(n) always-on cost for O(1) plus one hop, and relocating the routing
problem into one description that can be measured and tuned rather than 250 that cannot. It is a
candidate, not a decision: the spike above gates it.

Two instrument gaps are already visible either way: `lint` does not skip the two routing codes for
typed-only commands although `budget` already zeroes them, so the two disagree about the same
surface; and `context-budget.md` §What the description may carry has no tier for a command that
carries no description at all.
