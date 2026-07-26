---
type: standard
title: Skill authoring and alignment
description: How the plugin's skills are classified, authored, named, mirrored as commands, and swept into conformance
resource: plugins/claude-quenching/skills/**, plugins/claude-quenching/commands/**
tags: [automation, skills, taxonomy, authoring]
timestamp: 2026-07-24
audience: both
authority: current
source: add-quenching-skill-pair change (skill-authoring + skill-alignment deltas)
maintainer: claude-quenching
---

# Skill authoring and alignment

The contract for how a skill enters and stays in this plugin's automation surface, distilled from
the `add-quenching-skill-pair` change. `quenching-skill-new` mints or edits one skill; `quenching-skill-align`
sweeps the whole surface into conformance. The command naming these produce is governed by
[command-surface.md](../naming/command-surface.md); the writing-doctrine detail lives once in
`plugins/claude-quenching/skills/quenching-skill-new/references/` and is cited, never restated.

## Single-axis classification

Every skill is classified on **exactly one axis**, and all naming and placement derive from it:

- **Domain-bound** — serves one folder subtree / one front. Named as the flattened path plus a
  verb, and mirrored by a thin command wrapper (see [command-surface.md](../naming/command-surface.md)).
- **Generic** — serves the surface as a whole. Named verb-object, never mirrored under a path: a
  flat command or none.

The classification test is naming the one folder/front the skill acts on: exactly one answer means
domain-bound; "the whole surface" means generic; several unrelated targets means the skill is kept
as-is and reported, never forced onto the axis.

**A technique is a parameter of a verb, not a new axis.** Variants of one action — different
elicitation scripts, different depths, different output shapes — become an argument to a single
skill, never sibling skills. The axis is the object plus the verb; the technique rides along. Four
interrogation modes (`interview`, `critic`, `premortem`, `alternatives`) shipped as
`quenching-specs-plan-refine --mode`, not as four `refine-*` skills, because four always-on
descriptions spend the shared per-skill cap forever to express one verb four ways, and the wrapper
bijection would mirror them into four near-identical files. Split only when the *object* or the
*verb* differs — a skill that waits for a human-stated edit and one that generates the questions
are opposite directions of initiative and stay apart; two scripts for the same interrogation do not.

## Authoring (`quenching-skill-new`)

- **Mirrored wrapper** for every domain-bound skill; a generic skill stays flat.
- **Writing doctrine** applied to every `SKILL.md`: predictable naming, trigger phrases in the
  description's second sentence, a no-op self-test, no negation-only guidance, a body well under
  the size cap with shared procedure pushed into `references/`.
- **Read the taxonomy rule before minting** (this standard); offer to create it from the template
  when a bundle-carrying repo lacks it.
- **One plan → one OK**: classification, names, files to write, and the OKF tail presented as a
  single plan, applied on one confirmation.
- **OKF tail** on every mint: regenerate the derived registry's GENERATED zone, offer a glossary
  entry for any coined term, append a log entry, and self-check.

## Alignment (`quenching-skill-align`)

- **Read-only inventory** of the existing skill + command surface before any plan.
- **One consolidated migration plan, one confirmation** — renames, wrapper mirroring, and the rule
  + registry created from the molds when missing; a rename referenced by product code or scripts
  gets its own individual confirmation.
- **MERGE, never clobber; never delete without a human word.** Only names, placement, and missing
  scaffolding change — existing skill bodies are preserved. An unclassifiable skill is kept and
  reported, never forced.
- **Post-apply verification**: regenerate the registry zone, confirm every wrapper resolves to a
  skill and vice versa (the bijection), and report residue.

## Invocation and permission are authored decisions

Three frontmatter fields decide who may invoke a skill and what it may reach. They are chosen
deliberately at mint, never left to default:

| `user-invocable` | `disable-model-invocation` | Who can invoke it | Use for |
| --- | --- | --- | --- |
| `false` | *(unset)* | the model, and any command wrapper | **the default here** — every skill behind a `/` wrapper: hidden from the menu, still routable by description |
| *(unset)* | *(unset)* | everyone | a skill a human is expected to pick from the `/` menu by name |
| `false` | `true` | **nobody** | never — this is `sk-unreachable`, an error |
| *(unset)* | `true` | the human only | a skill whose cost or blast radius means a human must choose it, never a router |

`user-invocable: false` **hides the menu entry; it does not block programmatic invocation.**
`disable-model-invocation: true` is the only field that does. Confusing the two is how a skill
meant to be human-gated ends up firing from a description match.

`context: fork` runs the skill in a separate context. It is **forbidden** on any skill that gates
on a mid-flow confirmation — a forked context cannot present the plan whose OK the run depends on.
A skill that only reads and reports may fork freely.

### `allowed-tools` is always scoped

Grant the narrowest set that lets the workflow finish. A tool that takes a scope gets one:
`Bash(python3:*)`, `Bash(py:*)`, `Bash(git status:*)` — never a bare `Bash`, which grants the whole
shell for the turn. `skills.py lint` reports a bare grant as `sk-unscoped-bash`.

One exception, and it must be **stated in the body**: a skill that runs the *target repo's own*
toolchain — its build, its tests, its linters, its migrations — cannot enumerate those commands in
advance, because they are the repo's, not the plugin's. Such a skill may hold an unscoped `Bash`
provided its body says so and says why. `quenching-specs-plan-apply` is the standing example. The
finding is still reported; what the stated reason buys is a reader who can tell a deliberate grant
from an unexamined one.

## The verifier

`skills.py` is this front's verifier, the peer of `okf-validate.py` for `docs/` and `specs.py` for
`specs/`. Same contract: `--json` on every subcommand, exit **0** ok · **1** findings · **2**
refusal, errors setting the exit code and warnings never doing so.

| Subcommand | Decides |
| --- | --- |
| `lint [path]` | one skill against this standard — the description caps, trigger position, the `Not for:` boundary, body length, a `**Done when:**` per numbered step, unscoped `Bash`, invocation coherence |
| `doctor` | the surface's shape — the bijection, canonical names, collisions, unmirrored wrappers |
| `registry reindex` | regenerates the registry's GENERATED zone; it **owns** that format |
| `budget` | what the surface costs before anything fires — see [context-budget.md](context-budget.md) |

Every threshold this standard names is implemented there, and the tool is the normative
statement: a rule whose only check is a sentence decays, because nothing fails when it is broken.

**What the tool does not decide.** The axis. Naming the one folder a skill acts on is a claim
about what the skill is *for*, and no parser makes it. So are the doctrine's remaining tests — the
no-op test, sediment, sprawl, positive prescription. Those stay a human read, and a report keeps
the two kinds of evidence apart: a code names a threshold crossed, a read names a claim about
behaviour.

## Convergence condition

The surface is aligned when `skills.py doctor` and `skills.py lint` exit 0 — or every surviving
finding is named in the report by its `sk-*` code — and `skills.py registry reindex` reports
`changed: false`.
