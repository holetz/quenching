---
slug: collapse-skills-into-commands
title: Collapse the 28 skill+wrapper pairs into one command file per entry point
verification: per-section
---

# Collapse the 28 skill+wrapper pairs into one command file per entry point

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

Claude Code merged custom commands into skills: a `commands/deploy.md` and a
`skills/deploy/SKILL.md` "both create `/deploy` and work the same way". The plugin's 28 skills
plus their 28 mirrored wrappers are therefore a redundant pair — two always-on descriptions
where one would do. Collapsing to one command file per entry point would take always-on
metadata from 30,705 characters to ~2,069 (a 93% cut) and delete the `wrapper == skill`
duplication outright, rather than making it mechanical via `sk-wrapper-drift` as
`skill-description-tiering` does.

A related finding from that spec: all 28 skills carry `user-invocable: false`, the one row of
Claude Code's invocation table where the description is permanently resident *and* the human
cannot type the skill — which is exactly why the wrappers exist. Once the wrappers *are* the
skills, `disable-model-invocation: true` becomes available as a further lever.

**Gated on the spike at `skill-description-tiering` task 0.2**, which must answer three
questions YES before this is worth building:

1. Does `${CLAUDE_PLUGIN_ROOT}` substitute inside a `commands/*.md` body? The docs grant
   substitution to "Skill and agent content" and state that commands are now skills, but do
   not name `commands/**` in the substitution table. This is load-bearing: all 28 skills cite
   at least one `references/*.md`, so without a portable absolute path a command file cannot
   replace a skill.
2. Does a command file honour `allowed-tools` frontmatter?
3. Can a conductor invoke a command by name via the Skill tool, the way it invokes a stage
   skill today? Five conductors depend on this.

If the spike passes, `skill-description-tiering` is abandoned in favour of this spec. If it
fails, this spec is abandoned and that one proceeds. The two are mutually exclusive.

Rough shape if it proceeds: 28 skill directories become 28 command files; every cross-skill
citation is rewritten to an absolute plugin-root path; the 17 `references/` directories are
re-homed; five conductors are re-plumbed; `skills.py` is re-pointed at `commands/**`; and all
three `QUENCHING.md` operator manuals plus `CLAUDE.md` are rewritten. Reverting is a migration,
not a `git revert` — which is why this is separate from `skill-description-tiering`.
