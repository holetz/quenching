---
okf_version: "0.1"
---

# Every repository, the same shape

**quenching** is a Claude Code plugin. Point it at a repository and its knowledge, its plans, its
design source, automation, operations and verification each converge onto one canonical, verifiable structure — probed first, planned
once, changed only on your OK.

In metallurgy, *quenching* is the rapid cooling that fixes a metal's structure and makes it hard.
This plugin does that to a repository: whatever loose shape your knowledge base, your plans and
your `.claude/` automation have today, one pass fixes each of them into a canonical structure —
and keeps it hard against drift, because every front ships a verifier that can prove the shape
before anyone touches a file.

## Choose your path

- **Get it running** — from install to your first verified alignment, in a handful of commands:
  [the getting-started tutorial](tutorials/getting-started.md).
- **Do a task** — adopt quenching in a repo, drive one spec to merge, publish a docs site:
  [the how-to guides](how-to/index.md).
- **Understand why** — the five local fronts, the OKF bundle, the DTCG design source, and the provider-owned spec lifecycle:
  [the explanations](explanation/index.md).
- **Look it up** — all forty-seven commands, the local automation registry:
  [this project's reference](project/index.md), and the [glossary](glossary.md).

## The problem

A repository that grows with AI agents accumulates drift across its knowledge, provider-owned plans,
design, automation, operations and verification surfaces. Knowledge
scatters across READMEs, wikis and chat threads, so every session re-derives what the last one
already learned. Plans live in prose nobody can verify, so "done" is an opinion. And the
`/.design/` accumulates duplicated or stale visual values, while the `.claude/` automation surface grows one ad-hoc command at a time, until no two repositories —
and no two commands — look alike.

Each kind of drift makes the next one worse: an agent without durable knowledge writes vaguer
plans, and vaguer plans produce automation nobody dares to reorganize.

## The solution

quenching acts on five local surfaces where that drift lives, with **the same interface on each**:
each local front has exactly ONE `align` command that probes first — a clean front costs a couple of
tool calls and stops there — then presents one consolidated plan and waits for one OK before
writing anything.

| Surface | What converges | The one align |
| --- | --- | --- |
| `/docs/` | a canonical **OKF bundle** — standards, concepts, glossary, and this site | `/quenching:knowledge:align` |
| Specs | a provider-owned plan cycle on **GitHub issues or Azure Boards** | cycle and status commands |
| `/.design/` | one DTCG source projected to portable Impeccable and editorial media artifacts | `/quenching:design:align` |
| `.claude/` | one file per entry point, every description audited | `/quenching:components:align` |
| `ops` | a declared operations root, its entry-point inventory, registry and lifecycle/write policy | `/quenching:ops:align` |
| `proof` | test layers, fixture ownership, gate evidence, measured surfaces and the coverage floor | `/quenching:proof:align` |
| *(git)* | nothing — a pillar that answers questions, converges no tree | *(none, by design)* |

One more command, `/quenching:align`, conducts the five local aligned fronts in dependency order on a single
OK. Read [the operating model](explanation/operating-model.md) and you know the whole plugin.

## Quick start

```bash
claude --plugin-dir ./plugins/quenching   # load the plugin into Claude Code
cq --version                              # 6.3.0 — the bundled CLI answers
```

Then, inside the session, ask for a read-only status before you change anything:

```text
/quenching:knowledge:status
```

The full path — install, probe, first alignment — is the
[getting-started tutorial](tutorials/getting-started.md).

## This page is also the bundle's front door

Everything above and below it lives in one **Open Knowledge Format (OKF v0.1)** bundle rooted at
`/docs/`. Each **home** has a fixed name and a single purpose, so anyone moving between
repositories that adopt this method finds the **same tree in the same place**. This `index.md` is
that bundle's reserved listing — the only one carrying frontmatter, and only `okf_version`. Folder
names and frontmatter keys are canonical English kebab-case; the language of authored prose is
owned by [standards/agents/communication.md](standards/agents/communication.md).

### Homes

* [standards/](standards/index.md) — how **WE** do it (current contracts/conventions), by subject; agreed-but-unproven rules sit here as `authority: background`
* [vision/](vision/index.md) — direction segmented by area, no deadline
* [tutorials/](tutorials/index.md) — learning-oriented pages, the Diátaxis tutorial quadrant
* [how-to/](how-to/index.md) — task recipes for a reader with a goal
* [explanation/](explanation/index.md) — why the product works the way it does
* [project/](project/index.md) — the manual for *this* repository: its commands, its automation, its layout
* [concepts/](concepts/index.md) — generic knowledge we hold (domain concepts, explanations, learnings); ships the fixed [glossary.md](glossary.md) term lookup
* [external/](external/index.md) — facts about what **WE CONSUME** (external, background)
* [catalog/](catalog/index.md) — our **data** / domain (`system/catalog/schema/table`)

### Boundaries (memorable summary)

- `standards/` = "how **WE** do it (current/active)"; an agreed-but-unproven rule sits here as `authority: background` (no separate decisions home).
- `concepts/` = "generic **understanding** we hold" (concepts/explanations; non-binding).
- `external/` = "facts about what **WE CONSUME** (external, background)".
- `catalog/` = "our **data** / domain".
- `tutorials/` `how-to/` `explanation/` `project/` = the **reader-facing** quadrants; a published page belongs here, internal team understanding in `concepts/`, a current contract in `standards/`.
- The **task inbox** lives at `/.specs/backlog/`, **outside** this bundle (quenching-managed).
- `patterns` **is not a silo** — it dissolves into `standards/architecture/`.

**Resolving a term.** Unfamiliar repo word, acronym, or codename? Look it up in the glossary
first — [glossary.md](glossary.md), the A–Z lookup (one entry per term, linked to its full doc
when one exists): `grep -i '<term>' docs/glossary.md`.

The full contract (homes, types, migration doctrine, conformance) lives in the `quenching`
skills' `references/`.

## TL;DR for agents

- Contract: five local fronts (`knowledge`, `design`, `components`, `ops`, `proof`) plus the
  provider-owned `specs` flow and a `git` pillar; ONE align per local front, probe-first;
  `/quenching:align` conducts the five aligned fronts on one OK.
- Rails: `cq` CLI — `cq knowledge`, `cq specs`, `cq design`, `cq components`, `cq ops`, `cq proof`, `cq git`; uniform `--json`;
  exit codes `0` ok · `1` findings · `2` refusal.
- Invariants: nothing is written before a human OK; blast radius reaching product code
  confirms on its own; a probe that finds nothing ends the run.
- Canonical anchors: [#the-problem](#the-problem), [#the-solution](#the-solution),
  [#quick-start](#quick-start); command catalog at [project/commands.md](project/commands.md).
