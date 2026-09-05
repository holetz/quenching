---
description: Develop an existing spec — compose it to ready, argue with it, approve it. Triggers on "develop this spec", "refine the spec", "fill in the missing sections", "approve this spec", "poke holes in this". Not for: capturing an unrelated new spec → /quenching:specs:create; executing one → /quenching:specs:execute.
argument-hint: [id-or-description]
allowed-tools: Read, Grep, Glob, Edit, Bash(python3:*), Bash(py:*), AskUserQuestion, Task
model: opus
---

# /quenching:specs:develop — compose a spec, argue with it, and settle its go

**Input**: `$ARGUMENTS` — a spec id, or a description of what to work on.

Takes a spec from wherever it is toward being worth building, in ONE pass: resolving what an
executor discovered, **composing** a bare `## Problem` into a closed ten-section spec,
**refining** that spec by arguing with it, and closing on the go-ahead.

**Two operations, and both are derived.** **Compose** is monotonic — it fills what is absent and
closes the ready gate. **Refine** may overturn anything it finds, the proposal included. The
spec's **derived stage** says where composing starts; the **gear** says whether refining runs
without anyone asking for it. Neither is ever put to the human as a choice.

**Every `§X` below is an address, and it is loaded as one — never by opening the file.**

```bash
cq components read <the cited file> --sections "§The pass" --sections "§The four shared mechanics"
```

One call, N sections, no frontmatter; a unique prefix resolves. `--rules-only` narrows further to
the `<!-- rules -->` half where a section carries the marker, and returns the whole section, saying
so, where it does not.

**Load now, and nothing else:**

- what runs and in what order, and the mechanics every stage shares —
  [specs-develop/questions.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-develop/questions.md)
  §The pass §The four shared mechanics;
- the spec-driven facts —
  [specs-develop/spec-driven.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-develop/spec-driven.md)
  §Derived stages §The gates.

The stages' own sections, the per-section authoring doctrine in
[specs-develop/artifacts.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-develop/artifacts.md),
§Writing a section through stdin §The explicit-none rule §The nine definition sections
§`## Impact` — the parsed sub-heading §`## Tasks`
§Execution metadata — optional, indented, additive,
and the records' shapes are loaded **inside the step that uses them** — steps 3b and 6; step 8
loads specs-develop/report-mold.md's §The report mold, whose shape that step's report is built from,
the same way.

## Resolving the tool

Resolve `cq` (`cq components read` is the section reader every `§X` citation above resolves through)
per
[align/tool-resolution.md](${CLAUDE_PLUGIN_ROOT}/assets/references/align/tool-resolution.md)
§Resolving the tool, §Write the resolved path literally on every invocation; branch on the **exit
code** (0 ok · 1 findings · 2 refusal) and the `--json`, never on prose.

## Doctrine

- **The stage says where composing starts; the gear says whether refining runs.** `cq specs status
  --spec <id> --json` returns both. Never infer the stage by reading the headings, never ask the
  human which mode they want, and **never ask which gear to run in** — the answers are on disk. A
  conductor that moved the level on its own plan declares the moved level in the invocation.
- **The gear never shortens a stage that runs.** No checklist shrinks at a low level — the same
  axes, lenses and gate symptoms are worked either way, and what changes is who answers them.
  Everything about *how* a stage runs is owned by
  [questions.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-develop/questions.md) §The four
  shared mechanics §Who answers.
- **A pass lands ONE edit.** Compose and refine accumulate and write together, so the spec never
  holds a half-composed state and never holds a draft refine already superseded. An abandoned pass
  leaves the spec exactly as it was.
- **Apply the explicit-none rule on every write.** A section with nothing in it is
  `- none — <reason>`, a present-but-empty heading is malformed, and an absent heading before its
  own gate is legal —
  [spec-driven.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-develop/spec-driven.md)
  §The gates.
- **Read `/docs/` before writing — in the branch that needs it, and by section.** The relevant
  `/docs/standards/` and `/docs/glossary.md` are binding on wording. Only **compose**
  and **refine** ask questions that reading answers, so it is step 3b's and never the preamble's.
  Read it per
[align/evidence-doctrine.md](${CLAUDE_PLUGIN_ROOT}/assets/references/align/evidence-doctrine.md)
§1. Extract the aggregate; never paste the raw dump
§2. Section-address any markdown — a target's `/docs/` included
— `cq components read <path> --sections "§X"`, not the whole file, when only a rule or two
  governs the question at hand; it resolves `/docs/` the same way it resolves this plugin's own
  references. No OKF bundle in the repo (`/docs/index.md` with `okf_version`) → skip silently.
- **Never edit code.** If the work implies code changes, that is `/quenching:specs:execute`.
- **`complexity` is re-evaluated at the close, never mid-pass.** The level
  `/quenching:specs:create` computed from the input is stale the moment this pass writes what the
  input could not support. The close's own recommendation IS that re-evaluation where it names a
  raise; where the pass merely outgrew its size, the evidence that moved it is named and the level
  proposed. A pass that changed no size proposes nothing — the level on disk is still the latest
  word on it.
- **Capture confirms no classification at all — every pass reviews it in silence.**
  `/quenching:specs:create` writes subject, tags and `complexity` as presumptions the human may
  never have looked at. So every pass here also reviews `tags` — silently, narrated in step 6's
  consolidated plan and applied in step 7's single edit. No new screen, anywhere: the review rides
  the edit that was already going to happen.

## The batching contract

| Where | The bounded read(s) |
| --- | --- |
| steps 1+2 | `cq specs status --spec <id> --json`, which also carries the `path` step 1 announces, the gear, and the `sections`/`ready` map compose drives off. Only an ID that must be *chosen* splits this: `cq specs list --json` runs first, because the question depends on its output |
| step 3b | every stage's own section and the union of the spec sections the pass reads or writes — `cq components read` and `cq specs section` together, never one call per source or per stage |
| step 7 | the entire application — the section write, every `cq specs discover` line, every `cq specs record`, `cq specs verification`, `cq specs validate` (plus `cq specs parallel` where `## Tasks` moved), and the closing `cq specs status` that verifies where the pass landed |

A call splits only where the next command's **input** depends on the previous one's output. The
`approved` stamp is the one such split: it waits for step 7's verification to prove `ready` rather
than asserting it off the drafts.

**No turn exists only to announce what the next tool call will do.** "Now I'll load the stage",
"next I'll write the sections" — a turn whose entire content is the call that follows it. Narration
that carries content stays: the pass and its stop conditions (step 3), the consolidated plan
(step 6), the report (step 8).

**A recommendation rides inside the question, never in a turn before it.** Where a choice is
genuinely the human's, the recommendation and the reasoning behind it go in the **AskUserQuestion**
payload — the recommended option first and marked "(Recommended)", the reasoning in its description
— so the human answers in one word and no turn was spent setting the question up.
**This contract stops at the edge of how questions are grouped.**
[questions.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-develop/questions.md) §The four shared
mechanics §1 is the only authority there: a question travels with the ones whose answers cannot
change it, and alone otherwise. "Fewer turns" is a rule about tool calls and about prose turns; it
is never a licence to put two dependent questions into one call, and **never a licence to skip a
question** — this command changes when a question is asked, never whether it is.

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
submitted (step 6), the backend is the window the human watches the pass through and the place a
correction is given, so it is stated before anything is read and repeated in the report (step 8).
**Done when:** one provider-owned spec is resolved and its backend URL has been announced.

### 2. Read the spec's STATE — not its body
```bash
cq specs status --spec <id> --json      # stage, section states, ready map, records, tasks, gate, path
```
**This is the same call as step 1** — §The batching contract's first row. The id either came in
the input or was inferred, and the payload answers both steps at once.

**The payload also carries the gear and the gap.** `records.priority.complexity` rides it, so
reading the gear costs nothing; absent, or no `priority` record at all, reads as `high`
([spec-driven.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-develop/spec-driven.md) §The scale). So does
`ready: {ok, missing, malformed}`, which is the list compose owes — **no `cq specs next` call is
needed to obtain it**.

That is the whole of this step. **No section body is pulled here.**
**Done when:** the spec's stage, section states, ready map, records, gate, backend URL and gear are
in hand.

### 3. Derive the pass, and name it
Look the derived stage and the gear up in
[questions.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-develop/questions.md) §The pass —
already loaded. The pass is up to four stages, always in this order:

| Stage | Runs when |
| --- | --- |
| discoveries | `## Discoveries` holds a line nobody resolved |
| compose | the spec is not yet `ready` |
| refine | the gear is `high` or `xhigh`, or the input asked for it |
| approval | always |

A spec already `ready`/`approved` has nothing to compose, so an invocation over one **is** a refine
request; at `low` that request raises the gear to `high` (or `xhigh`, where the premortem is asked
for) before refine runs, because `low` never refines.

Name, in ONE narration before the first question: **the stages this pass will run, in order**, the
gear, whether the human will be asked anything and at which stages, and **each stage's stop
condition**. The gear is announced here and nowhere else.
**Done when:** the pass's stages are named in order, with the gear and each stop condition.

### 3b. Load what THIS pass needs — and nothing more
Now that the pass is known, and in **one call** — §The batching contract's second row, both
commands together, every stage at once:

```bash
cq components read ${CLAUDE_PLUGIN_ROOT}/assets/references/specs-develop/questions.md \
  --sections "§Compose" --sections "§Approval"      # + "§Refine" where refine runs,
                                                    # + "§Who answers", + "§Gathering the evidence"
cq specs section <id> "<every heading this pass reads or writes>"     # the union, once
```

| Stage | Spec sections it reads or writes |
| --- | --- |
| discoveries | `## Discoveries` |
| compose | `## Problem` `## Design`, plus every heading `ready.missing`/`ready.malformed` named in step 2 |
| refine | `## Problem` `## Proposal` `## Design` `## Alternatives Considered` `## Risks` `## Impact` `## Tasks` |
| approval | `## Proposal` `## Impact` `## Risks` — and it writes nothing into the body |

Ask for the **union**, in one call. A heading that is absent comes back as `(## X is absent)` with
exit 1 — a result, not a refusal, and it is the same gap map `ready` already reported.

**Compose and refine also read `/docs/`** (Doctrine): the `/docs/standards/` this spec's
`## Impact` declares — the declared files, never the folders they sit in — and
`/docs/glossary.md`. Either **may** delegate that reading to a read-only sub-agent under
§Gathering the evidence, which returns one compact table. It is an option, not a step: for a
two-file spec, keep the reading.
**Done when:** every stage's section and the union of spec sections are in hand, in one call, and
nothing else was opened.

### 3c. Run the dependency sweep — once, at the pass's open
Skip whole where `### Mapa de dependências` already sits under `## Design`: a spec is swept at most
once. **This step opens nothing** — step 3b's two calls already carry both the `## Design` it reads
and the §Gathering the evidence that governs it.

Otherwise dispatch one read-only `Task` sub-agent under the **wider** profile of §Gathering the
evidence, briefed with whichever of `## Problem` / `## Proposal` is filled, asked for the one table
that section names: every file the proposal's own area touches or is touched by, and what breaks or
goes orphaned if it changes.

**The orchestrator holds the result; the sub-agent never writes it.** The table waits for step 7's
own consolidated write, landing as `### Mapa de dependências` under `## Design`, dated.
**Done when:** the spec already carries a map, or this pass holds the sub-agent's table to write at
step 7.

### 4. Compose
Skip where the spec is already `ready`. Otherwise follow §Compose, under the four shared mechanics:
sequential to shape, grouped to close, every question carrying **an inline recommendation**, every
answer naming the section it lands in, and the stage's declared stop condition.

**The gear decides who answers; §Compose is unchanged either way.** At **`low`** the pass answers
every item **from evidence**, names the assumption inside any answer that rests on one, and parks
what no evidence answers as an `## Open Decisions` line carrying how it will be decided — it asks
nothing. At **`medium`, `high` and `xhigh`** it drafts those same answers first and then asks the
human **about the draft**, which is why independent headings travel grouped: a question about a
section already drafted cannot change what another drafted section says.

Questions must be **specific to this spec**. One that would read identically against any spec is
noise — do not ask it, and do not pad the count with it. That holds for a drafted answer too: one
that would read identically against any spec is a default, not evidence, and it is parked.

Nothing is written. Keep a running list of `(question or drafted answer, its source, target
section)`.
**Done when:** the ready set is closed in the draft, or the user called it.

### 5. Refine — where it runs
Runs at **`high`** and **`xhigh`** automatically, and at any gear where the input asked for it
(which raises a `low` gear first, per step 3). Skip whole otherwise, and say so in the report —
`medium` reaches refine through step 8's recommendation, not through this step.

Follow §Refine over what step 4 just drafted: the signals select the lenses, the premortem runs
unconditionally at `xhigh`, and a criticism once answered rewrites the next one, so this stage is
sequential.

**This is the one stage that may overturn.** It rewrites the draft, not the file — both land in
step 7's single edit, so the spec never holds the superseded version. **A change to `## Proposal`
is always the human's**, never a decision this stage takes alone; where no human is present the
pass did not reach this stage at all.
**Done when:** §Refine's stop condition is met, or the user called it.

### 6. Consolidate the edit, and narrate it
Load the authoring doctrine now — the union of `artifacts.md` sections this pass needs, in one call:

```bash
cq components read ${CLAUDE_PLUGIN_ROOT}/assets/references/specs-develop/artifacts.md \
  --sections "§Writing a section through stdin" --sections "§The explicit-none rule" \
  --sections "§The nine definition sections" --sections "§`## Impact`" --sections "§`## Tasks`" \
  --sections "§Execution metadata"
```

**The consolidation stays; the confirmation goes.** Show every accumulated answer as a single plan —
per section, what changes and the answer it came from, drafted under the doctrine just loaded, with
what refine overturned marked as such — and then write it in step 7. The plan is **narrated, never
submitted**: do not ask for a confirmation of it and do not wait for one. Invoking this command is
the authorization.

Anything that turned out to belong outside the spec is narrated here too: a durable rule or a term
as a **routed offer**, not an edit, and an **out-of-scope follow-up as the one `## Discoveries` line
this edit will park** — a line, not an offer (§Invariants).
**Done when:** the plan has been narrated in full, as one plan for the whole pass.

### 7. Apply, verify, and record what the pass earned
**Every write of this step is ONE call** — §The batching contract's third row: the section write,
the `## Discoveries` lines, the records, `verification`, `validate`, and the closing `status`.

Write the narrated sections with `cq specs section <id> "<Heading>[,<Heading>…]" --write` (bodies
on stdin) — it creates each heading in canonical position on first write, so creating and revising
are the same call. An emptied section becomes an explicit `- none — <reason>`, never a deleted
heading.

**The bodies go on stdin as one heredoc, in the same call** — a scratch file, a `mkdir` and a `cat`
are three turns buying what one already does:

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
was. One heading with a raw body and no `## ` line is the singular form and is unchanged. The N
splices land as ONE write, which is what makes a pass all-or-nothing.

Every follow-up the plan parked is written in this same edit — `cq specs discover <id>
"<finding>"`, one call per line — and never mid-stage, which
[questions.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-develop/questions.md) §The four shared
mechanics forbids. The call creates `## Discoveries` when the heading is absent, and a filled
`## Discoveries` moves no derived stage.

Then the frontmatter records this command owns — read
[questions.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-develop/questions.md) §Recording the
pass for which stage earns which, and
[spec-driven.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-develop/spec-driven.md) §Frontmatter
for the write-once semantics, in one call. Each is stamped through `cq specs record`:

| Record | When | Call |
| --- | --- | --- |
| `refined: {mode, date}` | compose or refine ran; `mode` is the deepest reached | `cq specs record <id> refined --set mode=<compose\|refine> --set date=<today>` |
| `verification` | compose settled the policy | `cq specs verification <id> <per-task\|per-section\|end-of-plan>` |
| `tags` | the pass changed the spec's scope, or the capture presumed wrong | `cq specs tags <id> "<whole list>"` |
| `complexity` (in `priority`) | the pass outgrew its size and the human approved the new level, or the close's recommendation was taken (step 8) | `cq specs record <id> priority --set complexity=<level> --set date=<today>` |

`approved` is **not** stamped here — it waits for the verification below to prove `ready`, and is
stamped in step 8.

`cq specs tags` **replaces** the whole list, never appends — reissue the subject's own fixed tags
together with whatever this pass adds, or the fixed ones are lost.

The title is the sole short description every ranked listing prints (`cq specs next --front
--table`). Keep it descriptive when the spec's scope changes; the sections carry the rationale and
detail, so no separate summary field is maintained.

`verification` is a plain frontmatter key rather than a record, so it has a verb of its own instead
of a `--set`. Omit the value to read what is in force and whether anything declared it; absent
means the default, and stamping the default to make it explicit records a decision nobody made.

`complexity` is a field of `priority`, and the record merges — `level` and `criticality` survive
a re-stamp that touches only the size, and `date` is the ranking's own.

Then, in the same call, **verify where the pass landed**: `cq specs validate --spec <id>` and
`cq specs status --spec <id> --json`. **When this pass touched `## Tasks`, run `cq specs parallel
--spec <id>` here too** — exit 1 names the `[P]` group whose `files:` sets are not disjoint, and
definition time is the only moment that is cheap to fix. Report what each says; a `[P]` nobody
proved is a promise execution will refuse.
**Done when:** the pass's one edit is written, the records it earned are stamped, and validate,
`status` — plus `parallel`, where `## Tasks` moved — have run in that same call.

### 8. Close on a recommendation, and report
The re-derived stage came back in step 7's call, so **this step opens nothing**. Compare it with
where the pass expected to land: a divergence is named and the pass re-enters at step 3 with a pass
derived from the real stage. **The re-entry is narrated, never offered.**

Otherwise close, and how it closes is the gear's — §Approval owns the screen's own content:

- **`low`** — no screen. With `ready` now **proved** by step 7's payload and `approved` unset, stamp
  it here: `cq specs record <id> approved --set date=<today> --set by=low-gear`. **`by:` is never
  omitted** — a record with no `by:` reads as `human`, so leaving it off silently claims a human
  this pass never had.
- **`medium` · `high` · `xhigh`** — ONE closing screen that **recommends** rather than defaulting to
  approve. Judge what the pass produced against §Refine's three signals and lead with the move they
  argue for, marked "(Recommended)", carrying the signal in its own text: approve, refine (a raise
  to `high`), refine with the premortem (a raise to `xhigh`), or stop. Choosing a raise IS the OK to
  restamp `complexity`; apply both and re-enter at step 3 under the raised level. A pass where
  refine already ran recommends approving and names what the argument settled — never the raise the
  human already took.

**A raise re-enters the pass; it never restarts it.** What compose already wrote stays written —
the raise buys the argument the lower gear did not have, over the artifact it drafted.

**The screen belongs to whoever holds the human.** Running standalone, present it. Running as a
sub-agent under a conductor, present nothing: return the screen's content and let the conductor
present it — a sub-agent never talks to the human, at any gear.

Then report:

```bash
cq components read ${CLAUDE_PLUGIN_ROOT}/assets/references/specs-develop/report-mold.md \
  --sections "§The report mold" --rules-only
```

Emit §The report mold. The single-spec header line carries the stage **after** the pass; two body
blocks:

1. **The pass** — fixed. The spec's URL in the backend, repeated from step 1 off the same `path`
   field and never re-fetched; **the stages that ran, in order, and whether refine ran or was left
   to the close's recommendation**; the gear and what it changed about who answered; how many
   questions were asked and answered, and how many answers the pass gave from evidence with an
   assumption named; **what refine overturned**, if anything; **an `approved` stamped
   `by: low-gear` on its own line**; the sections edited; the records stamped; the routed offers and
   whether each was taken; the stage before and after, and whether it landed where the pass expected.
2. **Parked into `## Discoveries`** — optional, and every line **quoted**.

Close on §The next-step block — `/quenching:git:branch <id>` once `approved` is stamped, naming it
the natural moment to isolate before `/quenching:specs:execute <id>` writes any code;
`/quenching:specs:develop <id>` again to refine a spec that is already `ready`; or
`/quenching:specs:execute <id>` to carry it to the end task by task.

**Isolation is named, never taken.** A pass that rewrites half a spec dirties the tree, so the human
may want it on a branch before the next pass or before `execute` — naming `/quenching:git:branch
<id>` in the next-step block is that suggestion, stated once at the close and never asked as a
question mid-pass.
**Done when:** the pass closed or re-entered, and the summary is shown.

## Invariants to never violate

- **NEVER edit implementation code.** If the spec implies code changes, stop and name
  `/quenching:specs:execute`.
- **Never write into `/docs/`.** A durable rule a question surfaces routes to `/quenching:knowledge:add`, an
  understanding to `/quenching:knowledge:learn`, a term to `/quenching:knowledge:define` — **offered, never
  auto-written**. The rules a spec *proves* are written during execution, not during definition.
- **Never write into `## Tasks` what the merge owns.** A version bump, a changelog entry, a manifest
  re-stamp; the `/docs/` the work *revealed* rather than declared; the cycle's own closing actions
  (review, archive, distil, merge, open the PR) — all three belong to `/quenching:specs:conclude`,
  which settles them once what the release *is* is knowable. A standard this spec **declares** under
  `## Impact` still gets its own checkbox and still must: the axis is declared versus revealed,
  never docs versus code.
- **Park an out-of-scope follow-up; never mint a spec for it.** A finding this pass raised that does
  not belong to the spec being developed becomes ONE line of `## Discoveries` on that same spec —
  `cq specs discover <id> "<finding>"` — landed inside the step 7 edit, never as a loose call
  mid-stage. Turning a follow-up into its own spec stays `/quenching:specs:conclude`'s. This route
  is not an offer: nothing is created, so there is nothing to ask for.
- **Inside a develop pass, `cq specs new` runs only as the discoveries stage's `promoted:`
  resolution.** Nothing else here mints a spec.
- **Changing the spec's intent is refine's, and only with a human.** Compose may not overturn what a
  human settled; refine may, and a change to `## Proposal` is always put to the human rather than
  taken. Where no human is present the pass never reached refine, so the licence never runs
  unattended — and a request that replaces the spec's subject outright is still a fresh
  `/quenching:specs:create`, not a rewrite of what was already agreed.
- **Never write a section that was not narrated first.** The consolidated plan is shown in full
  (step 6) and then applied.
- Never write anything mid-stage — accumulate across the whole pass, then apply once.
- **Never group two questions whose answers can change each other**, and never ask alone what could
  have travelled with them. Grouping is by dependence, never by convenience, and every question
  carries a recommendation either way. **And never drop a question for cadence:** this command
  changes when a question is asked, never whether it is.
- Never ask the human to choose a mode; the derived stage says where composing starts — **and never
  ask them to choose a gear**: the level on disk chooses it, or a conductor declares a moved one in
  the invocation.
- **Never let a `low` pass ask a question, and never let it refine.** An item no evidence answers
  becomes an `## Open Decisions` line with how it will be decided. Inventing the answer and asking
  anyway are the two failures here, and the second is the one that breaks what the gear promised. A
  refine asked for at `low` raises the gear first; it never runs under it.
- **A sub-agent may read; it may never ask, write, or decide.** The evidence sweep of step 3b
  returns a table. Every question, every `cq specs` call and every confirmation stays here.
- **The dependency sweep's map is written by the orchestrator; the sub-agent never touches the
  spec.** Step 3c's sub-agent returns a table too, same as step 3b's — the map lands only inside
  step 7's own consolidated write, into `### Mapa de dependências` under `## Design`.
- **Never hand this command file `context: fork`** — every gear but `low` asks the human its own
  questions, and step 3c's read-only sub-agent is a step inside that, never a delegation of it.
- **Never open a cited reference as a file.** `§X` is an address, loaded through
  `cq components read --sections`; and never hoist into the preamble what only one branch reads.
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
  screen, `low-gear` when the level authorized the mode and this pass stamped on that authority
  after `ready` was proved.
- **Never restamp `complexity` beyond what the close authorizes**: a fall always needs a human, and
  a level a pass did not move is the latest word on it, not a value to re-propose.
- Never gate on refinement. A spec may always be built unrefined; `sp-unrefined` is a warning by
  design.
- Never rename a spec, and never rewrite its `date:` — the capture date is stamped once, at
  creation.
