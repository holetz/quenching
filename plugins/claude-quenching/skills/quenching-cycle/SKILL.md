---
name: quenching-cycle
description: >-
  Drives a repository's knowledge surface to OKF convergence by running the plugin's
  sweep skills — quenching-align, then quenching-memory-to-docs, then quenching-harness,
  then quenching-knowledge-scan — as a dependency pipeline, pass after pass, until a full
  pass changes nothing (a fixpoint). Use when the user asks to "run the full quenching
  cycle", "loop the skills until the knowledge base is done", "exhaust the OKF
  improvement opportunities", "drive the repo to OKF convergence", "run all the quenching
  skills in a loop", "keep aligning and capturing until nothing's left", or "auto-run
  align/memory/harness/glossary end to end". ONE OK at cycle start authorizes the whole
  run (code-coupled items still gate individually); each pass: one read-only assessment,
  the applicable stages run in order with plans narrated,
  re-assess; stops at the fixpoint (every stage empty AND the validator clean), a pass
  cap, or a no-progress guard — reporting residue instead of spinning. Not for: a single
  skill in isolation → invoke it directly; per-item skills (insert / knowledge /
  glossary) are stage tools, not loop stages.
when_to_use: >-
  running align → memory-to-docs → harness → knowledge-scan pass after pass until the
  repo reaches an OKF fixpoint. The orchestration layer over the other skills; a single
  skill in isolation is invoked directly.
allowed-tools: Read, Grep, Glob, Bash, Write, Edit, Task, Skill
---

# quenching-cycle — drive the repo to OKF convergence, pass by pass

The conductor. It runs the plugin's **sweep/structural** skills as a dependency pipeline, one
pass at a time, re-assesses after each pass, and loops until a full pass changes **nothing** and
the validator is clean — a fixpoint. It never edits a concept doc, a variant folder, or a harness
file itself: every change is made by the sub-skill it invokes, under that sub-skill's own
doctrine. The cycle only **assesses, orders, gates, and repeats**.

The pass pipeline, the opportunity→skill routing table, and the convergence contract live in
[references/cycle.md](references/cycle.md). The `type` vocabulary and conformance rules are shared
with `quenching-align` ([../quenching-align/references/taxonomy.md](../quenching-align/references/taxonomy.md),
[.../conformance.md](../quenching-align/references/conformance.md)); the executable checker is
`${CLAUDE_PLUGIN_ROOT}/assets/hooks/okf-validate.py`.

## Doctrine

- **Convergence to a fixpoint, not a single run.** Inherits the plugin's *convergence, not
  accommodation*: the cycle ends when a full pass finds nothing left to do, **not** after a fixed
  count of passes. Every sub-skill is idempotent on a converged repo — `quenching-align` finds no
  variants, `quenching-memory-to-docs` finds no undrained memory, `quenching-harness` finds a thin
  harness, `quenching-knowledge-scan` finds no unlisted terms — so a pass where **every** stage
  reports "nothing to do" **and** the validator's structural WARNs are all clear **is** the fixpoint.
- **Conduct, never reimplement.** The cycle sequences and gates; it does not re-derive a stage's
  logic. If a stage's behavior must change, change the sub-skill, not the cycle. This keeps ONE
  authority per concern — the same reason `quenching-insert` delegates the glossary tail step
  rather than re-encoding it.
- **One OK per cycle; the cycle run is the unit.** The gate runs ONCE, before Pass 1: present
  the initial assessment (which stages have work, in counts) and ask for the OK that authorizes
  up to the pass cap of passes, under the cycle-authorization contract in
  [references/cycle.md](references/cycle.md) — later passes run without a gate, narrating their
  plan. The authorization absorbs each stage's routine plan pause; it never absorbs a
  **code-coupled** item: a rename inside `quenching-align`/`quenching-harness` whose blast
  radius reaches product code still surfaces as **its own** confirmation, always — the
  sub-skill enforces that and the cycle must not suppress it.
- **Order is a dependency pipeline.** Structure → content → glossary → validation:
  `quenching-align` first (nothing can be listed into a tree that isn't there), then the two
  content feeders `quenching-memory-to-docs` and `quenching-harness` (they move facts in from the
  two out-of-band stores — project memory and the harness files), then `quenching-knowledge-scan`
  (a glossary swept before content lands misses terms), then re-validate. Never run a later stage
  before an earlier one.
- **Per-item skills are stage tools, not stages.** `quenching-insert` / `quenching-knowledge` /
  `quenching-glossary` each act on **one** item a human states, and the cycle has **no** fresh
  human input per pass — so they are not loop stages. They are the tools the sweep stages already
  delegate to (`quenching-harness` MOVEs a durable fact via `quenching-insert`; a coverage-ledger
  deferral is an `quenching-insert` opportunity). The cycle **surfaces** such content gaps in its
  report; it never fabricates content to close them (anti-fabrication, inherited from every stage).
- **Idempotence is the stop signal; never spin.** A **pass cap** (default 5) and a **no-progress
  guard** bound the loop: a pass that changed nothing but left validator findings is
  **non-convergent residue** — stop and report it, do not re-run the same empty pass. Silent
  non-convergence is a bug.

## Workflow (one cycle OK → assess → pass → re-assess → loop)

### 1. Preflight — is there a bundle to cycle?
Resolve the bundle root (`docs/` or the repo's variant). Read the baseline read-only: run
`okf-validate.py <docs> --json`, note which homes apply, whether the project's memory dir
(`~/.claude/projects/<cwd>/memory/`) holds files, and which harness files (`CLAUDE.md`,
subfolder `CLAUDE.md`, `AGENTS.md`) exist. If **no** OKF bundle exists at all (no `index.md` /
`log.md` / `okf_version`), that is expected — the first pass's `quenching-align` stage installs it.

### 2. Assess the pass (read-only) — build the opportunity list
Delegate the assessment to **one read-only `Task` sub-agent** (`model: sonnet`, `effort: low`)
that runs `okf-validate.py <docs> --json`, inventories the memory dir, the harness files, and the
glossary, and returns only the compact opportunity table below — this keeps the orchestrator's
context roughly constant across passes instead of growing by one full survey per pass. Sonnet,
not haiku, deliberately: a false "nothing to do" ends the loop early and breaks the convergence
contract. Without writing, survey each sweep stage's input and map every finding to its owning
skill via the routing table in [references/cycle.md](references/cycle.md):
- **align** — variant folder names, missing applicable homes, un-stamped/mis-stamped frontmatter,
  prefix-clusters to fold, non-English slugs to translate, and the validator's
  `dir-no-index` / `index-broken-link` / `index-orphan` WARNs + coverage-ledger deferrals.
- **memory-to-docs** — undrained facts in the project's memory dir.
- **harness** — a **fat** harness (durable knowledge inlined in `CLAUDE.md`/`AGENTS.md` that
  belongs in a home) or a broken/lying pointer.
- **knowledge-scan** — repo-specific terms already in the bundle but absent from `knowledge/glossary.md`.
If **every** stage is empty **and** the validator is clean → already converged, skip to Step 6.

### 3. Present the CYCLE plan → gate on ONE OK (once, before Pass 1)
Runs once per cycle, not per pass. Show, in pipeline order, which stages have work and what each
will touch — **counts and scope, not full diffs** (each sub-skill still presents its own
detailed plan, as narration, when it runs). State explicitly: *"this authorizes up to <pass cap>
passes running the stages below; any item that touches product code still pauses for its own
confirmation, always."* Wait for **one** OK — it grants the cycle-authorization contract
([references/cycle.md](references/cycle.md)) for the whole run; it does **not** pre-authorize
the sub-skills' code-coupled items. Later passes skip this step and only narrate their plan.

### 4. Run the pass — invoke each applicable stage, in order
Invoke the sub-skills via the **Skill** tool in dependency order, **skipping** any stage the
assessment found empty and declaring the cycle-authorization mode to each
([references/cycle.md](references/cycle.md) §contract). When BOTH content feeders (stages 2 and
3) have work this pass, use the parallel-prep flow (cycle.md §Parallel prep): dispatch the
read-only harness-discovery `Task` agent in the background once stage 1 completes, run stage 2
inline, then hand stage 3 the pre-collected table plus stage 2's created-docs list for its
staleness delta-recheck — writes stay one stage at a time, always:
1. `quenching-align` — converge structure, regenerate listings, validate.
2. `quenching-memory-to-docs` — drain project memory into its homes, clear each migrated memory.
3. `quenching-harness` — thin `CLAUDE.md`/`AGENTS.md`, MOVE durable knowledge into homes.
4. `quenching-knowledge-scan` — backfill `knowledge/glossary.md` from the whole bundle.
Each runs under its own doctrine, its own plan, and its own confirmation for code-coupled items.
Record what each stage reports it changed (for the convergence decision and the final report).

### 5. Re-assess → decide (loop or stop)
Re-run the Step 2 read-only assessment. Then:
- **Pass changed something** → run the next pass (back to Step 4) under the same authorization —
  no new OK; narrate the new pass's stages and counts. A fresh assessment may
  surface **follow-on** work the prior pass created (e.g., `quenching-harness` MOVEd a fact that
  `quenching-knowledge-scan` should now index; `quenching-align` relocated a doc that shifted an
  index) — this is why the loop re-assesses rather than assuming one pass suffices.
- **Pass changed nothing AND validator clean** → **converged.** Go to Step 6.
- **Pass changed nothing BUT findings remain** → **non-convergent residue** (something the cycle
  cannot auto-close: a per-item content gap, an unroutable harness fact, a deferred sub-standard).
  Stop; do not spin. Report the residue in Step 6.
- Respect the **pass cap** (default 5): if reached before convergence, stop and report what remains.

### 6. Report + one cycle log entry
Summarize the whole cycle: N passes, what each stage did across all passes, the final validator
state, and — explicitly — the opportunities the cycle **deliberately did not auto-close** (per-item
content needing human input, unroutable facts, deferred sub-standards), so nothing is silently
dropped. Append **one** summarizing entry to `docs/log.md` per **Appending to `log.md`** in
[../quenching-insert/references/homes.md](../quenching-insert/references/homes.md):
`**Update**: [Cycle](/docs/index.md) — converged in N passes
(align/memory/harness/glossary) ; M opportunities deferred to <skill>`. Self-check the entry
against [../quenching-align/references/conformance.md](../quenching-align/references/conformance.md).

## Invariants to never violate
- Never author content to close an opportunity that needs human input — **surface** it, never
  fabricate. The cycle only runs the sweep stages; it never invents a standard, a concept, or a term.
- Never suppress a sub-skill's **code-coupled** confirmation. The cycle's single upfront OK
  absorbs the stages' routine plan pauses (cycle.md §contract) — it never absorbs a
  code-coupled item, and never widens to product code.
- Never let two stages write `docs/` concurrently — parallel prep is read-only; writes are one
  stage at a time (cycle.md §Parallel prep).
- Never reimplement a stage's logic in the cycle — **invoke** the sub-skill via the Skill tool.
- Never run stages out of dependency order (structure → content → glossary → validate).
- Never loop past the pass cap, and never re-run a no-progress pass — stop and report the residue.
- Never treat validator **exit 0** alone as converged — the structural-integrity WARNs
  (`dir-no-index` / `index-broken-link` / `index-orphan`) are must-fix; read them from `--json`.
