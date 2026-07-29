---
slug: add-eli5-section-to-specs
title: Add an ELI5 section that makes a spec comprehensible to a human
verification: per-section
priority: {level: 22, criticality: low, date: 2026-07-28}
refined: {mode: gate, date: 2026-07-28}
approved: {date: 2026-07-29}
branch: {base: main, work: plan/add-eli5-section-to-specs}
---

# Add an ELI5 section that makes a spec comprehensible to a human

<!-- ONE spec is ONE file for its whole lifecycle. Phases enrich it; they never split it.

     `specs.py new` stamps the frontmatter and `## Problem` ALONE — a captured spec is four
     lines of body, not a thirteen-heading skeleton. Every other heading below is created on
     first write by `specs.py section <slug> "<Heading>" --write`, which inserts it in the
     canonical position with the guidance comment kept here.

     THE STAGE-SCOPED EXPLICIT-NONE RULE. A heading is required — and required to carry
     `- none — <reason>` when it has nothing in it — only once ITS OWN gate is reached:

       new (capture)        `## Problem`
       ready (derived)      the nine definition sections (`## Problem` .. `## Risks`)
                            AND `## Tasks`
       ready (warn only)    `## Handoff` non-empty
       promote -> archive/  `## Outcome`

     `ready` is a DERIVED STAGE, not a folder: a spec lives in `plans/` for its whole active
     life, and filling those ten sections is what makes it ready. Nothing refuses on that
     gate — it is a floor `execute` reports against, and the human's go-ahead is the
     `approved:` frontmatter record, asked for inline.

     Before its gate, a heading's absence is NOT an omission — it is a not-yet. After its
     gate, three rules decide whether a section counts as filled:

       1. `- none — <reason>` counts as filled. An omission and a null are different facts.
       2. A heading present with an EMPTY body is malformed and refuses. It is neither an
          answer nor a not-yet.
       3. An absent heading before its gate is legal.

     Headings are a PARSED contract — canonical English, exactly as written here. Body prose
     follows the repo's language. A heading outside this set is a stray and validate flags it.

     AUDIENCE. Each section names who reads it. `## Problem`/`## Proposal`/`## Design` are for
     the human — examples and plain language belong there. `## Handoff`/`## Tasks` are for
     agents — terse, with `files:`/`verify:`/`pattern:` metadata. An orchestrator never sends
     the human sections to an executor; that is what lets one file serve both audiences
     without bloating agent context. -->

## Problem

A spec's sections are already written for a human reader, and it still is not enough:
understanding what a spec is actually about takes real effort. The dense, precise framing that
makes a spec good to build from is the same thing that makes it hard to grasp on first read.

Specs need an ELI5 rendering that simplifies them enough to be understood quickly. Two shapes are
on the table and neither has been chosen: one complementary `## ELI5` section covering the whole
spec, or an ELI5 subsection inside each section.

## Proposal

A fourteenth canonical section, `## Overview`, positioned first — ahead of `## Problem` — whose
job is to orient a reader who is not holding the spec in their head: someone reviewing a spec they
did not write, or returning to their own two weeks later.

It is **connective tissue, not a summary**. A summary compresses each section; an Overview links
them, so the dense material that follows has somewhere to attach. The two failures reported are
not independent — being unable to see a spec's scope, and finding the sections too complicated
once read — because the second is largely downstream of the first. A reader given the frame can
follow the dense sections; a reader without it cannot, however plainly each section is written.

After this lands:

- `specs.py` knows the heading: canonical position 1 of 14, so `validate` no longer flags it as a
  stray, and `section <slug> "Overview" --write` inserts it in place.
- It is **warn-only**, like `## Handoff` — never one of the ten sections the derived `ready` stage
  requires.
- `/specs:develop` writes it in the shape bank and refreshes it inside every later bank's
  consolidated edit, so it stays true without a new prompt or a second confirmation.
- Existing specs in `plans/` are backfilled by a one-time sweep, so the section is uniformly
  present rather than partially — `archive/` is left alone.
## Out of Scope

- The OKF `docs/` bundle gains no equivalent. This is a `specs/`-front section; concept docs keep
  their current frontmatter and shape.
- No change to the other thirteen headings — their wording, their order relative to each other,
  their declared audiences, or which ten make up the `ready` gate.
- `specs.py` never generates the text. The three tools carry no model: they parse, position and
  validate the heading, and every word of an Overview is written by a command.
- The three consumers keep regenerating their own renderings. `/specs:triage`, `/specs:continue`
  and the approval bank do not read `## Overview` in this spec. Backfill enables that work, but
  enabling establishes ordering, not membership — and the wiring answers a different problem
  (three commands regenerating a rendering per invocation and disagreeing with each other) than
  the one in `## Problem`. It is a follow-up spec.
- `archive/` is not backfilled. Archived specs carry `## Outcome`, a written record of what
  actually happened — a better orientation than a reconstructed one, and free.
## Impact

### Standards this spec will write into docs/standards/

- `docs/standards/workflows/plan-artifacts.md` — revised: the canonical set becomes fourteen
  sections with `## Overview` at position 1, and the gate table gains it as warn-only beside
  `## Handoff`

### Product code this spec expects to touch

- `plugins/quenching/assets/specs/schema.json` — the `sections` array and the `ready` stage rule
- `plugins/quenching/assets/bin/specs.py` — the duplicated `SCHEMA["sections"]` constant, the
  duplicated `TEMPLATE_SPEC`, and a new `sp-overview-missing` (warn) finding
- `plugins/quenching/assets/specs/templates/spec.md` — the heading and its guidance comment
- `plugins/quenching/assets/references/specs-develop/spec-driven.md` — §The thirteen sections
- `plugins/quenching/assets/references/specs-develop/artifacts.md` — the section's entry and its
  writing register
- `plugins/quenching/assets/references/specs-develop/questions.md` — the shape bank lands it, every
  bank refreshes it
- `plugins/quenching/commands/specs/align.md` — reports `sp-overview-missing`; never authors it
- the six version artifacts of `docs/standards/ci-cd/versioning-release.md`
- `specs/plans/*.md` — every active spec gains the section, once

The middle sub-heading (`authority: background`) is deliberately absent: the check is opt-in by
writing the heading, and this spec promotes nothing.

## Validation

Run from `plugins/quenching/` unless a path says otherwise.

**The two assertions this spec is the reason for.**

- **`## Overview` is warn-only, not a gate.** A spec that does not carry the heading must report the
  same `stage` and the same `ready.ok` it reported before the change — the derived `ready` set stays
  at ten. A regression here retroactively un-readies every spec in every aligned repo.

  ```bash
  python3 assets/bin/specs.py status --spec <a-spec-without-overview> --json \
    | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['stage'], d['ready']['ok'], d['ready']['missing'])"
  ```

- **The backfill is complete, not partial.** Every spec in `plans/` reports `## Overview` as
  `filled`; the sweep prints nothing. This is the only detection the half-landed backfill in
  `## Risks` has.

  ```bash
  python3 - <<'EOF'
  import glob, json, re, subprocess
  for f in sorted(glob.glob("specs/plans/*.md")):
      m = re.match(r"\d{4}-\d{2}-\d{2}-(.+)\.md$", f.rsplit("/", 1)[-1])
      if not m:
          continue
      out = subprocess.run(["python3", "plugins/quenching/assets/bin/specs.py",
                            "status", "--spec", m.group(1), "--json"],
                           capture_output=True, text=True).stdout
      states = {s["heading"]: s["state"] for s in json.loads(out)["sections"]}
      if states.get("Overview") != "filled":
          print("missing:", m.group(1))
  EOF
  ```

**The routine gates, all of which must still pass.**

- `python3 assets/bin/specs.py selftest` — proves `TEMPLATE_SPEC` is byte-for-byte
  `assets/specs/templates/spec.md`, and the shared frontmatter rule
- `python3 assets/bin/specs.py validate` over `specs/plans` — no `sp-stray-heading` for `Overview`
- `python3 assets/hooks/okf-validate.py assets/docs` and
  `python3 assets/hooks/okf-validate.py assets/specs/plans --listing-root` — 0 errors, 0 warnings
- `./assets/bin/functional-checks.sh` — exit 0. The only check that the changed `commands/**` bodies
  and citation paths actually load
- `python3 assets/bin/skills.py --root . doctor --json` — 25 commands, no findings
- the six-artifact lockstep of `docs/standards/ci-cd/versioning-release.md`

## Design

**Position and audience.** Section 1 of fourteen, ahead of `## Problem`. Audience: human.
Orientation that arrives after the dense material is not orientation.

**Gate membership: warn-only.** The ten gate sections are declared once, in `schema.json`, as the
`ready` stage rule marked `gate: true`. An eleventh required heading would retroactively un-ready
every spec in every aligned repo the moment the schema shipped — `ready` is derived and recomputed
from disk on every read. Warn-only avoids that, and the refresh mechanic below removes the reason
a gate would otherwise exist. The explicit-none rule also argues against gating: `- none — not
needed` would satisfy a gate while defeating the section's entire purpose.

**Ownership and refresh.** `/specs:develop` owns it. Every bank already lands exactly one
consolidated edit behind one confirmation, so a refreshed Overview rides along in a diff the human
is already reading — no new prompt, no separate OK. A spec's sections are rewritten repeatedly, and
a stale Overview is worse than none: it is read first and frames everything after it.

**The Overview is written last, and shown separately.** In every consolidated edit it is authored
after the other sections have settled — it can only be correct once they have — and presented as
its own labelled before → after block, never folded into the list of section diffs. The section
whose job is to be read first must not be the least-read line of the diff it lands in. This is the
whole defence of the refresh mechanic: without it, a regenerated frame slides through behind
changes that were the actual subject of the confirmation.

**Register, stated rather than named.** `ELI5` carried its own writing instruction; `Overview` does
not, and pulls toward summary. `artifacts.md` must therefore state the register explicitly: plain
language, assume no prior context, no jargon the spec itself introduces, and connective rather than
compressive.

**Backfill bounds.** One sweep over `plans/`, never `archive/`. Full rather than lazy: partial
coverage teaches a reader to check whether the section is there before deciding how to read, which
is the cognitive cost the section exists to remove. Lazy backfill also puts the cost at the worst
moment — the first time someone opens a spec wanting orientation, they wait while it is generated.
Priced at roughly one long `develop` session, paid once.

**The backfill owner: a task here, a reported finding everywhere else.** Both candidates the open
decision listed are ruled out by their own published contracts — `/specs:align` reports authoring
actions "with the command that closes each, never performed"
([align-surface.md](../../docs/standards/architecture/align-surface.md)), and `/specs:triage` writes
the priority record "and nothing else". So the sweep splits along the authoring line rather than
being assigned to one owner: this repo's `plans/` is backfilled by one task on this branch, executed
once, and every other repo gets `sp-overview-missing` (warn) from `specs.py validate`, which
`/specs:align` reports and routes to `/specs:develop <slug>`. No command is minted for a one-time
migration, and no sweep gains the power to write prose.

**The backfill task names a rule, not a list.** One checkbox over a dynamic set — every spec in
`plans/` that lacks the heading — rather than one checkbox per slug. A list enumerated at definition
time is already wrong at execution time, since specs are created in between, and thirty-one
checkboxes for one paragraph each is the metadata noise `artifacts.md` warns against. The executor
may still fan out per spec; the task simply does not promise a shape it cannot keep.

**The lockstep tail.** The heading is a parsed contract, so it lands in every place the set is
declared: `assets/specs/schema.json`, the templates duplicated as constants in `specs.py`,
`assets/specs/templates/`, `spec-driven.md` §The thirteen sections, `artifacts.md`,
`questions.md` (the shape bank now lands here too), and
`docs/standards/workflows/plan-artifacts.md`.
## Alternatives Considered

- **An ELI5 subsection inside each section** — rejected. The per-section opacity is largely
  downstream of never having been given the whole-spec frame, so one section addresses both
  reported failures while thirteen glosses treat the symptom and multiply the maintenance surface
  by thirteen.
- **Refresh only at the approval gate** — rejected. Cheapest, and it lands where the decision is
  made, but the frame is wanted *while* the spec is being developed, not after.
- **No refresh; detect drift instead** — rejected. `specs.py` cannot judge semantic staleness. The
  most it could do is hash the body at write time and flag "sections changed since", a warning
  nobody can act on without rewriting the text by hand anyway.
- **A GENERATED zone maintained by `specs.py`** — rejected as impossible rather than undesirable.
  The tools are stdlib Python with no model; a listing is derivable from frontmatter, an
  orientation is not.
- **Wiring the three consumers in this spec** — rejected. Backfill makes the consumers viable, but
  that is an ordering argument, satisfied equally by a follow-up spec shipping the day this merges.
  Only the section and the backfill follow from `## Problem`.
- **Lazy backfill, on next touch** — rejected. Cheaper, but it produces partial coverage and bills
  the cost at the moment orientation was wanted.
- **Bounding the backfill by priority (top N)** — rejected. "Top N" goes stale the moment
  `/specs:triage` re-ranks, and the boundary would need re-deciding on every sweep.
- **A backfill stage inside `/specs:align`** — rejected. One mechanism covering every repo
  automatically, and skip-if-present would make it free after the first run — but it would make
  "Authoring and cycle actions are reported … never performed" false in the align description, which
  is the sentence that routes work to the right command.
- **`/specs:triage` as the sweep** — rejected for the same reason, more sharply: it already reads
  every spec in one pass, and its description commits it to writing the priority record and nothing
  else.
- **A new `/specs:backfill` command** — rejected. Uniform and honestly authorial, but it adds a
  permanent twenty-sixth entry point for a migration that runs once.
- **Names.** `ELI5` — off-register beside `Problem`, `Impact`, `Handoff`. `Orientation` — names the
  function precisely but signals nothing about the writing register. `Primer`, `Abstract` —
  literary and academic respectively. `Plain English` — disqualified: headings are canonical
  English while body prose follows the target repo's language, so the name would promise English
  over a body that may not be.
## Open Decisions

- none — the backfill owner was the only one open, and it is settled in `## Design`: one task on
  this branch for this repo, `sp-overview-missing` reported by `/specs:align` for every other.
## Risks

- **An installed `specs.py` that predates the heading flags every Overview as a stray.** A target
  repo aligned before this shipped carries an older tool at `.claude/hooks/`; validate then errors
  across a front that was clean, with a message pointing at the spec rather than the tool.
  Likelihood high, badness high, detection loud but misattributed. **Accepted without mitigation**:
  the drift problem is owned by `notice-installed-tool-version-drift` (priority 5, criticality
  high), ranked above this spec, and closing it here would duplicate that remedy inside one
  command.
- **The backfill half-lands.** A sweep interrupted at spec 18 of 31 leaves exactly the partial
  coverage the design argues against. **Accepted without mitigation**: re-running the sweep repairs
  it, since a spec that already carries the section is skipped.
- **Reverting is a migration, not a revert.** Removing the heading later makes every backfilled
  spec carry a stray. **Accepted explicitly, as the spec's biggest standing risk**: it is the
  ordinary cost of a parsed contract, `specs.py migrate` is the established one-way fold for this
  shape of change, and the section is warn-only, so nothing gates on it.
- **Every Overview drifts into a summary anyway.** The name pulls that way and the doctrine is one
  paragraph in `artifacts.md`; nobody notices, and the section becomes redundant with `## Problem`.
  Detection: none — this is the quiet one. **Accepted without mitigation**: the write-last rule
  partially counters it by authoring with every other section visible, and the failure is cosmetic
  rather than corrupting.

## Tasks

### 1. The parsed contract

- [x] 1.1 Add `## Overview` to the canonical section set as position 1 of fourteen, warn-only —
      the schema and the constant duplicated in the tool
      files: plugins/quenching/assets/specs/schema.json, plugins/quenching/assets/bin/specs.py
      verify: python3 plugins/quenching/assets/bin/specs.py selftest
      subject: plan/add-eli5-section-to-specs: 1.1 Add `## Overview` to the canonical section set as position 1 of fourteen, warn-only
- [x] 1.2 Add the heading and its guidance comment to the template, in BOTH copies
      files: plugins/quenching/assets/specs/templates/spec.md, plugins/quenching/assets/bin/specs.py
      pattern: the `## Handoff` block in the same template
      verify: python3 plugins/quenching/assets/bin/specs.py selftest
      subject: plan/add-eli5-section-to-specs: 1.2 Add the heading and its guidance comment to the template, in BOTH copies
- [ ] 1.3 Add `sp-overview-missing` (warn) to `specs.py validate`
      files: plugins/quenching/assets/bin/specs.py
      verify: python3 plugins/quenching/assets/bin/specs.py validate --json
- [ ] 1.4 Prove the gate did not move: a spec without `## Overview` reports the same stage and
      `ready.ok` as before, per the first assertion in `## Validation`

### 2. The prose contract

- [ ] 2.1 spec-driven.md §The thirteen sections becomes fourteen, with the position and the
      warn-only gate membership
      files: plugins/quenching/assets/references/specs-develop/spec-driven.md
- [ ] 2.2 artifacts.md gains the section's entry AND its writing register, stated explicitly:
      plain language, assume no prior context, no jargon the spec itself introduces, connective
      rather than compressive
      files: plugins/quenching/assets/references/specs-develop/artifacts.md
- [ ] 2.3 questions.md: the shape bank lands `## Overview`, and every bank refreshes it — authored
      last, shown as its own labelled before → after block, never folded into the section diffs
      files: plugins/quenching/assets/references/specs-develop/questions.md

### 3. The report surface

- [ ] 3.1 `/specs:align` reports `sp-overview-missing`, routing each to `/specs:develop <slug>`,
      and authors nothing
      files: plugins/quenching/commands/specs/align.md
      verify: ./plugins/quenching/assets/bin/functional-checks.sh

### 4. The standard

- [ ] 4.1 Revise docs/standards/workflows/plan-artifacts.md — fourteen sections, `## Overview` at
      position 1, warn-only in the gate table (authority: current)
      files: docs/standards/workflows/plan-artifacts.md, docs/standards/workflows/index.md, docs/log.md

### 5. Backfill and release

- [ ] 5.1 Backfill `## Overview` into every spec in `specs/plans/` that lacks it — the set resolved
      at execution time, one commit, `archive/` untouched
      verify: the completeness sweep in `## Validation` prints nothing
- [ ] 5.2 Bump the six version artifacts per docs/standards/ci-cd/versioning-release.md
      verify: cat VERSION and the three `--version` calls all agree
- [ ] 5.3 Run the full skeleton gate — selftest ×3, okf-validate ×2, skills.py doctor and lint,
      and ./assets/bin/functional-checks.sh — all clean
