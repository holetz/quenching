---
type: standard
title: Spec file contract
description: The one-file spec, its thirteen canonical sections, the phase-scoped explicit-none rule, the parsed Impact sub-heading, the duplicated template, and how to read a v1 plan in specs/archive/
resource: plugins/quenching/assets/specs/templates/spec.md, plugins/quenching/assets/specs/schema.json, plugins/quenching/assets/bin/specs.py, plugins/quenching/commands/specs/**
tags: [workflows, specs, sections, gates, validation]
timestamp: 2026-07-27
audience: both
authority: current
source: specs-front-v2 plan (sections 1-2); lifecycle claims superseded by the specs-flow-consolidation plan
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
It is named `YYYY-MM-DD-<slug>.md` **in every folder**, and the date is stamped once, at capture,
and never rewritten — a promote moves the file without renaming it.

Two consequences are load-bearing:

- **A plain `ls` is the status view.** Any folder listing is chronological, which answers *how long
  has this sat here?* without a tool. No file listing reads frontmatter, which is why the date is
  in the name and not in a field.
- **Identity is the slug, not the path.** Every cross-reference names the bare slug; the tool
  resolves it to the one file ending in `-<slug>.md`, wherever it sits. **Two matches is a refusal,
  never a guess.**

There is **no `phase:` frontmatter field**, because two declared sources of one fact diverge and a
folder cannot lie. Which folders exist, and the one hop a spec makes between them, are
[plan-lifecycle.md](plan-lifecycle.md) §One active folder.

## Frontmatter carries only what a human reads

`slug`, `title` and `verification` are required; every other key is a **record of a human judgment
no derivation can reproduce**, and the admission test plus the full list live in
[plan-lifecycle.md](plan-lifecycle.md) §Frontmatter records human judgments. The two exclusions are
this file's: there is **no `created`** — the filename's date prefix is that fact — and **no attempt
counter**, because machine state a human never reads does not belong in a spec.

`slug` is the deliberate exception to the no-duplicate-truth rule: it is the identity key, so a
mirror inside the file is worth its keep, and `validate` compares it to the filename. A merely
derived fact earns no such mirror.

## Thirteen canonical sections

`## Problem`, `## Proposal`, `## Out of Scope`, `## Impact`, `## Validation`, `## Design`,
`## Alternatives Considered`, `## Open Decisions`, `## Risks`, `## Handoff`, `## Tasks`,
`## Discoveries`, `## Outcome`.

**Headings are a parsed contract** — canonical English, exactly as written; body prose follows the
repo's language. A heading outside the set is a stray and `validate` flags it.

Two are load-bearing for machinery, not only for thinking:

- **`## Validation`** is the fallback for a task with no `verify:` line.
- **`## Impact`** is the one machine-parsed declaration (below). Removing the heading disables a
  check without a line of code changing.

## The explicit-none rule is PHASE-SCOPED

A heading is required — and required to carry `- none — <reason>` when it has nothing in it — only
once **its own gate** is reached. Two of the four gates move a file; two are computed.

| Gate | Kind | Required sections |
| --- | --- | --- |
| `new` (capture) | entry to `plans/` | `## Problem` |
| the `ready` stage | derived, refuses nothing | the nine definition sections (`## Problem` … `## Risks`) **and `## Tasks`** |
| the `ready` stage (warning only) | derived | `## Handoff` non-empty |
| `promote → archive/` | entry to `archive/` | `## Outcome` |

Three rules decide whether a section counts as filled:

1. **`- none — <reason>` counts as filled.** An omission and a null are different facts. *We drew
   the boundary and nothing fell outside it* and *nobody ever drew the boundary* read identically
   when the heading is missing, and only one is safe to build on.
2. **A present-but-empty heading is malformed and refuses.** It is neither an answer nor a not-yet.
3. **An absent heading before its gate is legal** — a *not-yet*, not an omission.

**Why scoped and not absolute.** Applied absolutely the rule would kill the derived stage: since an
explicit none counts as filled, a freshly captured spec carrying thirteen `- none` sections would
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
as a fallback constant — because an installed copy under a target's `.claude/hooks/` has no adjacent
assets and must still stamp the same file. **Edit both or neither.**

The template holds all thirteen headings with their guidance; `new` stamps only the **capture
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
