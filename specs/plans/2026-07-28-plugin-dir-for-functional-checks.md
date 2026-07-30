---
slug: plugin-dir-for-functional-checks
title: Plugin Dir For Functional Checks
verification: per-section
priority: {level: 10, criticality: high, complexity: 2, date: 2026-07-29}
---

# Plugin Dir For Functional Checks

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

`functional-checks.sh` checks 1-3 spawn `claude -p` in a sandbox whose `.claude/settings.json`
copies this repo's `enabledPlugins`, so the plugin loads **through the marketplace registration** —
that is, from `~/.claude/plugins/cache/`, not from the checkout the script was invoked in.

Measured 2026-07-28: the cache held **3.0.0**, a tree still carrying `commands/align-and-update.md`
which 4.2.0 deleted. So the repo's only check for a `commands/**` change was grading a copy nobody
had edited in days, and passing.

Check 4 (added by `notice-installed-tool-version-drift`) avoids it with
`claude -p --plugin-dir "$REPO/plugins/quenching"` and a sandbox that enables no plugin at all, so
exactly one copy is loaded and it is the one under test. The same one-flag fix applies to checks
1-3; it was left out of that spec because rewiring the three existing checks is a change to what
they measure, not a fix to what this one added.
