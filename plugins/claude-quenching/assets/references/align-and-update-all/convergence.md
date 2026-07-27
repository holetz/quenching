# The convergence contract — shared by every conductor

The plugin has **five** conductors: one align-and-update per front, plus the two cross-front
ones. They differ only in *which* stages they run; everything about **how** a conducted run is
authorized, when it stops, and what keeps it from spinning is identical — so it lives here,
once, and every conductor and every stage skill cites this file instead of restating it.

| Conductor | Runs | Loops? |
| --- | --- | --- |
| `/docs:align-and-update` | the `docs/` front's four sweeps | yes, to a fixpoint |
| `/specs:align-and-update` | the `specs/` front's three stages | yes, to a fixpoint |
| `/skill:align-and-update` | the `.claude/` front's two stages | yes (converges in 1–2 passes by nature) |
| `/align-and-update` | the three front conductors above | yes, across fronts |
| `/align` | the three front **aligns** only | **no** — one structural pass |

This file is **self-contained**: a conductor reads it and needs nothing else. Each front's own
pipeline — which stages, in what order, and why — is the invoking conductor's to know and is
already loaded by the time this contract is read; it is deliberately **not** repeated here and
**not** linked from here. A reference that sends a reader to another reference makes the second
one mandatory, which is the opposite of what the loading hierarchy is for.

The sweep-side peer of this contract — how one align behaves standalone — is owned by
`/align`'s `sweep-doctrine.md`, which states the cycle-authorized case in full
rather than deferring back here. The two files agree by saying the same thing, not by pointing
at each other.

Read "the cycle" below as "the invoking conductor" — nothing in this contract changes between
them.

## Contents

- [The cycle-authorization contract](#the-cycle-authorization-contract)
- [The convergence contract](#the-convergence-contract)
- [Per-item skills are stage tools, not stages](#per-item-skills-are-stage-tools-not-stages)

## The cycle-authorization contract

A conductor asks for ONE human confirmation, at run start, that authorizes the entire run — up
to the pass cap or convergence. This section is that contract's single normative home. Every
skill a conductor invokes carries **one** exception sentence pointing here and never restates
it: the four `docs/` stages (`/docs:align`, `/docs:import-memory`, `/docs:harness`,
`/docs:glossary-backfill`), the `specs/` stages (`/specs:align`,
`/specs:archive`, `/specs:triage`), and
`/skill:align`.

**What the authorization covers** — every routine write a stage performs: frontmatter stamps,
new concept docs, index/log/glossary entries, align's routine doc/folder renames, variant
migrations, and the deletions those migrations require, memory migration + deletion (after its
write-then-verify self-check), harness unit cuts (after theirs), backlog triage edits, the
`specs/` workspace's structural repairs — as long as it touches no product code.

**What it NEVER covers** — two classes of item, each of which gates individually, always,
exactly as when the stage runs standalone. After the initial OK these are the only possible
stops:

1. **Code-coupled items** — any rename or edit whose blast radius reaches **product code** (a
   path constant, an import, a docstring, a branch name, a CI job).
2. **Irreversible cycle actions** — an action that discards or relocates a record of work rather
   than reshaping it: archiving a specs change (it moves the change out of `changes/` and distils
   into `docs/`), and removing a task from the backlog. Judgment the conductor
   does not have decides these: a change whose tasks are all checked may still be waiting on a
   deploy. One OK **per item**, with what it will do shown.

**What it does not change** — the stages' safe-write invariants (write-then-verify-then-delete
for memory, write-then-verify-then-cut for harness, write-then-verify for a captured spec) do not
depend on who authorized the run and remain in force. Scope surprises do not re-gate: a later
pass discovering more work than the preview estimated proceeds under the same authorization,
bounded by the pass cap and the stages' own invariants.

**How the conductor signals the mode** — it declares, in the invocation of each stage:
*"Running under <conductor-name> authorization granted at run start — skip your
plan-confirmation pause; present your plan as narration and execute; code-coupled and
irreversible items still gate individually."* A stage invoked WITHOUT this declaration
(standalone) keeps its normal plan → OK gate.

**Narration replaces the gate, not the plan** — an authorized stage still presents its full plan
table before writing; the user watching the session sees everything and types nothing.

**Nesting is one level of authorization, not two gates.** When
`/align-and-update` invokes a front conductor, the front conductor does **not** ask
for its own OK — it inherits the authorization and passes it down verbatim to its stages. The
human confirms once for the whole repo; only code-coupled and irreversible items still interrupt.

## The convergence contract

Let a pass be **empty** when every applicable stage reports "nothing to do." Let a front be
**clean** when its own verifier passes: `okf-validate.py <docs> --json` exiting 0 **and**
reporting zero `dir-no-index` / `index-broken-link` / `index-orphan` for `docs/` (these are
WARN — exit 0 alone does not prove them clear, read the findings); `specs.py doctor` +
`specs.py validate` clean **and** `okf-validate.py specs/backlog --listing-root` clean by
the same read-the-findings rule, for `specs/`; `skills.py lint` + `skills.py doctor` exiting 0
**and** `skills.py registry reindex` reporting `changed: false` for `.claude/`.

- **Converged (stop, success):** a pass is **empty** *and* the front is **clean**. This is the
  fixpoint. Report and write the log entry.
- **Progress (loop):** the pass changed something. Re-assess and run another pass — a change can
  create follow-on work (a MOVE that needs glossary indexing, an archive whose distillation adds
  docs the glossary must index, a relocation that shifts an index).
- **Residue (stop, report):** the pass was **empty** but the front is **not clean**, or only
  non-auto-closable findings remain (per-item gaps, unroutable facts, deferred sub-standards, a
  doctrine violation only a human-gated edit can fix). Stop — re-running an empty pass cannot
  clear it. Report the residue as deferred opportunities, each with the skill that owns it.

**Guards against spinning:**
- **Pass cap** — default **5** per conductor (a front conductor nested inside the cross-front one
  keeps its own cap). If reached before convergence, stop and report what remains; do not raise
  the cap silently. A well-aligned repo converges in 1–2 passes; needing more signals a stage
  that keeps producing follow-on work, worth reporting.
- **No-progress guard** — never run a pass identical to one that just changed nothing. An empty
  pass with residual findings is a **stop** condition, not a reason to iterate.
- **Never widen scope to force convergence** — a conductor does not fabricate content, relax a
  sub-skill's confirmation, or auto-close a per-item opportunity to make the numbers reach zero.
  A residue reported honestly beats a fixpoint reached by cutting a corner.

## Per-item skills are stage tools, not stages

A skill that acts on **ONE item a human states** is never a loop stage, because a conducted pass
has **no fresh human input**: `/docs:add`, `/docs:learn`, `/docs:define`,
`/docs:import`, `/skill:new`, `/specs:capture`, `/specs:explore`,
`/specs:develop`, `/specs:apply`, `/specs:develop`,
`/specs:archive`.

`/specs:archive` is the sharpest case: it is not merely un-stageable for lack of input,
it is un-stageable **in principle**. Abandonment is a judgment no repo state implies — a change
untouched for a year may be waiting on a vendor. A conductor that inferred it from staleness
would be fabricating a decision, which is exactly what this boundary exists to prevent.

`/specs:status` is not a stage either, for the opposite reason: it writes nothing, so it can
never close a finding. Its place is **before** a conducted run, as the preview of what the OK
would authorize — the assessment a conductor performs internally, made visible on its own.

They enter a run only **indirectly**, as the tools a sweep stage delegates to
(`/docs:harness` MOVEs a durable fact via `/docs:add`). When the assessment finds a gap
only a per-item skill could fill, the conductor **names the gap and the skill that would close
it** in its report — the user then invokes that skill with the missing input, and the next run
picks the change up. This is the plugin's **anti-fabrication boundary**: a conductor closes only
what a sweep can close deterministically from what the repo already contains.

The same split runs through the whole plugin: the whole-bundle glossary sweep
(`/docs:glossary-backfill`) IS a stage, the single-term capture (`/docs:define`) is not;
the whole-backlog triage (`/specs:triage`) IS a stage, the single-task capture
(`/specs:capture`) is not.
