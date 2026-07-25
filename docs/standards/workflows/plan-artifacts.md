---
type: standard
title: Plan artifact contract
description: The required sections of a plan's artifacts, the parsed Impact declaration, the refinement record, and what applyReady does and does not guarantee
resource: plugins/claude-quenching/assets/specs/templates/*.md, plugins/claude-quenching/assets/bin/specs.py, plugins/claude-quenching/skills/quenching-specs-plan-*/
tags: [workflows, specs, plans, artifacts, validation]
timestamp: 2026-07-25
audience: both
authority: current
source: refine-and-execute-specs-flow plan (sections 1-3)
maintainer: claude-quenching
---

# Plan artifact contract

What a plan's three artifacts must contain before the plan is worth building, and which parts of
them a machine checks. The per-artifact *authoring* doctrine (what to write in each section) lives
in `quenching-specs-plan-propose/references/artifacts.md`; the layout and tool surface in
`.../references/spec-driven.md`. This standard is the **contract** those two implement.

## Every section is required-with-explicit-fallback

The heading always exists. A section with nothing in it is answered `- none` — in `design.md`,
`- none — <reason>`. It is never deleted, and never padded with text restated from another
section.

An omission and a null are different facts. *We drew the boundary and nothing fell outside it* and
*nobody ever drew the boundary* read identically when the section is missing, and only one of them
is safe to build on. An explicit null is strictly more information than an absent heading, and it
costs one line.

- `proposal.md` — `## Why`, `## What Changes`, `## Out of Scope`, `## Validation`, `## Impact`.
- `design.md` — `## Context`, `## Decisions`, `## Alternatives Considered`, `## Open Decisions`,
  `## Risks`.
- `tasks.md` — `- [ ] <id> <text>` checkboxes under `## N. <Section>` headings.

## `design.md` is required as a section set, never as a dependency

The file always exists; **do not delete it** to signal that no design was needed. But
`applyRequires` stays `["tasks"]`, and `design` must never be added to it: a required *section
set* and a required *dependency* are different things, and promoting one to the other would move
every plan authored before this rule from apply-ready to blocked on upgrade.

The rule is enforced by report, not by gate — `specs.py validate` emits `sp-design-scaffold`
(warn) for a file still on the shipped scaffold. An **absent** `design.md` is a legacy plan and is
never flagged.

## `## Impact` carries one parsed sub-heading

`## Impact` is declared scope for human review, with exactly one machine-checked part:

```markdown
### Standards this plan will write into docs/standards/

- `docs/standards/auth/session-tokens.md` — how a session token is minted and revoked
```

`specs.py`'s `parse_impact_standards()` reads the `docs/standards/**.md` paths bulleted under that
heading — and only that heading — and `validate` emits `sp-impact-uncovered` (warn) for any path
no `tasks.md` item names. A bold `**Standards this plan will write into ...**` line is accepted
for plans written before the format.

Two exclusions are deliberate:

- **The sibling sub-headings are not parsed.** A background standard the plan *may* resolve, and
  the product code it touches, name paths the plan never promised to write; checking them would
  flag a plan for not delivering a doc it never claimed.
- **An unfilled `<placeholder>` declares nothing**, so a freshly scaffolded plan is never flagged
  against the template's own example.

A proposal with no such sub-heading declares nothing and is never flagged. **The check is opt-in
by writing the heading** — which is what keeps it backward compatible with every existing plan.

## Refinement is recorded, surfaced, and never gating

`.specs.json` carries `refined: {mode, date}`, written by `quenching-specs-plan-refine` after a
real pass with real answers. `specs.py validate` emits `sp-unrefined` (warn) for a plan that has a
`tasks.md` and no such record.

It is a **warning by construction**. Gating `applyReady` on refinement would break every existing
plan in every installed repo on upgrade, and it would contradict the front's own rule that a sweep
never blocks on a judgment call. A warning surfaced in `/specs:status` gets the behavior without
the breakage.

## What `applyReady` does and does not guarantee

`applyReady` means `proposal.md` and `tasks.md` exist, carry real content, and yield at least one
parseable checkbox. **It is a floor, not a verdict.**

It does **not** guarantee that anyone disagreed with the plan, that `design.md` was filled, or
that the declared `## Impact` is covered. Those are `sp-unrefined`, `sp-design-scaffold`, and
`sp-impact-uncovered` — all warnings, none affecting `applyReady`, all surfaced by
`specs.py validate` and `/specs:status`. Each names a piece of **thinking** a plan skipped, and
thinking is not something a sweep can supply, so none of them is ever auto-repaired.

## The templates are duplicated on purpose

`assets/specs/templates/{proposal,design,tasks}.md` are the source, and the identical content is
embedded in `specs.py` as fallback constants — because an installed copy under a target's
`.claude/hooks/` has no adjacent assets and must still stamp the same files. **Edit both or
neither.**

A template's scaffold content must stay invisible to `has_real_content()`: only headings and HTML
comments, with any example inside a comment or written as a `<placeholder>`. A literal alphanumeric
line in a template makes every freshly scaffolded plan read as authored, which silently disables
`sp-empty-proposal` and the `next` walk that depends on it.
