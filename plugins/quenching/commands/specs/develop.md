---
description: Develop an existing spec. Triggers on "develop this spec", "refine the spec", "fill in the missing sections", "approve this spec". Not for: creating a spec or executing one.
argument-hint: [slug-or-description]
allowed-tools: Read, Grep, Glob, Edit, Bash(python3:*), Bash(py:*), AskUserQuestion, Task
model: opus
---

# /quenching:specs:develop — ask one spec the questions its stage calls for

**Input**: `$ARGUMENTS` — a spec slug, or a description of what to work on.

Takes a spec from wherever it is toward being worth building: giving a bare `## Problem` a shape,
arguing with the shape once it exists, closing the ten-section ready gate, resolving what an
executor discovered, and finally asking the human for the go-ahead.

**One loop.** The spec's **derived stage** picks the bank — only `## Problem` needs shape, a
proposal needs an argument, a spec at the gate needs a yes. The bank is looked up, never asked for.

**Every `§X` below is an address, and it is loaded as one — never by opening the file.**

```bash
cq components read <the cited file> --sections "§Choosing the bank" --sections "§The four shared mechanics"
```

One call, N sections, no frontmatter; a unique prefix resolves. The reason is this command's own
cost: a preamble is re-sent on every turn that follows it, and the three references this command
cites run to ~58,000 characters read whole — measured on one real run at ~900k token-turns for two
of them. `--rules-only` narrows further to the `<!-- rules -->` half where a section carries the
marker, and returns the whole section, saying so, where it does not.

**Load now, and nothing else:**

- the banks and the mechanics they share —
  [specs-develop/questions.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-develop/questions.md)
  §Choosing the bank §The four shared mechanics;
- the spec-driven facts —
  [specs-develop/spec-driven.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-develop/spec-driven.md)
  §Derived stages §The gates.

The selected bank's own section, the per-section authoring doctrine in
[specs-develop/artifacts.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-develop/artifacts.md),
and the records' shapes are loaded **inside the step that uses them** — steps 3b, 5 and 6; step 8
loads spec-driven.md's §The report mold, whose shape that step's report is built from, the same
way. A reference read in one branch is never hoisted into a preamble every turn pays for regardless
of which branch runs.

## Resolving the tool

Resolve `cq` (`cq components read` is the section reader every `§X` citation above resolves through)
per
[align/tool-resolution.md](${CLAUDE_PLUGIN_ROOT}/assets/references/align/tool-resolution.md)
§Resolving the tool, §Write the resolved path literally on every invocation; branch on the **exit
code** (0 ok · 1 findings · 2 refusal) and the `--json`, never on prose.

**No deltas.** A spec writes its durable rules **directly** into `/.docs/standards/` while it is
built, isolated on a branch. Whichever backend holds the spec is the only one that holds it, so
there is no second store to bridge to: nothing here writes a delta and nothing later syncs one.

## Doctrine

- **The stage picks the bank; the tool reports the stage.** `cq specs status --spec <slug> --json`
  returns it. Never infer the stage by reading the headings, and never ask the human which mode
  they want — the answer is on disk. This is the one rule that is this command's own; everything
  about *how* a bank runs is owned by
  [questions.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-develop/questions.md) §The four
  shared mechanics, and is not optional.
- **The explicit-none rule is the spec's, not this command's.** A section with nothing in it is
  `- none — <reason>`, a present-but-empty heading is malformed, and an absent heading before its
  own gate is legal — stated once in
  [spec-driven.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-develop/spec-driven.md)
  §The gates, applied here on every write.
- **Read `/.docs/` before writing — in the branch that needs it.** The relevant `/.docs/standards/` and
  `knowledge/glossary.md` are binding on wording, so a spec does not contradict a rule the repo
  already agreed on or invent a second name for a thing that already has one. Only the
  **adversarial** and **gate** banks ask questions that reading answers, so it is step 3b's and
  never the preamble's; shape, discoveries and approval skip it. No OKF bundle in the repo
  (`/.docs/index.md` with `okf_version`) → skip silently.
- **Never edit code.** If the work implies code changes, that is `/quenching:specs:execute`. If a request
  changes the spec's *intent* rather than sharpening it, say so and offer a fresh
  `/quenching:specs:create` instead of quietly rewriting what was already agreed.
- **`complexity` is re-evaluated when a pass closes, never mid-bank.** The level
  `/quenching:specs:create` computed from the input is stale the moment this pass writes what the
  input could not support. The re-evaluation rides the consolidated plan (step 5): the evidence
  that moved it is named, the new level recommended, and the human's one OK applies it. A pass
  that changed no size proposes nothing — the level on disk is still the latest word on it.

## Workflow

### 1. Resolve the spec
Take the slug from the input, infer it from the conversation, or run `cq specs list --json` and ask
with **AskUserQuestion** (most recently modified marked "(Recommended)"). Announce it and how to
override. Two matches for one slug is exit 2 — report both paths and stop, never guess which was
meant. An archived spec has nothing to develop: say so and stop.
**Done when:** one spec in `plans/` is resolved.

### 2. Read the spec's STATE — not its body
```bash
cq specs status --spec <slug> --json      # stage, section states, records, tasks, gate
```
That is the whole of this step. **No section body is pulled here**, because nothing has chosen the
bank yet and a body read before the choice is a body read for a bank that may not want it — at the
gate that is ten sections against the discoveries bank's one.
**Done when:** the spec's stage, section states, records and gate are in hand.

### 3. Select the bank
Look the **derived stage** up in
[questions.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-develop/questions.md) §Choosing the
bank — already loaded. If `## Discoveries` holds an unresolved line, the discoveries bank runs
**first** regardless of stage — resolving what execution already found beats adding to a spec that
has not absorbed it.

Name the bank, what it will ask, and **its stop condition** before the first question. If the input
asked for something the stage does not select — "poke holes in this" on a spec with no proposal —
say which bank the spec's state calls for, offer the requested one anyway, and let the human pick.
**Done when:** exactly one bank is named back to the user with its stop condition.

### 3b. Load what THIS bank needs — and nothing more
Now that the bank is known, and in **one call per source**:

```bash
cq components read ${CLAUDE_PLUGIN_ROOT}/assets/references/specs-develop/questions.md \
  --sections "§Bank: <name>"
cq specs section <slug> "<Heading1>,<Heading2>,…"     # only the sections this bank reads or writes
```

| Bank | Spec sections | `artifacts.md` (loaded at step 5) |
| --- | --- | --- |
| shape | `## Problem` | §The explicit-none rule §`## Overview` §The nine definition sections |
| adversarial | `## Problem` `## Proposal` `## Design` `## Alternatives Considered` `## Risks` | §The nine definition sections §`## Overview` |
| gate | the headings `cq specs next --spec <slug> --json` reports, plus `## Impact` and `## Tasks` | §The explicit-none rule §The nine definition sections §`## Impact` §`## Tasks` §Execution metadata |
| discoveries | `## Discoveries` | §`## Discoveries` and `## Outcome` |
| approval | `## Proposal` `## Impact` `## Risks` | none — this bank writes nothing into the body |

**The adversarial and gate banks also read `/.docs/`** (Doctrine): the `/.docs/standards/` this spec's
`## Impact` declares — the declared files, never the folders they sit in — and
`/.docs/knowledge/glossary.md`. Those two banks **may** delegate that reading to a read-only
sub-agent under
[questions.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-develop/questions.md) §Gathering the
evidence, which returns one compact table and keeps the file reads out of the context every later
turn pays for. It is an option, not a step: for a two-file spec, keep the reading.
**Done when:** the bank's sections are in hand and nothing else was opened.

### 4. Run the bank
Follow the bank's script in
[questions.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-develop/questions.md), under the four
shared mechanics it owns: questions **grouped by dependency** — independent ones in a single
**AskUserQuestion** call of up to four, sequential only where the next question's content depends on
the last answer, and the bank states which shape it takes — every question carrying **an inline
recommendation**, accumulate and never write mid-flow, the bank's **declared stop condition**, and
every answer naming the section it lands in.

Questions must be **specific to this spec**. One that would read identically against any spec is
noise — do not ask it, and do not pad the count with it.

Nothing is written to the spec during this step. Keep a running list of
`(question, answer, target section)`.
**Done when:** the bank's stop condition is met, or the user calls it.

### 5. Present ONE consolidated edit → one OK
Load the authoring doctrine now — the `artifacts.md` sections step 3b's table names for **this**
bank, in one call:

```bash
cq components read ${CLAUDE_PLUGIN_ROOT}/assets/references/specs-develop/artifacts.md \
  --sections "§The explicit-none rule" --sections "§`## Tasks`"
```

Show every accumulated answer as a single plan: per section, what changes and the answer it came
from, drafted under the doctrine just loaded. Anything that
turned out to belong outside the spec is shown here as well: a durable rule or a term as a
**routed offer**, not an edit, and an **out-of-scope follow-up as the one `## Discoveries` line
this edit will park** — a line, not an offer, because parking creates nothing to consent to
(§Invariants).

**A pass that changed the spec's size re-evaluates `complexity` in this same plan.** The
evidence that moved it — the `## Tasks` a gate bank just wrote, a scope the adversarial bank
widened — is named, and the level it recommends is proposed with the scale in front of the
human:

| Level | What it changes in the gears plan |
| --- | --- |
| `low` | the whole cycle runs in one session on a single authorization and ends opening a PR |
| `medium` | the larger stages run isolated in sub-agents |
| `high` | the stage-by-stage stops and confirmations are kept |
| `xhigh` | at least one judgment stage (adversarial review, premortem) joins the plan |

A pass that changed no size proposes nothing — the level on disk is still the latest word on
it.

Wait. Declined → nothing is written, and the questions and answers are still reported so the
thinking is not lost.
**Done when:** the user has answered.

### 6. Apply, and record what the pass earned
Write each confirmed section with `cq specs section <slug> "<Heading>" --write` (body on stdin) —
it creates the heading in canonical position on first write, so creating and revising are the same
call. An emptied section becomes an explicit `- none — <reason>`, never a deleted heading.

**The body goes on stdin as a heredoc, in the same call** — a scratch file, a `mkdir` and a `cat`
are three turns buying what one already does:

```bash
cq specs section "<slug>" "<Heading>" --write <<'BODY'
<the drafted section, verbatim>
BODY
```

Quote the delimiter (`<<'BODY'`) so nothing in the prose is expanded by the shell.

Every follow-up the plan parked is written in this same edit — `cq specs discover <slug>
"<finding>"`, one call per line — and never mid-bank, which
[questions.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-develop/questions.md) §The four shared
mechanics forbids. The call creates `## Discoveries` when the heading is absent, and a filled
`## Discoveries` moves no derived stage, so the line costs the pass nothing but itself.

Then the frontmatter records this command owns — read
[questions.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-develop/questions.md) §Recording the
pass for which bank earns which, and
[spec-driven.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-develop/spec-driven.md) §Frontmatter
for the write-once semantics, in one call. Each is stamped through `cq specs record` — **never by
editing the frontmatter**, which merges nothing and works only while the backend is `files`:

| Record | When | Call |
| --- | --- | --- |
| `refined: {mode, date}` | the adversarial or gate bank ran | `cq specs record <slug> refined --set mode=<per questions.md §Recording the pass> --set date=<today>` |
| `approved: {date}` | the human said go in the approval bank | `cq specs record <slug> approved --set date=<today>` |
| `verification` | the gate bank settled the policy | `cq specs verification <slug> <per-task\|per-section\|end-of-plan>` |
| `complexity` (in `priority`) | the plan proposed a re-evaluation, and the human approved it | `cq specs record <slug> priority --set complexity=<level> --set date=<today>` |

`verification` is a plain frontmatter key rather than a record, which is why it has a verb of its
own instead of a `--set`. **It is written through that verb and never by editing the frontmatter**
— a hand edit needs a file, and under an external backend there is none, so this bank's answer had
nowhere to land at all. Omit the value to read what is in force and whether anything declared it;
absent means the default, and stamping the default to make it explicit records a decision nobody
made.

`approved` is write-once: a spec that already carries it refuses (exit 2) with the date it holds,
which is the answer, not an obstacle.

`complexity` is a field of `priority`, and the record merges — `level` and `criticality` survive
a re-stamp that touches only the size, and `date` is the ranking's own.

Re-run `cq specs validate --spec <slug>` and report what it says. **When this pass touched
`## Tasks`, run `cq specs parallel --spec <slug>` in the same call** — exit 1 names the `[P]` group
whose `files:` sets are not disjoint, and definition time is the only moment that is cheap to fix.
Report what it says either way; a `[P]` nobody proved is a promise execution will refuse.
**Done when:** the sections are written, the records this bank earned are stamped, and validate —
plus `parallel`, where `## Tasks` moved — has been re-run.

### 7. Re-derive, and offer the next bank
Run `cq specs status --spec <slug> --json` again. The stage is now a fact about disk. If it selects
a different bank, name it and what it would ask — then wait. Accepted → return to step 3. Declined,
or the same bank selected again with nothing left to ask → go to step 8.
**Done when:** the human has taken or declined the next bank.

### 8. Report

```bash
cq components read ${CLAUDE_PLUGIN_ROOT}/assets/references/specs-develop/spec-driven.md \
  --sections "§The report mold" --rules-only
```

Emit §The report mold. The single-spec header line carries the stage **after** the pass; two body blocks:

1. **The pass** — fixed. The bank(s) that ran; how many questions were asked and answered; the
   sections edited; the records stamped; the routed offers and whether each was taken; the stage
   before and after.
2. **Parked into `## Discoveries`** — optional, and every line **quoted**. A parked line was never
   offered, so nothing else in this report names it, and an unreported one is indistinguishable from
   a finding the pass dropped.

Close on §The next-step block — `/quenching:specs:execute <slug>` once `approved` is stamped, `/quenching:specs:develop <slug>` again
for the next bank, or `/quenching:specs:continue` to be told what the whole front wants next.

**Isolation is forwarded, never offered.** An interrogation that rewrites half a spec dirties the
tree, so the human may want it on a branch — when they ask, name `/quenching:specs:execute <slug>` as the
next command: its inline offer owns the branch name and the `branch: {base, work}` record. Never
raise it unprompted; this command's job is questions, and a prompt about git in the middle of one
is friction for everyone.
**Done when:** the summary is shown.

## Invariants to never violate

- **NEVER edit implementation code.** If the spec implies code changes, stop and name
  `/quenching:specs:execute`.
- **Never write into `/.docs/`.** A durable rule a question surfaces routes to `/quenching:knowledge:add`, an
  understanding to `/quenching:knowledge:learn`, a term to `/quenching:knowledge:define` — **offered, never
  auto-written**. The rules a spec *proves* are written during execution, not during definition.
- **Never write into `## Tasks` what the merge owns.** A version bump, a changelog entry, a manifest
  re-stamp; the `/.docs/` the work *revealed* rather than declared; the cycle's own closing actions
  (review, archive, distil, merge, open the PR) — all three belong to `/quenching:specs:conclude`,
  which settles them once what the release *is* is knowable. A standard this spec **declares** under
  `## Impact` still gets its own checkbox and still must: the axis is declared versus revealed,
  never docs versus code.
- **Park an out-of-scope follow-up; never mint a spec for it.** A finding this pass raised that does
  not belong to the spec being developed becomes ONE line of `## Discoveries` on that same spec —
  `cq specs discover <slug> "<finding>"` — landed inside the step 6 edit the human already
  confirmed, never as a loose call mid-bank. Turning a follow-up into its own spec stays
  `/quenching:specs:conclude`'s, which harvests it once the parent's fate is known. This route is
  not an offer: nothing is created, so there is nothing to ask for.
- **Inside a develop pass, `cq specs new` runs only as the discoveries bank's `promoted:`
  resolution.** Nothing else here mints a spec.
- Never write a section without showing it and getting the human's word first.
- Never write anything mid-bank — accumulate, then apply once.
- **Never group two questions whose answers can change each other**, and never ask alone what could
  have travelled with them. Grouping is by dependence, never by convenience, and every question
  carries a recommendation either way.
- Never ask the human to choose a mode; the derived stage chooses the bank.
- **A sub-agent may read; it may never ask, write, or decide.** The evidence sweep of step 3b
  returns a table. Every question, every `cq specs` call and every confirmation stays here.
- **Never open a cited reference as a file.** `§X` is an address, loaded through
  `cq components read --sections`; and never hoist into the preamble what only one branch reads.
- Never derive the stage from what this pass intends to write — only from disk.
- Never cross into another bank without offering it first.
- Never delete a heading to signal that nothing applies — write `- none — <reason>`.
- Never invent an explicit none the human did not give, and never invent an answer to an
  unanswered question: it goes in `## Open Decisions` with how it will be decided, which is a
  result, not a failure.
- Never create a heading you are not filling in the same edit.
- **Never edit a frontmatter record by hand.** `cq specs record` is the writer — it merges, it
  enforces write-once, and it is the only form that survives a backend with no file to edit.
- **Never fabricate a record.** `refined` is stamped only after real questions got real answers;
  `approved` only after a human actually said go. Neither can be inferred from the sections — that
  is the entire reason they exist.
- **Never restamp `complexity` without the human's OK.** The re-evaluation rides the consolidated
  plan — evidence named, level recommended — and a level a pass did not move is the latest word
  on it, not a value to re-propose.
- Never gate on refinement. A spec may always be built unrefined; `sp-unrefined` is a warning by
  design.
- Never rename a spec, and never rewrite its `date:` — the capture date is stamped once, at
  creation.
