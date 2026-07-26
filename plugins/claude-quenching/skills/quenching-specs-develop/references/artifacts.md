# Authoring the three plan artifacts

The per-artifact authoring doctrine `quenching-specs-develop` applies when it writes each
file. The **layout, the artifact graph, the formats, and the `specs.py` surface** live once in
[spec-driven.md](spec-driven.md) and are cited, never restated here — this file is only the
*writing* guidance: what belongs in each artifact, when `## Design` is warranted, and how to
shape `## Tasks` (including the items that write standards into `docs/`).

There is **no delta spec and no sync**. A plan proves its durable rules straight into
`docs/standards/` while it is built (`quenching-specs-apply`); the proposal *declares* that
scope. Two things in these files are machine contracts — the `## Tasks` checkboxes and the one
parsed sub-heading of `## Impact` — and everything else is prose for a human reviewer.

## Contents

- [The explicit-none rule](#the-explicit-none-rule)
- [`## Problem`/`## Proposal` — required, no dependencies](#proposalmd--required-no-dependencies)
- [`## Design` — required-with-explicit-fallback, depends on `proposal`](#designmd--required-with-explicit-fallback-depends-on-proposal)
- [`## Tasks` — required, depends on `proposal`](#tasksmd--required-depends-on-proposal)

## The explicit-none rule

Every section of `## Problem`/`## Proposal` and `## Design` is **required-with-explicit-fallback**: the heading
always exists, and a section with nothing in it is answered `- none` (in `## Design`, `- none —
<reason>`). Never delete the heading, and never pad it with restated text from another section.

An omission and a null are different facts. "We drew the boundary and nothing fell outside it" and
"nobody ever drew the boundary" read identically when the section is missing, and only one of them
is safe to build on. An explicit null is strictly more information than an absent heading, and it
costs one line.

`specs.py new <name>` stamps each file from `assets/specs/templates/{proposal,design,tasks}.md`.
Fill the template's sections — do not invent new top-level headings, and never paste this
doctrine into the artifact.

## `## Problem`/`## Proposal` — required, no dependencies

Five sections; keep it tight enough to read in one sitting.

- **`## Why`** — the problem or opportunity, in the repo's own terms (use
  `docs/knowledge/glossary.md` vocabulary). One or two paragraphs. If a `specs/backlog/` task
  seeded the plan, its gist is the germ of this section — sharpen it, do not just paste it.
- **`## What Changes`** — the change in behavior or capability, as a short bulleted list of
  outcomes (WHAT, not HOW — the how is `## Design`/the code). Each bullet is something a
  reviewer could later check was delivered.
- **`## Out of Scope`** — what the plan deliberately does NOT do, and why each was ruled out.
  This is where a rejected adjacent idea goes so it stops being re-proposed, and where a
  deferred piece is recorded as deferred rather than forgotten. `- none` when nothing was
  excluded.
- **`## Validation`** — how anyone confirms the plan worked: the commands and the output they
  must produce, the fixtures, the invariants that must still hold. `- none` is a claim that the
  plan is unverifiable by construction — make it deliberately or fill the section in.
- **`## Impact`** — declared scope for human review, and the plan's **one parsed contract**.

### `## Impact` — the parsed sub-heading

`## Impact` carries three sub-headings, and exactly one of them is machine-checked:

```markdown
### Standards this plan will write into docs/standards/

- `docs/standards/auth/session-tokens.md` — how a session token is minted and revoked

### Standards at `authority: background` this plan may resolve

- `docs/standards/auth/rotation.md` — proves out, promote to `current` if it holds

### Product code this plan expects to touch

- `src/auth/session.ts` — the mint/revoke path
```

`specs.py validate` parses **only the first sub-heading** (`parse_impact_standards`) and emits
`sp-impact-uncovered` (warn) for any `docs/standards/**.md` path bulleted there that no `## Tasks`
item names. Keep the heading text verbatim — it is the anchor; a `**Standards this plan will write
into ...**` bold line is accepted too, for plans written before this format.

The other two sub-headings are deliberately **not** parsed: they name paths the plan does not
promise to write, and checking them would flag a plan for not delivering a doc it never claimed.
A proposal with no such sub-heading declares nothing and is never flagged — the check is opt-in by
writing the heading. An unfilled `<placeholder>` declares nothing either.

## `## Design` — required-with-explicit-fallback, depends on `proposal`

**The file always exists.** Do not delete it to signal "no design was needed": an absent
`## Design` cannot distinguish *we weighed the alternatives and there were none* from *nobody ever
thought about it*, and those are opposite facts. Answer an empty section `- none — <reason>`.

`## Design` is required as a **section set**, never as a **dependency** — `applyRequires` stays
`["tasks"]`, so a bare scaffold does not block apply. It is reported instead: `specs.py validate`
emits `sp-design-scaffold` (warn) for a file that is still the shipped scaffold, and `specs.py
next` names it as the artifact to write while `## Tasks` is still unwritten.

Five sections:

- **`## Context`** — the constraints in play: relevant `docs/standards/` contracts (the design
  must not contradict them), existing code shape, external limits.
- **`## Decisions`** — each decision with the alternatives weighed and why this one. This is the
  material that later distills into a `docs/standards/` or `docs/knowledge/` doc, so state it as
  a durable rule, not a diary entry.
- **`## Alternatives Considered`** — whole-shape alternatives rejected at the plan level, each
  with the reason it lost. Per-decision alternatives stay inside `## Decisions`; this section is
  for the ones that would have changed the plan's shape.
- **`## Open Decisions`** — what is deliberately still undecided, and **how each gets decided** —
  the evidence or the moment that settles it, never a bare "TBD". A task may be written to close
  one (`- [ ] 6.5 Decide per ## Design §Open Decisions whether …`).
- **`## Risks`** — what could go wrong and the mitigation for each.

## `## Tasks` — required, depends on `proposal`

The implementation checklist `specs.py` parses. Format (owned by
[spec-driven.md](spec-driven.md) §Artifact formats): checkboxes `- [ ] <id> <text>` grouped
under `## N. <Section>` headings. `specs.py task --spec <slug> --check <id>` flips a box
mechanically — never hand-edit the checkbox character.

Shape it so `quenching-specs-apply` can walk it top to bottom:

- **Ordered by dependency**, grouped into coherent sections (setup → core → wiring → tests →
  docs). Each item is one reviewable unit of work — small enough to check off honestly, large
  enough not to be noise.
- **The standards-writing items are explicit tasks, not an afterthought.** Every
  `docs/standards/` path declared under `## Impact`'s parsed sub-heading gets its own checkbox —
  e.g. `- [ ] 4.1 Write docs/standards/auth/session-tokens.md (authority: current once proved)`.
  Applying the plan *is* proving the rule, so writing the standard is part of the work, honestly
  `authority`-graded when it lands ([spec-driven.md](spec-driven.md) §Boundary). This is the
  pairing `sp-impact-uncovered` checks: name the path in the task text so the match is findable.
- **Verification belongs in the list** — a task whose completion is "tests pass" / "the standard
  is written and self-checks clean" is a task, not an implicit hope.

Do not put `docs/knowledge/` captures or glossary terms in `## Tasks` as durable content — those
route through `quenching-docs-learn`/`quenching-docs-define` at apply time; a task may *name* the
capture ("- [ ] 5.2 Capture the retry-budget gotcha via /docs:learn") but the knowledge itself
lives in its OKF home, never in the checklist.

### Execution metadata — optional, indented, additive

A checkbox MAY carry indented metadata lines directly beneath it. `specs.py` parses them and
`quenching-specs-apply` consumes them; `CHECKBOX_RE` is untouched, so every `## Tasks`
written before this format parses identically and simply reports empty metadata.

```markdown
- [ ] 3.2 Add rate limiting to the auth middleware
      files: src/middleware/auth.ts, src/config/limits.ts (new)
      pattern: src/middleware/cors.ts
      verify: pnpm test middleware/
```

| Key | What it carries | Why apply wants it |
| --- | --- | --- |
| `files:` | comma-separated paths this task may touch | bounds the work; **declaring it is what permits the task to be handed to an executor sub-agent**, and it is what makes a `[P]` marker checkable |
| `pattern:` | an existing file to imitate | the cheapest context an executor can be given — one path beats three paragraphs of description |
| `verify:` | the command that proves the task done | apply runs it under the plan's `verification` policy; a task with no `verify:` falls back to the proposal's `## Validation` |

Write them where they earn their place — a task touching three known files with an obvious test
command deserves all three; a one-line doc edit deserves none. Metadata that restates the task
text is noise.

**`[P]` marks a task parallel-eligible**, written right after the id:

```markdown
- [ ] 3.3 [P] Add the rate-limit config loader
      files: src/config/limits.ts
```

Set it **here, at propose time** — apply never infers it. It is honoured only when the marked
tasks' `files:` sets are provably disjoint and none writes into `docs/`, which `specs.py parallel`
checks mechanically. Serial is the default and needs no marker: without proven disjunction,
parallel execution trades wall-clock for merge conflicts and loses on both.

### The verification policy is the plan's, not the task's

`per-task` / `per-section` (default) / `end-of-plan`, recorded in the spec's frontmatter by
`specs.py new --verification` at propose time. It answers *when* the checks run; `verify:` answers
*what* runs. Deciding it here is what keeps `quenching-specs-apply` from having to guess, or
from stopping mid-implementation to ask.
