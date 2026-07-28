---
slug: fix-skills-py-description-truncation
title: skills.py silently truncates a description at the first '#'
verification: per-section
priority: {level: 4, criticality: high, complexity: 3, date: 2026-07-28}
---

# skills.py silently truncates a description at the first '#'

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

`skills.py`'s `parse_frontmatter` treats a `#` anywhere in a value as the start of a YAML comment
and drops the rest of the line. A command `description` is a single long line, so a `#` inside it
**silently truncates the description at that point** — for the parser, not for Claude Code, which
reads the real thing.

Found while rewriting `/specs:create`'s description during `specs-flow-consolidation`: writing a
markdown heading inline (backticked, as `## Problem`) cost the whole `Not for:` boundary and half
the trigger phrases. `lint` then reported `sk-no-boundary` — technically true of what it had
parsed, and completely misleading about the cause, which sent the fix at the wrong thing.

Two defects, and the second is the dangerous one:

- The parser is wrong: inside a quoted or plain scalar, `#` only begins a comment when preceded by
  whitespace, and never inside quotes.
- **A truncation is reported as absence.** Every downstream check — the character cap, trigger
  position, the boundary — runs against a silently shortened string, so the finding always names a
  missing part rather than the truncation that removed it. A verifier that misreports its own
  parse failure is worse than one that refuses.

The immediate fix is the comment rule; the durable one is a distinct finding (`sk-description-
truncated`, or a parse-level refusal) so the cause is never again presented as a content gap.
