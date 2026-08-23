# The gears contract — how `quenching-specs-cycle` derives its run

[cycle.md](../../commands/specs/cycle.md) conducts ONE spec's lifecycle, in two
halves authorized separately. This file is the contract it derives each half from: what a gear is,
how the `complexity` field on the `priority` record becomes the ONE gears plan a half presents
before any write, and how the gear is re-evaluated at the end of every stage — with a fresh
authorization when it moves up.

**A gear governs the stages of ONE spec, and nothing about N.** Conducting N specs, the form a
run's recursive return takes, how a block in one spec is classified against the ones after it, and
the deliberate absence of a cap on N all belong to
[fanout.md](../../references/specs-fanout/fanout.md) §The two regimes
§The queue's shape §The entry contract §Classifying a block §The recursive return, which
`quenching-specs-execute-queue` and `quenching-specs-develop-batch` derive their runs from.
Neither of them **derives** a gears plan. Both, however, read §The scale: the level says who answers inside the stage they invoke, and `quenching-specs-develop-batch` needs it to know which spec its conductor stamps without asking. §The scale is the only section here that is theirs to read.

This contract lives in the plugin, never in a target's bundle: it is procedure a command needs
while running inside a target, not a fact about that target, so it is cited by
`../..` from every repo the same way — never installed, and never resolved from a
target's own `/.knowledge/`.

## Contents

`cq components read <this file>` returns the heading index; `--sections` addresses one.

## What a gear is

<!-- rules -->

A **gear** is the execution mode of ONE lifecycle stage. Each of the four stages — create,
develop, execute, conclude — runs in one of three gears:

- **in-session** — the stage runs here, in the conducting conversation;
- **sub-agent** — the stage runs isolated, and only its summary returns;
- **skipped** — the stage the derived stage has already passed never re-runs.

A gear changes **how** a stage runs, never **what** it writes — with ONE exception, declared by
the scale rather than taken by a stage: under `low`, `develop` stamps `approved` itself
(§The scale). That is the level's own content, not a stage's discretion, and it is why it is
written down here instead of being discovered in a command body. The per-task commit, the
`## Outcome` and the archiving are never skipped in any gear — the stages write them, and no gear
waives them.

**Capture is the one stage whose gear is not derived.** A spec that does not exist yet carries no
`priority` record, so there is nothing to derive a plan from; `create` runs in-session on its own
gate, and the `complexity` it proposes is what the first gears plan is then derived from.

**The sub-agent gear's own test:** delegate when the returned summary is **much smaller than the
work** that produced it (a repo-wide sweep, a many-file audit, a read that ends in one table), when
slices run in parallel, or when the tool set must be narrower than the conversation's. Keep work
inline when its output is as large as itself (a rewrite lands in context anyway), when it is one
quick lookup, or when the handoff context would cost what the isolation saves. A recurring
*workflow* is a command; a delegated *unit of work* is an agent — the two are not rivals, and a
command may invoke an agent as one step. A stage whose summary would be as large as itself belongs
in-session.

## The scale

<!-- rules -->

Four levels, and each changes something real in **both** halves — who answers during definition,
and how the stages run during building. A level that changes nothing in either half is vocabulary,
and this table is the whole of what each one buys:

| Level | Defining — who answers | Building — how the stages run |
| --- | --- | --- |
| `low` | the pass answers every question from evidence and interrupts nobody; it stamps `approved` itself, `by: low-gear`, and the review window is the spec's URL in the backend | every stage in one session on that half's one OK, nothing stopping mid-flow, ending by opening a pull request |
| `medium` | the pass answers every question from evidence and interrupts nobody, then ends on ONE closing screen: approve, refine a named section, run the premortem, or raise the gear | `develop` runs isolated in a sub-agent — the one stage whose returned summary is much smaller than the work; the rest in session, stopping at each section boundary |
| `high` | the pass **drafts first and then asks about the draft**, which is what collapses the dependency between its questions and lets them travel grouped | every stage in session; the stage-by-stage stops and confirmations are kept, and a section boundary waits for an answer rather than continuing by default |
| `xhigh` | `high`, plus the adversarial bank's **premortem lens runs unconditionally** — not only when the spec's own risk triggers it | `high`, plus each section boundary's self-review going to a reviewer that did not write the code |

**Where the levels split is who answers, not how much work there is.** `low` and `medium` do not
ask; `high` and `xhigh` do. Everything else in the table follows from that one line, including why
`medium` isolates `develop` and `high` cannot: isolation means only the summary returns, which is
incompatible with stopping to ask. Where nobody is interrogated, isolating buys context; where the
human is in the loop, the stage has to run where they can see it.

**A level's gear is the plan that level derives**, and `low`'s has a second name. "The `low` gear"
and **"the minimal gear"** are the same thing: the whole plan `low` derives — never a fourth value
beside in-session, sub-agent and skipped. The three gears stay the modes of ONE stage; a level names
the set of them. `cycle.md`, `convergence.md`, `plan-git-record.md` and the glossary say *minimal
gear*; this file and the `priority` record say `low`. **The binding is here**, at the scale itself,
so neither vocabulary has to be resolved through a third document.

**What the scale measures.** Not the size of the change, its scope or its difficulty — a small
change can still need a human at every step, and a large mechanical one can need almost none. It
measures **how much a human needs to be part of the process**, and the two columns above are that
measure spent. `triage`, `create` and `develop` propose a level against this criterion, never
against the word's plain reading.

**Absent reads as `high`, never `low`.** A spec whose `priority` record carries no `complexity` has
nothing to derive from, and the two errors are not symmetric: `low` is a positive claim — *this can
run unattended, and the pass may stamp the go itself* — and it is the one that costs when it is
wrong. Guessing upward is free; guessing downward is not
([triage.md](../../commands/specs/triage.md) states the same asymmetry for a ranked
row's floor).

**Every stage reads the level from a payload it already fetches.** `cq specs status --spec <slug>
--json` returns `records`, and `priority.complexity` is inside it — so reading the gear costs no
call of its own, which is the condition under which a command may trade a stop for a record it
announces instead.

## Deriving the gears plan

<!-- rules -->

**Two halves, two plans, two authorizations.** Defining (`develop`) and building (`execute` →
`conclude`) are authorized separately, and no level of the scale below collapses the seam — the
building half is authorized after the spec is `ready`, on a plan derived from the `complexity` then
on disk.

ONE gears plan is presented before a half's first write. The level on the `priority` record's
`complexity` field derives it; every stage of that half — and no other — appears in the plan, with
its gear and what the gear changes; the human adjusts it on the same screen, and the OK of the plan
is that half's authorization and no more, per
[convergence.md](../../references/align/convergence.md) §The
cycle-authorization contract: one confirmation authorizes the run it opens, narration replaces
each stage's plan gate, and code-coupled items and irreversible cycle actions still gate
individually.

**The four levels and what each buys are §The scale — never transcribed anywhere else.** This
section is only how a half's plan is derived from one of them.

**"The larger stages" is exactly one stage, and naming it is the point.** `medium` isolates
`develop` and nothing else: it is the one stage whose returned summary is much smaller than the
work, and the only one that *can* be isolated, since at `medium` it asks nothing. `execute`'s
output is code that lands in the tree either way, and its real delegation is per task under
[execution.md](../../references/specs-execute/execution.md) §Delegating an
executor. `conclude` takes irreversible cycle actions that gate individually, and a sub-agent
cannot present a gate. A plan claiming to isolate either would describe a run nobody can execute.

`complexity` is written by `triage`, `create` and `develop` — never silently: every write is
proposed with the scale in front of the human and lands on a confirmation, under a record whose
owner stays `triage`. **`create` is the one exception to the ordering, never to the rule.** It
writes the level it computed from the input BEFORE anyone sees it, because the spec does not exist
yet for a confirmation to gate on — but the scale still reaches the human, on the capture's own
closing screen, or on `quenching-specs-develop`'s first pass over a spec nobody looked at. The
proposal survives; only its position relative to the write moves. The defining half derives its
plan from this level before the build, when the sections that would evidence the size do not exist
yet — which is why the field lives in frontmatter at all.

## Re-evaluating a gear

<!-- rules -->

At the end of every stage, the state is read again (`cq specs status --spec <id> --json`) and the
gear is re-evaluated against what the stage just revealed. Three signals move a gear up:

- **tasks born** — the task count grew beyond what the plan assumed;
- **files beyond `## Impact`** — a stage wrote or revealed paths the spec never declared;
- **a `- [!]` task** — work that started and stopped, which a plan made from the input could not
  have predicted;
- **a human asked for more** — on the defining half's closing screen, choosing to refine a named
  section or to run the premortem is the human saying the gear was too low. This one is **declared
  rather than derived**, and the choice IS the OK to restamp `complexity`: the option's own text
  names the level it moves to, so the raise and the record land in the same edit.

The first three signals fire at any level. The fourth exists only where a closing screen does —
`medium` and above — and giving it up is part of what `low` gives up.

A gear that moved up returns to the plan of the half the run is in: a new gears plan and a fresh
authorization — that half's OK covers the gear its plan presented, never the one above it. A stage
that changed no size keeps its gear; the level on disk remains the latest word on it.

The re-evaluation is what keeps the gear honest. Derived from `complexity` at the start of a half,
the gear is a bet placed with the information that half opened on; the stages that ran are newer
information, and a run that never re-checked would execute the rest of the half under a bet it
already outgrew.
