# The question banks — what `develop` asks, and how

The owner of **what** `/quenching:specs:develop` asks and **when it stops**. The command body owns the loop
(resolve → derive → ask → one edit → re-derive); this file owns the banks and the mechanics they
share, and the body never restates it.

The bank is **derived** from the same stage `cq specs status` reports, never chosen by the human, so
the interrogation a spec gets is the one its content earns.

## Contents

`cq components read <this file>` returns the heading index; `--sections` addresses one.

## Choosing the bank

One lookup on the derived stage, taken from `cq specs status --spec <slug> --json`:

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

**The gear is orthogonal to this lookup.** `priority.complexity` never changes WHICH bank runs —
the derived stage is the only input to the table above. It changes who answers the bank once it is
chosen (§Who answers — the gear decides), and at `xhigh` it forces one lens of the adversarial bank
that the spec's own state might not have argued for.

**Crossing a bank boundary is automatic and narrated, never offered.** When a bank's edit lands
and the re-derived stage selects a different one, name the next bank and what it will ask, then
continue. The stage is a fact derived from disk; offering the crossing asks the human to decide
again what the completed bank already decided.

## The four shared mechanics

Every bank obeys all four.

### 1. Grouped by dependency, and every question carries a recommendation

<!-- rules -->
**A question travels with the ones whose answers cannot change it, and alone otherwise.**

- **Independent → one call.** Where answering A would not change what B asks, ask A and B together
  in a single **AskUserQuestion** — up to the harness cap of **four per call**, each with its own
  options.
- **Dependent → sequential.** Where the next question's *content* depends on the last answer, ask
  it alone, wait, and choose the next in light of what was just said rather than from a list
  written in advance.

Which shape a bank takes is a property of the bank, stated with it:

| Bank | Shape | Why |
| --- | --- | --- |
| [discoveries](#bank-discoveries) | grouped | every line is independent, and all of them take the same fixed set of three resolutions |
| [gate](#bank-gate) | grouped | `cq specs next` returns the missing headings, and a heading's answer does not move another's |
| [shape](#bank-shape) | sequential | what is actually wrong decides which shapes are worth tabling at all |
| [adversarial](#bank-adversarial) | sequential | a criticism once answered rewrites the next one |

Every question carries **an inline recommendation and the reasoning behind it**, so the human can
answer in one word — in a grouped call, the recommended option is listed **first and marked
"(Recommended)"**:

> **Weak** — "What should the failure budget be?"
> **Strong** — "How many attempts before a task is declared blocked? I'd say five: enough to
> absorb a flaky test or a missing import, short enough that a genuinely wrong approach stops
> burning tokens. Agree, or is this suite slow enough that five is too many?"

Use **AskUserQuestion** when relevant.

The shape a bank takes above is its shape **when it asks at all**. Whether it asks is §Who answers
— the gear decides, which is upstream of all four mechanics.

<!-- rationale -->
The rule this replaced was *never batch* — absolute, and stronger than its own reason. That reason
was always about **dependence**: a batch of five questions gets one shallow answer covering the
easiest of them, and a single question lets the next be sharper for having heard it. Neither clause
says anything about two questions that cannot reach each other, and paying a full round trip for
each of those buys nothing — every turn re-sends the whole conversation, so a question asked alone
costs the preamble again.

Measured on this repository's own transcripts, question turns are **not** where this command's
tokens go: real `/quenching:specs:develop` runs made 2–5 `AskUserQuestion` calls, against whole-file
reference reads worth ~900k token-turns in a single run. Grouping is here because the old rule
overreached, not because it closes a leak.

The recommendation is not a formality. A pass that hands the human a bare question list has moved
the work rather than done it — the command is supposed to arrive with an opinion.

### 2. Accumulate; apply in ONE edit per bank

<!-- rules -->
**Nothing is written while a bank is running.** Keep a running list of
`(question, answer, target section)` and write it all at once, as a single narrated edit. The
accumulation and the one-edit-per-bank shape are the mechanic; the confirmation that used to gate
them is not. Invoking the command is the authorization, and the human's window on the edit is the
spec's own URL in the backend.

The edit lands per **bank**, not per pass. A pass that crosses two boundaries produces two edits,
and the stage between them is real. That boundary is also the width of the exposure: an abandoned
pass can leave a spec half-written between two banks, never between two sections of one bank.

<!-- rationale -->
- Later answers routinely revise earlier ones. Writing answer 2 before hearing answer 6 means
  editing the same paragraph twice, and the intermediate state is never reviewed by anyone.
- One diff is readable. Six scattered edits are not — and that one diff is what the human reads in
  the backend afterwards.
- The gate left when it was priced: this command edits no code and takes no irreversible cycle
  action, so the pair of turns each bank spent waiting protected nothing the backend's own edit
  history does not now carry. Its one real guarantee — a pass abandoned halfway left the spec
  **exactly** as it was — is narrowed by the per-bank boundary above, not recovered.

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

## Who answers — the gear decides

<!-- rules -->

The banks below are the engine of **content**, and they are the same at every gear: the same axes,
the same lenses, the same seven gate symptoms, the same stop conditions. **A gear never shortens a
bank.** What it decides is who answers it — the pass, from evidence, or the human.

The gear is `priority.complexity`, read from the same `cq specs status --spec <slug> --json`
payload that reports the stage
([gears.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-cycle/gears.md) §The scale). Absent reads
as `high`.

| Gear | How the bank runs |
| --- | --- |
| `low` · `medium` | **the pass answers.** Every item is answered from what the spec, the codebase, the `/.knowledge/standards/` its `## Impact` declares and `/.knowledge/glossary.md` support. An answer resting on something unproved is written with **the assumption named in the text it lands in**. Anything no evidence answers becomes a `## Open Decisions` line carrying **how it will be decided** — never invented, and never asked |
| `high` · `xhigh` | **the pass drafts, then asks about the draft.** It produces the same evidence-based answers first and puts them in front of the human as the question: *"here is what I would write for `## Out of Scope`; is the boundary right?"* |
| `xhigh` | `high`, and §Bank: adversarial's **premortem lens runs unconditionally** |

**Drafting first is what makes grouping legal at `high`.** §The four shared mechanics §1 forbids
two questions whose answers can change each other from travelling together, and that is exactly why
the shape and adversarial banks are sequential: an open question about the problem rewrites the next
question about the shape. A question about a **drafted section** does not have that property — the
draft is already written, so answering "the boundary is wrong" changes what the next edit writes,
never what the next question asks. Those two banks therefore run **sequential to draft, grouped to
ask**: up to four drafted sections per **AskUserQuestion**, each carrying its own draft as the
recommended option. This is the one place a gear touches §1, and it narrows nothing — two genuinely
dependent questions still travel alone.

**What a no-ask gear may never do.** It may not invent an explicit none. It may not resolve a
`## Discoveries` line `promoted:`, which mints a spec (§Bank: discoveries). It may not present a
screen from inside a sub-agent — the sub-agent returns the screen's content and the conductor
presents it. And it may not treat an unanswerable item as answered: `## Open Decisions` with how it
will be decided is the result, and a bank that has no evidence and writes a confident sentence
anyway has failed in the way this gear is most likely to fail.

**What it still does.** `refined` is stamped exactly as at any other gear when the adversarial or
the gate bank ran: drafting from evidence IS the interrogation, and the record says which bank ran
it, never who answered. §Recording the pass owns that.

<!-- rationale -->

The mechanism is not new. `/quenching:specs:develop-batch` has declared it verbatim to every
sub-agent since it existed — *"Ask the human nothing: a question no evidence answers goes to
`## Open Decisions` with how it will be decided"* — and `/quenching:specs:create` offers it as the
recommended way out of a capture. What changes is that it stops being a property of the caller and
becomes a mode **the spec's own record selects**, so a spec gets the same treatment whether a batch,
a cycle or a human at a prompt invoked the pass. A mode two callers declare and the command body
never documents is a behaviour nobody can read off the command.

## Bank: shape

**Stage.** `captured` — a spec with `## Problem` and nothing else. This is the thinking bank: the
spec exists, so there is always somewhere to land, and nothing has to be reconstructed later from
conversation.

**Goal.** Turn one stated problem into a shape worth arguing with — enough that the adversarial
bank has a claim to attack.

**Shape.** Sequential (§1) — what is actually wrong decides which shapes are worth tabling at all.

**Where the questions come from.** The dependency sweep first: selecting this bank triggers the
mandatory sweep of §Gathering the evidence below, whose map lands in `### Mapa de dependências`
under `## Design` — written by the orchestrator, never the sub-agent — before anything below is
asked. Then the problem statement itself, read against the codebase. Ask about, roughly in this
order:

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
`## Alternatives Considered` when the shapes table produced a real comparison.

**Evidence answers** what is actually wrong (read the code), the shapes table with its
recommendation, and the boundary. **Only a human answers** *why now* — what waiting costs is
appetite, not a fact about the tree — and *what would make this not worth doing*. Under a no-ask
gear both go to `## Open Decisions` unless `## Problem` already states them.

**Stop when** `## Proposal` states what will be true afterwards that is not true now, and the human
would recognise the spec as describing their idea. Not when the gate is met — that is two banks
away.

## Bank: adversarial

**Stage.** `proposed` — there is a claim on the page, so it can be attacked. This bank is the
disagreement the gate never requires: nothing about filling sections forces anyone to have
**disagreed** with the spec.

**Goal.** Make the proposal survive the argument, or change it.

**Shape.** Sequential (§1) — a criticism once answered rewrites the next one.

**The dependency sweep's second trigger.** A spec that reached this bank already `proposed` —
born with `## Proposal` filled — and never swept gets the same mandatory sweep here, on first
entry, before any lens below runs: it is the closed path §Gathering the evidence exists to cover,
so a spec born past the shape bank is never argued over without a map either. Its result lands in
the same `### Mapa de dependências` under `## Design`, written by the orchestrator.

It runs three lenses. Use the one the spec's own state argues for; a spec that deserves two gets
two, in this order. **At `xhigh` the premortem runs regardless of what the spec's state argues** —
that lens is the judgment stage the level buys, and a level whose stage fires only on a trigger it
shares with every other level buys nothing.

### Lens: alternatives — when `## Alternatives Considered` is absent, empty, or records one option

Generate **two to four genuinely different** approaches — different in shape, not in parameter.
"Same design with a bigger cache" is not an alternative. Include, where they apply, the three that
are almost always available and almost never written down: **do nothing** (what happens if this is
not built?), **the smallest thing that could work**, and **buy or borrow instead of build**.

Table them — approach, cost, benefit, what it forecloses — state a recommendation with the
reasoning, and ask the one question: does the spec keep its approach, or switch?

Each alternative is stated as its strongest advocate would state it; one that cannot be written
down convincingly was not a real alternative and does not belong in the table.

Lands in `## Alternatives Considered` — **including the rejected ones and why they lost**, which is
the entire point: the next person to have the same idea reads why it was already turned down.

### Lens: critique — when the spec is large, reaches into product code, or declares an uncovered standard

Assume the spec is wrong and find where. Be specific. Aim at:

- **The premise.** Does `## Problem` describe a problem anyone actually has? What is the evidence?
- **Scope inflation.** Which part of `## Proposal` does not follow from `## Problem`? What survives
  if it is cut?
- **Cheaper paths.** What buys 80% of the benefit for 20% of the change?
- **Contradiction with a binding contract.** Does any task violate a `knowledge/standards/` doc? Name
  the doc and the line.
- **Permanent cost.** What does this add forever — surface, config, a rule to remember? Is the
  benefit recurring or one-off?
- **Reversibility.** If this turns out wrong in a month, what does undoing it cost?
- **The load-bearing assumption.** Which single unstated assumption, if false, invalidates the spec?

**Every criticism carries a proposed remedy**: cut it, defer it, shrink it, or accept it with a
stated reason.

Lands in `## Out of Scope` (a scope cut taken), `## Open Decisions` (one that needs evidence), or
the spec's own sections where the remedy rewrites them.

### Lens: premortem — unconditionally at `xhigh`, and otherwise when the spec is risky or irreversible: a migration, a rename with a blast radius, a release

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

**Evidence answers** every alternative in the table, all seven critique targets and every
premortem story — each is readable against the tree. **Only a human answers** the accept-versus-cut
verdict where the remedy trades scope for risk; under a no-ask gear the pass takes its own
recommended remedy and writes the accepted risk as `ACCEPTED — <why>, taken by the pass under the
<level> gear`, so the trade is legible rather than silent.

**Stop when** every criticism has been answered, every failure story converted, the alternatives
table exists and the human has chosen — and the spec's biggest remaining risk is one they
explicitly accepted.

## Bank: gate

**Stage.** `designed` or `refined`, with `cq specs next` still reporting `write_section`.

**Goal.** Close the ten-section ready set, honestly. This is the bank that most easily degrades
into filling headings to make a check pass, and the explicit-none rule is the whole defence.

**Shape.** Grouped (§1) — the headings `next` reports are independent of one another.

**Drive it off the tool, never off a reading of the file.** `cq specs next --spec <slug> --json`
returns the first `missing` or `malformed` heading and the full list behind it. Ask about that
list, four headings to a call.

**Where the questions come from.** The gap itself, in the spec's own terms:

- a section that says `- none` with no reason attached — is that a decision or an omission?
- `## Out of Scope` absent → what was ruled out, and what is the nearest in-scope lookalike?
- `## Validation` absent or vague → what exact command proves this worked, and what must it print?
- `## Impact` declaring a standard no task names, or a task writing a doc `## Impact` never
  declared;
- a `## Tasks` item whose completion nobody could judge ("improve error handling");
- a task ordering that has step 4 depending on step 7;
- a term the spec uses in a sense the repo's glossary does not.

**And the three questions only this moment can answer** — every one of them is a decision
`/quenching:specs:execute` is forbidden to make for itself, so a spec that leaves them unasked is
built with the cheap options closed:

- **which task groups touch provably disjoint `files:`** → mark them `[P]` now. Execution **never
  infers** the marker ([spec-driven.md](spec-driven.md) §`## Tasks` and the `[!]` blocked marker),
  so an unmarked group runs serially forever, however disjoint it was.
- **which delegable task is missing `files:`** → declaring it is what *permits* the task to be
  handed to an executor sub-agent at all; omitting it forecloses both delegation and `[P]`.
- **which task has an obvious existing file to imitate** → `pattern:`, the cheapest context an
  executor can be given: one path beats three paragraphs of description.

Measured across five `ready` specs on this repository — 48 tasks — `files:` was declared on 81% and
`verify:` on 92%, but `pattern:` on 8% and `[P]` on **4%**, with three of the five specs carrying no
parallel-eligible task at all. The mechanism was never the missing piece; the question was.

This bank also settles the two declarations nothing else owns: the **`verification` policy** (one of
the three values in [spec-driven.md](spec-driven.md) §Frontmatter, asked once and written to
frontmatter, so `execute` never has to guess mid-build) and the parsed `### Standards this spec will
write into knowledge/standards/` sub-heading under `## Impact`.

**Evidence answers** all seven symptoms and all three execution decisions — `[P]`, `files:`
and `pattern:` are provable against the tree, and `cq specs parallel` proves the first
mechanically. **Only a human answers** the `verification` policy; under a no-ask gear the pass
**declares nothing** and lets the default stand, because stamping the default records a decision
nobody made.

**Stop when** `cq specs next` stops reporting `write_section` — every gate section answered with
content or a reasoned `- none`, every task with a judgeable completion, no `## Impact` path
uncovered. A `[P]` this bank set is **proved** when the edit lands, by `cq specs parallel`, never
argued about here: the tool checks disjunction mechanically and names the group it refuses.

## Bank: discoveries

**Stage.** Any. Runs whenever `## Discoveries` holds a line with no resolution on it.

**Goal.** Empty the queue an executor filled indiscriminately. Whether a discovery is worth acting
on is this bank's judgment, never the executor's — which is exactly why it was captured without
one.

**Shape.** Grouped (§1) — the lines do not reach each other, and every one of them takes the same
three resolutions, so four fit in one call.

Ask about the unresolved lines, four to a call, each with a recommendation. Every line resolves **in
place**, so provenance is never lost:

```markdown
- the rate limiter double-counts retries -> promoted: fix-retry-accounting
- the config loader is slow on cold start -> dismissed: acceptable, runs once
```

Three resolutions and nothing else:

| Resolution | When | What it costs |
| --- | --- | --- |
| `promoted: <slug>` | it is work someone will do, and the front does not already hold it | one `cq specs list --json` to check, then one `cq specs new` — offer it, and write the slug back |
| `folded: <section>` | it changes THIS spec | the answer lands in that section in the same edit |
| `dismissed: <reason>` | it is real but not worth acting on, or another spec already covers it | one line, and the reason is the whole value |

**Check the front before minting.** `promoted:` reads the open specs first; where one already
covers the line, resolve it `dismissed: already covered by {slug}`.

A line is never deleted, and never left unresolved with a shrug. `dismissed: acceptable` with no
reason is the failure mode to hunt for.

Under a no-ask gear, `folded:` and `dismissed:` are resolutions evidence supports.
**`promoted:` is not** — it mints a spec, which no pass may do unasked. The line stays unresolved,
this bank's stop condition is **not met**, and the report says so. A `dismissed:` invented to empty
the queue is the failure mode to hunt for here.

**Stop when** every line carries a resolution.

<!-- rationale -->
A queue filled by executors that could not see each other produces the same finding several times,
so the duplicate arrives through the front door and has to be turned away there.

## Bank: approval

**Stage.** `ready`, or the gate is met and `approved` is unset.

**Goal.** Settle the one fact the sections cannot: **that this spec may be built.**

This is the only bank that adds nothing to the body — it writes one record and no section. What it
shows is always the same: what the spec now commits to, in the proposal's one line, the task count,
the `verification` policy in force, the declared `knowledge/standards/` paths, and the biggest
accepted risk. **Who settles it is §Who answers — the gear decides.**

**At `medium`, `high` and `xhigh` — a human does, on the closing screen this bank IS.** One
**AskUserQuestion**, four options, the recommended one first:

1. **Approve (Recommended)** — `cq specs record "<slug>" approved --set date=<today> --set by=human`,
   never by editing the provider document directly.
2. **Refine `## <Section>`** — the section named on the screen. This is a **gear raise to `high`**
   ([gears.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-cycle/gears.md) §Re-evaluating a gear,
   the fourth signal), and choosing it IS the OK to restamp `complexity`.
3. **Run the premortem** — a raise to `xhigh`, same mechanics; the adversarial bank re-enters with
   the lens forced.
4. **Stop here** — nothing stamped, and the report says what is open.

Options 2 and 3 are what the old "on no, ask what would have to change and route it back" always
meant; naming the destination on the screen is what makes the answer one word instead of two turns.

**At `low` — the pass does, and the record says so.**
`cq specs record "<slug>" approved --set date=<today> --set by=low-gear`. There is no screen,
because `low` is the level whose whole content is that there is none. The review window is **the
spec's URL in the backend**, announced before the pass read anything and repeated in its report —
the same substitution this command already makes for every write it lands without a gate. The stamp
is not an inference from the sections and never claims to be one: `by:` is what keeps a level's
authority distinguishable from a human's word, and a reader who wants only human approvals filters
on it.

**The gate is a floor, not a verdict.** `ready` means ten sections have content; it does not mean
the spec is good. And approval is not a gate either — `execute` on an unapproved spec asks inline
and stamps rather than refusing, so declining here costs nothing but a question later.

**Stop when** the record carries both a `date` and a `by`.

## Gathering the evidence — economically, and delegated for three banks

<!-- rules -->

Every bank that reads the codebase or `.knowledge/` to answer its own questions — the **shape** bank's
"read it, do not theorize" included, not only what follows below — does so under
[align/evidence-doctrine.md](${CLAUDE_PLUGIN_ROOT}/assets/references/align/evidence-doctrine.md):
the aggregate a `grep`/`gh`/`cq` call produces, never the raw dump; `cq components read <path>
--sections "§X"` for `knowledge/standards/` and `knowledge/glossary.md`, the same way this
plugin's own references already address a section instead of a whole file.

Three uses delegate that reading to a sub-agent, and they do not share one tool profile.

**The dependency sweep** serves the **shape** bank, and by §Bank: adversarial's second trigger the
**adversarial** one too — and it is the only mandatory reading of the three: a cross-file
dependency map gathered before the bank asks anything, never in place of asking. It is asked for
**one table** — every file the proposal's own area touches or is touched by, and what breaks or
goes orphaned if it changes — which lands **dated** in `### Mapa de dependências` under
`## Design`. A spec is swept **at most once**, and never for having crossed a `complexity` level: a
spec looks small exactly while nobody has read its dependencies. Its sub-agent runs the **wider**
profile — read-only in full, everything but `Edit`, `Write`, `NotebookEdit` and `Agent`, `Bash`
included — because a dependency map is exactly the aggregate a `grep`/`gh`/`cq` call produces, and
the narrower profile below could not return it.

The **adversarial** and **gate** banks additionally ask questions that only a reading answers:
which alternatives the codebase actually admits, which `knowledge/standards/` contract a task would
violate, which term the spec uses in a sense the glossary does not. That reading is **optional and
delegable**; the interrogation never is.

Where it is taken, the sub-agent runs the **narrower** profile — `Read, Grep, Glob` and nothing
else — and returns **one compact table** and no trail:

| Bank | What it is asked for |
| --- | --- |
| adversarial | candidate whole-shape alternatives, each with cost, benefit and what it forecloses |
| adversarial | contradictions with a binding contract — the `knowledge/standards/` doc and the line |
| gate | terms the spec uses in a sense `glossary.md` does not |
| gate | `## Impact` paths no `## Tasks` item names, and tasks naming paths `## Impact` never declared |

All three sub-agents follow the verifier shape: they **inspect and report, never edit**. The
narrower two state an explicit *not checked here* list, which is the false-positive control; the
dependency sweep returns a table with no verdict to hedge, so it carries none.

**The orchestrator keeps every question, every write and every confirmation.** The sub-agent never
talks to the human and never touches the spec — the dependency map included, which the
orchestrator writes into `### Mapa de dependências` under `## Design`, never the sub-agent. Every
sub-agent's findings are material for questions the orchestrator still asks itself, under §1 —
never answers substituted for them.

<!-- rationale -->

Two things that look like this and are not available. **`context: fork` cannot ask a question** —
`sk-fork-gate` is an error, and a fork beside an `AskUserQuestion` grant is incoherent by
construction ([capabilities.md](${CLAUDE_PLUGIN_ROOT}/assets/references/components-command-new/capabilities.md)
§`context: fork`); a bank is nothing but questions. And a sub-agent **does not share the session's
prompt cache** — it runs on a cold context and pays the full first read of every file it touches, so
delegation here is never a cache play.

What it *is* is the delegation test met exactly: the returned table is far smaller than the sweep
that produced it, and the sweep's file reads stay out of the long context that the interrogation
then pays for on **every** turn that follows.

Why the dependency sweep exists at all, and the measurement that would graduate it, are recorded in
`/.knowledge/standards/automation/dependency-sweep.md` — this plugin's own bundle, not a target's.
Named bare because the rules above stand without it; every binding half is here.

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
that is the strongest claim the pass supports. The record is `writeOnce: false`
([spec-driven.md](spec-driven.md) §Frontmatter): a later pass restamps it, because a second
interrogation is a new fact, not a correction of the old one.

**Never fabricate it.** `refined` is written only after a bank really ran. It is the one field
whose entire value is that it cannot be inferred from the sections, so a stamp on a pass where no
bank ran at all makes the field worthless everywhere.

**A no-ask gear still stamps it.** Under `low` and `medium` the adversarial and gate banks answer
their own questions from evidence, and **that drafting IS the interrogation** — the record says
which bank ran it, never who answered. What the record can never survive is a pass that ran no bank
and stamped anyway.

**`approved` carries a second field, and it is never omitted.** `by: human` for a person's word on
the closing screen, `by: low-gear` for the stamp a `low` pass makes on the level's authority
(§Bank: approval). A record written with no `by:` reads as `human` — that is the only thing that
could have written it before the field existed — so leaving it off a `low-gear` stamp silently
claims a human the pass never had. The tool cannot require a field on a record; this rule is what
does.
