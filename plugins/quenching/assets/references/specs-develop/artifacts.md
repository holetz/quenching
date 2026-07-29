# Authoring a spec's sections

The per-section authoring doctrine every `/specs:*` command applies when it writes into a spec. The
**layout, the fourteen sections, the gates, the derived stages and the `specs.py` surface** live
once in
[spec-driven.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-develop/spec-driven.md) and are
cited, never restated here — this file is only the *writing* guidance: what belongs under each
heading, how to write an honest explicit none, and how to shape `## Tasks`.

There is **no delta and no sync**. A spec proves its durable rules straight into `docs/standards/`
while it is built (`/specs:execute`), and `## Impact` is where it *declares* that scope. Two things
in a spec are machine contracts — the `## Tasks` checkboxes and the one parsed sub-heading of
`## Impact` — and everything else is prose for a human reviewer.

## Contents

- [The explicit-none rule](#the-explicit-none-rule)
- [`## Overview` — connective tissue, not a summary](#-overview--connective-tissue-not-a-summary)
- [The nine definition sections](#the-nine-definition-sections)
- [`## Impact` — the parsed sub-heading](#-impact--the-parsed-sub-heading)
- [`## Handoff` — small, and refreshed on events](#-handoff--small-and-refreshed-on-events)
- [`## Tasks`](#-tasks)
- [Execution metadata — optional, indented, additive](#execution-metadata--optional-indented-additive)
- [`## Discoveries` and `## Outcome`](#-discoveries-and--outcome)

## The explicit-none rule

A section with nothing in it is answered `- none — <reason>`. Never delete the heading, and never
pad it with restated text from another section.

An omission and a null are different facts. "We drew the boundary and nothing fell outside it" and
"nobody ever drew the boundary" read identically when the section is missing, and only one of them
is safe to build on. An explicit null is strictly more information than an absent heading, and it
costs one line.

Three rules follow, and the scoping is what keeps them from contradicting the derived stage:

1. **`- none — <reason>` counts as filled.**
2. **A present-but-empty heading is malformed.** It is neither an answer nor a not-yet.
3. **An absent heading before its own gate is legal** — a *not-yet*, not an omission.

**Never invent the explicit none.** `- none — <reason>` is an *answer*; writing one the human never
gave is worse than leaving the heading absent, because it looks decided. And never write fourteen
of them at creation: a spec that did would derive as `designed` and clear the whole ready gate
without anyone having thought anything.

`specs.py new <slug>` stamps the frontmatter and `## Problem` alone, from
`assets/specs/templates/spec.md`. Every other heading is created on first write by
`specs.py section <slug> "<Heading>" --write`, in canonical position. Do not invent new top-level
headings — one outside the canonical fourteen is a stray and `validate` flags it — and never paste
this doctrine into the spec.

## `## Overview` — connective tissue, not a summary

Position 1, ahead of `## Problem`. Warn-only, like `## Handoff` — never part of the `ready` gate
(spec-driven.md §The fourteen sections).

**Register.** Plain language, assuming no prior context. No jargon the spec itself introduces — a
reader who has not yet read `## Design` should not need a term `## Design` coins. Connective, not
compressive: link the sections to each other so the dense material that follows has somewhere to
attach, rather than restating what each one already says. A summary compresses each section; an
Overview orients the reader among them.

**Written last.** The shape bank is where it is first written, the same way that bank first writes
`## Proposal`; every later bank's consolidated edit refreshes it — always authored last within that
edit, because it can only be correct once the sections it connects have settled. It still sits
first in the file: only the authoring order within a pass is last, never its position.

## The nine definition sections

`## Problem` … `## Risks`, all gated on `ready`. Keep the set tight enough to read in one sitting.

- **`## Problem`** — the problem or opportunity and **why now**, in the repo's own terms (use
  `docs/knowledge/glossary.md` vocabulary). One or two paragraphs. This is the only section a
  freshly created spec carries.
- **`## Proposal`** — the change as a short bulleted list of outcomes: WHAT will be true afterwards
  that is not true now, never HOW. Each bullet is something a reviewer could later check was
  delivered.
- **`## Out of Scope`** — what the spec deliberately does NOT do, and why each was ruled out. This
  is where a rejected adjacent idea goes so it stops being re-proposed, and where a deferred piece
  is recorded as deferred rather than forgotten.
- **`## Impact`** — declared scope for human review, and the spec's **one parsed contract** (below).
- **`## Validation`** — how anyone confirms the spec worked: the commands and the output they must
  produce, the fixtures, the invariants that must still hold. **Load-bearing**: a `## Tasks` item
  with no `verify:` line falls back to it. `- none — <reason>` here is a claim that the spec is
  unverifiable by construction — make it deliberately or fill the section in.
- **`## Design`** — each decision with the alternatives weighed and why this one, plus the binding
  contracts the design must not contradict (the relevant `docs/standards/`, the existing code
  shape, external limits). State a decision as a **durable rule**, not a diary entry: this is the
  material `/specs:conclude` later distils.
- **`## Alternatives Considered`** — whole-shape alternatives rejected at the spec level, each with
  the reason it lost. Per-decision alternatives stay inside `## Design`; this section is for the
  ones that would have changed the spec's shape. **The rejected ones and why they lost are the
  point** — the next person with the same idea reads why it was already turned down.
- **`## Open Decisions`** — what is deliberately still undecided, and **how each gets decided** —
  the evidence or the moment that settles it, never a bare "TBD". A task may be written to close
  one (`- [ ] 6.5 Decide per ## Open Decisions whether …`).
- **`## Risks`** — what could go wrong and the mitigation for each. A risk taken knowingly is
  written `ACCEPTED — <why>`; a silent failure mode is the shape to hunt for.

## `## Impact` — the parsed sub-heading

Three sub-headings, and exactly one is machine-checked:

```markdown
### Standards this spec will write into docs/standards/

- `docs/standards/auth/session-tokens.md` — how a session token is minted and revoked

### Standards at `authority: background` this spec may resolve

- `docs/standards/auth/rotation.md` — proves out, promote to `current` if it holds

### Product code this spec expects to touch

- `src/auth/session.ts` — the mint/revoke path
```

`specs.py validate` parses **only the first sub-heading** (`parse_impact_standards`) and emits
`sp-impact-uncovered` (warn) for any `docs/standards/**.md` path bulleted there that no `## Tasks`
item names. Keep the heading text verbatim — it is the anchor.

The other two are deliberately **not** parsed: they name paths the spec does not promise to write,
and checking them would flag a spec for not delivering a doc it never claimed. A spec with no such
sub-heading declares nothing and is never flagged — **the check is opt-in by writing the heading**.
An unfilled `<placeholder>` declares nothing either.

This sub-heading is also the **declared/emergent line**: a `docs/standards/` doc named here *and*
by a task is written during execution; anything the work merely reveals is one `specs.py discover`
line and is written at conclude
([execution.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-execute/execution.md) §Declared
versus emergent `docs/`).

## `## Handoff` — small, and refreshed on events

The context an executor needs and cannot derive: the state of play, the conventions in force, what
was already tried. **Small by construction** — it is sent with every task, and it does not carry
the human sections.

It is warned on (not gated) once the ready gate is met, and it is rewritten after **each committed
task** rather than when someone judges it stale. Staleness is this section's only failure mode, and
an event-bound rule is the one cure that survives an unattended run.

## `## Tasks`

The implementation checklist `specs.py` parses: checkboxes `- [ ] <id> <text>` grouped under
`### N. <Section>` headings. `specs.py task --spec <slug> --check <id>` flips a box mechanically —
never hand-edit the checkbox character.

Shape it so `/specs:execute` can walk it top to bottom:

- **Ordered by dependency**, grouped into coherent sections (setup → core → wiring → tests → docs).
  Each item is one reviewable unit of work — small enough to check off honestly, large enough not
  to be noise. Each is also **one commit**, so a section is what a `verification: per-section` spec
  verifies after.
- **The standards-writing items are explicit tasks, not an afterthought.** Every `docs/standards/`
  path declared under `## Impact`'s parsed sub-heading gets its own checkbox — e.g.
  `- [ ] 4.1 Write docs/standards/auth/session-tokens.md (authority: current once proved)`.
  Building the spec *is* proving the rule, so writing the standard is part of the work, honestly
  `authority`-graded when it lands. This is the pairing `sp-impact-uncovered` checks: **name the
  path in the task text** so the match is findable.
- **Verification belongs in the list** — a task whose completion is "tests pass" or "the standard
  is written and self-checks clean" is a task, not an implicit hope.

Do not put `docs/knowledge/` captures or glossary terms in `## Tasks` as durable content — those
route through `/docs:learn` / `/docs:define`; a task may *name* the capture
(`- [ ] 5.2 Capture the retry-budget gotcha via /docs:learn`) but the knowledge itself lives in its
OKF home, never in the checklist.

## Execution metadata — optional, indented, additive

A checkbox MAY carry indented metadata lines directly beneath it:

```markdown
- [ ] 3.2 Add rate limiting to the auth middleware
      files: src/middleware/auth.ts, src/config/limits.ts (new)
      pattern: src/middleware/cors.ts
      verify: pnpm test middleware/
      subject: plan/session-tokens: 3.2 Add rate limiting to the auth middleware
```

| Key | What it carries | Why execute wants it |
| --- | --- | --- |
| `files:` | comma-separated paths this task may touch | bounds the work; **declaring it is what permits the task to be handed to an executor sub-agent**, and it is what makes a `[P]` marker checkable |
| `pattern:` | an existing file to imitate | the cheapest context an executor can be given — one path beats three paragraphs of description |
| `verify:` | the command that proves the task done | run under the spec's `verification` policy; a task with no `verify:` falls back to `## Validation` |
| `subject:` | the SUBJECT of the commit that implements this task | **written by the tool, never by hand** (`task --check --subject`), so code and spec stay linked without a trailer inside the commit message. Known before the commit exists, which is what lets the box travel inside it |

Write the first three where they earn their place — a task touching three known files with an
obvious test command deserves all three; a one-line doc edit deserves none. Metadata that restates
the task text is noise. `subject:` is not written by an author at all; it appears when the task is
ticked.

**`[P]` marks a task parallel-eligible**, written right after the id:

```markdown
- [ ] 3.3 [P] Add the rate-limit config loader
      files: src/config/limits.ts
```

Set it **here, at definition time** — execution never infers it. It is honoured only when the
marked tasks' `files:` sets are provably disjoint and none writes into `docs/`, which
`specs.py parallel` checks mechanically. Serial is the default and needs no marker: without proven
disjunction, parallel execution trades wall-clock for merge conflicts and loses on both.

**A blocked task is a visible marker, not a hidden counter** —
`- [!] 2.3 <title> — blocked: <reason>`, written by `task --block --reason`, skipped by `next`.

### The verification policy is the spec's, not the task's

`per-task` / `per-section` (default) / `end-of-plan`, recorded in frontmatter. It answers *when* the
checks run; `verify:` answers *what* runs. Declaring it during definition is what keeps
`/specs:execute` from having to guess, or from stopping mid-build to ask.

## `## Discoveries` and `## Outcome`

**`## Discoveries`** has no gate — it is appended to during execution, one line per finding, by
`specs.py discover`. Captured **indiscriminately**: whether a discovery is worth acting on is a
later judgment, and asking the executor to make it mid-task is how a finding gets dropped for being
inconvenient. Each line is resolved **in place** by `/specs:develop`'s discoveries bank, so
provenance is never lost:

```markdown
- the rate limiter double-counts retries -> promoted: fix-retry-accounting
- the config loader is slow on cold start -> dismissed: acceptable, runs once
```

**`## Outcome`** is the archive gate, written at close-out: what shipped, what was left out, what
the next reader needs to know — **including the merge strategy**, since a squash changes what a
future reader can resolve from a `subject:` field. For an abandoned spec, the reason it will not be
built is the whole content.
