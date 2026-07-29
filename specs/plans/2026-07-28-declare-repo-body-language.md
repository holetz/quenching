---
slug: declare-repo-body-language
title: Declare the repo's body language in docs/standards so every command reads it for free
verification: per-section
priority: {level: 6, criticality: high, date: 2026-07-28}
---

# Declare the repo's body language in docs/standards so every command reads it for free

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

Spec bodies are written in English today, which makes them hard to read for the users of a
repository whose working language is not English (Portuguese, for instance). The canonical-surface
rule already fixes what must stay English — folder names, file slugs, frontmatter keys, `type`
values — but it says nothing about where a repository *declares* which language its bodies should
be written in, so today every command either guesses or leaves it to whoever is typing.

That declaration needs a home of its own in the repo — preferably under `docs/standards/` — and
reaching it has to be nearly free for the agent: cheap enough that knowing the correct setting is
never a reason to skip checking. A hook that reads it automatically is one candidate mechanism.
