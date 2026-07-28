---
slug: restructure-claude-front-namespace
title: Rename the /skill namespace to /claude and separate the skill, agent and hook contexts
verification: per-section
---

# Rename the /skill namespace to /claude and separate the skill, agent and hook contexts

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

## Problem

The plugin grew the skill-authoring flow inside `commands/skill/`, when a command was the only
artifact that front minted. The tree now also holds `commands/skill/agent/` and
`commands/skill/hook/`, so `skill` names both the whole `.claude/` front *and* one artifact kind
inside it — agents and hooks read as sub-kinds of a skill, which they are not.

The proposal is to rename `commands/skill/` to a generic front name such as `claude`, and inside it
create a `skill` context that sits beside `hook` and `agent` rather than above them. The commands
that align or update `CLAUDE.md` should move into that front too.

Separately, `assets/` refers to the plugin's commands without the plugin-name prefix — e.g.
`assets/references/skill-new/doctrine.md` names `/skill:new` where the registered identity is
`/quenching:skill:new`. Those citations would all be wrong twice over after a rename.
