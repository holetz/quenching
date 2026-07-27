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

### The gate is resolved — this spec is live

`skill-description-tiering` task 0.2 ran the spike on **2026-07-26** and the human took this
branch; that spec is now
[archived as abandoned](/specs/archive/2026-07-26-skill-description-tiering.md). Method: throwaway
command and skill probes exercised in fresh `claude -p` processes against Claude Code 2.1.215, all
reverted. Full facts in
[reference/tools/claude-code-skill-command-mechanics.md](/docs/reference/tools/claude-code-skill-command-mechanics.md).

| # | Question | Result |
| --- | --- | --- |
| 1 | `${CLAUDE_PLUGIN_ROOT}` substitutes in a `commands/*.md` body | **YES** — resolved to the absolute plugin root on both invocation paths. The load-bearing unknown is cleared: a command file *can* cite a bundled `references/*.md`. |
| 2 | A command honours `allowed-tools` | **Parity, not proof** — the allowlist failed to block a `Write` in all four cells of command × skill by slash × Skill-tool invocation. Commands are no worse than skills, so the collapse loses nothing; but nobody should claim it as enforcement. Tracked separately as `verify-allowed-tools-enforcement`. |
| 3 | A conductor invokes a command by name via the Skill tool | **YES** — a command was invoked by name through the Skill tool with substitution intact, the exact path a conductor uses. |

Q2 is why this was a judgement call rather than an automatic pass: the gate's letter demanded
three clean YES. It was taken on the reading that "no regression" suffices, since the guarantee
turns out to be absent from skills too.

**Two findings the spike added, both easing this spec:**

- **`hide-from-slash-command-tool: "true"` exists** as a frontmatter key, observed in Anthropic's
  shipped `ralph-wiggum/commands/ralph-loop.md`. This answers the objection that made
  `skill-description-tiering` defer `disable-model-invocation: true` — that dropping
  `user-invocable: false` floods the `/` menu with duplicates. Worth confirming it behaves as the
  name suggests before designing around it.
- **One unified frontmatter schema.** The 2.1.215 binary parses `user-invocable`, `allowed-tools`,
  `disallowed-tools`, `argument-hint`, and `disable-model-invocation` from a single key list,
  corroborating the merge rather than resting on the changelog sentence.
- **Precedent exists in the wild.** Anthropic ships four `commands/**` files using
  `${CLAUDE_PLUGIN_ROOT}`, one load-bearingly inside `allowed-tools` itself.

One operational note for whoever builds this: **the command/skill registry is built at session
start**, so no change to `commands/**` is testable in the session that makes it. Every verification
step needs a fresh process.

Rough shape now that it proceeds: 28 skill directories become 28 command files; every cross-skill
citation is rewritten to an absolute plugin-root path; the 17 `references/` directories are
re-homed; five conductors are re-plumbed; `skills.py` is re-pointed at `commands/**`; and all
three `QUENCHING.md` operator manuals plus `CLAUDE.md` are rewritten. Reverting is a migration,
not a `git revert` — which is why this was kept separate from `skill-description-tiering`.
