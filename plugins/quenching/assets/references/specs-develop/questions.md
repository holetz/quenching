# The question banks — what `develop` asks, and how

The owner of **what** `/quenching:specs:develop` asks and **when it stops**. The command body owns the loop
(resolve → derive → ask → one edit → re-derive); this file owns the banks and the mechanics they
share, and the body never restates it.

**There is no mode to choose.** v2 asked the human to pick between `interview`, `critic`,
`premortem` and `alternatives` before it had read anything — a question the spec's own state
answers better than the human can. The bank is now **derived**, from the same stage
`specs.py status` reports, so the interrogation a spec gets is the one its content earns.

## Contents

- [Choosing the bank](#choosing-the-bank)
- [The four shared mechanics](#the-four-shared-mechanics)
- [Bank: shape](#bank-shape)
- [Bank: adversarial](#bank-adversarial)
- [Bank: gate](#bank-gate)
- [Bank: discoveries](#bank-discoveries)
- [Bank: approval](#bank-approval)
- [Recording the pass](#recording-the-pass)

## Choosing the bank

One lookup on the derived stage, taken from `specs.py status --spec <slug> --json`:

| Derived stage | Bank | The question it is really asking |
| --- | --- | --- |
| `captured` — only `## Problem` is filled | [shape](#bank-shape) | what IS this, and what shape should it take? |
| `proposed` — `## Proposal` is filled | [adversarial](#bank-adversarial) | is this the right thing to build at all? |
| `designed` / `refined` — the gate is not met | [gate](#bank-gate) | what has nobody answered yet? |
| `ready` / `approved` / `executing` | [approval](#bank-approval) | does a human say go? |

[discoveries](#bank-discoveries) is **orthogonal** — it runs at any stage, whenever `## Discoveries`
holds a line nobody has resolved, and it is the only bank that resolves rather than adds.

The stage always derives **from disk**, never from what the current pass has accumulated. That is
what makes the loop honest: a bank's answers reach the file before the next bank is chosen, so a
re-derived stage is a fact rather than a projection.

**Crossing a bank boundary is offered, never automatic.** When a bank's edit lands and the
re-derived stage selects a different one, name the next bank and what it will ask, and wait. A
human who came to sharpen a proposal did not sign up for the whole gate walk.

## The four shared mechanics

Every bank obeys all four. They are what make a pass finish.

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

The recommendation is not a formality. A pass that hands the human a bare question list has moved
the work rather than done it — the command is supposed to arrive with an opinion.

Use **AskUserQuestion** when the answer space is genuinely a small set of options (it renders as
choices and takes one click); ask in prose when the answer is open-ended. Either way: one at a
time.

### 2. Accumulate; apply in ONE edit per bank

**Nothing is written while a bank is running.** Keep a running list of
`(question, answer, target section)` and write it all at once, as a single edit the human confirms
once.

Three reasons this is not merely tidier:

- A pass abandoned halfway leaves the spec **exactly** as it was — no half-filled `## Design` whose
  decisions contradict a `## Proposal` that was never updated.
- Later answers routinely revise earlier ones. Writing answer 2 before hearing answer 6 means
  editing the same paragraph twice, and the intermediate state is never reviewed by anyone.
- One diff is reviewable. Six scattered edits are not, and the human's single OK is what authorizes
  the whole bank.

The edit lands per **bank**, not per pass. A pass that crosses two boundaries produces two
confirmed edits, and the stage between them is real.

Every bank's consolidated edit also refreshes `## Overview` to match whatever the bank just
changed — it is authored **last** within that one edit, after every other section has settled,
because it can only be correct once they have. It still sits first in the file; only its authoring
order within the pass is last. Present the refreshed Overview to the human as its own labelled
before → after block, separate from the list of other section diffs — never folded in alongside
them — and this rides inside the same one-OK edit the bank already produces, not a second
confirmation.

### 3. A declared stop condition

Each bank below states when it is **done**. Announce the stop condition when the bank starts, so
the human knows the shape of what they agreed to, and honour it — a bank that keeps finding one
more question is the free-ranging exploration this front deliberately gave up.

Three universal stops apply on top of each bank's own:

- **The human calls it.** "That's enough" ends the bank and goes straight to the consolidated edit
  with whatever was accumulated.
- **Diminishing returns.** Two consecutive questions whose answers change nothing about the spec —
  stop and say why.
- **The question is not this spec's.** A question that would read identically against any spec is
  noise. Do not ask it; do not pad the count with it.

### 4. Every answer names the section it lands in

An answer with no destination is conversation, and conversation is what gets summarized away. As
each answer arrives, record which canonical section it belongs to — that mapping IS the
consolidated edit, and an answer that maps to nothing is either out of scope (route it, per the
body's guardrails) or was not worth asking.

## Bank: shape

**Stage.** `captured` — a spec with `## Problem` and nothing else. This is the thinking bank: the
spec exists, so there is always somewhere to land, and nothing has to be reconstructed later from
conversation.

**Goal.** Turn one stated problem into a shape worth arguing with — enough that the adversarial
bank has a claim to attack.

**Where the questions come from.** The problem statement itself, read against the codebase. Ask
about, roughly in this order:

- **What is actually wrong.** Is the `## Problem` describing a symptom or a cause? What does the
  code do today — read it, do not theorize.
- **Why now.** What changed, or what does waiting cost? A problem with no answer here is a plan to
  leave in `plans/`, and saying so is a result.
- **The shape.** Two to four genuinely different shapes the answer could take, in a table:
  approach, what it costs, what it buys, what it forecloses. Recommend one.
- **The boundary.** What is the nearest thing someone will mistake for in-scope? That answer is
  `## Out of Scope`, and it is cheapest to write now.
- **What would make this not worth doing.** The honest version of a go/no-go.

A good ASCII diagram — current flow, proposed flow, the state machine — is worth several of these
questions and often replaces one.

**Lands in** `## Proposal` (the shape), `## Out of Scope` (the boundary), `## Design` /
`## Alternatives Considered` when the shapes table produced a real comparison, and `## Overview` —
this is the bank that first writes it, the same way it first writes `## Proposal`.

**Stop when** `## Proposal` states what will be true afterwards that is not true now, and the human
would recognise the spec as describing their idea. Not when the gate is met — that is two banks
away.

## Bank: adversarial

**Stage.** `proposed` — there is a claim on the page, so it can be attacked. This bank is the
disagreement the gate never requires: nothing about filling sections forces anyone to have
**disagreed** with the spec.

**Goal.** Make the proposal survive the argument, or change it.

It runs three lenses. Use the one the spec's own state argues for; a spec that deserves two gets
two, in this order.

### Lens: alternatives — when `## Alternatives Considered` is absent, empty, or records one option

Generate **two to four genuinely different** approaches — different in shape, not in parameter.
"Same design with a bigger cache" is not an alternative. Include, where they apply, the three that
are almost always available and almost never written down: **do nothing** (what happens if this is
not built?), **the smallest thing that could work**, and **buy or borrow instead of build**.

Table them — approach, cost, benefit, what it forecloses — state a recommendation with the
reasoning, and ask the one question: does the spec keep its approach, or switch?

**Do not strawman.** Each alternative is stated as its strongest advocate would state it; one that
cannot be written down convincingly was not a real alternative and does not belong in the table.

Lands in `## Alternatives Considered` — **including the rejected ones and why they lost**, which is
the entire point: the next person to have the same idea reads why it was already turned down.

### Lens: critique — when the spec is large, reaches into product code, or declares an uncovered standard

Assume the spec is wrong and find where. Be specific — a critique that could be levelled at any
spec is worthless. Aim at:

- **The premise.** Does `## Problem` describe a problem anyone actually has? What is the evidence?
- **Scope inflation.** Which part of `## Proposal` does not follow from `## Problem`? What survives
  if it is cut?
- **Cheaper paths.** What buys 80% of the benefit for 20% of the change?
- **Contradiction with a binding contract.** Does any task violate a `docs/standards/` doc? Name
  the doc and the line.
- **Permanent cost.** What does this add forever — surface, config, a rule to remember? Is the
  benefit recurring or one-off?
- **Reversibility.** If this turns out wrong in a month, what does undoing it cost?
- **The load-bearing assumption.** Which single unstated assumption, if false, invalidates the spec?

**Every criticism carries a proposed remedy**: cut it, defer it, shrink it, or accept it with a
stated reason. A criticism with no remedy is a complaint.

Lands in `## Out of Scope` (a scope cut taken), `## Open Decisions` (one that needs evidence), or
the spec's own sections where the remedy rewrites them.

### Lens: premortem — when the spec is risky or irreversible: a migration, a rename with a blast radius, a release

State the frame out loud: *"It is three months from now. This spec was built and it went badly.
What happened?"* — then generate the failure stories from the spec's actual content, not from a
generic risk list.

Cover at least: what broke for a user of this repo; what half-landed and left an inconsistent
state; what the spec assumed about existing code that was not true; what the tasks did not cover;
who could not use the result. For each story: how likely, how bad, and **how it is detected** — a
failure nobody notices is worse than a loud one.

Then convert. Every story becomes exactly one of: a **mitigation task** in `## Tasks`; a **risk
with a named mitigation** in `## Risks`; an **accepted risk**, recorded with the reason it is
acceptable; or a **scope cut** into `## Out of Scope`. A story that converts into nothing was not a
real risk — drop it and say so.

**Stop when** every criticism has been answered, every failure story converted, the alternatives
table exists and the human has chosen — and the spec's biggest remaining risk is one they
explicitly accepted.

## Bank: gate

**Stage.** `designed` or `refined`, with `specs.py next` still reporting `write_section`.

**Goal.** Close the ten-section ready set, honestly. This is the bank that most easily degrades
into filling headings to make a check pass, and the explicit-none rule is the whole defence.

**Drive it off the tool, never off a reading of the file.** `specs.py next --spec <slug> --json`
returns the first `missing` or `malformed` heading and the full list behind it. Ask about that
heading; do not choose one by eye.

**Where the questions come from.** The gap itself, in the spec's own terms:

- a section that says `- none` with no reason attached — is that a decision or an omission?
- `## Out of Scope` absent → what was ruled out, and what is the nearest in-scope lookalike?
- `## Validation` absent or vague → what exact command proves this worked, and what must it print?
- `## Impact` declaring a standard no task names, or a task writing a doc `## Impact` never
  declared;
- a `## Tasks` item whose completion nobody could judge ("improve error handling");
- a task ordering that has step 4 depending on step 7;
- a term the spec uses in a sense the repo's glossary does not.

This bank also settles the two declarations nothing else owns: the **`verification` policy** (one of
the three values in [spec-driven.md](spec-driven.md) §Frontmatter, asked once and written to
frontmatter, so `execute` never has to guess mid-build) and the parsed `### Standards this spec will
write into docs/standards/` sub-heading under `## Impact`.

**Stop when** `specs.py next` stops reporting `write_section` — every gate section answered with
content or a reasoned `- none`, every task with a judgeable completion, no `## Impact` path
uncovered.

## Bank: discoveries

**Stage.** Any. Runs whenever `## Discoveries` holds a line with no resolution on it.

**Goal.** Empty the queue an executor filled indiscriminately. Whether a discovery is worth acting
on is this bank's judgment, never the executor's — which is exactly why it was captured without
one.

Ask about each unresolved line, one at a time, with a recommendation. Every line resolves **in
place**, so provenance is never lost:

```markdown
- the rate limiter double-counts retries -> promoted: fix-retry-accounting
- the config loader is slow on cold start -> dismissed: acceptable, runs once
```

Three resolutions and nothing else:

| Resolution | When | What it costs |
| --- | --- | --- |
| `promoted: <slug>` | it is work someone will do, and the front does not already hold it | one `specs.py list --json` to check, then one `specs.py new` — offer it, and write the slug back |
| `folded: <section>` | it changes THIS spec | the answer lands in that section in the same edit |
| `dismissed: <reason>` | it is real but not worth acting on, or another spec already covers it | one line, and the reason is the whole value |

**Check the front before minting.** `promoted:` reads the open specs first — `specs.py list --json`
— and where one of them already covers the line, the resolution is
`dismissed: already covered by {slug}` instead. That is the third resolution doing its ordinary
job, not a fourth token: the resolutions stay `promoted:`, `folded:` and `dismissed:`, and the slug
is the reason. A queue filled by executors that could not see each other produces the same finding
several times, so the duplicate arrives through the front door and has to be turned away there.

A line is never deleted, and never left unresolved with a shrug. `dismissed: acceptable` with no
reason is the failure mode to hunt for.

**Stop when** every line carries a resolution.

## Bank: approval

**Stage.** `ready`, or the gate is met and `approved` is unset.

**Goal.** Get the one fact no derivation reproduces: **a human said go.**

This bank asks a single question, and it is the only bank that adds nothing to the body. Show what
the spec now commits to — the proposal in one line, the task count, the `verification` policy, the
declared `docs/standards/` paths, the biggest accepted risk — and ask for the go-ahead.

On yes, stamp `approved: {date: YYYY-MM-DD}` into frontmatter. On no, ask what would have to change
and route it back to the bank that owns it.

**The gate is a floor, not a verdict.** `ready` means ten sections have content; it does not mean
the spec is good. And approval is not a gate either — `execute` on an unapproved spec asks inline
and stamps rather than refusing, so declining here costs nothing but a question later.

**Stop when** the human has answered. One question, one answer, done.

## Recording the pass

`refined: {mode, date}` records that a real interrogation happened and which bank ran it. Stamp it
**only** for the two banks that interrogate an existing claim:

| Bank | Stamps `refined`? | Why |
| --- | --- | --- |
| shape | no | it creates the claim; it cannot also be the challenge to it |
| adversarial | `mode: adversarial` | the spec was argued with |
| gate | `mode: gate` | every gap was questioned rather than filled in silently |
| discoveries | no | it resolves a queue; it does not interrogate the spec |
| approval | no | it authorizes; `approved` is its own record |

A pass that ran both stamping banks records the **deepest** one reached, in the bank order above —
that is the strongest claim the pass supports. The record is `writeOnce: false`: a later pass
restamps it, because a second interrogation is a new fact, not a correction of the old one.

**Never fabricate it.** `refined` is written only after real questions got real answers. It is the
one field whose entire value is that it cannot be inferred from the sections, so a stamp on a pass
where nobody was asked anything makes the field worthless everywhere.
