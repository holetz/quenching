---
description: Develop an existing spec. Triggers on "develop this spec", "refine the spec", "fill in the missing sections", "approve this spec". Not for: defining N specs at once → /quenching:specs:develop-batch; creating a spec or executing one.
argument-hint: [id-or-description]
allowed-tools: Read, Grep, Glob, Edit, Bash(python3:*), Bash(py:*), AskUserQuestion, Task
model: opus
---

# /quenching:specs:develop — ask one spec the questions its stage calls for

**Input**: `$ARGUMENTS` — a spec id, or a description of what to work on.

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

**No deltas.** A spec writes its durable rules **directly** into `/.knowledge/standards/` while it is
built, isolated on a branch. Whichever backend holds the spec is the only one that holds it, so
there is no second store to bridge to: nothing here writes a delta and nothing later syncs one.

## Doctrine

- **The stage picks the bank; the tool reports the stage.** `cq specs status --spec <id> --json`
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
- **Read `/.knowledge/` before writing — in the branch that needs it, and by section.** The relevant
  `/.knowledge/standards/` and `/.knowledge/glossary.md` are binding on wording, so a spec does not
  contradict a rule the repo already agreed on or invent a second name for a thing that already has
  one. Only the **adversarial** and **gate** banks ask questions that reading answers, so it is
  step 3b's and never the preamble's; shape, discoveries and approval skip it. Read it per
  [align/evidence-doctrine.md](${CLAUDE_PLUGIN_ROOT}/assets/references/align/evidence-doctrine.md)
  — `cq components read <path> --sections "§X"`, not the whole file, when only a rule or two
  governs the question at hand; it resolves `/.knowledge/` the same way it resolves this plugin's own
  references. No OKF bundle in the repo (`/.knowledge/index.md` with `okf_version`) → skip silently.
- **Never edit code.** If the work implies code changes, that is `/quenching:specs:execute`. If a request
  changes the spec's *intent* rather than sharpening it, say so and offer a fresh
  `/quenching:specs:create` instead of quietly rewriting what was already agreed.
- **`complexity` is re-evaluated when a pass closes, never mid-bank.** The level
  `/quenching:specs:create` computed from the input is stale the moment this pass writes what the
  input could not support. The re-evaluation is the bank's **last question** (step 5): the evidence
  that moved it is named, the new level recommended, and the human's answer applies it. A pass
  that changed no size asks nothing — the level on disk is still the latest word on it.
- **Capture confirms no classification at all — every bank reviews it in silence.**
  `/quenching:specs:create` writes subject, tags and `complexity` as presumptions the human may
  never have looked at: its own closing screen offers the correction, but nothing forces it. So
  every bank here also reviews `tags` — silently, narrated in step 5's
  consolidated plan and applied in step 6's single edit. No new screen, anywhere: the review rides
  the bank that was already going to write.

## The batching contract

Every turn re-sends the whole conversation, so a pass costs Σ(context per turn) and the turn count
is the multiplier — not the size of any one turn. Three points of the workflow below are therefore
**one call each**, and running them as two is the defect this contract names:

| Where | The one call |
| --- | --- |
| steps 1+2 | `cq specs status --spec <id> --json`, which also carries the `path` step 1 announces. Only an ID that must be *chosen* splits this: `cq specs list --json` runs first, because the question depends on its output |
| step 3b | the bank's own section and the spec sections it reads — `cq components read` and `cq specs section` together, never one call per source. For **shape** and **adversarial** the sweep's own profile and the `## Design` it checks ride these same two calls, so step 3c opens nothing |
| step 6 | the entire application — the section write, every `cq specs discover` line, every `cq specs record`, `cq specs verification`, and the closing `cq specs validate` (plus `cq specs parallel` where `## Tasks` moved) |

A call splits only where the next command's **input** depends on the previous one's output. Splitting
for tidiness, or to report progress between two commands, buys nothing and is paid by every turn
after it.

**No turn exists only to announce what the next tool call will do.** "Now I'll load the bank", "next
I'll write the sections" — a turn whose entire content is the call that follows it says nothing the
call's own output will not say, and costs a re-send of the whole conversation to say it. Narration
that carries content is not this: the bank and its stop condition (step 3), the consolidated plan
(step 5), the report (step 8) all stay. What is forbidden is the empty announcement, never the
narration.

**A recommendation rides inside the question, never in a turn before it.** Where a choice is
genuinely the human's, the recommendation and the reasoning behind it go in the **AskUserQuestion**
payload — the recommended option first and marked "(Recommended)", the reasoning in its description
— so the human answers in one word and no turn was spent setting the question up.

**This contract stops at the edge of how questions are grouped.**
[questions.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-develop/questions.md) §The four shared
mechanics §1 is the only authority there: a question travels with the ones whose answers cannot
change it, and alone otherwise. "Fewer turns" is a rule about tool calls and about prose turns; it
is never a licence to put two dependent questions into one call.

## Workflow

### 1. Resolve the spec, and announce where it lives
Take the id from the input, infer it from the conversation, or run `cq specs list --json` and ask
with **AskUserQuestion** (most recently modified marked "(Recommended)"). Announce it and how to
override. Two matches for one id is exit 2 — report both paths and stop, never guess which was
meant. An archived spec has nothing to develop: say so and stop.

**Announce the spec's URL in the backend along with it.** It is the `path` field of the
`cq specs status --spec <id> --json` payload step 2 takes in this same call, so nothing extra is
invoked to obtain it — an issue or work-item URL under an external backend, the file's path under
`files`. The announcement is load-bearing rather than decorative: with the plan narrated instead of
submitted (step 5), the backend is the window the human watches the pass through and the place a
correction is given, so it is stated before anything is read and repeated in the report (step 8).
**Done when:** one spec in `plans/` is resolved and its backend URL has been announced.

### 2. Read the spec's STATE — not its body
```bash
cq specs status --spec <id> --json      # stage, section states, records, tasks, gate, path
```
**This is the same call as step 1** — §The batching contract's first row. The id either came in
the input or was inferred, and the payload answers both steps at once.

That is the whole of this step. **No section body is pulled here**, because nothing has chosen the
bank yet and a body read before the choice is a body read for a bank that may not want it — at the
gate that is ten sections against the discoveries bank's one.
**Done when:** the spec's stage, section states, records, gate and backend URL are in hand.

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
Now that the bank is known, and in **one call** — §The batching contract's second row, both
commands together:

```bash
cq components read ${CLAUDE_PLUGIN_ROOT}/assets/references/specs-develop/questions.md \
  --sections "§Bank: <name>"          # + ",§Gathering the evidence" for shape and adversarial
cq specs section <id> "<Heading1>,<Heading2>,…"     # only the sections this bank reads or writes
```

| Bank | Spec sections | `artifacts.md` (loaded at step 5) |
| --- | --- | --- |
| shape | `## Problem` `## Design` — the second only to let step 3c see whether a map is already there | §The explicit-none rule §The nine definition sections |
| adversarial | `## Problem` `## Proposal` `## Design` `## Alternatives Considered` `## Risks` | §The nine definition sections |
| gate | the headings `cq specs next --spec <id> --json` reports, plus `## Impact` and `## Tasks` | §The explicit-none rule §The nine definition sections §`## Impact` §`## Tasks` §Execution metadata |
| discoveries | `## Discoveries` | §`## Discoveries` and `## Outcome` |
| approval | `## Proposal` `## Impact` `## Risks` | none — this bank writes nothing into the body |

**The adversarial and gate banks also read `/.knowledge/`** (Doctrine): the `/.knowledge/standards/` this spec's
`## Impact` declares — the declared files, never the folders they sit in — and
`/.knowledge/glossary.md`. Those two banks **may** delegate that reading to a read-only
sub-agent under
[questions.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-develop/questions.md) §Gathering the
evidence — already in hand for adversarial, from the call above — which returns one compact table
and keeps the file reads out of the context every later turn pays for. It is an option, not a step:
for a two-file spec, keep the reading.
**Done when:** the bank's sections are in hand and nothing else was opened.

### 3c. Run the dependency sweep — shape and adversarial only
Only the **shape** and **adversarial** banks reach this step — any other bank skips it whole, and
never loaded what it needs. **This step opens nothing**: step 3b's two calls already carry both
the `## Design` it reads and the §Gathering the evidence that governs it, which is why the sweep
costs no turn of its own.

`### Mapa de dependências` already in that `## Design` → this spec was swept; go straight to step
4. Absent → dispatch one read-only `Task` sub-agent under the **wider** profile of §Gathering the
evidence, briefed with whichever of `## Problem` / `## Proposal` is filled, asked for the one table
that section names: every file the proposal's own area touches or is touched by, and what breaks or
goes orphaned if it changes.

**The orchestrator holds the result; the sub-agent never writes it.** The table waits for step 6's
own consolidated write, landing as `### Mapa de dependências` under `## Design`, dated — never a
separate call, and never before the bank's other answers are ready to land with it.
**Done when:** the spec already carries a map, or this pass holds the sub-agent's table to write at
step 6.

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

### 5. Consolidate the edit, and narrate it
Load the authoring doctrine now — the `artifacts.md` sections step 3b's table names for **this**
bank, in one call:

```bash
cq components read ${CLAUDE_PLUGIN_ROOT}/assets/references/specs-develop/artifacts.md \
  --sections "§The explicit-none rule" --sections "§`## Tasks`"
```

**The consolidation stays; the confirmation goes.** Show every accumulated answer as a single plan
— per section, what changes and the answer it came from, drafted under the doctrine just loaded —
and then write it in step 6. The plan is **narrated, never submitted**: do not ask for a
confirmation of it and do not wait for one. Invoking this command is the authorization, because a
command that edits no code and takes no irreversible cycle action has nothing to confirm, and the
window the human watches the pass through is the spec's own URL in the backend.

Anything that turned out to belong outside the spec is narrated here too: a durable rule or a term
as a **routed offer**, not an edit, and an **out-of-scope follow-up as the one `## Discoveries` line
this edit will park** — a line, not an offer, because parking creates nothing to consent to
(§Invariants).

**A pass that changed the spec's size re-evaluates `complexity`, and that re-evaluation is the
bank's last question** — a real question, not a gate on the plan, asked alone because its content
depends on every answer before it. The evidence that moved it — the `## Tasks` a gate bank just
wrote, a scope the adversarial bank widened — is named, and the level it recommends leads the
options with the scale in front of the human. The level answers how much a human needs to be part
of the gears plan, never the size of what just changed
([gears.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-cycle/gears.md) §Deriving the gears
plan states the criterion):

| Level | What it changes in the gears plan |
| --- | --- |
| `low` | the whole cycle runs in one session on a single authorization and ends opening a PR |
| `medium` | the larger stages run isolated in sub-agents |
| `high` | the stage-by-stage stops and confirmations are kept |
| `xhigh` | at least one judgment stage (adversarial review, premortem) joins the plan |

A pass that changed no size asks nothing — the level on disk is still the latest word on it.

**Exception: the first pass over a spec still at `captured`.** `/quenching:specs:create` computed
this level without asking, so nobody has confirmed it yet — the first bank that touches such a spec
treats `complexity` as presumed rather than settled, and folds a confirm-or-adjust into this same
question even when this pass moved no size of its own. Every later pass returns to the ordinary
rule above: ask only when the size moved.
**Done when:** the plan has been narrated in full, and `complexity` — where the pass moved it, or
where this is the first pass over a `captured` spec — has been answered.

### 6. Apply, and record what the pass earned
**Every write of this step is ONE call** — §The batching contract's third row: the section write,
the `## Discoveries` lines, the records, `verification`, and the closing `validate`. None of them
needs another to have printed first. The one legitimate split is the doctrine read below, which
decides *which* record this bank earned and therefore has to precede the stamping.

Write the narrated sections with `cq specs section <id> "<Heading>[,<Heading>…]" --write` (bodies
on stdin) — it creates each heading in canonical position on first write, so creating and revising
are the same call. An emptied section becomes an explicit `- none — <reason>`, never a deleted
heading.

**The bodies go on stdin as one heredoc, in the same call** — a scratch file, a `mkdir` and a `cat`
are three turns buying what one already does, and a bank that filled six sections over six calls
paid six round trips for one edit:

```bash
cq specs section "<id>" "<Heading>,<Other Heading>" --write <<'BODY'
## <Heading>

<the drafted section, verbatim>

## <Other Heading>

<the other drafted section, verbatim>
BODY
```

Quote the delimiter (`<<'BODY'`) so nothing in the prose is expanded by the shell.

The `## <Heading>` lines in the stream are the delimiter, and the set they carry must equal the set
declared on the command line — a mismatch, a repeat, or a heading outside the canonical thirteen
refuses (exit 2) **without writing any of them**, so a rejected edit leaves the spec exactly as it
was. One heading with a raw body and no `## ` line is the singular form and is unchanged.

Every follow-up the plan parked is written in this same edit — `cq specs discover <id>
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
| `refined: {mode, date}` | the adversarial or gate bank ran | `cq specs record <id> refined --set mode=<per questions.md §Recording the pass> --set date=<today>` |
| `approved: {date}` | the human said go in the approval bank | `cq specs record <id> approved --set date=<today>` |
| `verification` | the gate bank settled the policy | `cq specs verification <id> <per-task\|per-section\|end-of-plan>` |
| `tags` | the pass changed the spec's scope, or the capture presumed wrong | `cq specs tags <id> "<whole list>"` |
| `complexity` (in `priority`) | the plan proposed a re-evaluation, and the human approved it | `cq specs record <id> priority --set complexity=<level> --set date=<today>` |

`cq specs tags` **replaces** the whole list, never appends — reissue the subject's own fixed tags
together with whatever this pass adds, or the fixed ones are lost.

The title is the sole short description every ranked listing prints (`cq specs next --front
--table`). Keep it descriptive when the spec's scope changes; the sections carry the rationale and
detail, so no separate summary field is maintained.

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

Re-run `cq specs validate --spec <id>` and report what it says. **When this pass touched
`## Tasks`, run `cq specs parallel --spec <id>` in the same call** — exit 1 names the `[P]` group
whose `files:` sets are not disjoint, and definition time is the only moment that is cheap to fix.
Report what it says either way; a `[P]` nobody proved is a promise execution will refuse.
**Done when:** the sections are written, the records this bank earned are stamped, and validate —
plus `parallel`, where `## Tasks` moved — has been re-run.

### 7. Re-derive, and cross into the next bank
Run `cq specs status --spec <id> --json` again. The stage is now a fact about disk, and the pass
follows it: it selects a different bank → name the bank and what it will ask, and return to step 3.
**The crossing is narrated, never offered.** The stage chose it off what step 6 just wrote, so an
offer here asks the human to re-decide what the disk already answered. The same bank selected again
with nothing left to ask → go to step 8.

Every bank the pass crosses into still asks its own questions, and the `approval` bank still ends
in a real go/no-go — the crossing being automatic never makes a bank's questions automatic.
**Done when:** the re-derived stage has sent the pass back to step 3 or ended it at step 8.

### 8. Report

```bash
cq components read ${CLAUDE_PLUGIN_ROOT}/assets/references/specs-develop/spec-driven.md \
  --sections "§The report mold" --rules-only
```

Emit §The report mold. The single-spec header line carries the stage **after** the pass; two body blocks:

1. **The pass** — fixed. The spec's URL in the backend, repeated from step 1 off the same `path`
   field and never re-fetched; the bank(s) that ran; how many questions were asked and answered;
   the sections edited; the records stamped; the routed offers and whether each was taken; the
   stage before and after. The URL closes the pass the way it opened it: a pass that wrote without
   a plan gate ends by pointing at the one place that writing can be read and corrected.
2. **Parked into `## Discoveries`** — optional, and every line **quoted**. A parked line was never
   offered, so nothing else in this report names it, and an unreported one is indistinguishable from
   a finding the pass dropped.

Close on §The next-step block — `/quenching:git:branch <id>` once `approved` is stamped, naming it
the natural moment to isolate before `/quenching:specs:execute <id>` writes any code;
`/quenching:specs:develop <id>` again for the next bank; or `/quenching:specs:cycle <id>` to
carry it to the end in one run, which takes its own isolation inline and needs neither named
separately.

**Isolation is named, never taken.** An interrogation that rewrites half a spec dirties the tree, so
the human may want it on a branch before the next pass or before `execute` — naming
`/quenching:git:branch <id>` in the next-step block is that suggestion, stated once at the close
and never asked as a question mid-pass; this command's own job is questions, and one about git in
the middle of an interrogation is friction for everyone. `execute` no longer owns an inline offer of
its own to fall back on — it hands off to the same command.
**Done when:** the summary is shown.

## Invariants to never violate

- **NEVER edit implementation code.** If the spec implies code changes, stop and name
  `/quenching:specs:execute`.
- **Never write into `/.knowledge/`.** A durable rule a question surfaces routes to `/quenching:knowledge:add`, an
  understanding to `/quenching:knowledge:learn`, a term to `/quenching:knowledge:define` — **offered, never
  auto-written**. The rules a spec *proves* are written during execution, not during definition.
- **Never write into `## Tasks` what the merge owns.** A version bump, a changelog entry, a manifest
  re-stamp; the `/.knowledge/` the work *revealed* rather than declared; the cycle's own closing actions
  (review, archive, distil, merge, open the PR) — all three belong to `/quenching:specs:conclude`,
  which settles them once what the release *is* is knowable. A standard this spec **declares** under
  `## Impact` still gets its own checkbox and still must: the axis is declared versus revealed,
  never docs versus code.
- **Park an out-of-scope follow-up; never mint a spec for it.** A finding this pass raised that does
  not belong to the spec being developed becomes ONE line of `## Discoveries` on that same spec —
  `cq specs discover <id> "<finding>"` — landed inside the step 6 edit the human already
  confirmed, never as a loose call mid-bank. Turning a follow-up into its own spec stays
  `/quenching:specs:conclude`'s, which harvests it once the parent's fate is known. This route is
  not an offer: nothing is created, so there is nothing to ask for.
- **Inside a develop pass, `cq specs new` runs only as the discoveries bank's `promoted:`
  resolution.** Nothing else here mints a spec.
- **Never write a section that was not narrated first.** The consolidated plan is shown in full
  (step 5) and then applied; what left this command is the wait, never the showing. A section that
  reaches the spec without appearing in a narrated plan is unreviewable by anyone, gate or no gate.
- Never write anything mid-bank — accumulate, then apply once.
- **Never group two questions whose answers can change each other**, and never ask alone what could
  have travelled with them. Grouping is by dependence, never by convenience, and every question
  carries a recommendation either way.
- Never ask the human to choose a mode; the derived stage chooses the bank.
- **A sub-agent may read; it may never ask, write, or decide.** The evidence sweep of step 3b
  returns a table. Every question, every `cq specs` call and every confirmation stays here.
- **The dependency sweep's map is written by the orchestrator; the sub-agent never touches the
  spec.** Step 3c's sub-agent returns a table too, same as step 3b's — the map lands only inside
  step 6's own consolidated write, into `### Mapa de dependências` under `## Design`.
- **The sweep does not reopen `context: fork`.** Dispatching its `Task` sub-agent is a step inside
  a command that still asks every one of its own banks' questions — the prohibition a fork cannot
  ask a question stays exactly where it was; step 3c changes nothing about what this command's own
  frontmatter may declare.
- **Never open a cited reference as a file.** `§X` is an address, loaded through
  `cq components read --sections`; and never hoist into the preamble what only one branch reads.
- Never derive the stage from what this pass intends to write — only from disk.
- Never cross into another bank silently — name it and what it will ask before running it. The
  crossing itself is narrated, not offered: the re-derived stage picks the bank, and a human who
  wants the pass to stop says so.
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
