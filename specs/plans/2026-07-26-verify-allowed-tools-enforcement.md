---
slug: verify-allowed-tools-enforcement
title: Verify Allowed Tools Enforcement
verification: per-section
---

# Verify Allowed Tools Enforcement

<!-- ONE spec is ONE file for its whole lifecycle. Phases enrich it; they never split it.

     `specs.py new` stamps the frontmatter and `## Problem` ALONE — a captured spec is four
     lines of body, not a thirteen-heading skeleton. Every other heading below is created on
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

     AUDIENCE. Each section names who reads it. `## Problem`/`## Proposal`/`## Design` are for
     the human — examples and plain language belong there. `## Handoff`/`## Tasks` are for
     agents — terse, with `files:`/`verify:`/`pattern:` metadata. An orchestrator never sends
     the human sections to an executor; that is what lets one file serve both audiences
     without bloating agent context. -->

## Problem

Two skills promise in prose that they write nothing: `quenching-docs-status` and
`quenching-specs-status` both state *"writes nothing (no `Write`/`Edit` in `allowed-tools`)"*.
That guarantee is the whole point of a read-only view — it is what lets a human run one before
authorizing a sweep.

A spike run during the `skill-description-tiering` spec (task 0.2, now
[archived](/specs/archive/2026-07-26-skill-description-tiering.md)) suggests the mechanism behind
that promise may not do anything. A probe declaring `allowed-tools: ["Bash(echo:*)"]` still
completed a `Write` — verified on the filesystem, not by asking the model — in all four cells of
command × skill by slash-invocation × Skill-tool-invocation.

**This is a lead, not a verdict.** The runs used `claude -p` on one Linux machine under that
machine's permission settings, against Claude Code 2.1.215; no interactive session was tested, and
a permission mode may fully account for the result. The spike was measuring command-vs-skill
*parity* and got a clean answer to that question; enforcement was incidental to it.

What needs settling:

1. Does `allowed-tools` restrict the tool set at all — interactively, and under each permission
   mode? If it does, what exactly did the probe hit?
2. If it does not restrict reliably, the two status skills' prose is asserting an enforcement
   that does not exist. Either the claim is reworded to describe intent rather than a guarantee,
   or the read-only property is enforced some other way.
3. The same question applies to every other skill whose `allowed-tools` is narrower than what its
   body could reach — the sweeps scoped to `python3`/`py` among them.

Nothing here is urgent: no incident is known to have come from it, and the skills in question are
written not to write regardless. What is at stake is whether a stated guarantee is real, which is
worth knowing before anyone leans on it harder.

Background facts, already measured, are in
[reference/tools/claude-code-skill-command-mechanics.md](/docs/reference/tools/claude-code-skill-command-mechanics.md) §6.
