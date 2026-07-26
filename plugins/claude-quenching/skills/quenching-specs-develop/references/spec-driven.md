# Spec-driven facts — the single-file lifecycle, the phase gates, the `specs.py` tool

The shared factual reference for the `quenching-specs-*` skills. **This file is the single owner
of the spec-driven facts** — the `specs/` layout, the spec file's format, the phase gates, the
derived stages, the executor contract, and the `specs.py` tool surface — and every
`quenching-specs-*` skill cites these sections instead of restating them. The OKF bridge (what
durable knowledge crosses from a spec into `docs/` and how) lives with the archive-side skill
([../../quenching-specs-archive/references/distill.md](../../quenching-specs-archive/references/distill.md)).

This front is **entirely native** — no external CLI, no Node runtime, no main spec store, no delta
format. A **spec** writes straight into the OKF `docs/` bundle (a decision into `docs/standards/`,
an understanding into `docs/knowledge/`), isolated on a branch while it is built. The tool that
gives the LLM deterministic rails is `assets/bin/specs.py` — a stdlib-only Python script in the
same mold as `okf-validate.py`.

## Contents

- [The `specs/` layout](#the-specs-layout)
- [Identity: the slug and the filename](#identity-the-slug-and-the-filename)
- [Frontmatter](#frontmatter)
- [The thirteen sections](#the-thirteen-sections)
- [The phase gates and the phase-scoped explicit-none rule](#the-phase-gates-and-the-phase-scoped-explicit-none-rule)
- [Derived stages](#derived-stages)
- [`## Impact` — the one parsed declaration](#-impact--the-one-parsed-declaration)
- [`## Tasks` and the `[!]` blocked marker](#-tasks-and-the--blocked-marker)
- [The executor contract](#the-executor-contract)
- [The `specs.py` tool surface](#the-specspy-tool-surface)
- [Boundary: `specs/` vs the OKF `docs/` bundle](#boundary-specs-vs-the-okf-docs-bundle)

## The `specs/` layout

**One spec is ONE markdown file for its entire lifecycle.** Phases enrich it; they never split it.
The front lives at the target repo root (never inside `docs/`):

```
specs/
  backlog/                     # DEFINITION — raw problem through refined, buildable spec
    index.md                   # listing with a GENERATED zone, grouped by derived stage
    2026-07-25-session-tokens.md
  ready/                       # EXECUTION — ready to build, or building
    2026-07-14-rate-limiting.md
  archive/                     # done or abandoned, told apart by `outcome:` frontmatter
    2026-06-30-audit-log.md
```

**The folder is the macro-phase, and it is the single truth.** There is no `phase:` frontmatter
field: two declared sources of one fact will diverge, and a folder cannot lie. The transition is
`git mv` (performed by `specs.py promote`), so `git log` narrates the lifecycle.

`backlog/` is the definition phase — it is where a spec is captured, proposed, designed and
refined. It is **not** part of the OKF `docs/` bundle, so `okf-validate.py` does not scan it (it is
checked with `--listing-root`; see
[backlog-zone.md](../../quenching-specs-capture/references/backlog-zone.md)).

There is **one truth**, not two: a spec does not edit a separate "main spec" store — it writes the
durable rule directly into `docs/standards/`, honestly `authority`-graded. There is no delta,
because there is no other copy for a delta to bridge to; isolation-while-building is what a
**branch or worktree** provides, with real merge, history, and reversion.

## Identity: the slug and the filename

**Every spec file is named `YYYY-MM-DD-<slug>.md`, in every folder.** The date prefix records when
the spec was **born** and is written **once, at capture** — `promote` moves the file and never
renames it. The basename is therefore stable for the whole lifecycle, `git log --follow` reads as
one history, and a plain `ls` of any folder is chronological. That last property is the point: a
file listing IS the status view this design is built on, and no file listing reads frontmatter.

**Identity is the slug, not the path.** Every cross-reference names the bare slug; `specs.py`
resolves it to the one file whose name ends in `-<slug>.md`, wherever it sits. **Two matches is a
refusal (exit 2), never a guess.** This is what makes repeated folder moves survivable.

The prefix earns its place in all three folders, not just `archive/`: birth order is the order a
human wants in every phase — *how long has this sat in `backlog/`? how long has this build been
open in `ready/`?*

## Frontmatter

Write-once, low-churn fields only. Machine state a human never reads does not belong in a spec.

| Key | Required | Meaning |
| --- | --- | --- |
| `slug` | always | the identity key every command and cross-reference names |
| `title` | always | one human-readable line |
| `verification` | always | `per-task` · `per-section` · `end-of-plan` — when `verify:` runs |
| `refined` | once refined | `{mode, date}` — written after a real refinement pass |
| `outcome` | at archive | `done` · `abandoned` — stamped by `promote --to archive` |

**There is no `created` field**: the filename's date prefix IS that fact, and one truth never gets
two declared sources. `slug` is the deliberate exception — it is the identity key, so a mirror
inside the file is worth its keep, and `validate` compares it to the filename suffix. A merely
derived fact earns no such mirror.

There is no attempt counter and no `.specs.json`. Both are gone.

## The thirteen sections

The canonical set, in canonical order. **Headings are a parsed contract** — canonical English, like
frontmatter keys — while body prose follows the repo's language. A heading outside this set is a
**stray** and `validate` flags it.

| # | Heading | Phase | Audience |
| --- | --- | --- | --- |
| 1 | `## Problem` | definition | human |
| 2 | `## Proposal` | definition | human |
| 3 | `## Out of Scope` | definition | human |
| 4 | `## Impact` | definition | human + **parsed** |
| 5 | `## Validation` | definition | human + agent (the `verify:` fallback) |
| 6 | `## Design` | definition | human |
| 7 | `## Alternatives Considered` | definition | human |
| 8 | `## Open Decisions` | definition | human |
| 9 | `## Risks` | definition | human |
| 10 | `## Handoff` | execution | **agent** |
| 11 | `## Tasks` | execution | **agent** |
| 12 | `## Discoveries` | execution | triage |
| 13 | `## Outcome` | archive | archive reader |

**Every section declares its audience, and that is load-bearing.** `## Problem` / `## Proposal` /
`## Design` are for the human — examples and plain language live there. `## Handoff` / `## Tasks`
are for agents — terse, carrying `files:` / `verify:` / `pattern:` metadata. An orchestrator never
sends the human sections to an executor; this is what lets one file serve both audiences without
bloating agent context.

Two of these sections are load-bearing for machinery, not just for thinking:

- **`## Validation`** is the fallback for a task with no `verify:` line.
- **`## Impact`** is machine-parsed (see below). Removing the heading silently disables a check.

## The phase gates and the phase-scoped explicit-none rule

A section is required — and required to carry an explicit `- none — <reason>` when it has nothing
in it — **only once its own phase gate is reached**. Before its gate, a heading's absence is not an
omission; it is a *not-yet*.

| Gate | Required sections |
| --- | --- |
| `new` (capture) | `## Problem` |
| `promote → ready/` | the nine definition sections (`## Problem` … `## Risks`) **and `## Tasks`** |
| `ready/` (warning only) | `## Handoff` non-empty |
| `promote → archive/` | `## Outcome` |

`## Tasks` is in the `ready/` gate because **promote-to-`ready/` IS the human OK to build**, and
nothing may enter the execution phase with nothing to execute. This is the v2 form of the
guarantee v1 spelled `applyRequires: ["tasks"]`.

Three rules decide whether a section counts as filled:

1. **`- none — <reason>` counts as filled.** An omission and a null are different facts, and an
   explicit null is strictly more information than an absent heading. It costs one line.
2. **A present-but-empty heading is malformed and refuses.** It is neither an answer nor a
   not-yet, and admitting it would reintroduce the ambiguity this rule exists to remove.
3. **An absent heading before its gate is legal.** `specs.py new` stamps `## Problem` and nothing
   else — a captured spec is four lines of body, not a thirteen-heading skeleton.

**Why the rule is scoped rather than absolute.** Applied absolutely it would kill the derived
stage: since `- none — <reason>` counts as filled, a freshly captured spec carrying thirteen
`- none` sections would derive as `designed` and pass every gate without anyone having thought
anything. Phase-scoping is the version where both rules survive.

The per-phase sets live in `assets/specs/schema.json` and are read by **both** `promote` and
`validate` — one source, two consumers. A wrong mapping there fails in one of two silent ways (too
strict blocks every promote; too loose lets an empty spec through every gate), which is why it is
declared once and asserted by `validate`.

## Derived stages

Sub-stages are **computed from section completeness, never declared**. Declared state is forgotten
on edit and goes stale; derived state regresses automatically when a section empties. The
computation reads **heading presence**, never a three-state body — which is exactly what the
phase-scoped rule above keeps unambiguous.

| Folder | Stage | Derived from |
| --- | --- | --- |
| `backlog/` | `captured` | only `## Problem` filled |
| `backlog/` | `proposed` | `## Proposal` filled |
| `backlog/` | `designed` | `## Design` filled |
| `backlog/` | `refined` | a `refined` record in frontmatter |
| `ready/` | `executing` | any `[x]` or `[!]` box, or `## Handoff` filled |

`specs.py list` and the `backlog/index.md` GENERATED zone group by these stages.

## `## Impact` — the one parsed declaration

`## Impact` is declared scope for human review, with exactly one machine-checked part:

```markdown
### Standards this spec will write into docs/standards/

- `docs/standards/auth/session-tokens.md` — how a session token is minted and revoked
```

`parse_impact_standards()` reads the `docs/standards/**.md` paths bulleted under **that heading and
only that heading**, and `validate` emits `sp-impact-uncovered` (warn) for any path no `## Tasks`
item names.

Two exclusions are deliberate: the **sibling sub-headings are not parsed** (a background standard
the spec *may* resolve, and the product code it touches, name paths the spec never promised to
write), and an unfilled `<placeholder>` declares nothing. A spec with no such sub-heading declares
nothing and is never flagged — **the check is opt-in by writing the heading**.

## `## Tasks` and the `[!]` blocked marker

Checkboxes `- [ ] <id> <text>` grouped under `### N. <Section>` headings, carrying optional
`files:` / `verify:` / `pattern:` / `[P]` metadata. `specs.py task --check <id>` flips a box
mechanically — **never by string surgery**.

A blocked task is a **visible marker, not a hidden counter**:

```markdown
- [!] 2.3 Implement the gate check — blocked: schema.json has no `ready` set yet
```

Written by the orchestrator when it decides to stop retrying; `next` skips it. **There is no
attempt budget.** Its only value was stopping unattended retry loops, and an honest written reason
serves that better than a counter nobody sees — and it is readable by the human who has to unblock
it.

`[P]` marks a parallel-eligible group, honoured only when the group's `files:` sets are provably
disjoint (`specs.py parallel`). Serial by default.

## The executor contract

**The orchestrator is the spec's only writer.** An executor receives:

- its task line (with `files:` / `verify:` / `pattern:`),
- the whole `## Handoff` (small by construction),
- the touched subjects' `docs/standards/` contracts.

It does **not** receive `## Problem` / `## Proposal` / `## Design`. It returns a structured result
— status, diff summary, `verify:` output, discoveries, handoff deltas — and **never writes the
spec**. The orchestrator applies everything via `specs.py` (`task --check`, `discover`,
`section --write`), runs `verify:` itself, and commits: **whoever commits, verifies.** This is also
what makes one file safe under parallelism — one writer, mechanical writes.

Discoveries are **captured indiscriminately**; whether one is worth acting on is triage's judgment,
not the executor's. They are born in the origin spec's `## Discoveries` and resolved later, in
place, to `→ promoted: <new-slug>` or `→ dismissed: <reason>`, so provenance is never lost and the
human pays the decision cost in batch.

`## Handoff` refresh is **bound to events, not judgment**: the orchestrator rewrites it after each
committed task and at every promote. Staleness is this section's failure mode, and an event-bound
rule is the only cure that survives unattended runs — `validate` warns when a `ready/` spec has an
empty `## Handoff`.

## The `specs.py` tool surface

Uniform contract: `--json` on every subcommand; strict exit codes — **0** ok · **1** findings ·
**2** refusal. A skill branches on the exit code and the JSON, never on prose.

| Command | Use |
| --- | --- |
| `specs.py new <slug> [--title T] [--verification P]` | scaffold `backlog/YYYY-MM-DD-<slug>.md` with `## Problem` as its only section; the date is stamped here and never again |
| `specs.py list [--json]` | every spec, grouped by folder and derived stage |
| `specs.py status --spec <slug> [--json]` | sections present, derived stage, task progress, and the destination phase's outstanding gates |
| `specs.py section <slug> <heading> [--write]` | deterministic partial read/write of ONE section; `--write` creates the heading in canonical position |
| `specs.py promote <slug> [--to ready\|archive] [--outcome done\|abandoned] [--force]` | gated transition; **exit 2** with the missing list, else `git mv` |
| `specs.py next --spec <slug> [--json]` | THE single next action, carrying the task's `verify`/`files`/`pattern`/`[P]`; skips `[!]` |
| `specs.py task --spec <slug> --check ID \| --uncheck ID \| --block ID --reason MSG` | flip or block a checkbox mechanically |
| `specs.py discover <slug> <text>` | append one line to `## Discoveries` |
| `specs.py parallel --spec <slug> [--json]` | verify each `[P]` group's `files:` sets are disjoint — **exit 1** when any group is ineligible |
| `specs.py backlog reindex` | regenerate the `backlog/index.md` GENERATED zone, grouped by derived stage |
| `specs.py validate [--spec <slug>]` | the canonical heading set, the phase-scoped rule, filename conformance, the `sp-*` vocabulary |
| `specs.py doctor` | workspace shape — three folders, strays, v1 leftovers; remedies **declared** for the skill to apply |
| `specs.py migrate` | one-way v1 → v2 fold; **exit 2** on an already-v2 target; `specs/archive/**` never touched |

`promote` is the load-bearing command. Destination is inferred (`backlog`→`ready`→`archive`) or
forced with `--to`. It checks the destination phase's required-section set from `schema.json`,
refuses with **exit 2** and the missing list, and otherwise moves the file **without renaming it**.
`--outcome` applies to the archive hop only, and is the only content a promote ever writes.

**Archiving a spec with open tasks refuses.** `--outcome done` with unchecked `- [ ]` boxes exits 2
and lists them, overridable with `--force`; `--outcome abandoned` is always allowed, because
closing out a spec that will not be built is exactly the case where open tasks are expected.

There is no `init` (scaffold is an asset copy — the skill's job), no `store`, no `profiles`, no
telemetry, and no delta parser.

Templates live in `assets/specs/templates/spec.md` and are stamped by `specs.py new` — with the
same content embedded as a fallback constant in `specs.py` itself, so an installed copy under a
target's `.claude/hooks/` with no adjacent assets stamps an identical file. **Edit both or
neither.** A template's scaffold content must stay invisible to `has_real_content()`: only headings
and HTML comments, with any example inside a comment or written as a `<placeholder>`.

### Resolving the tool

Each `quenching-specs-*` skill resolves the script by the same fallback the backlog zone uses
([backlog-zone.md](../../quenching-specs-capture/references/backlog-zone.md)): the plugin path
`${CLAUDE_PLUGIN_ROOT}/assets/bin/specs.py` first, then a copy installed into the target's
`.claude/hooks/specs.py`, and if neither resolves, the declared manual check — do the same rule by
hand and **say in the report that the check was manual**, never silently skip it. Invoke with
`python3` or `py` (`allowed-tools: Bash(python3:*), Bash(py:*)`).

## Boundary: `specs/` vs the OKF `docs/` bundle

**This section is the single normative owner of the boundary.** Everywhere it comes up —
`quenching-specs-align`'s conformance codes, `distill.md`'s what-crosses table, `homes.md`'s
task-vs-vision tie-breaker, the `QUENCHING.md` operator manuals — cites it.

- `specs/backlog/` and `specs/ready/` — **the in-flight unit of work**: a spec's problem, design,
  and task checklist while it is being defined and built. Owned by the `quenching-specs-*` skills;
  leaves for `archive/` when done.
- `docs/standards/` — **how WE build** (binding contracts: naming, architecture, code);
  `docs/knowledge/` — generic understanding. A spec writes its durable rule **directly** into
  `docs/standards/` (`authority`-graded), and the archive-time distillation
  ([distill.md](../../quenching-specs-archive/references/distill.md)) routes any remaining
  by-products (a term, an understanding, a follow-up) — never by bulk copy.

The spec **is** the change: what it proves out lands in `docs/` as it is built, honestly graded
(`authority: background` for an agreed-but-unproven rule, `current` for one the spec implemented
and proved). There is no second store for it to duplicate.
