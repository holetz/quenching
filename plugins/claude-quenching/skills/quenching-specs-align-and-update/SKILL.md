---
name: quenching-specs-align-and-update
description: >-
  Aligns AND updates the specs/ front: runs quenching-specs-align, then
  quenching-specs-plan-archive (each complete plan, its own confirmation), then
  quenching-specs-backlog-triage as a THREE-STAGE dependency pipeline, pass after pass, until a
  full pass changes nothing and specs.py doctor/validate are clean. Use when the user asks to
  "align and update specs", "bring the specs workspace up to date", "close out the finished
  plans and re-rank the backlog", "run the full specs cycle", or "tidy specs end to end".
  Where quenching-specs-align only fixes STRUCTURE and merely REPORTS the cycle actions, this
  one DRIVES them: it archives what specs.py reports complete (distilling durable knowledge into
  docs/) and triages the inbox. ONE OK at run start authorizes the run; each archive still
  confirms on its own, and so does any rename reaching product code. Never proposes, never
  implements, never infers completion. Not for: structure only, one pass → quenching-specs-align;
  the docs/ front → quenching-docs-align-and-update; the .claude/ front →
  quenching-skill-align-and-update; all three → quenching-align-and-update-all.
when_to_use: >-
  aligning AND updating the specs/ front — align → archive → triage, pass after pass to a
  fixpoint. Structure-only in one pass is quenching-specs-align; the other fronts have their
  own align-and-update; all three at once is quenching-align-and-update-all.
allowed-tools: Read, Grep, Glob, Bash(python3:*), Bash(py:*), Bash, Write, Edit, Task, Skill
user-invocable: false
---

# quenching-specs-align-and-update — align AND update the `specs/` front, pass by pass

The **`specs/` front's conductor**, peer of `quenching-docs-align-and-update` (`docs/`) and
`quenching-skill-align-and-update` (`.claude/`). The name says what separates it from
`quenching-specs-align`: align fixes **structure** in one pass and deliberately only **reports**
the cycle actions it finds; this conductor **drives** them — the complete plan gets archived
(which distils its durable knowledge into `docs/`), and the inbox gets ranked — looping until
nothing is left.

The pass pipeline and the opportunity→skill routing table live in
[references/cycle.md](references/cycle.md); the cycle-authorization contract, the convergence
condition, and the anti-spin guards are shared with every conductor and live in
[../quenching-align-and-update-all/references/convergence.md](../quenching-align-and-update-all/references/convergence.md).
The workspace facts live in
[../quenching-specs-plan-propose/references/spec-driven.md](../quenching-specs-plan-propose/references/spec-driven.md)
and the conformance codes in
[../quenching-specs-align/references/conformance.md](../quenching-specs-align/references/conformance.md).

## Doctrine

- **Three stages, not four.** There is no separate spec store, so there is no sync stage: a plan
  writes its durable rule directly into `docs/standards/` as it is built, and the archive distils
  the rest. The pipeline is `quenching-specs-align` → `quenching-specs-plan-archive` →
  `quenching-specs-backlog-triage` ([cycle.md](references/cycle.md) §pipeline).
- **Convergence to a fixpoint, not a single run.** The front is converged when a full pass finds
  nothing to do **and** `specs.py doctor` + `specs.py validate` are clean **and** the backlog
  check (`okf-validate.py specs/backlog --listing-root`) is clean. Every stage is idempotent on a
  converged workspace, so an empty pass **is** the fixpoint.
- **Conduct, never reimplement.** The conductor sequences, gates, and reports; it never renames a
  plan, distils a doc, or edits a task itself. If a stage's behavior must change, change that
  stage's skill.
- **One OK per run — except each archive.** The run gate fires once, before Pass 1, under the
  shared contract
  ([convergence.md](../quenching-align-and-update-all/references/convergence.md)
  §cycle-authorization). It absorbs the stages' routine plan pauses. It does **not** absorb a
  code-coupled rename, and it does **not** absorb an **archive**: moving a plan out of `specs/`
  is irreversible in the sense that matters, and a plan whose tasks are all checked may still be
  waiting on a deploy — so every archive is its own confirmation, with what it will distil shown.
- **Order is a dependency pipeline.** structure → retire completed work → rank what remains
  ([cycle.md](references/cycle.md) §pipeline). Triage run before archive would rank tasks whose
  plans are already done.
- **Never propose, never implement, never infer completion.** `quenching-specs-plan-propose`,
  `quenching-specs-plan-apply`, and `quenching-specs-explore` are per-item skills driven by human
  intent — a conducted pass has no fresh human input. A plan is archivable only when `specs.py
  status` reports every artifact `done` and every task `- [x]`; a task leaves the backlog only
  when a human says it is done. Everything else is **surfaced**, never invented.
- **Never abandons.** `quenching-specs-plan-abandon` is the exit no signal can justify — age, a
  blocked artifact, and an untouched branch are evidence, never a decision. This loop reports
  `sp-plan-stale` with its age and names `/specs:plan:abandon`; it never invokes it.
- **Idempotence is the stop signal; never spin.** A pass cap (default 5) and a no-progress guard
  bound the loop. An empty pass with residual findings is **residue** — stop and report it, with
  the skill that owns each item.

## Workflow (one run OK → assess → pass → re-assess → loop)

### 1. Preflight — is there a workspace to cycle?
Resolve `specs.py` by the fallback in
[../quenching-specs-backlog-add/references/backlog-zone.md](../quenching-specs-backlog-add/references/backlog-zone.md)
§Resolving the tool (invoke via `python3`/`py`). Resolve the `specs/` root at the repo root; if
**neither** `specs/` nor a legacy `openspec/` exists, that is expected — Pass 1's Stage 1 offers
to scaffold. Note whether an OKF bundle exists (`docs/index.md` with `okf_version`) — without
one, Stage 2's distillation is out of scope and `quenching-docs-align` is suggested once.
**Done when:** the root is resolved (or its absence recorded) and nothing has been written.

### 2. Assess the pass (read-only) — build the opportunity list
Without writing, run `specs.py doctor`, `specs.py validate`, `specs.py list --json`; `Glob`
`specs/backlog/*.md` and read their frontmatter; `Glob` a legacy `openspec/` tree and the shadow
copies (`.claude/skills/openspec-*/SKILL.md`, `.claude/commands/opsx/*.md`) for a migration. Map
every finding to its owning stage via the routing table in
[references/cycle.md](references/cycle.md):
- **align** — the `sp-*` conformance codes (scaffold, migrate, doctor/validate, names, the
  `backlog/` inbox and its zone, shadow copies).
- **archive** — plans `specs.py status` reports complete (every artifact `done`, every task
  `- [x]`).
- **triage** — tasks with no `priority`, or a `priority` outside the enum.
Run `specs.py status --plan <n> --json` **only** for the plans `list --json` already shows at
full task progress — those are the archive candidates Stage 2 needs. A plan still
mid-implementation needs no status payload to be classified as "not this pass".
No sub-agent fan-out: the tool answers in one call and a backlog is small by nature — the
orchestrator reads everything itself. If **every** stage is empty **and** doctor/validate are
clean → already converged, skip to Step 6.
**Keep this inventory** — it is handed to Stage 1 verbatim in Step 4, and re-collected only after
a pass has written to disk.
**Done when:** every finding carries an owning stage or is marked report-only.

### 3. Present the RUN plan → gate on ONE OK (once, before Pass 1)
Show, in pipeline order, which stages have work and what each will touch — **counts and scope,
not full diffs** (each stage still presents its own plan as narration when it runs). List the
plans proposed for archiving **by name**, and state explicitly: *"this authorizes up to <pass
cap> passes running the stages below; each archive still asks separately, and any item touching
product code still confirms on its own."* Then, separately, the **report-only** findings
(`sp-plan-blocked`, `sp-plan-stale`, `sp-ledger-orphan`, `sp-shadow-diverged`) with their owning
skill. Wait for **one** OK. Later passes skip this step and only narrate.
**Done when:** the user has answered; declined → nothing written, run ends.

### 4. Run the pass — invoke each applicable stage, in order
Invoke the sub-skills via the **Skill** tool in dependency order, **skipping** any stage the
assessment found empty, and declaring the authorization mode verbatim per
[convergence.md](../quenching-align-and-update-all/references/convergence.md)
§cycle-authorization:
1. `quenching-specs-align` — converge structure, migrate a legacy workspace, seed/stamp the
   inbox, clear shadow copies, validate. **Hand it the Step 2 inventory** (per its Step 1
   §Supplied inventory) so it does not re-run `doctor`, `validate`, and `list --json` against a
   disk nothing has touched since.
2. `quenching-specs-plan-archive` — **once per complete plan, each with its own confirmation**;
   accept its OKF distillation pass.
3. `quenching-specs-backlog-triage` — rank what remains.
Never run two stages concurrently: Stage 2 changes what Stage 3 sees (an archived plan removes
the reason a task is still open). Record what each stage reports it changed.
**Done when:** every applicable stage has run or been skipped with a stated reason.

### 5. Re-assess → decide (loop or stop)
Re-run the Step 2 assessment — now the disk **has** changed, so the collection is real. Two
things are still not re-run: Stage 1 finished with its own `doctor` + `validate` verify, so reuse
those results unless a later stage wrote after them; and `status --json` stays scoped to the
plans `list --json` reports at full progress. Then:
- **Pass changed something** → run the next pass (back to Step 4) under the same authorization,
  narrating its stages. A fresh assessment surfaces follow-on work the prior pass created (an
  archive that freed a backlog task's reason to exist; a distillation that added `docs/` content).
- **Pass changed nothing AND doctor/validate clean** → **converged.** Go to Step 6.
- **Pass changed nothing BUT findings remain** → **residue.** Stop; do not spin.
- Respect the **pass cap** (default 5).
**Done when:** the loop has stopped for a stated reason.

### 6. Report + one log entry
Summarize: N passes, what each stage did across all passes, the final doctor/validate state, and
— explicitly — what the run **deliberately did not close** (blocked plans → `/specs:plan:update`,
stale plans → `/specs:plan:abandon`, ledger orphans, diverged shadow copies, declined archives),
each with its owning command. In a repo with an OKF bundle, append **one** entry to `docs/log.md`
per **Appending to `log.md`** in
[../quenching-docs-add/references/homes.md](../quenching-docs-add/references/homes.md):
`**Update**: [specs/](/specs/backlog/index.md) — aligned and updated in N passes
(align/archive/triage); M deferred`. Then run the backlog check in
[../quenching-specs-backlog-add/references/backlog-zone.md](../quenching-specs-backlog-add/references/backlog-zone.md)
§The on-write check (`okf-validate.py specs/backlog --listing-root`).
**Done when:** counts, residue, and the final state are reported and the entry is written.

## Invariants to never violate

- Never archive without that plan's **own** confirmation, and never archive a plan `specs.py
  status` does not report complete.
- Never propose a plan, implement a task, or tick a `tasks.md` checkbox — those need human intent
  this loop does not have.
- Never abandon a plan and never remove a backlog task the human has not said is done; never
  author a proposal, a design, or a standard.
- Never suppress a stage's code-coupled confirmation, and never widen the run to product code.
- Never run stages out of dependency order, and never run two concurrently.
- Never add a fourth (sync) stage — there is no separate spec store to sync into.
- Never loop past the pass cap, never re-run a no-progress pass — stop and report the residue.
- Never treat `specs.py validate` exit 0 alone as converged — the backlog validator run and the
  emptiness of every stage are part of the condition
  ([convergence.md](../quenching-align-and-update-all/references/convergence.md)).
- Never hand this SKILL.md `context: fork` — the run gate and every archive confirmation are
  mid-flow.
