---
slug: restructure-claude-front-namespace
title: Rename the /skill namespace to /automation and split it into artifact contexts
verification: per-section
priority: {level: 19, criticality: medium, date: 2026-07-29}
---

# Rename the /skill namespace to /automation and split it into artifact contexts

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

The plugin's `.claude/` command front is named `skill`, but `skill` is also the name of one
specific artifact kind inside it, so the agents and hooks nested under `commands/skill/` read as
sub-kinds of a skill when they are not — that's the defect this spec exists to fix. The fix renames
the whole front to `automation` (a name the repo already uses for this territory elsewhere) and
gives it four peer contexts, one per artifact it mints — `command/`, `agent/`, `hook/`,
`harness/` — with the CLAUDE.md-aligning commands moving into `harness`. `## Design` works through
the choices this forces: why `automation` beats `claude` as the front's name, why
sweep-the-whole-front verbs sit at the root while single-artifact verbs sit under their context,
why the shared `harness` stage can safely be invoked by two different aligns, and where the
bare-vs-registry-name rule should live once renamed. Every citation of a moved path across
`commands/**`, `assets/**`, `docs/**` and the three manuals is rewritten in the same diff, since the
noun `skill` is being retired from the same ~50 files the path rename touches. The work is blocked
until `instrument-and-extend-skill-front` merges, and `## Open Decisions` leaves two questions for
later — whether `skills.py` itself gets renamed, and whether a sibling spec on stale vocabulary is
now superseded.

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

## Proposal

- The `.claude/` front is named **`automation`**, the word the repo already uses for it
  (`docs/standards/automation/`, `assets/templates/automation/`, "the automation taxonomy"),
  so the rename introduces no new vocabulary and the glossary gains no term.
- `commands/skill/` becomes `commands/automation/`, holding **four peer contexts named for the
  artifact each mints** — `command/`, `agent/`, `hook/`, `harness/`. No context is a sub-kind of
  another, which is the defect this spec exists to fix.
- `/skill:new` becomes `/automation:command:new`, so the front no longer uses one word for both
  itself and one artifact inside it.
- `/docs:harness` becomes `/automation:harness:align`, joining the front that owns every file
  Claude Code reads as instruction.
- Front-level verbs sit at the front root (`/automation:align`); artifact-level verbs sit under
  their context (`/automation:command:eval`).
- Every citation of a moved path across `commands/**`, `assets/**`, `docs/**`, `CLAUDE.md`,
  `README.md` and the three `QUENCHING.md` manuals resolves to its new name.
- The noun "skill" no longer appears where "command" is meant — the vocabulary sweep
  `retire-skill-vocabulary` describes is delivered in the same diff as the path rename, because
  both rewrite the same ~50 files.
- The bare-vs-registry-name rule has exactly one owner that both aligns cite, instead of being
  restated inline in two command bodies.

## Out of Scope

- **Prefixing human-facing citations with `quenching:`.** This spec's original premise was that
  `assets/` citations lacked the plugin prefix. They do not: bare `/skill:new` is the correct prose
  form, stated at `commands/docs/align.md` §6 — "a bare `/docs:harness` is what a human types, not
  what the Skill tool resolves" — and the one site that resolves through the Skill tool,
  `commands/align.md`, already reads `quenching:skill:align`. The ~200 prose citations are wrong
  exactly once after this rename, and a mechanical rewrite closes them.
- **Renaming this spec's file or slug.** `restructure-claude-front-namespace` is historical: it
  records that `claude` was the proposed name before `automation` won. A spec never moves except
  into `archive/`.
- **Renaming the `docs/standards/automation/` subject folder.** It is already the target name; this
  spec brings the command surface to it, not the reverse.
- **Auditing command bodies for doctrine drift.** That is `/automation:align`'s read-only audit and
  stays a separate, human-driven pass.

## Design

### The front is named for the work, not for the tree

`docs/` and `specs/` are named for the trees they own, and naming this front `claude` after
`.claude/` would preserve that symmetry. The symmetry is broken deliberately: `automation` is
already the repo's word for this territory in three places, so `claude` would be a *second* name
for a thing that has one. It also survives Claude Code renaming `.claude/`, which the other two
fronts have no equivalent exposure to.

### A context is named for the artifact it mints

`command/`, `agent/`, `hook/`, `harness/`. `skill/` was rejected as the middle segment: the
artifact it mints is a **command** (the glossary's *Entry point*), and `retire-skill-vocabulary` is
retiring that noun — a permanent path segment reintroducing it would need a carve-out on the one
instance that is hardest to justify.

Rejected alternative: no middle segment at all (`/automation:new` mints a command, agent and hook
stay nested). It reproduces one-artifact-kind-as-default asymmetry one level down, which is the
shape this spec removes.

### Front-level verbs at the root, artifact-level verbs under their context

`/automation:align` sweeps the whole front. `/automation:command:eval` measures one command and
reads command files only, so it sits in the context whose scope it actually has. Extending eval to
agent definitions or hook wiring later is a rename, and that cost is accepted over naming it
`/automation:eval` today and implying a scope it does not have.

Rejected: one eval per context. Three bodies restating one measurement procedure is the
skill+wrapper shape the collapse spec just removed.

### `harness` is a shared, idempotent stage with two callers

`/docs:align` and `/automation:align` both invoke `quenching:automation:harness:align`, and both
compute the fat-harness probe signal. The stage is idempotent, so a double run inside `/align` is a
no-op.

This is a knowing duplication, taken over the two alternatives:

- **Only `/automation:align` drives it** — a bare `/docs:align` would stop converging on the
  glossary work harness creates, and closing that loop would require `/align`.
- **Only `/docs:align` drives it** — the front boundary becomes decorative, since a docs sweep
  would write through an automation-front command.

`sweep-doctrine.md` states no single-owner-per-stage rule, so this contradicts no contract. The
cost is that the probe signal is computed in two bodies and can drift; the mitigation belongs in
`## Risks`.

### The bare-vs-registry-name rule gets one owner

It is currently stated inline in `commands/docs/align.md` §6 and `commands/align.md` §4, and owned
by no reference file. A namespace rename is precisely the change that can silently violate it — a
conductor's stage invocation rewritten to the bare form still reads correctly and simply stops
resolving. Moving the rule into a reference both aligns cite makes it one string to check.

### Sequencing

This spec is **blocked on `instrument-and-extend-skill-front` merging**. That spec is `executing`
with 7 of 14 tasks done, and every remaining task lands in a file this rename moves — renaming
first means resolving the same conflict seven times, against tasks whose recorded commit shas point
at paths that would no longer exist.

## Open Decisions

- **Does `skills.py` get renamed, and do its `sk-*` finding codes change?** The tool is the
  automation front's verifier and carries the retired noun in its filename, its findings, and every
  `--json` consumer. Decided by: pricing the rename against the fact that `specs.py` and
  `okf-validate.py` are named for their fronts, and that the codes appear in installed target repos
  this plugin cannot rewrite. Settle before `## Tasks` is written.
- **Does `retire-skill-vocabulary` close as superseded, or narrow to the `docs/` prose it uniquely
  found?** It independently discovered four stale references in `docs/standards/` and
  `docs/knowledge/glossary.md` that no path rename reaches. Decided by: checking, once this spec's
  tasks exist, whether the `docs/` sweep is inside them; if it is, that spec is `/specs:conclude`d
  as `abandoned` with the reason.
