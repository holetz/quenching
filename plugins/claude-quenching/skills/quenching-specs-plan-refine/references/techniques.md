# Refinement techniques — the four modes and the mechanics they share

The owner of **how** `quenching-specs-plan-refine` interrogates a plan. The skill body owns the
workflow (select plan → choose mode → read → run → one edit → record); this file owns the
technique, and the body never restates it.

A mode is a **parameter of one action**, not a different skill: same target (one plan's
artifacts), same output (one consolidated edit), same terminating contract. Only the questions
differ.

## The three shared mechanics

Every mode obeys all three. They are what make a refinement finish.

### 1. One question at a time, with a recommendation

Ask **one** question. Wait for the answer. Then ask the next — chosen in light of what was just
said, not from a list written in advance.

A batch of five questions gets one shallow answer covering the easiest of them. A single question
gets a real one, and lets the next question be sharper for having heard it.

Every question carries **an inline recommendation and the reasoning behind it**, so the human can
answer in one word:

> **Weak** — "What should the failure budget be?"
> **Strong** — "How many attempts before a task is declared blocked? I'd say five: enough to
> absorb a flaky test or a missing import, short enough that a genuinely wrong approach stops
> burning tokens. Agree, or is this suite slow enough that five is too many?"

The recommendation is not a formality. Refinement that hands the human a bare question list has
moved the work rather than done it — the skill is supposed to arrive with an opinion.

Use **AskUserQuestion** when the answer space is genuinely a small set of options (it renders as
choices and takes one click); ask in prose when the answer is open-ended. Either way: one at a
time.

### 2. Accumulate; apply in ONE edit at the end

**Nothing is written to any artifact during the interrogation.** Keep a running list of
`(question, answer, target artifact + section)` and write it all at once, as a single plan the
human confirms once.

Three reasons this is not merely tidier:

- A refinement abandoned halfway leaves the plan **exactly** as it was — no half-updated proposal
  whose `## Why` now contradicts its `## What Changes`.
- Later answers routinely revise earlier ones. Writing answer 2 before hearing answer 6 means
  editing the same paragraph twice, and the intermediate state is never reviewed by anyone.
- One diff is reviewable. Six scattered edits are not, and the human's single OK is what
  authorizes the whole pass.

### 3. A declared stop condition

Each mode below states when it is **done**. Announce the stop condition when the mode starts, so
the human knows the shape of what they agreed to, and honour it — a refinement that keeps finding
one more question is `quenching-specs-explore` wearing the wrong name.

Three universal stops apply on top of each mode's own:

- **The human calls it.** "That's enough" ends the mode and goes straight to the consolidated edit
  with whatever was accumulated.
- **Diminishing returns.** Two consecutive questions whose answers change nothing about the
  artifacts — stop and say why.
- **The question is not this plan's.** A question that would read identically against any plan is
  noise. Do not ask it; do not pad the count with it.

## Mode: `interview` (default)

**Goal.** Fill the gaps the artifacts left — the questions a careful reviewer would ask on first
read, in the plan's own terms.

**Where the questions come from.** Read the artifacts against the required-section contract and
attack what is missing or hollow:

- a section that says `- none` with no reason attached — is that a decision or an omission?
- `## Out of Scope` absent → what was ruled out, and what is the nearest thing someone will
  mistake for in-scope?
- `## Validation` absent or vague → what exact command proves this worked, and what must it print?
- `## Impact` declaring a standard no task names, or a task writing a doc `## Impact` never
  declared;
- a `tasks.md` item whose completion nobody could judge ("improve error handling");
- a task ordering that has step 4 depending on step 7;
- a term the plan uses in a sense the repo's glossary does not.

**Stop when** every required section is answered (with content or a reasoned `- none`), every task
has a judgeable completion, and no `## Impact` path is uncovered.

## Mode: `critic`

**Goal.** Attack the plan the way a hostile reviewer would, and make it survive or change.

**Stance.** Assume the plan is wrong and find where. Be specific — a critique that could be
levelled at any plan is worthless. Aim at:

- **The premise.** Does the `## Why` describe a problem anyone actually has? What is the evidence?
- **Scope inflation.** Which part of `## What Changes` does not follow from `## Why`? What
  survives if it is cut?
- **Cheaper paths.** What buys 80% of the benefit for 20% of the change?
- **Contradiction with a binding contract.** Does any task violate a `docs/standards/` doc? Name
  the doc and the line.
- **Permanent cost.** What does this add forever — surface, config, a rule to remember? Is the
  benefit recurring or one-off?
- **Reversibility.** If this turns out wrong in a month, what does undoing it cost?
- **The load-bearing assumption.** Which single unstated assumption, if false, invalidates the
  plan?

**Discipline.** Every criticism carries a proposed remedy: cut it, defer it, shrink it, or accept
it with a stated reason. A criticism with no remedy is a complaint.

**Stop when** every criticism has been answered — accepted into an edit, or rejected with a reason
recorded in the plan (`## Out of Scope` for a rejected scope cut, `## Open Decisions` for one that
needs evidence).

## Mode: `premortem`

**Goal.** Assume the plan shipped and failed. Work backwards to what killed it, then fix it now.

**Opening.** State the frame out loud: *"It is three months from now. This plan was applied and
it went badly. What happened?"* — then generate the failure stories from the plan's actual
content, not from a generic risk list.

Cover at least: what broke for a user of this repo; what half-landed and left an inconsistent
state; what the plan assumed about existing code that was not true; what the tasks did not cover;
who could not use the result. For each failure story: how likely, how bad, and how it is detected
— a failure nobody notices is worse than a loud one.

**Then convert.** Every story becomes exactly one of:

- a **mitigation task** in `tasks.md`;
- a **risk with a named mitigation** in `design.md` `## Risks`;
- an **accepted risk**, recorded with the reason it is acceptable;
- a **scope cut** into `## Out of Scope`.

A failure story that converts into nothing was not a real risk — drop it and say so.

**Stop when** every story has been converted, and the plan's biggest remaining risk is one the
human has explicitly accepted.

## Mode: `alternatives`

**Goal.** Surface the shapes nobody weighed, so the chosen one is a choice rather than the first
idea.

**Procedure.** Generate **two to four genuinely different** approaches — different in shape, not
in parameter. "Same design with a bigger cache" is not an alternative. Include, where they apply,
the three that are almost always available and almost never written down: **do nothing** (what
happens if this is not built?), **the smallest thing that could work**, and **buy/borrow instead
of build**.

Put them in a table — approach, what it costs, what it buys, what it forecloses — and state a
recommendation with the reasoning. Then ask the one question: does the plan keep its current
approach, or switch?

**Discipline.** Do not strawman. Each alternative is stated as its strongest advocate would state
it; if an alternative cannot be written down convincingly, it was not a real alternative and does
not belong in the table.

**Stop when** the table exists, the recommendation is made, and the human has chosen. The result
lands in `design.md` `## Alternatives Considered` — **including the rejected ones and why they
lost**, which is the entire point: the next person to have the same idea reads why it was already
turned down.
