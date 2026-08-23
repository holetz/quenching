---
name: quenching-specs-cycle
description: "Conduct ONE spec's lifecycle — capture, define, build, close — as two halves, each on its own authorization. Triggers on \"run this spec end to end\", \"take this spec to the finish\", \"cycle this spec\". Enters at the derived stage the spec already has; an ID that resolves to nothing is captured through quenching-specs-create and the run carries on at defining. Defining opens on its own gears plan and delegates to quenching-specs-develop; building is authorized separately and delegates to quenching-specs-execute then quenching-specs-conclude. The gear is re-evaluated at every stage end, and larger revealed size asks afresh. Typed-only: a whole lifecycle is a human's choice, so this description pays no routed budget. Not for: N specs in one build queue → quenching-specs-execute-queue; N specs defined at once → quenching-specs-develop-batch; one stage only → quenching-specs-develop, quenching-specs-execute, quenching-specs-conclude."
---

<!-- GENERATED FROM plugins/quenching/commands/specs/cycle.md -->


# quenching-specs-cycle — ONE spec, two authorizations

**Input**: `$ARGUMENTS` — a spec id, or a description of what to conduct.

The conductor over ONE spec's lifecycle. Where `quenching-align` conducts the three fronts, this
command conducts the stages of one spec — `quenching-specs-create`, `quenching-specs-develop`,
`quenching-specs-execute` and `quenching-specs-conclude` — entering at the stage the spec already
has, invoking each stage as the command that owns it, and writing nothing itself.

**Two halves, authorized separately.** **Defining** delegates to `quenching-specs-develop`;
**building** delegates to `quenching-specs-execute` and then `quenching-specs-conclude`. Each
half opens with its own gears plan and its own OK, and **no gear collapses the seam** — deciding
what a spec is and deciding to build it are two decisions, and one OK never buys both.

**N specs is another command's run.** Building N is `quenching-specs-execute-queue`, defining N is
`quenching-specs-develop-batch`; both derive their runs from the fan-out contract, and neither has
a gear. This command is the N=1 case and never conducts a second spec.

**Every stage runs in a gear** — in-session, isolated in a sub-agent, or skipped because the
derived stage has already passed it — and every gear derives from `priority.complexity`. A stage
whose gear is `sub-agent` runs isolated and returns its summary per §What a gear is, whose test is
that the returned summary is much smaller than the work that produced it.

**The contracts, owned once:**

- [gears.md](../../references/specs-cycle/gears.md) §What a gear is
  §Deriving the gears plan §Re-evaluating a gear — the three ways a stage runs, how `complexity`
  derives each half's plan, and the signals that move a gear up.
- [align/convergence.md](../../references/align/convergence.md) §The
  cycle-authorization contract §The PR route — one confirmation authorizes a half; narration
  replaces each stage's plan gate; code-coupled items and irreversible cycle actions still gate
  individually, except under the minimal gear, where the review moves to the pull request.
- [specs-develop/spec-driven.md](../../references/specs-develop/spec-driven.md)
  §Derived stages §Frontmatter §The `cq specs` tool surface — the derived stage is the dispatch,
  and the records (`priority.complexity`, `approved`, `branch`, `merge`) and the tool surface this
  command reads.

**Every `§X` above is an address, and it is loaded as one** — `cq components read <the cited file>
--sections "§A" --sections "§B"`, one call for N sections, `--rules-only` to narrow to the binding
half. Never open a cited reference as a file.

## Resolving the tool

Resolve `cq` per
[align/tool-resolution.md](../../references/align/tool-resolution.md)
§Resolving the tool §Write the resolved path literally on every invocation; branch on the **exit
code** (0 ok · 1 findings · 2 refusal) and the `--json`, never on prose.

`cq` is the only tool this command needs: every read it makes goes through it, and every write
belongs to a stage it invokes — which is why no `Read`/`Grep`/`Glob` is granted here.

## Doctrine

- **The derived stage picks the half and the stage inside it; never read the sections to
  dispatch.** `cq specs status --spec <id> --json` is the dispatch. A stage the derived stage has
  passed is skipped, never re-run.
- **ONE gears plan per half, before that half's first write.** It derives from §Deriving the gears
  plan on the `complexity` the `priority` record carries, and every stage of the half appears in it
  — its gear, and what the gear changes. Nothing is written before the OK.
- **Capture is not part of either half.** An ID that resolves to nothing is not an error: it
  becomes `quenching-specs-create`, invoked with **no** authorization declaration, so it keeps its
  own gate. The `complexity` it stamps is what the defining half's plan is then derived from —
  which is why the capture cannot sit inside a plan derived from it.
- **Conduct, never reimplement.** Every write belongs to the stage that makes it, under that
  stage's own doctrine and its own safe-write invariants. If a stage's behaviour must change,
  change the stage — never re-derive its logic here.
- **A gear is re-evaluated at the end of every stage, and moving up re-authorizes.** The signals
  and the jump live in §Re-evaluating a gear. A stage whose work reveals larger size than declared
  returns to its half's plan: a new plan and a fresh OK — the half's OK does not cover the higher
  gear.
- **The minimal gear runs a half on that half's one OK, and pays for it outside the session.**
  Under it neither protected class stops the run — code-coupled items and irreversible closes
  included — and the building half ends with this command itself opening a pull request, via
  `quenching-git-pr-create` invoked under the same authorization, against the primary branch,
  never with a direct merge: the human review lives in the PR (§The PR route).
  A half that outgrows the minimal gear climbs back into a run with gates before it reaches the PR.
- **Typed-only: a human chooses this command.** It conducts a whole lifecycle, so no spoken trigger
  reaches it and the description pays no routed budget.
- **The trace of a small spec is identical to a big one.** The per-task commit, the `## Outcome`
  and the archiving are never skipped in any gear — the stages write them, and this command never
  waives them.

## Workflow (resolve or capture → define on one OK → build on another → report)

### 1. Resolve the spec — or capture it
Take the ID from the input, infer it from the conversation, or run `cq specs list --json` and ask
with **AskUserQuestion** (most recently modified marked "(Recommended)"). Two matches for one ID
is exit 2 — report both paths and stop, never guess which was meant. An archived spec has nothing
to conduct: say so and stop.

**An ID that resolves to nothing, and a description that names no spec, take the same path**:
invoke `quenching:specs:create` through the **Skill** tool with what the input carried, and carry
on from the spec it just created. No authorization has been granted at this point, so the
invocation carries no declaration and `create` keeps its own gate.
**Done when:** one spec in `plans/` is resolved — found, or just captured.

### 2. Read the state in one call
```bash
python3 "$(find "${CODEX_HOME:-$HOME/.codex}" "$HOME/.codex" -type f -path '*/quenching-codex*/scripts/cq' -print -quit 2>/dev/null)" specs status --spec <id> --json    # derived stage, records, tasks, gate, verification
python3 "$(find "${CODEX_HOME:-$HOME/.codex}" "$HOME/.codex" -type f -path '*/quenching-codex*/scripts/cq' -print -quit 2>/dev/null)" specs config --json                  # backend
```
The derived stage says which halves this run still has:

| The derived stage | The half that runs |
| --- | --- |
| `captured` · `proposed` · `designed` · `refined` | **defining**, then building |
| `ready` · `approved` · `executing` | **building** only — defining is already passed |

A spec whose tasks are all `- [x]` and that still sits in `plans/` enters building at
`quenching-specs-conclude`: `execute` has nothing left, so its gear is `skipped`.

Nothing else is read here — each stage reads what it needs when it runs.
**Done when:** the stage, the records and the halves this run still has are in hand.

### 3. Authorize the defining half
Skip to step 5 when the derived stage has already passed it. Otherwise derive the plan from
§Deriving the gears plan on the `complexity` the `priority` record carries, and present it as ONE
screen: the stage, its gear, and what the gear changes. An adjustment re-presents the plan; use
**AskUserQuestion** when the choice is between two gears for one stage.

This OK authorizes **the defining half and nothing beyond it**. Declare it verbatim per §The
cycle-authorization contract, naming this command as the grantor:
*"Running under quenching-specs-cycle authorization granted at run start — skip your
plan-confirmation pause; present your plan as narration and execute; code-coupled and irreversible
items still gate individually."*
**Done when:** the plan is approved as presented, or the run is declined (nothing written).

### 4. Define — `quenching-specs-develop`
Invoke `quenching:specs:develop` through the **Skill** tool under step 3's sentence, in the gear
the plan gave it.

Then read the state again (`cq specs status --spec <id> --json`) and re-evaluate the gear per
§Re-evaluating a gear. **The gear moved up** → return to step 3: a new plan and a fresh
authorization for this half. A spec that did **not** reach `ready` — open decisions a human has to
answer, a section the pass could not fill — stops here and is reported with what is missing: the
building half is never authorized over a spec that is not ready.
**Done when:** the spec reached `ready`/`approved`, or the run stopped for a stated reason.

### 5. Authorize the building half — a second OK, never the first one stretched
Present a **second** gears plan, derived the same way from the `complexity` on disk — which the
defining pass may have moved: `quenching-specs-execute` and `quenching-specs-conclude`, each with
its gear, plus the base branch and the isolation form. **Under the minimal gear only**, the plan
also names `quenching-git-pr-create` as a third stage this half runs, against the primary
branch — every other gear ends this half at `conclude`'s own handoff, and the PR or the
merge is the human's separate, later command. Step 3's OK does not reach here, and a run that
entered at building has this plan as its first.

Declare the same sentence as step 3 to every stage this half runs — two under every other gear,
three under the minimal one. Under the minimal gear the last clause changes — nothing gates
mid-flow, and the review lives in the PR:
*"Running under quenching-specs-cycle minimal-gear authorization granted at run start — skip your
plan-confirmation pause; present your plan as narration and execute; neither code-coupled items nor
irreversible closes stop this run — the review lives in the PR it opens."*
**Done when:** the plan is approved as presented, or the run is declined with the spec left where
the defining half put it and nothing built.

### 6. Build, then close
Invoke `quenching:specs:execute` through the **Skill** tool under step 5's sentence, then
`quenching:specs:conclude`, each in the gear the plan gave it. **Under the minimal gear only**, once
`conclude` reports its gate passed and names its handoff, invoke `quenching:git:pr:create` through
the **Skill** tool too, under the same sentence — approved in step 5's plan, never rediscussed at
the stage, and the one point this command executes a stage's own suggested next step rather than
leaving it for the human to run separately. Every other gear ends this half the moment `conclude`
reports its handoff, and never invokes it.

Between stages, read the state again and re-evaluate the gear per §Re-evaluating a gear — moved up
→ return to step 5 for a new plan and a fresh OK. The half ends when the spec is archived
(`conclude` did it) — under the minimal gear, with the pull request `git:pr:create` just opened and
its merge waiting on review — or when the human stops it. Never end on a residue you could carry
into the report.
**Done when:** the spec is archived, or the half stopped for a stated reason.

### 7. Report
One report, stage by stage: the plan each half ran under (and every re-evaluation), what each stage
did in total, the derived stage at the end — and, under the minimal gear, the pull request the
building half opened, with the merge waiting on its review — and everything deferred, each with the
command that closes it.

This command writes **nothing** of its own — not even a record that it ran. Every write belongs to
the stage that made it, and the report is where this run is accounted for.
**Done when:** every stage's outcome and every deferral is stated.

## Hard rules — no exceptions, and no "just this once"

- **Never run the two halves on one authorization.** Defining and building are two decisions, and
  the seam between them is the one thing no gear moves — including the minimal one, whose PR route
  relocates the review inside the building half and nothing else.
- **Never build a spec that is not `ready`/`approved`.** A defining half that stopped short stops
  the run; the missing sections are reported, not worked around.
- **Never conduct a second spec.** A `## Discoveries` line promoted during the run waits in
  `plans/`; N specs belong to `quenching-specs-execute-queue` and `quenching-specs-develop-batch`.

## Invariants to never violate

- Never reimplement a stage's logic here — **invoke** the stage via the Skill tool, always.
- Never dispatch by reading the sections — the derived stage is the only dispatch.
- Never write anything of your own — not even a record that this command ran.
- Never present less than a half's whole gears plan before its first write, and never apply an
  authorization to a gear the plan did not present.
- Never let a stage re-gate — authorization nests one level (§The cycle-authorization contract);
  equally, never suppress the two interruptions the contract never covers — code-coupled renames
  and irreversible closes — outside the minimal gear, where the approved plan relocates both to the
  PR (§The PR route).
- Never skip the per-task commit, the `## Outcome` or the archiving in any gear — a gear changes
  how a stage runs, never what it writes.
- Never refuse an input because no spec answers to it — capture it and carry on.
- Never open a cited reference as a file — `§X` is an address, loaded through
  `cq components read --sections`.
- Never hand this command file `context: fork` — a half's plan gate and every nested confirmation
  are mid-flow, and a forked context cannot present either. The one admission is a minimal-gear run
  that enters at **building**: its plan is the run's first screen and no mid-flow confirmation
  follows it — neither protected class stops it, the review lives in the PR it opens (§The PR
  route). A run that also has the defining half carries the building authorization mid-flow, so the
  prohibition holds; so does any gear above the minimal.
