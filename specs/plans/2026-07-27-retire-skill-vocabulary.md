---
slug: retire-skill-vocabulary
title: Retire the skill vocabulary left behind by the collapse
verification: per-section
priority: {level: 12, criticality: low, date: 2026-07-28}
---

# Retire the skill vocabulary left behind by the collapse

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

The `collapse-skills-into-commands` spec fixed every **factual** stale reference — a path or link
naming a file that no longer exists — and deliberately left the **vocabulary**, because judging
hundreds of instances of prose is the body audit its `## Out of Scope` excludes to keep a 28-file
diff reviewable.

What remains is the noun *"skill"* where *"command"* is now meant, e.g. *"the one `/specs:*` skill
that runs the repo's own toolchain"*. Nothing points at a missing file, so this is cosmetic rather
than broken — but it is the vocabulary of a shape the plugin abandoned, sitting in the bodies that
teach a future session how the surface works.

**It reached `docs/` too, which the archived spec did not record.** Found while distilling:

- `docs/standards/automation/index.md` — the subject boundary still reads *"skills and their
  command wrappers"* and *"the plugin's own `skills/` + `commands/`"*.
- `docs/standards/CLAUDE.md` — routes the reader to `quenching-docs-add` / `quenching-docs-align`,
  both retired names.
- `docs/standards/quality/bundle-verification.md` — cites
  `quenching-docs-align/references/conformance.md`, a path that no longer exists.
- `docs/knowledge/glossary.md` §How to enrich — names five retired `quenching-docs-*` skills as
  the way in.

Scope is therefore both trees: the 28 command bodies plus 22 reference files, and the stale prose
in `docs/`. Worth checking whether `/skill:align-and-update`'s doctrine audit already covers the
first half before writing tasks for it.

Recorded in the archived spec's `## Discoveries`:
[/specs/archive/2026-07-26-collapse-skills-into-commands.md](/specs/archive/2026-07-26-collapse-skills-into-commands.md)

## Discoveries

- Scope extends past command bodies, references and docs/ into SHIPPED PRODUCT SOURCE, where the retired vocabulary is user-visible at runtime: (1) okf-validate.py's own finding message tells every user to 'Fix with the quenching-docs-align / quenching-docs-add skill' — emitted on each hook firing in every target repo, so this is the highest-traffic instance in the plugin and not cosmetic; (2) plugins/quenching/README.md still heads its per-command sections with quenching-docs-* / quenching-skill-* names; (3) assets/templates/harness/claude-root.md, the mold /docs:harness writes FROM, names five retired skills and specs/backlog/, so a harness refactor propagates retired vocabulary into every target repo it touches; (4) .claude-plugin/plugin.json's description says 'Twenty-four commands' where there are twenty-five. Items 1 and 3 are the load-bearing ones — both are copied into target repos, so they re-seed the vocabulary this spec exists to retire. Found during an /align run, 2026-07-28.
