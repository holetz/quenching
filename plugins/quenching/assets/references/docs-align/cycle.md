# The `docs/` front's cycle — pipeline and routing

The reference `/docs:align` reads for the two things specific to the **`docs/` front's loop**: the
**stage pipeline** (which stages run, in what order, and why) and the **finding → owning-command
routing table** (which findings the align closes itself, and which it can only surface).

Everything that is **not** front-specific lives elsewhere and is cited, never restated here: the
probe-before-inventory rule, the one-plan-one-OK model and the blast-radius procedure in
[`align-all/sweep-doctrine.md`](${CLAUDE_PLUGIN_ROOT}/assets/references/align-all/sweep-doctrine.md);
the cycle-authorization contract, the convergence condition and the anti-spin guards in
[`align-all/convergence.md`](${CLAUDE_PLUGIN_ROOT}/assets/references/align-all/convergence.md).

## The stage pipeline

A **pass** is a dependency chain, and the order is not cosmetic — each stage's output is the next
stage's input. Stage 1 is `/docs:align`'s own work; stages 2–4 are commands it invokes.

| # | Stage | Concern | Why here in the order |
| --- | --- | --- | --- |
| 1 | the align's own structural pass | **structure** | Nothing can be filed, listed, or validated into a tree that isn't there. Scaffold homes, migrate variants, stamp frontmatter, regenerate every `index.md`, run the checker. Everything downstream assumes an aligned bundle. |
| 2 | `/docs:import-memory` | **content in from memory** | The project's Claude Code memory is one of two out-of-band stores of durable facts. Drain it into homes **before** the glossary sweep, so terms it introduces are in the bundle when stage 4 reads. |
| 3 | `/docs:harness` | **content in from the harness** | `CLAUDE.md`/`AGENTS.md` are the other out-of-band store. Harness MOVEs inlined durable knowledge into homes (delegating each MOVE to `/docs:add`), leaving thin pointers. Runs after memory so both content feeders finish before the glossary sweep. |
| 4 | `/docs:glossary-backfill` | **glossary from the whole bundle** | Now the bundle is structurally sound and both feeders have landed, sweep the **complete** bundle for repo-specific terms and backfill `knowledge/glossary.md`. Swept earlier, it would miss terms stages 2–3 were still importing. |

**Stages 1–3 are probed; stage 4 is offered.** The align knows before it starts whether stages 1–3
have work — a validator exit code, a directory listing, one file read. Stage 4 has no such signal:
proving the glossary is complete costs the same whole-bundle sweep as backfilling it. So it is
gated on a free proxy (concept-doc count against glossary size, plus whether this pass created any
docs) and **offered** with its cost, once per run. Running it to find out would spend the exact
budget the probe rule exists to protect.

A stage the probe found empty is **skipped** this pass — the chain is "each applicable stage in
order", never "all four every pass". Re-validation is implicit: stage 1 ends by running
`okf-validate.py`, and the align re-probes in its loop decision.

### Parallel prep: overlap harness discovery with the memory drain

When both content feeders have work in the same pass (stages 2 AND 3 non-empty), overlap stage 3's
read-only prefix with stage 2's execution — plan in parallel, write in series:

1. Stage 1 completes first, as always.
2. Dispatch **one read-only `Task` sub-agent in the background** (`model: sonnet` — MOVE/KEEP
   classification is real judgment) instructed to execute steps 1–4 of `/docs:harness`
   **as written there** (inventory, unit parse, classification, blast-radius sweep) and return the
   draft `file → unit → verdict → destination` table. The logic stays in its owner; only its
   read-only prefix runs ahead of schedule.
3. In parallel, run `/docs:import-memory` to completion, inline.
4. Then invoke `/docs:harness`, handing it the pre-collected table **plus the list of docs stage 2
   just created**. Harness runs its **staleness delta-recheck** before writing: a doc stage 2
   landed can flip a unit's verdict from MOVE to **DEDUPE** (the fact now has a doc) — re-verify
   (a cheap `Grep` for coverage) only the units whose home/subject intersects the new docs; the
   rest of the table stands.
5. **Writes to `docs/` are one stage at a time, always** — harness's writes start only after the
   memory drain's writes have finished. Two stages read-modify-writing the same shared files (a
   home's `index.md`, `docs/log.md`, `knowledge/glossary.md`) is a race with no lock; the
   serial-write rule is an invariant, not an optimization choice.

When only ONE feeder has work, run it in the normal serial flow — dispatching a discovery agent
with nothing to overlap only costs tokens. The stages' own internal fan-outs (memory slice
classification, knowledge-scan home slices) are unchanged.

## Finding → owning-command routing table

The probe and the inventory produce findings; each maps to exactly one owner. A finding with **no**
stage owner is a **per-item** or **unroutable** opportunity — surfaced in the report, never
auto-closed. The rightmost column is also what the probe reads: a run whose only findings say
**No** has nothing to align and stops there.

| Finding (read-only signal) | Owner | Auto-closed by the align? |
| --- | --- | --- |
| Variant folder name (`docs/arquitetura/`), missing applicable home | stage 1 | Yes |
| Un-stamped / mis-stamped frontmatter, `summary:`→`description:`, enum drift | stage 1 | Yes |
| Prefix-cluster to fold (`nomenclatura-*.md`), non-English slug to translate | stage 1 | Yes |
| `dir-no-index` / `index-broken-link` / `index-orphan` (validator WARN) | stage 1 | Yes |
| Undrained facts in `~/.claude/projects/<cwd>/memory/` | `/docs:import-memory` | Yes |
| Fat harness — durable knowledge inlined in `CLAUDE.md`/`AGENTS.md` | `/docs:harness` | Yes (MOVE, via `/docs:add`) |
| Broken / lying harness pointer | `/docs:harness` | Yes |
| Repo-specific term in the bundle, absent from `knowledge/glossary.md` | `/docs:glossary-backfill` | **Offered** — no cheap signal proves the gap, so the human is asked once per run |
| `resource-unresolved` — a `resource` entry matching nothing on disk | *(surface → `/docs:add` to restamp)* | **No** — only a human knows what the doc now governs; reported with the entry |
| `resource-self` — the doc sits inside its own declared scope | *(surface → `/docs:add` to restamp)* | **No** — narrowing a scope is a judgement, and a bundle aggregate is legitimate; reported |
| `glossary-broken-link` — a glossary entry points at a deleted doc | *(surface → `/docs:define`)* | **No** — the backfill stage ADDS missing terms, it never prunes a dead one; reported |
| `stale-doc` — `timestamp` predates the last commit touching its `resource` | *(surface → the doc's owner)* | **No** — advisory; code may have moved under a rule that did not change |
| Coverage-ledger deferral — a candidate sub-standard not yet written | *(surface → `/docs:add`)* | **No** — needs human-provided evidence; reported |
| A generic concept / standard / term a human has NOT yet stated | *(surface → `/docs:learn` / `/docs:add` / `/docs:define`)* | **No** — no fresh human input this pass; reported |
| `user` memory, secret, or unroutable harness fact | *(kept in place)* | **No** — flagged and kept, never deleted |

The rightmost column is the anti-fabrication boundary: the align closes only what a **sweep** can
close deterministically from what the repo already contains. Content that requires a human to
state something new is **surfaced**, never invented.
