---
slug: probe-a-frontmatter-hook-firing
title: No probe observes a frontmatter hooks: block actually fire
verification: per-section
priority: {level: 14, criticality: high, date: 2026-07-28}
---

# No probe observes a frontmatter hooks: block actually fire

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

`instrument-and-extend-skill-front` added frontmatter `hooks:` blocks to `/docs:add`, `/docs:learn`
and `/docs:define`, taught `skills.py lint` to read them, and graduated
`docs/standards/automation/hooks.md` to `authority: current` on that adopting surface.

**Nothing has observed one fire.** The three blocks parse clean and `lint` reports zero hook
findings — but the command registry is built at session start, so a block written in a session is
inert in that same session. Every claim about them is therefore verified-by-parser, not
verified-by-execution, which is the precise distinction the `.claude/` front was instrumented to
stop accepting.

`functional-checks.sh` is the only harness in the repo that spawns a fresh `claude -p` and asserts
on captured tool calls — exactly the property needed here — and it has no probe for this. Its nine
assertions cover `${CLAUDE_PLUGIN_ROOT}` substitution in a body, conductor-by-registry-name, and
five spoken triggers; none of them touch a hook.

The gap widened during that spec's conclude. The branch review found that the three blocks pointed
at an `okf-validate.py` that `/docs:align` only *offers* to install, so `python3 <missing-file>`
exited 2 — an error under the hook protocol — on every `Write`/`Edit` in any repo that declined the
offer. A `test -f … || exit 0` guard now leads each block. **That guard is also unobserved**: it
was proven in a shell, not in a hook firing. A probe that asserts a rung-1 block runs would cover
the graduation and the guard together.

Discovered by `instrument-and-extend-skill-front`; the guard half added during its conclude.
