---
type: standard
title: When a command's plan gate may drop
description: The two protected classes — a code-coupled item, an irreversible cycle action — are the whole test, and a command in which neither occurs has nothing to confirm; what replaces the approval window when the gate goes (the record's URL, announced before any read and repeated in the report), the difference between the confirmation that drops and the consolidation that stays, what still stops the pass either way, the three intermediate forms measured and rejected, and the three conditions under which a gear's authority replaces the person at the go/no-go
resource: plugins/quenching/commands/**, plugins/quenching/assets/references/align/convergence.md, plugins/quenching/assets/references/specs-develop/questions.md
tags: [automation, commands, gates, confirmation, cost, turns]
timestamp: 2026-08-25
audience: both
authority: background
source: spec revisar-fluxo-do-develop-custo-e-gates, distilled at its conclude (2026-08-16); §When authority replaces the person added on 2026-08-22 by the reform that made the gear (`priority.complexity`) govern the interior of `/quenching:specs:develop` — under the `low` gear the pass stamps `approved` on its own authority, with `by: low-gear` in the record, and that is the first time a go/no-go has left the pass in this repository; the post-merge measurement is still owed, now for both changes — the criterion and the three rejected alternatives come from its `## Design` and its `## Alternatives Considered`, and the measured application is `/quenching:specs:develop`, the first command to run without a plan gate; the cost claim that motivated it (<= 4M for work equivalent to a 9.73M baseline over 100 turns) is still **unmeasured post-merge**, and that measurement is the graduation condition
maintainer: quenching
---

# When a command's plan gate may drop

A **plan gate** is the stop where a command presents what it is about to write and waits for an OK.
It costs a pair of turns per unit of work, and every turn re-sends the whole conversation
([context-discipline.md](context-discipline.md) §Emit fewer turns per unit of work). This document
is the test that decides whether that stop is buying anything.

## The criterion

<!-- rules -->

> A plan gate protects exactly two classes: **a code-coupled item** and **an irreversible cycle
> action**. A command in which neither occurs **has nothing to confirm**, and its gate is cost with
> nothing on the other side.

The two classes are the same ones
`plugins/quenching/assets/references/align/convergence.md`
§The cycle-authorization contract already protects — this criterion invents no third one, and a
command does not lose its gate for being cheap, short or "low-risk". It loses it for containing
neither of the two.

**The confirmation drops; the consolidation stays.** They are different things and only the first
is the gate. A command that accumulated and wrote once goes on accumulating and writing once — what
goes is the wait, never the presentation. A plan narrated whole and then applied is reviewable; six
scattered edits are not, gate or no gate.

**What still stops the pass after the gate drops:**

- the questions the work itself asks — an `AskUserQuestion` whose answer changes what gets written
  is not a plan gate and does not go with it;
- any go/no-go that is the **sole origin** of a record of human judgment — unless the record writes
  down **whose** authority stamped it (§When authority replaces the person).

<!-- rationale -->

The gate exists to give the human the chance to block a write they cannot undo, or one that leaves
the command's scope and enters the repository's. Where none of that is possible, the stop is not
protecting — it is charging a pair of turns per bank to re-obtain an authorization the invocation
already gave.

## The review window replaces the approval window

<!-- rules -->

With the stop removed, the human no longer has a point of intervention **inside** the pass. The
substitute is the **external record where the work shows up** — an issue, a work item, a file — and
the command has two obligations because of it:

- **announce the record's URL before any read**, so the window is open while the pass runs, and not
  after it;
- **repeat it in the report**, because a pass that wrote without a gate ends by pointing at the one
  place where that write can be read and corrected.

The URL comes out of data the command already fetches. A command that would need **one more call**
to obtain it has not won this trade: it spent in tool calls what it saved in turns.

<!-- rationale -->

The idea that review has disappeared is the error this pair of obligations prevents. Review moved in
time: it was synchronous and blocking, and becomes asynchronous and about the result — and an
asynchronous review over an address nobody received is what would be a review that does not exist.

## When authority replaces the person

<!-- rules -->

A go/no-go may leave the pass — and only under the three conditions, together:

1. **The human declared the mode beforehand.** The level is on disk (`priority.complexity`), it was
   written by `triage`, `create` or `develop` with the scale in front of someone, and it is the
   level — not the command — that waives the stop. The authorization belongs to the **mode**, never
   to that one spec.
2. **The record writes down the provenance.** `approved: {date, by}` — `by: human` when a person
   answered, `by: low-gear` when the level authorized the mode and the pass stamped it. A record
   that does not say whose word it is cannot tell the two apart, and that is where the waiver stops
   being delegation and becomes falsification.
3. **The review window counts double.** The record's URL is announced before any read and repeated
   in the report, and the report **names** the automatic stamp on a line of its own. A stamp nobody
   asked for that the report does not mention is indistinguishable from an invented one.

With any one of the three missing, the stop stays.

<!-- rationale -->

The criterion in §The criterion has not changed: the two protected classes are still the same, and
`approved` was never one of them — it was the third thing that stopped the pass, and it stopped it
by being the **sole origin** of a fact. What provenance changes is exactly that: there are now two
declared, distinguishable origins, and whoever reads the record chooses which to trust. Without the
field, waiving the go/no-go would erase the fact; with it, the waiver is a second entry in the same
ledger, and review goes on existing — asynchronous, about the result, at the address the pass
announced twice.

## Three intermediate forms, measured and rejected

<!-- rationale -->

All three preserve some stop. None survived the same test:

| Form | Why it lost |
| --- | --- |
| **Pass authorization** — one OK at the opening authorizes the whole pass, the plan stays narrated before each write | charges a stop that protects nothing: if neither of the two classes occurs in the pass, neither occurs at its opening |
| **Confirmation by exception** — the OK survives only where the edit overwrites or contradicts content already present | adds a classification rule every bank then has to apply — more doctrine to solve an excess of doctrine, and the classification is judgment, not a test |
| **Cutting only the crossing between stages, keeping each stage's gate** | cuts ~1 stop per pass and does not deliver the model: the per-stage confirmation is precisely the stop the problem names |

The pattern across the three is the same: they negotiate *how many* stops, when the question is
whether **that** stop protects anything. A stop that does not protect does not get better by being
rare.

**Merging stages is not the third form.** `/quenching:specs:develop` later came to compose and
refine in a single pass, with one edit — and that does not reopen the table above. The third form
preserved *each stage's gate*; there has been no stage gate here since this criterion was applied to
the command (2026-08-16), and what gets merged are crossings and reads, never questions. The command
changed **when** a question is asked, never **whether** it is asked — and the rule above, that a
question whose answer changes what gets written does not go with the gate, is what keeps the merge
from becoming a cut.

## Why this is born `background`

<!-- rationale -->

The criterion is argued and has been applied with a consistent result to four commands — one lost
its gate, three kept theirs for containing the protected classes. What was **not** measured is the
cost claim that motivated all of it: that the pass without a gate costs a fraction of what it used
to. Until that measurement exists, what is proved is that the gate was not protecting — not that
removing it bought what was expected. Graduation to `current` is that measurement.
