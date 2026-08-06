# The convergence contract — shared by every align

<!-- rules -->
This file is **self-contained**: an align reads it and needs nothing else. Each front's own
pipeline — which stages, in what order, and why — is the invoking align's to know and is already
loaded by the time this contract is read; it is deliberately **not** repeated here and **not**
linked from here.

The sweep-side peer of this contract — how one align behaves standalone — is its sibling
[`sweep-doctrine.md`](${CLAUDE_PLUGIN_ROOT}/assets/references/align/sweep-doctrine.md), which
states the cycle-authorized case in full rather than deferring back here.

<!-- rationale -->
A reference that sends a reader to another reference makes the second one
mandatory, which is the opposite of what the loading hierarchy is for. The two files agree by
saying the same thing, not by pointing at each other.

## Contents

`skills.py read <this file>` returns the heading index; `--sections` addresses one.

## The cycle-authorization contract

<!-- rules -->
An align asks for ONE human confirmation, at run start, that authorizes the entire run — up to
the pass cap or convergence. Every command
an align invokes as a stage carries **one** exception sentence pointing here and never restates
it: the `docs/` stages (`/quenching:docs:import-memory`, `/quenching:docs:harness`, `/quenching:docs:glossary-backfill`), the
`specs/` stages (`/quenching:specs:conclude`, `/quenching:specs:triage`), and the three front aligns when `/align`
invokes them.

**What the authorization covers** — every routine write a stage performs: frontmatter stamps,
new concept docs, index/log/glossary entries, align's routine doc/folder renames, variant
migrations, and the deletions those migrations require, memory migration + deletion (after its
write-then-verify self-check), harness unit cuts (after theirs), triage's `priority` writes, the
`specs/` workspace's structural repairs — as long as it touches no product code.

**What it NEVER covers** — two classes of item, each of which gates individually, always,
exactly as when the stage runs standalone. After the initial OK these are the only possible
stops:

1. **Code-coupled items** — any rename or edit whose blast radius reaches **product code** (a
   path constant, an import, a docstring, a branch name, a CI job).
2. **Irreversible cycle actions** — an action that discards or relocates a record of work rather
   than reshaping it: concluding a spec (it moves the spec into `archive/` and distils into
   `docs/`), and removing a spec from `plans/`. One OK **per item**, with
   what it will do shown.

**What it does not change** — the stages' safe-write invariants (write-then-verify-then-delete
for memory, write-then-verify-then-cut for harness, write-then-verify for a captured spec) do not
depend on who authorized the run and remain in force. Scope surprises do not re-gate: a later
pass discovering more work than the preview estimated proceeds under the same authorization,
bounded by the pass cap and the stages' own invariants.

**How the align signals the mode** — it declares, in the invocation of each stage:
*"Running under <align-name> authorization granted at run start — skip your plan-confirmation
pause; present your plan as narration and execute; code-coupled and irreversible items still gate
individually."* A stage invoked WITHOUT this declaration (standalone) keeps its normal plan → OK
gate.

**Narration replaces the gate, not the plan** — an authorized stage still presents its full plan
table before writing; the user watching the session sees everything and types nothing.

**Nesting is one level of authorization, not two gates.** When `/align` invokes a front align, the
front align does **not** ask for its own OK — it inherits the authorization and passes it down
verbatim to its own stages. The human confirms once for the whole repo; only code-coupled and
irreversible items still interrupt.

<!-- rationale -->
**Irreversible cycle actions** — Judgment the align does not have decides these: a
spec whose tasks are all checked may still be waiting on a deploy.

## The PR route — where review lives when the run does not stop

<!-- rules -->
The minimal gear differs from the contract in exactly one point, and pays for it outside the
session. The contract requires a code-coupled item and an irreversible cycle action to stop the
run, always; under the orchestrator's minimal gear
([orchestration-gears.md](/docs/standards/automation/orchestration-gears.md) §Deriving the gears
plan, the `low` row) neither stops — the whole cycle runs in one session on a single authorization
and ends opening a pull request, so the human review the gates would have hosted moves to the PR
instead: opened against the integration branch declared in `.claude/quenching.json`
(`integrationBranch`), where the merge waits on review and on the checks before it lands. The
trade is said out loud: if the PR is merged unread, no gate was left anywhere on the path — which
is what the gear re-evaluation exists to bound, as a run that outgrows the minimal gear climbs
back into a run with gates before it reaches the PR.

The route already exists — nothing new is built for it. `conclude` offers pull request or local
alongside the strategy ([plan-git-record.md](/docs/standards/workflows/plan-git-record.md) §The
route is a second choice, and it moves when `merge:` is stamped), and the `merge` record's `pr`
field names the pull request — the fact the base branch's history cannot reproduce: which PR the
merge went through, and where the review and the checks still live once the branch is gone
(§Two frontmatter records carry the underivable git facts).

No gear above the minimal changes the contract: a run that stops stage by stage keeps the two
classes gating individually, item by item, in the session, exactly as when the stage runs
standalone. The PR route is the minimal gear's answer — review relocated, never removed.

<!-- rationale -->
**The PR route** — a run whose minimal gear stops for nothing would end with nobody having seen
the work; the PR is where that review happens instead — before the merge, with the checks, on the
branch the cycle built. Relocating review is the alternative to adding a stop, which is exactly
what the minimal gear exists to avoid.

## The convergence contract

<!-- rules -->
Let a pass be **empty** when every applicable stage reports "nothing to do." Let a front be
**clean** when its own verifier passes: `okf-validate.py <docs> --json` exiting 0 **and**
reporting zero `dir-no-index` / `index-broken-link` / `index-orphan` for `docs/` (these are
WARN — exit 0 alone does not prove them clear, read the findings); `specs.py doctor` +
`specs.py validate` clean, and nothing else, for `specs/`; `skills.py lint` + `skills.py doctor` exiting 0
**and** `skills.py registry reindex` reporting `changed: false` for `.claude/`.

- **Converged (stop, success):** a pass is **empty** *and* the front is **clean**. This is the
  fixpoint. Report and write the log entry.
- **Progress (loop):** the pass changed something. Re-assess and run another pass.
- **Residue (stop, report):** the pass was **empty** but the front is **not clean**, or only
  non-auto-closable findings remain (per-item gaps, unroutable facts, deferred sub-standards, a
  doctrine violation only a human-gated edit can fix). Stop — re-running an empty pass cannot
  clear it. Report the residue as deferred opportunities, each with the command that owns it.

**Guards against spinning:**
- **Pass cap** — default **5** per align (a front align nested inside `/align` keeps its own cap;
  `/align`'s own cross-front cap is **3**). If reached before convergence, stop and report what remains; do not raise
  the cap silently.
- **No-progress guard** — never run a pass identical to one that just changed nothing. An empty
  pass with residual findings is a **stop** condition, not a reason to iterate.
- **Never widen scope to force convergence** — an align does not fabricate content, relax a
  stage's confirmation, or auto-close a per-item opportunity to make the numbers reach zero.

<!-- rationale -->
**Progress** — a change can
create follow-on work (a MOVE that needs glossary indexing, an archive whose distillation adds
docs the glossary must index, a relocation that shifts an index).

**Pass cap.** A well-aligned repo converges in 1–2 passes; needing more signals a stage
that keeps producing follow-on work, worth reporting.

**Never widen scope.** A residue reported honestly beats a fixpoint reached by cutting a corner.

## Per-item commands are stage tools, not stages

<!-- rules -->
A command that acts on **ONE item a human states** is never a loop stage, because a conducted pass
has **no fresh human input**: `/quenching:docs:add`, `/quenching:docs:learn`, `/quenching:docs:define`,
`/quenching:docs:import`, `/quenching:skill:new`, `/quenching:specs:create`, `/quenching:specs:develop`,
`/quenching:specs:execute`, `/quenching:specs:conclude`.

`/quenching:specs:status` is not a stage either: it writes nothing, so it can
never close a finding.

They enter a run only **indirectly**, as the tools a sweep stage delegates to
(`/quenching:docs:harness` MOVEs a durable fact via `/quenching:docs:add`). When the assessment finds a gap
only a per-item command could fill, the align **names the gap and the command that would close
it** in its report — the user then invokes that command with the missing input, and the next run
picks the work up. This is the plugin's **anti-fabrication boundary**: an align closes only what a
sweep can close deterministically from what the repo already contains.

<!-- rationale -->
`/quenching:specs:conclude` is the sharpest case: it is not merely un-stageable for lack of input,
it is un-stageable **in principle**. Abandonment is a judgment no repo state implies — a change
untouched for a year may be waiting on a vendor. An align that inferred it from staleness
would be fabricating a decision, which is exactly what this boundary exists to prevent.

**`/quenching:specs:status`.** Its place is **before** a conducted run, as the preview of what the OK
would authorize — the assessment an align performs internally, made visible on its own.

The same split runs through the whole plugin: the whole-bundle glossary sweep
(`/quenching:docs:glossary-backfill`) IS a stage, the single-term capture (`/quenching:docs:define`) is not;
the whole-front ranking sweep (`/quenching:specs:triage`) IS a stage, the single-spec capture
(`/quenching:specs:create`) is not.
