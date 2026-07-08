# The cycle — pipeline, routing, and the convergence contract

The reference `quenching-cycle` reads. It fixes three things the SKILL.md summarizes: the **pass
pipeline** (which stages run, in what order, and why), the **opportunity → skill routing table**
(how a read-only finding becomes a stage invocation), and the **convergence contract** (the exact
condition that ends the loop, and the guards that keep it from spinning).

## The pass pipeline

A **pass** runs the four sweep/structural skills as a dependency chain. The order is not
cosmetic — each stage's output is the next stage's input:

| # | Stage skill | Concern | Why here in the order |
| --- | --- | --- | --- |
| 1 | `quenching-align` | **structure** | Nothing can be filed, listed, or validated into a tree that isn't there. Align scaffolds homes, migrates variants, stamps frontmatter, regenerates every `index.md`, and runs the checker. Everything downstream assumes an aligned bundle. |
| 2 | `quenching-memory-to-docs` | **content in from memory** | The project's Claude Code memory is one of two out-of-band stores of durable facts. Drain it into homes **before** the glossary sweep, so terms it introduces are in the bundle when Stage 4 reads. |
| 3 | `quenching-harness` | **content in from the harness** | `CLAUDE.md`/`AGENTS.md` are the other out-of-band store. Harness MOVEs inlined durable knowledge into homes (delegating each MOVE to `quenching-insert`), leaving thin pointers. Runs after memory so both content feeders finish before the glossary sweep. |
| 4 | `quenching-knowledge-scan` | **glossary from the whole bundle** | Now the bundle is structurally sound and both feeders have landed their content, sweep the **complete** bundle for repo-specific terms and backfill `knowledge/glossary.md`. Swept earlier, it would miss terms Stages 2–3 were still importing. |

Re-validation is implicit: Stage 1 runs `okf-validate.py` as its own Step 5, and the cycle
re-runs the checker in its re-assessment (SKILL.md Step 5). A stage the assessment found empty is
**skipped** this pass — the chain is "each applicable stage in order," not "all four every pass."

### Parallel prep: overlap harness discovery with the memory drain

When the assessment finds work for **both** content feeders in the same pass (Stages 2 AND 3
non-empty), the cycle overlaps Stage 3's read-only prefix with Stage 2's execution — plan in
parallel, write in series:

1. Stage 1 (`quenching-align`) completes first, as always.
2. The cycle dispatches **one read-only `Task` sub-agent in the background** (`model: sonnet` —
   MOVE/KEEP classification is real judgment, the same rationale as the assessment agent)
   instructed to execute steps 1–4 of `quenching-harness/SKILL.md` **as written there**
   (inventory, unit parse, classification, blast-radius sweep) and return the draft
   `file → unit → verdict → destination` table. The logic stays in its owner; the cycle only
   runs the read-only prefix ahead of schedule.
3. In parallel, the orchestrator runs `quenching-memory-to-docs` to completion, inline.
4. The cycle then invokes `quenching-harness`, handing it the pre-collected table **plus the
   list of docs Stage 2 just created**. Harness runs its **staleness delta-recheck** before
   writing: a doc Stage 2 landed can flip a unit's verdict from MOVE to **DEDUPE** (the fact
   now has a doc) — re-verify (a cheap `Grep` for coverage) only the units whose home/subject
   intersects the new docs; the rest of the table stands.
5. **Writes to `docs/` are one stage at a time, always** — harness's writes start only after
   memory-to-docs' writes have finished. Two stages read-modify-writing the same shared files
   (a home's `index.md`, `docs/log.md`, `knowledge/glossary.md`) is a race with no lock; the
   serial-write rule is an invariant, not an optimization choice.

When only ONE feeder has work, run it in the normal serial flow — dispatching a discovery agent
with nothing to overlap only costs tokens. The stages' own internal fan-outs (memory slice
classification, knowledge-scan home slices) are unchanged.

## Opportunity → skill routing table

The read-only assessment (SKILL.md Step 2) produces findings; each maps to exactly one owning
skill. A finding with **no** sweep-stage owner is a **per-item** or **unroutable** opportunity —
surfaced in the report, never auto-closed.

| Finding (read-only signal) | Owning stage | Auto-closed by the cycle? |
| --- | --- | --- |
| Variant folder name (`docs/arquitetura/`), missing applicable home | `quenching-align` | Yes |
| Un-stamped / mis-stamped frontmatter, `summary:`→`description:`, enum drift | `quenching-align` | Yes |
| Prefix-cluster to fold (`nomenclatura-*.md`), non-English slug to translate | `quenching-align` | Yes |
| `dir-no-index` / `index-broken-link` / `index-orphan` (validator WARN) | `quenching-align` | Yes |
| Undrained facts in `~/.claude/projects/<cwd>/memory/` | `quenching-memory-to-docs` | Yes |
| Fat harness — durable knowledge inlined in `CLAUDE.md`/`AGENTS.md` | `quenching-harness` | Yes (MOVE, via `quenching-insert`) |
| Broken / lying harness pointer | `quenching-harness` | Yes |
| Repo-specific term in the bundle, absent from `knowledge/glossary.md` | `quenching-knowledge-scan` | Yes |
| Coverage-ledger deferral — a candidate sub-standard not yet written | *(surface → `quenching-insert`)* | **No** — needs human-provided evidence; reported |
| A generic concept / decision / term a human has NOT yet stated | *(surface → `quenching-knowledge`/`-insert`/`-glossary`)* | **No** — no fresh human input this pass; reported |
| `user` memory, secret, or unroutable harness fact | *(kept in place)* | **No** — flagged and kept, never deleted |

The rightmost column is the anti-fabrication boundary: the cycle closes only what a **sweep** can
close deterministically from what the repo already contains. Content that requires a human to
state something new is **surfaced**, never invented.

## The cycle-authorization contract

The cycle asks for ONE human confirmation, at cycle start, that authorizes the entire run — up
to the pass cap or convergence. This section is the contract's single normative home: the four
stage skills cite it (each carries one exception sentence pointing here) and never restate it.

**What the authorization covers** — every routine write a stage performs: frontmatter stamps,
new concept docs, index/log/glossary entries, align's routine doc/folder renames, variant
migrations, and the deletions those migrations require, memory migration + deletion (after its
write-then-verify self-check), harness unit cuts (after theirs) — as long as it touches no
product code.

**What it NEVER covers** — any rename or edit whose blast radius reaches **product code** (a
path constant, an import, a docstring). A code-coupled item gates individually, always, exactly
as when the stage runs standalone. After the initial OK this is the only possible stop.

**What it does not change** — the stages' safe-write invariants (write-then-verify-then-delete
for memory, write-then-verify-then-cut for harness) do not depend on who authorized the run and
remain in force. Scope surprises do not re-gate: a later pass discovering more work than the
preview estimated proceeds under the same authorization, bounded by the pass cap and the
stages' own invariants.

**How the cycle signals the mode** — it declares, in the invocation of each stage: *"Running
under quenching-cycle authorization granted at cycle start — skip your plan-confirmation pause;
present your plan as narration and execute; code-coupled items still gate individually."* A
stage invoked WITHOUT this declaration (standalone) keeps its normal plan → OK gate.

**Narration replaces the gate, not the plan** — a cycle-authorized stage still presents its
full plan table before writing; the user watching the session sees everything and types
nothing.

## The convergence contract

Let a pass be **empty** when every applicable stage reports "nothing to do." Let the validator be
**clean** when `okf-validate.py <docs> --json` exits 0 **and** reports zero `dir-no-index`,
`index-broken-link`, and `index-orphan` (these are WARN — exit 0 alone does not prove them clear;
read the findings).

- **Converged (stop, success):** a pass is **empty** *and* the validator is **clean**. This is the
  fixpoint. Report and write the cycle log entry.
- **Progress (loop):** the pass changed something. Re-assess and run another pass — a change can
  create follow-on work (a MOVE that needs glossary indexing, a relocation that shifts an index).
- **Residue (stop, report):** the pass was **empty** but the validator is **not clean**, or only
  non-auto-closable findings remain (per-item gaps, unroutable facts, deferred sub-standards).
  Stop — re-running an empty pass cannot clear it. Report the residue as deferred opportunities.

**Guards against spinning:**
- **Pass cap** — default **5**. If reached before convergence, stop and report what remains; do
  not raise the cap silently. A well-aligned repo converges in 1–2 passes; needing more signals a
  stage that keeps producing follow-on work, worth reporting.
- **No-progress guard** — never run a pass identical to one that just changed nothing. An empty
  pass with residual findings is a **stop** condition, not a reason to iterate.
- **Never widen scope to force convergence** — the cycle does not fabricate content, relax a
  sub-skill's confirmation, or auto-close a per-item opportunity to make the numbers reach zero.
  A residue reported honestly beats a fixpoint reached by cutting a corner.

## Relationship to the per-item skills

`quenching-insert`, `quenching-knowledge`, and `quenching-glossary` are **not** pipeline stages —
they act on ONE item a human states, and a cycle pass has no fresh human input. They enter the
cycle only **indirectly**, as the tools a sweep stage delegates to (`quenching-harness` → MOVE via
`quenching-insert`; a fresh capture during a pass a human happens to make). When the assessment
finds a gap only a per-item skill could fill, the cycle **names the gap and the skill that would
close it** in its report — the user then invokes that skill with the missing input, and a
subsequent `quenching-cycle` picks the change up on its next sweep. The whole-bundle glossary
counterpart (`quenching-knowledge-scan`) IS a stage; the single-term one (`quenching-glossary`) is
not — same split the plugin draws everywhere between a sweep and a capture.
