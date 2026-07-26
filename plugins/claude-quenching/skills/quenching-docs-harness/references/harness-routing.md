# Harness routing — from a CLAUDE.md/AGENTS.md unit to its OKF home

How `quenching-docs-harness` decides, for each unit of a harness file, whether it **stays** (harness-
operational) or **moves** into an OKF home (durable knowledge). Once a unit is routed to a home it
is filed exactly as `quenching-docs-add` would — see
[../../quenching-docs-add/references/homes.md](../../quenching-docs-add/references/homes.md) for the
`type`/mold/path shape and the index/log procedure, and
[../../quenching-docs-align/references/taxonomy.md](../../quenching-docs-align/references/taxonomy.md) for the
home boundaries.

## Contents

- [1. What a harness file is](#1-what-a-harness-file-is)
- [2. Content units](#2-content-units)
- [3. The one decision rule](#3-the-one-decision-rule)
- [4. Verdict table — unit kind → verdict → destination home (`type`)](#4-verdict-table--unit-kind--verdict--destination-home-type)
- [5. Pointer-honesty checklist (the step-8 verify gate)](#5-pointer-honesty-checklist-the-step-8-verify-gate)
- [6. Nesting rules](#6-nesting-rules)
- [7. AGENTS.md](#7-agentsmd)

## 1. What a harness file is

`CLAUDE.md` and `AGENTS.md` are **navigation pointers** the Claude Code / agent harness
auto-loads — `CLAUDE.md` repo-wide, a subfolder `CLAUDE.md` only when working under its folder.
OKF-strict point 7 ([../../quenching-docs-align/references/okf-spec.md](../../quenching-docs-align/references/okf-spec.md))
says they are **not** OKF concepts: they carry **no frontmatter** and **no `type`**, and the
validator (`okf-validate.py`) **skips them entirely** — including link checks (`index-broken-link`
runs only on `index.md`). So a CLAUDE.md that inlines a rule or lies about a link is **machine-
invisible**: it escapes validation, is invisible to anyone browsing `docs/`, and drifts from the
real doc. Pointer honesty is therefore this skill's job, not the validator's. The target shape is
the shipped exemplar [../../../assets/docs/standards/CLAUDE.md](../../../assets/docs/standards/CLAUDE.md)
("thin pointer, never a copy").

## 2. Content units

Parse each harness file into **units**, one verdict each:

- a **heading section** (a `##`/`###` and its body),
- a **fenced command block** (```` ``` ````),
- a **bullet run** (a contiguous list),
- a **paragraph**.

Capture each unit's text, its anchor (heading slug), and any links it carries. **Split a mixed
unit** — a section that pairs a build command (KEEP) with an architecture note (MOVE) becomes two
units. One unit, one verdict.

## 3. The one decision rule

> **Commands and etiquette stay; knowledge moves.** Would the agent need this on **EVERY** task
> under this file's folder → **keep**. Only when working on **that subject** → **move + pointer**.
> A harness file is context tax paid on every turn; it earns each line.

## 4. Verdict table — unit kind → verdict → destination home (`type`)

| The unit is… | Verdict | Destination home (`type`) |
| --- | --- | --- |
| build / run / test / lint commands, env vars, ports | **KEEP** | stays in the harness file |
| agent etiquette, permissions, tool rules | **KEEP** | stays — *unless* it is a team-wide process rule proven beyond the agent ⇒ **MOVE** `standards/workflows/` (`standard`) |
| environment quirk needed every turn | **KEEP** | stays in the harness file |
| architecture description / module map | **MOVE** | `standards/architecture/` (`standard`; unproven ⇒ `authority: background`), or `knowledge/<subject>/` (`knowledge`) if non-binding |
| coding / naming conventions | **MOVE** | `standards/code/` · `standards/naming/` (`standard`) |
| "we chose X because Y" — agreed / proven | **MOVE** | `standards/` (`standard`; agreed-but-unproven ⇒ `authority: background`, proven ⇒ `current`) — no separate decision home |
| roadmap / TODO / next-steps item (raw, unscoped) | **MOVE** | `specs/backlog/` (`task`, untriaged — via `quenching-specs-backlog-add`, outside the OKF bundle), or `vision/` (`vision`) for settled direction with no deadline |
| step-by-step procedure / onboarding | **MOVE** | `documentation/how-to/` (`documentation`) |
| facts about an external tool / lib / service | **MOVE** | `reference/{tools,libraries,regulations}/` (`reference`) |
| domain concept / glossary term | **MOVE** | `knowledge/<subject>/` (`knowledge`) |
| schema / table descriptions | **MOVE** | `catalog/…` (`schema` / `table`) |
| restates a fact an existing doc already holds | **DEDUPE** | cite the existing doc; cut + leave a pointer |
| contradicts an existing doc | **FLAG** | per-item: fix the doc, fix the file, or both — resolve, never auto-pick |
| secrets / credentials / personal notes / `CLAUDE.local.md` | **UNROUTABLE** | stays + reported; secrets urged out-of-band, NEVER into shared `docs/` |
| no documentary home | **UNROUTABLE** | stays + reported |

**Tie-breakers** are `quenching-docs-add`'s — "how **WE** do it" (proven) → `standards/`
(`authority: current`); agreed-but-unproven → `standards/` (`authority: background`); a fact
about a **named external** asset → `reference/`; generic understanding → `knowledge/`; a
**parked task** → `specs/backlog/` (via `quenching-specs-backlog-add`); **direction** → `vision/`; a
**procedure** → `documentation/how-to/`. Don't duplicate them here — see
[../../quenching-docs-add/references/homes.md](../../quenching-docs-add/references/homes.md).

## 5. Pointer-honesty checklist (the step-8 verify gate)

The validator won't check harness files, so this skill does:

- **Every link resolves** — each `[..](..)` target exists on disk (the file, the anchor).
- **Each pointer's one-liner matches its target** — the bullet describes what the doc really
  holds; no stale or aspirational description.
- **No moved fact is paraphrased inline** — a MOVED unit leaves the harness file entirely; only a
  citing pointer remains.
- **Only KEEP residue + pointers + the trailing harness comment remain** — no orphaned knowledge.
- **No frontmatter** — a harness file never carries frontmatter or a `type`.
- **Size budget** — root ≤ ~60 lines, subfolder ≤ ~20 (the exemplar is 18). Over budget ⇒ more
  knowledge still needs to move.

## 6. Nesting rules

- **Root `CLAUDE.md`** = repo-wide operations + the `docs/` home map. Auto-loads on every turn.
- **Subfolder `CLAUDE.md`** = nearest-file navigation (auto-loads only under that folder): the
  folder's local commands/quirks + a pointer to the home that **covers** it. **Never duplicate the
  root.**
- **Creation is evidence-gated.** Propose a new subfolder pointer **only** where the evidence is
  concrete — never blanket-create one per directory. Two evidence sources, each gated per item:
  1. **A unit scoped to a folder** — a harness file being refactored holds a KEEP-class unit (local
     commands/quirks) that clearly belongs under a subfolder; the pointer lands there.
  2. **A greenfield folder** (step 1's discovery pass, swept **repo-wide from the root** — never
     scoped to the folders that already have a `CLAUDE.md`, since those are precisely the ones a
     hand-picked list would over-represent) — a folder with a **local operational surface** but
     **no** `CLAUDE.md`: a `*.sh` / `Makefile` / `justfile` / `package.json`-script, a distinct
     toolchain, or a `README` whose fenced blocks are run-commands. It earns a `CLAUDE.md`
     **only** if it passes the §3 decision rule: the agent would need those commands on **every**
     task under that folder and they **don't derive from the root**. Fill the thin
     `claude-subfolder.md` mold — the local commands (KEEP) + a pointer to the home that covers the
     folder; the folder's `README` stays the deep map, the `CLAUDE.md` just points to it.
- **Exclude from discovery** generated-output, asset, and vendored dirs — `.build/`, `dist/`,
  `build/`, `target/`, `node_modules/`, `**/__pycache__/`, `fonts/`, `assets/`, `.venv/`, nested
  `site-packages`/vendored dependency trees, and anything gitignored as a build artifact (verify
  with `git check-ignore`, don't assume from the path alone). A folder that only holds data or
  output earns no harness.
- `quenching-docs-align`'s skeleton already owns `docs/standards/CLAUDE.md`.

## 7. AGENTS.md

Same pipeline as `CLAUDE.md`, run **independently**. A fact duplicated between `CLAUDE.md` and
`AGENTS.md` is itself a **FLAG** item; consolidation (make `AGENTS.md` canonical and `CLAUDE.md` a
one-line reference to it, or vice-versa) is a **per-repo proposal**, never assumed — surface it,
let the user choose.
