# The `specs/` front's cycle — pipeline and routing

The reference `quenching-specs-align-and-update` reads. It fixes the two things specific to the
**`specs/` front**: the **pass pipeline** (which stages run, in what order, and why) and the
**opportunity → skill routing table** (how a read-only finding becomes a stage invocation).

Everything that is **not** front-specific — the cycle-authorization contract, the convergence
condition, the anti-spin guards, and why per-item skills are never stages — lives once, for all
five conductors, in
[`../../quenching-align-and-update-all/references/convergence.md`](../../quenching-align-and-update-all/references/convergence.md).
Cite it; never restate it here.

The workspace facts (layout, plan artifact graph, `specs.py` surface) live in
[`../../quenching-specs-develop/references/spec-driven.md`](../../quenching-specs-develop/references/spec-driven.md);
the conformance codes Stage 1 works from live in
[`../../quenching-specs-align/references/conformance.md`](../../quenching-specs-align/references/conformance.md).

## The pass pipeline

A **pass** runs three stages as a dependency chain. As in the `docs/` front, the order is not
cosmetic — each stage's output is the next stage's input:

| # | Stage skill | Concern | Why here in the order |
| --- | --- | --- | --- |
| 1 | `quenching-specs-align` | **structure** | Nothing can be listed, validated, or archived in a workspace that is malformed. Align scaffolds, applies `specs.py doctor`'s declared repairs, canonicalizes plan and archive names, seeds and stamps `backlog/`, regenerates its zone, migrates a legacy `openspec/` workspace, and clears any shadow copies. Everything downstream assumes a `doctor`-clean workspace. |
| 2 | `quenching-specs-archive` | **retire completed work** | The front's real content stage, and the plan↔OKF bridge: archiving a complete plan distils the durable knowledge it produced into `docs/`. Runs before triage so the backlog is ranked against what is actually still open. **Each archive is its own confirmation** ([convergence.md](../../quenching-align-and-update-all/references/convergence.md) §What it NEVER covers) — it is irreversible in the sense that matters: the spec leaves `ready/`, and its `outcome:` is a claim only the human can make. |
| 3 | `quenching-specs-triage` | **sweep stages + discoveries** | Sweeps the backlog by derived stage AND resolves every active spec's `## Discoveries`. After Stage 2, because an archived spec's discoveries are exactly the ones that must not be lost. |

The pipeline is **three stages, not four** — there is no separate spec store, so there is no
`sync-specs` stage: a spec writes its durable rule directly into `docs/standards/` as it is built,
and the archive distils the rest. Re-validation is implicit: Stage 1 runs `specs.py doctor` +
`validate` as its own verify step, and the conductor re-runs them in its re-assessment. A stage
the assessment found empty is **skipped** this pass.

**Strictly serial, with one handoff.** Stage 2 changes what Stage 3 sees (an archived plan
removes the reason a task is still open), so the chain is serial. What this front shares with the
`docs/` front is the handoff: the conductor hands `quenching-specs-align` its Step 1 inventory, so
a pass does not pay for `doctor`, `validate`, and `list --json` twice — once in the conductor's
assessment and once inside align against an untouched disk.

**`status --json` is scoped, not per-plan.** It answers one question — is this plan complete
enough to archive — so it runs only for plans `list --json` already reports at full task progress.
A workspace with a dozen open plans should not pay a dozen JSON payloads per pass.

## Opportunity → skill routing table

The read-only assessment produces findings; each maps to exactly one owning stage. A finding with
**no** stage owner is a **per-item** or **unroutable** opportunity — surfaced, never auto-closed.

| Finding (read-only signal) | Owning stage | Auto-closed? |
| --- | --- | --- |
| `sp-no-workspace`, `sp-legacy-workspace`, `sp-doctor`, `sp-invalid-plan` (mechanical) | `quenching-specs-align` | Yes (a legacy fold's code-coupled renames gate individually) |
| `sp-plan-name`, `sp-archive-name`, `sp-task-slug` | `quenching-specs-align` | Yes (code-coupled renames gate individually) |
| `sp-backlog-missing`, `sp-index-frontmatter`, `sp-task-untyped`, `sp-zone-missing`, `sp-zone-stale` | `quenching-specs-align` | Yes |
| `sp-shadow-skill`, `sp-shadow-command` | `quenching-specs-align` | Yes (migration only) |
| `sp-plan-complete` — every artifact `done`, all tasks `- [x]` | `quenching-specs-archive` | Yes — **one OK per plan** |
| `sp-backlog-untriaged`, invalid `priority` value | `quenching-specs-triage` | Yes |
| `sp-plan-blocked` — an artifact stuck `blocked` | *(surface → `quenching-specs-develop`)* | **No** — revising artifacts is authoring; reported |
| `sp-plan-stale` — old `lastModified`, unfinished tasks | *(surface → `quenching-specs-develop` / `quenching-specs-archive` / `quenching-specs-archive`)* | **No** — stale is not a defect; reported with its age, and abandonment is never inferred from one |
| `sp-ledger-orphan` — a ledger row naming a plan that no longer exists | *(surface — a hand fix)* | **No** — the archive/ record is curated by hand, never regenerated |
| `sp-shadow-diverged` — a locally customized shadow copy | *(kept in place)* | **No** — flagged and kept, never deleted |
| A captured spec that is done but nobody said so | *(kept in place)* | **No** — completion is stated, never inferred |

The rightmost column is the **anti-fabrication boundary** for this front: the conductor closes
only what a sweep can close deterministically. Authoring a proposal, revising a design, writing a
standard, or deciding a plan is abandoned all need a human, and all are **surfaced**.

## What this front's conductor never does

Lines it must not cross, inherited from the skills it conducts:

- **Never proposes or implements.** `quenching-specs-develop`, `quenching-specs-apply`,
  `quenching-specs-from-claude`, and `quenching-specs-explore` are per-item skills driven by
  human intent — a conducted pass has no fresh human input, so a captured spec never becomes a plan
  here, and no `## Tasks` checkbox is ever ticked by this loop.
- **Never infers completion.** A plan is archivable only when `specs.py status` reports every
  artifact `done` and every task `- [x]`. A task leaves the backlog only when a human says it is
  done ([`quenching-specs-triage`](../../quenching-specs-triage/SKILL.md) doctrine).
- **Never abandons.** `quenching-specs-archive` is the third exit a plan can take, and the
  only one no signal can justify: age, a blocked artifact, and an untouched branch are all
  evidence, never a decision. The conductor reports `sp-plan-stale` with its age and names
  `/specs:archive` — it never invokes it, under any authorization.
