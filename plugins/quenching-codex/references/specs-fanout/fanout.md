# The fan-out contract — how N specs are conducted in one authorization

[execute-queue.md](../../commands/specs/execute-queue.md) builds N specs and
[develop-batch.md](../../commands/specs/develop-batch.md) defines N specs. This
file is the contract both derive their run from: which of the two regimes a stage belongs to, the
queue's shape, the entry contract that decides where a spec joins, how a block is classified, and
how a run absorbs the work it revealed.

This contract lives in the plugin, never in a target's bundle: it is procedure a command needs
while running inside a target, not a fact about that target, so it is cited by
`../..` from every repo the same way — never installed, and never resolved from a
target's own `/.knowledge/`.

## Contents

`cq components read <this file>` returns the heading index; `--sections` addresses one.

## The two regimes

<!-- rules -->

| Regime | Form | Command |
| --- | --- | --- |
| **building** | a **serial queue** over a single isolation | `quenching-specs-execute-queue` |
| **defining** | a **parallel batch** | `quenching-specs-develop-batch` |

The criterion is one: **whatever writes to the working tree serializes; whatever does not, does
not.** `create` and `develop` take no branch, and under the `github` and `azure-boards` backends
they touch no file at all — so they fan out for real. `execute` writes code, and code collides.

**Never call the defining regime a queue.** Serialization is the declared feature of the building
one alone, and a name whose apparent object differs from what it operates is prohibited by the
command-surface naming contract.

<!-- rationale -->

Measured over one front's 20 buildable specs — 143 declared files, 190 pairs — **107 pairs (56%)
collide** on the path as declared and **150 (79%)** once the path is normalized by basename; the
largest provably disjoint batch is **4 of 20**, and the worst single spec collides with 19 of 19.
The disjunction that parallel building would require does not exist at that density, and the two
collision figures diverge because `## Impact` declares paths in inconsistent notation — which is
what makes a mechanical disjunction proof *between* specs unreliable, unlike the `[P]` check
*within* one spec, whose paths one author wrote once.

Serializing also fixes a second defect, and this is the argument that survives even where collision
is zero: **spec N's gate runs over the result of 1..N−1.** Parallel runs each measure their gates
against the same base in isolation, and the combination is first verified after the merges.

The token saving never came from concurrency, so serializing does not cost it: it comes from each
spec running in a sub-agent of its own context — an in-session queue would make spec N re-send the
previous N−1 specs' context every turn — and from **one** `conclude` instead of N.

## The queue's shape

<!-- rules -->

**Isolate once → N × `quenching-specs-execute` on that same branch → 1 ×
`quenching-specs-conclude` with no `--spec`.**

The queue **invokes and never reimplements**. `quenching-specs-execute` stops at the last commit —
the branch review, the merge and the archive belong to `conclude` — which is exactly where a queue
needs it to stop.

One branch, one pull request, against the primary branch. **Nothing is chained**: no
stacked branches, no stacked PRs, no merge queue with rebase-on-green. Chaining trades a merge
conflict for a rebase conflict and couples the specs' fates in sequence.

Each spec runs in a sub-agent of its own context, pinned to the session model — **never `haiku`** —
under [execution.md](../../references/specs-execute/execution.md)
§Delegating an executor. The conductor keeps the confirmations and the bookkeeping.

**There is no cap on N, and no soft warning.** The authorization plan shows the whole list and the
N before any isolation, and that is what the human decides on. A threshold nobody measured would
add the appearance of measurement without the measurement; if reviewing a large PR saturates, what
changes is the number the human types next run, not a rule in a command body.

## The branch carries the slugs

<!-- rules -->

Every spec the queue builds appends its slug to the branch's own `quenching-slugs:` line, by the
read-merge-write in
[isolation.md](../../references/git/isolation.md) §Marking the branch with the
specs it built — one line, rewritten and never duplicated. `quenching-specs-conclude` with no
`--spec` reads that line to resolve the whole set, which is the queue's only handoff to it.

**A blocked spec leaves the mark, not the PR.** It comes off `quenching-slugs:`, stays in `plans/`
with its `[!]`, and the final report names which one was left out and why. The PR delivers what is
finished and **never implies it carries what it does not** — which is what keeps a mid-queue stop a
result rather than a loss.

## The entry contract

<!-- rules -->

Where a spec joins derives from the `complexity` field on its `priority` record, measured against
**the fan-out floor**, and from nothing else — no invocation flag, no menu:

| `complexity`, against the floor | Where the spec enters |
| --- | --- |
| below the floor | at defining, and runs through to the end |
| at or above the floor | requires `ready`/`approved`; it is built only |

**The floor is `fanoutMinComplexity`**, declared in `.agents/quenching.json` and read through
`cq specs config --json`; a repository that declares nothing gets `high`.

**Why `high` is the default, and not a number somebody liked.** It is the cut where
[gears.md](../../references/specs-cycle/gears.md) §The scale stops answering
its own questions from evidence and starts asking a human: `low` and `medium` interrupt nobody,
`high` and `xhigh` do. **A fan-out buys the drafting, never the judgment** — and a level that asks
has no drafting to sell, because its questions would reach a sub-agent with no human to put them
to. So the floor and the ask/no-ask line are the same line, and a repository that moves the floor is
saying something about that line rather than about batch size. (Before the gears scale reached
inside the stages, the floor was `medium` — a fixed cutoff with no reason attached to it.) The four levels order `low < medium < high < xhigh`, the
same order [gears.md](../../references/specs-cycle/gears.md) §Deriving the
gears plan already scales by; an unrecognised declared floor reports the same way an unrecognised
`backend` does (`unknownFanoutMinComplexity`, the effective floor staying at `medium`) rather than
refusing.

A spec whose `complexity` **rises mid-run** leaves the run and asks for a fresh authorization,
under the same contract as
[gears.md](../../references/specs-cycle/gears.md) §Re-evaluating a gear.
`complexity` declares `[triage, create, develop]` as its writers, so the rise is a fact the run
observes — never one it stamps.

**Run the verification policy each spec declares, and never judge who chose it.** A declared policy
is authoritative by definition; separating the decision from the stamp is a frontmatter matter the
run cannot settle and does not attempt.

## Classifying a block

<!-- rules -->

A block is **declared where it is judgment and measured where it is verifiable**.

| Classification | Who decides | What the run does |
| --- | --- | --- |
| **local** | the spec's executor | mark `[!]` and move to the next spec |
| **contaminating** | the spec's executor | stop the run and ask |
| **red gate** | the declared gate, after each spec | stop the run, whatever the classification above said |

Only the executor knows whether the pending decision changes the specs after it, which is why the
classification is its call; the declared gate is the objective floor underneath.

## The recursive return

<!-- rules -->

A run may absorb the work it revealed. The **only** source is specs promoted out of
`## Discoveries`, and they pass the same §The entry contract as everything else.

| Form | What it does | Why it terminates |
| --- | --- | --- |
| **no recursion** | what the run reveals waits in `plans/` for the next one | there is no return |
| **one generation** | absorbs the specs promoted on this pass, then stops | a second generation is never offered |
| **unbounded fixpoint** | repeats until a pass promotes nothing | the entry contract filters: at or above the fan-out floor requires `ready`/`approved`, so it **never enters a return on its own** |

All three are **always presented** in the authorization plan, alongside the chosen form and the
human's own stopping criterion. Which arrives pre-marked is not settled: until a real run absorbs a
promoted spec and says whether the second generation is worth what it adds to the PR, pre-mark **no
recursion** and say on screen that it is the provisional default.

The third form is the one that can fail to terminate if work generates work, and the entry contract
is what bounds it: a promoted spec that needs `ready`/`approved` leaves the return and waits for a
human.
