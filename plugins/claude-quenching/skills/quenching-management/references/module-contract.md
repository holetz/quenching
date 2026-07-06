# The Dimension Module Contract — the uniform shape of a dimension unit

> **Back path:** [../SKILL.md](../SKILL.md) (agent roadmap) ·
> [dimensions-template.md](dimensions-template.md) (the 15 dimensions + transversal
> doctrine) · [README.md](README.md) (`references/` index).

The method runs as a **thin orchestrator that dispatches per-dimension modules**, not as
one monolithic pass. Each of the 15 dimensions is a **self-contained, independently
evolvable unit** with the **same uniform runtime shape** — so a dimension can be sharpened,
measured, or migrated in **one place** without touching the others, and the orchestrator
composes them without knowing their internals.

This file is the **single source of that shape**. The doctrine of *what* each dimension
detects/scores/remediates lives in its own file under
[dimensions/](dimensions/README.md); this file defines the **contract** every dimension
module honors when the orchestrator dispatches it.

## Where a module runs (the vehicle)

A dimension module is dispatched as a **per-dimension sub-agent** — the dim-7 home:
*isolated work in its own context, returns only a condensed summary, invoked by a sibling
skill* ([dimensions/dim-07-subagents.md](dimensions/dim-07-subagents.md)). This keeps a
**clean context per dimension** and adds **no trigger surface** to the target: the modules
are **not** 15 free-triggering skills (that would violate the dim-6 skill-surface-bloat /
trigger-collision doctrine — [dimensions/dim-06-skills.md](dimensions/dim-06-skills.md));
they are runtime units the orchestrator drives. The runner mold lives under
[../assets/agents/](../assets/agents/) (the read-only scan reuses
[../assets/agents/quenching-auditor.md](../assets/agents/quenching-auditor.md); an applying
module reuses/extends the writer discipline of
[../assets/agents/quenching-writer.md](../assets/agents/quenching-writer.md)).

> **Still an inert installer, not an active component.** The modules are the *method's*
> runtime units; they never become auto-discoverable native skills/hooks of this plugin
> (the second non-negotiable invariant). Portability and self-containment are unchanged: a
> module couples to no repo and to no external skill. Dispatching a writer-discipline
> sub-agent during a **derived-content** apply does **not** change this: it is a runtime unit
> the orchestrator drives, still copied from `assets/`, still coupled to no repo.

## The six parts every module honors

Each module has exactly one home — its own `dimensions/dim-NN-*.md` file — so an
improvement opportunity maps to a single place. The six parts:

1. **detect** — the adaptive greps for this dimension (the reuse block per dim in
   [detection-and-smells.md](detection-and-smells.md)). Run from the target root; Step 0
   has already derived the real paths.
2. **score** — the four-state assignment (**Present / Partial / Drifted / Absent**) with
   evidence `file:line` (the rule in [detection-and-smells.md](detection-and-smells.md)).
3. **apply** — the remediation, **driven to completion**, in one of **three regimes by
   dimension type**. This split is the method's core invariant — *derived description the
   method writes × human direction it drafts-for-ratification × structure it installs* — and
   this file is its single source:
   - **Derived-content** (dim 2 standards, incl. dim 13's writes into the standards home):
     the module **installs structure AND populates derived content** — it dispatches a
     sub-agent with the [quenching-writer](../assets/agents/quenching-writer.md) discipline to
     **mine the repo and write the standard**, every `current` rule anchored at `file:line`;
     anything not de-facto-proven enters as `authority: background` (a proposal, never
     asserted current). This is faithful transcription of what the code already does, not a
     direction call.
   - **Human-direction** (dim 3 vision, 10 memory, 12 boundary): the module **drafts** the
     text from observable signals (git history, README/goals, backlog/ADR) and **writes it
     labeled `authority: background` + a "DRAFT — pending human ratification" banner** into
     the home; it **never** marks it `current` and never claims it is ratified. A **human
     ratification gate** stands between the draft and any authoritative status (Step 6).
   - **Structural** (dim 1 the CLAUDE.md map file, dim 11 catalog): **structure-only** apply —
     install / migrate / re-stamp / regenerate the artifact; catalog generators are
     repo-specific (the method signals separation, does not carry them); the map stays a thin
     pointer, never a contract.
   Consent follows the operation model ([installation.md](installation.md),
   [lifecycle.md](lifecycle.md) §3): standing **`managed`** consent for the reversible,
   git-tracked reconcile classes; a **`generate-derived`** grant (enumerated, one OK) for
   writing derived content into **absent/empty** subjects; **per-item OK** for deletes,
   renames, code-coupled blast radius, rewriting an existing authored body, and the first
   install of a new payload; the **`draft-direction`** class always requires the ratification
   gate, never `managed`.
4. **verify** — after apply, **re-run this dimension's own `detect` block on the
   just-written output**. A **non-empty** result means the apply is **incomplete** — the
   module is **not "done"**: it loops (re-apply the missed items) or **flags loudly**,
   never reports success. This is the reforço: *"applied"* is a **claim that must pass its
   own greps**, not a side effect that is assumed to have worked. See «The verify gate»
   below.
5. **payload** — a pointer to the `assets/` artifact the module installs or drives
   (unchanged from the dimension's **Payload** field): a structure payload, the
   `quenching-writer` discipline (derived-content dims), or the `quenching-direction`
   discipline (human-direction dims 3/10/12 — drafts labeled `authority: background`,
   ratification-gated). Catalog (dim 11) carries no generator (repo-specific).
6. **return** — a **condensed** scorecard + apply-summary with `file:line` (the dim-7
   return contract, R9): the state per dimension, what was applied, and — after part 4 —
   whether verify is **clean** or which checks still fire. Never a dump of file contents.

## The verify gate (the reforço)

The gate closes the failure mode where *an install reports success while the written output
stayed non-canonical*. It is **mandatory for every applying module** and is the same idea
for all dimensions: **apply is complete only when the dimension's own detection is silent on
the output it just wrote.**

- **Run the dimension's own `detect` block** against the just-written files — the same
  greps the audit used, now pointed at the output. Any candidate the detect block lists is
  a **fail**, not a pass.
- A **mandatory-incomplete / OKF-non-conformant** standard (missing a mandatory key,
  or missing `type:`/`resource:`), a **variant folder name** left un-migrated, a
  **missing `README.md`/`CLAUDE.md` front-door**, an **`INDEX.md` without
  `<!-- BEGIN/END GENERATED -->` markers** (or out of sync with disk) — each is a verify
  **failure**, because each is exactly what the detect block would flag on a fresh audit.
- **Human-direction dimensions (3/10/12) verify the DRAFT, not a `current` claim** — their
  apply writes a **labeled draft** (`authority: background` + a "pending human ratification"
  banner) into the home; the gate checks that the draft is present and correctly labeled and
  that **nothing was promoted to `current`**. It never claims the direction is ratified —
  that stands behind the human gate (Step 6).
- The gate is **portable**: it re-uses the dimension's existing detection, so it adds no
  new hardcoded rule and stays inert where the dimension's detect block is inert.

The gate is **wired into the live workflow**, not only described here: every apply ends with
a canon re-check at [../SKILL.md](../SKILL.md) Step 5 and [installation.md](installation.md)
step 7, so an apply cannot be recorded as installed until its detection is silent on the
output — even before the dimension's full module has been migrated.

> **Verify ≠ a new detector.** It reuses part 1 (detect) pointed at the output. This keeps
> a single source of truth: sharpening the detect block automatically sharpens the gate.

## The orchestrator's use of the contract

The thin orchestrator ([../SKILL.md](../SKILL.md)) dispatches modules across the workflow
phases and never re-implements a module's internals:

- **audit** — dispatch each dimension's `detect → score`, aggregate the returns into one
  prioritized report (Step 4), modulated by the derived profile.
- **apply + verify** — dispatch each selected dimension's `apply → verify` under the consent
  mode, in the dimension's regime (derived-content **writes** · human-direction **drafts for
  ratification** · structural **installs**); a module that fails its verify gate is surfaced,
  not silently closed.
- **draft-human** — dims 3/10/12 only: draft direction from observable signals and write it
  as a labeled `authority: background` draft; the human ratification gate promotes it, the
  method never does (Step 6).
- **install-loop** — wire the recurring maintenance cycle once (Step 8).

The links keep the R28 orchestration contract (hook OBSERVES/PROPOSES · command/skill
APPLIES-with-OK · sub-agent returns a CONDENSED summary) and the R28 dual barrier (a human
OK on every mutating link; the runtime's deterministic sub-agent depth cap). The module is
the *sub-agent* link; it never mutates the base without the confirmation the operation model
requires.

## What the contract does not change

- **Report-first.** Audit still precedes apply; the report is still one prioritized document.
- **Human DIRECTION is never asserted as ratified truth.** A dim 3/10/12 apply may draft and
  write direction text, but only labeled `authority: background` pending human ratification;
  the verify gate never promotes it to `current`. Derived description (dim 2) is written
  directly, because it transcribes the repo's proven de-facto reality, not a direction call.
- **`docs/` names stay canonical.** A module's apply converges variant names to the
  canonical taxonomy ([docs-taxonomy.md](docs-taxonomy.md)); it does not preserve a variant
  as "repo convention wins" (that exception is scoped to skills/agents/hooks, never `docs/`
  names).
- **15 dimensions, not 16.** The module contract is the *shape* of a dimension, not a new
  dimension.
