---
type: standard
title: Spec file contract
description: The one-file spec, its fourteen canonical sections, the phase-scoped explicit-none rule, the parsed Impact sub-heading, the duplicated template and the three-copy record vocabulary, and how to read a v1 plan in specs/archive/
resource: plugins/quenching/assets/specs/templates/spec.md, plugins/quenching/assets/specs/schema.json, plugins/quenching/assets/bin/specs.py, plugins/quenching/commands/specs/**
tags: [workflows, specs, sections, gates, validation]
timestamp: 2026-08-03
audience: both
authority: current
source: specs-front-v2 plan (sections 1-2); lifecycle claims superseded by the specs-flow-consolidation plan; the `## Overview` section added by the add-eli5-section-to-specs spec; the `moment` axis, the `§`addressed `## Impact` bullet and the schema entry in the three-file lockstep by the narrow-the-execute-preamble spec; `date` moved out of the basename, `verification` became optional and the slug's language was named by evaluate-spec-creation-flow (task 5.5); both duplicated constants shown to be selftest-only once nothing installs the tool (2026-08-03, enxugar-create-e-eliminar-o-rung-hooks spec)
maintainer: quenching
---

# Spec file contract

What a spec must **contain**, which parts a machine checks, and what each gate does and does not
guarantee. The per-section *authoring* doctrine (what to write under each heading) lives in
`assets/references/specs-develop/artifacts.md`; the layout and tool surface in the sibling
`spec-driven.md`. This standard is the **contract** those two implement.

**Scope: the file, not the lifecycle.** Where a spec lives, which stages are derived, and which
human judgments frontmatter records are [plan-lifecycle.md](plan-lifecycle.md); how the work is
recorded in git is [plan-git-record.md](plan-git-record.md). This file's earlier v2 *lifecycle*
claims — the three-folder phase model, promote-as-the-human-OK, and the minimal frontmatter list —
are superseded by those two and now stand here only as pointers.

**This also supersedes the v1 plan-artifact contract** that this file previously held — three
artifacts (`proposal.md`, `design.md`, `tasks.md`) plus a `.specs.json` sidecar, gated by
`applyRequires`. Plans written under that contract still sit in `specs/archive/`; §Reading a v1
plan below is what a reader of those needs.

## One spec is one file

A spec is a single markdown file for its entire lifecycle. Phases enrich it; they never split it.
It is named `<slug>.md` **in every folder** — the basename IS the identity key — and the capture
date is stamped once into the frontmatter's `date:` and never rewritten; a promote moves the file
without renaming it.

Two consequences are load-bearing:

- **Identity is the slug, not the path.** Every cross-reference names the bare slug; the tool
  resolves it to the one spec whose basename is `<slug>.md`, wherever it sits, and then — only if
  nothing matched exactly — by title, and by a single close match above a threshold, which it
  announces. **Two matches is a refusal at every rung**, never a guess.
- **The one thing this cost was a chronological `ls`.** The date prefix made any folder listing
  answer *how long has this sat here?* with no tool, precisely because no file listing reads
  frontmatter. That was worth its keep while a spec was always a file, and it is what the move
  gives up. What replaces it is `specs.py next --front`, which sorts on the declared `date` and
  works in a store with no folder at all — and the trade is not optional, because the alternative
  was a store minting synthetic filenames to keep a property only one backend could ever have.

There is **no `phase:` frontmatter field**, because two declared sources of one fact diverge and a
folder cannot lie. Which folders exist, and the one hop a spec makes between them, are
[plan-lifecycle.md](plan-lifecycle.md) §One active folder.

## Frontmatter carries only what a human reads

`slug`, `title` and `date` are required; every other key is either **optional by design** or a
**record of a human judgment no derivation can reproduce**, and the admission test plus the full
list live in [plan-lifecycle.md](plan-lifecycle.md) §Frontmatter records human judgments. The one
exclusion is this file's: there is **no attempt counter**, because machine state a human never
reads does not belong in a spec.

**`date` is here because nothing else holds it honestly.** It was the filename's `YYYY-MM-DD-`
prefix, which made a plain `ls` chronological and cost nothing — while every spec was a file. A
store without filenames has to mint a synthetic one to carry it, and the native value that looks
like a replacement is not the same fact: an issue's `created_at` is when the ISSUE was made, and a
migration makes them all in one afternoon. So the basename is now the bare slug and the date is
declared. That is not duplicated truth; it is the only copy.

**`verification` is OPTIONAL, and absent means the default** (`per-section`), applied on read by
`_policy`. It is never stamped into a document to make it explicit: writing the default would
record a decision nobody made. It stopped being required because it answers how long *this repo's*
suite takes — a judgment a one-sentence capture has nobody to make yet — and requiring it forced
`new` to invent a value at the one moment there is no opinion to record. The post-capture writer is
`specs.py verification <slug> [<policy>]`; before it existed the policy was decidable exactly once,
at capture, and under an external backend it could not be changed at all.

**The slug is kebab in the repo's declared language**, not in English. The language is declared
once, in the harness contract ([communication.md](../agents/communication.md)), and never again in
a config key of this front's own. `slugify` normalises to NFD and drops the combining marks before
reducing, so `criação` becomes `criacao` — the slug stays typeable without becoming a language
nobody wrote. Without that fold, `[^a-z0-9]+` treats an accent as a separator and the identity key
comes out `cria-o`.

`slug` is the deliberate exception to the no-duplicate-truth rule: it is the identity key, so a
mirror inside the file is worth its keep, and `validate` compares it to the basename. A merely
derived fact earns no such mirror.

## Fourteen canonical sections

| # | Heading | Moment |
| --- | --- | --- |
| 1 | `## Overview` | `decision` |
| 2 | `## Problem` | `decision` |
| 3 | `## Proposal` | `build` |
| 4 | `## Out of Scope` | `build` |
| 5 | `## Impact` | `build` |
| 6 | `## Validation` | `close` |
| 7 | `## Design` | `build` |
| 8 | `## Alternatives Considered` | `decision` |
| 9 | `## Open Decisions` | `decision` |
| 10 | `## Risks` | `decision` |
| 11 | `## Handoff` | `build` |
| 12 | `## Tasks` | `build` |
| 13 | `## Discoveries` | — (no moment; see below) |
| 14 | `## Outcome` | `close` |

**Headings are a parsed contract** — canonical English, exactly as written. A heading outside the
set is a stray and `validate` flags it. Which language a spec's body is written in belongs to
[../agents/communication.md](../agents/communication.md), not here.

**Moment replaces an unread `audience` field.** Each canonical section is born `moment: decision |
build | close` in `assets/specs/schema.json` — the point on the spec's timeline it is read at, not
who reads it. `/quenching:specs:execute` step 4 (`specs.py section <slug> --moment build`) sends an
executor exactly the `build` set; `decision` stays with the human weighing whether to build at all,
and `close` is `/quenching:specs:conclude`'s. `## Discoveries` carries no `moment` — captured
indiscriminately while building, it is resolved later by `/quenching:specs:develop`'s triage sweep on its own
schedule, tied to none of the three.

Two are load-bearing for machinery, not only for thinking:

- **`## Validation`** is the fallback for a task with no `verify:` line.
- **`## Impact`** is the one machine-parsed declaration (below). Removing the heading disables a
  check without a line of code changing.

`## Overview` is warn-only, like `## Handoff` — never one of the ten sections the `ready` gate
requires. It sits first, ahead of `## Problem`, but is authored **last**: `/specs:develop` writes
it once every other section has settled, because connecting them is only possible after they exist.

## The explicit-none rule is PHASE-SCOPED

A heading is required — and required to carry `- none — <reason>` when it has nothing in it — only
once **its own gate** is reached. Two of the four gates move a file; two are computed.

| Gate | Kind | Required sections |
| --- | --- | --- |
| `new` (capture) | entry to `plans/` | `## Problem` |
| the `ready` stage | derived, refuses nothing | the nine definition sections (`## Problem` … `## Risks`) **and `## Tasks`** |
| the `ready` stage (warning only) | derived | `## Overview` non-empty, `## Handoff` non-empty |
| `promote → archive/` | entry to `archive/` | `## Outcome` |

Three rules decide whether a section counts as filled:

1. **`- none — <reason>` counts as filled.** An omission and a null are different facts. *We drew
   the boundary and nothing fell outside it* and *nobody ever drew the boundary* read identically
   when the heading is missing, and only one is safe to build on.
2. **A present-but-empty heading is malformed and refuses.** It is neither an answer nor a not-yet.
3. **An absent heading before its gate is legal** — a *not-yet*, not an omission.

**Why scoped and not absolute.** Applied absolutely the rule would kill the derived stage: since an
explicit none counts as filled, a freshly captured spec carrying fourteen `- none` sections would
derive as `designed` and pass every gate without anyone having thought anything. Scoping is the
version where both rules survive, and it is why capture stamps `## Problem` alone.

The gate sets live in `assets/specs/schema.json` — `phases[].entryGate` for the two that move a
file, `stages.derived[].when.filled` for the `ready` stage — and are read by **both** `promote` and
`validate`. One source, two consumers. A wrong mapping there fails silently in one of two
directions: too strict blocks every promote, too loose lets an empty spec through every gate.

## `## Tasks` is in the ready set on purpose

Nothing reads as ready to build with nothing to execute. This is the surviving form of the
guarantee v1 spelled `applyRequires: ["tasks"]`: under v3 the ten sections are computed rather than
enforced by a `git mv`, so `## Tasks` is what keeps the derived `ready` stage from being a
statement about prose alone.

## What `promote` still refuses

`promote` refuses with **exit 2 and the missing list** rather than warning. A gate that warns is
not a gate. Its one hop stamps `outcome: done | abandoned` — the only content a promote ever
writes — and **refuses while `- [ ]` boxes remain when the outcome is `done`** (overridable with
`--force`); `abandoned` is always allowed, because open tasks are exactly what closing out unbuilt
work looks like.

The authorization to build is **not** a promote: it is the `approved` record, per
[plan-lifecycle.md](plan-lifecycle.md) §`ready` is derived, and `approved` is a human's word.

## `## Impact` carries one parsed sub-heading

```markdown
### Standards this spec will write into docs/standards/

- `docs/standards/auth/session-tokens.md` — how a session token is minted and revoked
```

`parse_impact_standards()` reads the `docs/standards/**.md` paths bulleted under **that heading and
only that heading**, and `validate` emits `sp-impact-uncovered` (warn) for any path no `## Tasks`
item names.

Two exclusions are deliberate: the sibling sub-headings are **not** parsed (they name paths the
spec never promised to write), and an unfilled `<placeholder>` declares nothing. A spec with no such
sub-heading declares nothing and is never flagged — **the check is opt-in by writing the heading**.

A bullet may carry a `§`address beside its path —
`docs/standards/automation/context-budget.md §The two caps` — naming exactly which sections of that
standard the task must honor. `parse_impact_standards()` already tolerates it: the regex matches
only the `docs/standards/**.md` path and ignores the rest of the line, addressed or not, so no code
changed to accept it. Without an address, `/quenching:specs:execute` step 4 reads the file whole,
exactly as before — the address is an assertion the spec's own author makes, never an economy the
executor infers on its own.

## Stages are derived, never declared

The stage list and its resolution order are [plan-lifecycle.md](plan-lifecycle.md) §`ready` is
derived. What belongs here is *why* the computation is safe to hang gates on: derived state
regresses automatically when a section empties, while declared state is forgotten on edit and lies.
The computation reads **heading presence**, never a three-state body — which is exactly what the
phase-scoped rule above keeps unambiguous.

## A blocked task is visible, not counted

```markdown
- [!] 2.3 Implement the gate check — blocked: waiting on the vendor SDK
```

Written by the orchestrator when attempts stop converging; `next` skips it. `--block` **requires**
`--reason`. There is no attempt budget: v1 kept a counter in `.specs.json` and stopped at five,
which meant a task went quiet with no trace of *why* and resumed only via a `--reset-attempts`
incantation that bought five more attempts at the same wrong approach.

## Refinement is recorded, surfaced, and never gating

`refined: {mode, date}` in frontmatter, written after a real pass with real answers.
`validate` emits `sp-unrefined` (warn) for a spec that reaches the **`ready` stage** and carries no
such record — judged against that set of ten sections, not capture, so a freshly parked idea is not
nagged.

It is a warning by construction: gating on refinement would contradict the front's own rule that a
sweep never blocks on a judgment call. **A spec may always be built unrefined.**

## The template is duplicated on purpose

`assets/specs/templates/spec.md` is the source, and the identical content is embedded in `specs.py`
as a constant, so the tool stays one self-contained file. **Edit both or neither.**

### There is a THIRD copy, and it shadows rather than falls back

`assets/specs/schema.json` holds the same record vocabulary as `specs.py`'s `DEFAULT_SCHEMA`, and
`load_schema()` prefers the file when it is adjacent. So the constant is **not** the authority when
the assets are present — the JSON silently wins, and a change made only to the constant is invisible
in exactly the layout the plugin ships. `load_template()` resolves the same way, and since the tool
now only ever runs from the plugin, where both assets *are* adjacent, **neither constant is what
executes**. They survive as what `selftest` compares against and what keeps the file readable on its
own — which is precisely why a change made to one and not the other passes unnoticed at runtime.

Any change to the record vocabulary is therefore a **three-file lockstep edit**: `DEFAULT_SCHEMA` in
`specs.py`, `assets/specs/schema.json`, and the guidance in `assets/specs/templates/spec.md`. This
was found by a task that declared only the first under `files:` and produced a tool that reported
the old vocabulary from the new code.

The `audience` → `moment` rename is exactly this shape: `sections[].moment` in `DEFAULT_SCHEMA` and
`schema.json`, plus the per-section `MOMENT:` comment token in the template — three files, one
edit, or the constant reports a vocabulary the JSON and the template have already left behind.

The template holds all fourteen headings with their guidance; `new` stamps only the **capture
form** (everything up to the second `## ` heading), and `section --write` pulls one heading's
guidance when creating it. One source, two slices.

Scaffold content must stay invisible to `has_real_content()`: only headings and HTML comments, with
any example inside a comment or written as a `<placeholder>`. A literal alphanumeric line in the
template makes every fresh capture read as authored.

## Reading a v1 plan in `specs/archive/`

`specs/archive/**` is **deliberately not migrated** — it is historical and read-only, and churning
it would break every link into it for no gain. So archived work predating v2 still has the old
shape, and a reader needs its contract:

- A v1 plan is a **folder**, `YYYY-MM-DD-<name>/`, not a file.
- It holds `proposal.md` (`## Why`, `## What Changes`, `## Out of Scope`, `## Validation`,
  `## Impact`), `design.md` (`## Context`, `## Decisions`, `## Alternatives Considered`,
  `## Open Decisions`, `## Risks`), and `tasks.md` (checkboxes under `## N.` headings).
- `.specs.json` carries the metadata v2 moved into frontmatter — `name`, `title`, `created`,
  `backlogTask`, `verification`, `refined` — plus per-task `attempts`, which v2 dropped entirely.
- The explicit-none rule applied **absolutely** there: every heading always existed, because v1 had
  no phase gates to scope it to.

The v2 equivalents map cleanly: `## Why`→`## Problem`, `## What Changes`→`## Proposal`,
`## Context`+`## Decisions`→`## Design`, `tasks.md`→`## Tasks`. `specs.py migrate` performs exactly
that fold for any v1 plan still **active**; it never touches the archive.
