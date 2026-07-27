---
description: Advance a spec's sections to the ready gate, then offer the promote
argument-hint: [slug-or-description]
allowed-tools: Bash(python3:*), Bash(py:*), Read, Glob, Grep, Write, Edit, AskUserQuestion
---

# /specs:develop — advance a spec to the ready gate

**Input**: `$ARGUMENTS` (a spec slug OR a description of what to develop).

Writes and revises the sections of ONE spec, from a bare `## Problem` through the whole definition
set, until `specs.py promote` will accept it.

**This is one skill because v2 made it one job.** v1 split it in two: `plan-propose` *created*
three artifact files from templates, and `plan-update` *revised* files that already existed and
reconciled them against each other. Neither difference survives a single file. Creating a section
and revising one are the same call — `specs.py section <slug> "<Heading>" --write`, which creates
the heading in canonical position on first write — and there is nothing to reconcile *between*
artifacts when there is one artifact.

What survived from each: the gate walk (fill toward the `ready/` set, then offer the promote), and
the absolute rule that this skill **never edits code**.

The spec-driven facts — layout, the thirteen canonical sections, the phase gates, the derived
stages, the `specs.py` surface, the `specs/`↔`docs/` boundary — live in
[specs-develop/spec-driven.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-develop/spec-driven.md). The per-section authoring doctrine (what
belongs under each heading, and how to write an honest explicit none) lives in
[specs-develop/artifacts.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-develop/artifacts.md). Both are cited here, never restated.

## Resolving the tool

Resolve `specs.py` by the fallback in
[specs-capture/backlog-zone.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-capture/backlog-zone.md)
§Resolving the tool. Branch on the **exit code** (0 ok · 1 findings · 2 refusal) and the `--json`,
never on prose.

**No deltas.** This front is entirely native: a spec writes its durable rules **directly** into
`docs/standards/` while it is built, isolated on a branch. There is no second store to bridge to,
so nothing here writes a delta and nothing later syncs one.

## Doctrine

- **The tool decides what is next, never a reading of the file.** `specs.py next --spec <slug>`
  returns THE next action — the first unfilled gate section, or `promote` once they are all
  filled. Walking the headings by eye is how a section gets skipped.
- **Every write is confirmed before it lands.** This skill authors content into a human's spec.
  Show what will be written, then write it — one section at a time.
- **An empty section is `- none — <reason>`, never a deleted heading.** *We drew the boundary and
  nothing fell outside it* and *nobody ever drew the boundary* read identically when the heading
  is missing, and only one of them is safe to build on. An explicit null is strictly more
  information than an absence, and it costs one line.
- **A heading that exists must say something.** A present-but-empty section is malformed — neither
  an answer nor a not-yet — and `promote` refuses on it. Never create a heading you are not about
  to fill in the same step.
- **Never invent the explicit none.** `- none — <reason>` is an *answer*. If the human has not
  given one, ask, or leave the heading absent and let the gate report it. A fabricated null is
  worse than a missing section, because it looks decided.
- **Read `docs/` before writing.** The relevant `docs/standards/` and `knowledge/glossary.md` shape
  the wording, so a spec does not contradict a rule the repo already agreed on, or invent a second
  name for a thing that already has one.
- **Never edit code.** If the work implies code changes, that is `/specs:apply`. If a
  request changes the spec's *intent* rather than sharpening it, say so and offer a fresh capture
  instead of quietly rewriting what was already agreed.
- **`## Impact` is the one parsed section.** Paths bulleted under
  `### Standards this spec will write into docs/standards/` are machine-checked against
  `## Tasks`; writing that heading opts the spec into the check.

## Workflow

### 1. Resolve the spec
Take the slug from the user, or run `specs.py list --json` and ask. Announce it, then read state:
```bash
specs.py status --spec <slug> --json
```
Two matches for a slug is exit 2 — report both paths and stop; never guess which was meant.
**Done when:** one spec is resolved and its section states are in hand.

### 2. Read the OKF bundle as context
If `docs/index.md` carries `okf_version`, read the `docs/standards/` subjects this spec touches
plus `docs/knowledge/glossary.md`. They are **binding** on wording and on any rule the spec
restates. No bundle → skip silently.
**Done when:** the relevant standards and vocabulary are in hand, or no bundle exists.

### 3. Set the verification policy, once
If the human has not declared one, ask which of `per-task` / `per-section` / `end-of-plan` this
spec verifies under, and write it to frontmatter. Declaring it here is what stops
`/specs:apply` from having to guess mid-build, or from asking at the worst moment.
**Done when:** `verification` is set, or was already.

### 4. Walk the gate
Loop, never batch:
```bash
specs.py next --spec <slug> --json              # -> the next unfilled gate section
specs.py section <slug> "<Heading>"             # read it first, when revising
specs.py section <slug> "<Heading>" --write     # body on stdin, AFTER confirmation
```
Draft each section per [specs-develop/artifacts.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-develop/artifacts.md), show it, confirm, write
it, then ask the tool again. Revising an already-filled section is the same call — read it, show
the change, write it.
**Done when:** `specs.py next` reports `action: promote`, or the human stops.

### 5. Offer the promote
When the gate is met, say so and offer it — this is the human OK, and it is theirs to give:
```bash
specs.py promote <slug>            # backlog/ -> ready/
```
A refusal (exit 2) lists exactly what is missing or malformed; fix and offer again. If
`specs.py validate --spec <slug>` reports `sp-unrefined`, mention `/specs:refine` **once**
— a spec may always be promoted unrefined, so this is an offer, never a gate.
**Done when:** the spec is promoted, or the human declines and the run ends cleanly.

## Invariants to never violate

- **NEVER edit implementation code.** If the spec implies code changes, stop and name
  `/specs:apply`.
- Never write a section without showing it and getting the human's word first.
- Never delete a heading to signal that nothing applies — write `- none — <reason>`.
- Never invent an explicit none the human did not give.
- Never create a heading you are not filling in the same step.
- Never choose the next section by reading the file — ask `specs.py next`.
- Never promote on the human's behalf; the promote IS their confirmation.
- Never write into `docs/` from here. A durable rule the spec surfaces routes to
  `/docs:add` / `/docs:learn`; the rules a spec *proves* are written during
  apply, not during definition.
- Never rename a spec or change its date prefix.
