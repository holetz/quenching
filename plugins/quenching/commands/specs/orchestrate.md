---
description: >-
  Conduct ONE spec's whole lifecycle — capture, develop, execute, conclude — on one
  authorization. Triggers on "run this spec end to end", "take this spec to the finish",
  "orchestrate this spec". Enters the cycle at the derived stage the spec already has (stages
  behind it are skipped), invokes each stage as the command that owns it, and presents ONE gears
  plan from priority.complexity, adjustable on the same screen: each stage runs in-session, in a
  sub-agent, or is skipped. The gear is re-evaluated at every stage end — larger revealed size
  moves it up and asks for a fresh authorization; the per-task commit, `## Outcome` and the
  archiving are never skipped in any gear. Typed-only: a whole lifecycle is a human's choice, so
  this description pays no routed budget. Not for: one stage only → /specs:create,
  /specs:develop, /specs:execute, /specs:conclude; the next action on one spec → /specs:continue;
  aligning one front → /docs:align, /specs:align, /skill:align.
argument-hint: [slug-or-description]
allowed-tools: Read, Grep, Glob, Bash(python3:*), Bash(py:*), AskUserQuestion, Skill
disable-model-invocation: true
---

# /quenching:specs:orchestrate — one authorization, the whole lifecycle

**Input**: `$ARGUMENTS` — a spec slug, or a description of what to conduct.

The conductor over the spec lifecycle. Where `/quenching:align` conducts the three fronts, this
command conducts the four stages of ONE spec — `/quenching:specs:create`,
`/quenching:specs:develop`, `/quenching:specs:execute` and `/quenching:specs:conclude` — in one
run, entering at the stage the spec already has, invoking each stage as the command that owns it,
and writing nothing itself.

**Every stage runs in a gear.** In the gears plan each stage runs one of three ways — in-session,
isolated in a sub-agent, or skipped (a stage the derived stage has already passed). The plan is
derived from `priority.complexity` and presented as ONE table before any write, adjustable by the
human on the same screen; the human's OK is the run's authorization.

**The contracts, owned once:**

- [align/convergence.md](${CLAUDE_PLUGIN_ROOT}/assets/references/align/convergence.md) §The
  cycle-authorization contract — one confirmation at run start authorizes the run; narration
  replaces each stage's plan gate; code-coupled items and irreversible cycle actions still gate
  individually.
- [orchestration-gears.md](/docs/standards/automation/orchestration-gears.md) §What a gear is
  §Deriving the gears plan §Re-evaluating a gear — the repo's gears contract: the three ways a
  stage runs, how `complexity` derives the plan, and the signals that move a gear up. A repo that
  does not carry it has no gears to derive: say so and stop before the plan.
- [specs-develop/spec-driven.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-develop/spec-driven.md)
  §Derived stages §Frontmatter §The `specs.py` tool surface — the derived stage is the dispatch,
  and the records (`priority.complexity`, `approved`, `branch`, `merge`) and the tool surface
  this command reads.

## Doctrine

- **The derived stage picks the stage; never read the sections to dispatch.** `specs.py status
  --spec <slug> --json` is the dispatch. The conductor enters the cycle where the spec is; a
  stage the derived stage has passed is skipped, never re-run.
- **ONE gears plan before any write.** The plan derives from the gears contract (§Deriving the
  gears plan) on the `complexity` the `priority` record carries, and every stage appears in it —
  its gear and what the gear changes. The human adjusts on the same screen; nothing is written
  before the OK.
- **Conduct, never reimplement.** Every write belongs to the stage that makes it, under that
  stage's own doctrine and its own safe-write invariants. If a stage's behaviour must change,
  change the stage — never re-derive its logic here.
- **A gear is re-evaluated at the end of every stage, and moving up re-authorizes.** The signals
  and the jump live in the gears contract (§Re-evaluating a gear). A stage whose work reveals
  larger size than declared returns to the plan: a new gears plan and a fresh authorization — the
  run's OK does not cover the higher gear.
- **Typed-only: a human chooses this command.** It conducts a whole lifecycle, so no spoken
  trigger reaches it and the description pays no routed budget.
- **The trace of a small spec is identical to a big one.** The per-task commit, the `## Outcome`
  and the archiving are never skipped in any gear — the stages write them, and this command never
  waives them.

## Workflow (stage → gears plan → one OK → stages → re-evaluate → report)

### 1. Resolve the spec
Take the slug from the input, infer it from the conversation, or run `specs.py list --json` and
ask with **AskUserQuestion** (most recently modified marked "(Recommended)"). Two matches for one
slug is exit 2 — report both paths and stop, never guess which was meant. An archived spec has
nothing to conduct: say so and stop.
**Done when:** one spec in `plans/` is resolved.

### 2. Read the state in one call
```bash
specs.py status --spec <slug> --json    # derived stage, records, tasks, gate, verification
specs.py config --json                  # backend, integrationBranch
```
The derived stage is the dispatch (Doctrine). Nothing else is read here — each stage reads what it
needs when it runs.
**Done when:** the stage and the records are in hand.

### 3. Present ONE gears plan → the OK is the authorization
Derive the plan from the gears contract (§Deriving the gears plan) on the `complexity` the
`priority` record carries. Present ONE table: per stage — the stage, its gear, and what the gear
changes. An adjustment re-presents the plan; use **AskUserQuestion** when the choice is between
two gears for one stage.

The OK of this plan is the run's authorization. Declare it verbatim per the cycle-authorization
contract, naming this command as the grantor:
*"Running under /quenching:specs:orchestrate authorization granted at run start — skip your
plan-confirmation pause; present your plan as narration and execute; code-coupled and
irreversible items still gate individually."*
**Done when:** the plan is approved as presented, or the run is declined (nothing written).

### 4. Run the stage the derived stage picks
The stage-to-run map:

| The derived stage | The stage that runs |
| --- | --- |
| `captured` | `/quenching:specs:create` |
| `proposed` · `designed` · `refined` · `ready` | `/quenching:specs:develop` |
| `approved` · `executing` | `/quenching:specs:execute` |
| every task `- [x]`, the spec still in `plans/` | `/quenching:specs:conclude` |

Invoke the stage via the **Skill** tool under its registry name (`quenching:specs:create`, and so
on), declaring the authorization as step 3's sentence. A stage whose gear is `sub-agent` runs
isolated and returns its summary per the gears contract (§What a gear is); the contract's test
that the summary is much smaller than the work is
[agents.md](/docs/standards/automation/agents.md).
**Done when:** the stage finished (or was skipped with a stated reason) and its outcome is
recorded.

### 5. Re-evaluate the gear, and re-derive the stage
At the end of every stage, read the state again (`specs.py status --spec <slug> --json`) and
re-evaluate the gear per the gears contract (§Re-evaluating a gear). Two outcomes:

- **The gear held, and the stage moved** → return to step 4 for the stage the new derived stage
  picks.
- **The gear moved up** → return to step 3: a new gears plan and a fresh authorization — the
  run's OK does not cover the higher gear.

The loop ends when the spec is archived (the conclude stage did it), the derived stage selects no
stage this command owns, or the human stops it. Never end on a residue you could carry into the
report — the report is where the run is accounted for.
**Done when:** the loop has stopped for a stated reason.

### 6. Report
One report, stage by stage: the gears plan that ran (and every re-evaluation), what each stage
did in total, the derived stage at the end, and everything deferred, each with the command that
closes it.

This command writes **nothing** of its own — not even a record that it ran. Every write belongs
to the stage that made it, and the report is where this run is accounted for.
**Done when:** every stage's outcome and every deferral is stated.

## Invariants to never violate

- Never reimplement a stage's logic here — **invoke** the stage via the Skill tool, always.
- Never dispatch by reading the sections — the derived stage is the only dispatch.
- Never write anything of your own — not even a record that this command ran.
- Never present less than the whole gears plan before the first write, and never apply an
  authorization to a gear the plan did not present.
- Never let a stage re-gate — authorization nests one level (the cycle-authorization contract);
  equally, never suppress the two interruptions the contract never covers: code-coupled renames
  and irreversible closes.
- Never skip the per-task commit, the `## Outcome` or the archiving in any gear — a gear changes
  how a stage runs, never what it writes.
- Never hand this command file `context: fork` — the plan gate and every nested confirmation are
  mid-flow.
