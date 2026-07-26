---
name: quenching-align-all
description: >-
  Aligns ALL THREE of a repository's fronts in one run — quenching-docs-align (the OKF
  docs/ bundle), then quenching-specs-align (the specs/ spec-driven workspace), then
  quenching-skill-align (the .claude/ skill + command surface) — as a dependency pipeline,
  on a single confirmation. Use when the user asks to "align everything", "align the whole
  repo", "run all the aligns", "normalize this repo", "install quenching in this repo",
  "align docs, specs and skills", or "set the repo up end to end". ONE read-only probe →
  ONE OK authorizes the whole run (each front still narrates its own plan, and any item
  touching product code confirms on its own) → the three sweeps run in order, each under its
  own doctrine → one consolidated report. The order is a dependency: docs/ first, because the
  other two write OKF artifacts into it. Not for: one front alone
  → quenching-docs-align / quenching-specs-align / quenching-skill-align; also pulling content in and
  looping every front to a fixpoint → quenching-align-and-update-all.
when_to_use: >-
  running the three align sweeps (docs → specs → skills) in dependency order on one
  confirmation.
allowed-tools: Read, Grep, Glob, Bash, Skill
user-invocable: false
---

# quenching-align-all — one confirmation, three fronts aligned

The plugin acts on **three** surfaces of a repository, and each has an align sweep that forces
it into the plugin's canonical shape:

| # | Front | Sweep | What converges |
| --- | --- | --- | --- |
| 1 | `docs/` — the OKF bundle | `quenching-docs-align` | homes, frontmatter stamps, every `index.md`, `log.md`, the validator |
| 2 | `specs/` — the spec-driven workspace | `quenching-specs-align` | scaffold, doctor/validate, change + archive names, the `backlog/` inbox and its derived zone |
| 3 | `.claude/` — the automation surface | `quenching-skill-align` | skill names on the taxonomy axis, mirrored command wrappers, the rule + registry, the GENERATED zone |

This skill is the **conductor** over the three. It runs one read-only probe, asks for **one**
confirmation, and then invokes the three sweeps in dependency order. It never edits a doc, a
change, or a skill itself: every write is made by the sweep it invokes, under that sweep's own
doctrine and its own confirmation for code-coupled items.

Its sibling conductor is `quenching-docs-align-and-update`, which is **orthogonal**: converge loops the
`docs/` front's four sweeps (align → import-memory → harness → glossary-backfill) pass after
pass to a fixpoint; this skill runs the **one** align of each of the **three** fronts, once.
Both share the single authorization contract in
[../quenching-align-and-update-all/references/convergence.md](../quenching-align-and-update-all/references/convergence.md)
§cycle-authorization — cited here, never restated.

This skill also **owns** the sweep contract the three aligns share —
[references/sweep-doctrine.md](references/sweep-doctrine.md): convergence over accommodation,
one plan → one OK with code-coupled items gating individually, the two-scan blast-radius
procedure, MERGE-never-clobber, never-delete-on-a-guess, and align-conformance-report-the-cycle.
It lives here because this is the skill that spans all three fronts; each align cites it as its
doctrine and states only its own front's deltas. A change to how a sweep behaves is one edit
here, not three edits that must stay in agreement.

## Doctrine

- **Order is a dependency, not a preference.** `docs/` → `specs/` → `.claude/`:
  - **docs first** — both other fronts write OKF artifacts into the bundle (the skill front's
    rule `docs/standards/automation/skills.md` and registry
    `docs/documentation/reference/automation.md`; the specs front's `docs/log.md` entry). None
    of them can land in a tree that is not there.
  - **specs before skills** — when migrating a legacy `openspec/` workspace, `quenching-specs-align`
    removes the CLI-generated `.claude/skills/openspec-*` + `.claude/commands/opsx/` shadow
    copies, so `quenching-skill-align` inventories an already-clean surface instead of
    classifying plugin duplicates onto the taxonomy axis (a native `specs/` repo has no such
    copies, so the order is harmless there and still holds).
  Never run a later front before an earlier one.
- **Conduct, never reimplement.** The conductor sequences, gates, and reports. If a front's
  behavior must change, change that front's skill — the same ONE-authority-per-concern rule
  that keeps `quenching-docs-align-and-update` from re-deriving its stages' logic.
- **One OK per run; the run is the unit.** The gate fires **once**, before Front 1, under the
  cycle-authorization contract
  ([convergence.md](../quenching-align-and-update-all/references/convergence.md) §cycle-authorization). It absorbs each
  sweep's routine plan pause — it **never** absorbs a **code-coupled** item: a rename whose
  blast radius reaches product code still surfaces as its own confirmation, always, in every
  front. The conductor must not suppress that.
- **Front presence decides the pass; only `docs/` is installed unasked.** An absent `docs/`
  bundle is *the* thing this plugin installs, so Front 1 always runs. An absent `specs/` is
  **offered as its own line in the plan** — scaffolding it imposes a spec-driven workflow, so it
  is opt-in, never a side effect. An empty `.claude/` surface (no skills, no
  commands) skips Front 3 with a note rather than scaffolding a taxonomy for nothing.
- **One pass, not a fixpoint.** This is a sequence, not a loop. Residue a front reports is
  **reported**, never chased by re-running the front — for the `docs/` front's deeper
  convergence the report points at `/docs:align-and-update`, whose whole job is the fixpoint.

## Workflow (probe → ONE OK → three fronts in order → report)

### 1. Probe the three fronts (read-only, cheap)
Establish presence and rough scale — **not** a full inventory, which each sweep does for
itself:
- **docs/** — does a bundle root exist (`docs/` or the repo's variant, `index.md` / `log.md` /
  `okf_version`)? Run `${CLAUDE_PLUGIN_ROOT}/assets/hooks/okf-validate.py <docs> --json` and
  keep the finding counts.
- **specs/** — does a `specs/` root exist? If yes, `specs.py list --json` for the change count
  and `Glob` `specs/backlog/*.md` for the task count.
- **.claude/** — `Glob` `.claude/skills/*/SKILL.md`, `.claude/commands/**/*.md`, and
  directory-scoped `**/.claude/skills/*/SKILL.md`; count them, and note how many are legacy
  CLI-generated `openspec-*` shadow copies (Front 2 clears those when migrating a legacy
  `openspec/` workspace).
**Done when:** each front is marked *present / absent / not applicable*, with its counts, and
nothing has been written.

### 2. Present the RUN plan → gate on ONE OK
One short table: front · state · what its sweep will do (scope and counts, **not** full diffs —
each sweep still presents its own detailed plan as narration when it runs) · skipped-and-why.
An absent `specs/` appears as an explicit opt-in line (*"scaffold `specs/`? — declining skips
Front 2"*). State plainly: *"this authorizes the three
sweeps below; any item that touches product code still pauses for its own confirmation,
always."* Wait for **one** OK. **Done when:** the user has answered; declined → nothing
written, run ends.

### 3. Front 1 — `quenching-docs-align` (the `docs/` bundle)
Invoke via the **Skill** tool, declaring the authorization mode verbatim per
[convergence.md](../quenching-align-and-update-all/references/convergence.md) §cycle-authorization: *"Running under
quenching-align-all authorization granted at run start — skip your plan-confirmation pause;
present your plan as narration and execute; code-coupled items still gate individually."*
Record what it reports it changed, and its residual validator findings. A hard failure here
(the bundle could not be established) **stops the run** — Fronts 2 and 3 write into the bundle.
**Done when:** the sweep has finished and its outcome is recorded.

### 4. Front 2 — `quenching-specs-align` (the `specs/` workspace)
Skip if the front was marked absent and the scaffold line was declined. Otherwise invoke it with
the same authorization declaration. Record its counts **and** its reported-not-applied residue
(complete changes to archive, stale changes, untriaged tasks, boundary smells) — those flow into
the final report unchanged, never acted on here. A failure in this front is **reported, not
fatal**: Front 3 still runs, and the report says the skill surface was inventoried with legacy
shadow copies possibly still present. **Done when:** the sweep has finished or been skipped with
a stated reason.

### 5. Front 3 — `quenching-skill-align` (the `.claude/` surface)
Skip if the surface is empty (nothing to migrate). Otherwise invoke it with the same
authorization declaration. Its rule + registry creation lands in the bundle Front 1 just
aligned — verify the front order held before invoking. **Done when:** the sweep has finished or
been skipped with a stated reason.

### 6. Consolidated report + one log entry
One report, front by front: what each sweep changed (counts), what each **deferred** and to
which skill/command, and the ending state of each front (validator findings, doctor/validate
state, registry-vs-`.claude/skills/` agreement). State which **operator manuals** each front
installed, refreshed, or left alone (`docs/QUENCHING.md`, `specs/QUENCHING.md`,
`.claude/QUENCHING.md`) — each front writes its own; this skill only reports them, and points a
first-time adopter at `docs/QUENCHING.md` as the place to start. Name the next moves explicitly —
`/docs:align-and-update` for the `docs/` fixpoint loop, `/specs:plan:archive` / `/specs:backlog:triage` for the
specs residue, `/skill:new` for a gap the sweep could only report. Then append **one**
entry to `docs/log.md` per **Appending to `log.md`** in
[../quenching-docs-add/references/homes.md](../quenching-docs-add/references/homes.md):
`**Update**: [Repository](/docs/index.md) — aligned all fronts (docs/specs/skills); N deferred`.
**Done when:** every front's outcome and every deferral is stated, and the entry is written.

## Invariants to never violate

- Never run the fronts out of order, and never run a later front when an earlier one failed to
  establish what it owns (a missing bundle stops the run).
- Never suppress a sweep's **code-coupled** confirmation. The single upfront OK covers routine
  writes only, exactly as in [convergence.md](../quenching-align-and-update-all/references/convergence.md)
  §cycle-authorization.
- Never scaffold `specs/` without its own explicit line in the plan, and never scaffold a
  `.claude/` taxonomy for an empty surface.
- Never reimplement a front's logic here — **invoke** the sweep via the Skill tool, always.
- Never act on a front's reported-not-applied residue (archiving a change, ranking a task,
  minting a skill) — carry it into the report and name the skill that owns it.
- Never loop a front to force a clean result — this is one pass; the fixpoint loop is
  `quenching-docs-align-and-update`.
- Never hand this SKILL.md `context: fork` — the gate and every code-coupled confirmation are
  mid-flow.
