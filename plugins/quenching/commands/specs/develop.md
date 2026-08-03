---
description: Develop ONE spec by asking about it — one question at a time, with the question bank chosen by the spec's own derived stage rather than by a mode flag. Triggers on "develop this spec", "think this through", "explore this idea", "what shape should this take", "refine the spec", "poke holes in this", "what are the alternatives", "premortem this", "fill in the missing sections", "is this ready to build", "resolve the discoveries", "approve this spec". A raw spec gets shape questions; a proposed one gets argued with; a designed one gets its gate gaps closed; one at the gate gets offered the approval stamp. Answers accumulate and land in ONE confirmed edit per bank. Never edits code. Not for: creating a spec → /specs:create; building one → /specs:execute; closing one out and merging → /specs:conclude; a version bump or release obligation → /specs:conclude; taking a branch or worktree → /specs:execute; ranking the whole front → /specs:triage; being told which spec to pick up next → /specs:continue.
argument-hint: [slug-or-description]
allowed-tools: Read, Grep, Glob, Edit, Bash(python3:*), Bash(py:*), AskUserQuestion
model: opus
---

# /quenching:specs:develop — ask one spec the questions its stage calls for

**Input**: `$ARGUMENTS` — a spec slug, or a description of what to work on.

Takes ONE spec from wherever it is toward being worth building: giving a bare `## Problem` a shape,
arguing with the shape once it exists, closing the ten-section ready gate, resolving what an
executor discovered, and finally asking the human for the go-ahead.

**One loop, not a menu.** v2 split this across three commands and a mode flag — `explore` to think,
`refine --mode critic|premortem|alternatives|interview` to argue, `develop` to fill gaps — which
made the human choose the interrogation before anything had read the spec. It is one loop now,
because the spec's **derived stage** answers that question better than the human can: a spec with
only `## Problem` needs shape, a spec with a proposal needs an argument, a spec at the gate needs a
yes. Same target, same one-question-at-a-time mechanic, same single confirmed edit — only the bank
of questions differs, and it is looked up rather than asked for.

The banks, the four shared mechanics, and each bank's stop condition live in
[specs-develop/questions.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-develop/questions.md) —
read it before running a bank; it is the owner of the technique, and this body never restates it.

The spec-driven facts — the layout, the fourteen canonical sections, the gates, the derived stages,
the `specs.py` surface, the `specs/`↔`docs/` boundary — live in
[specs-develop/spec-driven.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-develop/spec-driven.md).
The per-section authoring doctrine — what belongs under each heading, how to write an honest
explicit none — lives in
[specs-develop/artifacts.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-develop/artifacts.md).

## Resolving the tool

Resolve `specs.py` by the fallback in
[specs-create/specs-front.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-create/specs-front.md)
§Resolving the tool: `${CLAUDE_PLUGIN_ROOT}/assets/bin/specs.py` first, then the target's
`.claude/hooks/specs.py`, else the manual fallback (**say so in the report**). Invoke with
`python3`/`py`; branch on the **exit code** (0 ok · 1 findings · 2 refusal) and the `--json`,
never on prose.

**No deltas.** A spec writes its durable rules **directly** into `docs/standards/` while it is
built, isolated on a branch. Whichever backend holds the spec is the only one that holds it, so
there is no second store to bridge to: nothing here writes a delta and nothing later syncs one.

## Doctrine

- **The stage picks the bank; the tool reports the stage.** `specs.py status --spec <slug> --json`
  returns it. Never infer the stage by reading the headings, and never ask the human which mode
  they want — the answer is on disk. This is the one rule that is this command's own; everything
  about *how* a bank runs is owned by
  [questions.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-develop/questions.md) §The four
  shared mechanics, and is not optional.
- **The explicit-none rule is the spec's, not this command's.** A section with nothing in it is
  `- none — <reason>`, a present-but-empty heading is malformed, and an absent heading before its
  own gate is legal — stated once in
  [spec-driven.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-develop/spec-driven.md) §The phase
  gates, applied here on every write.
- **Read `docs/` before writing.** The relevant `docs/standards/` and `knowledge/glossary.md` are
  binding on wording, so a spec does not contradict a rule the repo already agreed on or invent a
  second name for a thing that already has one.
- **Never edit code.** If the work implies code changes, that is `/quenching:specs:execute`. If a request
  changes the spec's *intent* rather than sharpening it, say so and offer a fresh
  `/quenching:specs:create` instead of quietly rewriting what was already agreed.

## Workflow

### 1. Resolve the spec
Take the slug from the input, infer it from the conversation, or run `specs.py list --json` and ask
with **AskUserQuestion** (most recently modified marked "(Recommended)"). Announce it and how to
override. Two matches for one slug is exit 2 — report both paths and stop, never guess which was
meant. An archived spec has nothing to develop: say so and stop.
**Done when:** one spec in `plans/` is resolved.

### 2. Read the spec and the OKF bundle
```bash
specs.py status --spec <slug> --json      # stage, section states, records, tasks, gate
```
Then pull the body of every section `status` reported `filled` — one call naming them all,
`specs.py section <slug> "<Heading1>,<Heading2>,…"` — never the whole document and never assume
filenames. Then, if the repo carries an OKF bundle (`docs/index.md` with
`okf_version`), read the `docs/standards/` subjects this spec touches and
`docs/knowledge/glossary.md`, so the questions use the repo's own vocabulary and can catch a spec
that contradicts a binding contract. No bundle → skip silently.
**Done when:** the spec's state and the binding context are in hand.

### 3. Select the bank
Look the **derived stage** up in
[questions.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-develop/questions.md) §Choosing the
bank. If `## Discoveries` holds an unresolved line, the discoveries bank runs **first** regardless
of stage — resolving what execution already found beats adding to a spec that has not absorbed it.

Name the bank, what it will ask, and **its stop condition** before the first question. If the input
asked for something the stage does not select — "poke holes in this" on a spec with no proposal —
say which bank the spec's state calls for, offer the requested one anyway, and let the human pick.
**Done when:** exactly one bank is named back to the user with its stop condition.

### 4. Run the bank — one question at a time
Follow the bank's script in
[questions.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-develop/questions.md), under the four
shared mechanics it owns: one question at a time **with an inline recommendation**, accumulate and
never write mid-flow, the bank's **declared stop condition**, and every answer naming the section
it lands in.

Questions must be **specific to this spec**. One that would read identically against any spec is
noise — do not ask it, and do not pad the count with it.

Nothing is written to the spec during this step. Keep a running list of
`(question, answer, target section)`.
**Done when:** the bank's stop condition is met, or the user calls it.

### 5. Present ONE consolidated edit → one OK
Show every accumulated answer as a single plan: per section, what changes and the answer it came
from. Draft each section per
[artifacts.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-develop/artifacts.md). Anything that
turned out to belong outside the spec — a durable rule, a term, a follow-up — is listed as a
**routed offer**, not an edit (§Invariants).

Wait. Declined → nothing is written, and the questions and answers are still reported so the
thinking is not lost.
**Done when:** the user has answered.

### 6. Apply, and record what the pass earned
Write each confirmed section with `specs.py section <slug> "<Heading>" --write` (body on stdin) —
it creates the heading in canonical position on first write, so creating and revising are the same
call. An emptied section becomes an explicit `- none — <reason>`, never a deleted heading.

Then the frontmatter records this command owns, each through `specs.py record` — **never by
editing the frontmatter**, which merges nothing and works only while the backend is `files`:

| Record | When | Call |
| --- | --- | --- |
| `refined: {mode, date}` | the adversarial or gate bank ran | `specs.py record <slug> refined --set mode=<per questions.md §Recording the pass> --set date=<today>` |
| `approved: {date}` | the human said go in the approval bank | `specs.py record <slug> approved --set date=<today>` |
| `verification` | the gate bank settled the policy | `specs.py verification <slug> <per-task\|per-section\|end-of-plan>` |

`verification` is a plain frontmatter key rather than a record, which is why it has a verb of its
own instead of a `--set`. **It is written through that verb and never by editing the frontmatter**
— a hand edit needs a file, and under an external backend there is none, so this bank's answer had
nowhere to land at all. Omit the value to read what is in force and whether anything declared it;
absent means the default, and stamping the default to make it explicit records a decision nobody
made.

`approved` is write-once: a spec that already carries it refuses (exit 2) with the date it holds,
which is the answer, not an obstacle.

Re-run `specs.py validate --spec <slug>` and report what it says.
**Done when:** the sections are written, the records this bank earned are stamped, and validate has
been re-run.

### 7. Re-derive, and offer the next bank
Run `specs.py status --spec <slug> --json` again. The stage is now a fact about disk. If it selects
a different bank, name it and what it would ask — then wait. Accepted → return to step 3. Declined,
or the same bank selected again with nothing left to ask → go to step 8.
**Done when:** the human has taken or declined the next bank.

### 8. Report
The spec and the bank(s) that ran; how many questions were asked and answered; the sections edited;
the records stamped; the routed offers and whether each was taken; the stage before and after; and
the next step — `/quenching:specs:execute <slug>` once `approved` is stamped, `/quenching:specs:develop <slug>` again
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
- **Never write into `docs/`.** A durable rule a question surfaces routes to `/quenching:docs:add`, an
  understanding to `/quenching:docs:learn`, a term to `/quenching:docs:define`, an out-of-scope follow-up to
  `/quenching:specs:create` — **offered, never auto-written**. The rules a spec *proves* are written during
  execution, not during definition.
- Never write a section without showing it and getting the human's word first.
- Never write anything mid-bank — accumulate, then apply once.
- Never batch questions. One at a time, each with a recommendation.
- Never ask the human to choose a mode; the derived stage chooses the bank.
- Never derive the stage from what this pass intends to write — only from disk.
- Never cross into another bank without offering it first.
- Never delete a heading to signal that nothing applies — write `- none — <reason>`.
- Never invent an explicit none the human did not give, and never invent an answer to an
  unanswered question: it goes in `## Open Decisions` with how it will be decided, which is a
  result, not a failure.
- Never create a heading you are not filling in the same edit.
- **Never edit a frontmatter record by hand.** `specs.py record` is the writer — it merges, it
  enforces write-once, and it is the only form that survives a backend with no file to edit.
- **Never fabricate a record.** `refined` is stamped only after real questions got real answers;
  `approved` only after a human actually said go. Neither can be inferred from the sections — that
  is the entire reason they exist.
- Never gate on refinement. A spec may always be built unrefined; `sp-unrefined` is a warning by
  design.
- Never rename a spec or change its date prefix.
