---
slug: isolate-functional-checks-probes
title: functional-checks.sh check 3 creates real specs in the repo it probes
verification: per-section
priority: {level: 10, criticality: medium, complexity: 3, date: 2026-07-28}
---

# functional-checks.sh check 3 creates real specs in the repo it probes

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

`functional-checks.sh` check 3 proves a spoken phrase still routes by description alone, and it
runs its probes **inside the real repository**. Two of the three probes are capture phrases, so
each run genuinely fires `/specs:create` against `specs/plans/` — and `--max-turns` cuts the run
off before `## Problem` is written.

Every run therefore leaves two half-written specs behind, and `specs.py validate` reports two
`sp-empty-section` errors that belong to nobody. A verification script that dirties the tree it
verifies makes its own next run report findings it caused, and the operator has to know which
errors to ignore — which is exactly the knowledge a check exists to remove.

Confirmed again by the `specs-flow-consolidation` conclude run: the post-merge invocation on `main`
passed all seven assertions and left the same residue.

Checks 1 and 2 already show the two shapes of the fix — check 2 builds a throwaway sandbox and
copies the repo's `enabledPlugins` into it, and check 1 is read-only by construction. Either
running the capture probes in the sandbox, or cleaning up whatever `plans/` gained, would do; the
sandbox is the stronger version, because a probe that cannot reach the real workspace cannot
damage it even when a future edit changes what it asks for.
