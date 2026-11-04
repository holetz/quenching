---
type: standard
title: Command surface naming
description: How the plugin's commands are named and namespaced — one file per entry point, where the path is the identity; the module prefix each front publishes under and the full command and agent mapping; the design namespace for DTCG source and projections; the proof namespace for the verification surface rather than its test artifact; the seventh namespace (`git`, a pillar rather than a front) and its coexistence with a target's own `git` category; the components front's four sibling contexts, each named for the artifact it mints, and the rule that keeps a front-level verb off an artifact-level context; and the one-segment skill name of a target repository
resource: quenching/skills/**, quenching/agents/**, quenching/assets/modules.json
tags: [naming, commands, taxonomy]
timestamp: 2026-11-03
audience: both
authority: current
source: rename-command-surface, 2026-07-21, 2026-07-24, collapse-skills-into-commands, 2026-07-26, correct-command-citation-form, spec 1635 (module extraction), spec 1637 (the `quenching-opensource` module), spec 2118 (one-segment target skill names); spec 2160 (install only by deploy); lineage in ADR 0004 and ADR 0013
maintainer: quenching
---

# Command surface naming

<!-- rules -->

How the `quenching` plugin names its commands.

## The folder IS the identity

**One folder per skill.** `skills/<name>/SKILL.md` carries both the description that routes to it
and the body that runs; the folder name is the skill name, never derived from a path. A vertical with
many flows (`specs`, `git`, `knowledge`, `components`) is **one router skill** whose flows live in its
own `references/<flow>.md`, so a flow has no skill of its own and no shortcut. The other fronts keep
one skill per command, named `quenching-<front>-<verb>` (`quenching-design-genre-new` for the one
nested verb).

### Two citation forms, and the condition on each

The axis is **where the skill comes from**, never who is reading:

| Form | Example | Correct when |
| --- | --- | --- |
| Router and flow | `/quenching-specs develop` | the skill is a router of this plugin: the router id, a space, the flow named in its table |
| Skill name | `/quenching-handoff`, `/quenching-design-align` | the skill has no flows: its own folder name |
| Target skill | `/commands-tighten` | the skill lives in the target repo's own `.agents/skills/commands-tighten/` (§A target's skill name is one segment) |

The `Skill` tool takes the router name and the flow as its argument:
`Skill("quenching-specs", "develop <id>")`. A flow written as one hyphenated token
(`/quenching-specs-develop`) names a skill that does not exist, and `sk-dangling-citation` reports
it. Bare slash forms with a `:` separator (`/commands:tighten`) belong only to a repo that keeps the
legacy `.claude/commands/` layout.

That distinction is the reason `assets/checks/citation-check.sh` spells its dead set as each
retired front's **verbs** rather than as a bare prefix. A verb list asserts what was retired; a
prefix reserves a namespace, and would condemn any bare command that later lands under it.

There is **no second name**. Nothing derives a name that could disagree with the folder, so nothing
checks that they agree.

### A target's skill name is one segment

In a target repository a skill lives at `.agents/skills/<name>/SKILL.md`, and `<name>` is **one path
segment**: `<front>-<verb>`, or `<front>-<object>-<verb>`, joined by `-`. The `SKILL.md` frontmatter
`name:` equals the folder name, and the skill is invoked as `/<name>`. Claude Code 2.1.312 does not
discover a nested `.claude/skills/<a>/<b>/SKILL.md` (only the flat sibling is listed), and the Claude
bridge is a byte copy of `.agents/skills/` ([surface-translation.md](../architecture/surface-translation.md)
§Target repositories), so a nested source would vanish from Claude. The legacy
`.claude/commands/<a>/<b>.md` (`/a:b`) migrates to `.agents/skills/<a>-<b>/SKILL.md` (`/a-b`), and
`cq components migrate` rewrites the `/a:b` invocations in the bodies it moves. The plugin's own
commands keep their `:` identity: this rule governs a target's surface, not the package.

## The plugin prefix is the module

The source is split into modules ([../architecture/plugin-layout.md](../architecture/plugin-layout.md)
§One editable source, installed by deploy), and each module owns a list of skills in the `owned.skills`
record of `quenching/assets/modules.json` (`schemaVersion` 3). Every skill and every agent belongs to
exactly one module:

| Module | Skills it registers | Agents |
| --- | --- | --- |
| `quenching-specs` | `/quenching-specs`, `/quenching-handoff`, `/quenching-align` | `quenching-spec-orchestrator`, `-reviewer`, `-runner`, `-scout`, `-verifier` |
| `quenching-git` | `/quenching-git` | — |
| `quenching-knowledge` | `/quenching-knowledge` | — |
| `quenching-components` | `/quenching-components` | — |
| `quenching-design` | `/quenching-design-*` | — |
| `quenching-ops` | `/quenching-ops-*` | — |
| `quenching-proof` | `/quenching-proof-*` | — |
| `quenching-toolchain` | `/quenching-toolchain-*` | — |
| `quenching-delivery` | `/quenching-delivery-*` | — |
| `quenching-security` | `/quenching-security-*` | — |
| `quenching-opensource` | `/quenching-opensource-*` | — |

`quenching-specs` also owns the root `align`, because it is the mandatory module and `align` only
conducts the modules that are installed.

- **The map has one home.** The front-to-module assignment is the `owned` record of each module in
  `quenching/assets/modules.json`; `quenching.common.modules.namespace_map` derives the
  table above from it. The table is a reading of that record, never a second source.
- **The published name is written in the source.** Bodies, agents, references, the README and the
  Python literals that recognize ids spell `/quenching-<vertical> <flow>` or the skill name; the bare `quenching:` prefix
  survives only as the source's own unpublished registration and in history (`docs/decisions/`,
  `CHANGELOG.md`).
- **Flows stay inside their router.** A flow keeps its name (`/quenching-knowledge add`, never
  the router dropped), so the reference below the router is
  still the folder under `skills/` and §The folder IS the identity holds unchanged.
- **A route into another module is conditional.** A `Not for:` hand-off, an offer or a `Skill`
  call naming another module's command runs only when that module is enabled; otherwise it is
  reported `not-installed: <module>` and never invoked
  (`quenching/references/align/tool-resolution.md` §Routing into another module).
  A wildcard such as `/quenching-knowledge *` names every flow of one router and carries the same
  condition.

## Namespaces are honest by front

The surface is partitioned by the artifact each front's commands touch:

- **`/quenching-knowledge`** — the OKF `/docs/` bundle.
- **`/quenching-specs`** — provider-owned spec documents and their lifecycle.
- **`/quenching-design-`** — the `/.design/` DTCG source, projections, and editorial genres.
- **`/quenching-components`** — the target repo's `.claude/` automation surface.
- **`/quenching-ops-`** — the target repository's canonical operations surface. It is the fifth
  local aligned-front namespace; its contract and command bodies are now published.
- **`/quenching-proof-`** — the target repository's verification surface: its layers, fixtures,
  gates, and CI. It is the sixth plugin namespace and the fifth local aligned-front namespace. The front is named `proof`, not `tests`, because
  `tests` would name an artifact inside the surface rather than what the surface produces; the
  same front-versus-artifact distinction is why `components` replaced `skill`.
- **`/quenching-git`** — the seventh namespace, and the odd one out: it names a **pillar**, not a
  front. The other six namespaces name fronts or the provider-owned specs flow; only the five
  local fronts converge a tree toward a canonical shape. `git` answers questions about the target
  repository's own live git state instead, which is why it carries no `align` verb of its own —
  see [../architecture/align-surface.md](../architecture/align-surface.md) §The seventh pillar has
  no align.
- **root `/align`** — deliberately outside the front namespaces, because it is the one command
  that spans the five local aligned fronts. Under the old rule it was an exception the linter had to be
  told about; now it is simply a command at the top of the tree.

The namespace list has seven entries in total: six front or provider-flow namespaces and the
alignless `git` pillar. Exactly five of those namespaces are local aligned fronts and are conducted
by `/align`; `specs` remains provider-owned and `git` remains a pillar without an align.

**A target repo's own `git` category coexists with this namespace, and never collides with it.**
A target may mint its own `/git:commit` or `/git:cleanup` under its own `.claude/commands/git/` —
`components-command-new/taxonomy.md`'s own canonical category example — naming a convention that
repo declared for itself. §Three citation forms is what keeps the two apart: the plugin's own
`git` commands are always spelled `/quenching-git <verb>` (or bare, only inside this repo's own
`.claude/commands/`, which does not hold one), so a target's bare `/git:<verb>` names its own
command and nothing this plugin ships, on every repo that installs it.

This clause named a second root, `/align-and-update`, until the specs-flow-consolidation spec
deleted it from all six front namespaces — see
[../architecture/align-surface.md](../architecture/align-surface.md), which has said the surface is
a one-column align surface. Two `authority: current` standards disagreeing about what exists is worse than
either being merely out of date, which is why a rename's blast-radius sweep below has to reach the
standards and not only the code.

A command's namespace MUST match what it touches: a command that mints commands lives under
`/quenching-components`, never `/quenching-knowledge`; a command that reads or writes the bundle
lives under `/quenching-knowledge`.

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
| *(front root)* | — | `/quenching-components align` | — |
| `command/` | a command | — | `/quenching-components command-new`, `/quenching-components command-eval`, `/quenching-components command-retro` |
| `agent/` | a subagent | — | `/quenching-components agent-new` |
| `hook/` | a hook | — | `/quenching-components hook-new` |
| `harness/` | — | — | `/quenching-components harness-align` |

**The rule: a front-level verb sits at the front's own root; an artifact-level verb sits under its
context.** `/quenching-components align` is the front's own sweep — it has no artifact of its own
to sit under, so it stays at the root, exactly as `/quenching-knowledge align` does for its
front. `command:new`, `command:eval` and `command:retro` are three verbs that all act
on the same artifact (a command), so they share the `command/` context rather than each claiming a
piece of the front root the way the old front's `new`/`eval` verbs used to.

`/quenching-components harness-align` is the one entry that **changed front**, not merely name:
`AGENTS.md` is the file Claude Code and the other harnesses read as instruction; `CLAUDE.md` is legacy, which makes the harness an
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
- **`skills/**` is the only tree Claude Code registers**, so nothing that is not an entry point
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

<!-- rationale -->

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
and *"add a standard: we always use snake_case…"* reached `/quenching-knowledge add`. So a
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
