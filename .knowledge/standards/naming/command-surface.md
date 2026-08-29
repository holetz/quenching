---
type: standard
title: Command surface naming
description: How the plugin's commands are named and namespaced — one file per entry point, where the path is the identity; the design namespace for DTCG source and projections; the fifth namespace (`git`, a pillar rather than a front) and its coexistence with a target's own `git` category; the components front's four sibling contexts, each named for the artifact it mints, and the rule that keeps a front-level verb off an artifact-level context
resource: plugins/quenching/commands/**
tags: [naming, commands, taxonomy]
timestamp: 2026-08-27
audience: both
authority: current
source: rename-command-surface change (2026-07-21) + the specs-native refactor (2026-07-24) + collapse-skills-into-commands (2026-07-26) + correct-command-citation-form (2026-07-31); the `.claude/` front renamed `components` and split into four artifact-named contexts by modularizar-specs-knowledge-components (task 9.7, 2026-08-10), inheriting the split's own design from the retired restructure-claude-front-namespace spec — the split is orthogonal to the front's name and survived the rename intact; the declare-the-class rule for a rename's citation residual added by the orquestrar-specs-em-paralelo branch review (2026-08-16), whose `orchestrate` → `cycle` command rename found five citing files its `## Impact` had not named; the fourth namespace (`git`) and its coexistence with a target's own `git` category added by pilar-git-e-specs-agnosticas-ao-git (task 6.2); varrer-nomes-de-comando-legados (2026-08-27) — the front-level-verb example no longer cites the retired specs align
maintainer: quenching
---

# Command surface naming

How the `quenching` plugin names its commands.

## The path IS the identity

**One file per entry point.** Claude Code merged custom commands into skills, so
`commands/<front>/[<object>/]<verb>.md` carries both the description that routes to it and the
body that runs. The path `<front>/[<object>/]<verb>` is the identity — the `:` separator, one per
path segment — and everything below is how that one identity is *spelled* at a call site.

### Three citation forms, and the condition on each

The axis is **where the command comes from**, never who is reading. Same file, three spellings,
and only one of them is unconditionally correct for this repo's commands:

| Form | Example | Correct when |
| --- | --- | --- |
| Registry name (no `/`) | `quenching:specs:develop` | the `Skill` tool resolves it — always, for a plugin command |
| Plugin-prefixed slash | `/quenching:specs:develop` | a human types it wherever `quenching` is installed **as a plugin** |
| Bare slash | `/commands:tighten` | **only** where that command file lives in the target repo's own `.claude/commands/` |

So `commands/specs/develop.md` is cited as `quenching:specs:develop` for the tool and
`/quenching:specs:develop` for the human — and bare **only** by a repo that vendored the file into
its own `.claude/commands/`. Re-measured in this tree on 2026-08-26: that directory does exist
here, and holds four commands of this repo's own — `/release`, `/skill-map`, `/commands:tighten`
and `/references:tighten` — which is why the bare row's example is one of them. Not one plugin
command is vendored there, so every bare citation of a **plugin** command in this repo's prose
still names a form that resolves nowhere.

That distinction is the reason `assets/checks/citation-check.sh` spells its dead set as each
retired front's **verbs** rather than as a bare prefix. A verb list asserts what was retired; a
prefix reserves a namespace, and would condemn any bare command that later lands under it — which
is not hypothetical, because until 2026-08-26 the four above included a `/docs:`-prefixed local
command that had nothing to do with the plugin's retired `docs` front.

This mapping is what every command body copies, which is why it states the condition rather than
the shorthand. The prose form of the same rule used to live in `commands/docs/align.md`, declaring
two forms and calling the bare one "what a human types"; that claim authorised 687 bare citations
across the repo before it was corrected.

There is **no second name**. The `quenching-<front>-<object>-<verb>` skill name this standard once
mandated existed to be *mirrored* by a command path; with nothing to mirror, it is retired, and
with it the bijection rule, the mirroring requirement, and the two root exceptions that needed
`sk-path-mismatch` recorded as intended. Nothing derives a name that could disagree with the path,
so nothing checks that they agree.

## Namespaces are honest by front

The surface is partitioned by the artifact each front's commands touch:

- **`/quenching:knowledge:`** — the OKF `/.knowledge/` bundle.
- **`/quenching:specs:`** — provider-owned spec documents and their lifecycle.
- **`/quenching:design:`** — the `/.design/` DTCG source, projections, and editorial genres.
- **`/quenching:components:`** — the target repo's `.claude/` automation surface.
- **`/quenching:git:`** — the fifth namespace, and the odd one out: it names a **pillar**, not a
  front. The other four converge a tree toward a canonical shape; `git` answers questions about
  the target repository's own live git state instead, which is why it carries no `align` verb of
  its own — see [../architecture/align-surface.md](../architecture/align-surface.md) §The fifth
  pillar has no align.
- **root `/align`** — deliberately outside the four front namespaces, because it is the one
  command that spans the three local aligned fronts. Under the old rule it was an exception the linter had to be
  told about; now it is simply a command at the top of the tree.

**A target repo's own `git` category coexists with this namespace, and never collides with it.**
A target may mint its own `/git:commit` or `/git:cleanup` under its own `.claude/commands/git/` —
`components-command-new/taxonomy.md`'s own canonical category example — naming a convention that
repo declared for itself. §Three citation forms is what keeps the two apart: the plugin's own
`git` commands are always spelled `/quenching:git:<verb>` (or bare, only inside this repo's own
`.claude/commands/`, which does not hold one), so a target's bare `/git:<verb>` names its own
command and nothing this plugin ships, on every repo that installs it.

This clause named a second root, `/align-and-update`, until the specs-flow-consolidation spec
deleted it from all four fronts — see
[../architecture/align-surface.md](../architecture/align-surface.md), which has said the surface is
a one-column align surface. Two `authority: current` standards disagreeing about what exists is worse than
either being merely out of date, which is why a rename's blast-radius sweep below has to reach the
standards and not only the code.

A command's namespace MUST match what it touches: a command that mints commands lives under
`/quenching:components:`, never `/quenching:knowledge:`; a command that reads or writes the bundle
lives under `/quenching:knowledge:`.

## `components` — four contexts, each named for the artifact it mints

The `.claude/` front used to be named `skill`, and that name carried a defect independent of the
namespace rename: `skill` was simultaneously the front's own name and the name of one artifact
*inside* it, so its front-root `new` verb minted a command while its nested `agent:new` verb minted
a subagent — two artifact levels, one of them wearing the front's own name, treated as if one were
a sub-type of the other.

`components` does not have that defect: no artifact under this front is called "a component". It
holds **four sibling contexts, each named for the artifact it mints, none a sub-type of another**:

| Context | Mints | Front-level verb | Artifact-level verbs |
| --- | --- | --- | --- |
| *(front root)* | — | `/quenching:components:align` | — |
| `command/` | a command | — | `/quenching:components:command:new`, `/quenching:components:command:eval`, `/quenching:components:command:retro` |
| `agent/` | a subagent | — | `/quenching:components:agent:new` |
| `hook/` | a hook | — | `/quenching:components:hook:new` |
| `harness/` | — | — | `/quenching:components:harness:align` |

**The rule: a front-level verb sits at the front's own root; an artifact-level verb sits under its
context.** `/quenching:components:align` is the front's own sweep — it has no artifact of its own
to sit under, so it stays at the root, exactly as `/quenching:knowledge:align` does for its
front. `command:new`, `command:eval` and `command:retro` are three verbs that all act
on the same artifact (a command), so they share the `command/` context rather than each claiming a
piece of the front root the way the old front's `new`/`eval` verbs used to.

`/quenching:components:harness:align` is the one entry that **changed front**, not merely name:
`CLAUDE.md` and `AGENTS.md` are files Claude Code reads as instruction, which makes the harness an
artifact of `components` — the front that owns everything Claude Code loads as automation — never
a `knowledge` document, even though refactoring them moves durable knowledge *into* the bundle as a
side effect. The move is the front boundary stated correctly, not an exception to it.

## Verb-first names that reveal the action

A command name is a verb (or verb-object) that names its action, so the `/` menu tells the story
without the description. A name MUST NOT be a bare noun that reads as a query, a jargon term when
a plain verb exists, or a name whose apparent object differs from what it acts on (a name that
lies). The object is named when the verb alone is ambiguous
(`glossary-backfill`, not `knowledge-scan`).

This rule also governs directory names, which is why the collapse left no `skills/` directory
holding no skills: a name that lies is forbidden of the surface this standard governs.

## The surface invariant, and clean renames

- **Every command carries a non-empty `description`, and no two resolve to the same `/` path.**
  That is the whole invariant, and it is what replaced the bijection. `cq components doctor --json`
  decides it; the **count is not written down here**, because a number transcribed into prose goes
  stale the first time a command is minted. This standard once said "27 skills, 27 wrappers" while
  the surface carried 28, which is the whole argument.
- **`commands/**` is the only tree Claude Code registers**, so nothing that is not an entry point
  lives under it — see [../architecture/plugin-layout.md](../architecture/plugin-layout.md).
- A rename is **clean** — no compatibility aliases, no dual-registered names. A blast-radius sweep
  updates every reference (branch names, CI, scripts) and a rename reaching product code gets its
  own confirmation. The collapse took this literally at the largest scale the repo has seen: no
  `skills/` shim, no dual registration, no transitional period — the same discipline the `docs`/
  `skill` → `knowledge`/`components` rename applied to itself.
- **A rename's `## Impact` declares the *class* of citing files, never the list.** The list is the
  one thing the author cannot hold: `orquestrar-specs-em-paralelo` named the files its tasks
  rewrote and missed five more carrying the old name — a sibling command body, two standards, a
  GENERATED zone and a golden fixture — which the sweep dragged in anyway because its gate demanded
  a zero-result grep. Declare the class and make that grep the gate, exactly as
  [../workflows/retiring-a-standard.md](../workflows/retiring-a-standard.md) already requires of a
  retired standard; a `## Impact` that enumerates instead is a list that will be short.

## Why there is no longer a wrapper

This standard used to carry a §*Why the wrapper still exists*, arguing that the mandatory 1:1
wrapper bought exactly one thing — the `:`-namespaced `/` tree — at a measured cost of ~2,072
characters always in context, and closing with an explicit revisit trigger:

> reconsider it when the pre-refactor components script's `budget` verb shows wrapper descriptions displacing skill descriptions.

**That trigger fired, from the other side.** The question was never whether the wrapper displaced
the skill description; it was that the *skill* description was the redundant one. Collapsing into
the wrapper's file keeps the entire discovery story — same `/` tree, same paths, same namespaces —
and deletes the other description outright. Always-on metadata fell from 30,705 characters to
2,069.

**What that saving cost, and what it did not.** The deleted description is where the quoted
trigger phrases and the `Not for:` boundary lived, so every command now reports
`sk-trigger-position` and `sk-no-boundary` against a description written as a `/`-menu label.
Both are warnings, so no gate catches it — which is why it is recorded here instead.

**Spoken routing was measured, not assumed, and it survived.** On 2026-07-26, three natural
phrases with no `/` typed each reached their command by description alone in a fresh `claude -p`:
*"park a spec for later…"* and *"capture this for the backlog…"* both reached `/specs:capture`,
and *"add a standard: we always use snake_case…"* reached `/quenching:knowledge:add`. So a
description naming only the action **does** still route — the claim that it would not is
contradicted by the measurement.

What remains is a **thinner margin**, not a broken surface: routing now rests on the model
inferring intent from a short action label rather than matching a verbatim trigger the author
chose, and no description states which adjacent command owns the neighbouring job. That is a
structural risk the three probes cannot rule out — they show the common phrasings work, not that
every phrasing does. Restoring triggers and boundaries is **available headroom, not a defect to
repair**: it would cost characters the collapse just freed, and it should be decided on measured
should-trigger / should-not-trigger rates, per [../automation/skills.md](../automation/skills.md).

## Canonical English surface

Command paths, folder names, frontmatter keys, and `type` values are canonical English (cross-repo
greppable); identifier-derived slugs stay verbatim. Which language the body prose is written in is
not this doc's rule — [../agents/communication.md](../agents/communication.md) owns it.
