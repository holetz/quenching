---
slug: check-the-lockstep-itself
title: Check The Lockstep Itself
verification: per-section
---

# Check The Lockstep Itself

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

`skills.py drift` compares each installed copy against **the shipped tool's own `VERSION`
constant**, because that constant is what an install would put on disk. That leaves the lockstep's
own failure unchecked: a release that bumps `VERSION`, `plugin.json` and the marketplace entry but
forgets one of the three tools' constants.

[versioning-release.md](/docs/standards/ci-cd/versioning-release.md) says exactly what that costs —
"a tool whose constant was not bumped is therefore never upgraded in any target repo that already
has it" — and nothing checks it. It is one comparison: the plugin's `VERSION` file against each of
`assets/bin/specs.py`, `assets/bin/skills.py` and `assets/hooks/okf-validate.py`.

Found while building `notice-installed-tool-version-drift`, whose `drift` subcommand already reads
all four of those numbers and could report the mismatch for nearly nothing.
