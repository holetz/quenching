---
allowed-tools: Bash(cq:*), Bash(cq.cmd:*), Read, Grep, Glob, Edit, Bash(python3:*), Bash(py:*), AskUserQuestion, Task
---

# /quenching-specs develop — compose a spec, argue with it, and settle its go

**Input**: `$ARGUMENTS` — a spec id, or a description of what to work on.

Takes a spec from wherever it is toward being worth building, in ONE pass: resolving what an
executor discovered, **composing** a bare `## Problem` into a closed ten-section spec,
**refining** that spec by arguing with it, and closing on the go-ahead.

**Two operations, and both are derived.** **Compose** is monotonic — it fills what is absent and
closes the ready gate. **Refine** may overturn anything it finds, the proposal included. The
spec's **derived stage** says where composing starts; a **concrete signal** (or the human's ask)
says whether refining runs.

**Every `§X` below is an address, and it is loaded as one — never by opening the file.**

```text
components_read(verb="read", path="<the cited file>", sections=["§The pass", "§The four shared mechanics"])
```

One call, N sections, no frontmatter; a unique prefix resolves. `rules_only=true` narrows further to
the `<!-- rules -->` half where a section carries the marker, and returns the whole section, saying
so, where it does not.

**Every step is a file of its own.** This body is the index: it carries the doctrine, the batching
contract and the invariants every stage obeys. A step runs only after its file is loaded —
`components_read(verb="read", path=".claude/skills/quenching-specs/references/specs-develop/<file>")` —
and that file loads the `§` sections its own step uses, never the whole pass up front.

## Where the rest lives

Each step's file carries what only that step uses, so a stage run loads no more than its own: step 1
resolves `cq`, and its read batch (§The batching contract) opens the pass; step 3 carries the
rule that no turn only announces a call; step 3b reads `/docs/` by section; step 4 carries the rule
on recommendations inside a question; step 7 carries the explicit-none rule and the apply batch.

## Doctrine

- **The stage says where composing starts; the calculated pass says who answers and whether refining
  runs.** `specs_read(verb="status", spec=<id>)` returns the stage. Never infer the stage by reading
  the headings, never ask the human which mode they want, and **never ask them to choose a depth**
  — the session calculates it. It enumerates the decisions the execution needs and classifies each
  as resolved by evidence, dependent on the human, or very costly to undo. None depends on the
  human: simple track, the session composes everything, announces what it will do and stamps
  `by=session`. Some do: complex track, questions in batches, then `by=human`. A conductor running
  `--autonomous` declares **autonomy**: the same composition, no questions and no refine, stamp
  `by=orchestrator-forced`; it writes nothing to `priority`, so `complexity` on disk stays what it
  was.
- **Nothing shortens a stage that runs.** The same axes, lenses and gate symptoms are worked on
  every track, and what changes is who answers them.
  Everything about *how* a stage runs is owned by `questions.md` §The four shared mechanics
  §Who answers, which the steps that need it load.
- **A pass lands ONE edit.** Compose and refine accumulate and write together, so the spec never
  holds a half-composed state and never holds a draft refine already superseded. An abandoned pass
  leaves the spec exactly as it was.
- **`complexity` is re-evaluated at the close, never mid-pass.** The close's own recommendation IS
  that re-evaluation where it names a raise; where the pass merely outgrew its size, the evidence
  that moved it is named and the depth proposed. A pass that changed no size proposes nothing.
- **Every pass reviews `tags` in silence** — `/quenching-specs create` presumes them. The review is
  narrated in step 6's consolidated plan and applied in step 7's single edit, with no screen of its
  own.

## Workflow

Run the steps in order; load a step's file when it begins and not before. The file holds the step's
text and its `Done when:`. The files sit in `specs-develop/` beside this body.

| Step | File |
| --- | --- |
| 1. Resolve the spec, and announce where it lives | `step-1.md` |
| 2. Read the spec's STATE — not its body | `step-2.md` |
| 3. Derive the pass, and name it | `step-3.md` |
| 3b. Load what THIS pass needs — and nothing more | `step-3b.md` |
| 3c. Run the dependency sweep — once, at the pass's open | `step-3c.md` |
| 3d. Enumerate the surface refinement | `step-3d.md` |
| 4. Compose | `step-4.md` |
| 5. Refine — where it runs | `step-5.md` |
| 6. Consolidate the edit, and narrate it | `step-6.md` |
| 7. Apply, verify, and record what the pass earned | `step-7.md` |
| 8. Close on a recommendation, and report | `step-8.md` |

Steps 1 and 2 are one call (§The batching contract), so load `step-1.md` and `step-2.md` together.

## Invariants to never violate

- **Never edit anything but the spec.** The pass writes the spec and nothing else — no workflow,
  skill, reference, structure, `docs/` file or code, the surface refinement's targets included.
  What the ask plans lands in `## Tasks`; writing it belongs to `/quenching-specs execute`, one
  task at a time. A pass that edits the surface has broken the boundary that lets it obey the
  doctrine it is changing.
- **Never write into `/docs/`.** A durable rule a question surfaces routes to `/quenching-knowledge add`, an
  understanding to `/quenching-knowledge learn`, a term to `/quenching-knowledge define` — **offered, never
  auto-written**. The rules a spec *proves* are written during execution, not during definition.
- **Never write into `## Tasks` what the merge owns.** A version bump, a changelog entry, a manifest
  re-stamp; the `/docs/` the work *revealed* rather than declared; the cycle's own closing actions
  (review, archive, distil, merge, open the PR) — all three belong to `/quenching-specs conclude`,
  which settles them once what the release *is* is knowable. A standard this spec **declares** under
  `## Impact` still gets its own checkbox and still must: the axis is declared versus revealed,
  never docs versus code.
- **Park an out-of-scope follow-up; never mint a spec for it.** A finding this pass raised that does
  not belong to the spec being developed becomes ONE line of `## Discoveries` on that same spec —
  `specs_write(verb="discover", spec=<id>, text=<finding>)` — landed inside the step 7 edit, never as a loose call
  mid-stage. Turning a follow-up into its own spec stays `/quenching-specs conclude`'s. This route
  is not an offer: nothing is created, so there is nothing to ask for.
- **Inside a develop pass, `specs_write(verb="create")` runs only as the discoveries stage's `promoted:`
  resolution.** Nothing else here mints a spec.
- **Changing the spec's intent is refine's, and only with a human.** Compose may not overturn what a
  human settled; refine may, and a change to `## Proposal` is always put to the human rather than
  taken. Where no human is present the pass never reached refine, so the licence never runs
  unattended — and a request that replaces the spec's subject outright is still a fresh
  `/quenching-specs create`, not a rewrite of what was already agreed.
- **Never write a section that was not narrated first.** The consolidated plan is shown in full
  (step 6) and then applied.
- Never write anything mid-stage — accumulate across the whole pass, then apply once.
- **Never group two questions whose answers can change each other**, and never ask alone what could
  have travelled with them. Grouping is by dependence, never by convenience, and every question
  carries a recommendation either way. **And never drop a question for cadence:** this command
  changes when a question is asked, never whether it is.
- Never ask the human to choose a mode; the derived stage says where composing starts — **and never
  ask them to choose a depth**: the calculation chooses it, or a conductor declares `autonomous` in
  the invocation.
- **Never let a simple-track or `autonomous` pass ask a question, and never let `autonomous` refine.**
  An item no evidence answers becomes an `## Open Decisions` line with how it will be decided.
  Inventing the answer and asking anyway are the two failures here, and the second is the one that
  breaks what the track promised. **Never stamp `session` while a decision still depends on the
  human.**
- **A sub-agent may read; it may never ask, write, or decide.** The evidence sweep of step 3b
  returns a table. Every question, every `.agents/quenching/bin/cq specs` call and every confirmation stays here.
- **The dependency sweep's map is written by the orchestrator; the sub-agent never touches the
  spec.** Step 3c's sub-agent returns a table too, same as step 3b's — the map lands only inside
  step 7's own consolidated write, into `### Mapa de dependências` under `## Design`.
- **Never hand this command file `context: fork`** — the complex track asks the human its own
  questions, and step 3c's read-only sub-agent is a step inside that, never a delegation of it.
- **Never open a cited reference as a file.** `§X` is an address, loaded through
  `components_read(verb="read", path=…, sections=[…])`; and never hoist into the preamble what only one branch reads.
- Never derive the pass from what it intends to write — only from disk, once, and the disk confirms
  at the close where it landed. A divergence re-enters; it is never absorbed in silence.
- Never run a stage the pass did not name. The whole pass is announced before the first question.
- Never delete a heading to signal that nothing applies — write `- none — <reason>`.
- Never invent an explicit none the human did not give, and never invent an answer to an
  unanswered question: it goes in `## Open Decisions` with how it will be decided, which is a
  result, not a failure.
- Never create a heading you are not filling in the same edit.
- **Never fabricate a record, and never misattribute one.** `refined` is stamped only after a stage
  really ran — drafting from evidence counts, a pass that ran neither compose nor refine does not.
  `approved` is stamped only with a truthful `by:`: `human` when a person answered the closing
  screen, `session` when the calculation left no decision to a human and this pass stamped on its
  own authority after `ready` was proved, `orchestrator-forced` when a conductor declared
  `autonomous` and this pass stamped after `ready` was proved. `low-gear` is the historical value of
  older specs and is never written. No other path writes it.
- **`autonomous` writes nothing to `priority`.** The only record it adds is `approved` with
  `by: orchestrator-forced`; the depth on disk is never changed to match the way the pass was run.
- **Never restamp `complexity` beyond what the close authorizes**: a fall always needs a human, and
  a level a pass did not move is the latest word on it, not a value to re-propose.
- Never gate on refinement. A spec may always be built unrefined; `sp-unrefined` is a warning by
  design.
- Never rename a spec, and never rewrite its `date:` — the capture date is stamped once, at
  creation.
