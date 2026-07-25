# Authoring the three plan artifacts

The per-artifact authoring doctrine `quenching-specs-plan-propose` applies when it writes each
file. The **layout, the artifact graph, the formats, and the `specs.py` surface** live once in
[spec-driven.md](spec-driven.md) and are cited, never restated here — this file is only the
*writing* guidance: what belongs in each artifact, when `design.md` is warranted, and how to
shape `tasks.md` (including the items that write standards into `docs/`).

There is **no delta spec and no sync**. A plan proves its durable rules straight into
`docs/standards/` while it is built (`quenching-specs-plan-apply`); the proposal only *declares*
that scope in prose. Nothing in these three files is a machine contract except the `tasks.md`
checkboxes `specs.py` parses.

`specs.py new <name>` stamps each file from `assets/specs/templates/{proposal,design,tasks}.md`.
Fill the template's sections — do not invent new top-level headings, and never paste this
doctrine into the artifact.

## `proposal.md` — required, no dependencies

Three sections; keep it tight enough to read in one sitting.

- **`## Why`** — the problem or opportunity, in the repo's own terms (use
  `docs/knowledge/glossary.md` vocabulary). One or two paragraphs. If a `specs/backlog/` task
  seeded the plan, its gist is the germ of this section — sharpen it, do not just paste it.
- **`## What Changes`** — the change in behavior or capability, as a short bulleted list of
  outcomes (WHAT, not HOW — the how is `design.md`/the code). Each bullet is something a
  reviewer could later check was delivered.
- **`## Impact`** — **declared scope for human review, prose not a machine contract.** List:
  - the `docs/standards/<subject>/<concept>.md` paths the plan will **create or alter** (the
    durable rules it will write — every one of these also becomes a `tasks.md` item, see below);
  - the product code / areas it expects to touch;
  - any standard at `authority: background` it intends to prove out (promote to `current`).
  Nothing parses `## Impact`; it exists so a human can see the blast radius before apply.

## `design.md` — OPTIONAL, depends on `proposal`

Absent is a valid, common state. Write one **only when there is a real decision to record** —
a non-obvious architecture, a trade-off between alternatives, a risk that shapes the tasks. A
plan that just applies an already-agreed standard needs none: **delete the scaffolded
`design.md`** rather than fill it with restated proposal text (an empty or paraphrase-only
design is worse than none — it invites drift).

When warranted, three sections:

- **`## Context`** — the constraints in play: relevant `docs/standards/` contracts (the design
  must not contradict them), existing code shape, external limits.
- **`## Decisions`** — each decision with the alternatives weighed and why this one. This is the
  material that later distills into a `docs/standards/` or `docs/knowledge/` doc, so state it as
  a durable rule, not a diary entry.
- **`## Risks`** — what could go wrong and the mitigation or open question.

## `tasks.md` — required, depends on `proposal`

The implementation checklist `specs.py` parses. Format (owned by
[spec-driven.md](spec-driven.md) §Artifact formats): checkboxes `- [ ] <id> <text>` grouped
under `## N. <Section>` headings. `specs.py task --plan <n> --check <id>` flips a box
mechanically — never hand-edit the checkbox character.

Shape it so `quenching-specs-plan-apply` can walk it top to bottom:

- **Ordered by dependency**, grouped into coherent sections (setup → core → wiring → tests →
  docs). Each item is one reviewable unit of work — small enough to check off honestly, large
  enough not to be noise.
- **The standards-writing items are explicit tasks, not an afterthought.** Every
  `docs/standards/` path named in `## Impact` gets its own checkbox — e.g.
  `- [ ] 4.1 Write docs/standards/auth/session-tokens.md (authority: current once proved)`.
  Applying the plan *is* proving the rule, so writing the standard is part of the work, honestly
  `authority`-graded when it lands ([spec-driven.md](spec-driven.md) §Boundary).
- **Verification belongs in the list** — a task whose completion is "tests pass" / "the standard
  is written and self-checks clean" is a task, not an implicit hope.

Do not put `docs/knowledge/` captures or glossary terms in `tasks.md` as durable content — those
route through `quenching-docs-learn`/`quenching-docs-define` at apply time; a task may *name* the
capture ("- [ ] 5.2 Capture the retry-budget gotcha via /docs:learn") but the knowledge itself
lives in its OKF home, never in the checklist.
