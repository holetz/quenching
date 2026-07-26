# The `docs/` front's cycle — pipeline and routing

The reference `quenching-docs-align-and-update` reads. It fixes the two things specific to the
**`docs/` front**: the **pass pipeline** (which stages run, in what order, and why) and the
**opportunity → skill routing table** (how a read-only finding becomes a stage invocation).

Everything that is **not** front-specific — the cycle-authorization contract, the convergence
condition, the anti-spin guards, and why per-item skills are never stages — lives once, for all
five conductors, in
[`../../quenching-align-and-update-all/references/convergence.md`](../../quenching-align-and-update-all/references/convergence.md).
Cite it; never restate it here.

## The pass pipeline

A **pass** runs the four sweep/structural skills as a dependency chain. The order is not
cosmetic — each stage's output is the next stage's input:

| # | Stage skill | Concern | Why here in the order |
| --- | --- | --- | --- |
| 1 | `quenching-docs-align` | **structure** | Nothing can be filed, listed, or validated into a tree that isn't there. Align scaffolds homes, migrates variants, stamps frontmatter, regenerates every `index.md`, and runs the checker. Everything downstream assumes an aligned bundle. |
| 2 | `quenching-docs-import-memory` | **content in from memory** | The project's Claude Code memory is one of two out-of-band stores of durable facts. Drain it into homes **before** the glossary sweep, so terms it introduces are in the bundle when Stage 4 reads. |
| 3 | `quenching-docs-harness` | **content in from the harness** | `CLAUDE.md`/`AGENTS.md` are the other out-of-band store. Harness MOVEs inlined durable knowledge into homes (delegating each MOVE to `quenching-docs-add`), leaving thin pointers. Runs after memory so both content feeders finish before the glossary sweep. |
| 4 | `quenching-docs-glossary-backfill` | **glossary from the whole bundle** | Now the bundle is structurally sound and both feeders have landed their content, sweep the **complete** bundle for repo-specific terms and backfill `knowledge/glossary.md`. Swept earlier, it would miss terms Stages 2–3 were still importing. |

Re-validation is implicit: Stage 1 runs `okf-validate.py` as its own Step 5, and the cycle
re-runs the checker in its re-assessment (SKILL.md Step 5). A stage the assessment found empty is
**skipped** this pass — the chain is "each applicable stage in order," not "all four every pass."

### Parallel prep: overlap harness discovery with the memory drain

When the assessment finds work for **both** content feeders in the same pass (Stages 2 AND 3
non-empty), the cycle overlaps Stage 3's read-only prefix with Stage 2's execution — plan in
parallel, write in series:

1. Stage 1 (`quenching-docs-align`) completes first, as always.
2. The cycle dispatches **one read-only `Task` sub-agent in the background** (`model: sonnet` —
   MOVE/KEEP classification is real judgment, the same rationale as the assessment agent)
   instructed to execute steps 1–4 of `quenching-docs-harness/SKILL.md` **as written there**
   (inventory, unit parse, classification, blast-radius sweep) and return the draft
   `file → unit → verdict → destination` table. The logic stays in its owner; the cycle only
   runs the read-only prefix ahead of schedule.
3. In parallel, the orchestrator runs `quenching-docs-import-memory` to completion, inline.
4. The cycle then invokes `quenching-docs-harness`, handing it the pre-collected table **plus the
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
| Variant folder name (`docs/arquitetura/`), missing applicable home | `quenching-docs-align` | Yes |
| Un-stamped / mis-stamped frontmatter, `summary:`→`description:`, enum drift | `quenching-docs-align` | Yes |
| Prefix-cluster to fold (`nomenclatura-*.md`), non-English slug to translate | `quenching-docs-align` | Yes |
| `dir-no-index` / `index-broken-link` / `index-orphan` (validator WARN) | `quenching-docs-align` | Yes |
| Undrained facts in `~/.claude/projects/<cwd>/memory/` | `quenching-docs-import-memory` | Yes |
| Fat harness — durable knowledge inlined in `CLAUDE.md`/`AGENTS.md` | `quenching-docs-harness` | Yes (MOVE, via `quenching-docs-add`) |
| Broken / lying harness pointer | `quenching-docs-harness` | Yes |
| Repo-specific term in the bundle, absent from `knowledge/glossary.md` | `quenching-docs-glossary-backfill` | Yes |
| `resource-unresolved` — a `resource` entry matching nothing on disk | *(surface → `quenching-docs-add` to restamp)* | **No** — only a human knows what the doc now governs; reported with the entry |
| `resource-self` — the doc sits inside its own declared scope | *(surface → `quenching-docs-add` to restamp)* | **No** — narrowing a scope is a judgement, and a bundle aggregate is legitimate; reported |
| `glossary-broken-link` — a glossary entry points at a deleted doc | *(surface → `quenching-docs-define`)* | **No** — the backfill stage ADDS missing terms, it never prunes a dead one; reported |
| `stale-doc` — `timestamp` predates the last commit touching its `resource` | *(surface → the doc's owner)* | **No** — advisory; code may have moved under a rule that did not change |
| Coverage-ledger deferral — a candidate sub-standard not yet written | *(surface → `quenching-docs-add`)* | **No** — needs human-provided evidence; reported |
| A generic concept / standard / term a human has NOT yet stated | *(surface → `quenching-docs-learn`/`-insert`/`-glossary`)* | **No** — no fresh human input this pass; reported |
| `user` memory, secret, or unroutable harness fact | *(kept in place)* | **No** — flagged and kept, never deleted |

The rightmost column is the anti-fabrication boundary: the cycle closes only what a **sweep** can
close deterministically from what the repo already contains. Content that requires a human to
state something new is **surfaced**, never invented.

