---
slug: restore-routing-info-on-docs-commands
title: Restore trigger phrases and boundaries on the nine bare /docs:* descriptions
verification: per-task
priority: {level: 2, criticality: high, complexity: 4, date: 2026-07-29}
refined: {mode: gate, date: 2026-07-28}
---

# Restore trigger phrases and boundaries on the nine bare /docs:* descriptions

<!-- ONE spec is ONE file for its whole lifecycle. Phases enrich it; they never split it.

     `specs.py new` stamps the frontmatter and `## Problem` ALONE — a captured spec is four
     lines of body, not a fourteen-heading skeleton. Every other heading below is created on
     first write by `specs.py section <slug> "<Heading>" --write`, which inserts it in the
     canonical position with the guidance comment kept here.

     THE STAGE-SCOPED EXPLICIT-NONE RULE. A heading is required — and required to carry
     `- none — <reason>` when it has nothing in it — only once ITS OWN gate is reached:

       new (capture)        `## Problem`
       ready (derived)      the nine definition sections (`## Problem` .. `## Risks`)
                            AND `## Tasks`
       ready (warn only)    `## Overview` non-empty, `## Handoff` non-empty
       promote -> archive/  `## Outcome`

     `ready` is a DERIVED STAGE, not a folder: a spec lives in `plans/` for its whole active
     life, and filling those ten sections is what makes it ready. Nothing refuses on that
     gate — it is a floor `execute` reports against, and the human's go-ahead is the
     `approved:` frontmatter record, asked for inline.

     Before its gate, a heading's absence is NOT an omission — it is a not-yet. After its
     gate, three rules decide whether a section counts as filled:

       1. `- none — <reason>` counts as filled. An omission and a null are different facts.
       2. A heading present with an EMPTY body is malformed and refuses. It is neither an
          answer nor a not-yet.
       3. An absent heading before its gate is legal.

     Headings are a PARSED contract — canonical English, exactly as written here. Body prose
     follows the repo's language. A heading outside this set is a stray and validate flags it.

     AUDIENCE. Each section names who reads it. `## Overview`/`## Problem`/`## Proposal`/
     `## Design` are for the human — examples and plain language belong there.
     `## Handoff`/`## Tasks` are for agents — terse, with `files:`/`verify:`/`pattern:`
     metadata. An orchestrator never sends the human sections to an executor; that is what
     lets one file serve both audiences without bloating agent context. -->

## Overview

Nine of the eleven /docs:* and /skill:* command descriptions lost their quoted trigger phrases and
`Not for:` boundary clause when the command surface was collapsed to one file per entry point, so a
plainly-worded ask like "write this down in the docs" has nothing to tell it apart from /docs:add,
/docs:learn, /docs:define, or /docs:import. `## Proposal` restores all three parts of a conformant
description — concept, triggers, boundary — reusing phrasing that already exists elsewhere in the
repo rather than inventing new text, and `## Design` requires all eleven descriptions be drafted as
one allocation table, reviewed for collisions, before any file is edited. Restoring them pushes the
surface past its always-on character ceiling, which has zero headroom by construction, so
`## Tasks` runs in a fixed order: write the descriptions, then re-measure the ceiling from an actual
run and transcribe that number everywhere it lives, then bump the release version.
`## Open Decisions` flags that approval is currently withheld: a still-open spike into
`disable-model-invocation` could make this whole restoration unnecessary, or confirm it and
multiply its cost roughly tenfold once the surface grows as planned.

## Problem

The collapse into one file per entry point deleted the half of each pair that carried the quoted
trigger phrases and the `Not for:` boundary. Restoring them was called affordable, and it happened
— on `/specs:*` and on most of `/skill:*`. It never reached `/docs:*`.

Measured on `main` at 4.1.0, `skills.py lint` reports `sk-trigger-position` **and**
`sk-no-boundary` on nine of the eleven `/docs:*` commands: `add`, `define`, `documentation:build`,
`glossary-backfill`, `harness`, `import`, `import-memory`, `learn`, `status`. Only `/docs:align`
carries a full description. `/skill:eval` carries both findings too, and `/skill:new`
`sk-trigger-position` — so the command that measures routing and the command that mints commands
are themselves among the least routable on the surface.

Both are warnings, so the surface reports clean while the routing information is absent from the
only text that is always in context. A user who says "capture this thought" reaches `/specs:create`
because that description quotes the phrase; a user who says "write this down in the docs" has
nothing to route to.

**The constraint that makes this a spec rather than an edit.** The always-on ceiling has **no
headroom by construction** — it equals the surface's current total. It read 11,565 when this was
captured; it reads **12,726** today, because the ratchet fired on 2026-07-28 when `/specs:isolate`
became the 25th command and a human re-measured. Restoring the missing descriptions will cross it
again, and crossing it is the signal working, not a failure: it forces a measured re-set rather
than an unpriced expansion. So this spec must buy the routing information and re-measure the
ceiling from a run, in that order, and state both numbers.

Discovered by `instrument-and-extend-skill-front` (task 3.x territory, recorded in its
`## Discoveries` as two commands) and re-measured during its conclude, where it turned out to be
eleven.

## Proposal

Every command on the surface carries the three parts
[context-budget.md](/docs/standards/automation/context-budget.md) §What the description may carry
already calls mandatory — the leading concept, quoted trigger phrases in the **second** sentence,
and a `Not for: <adjacent job> → <owning command>` boundary — and the surface-wide ceiling is
re-measured **from a run** afterwards, in that order.

**Eleven descriptions, not nine.** The title names the nine bare `/docs:*` that motivated the
spec. The scope settled while shaping it is *every command reporting either code*, which adds
`/skill:eval` (both codes) and `/skill:new` (`sk-trigger-position` only — it already carries a
boundary). That makes the end state a checkable absolute rather than a list of improved files:
`skills.py lint` reports **zero** `sk-trigger-position` and **zero** `sk-no-boundary` across all
25 commands.

**What this buys — stated more narrowly than `## Problem` did.** Not "routing now works". A bare
label already routes a clearly-worded ask: `functional-checks.sh` probe c fires
`"add a standard: we always use snake_case for database columns"` → `quenching:docs:add` against a
76-character description, and the collapse's three spoken probes all survived. What eleven bare
labels cannot do is **discriminate**. "Write this down in the docs" has to choose between
`/docs:add`, `/docs:learn`, `/docs:define` and `/docs:import`, and nothing in a `/`-menu label
answers it — the `Not for:` clause is the only text that does, and it is the part truncation eats
first. So the claim is: *the routing information the standard mandates is present, allocated
without collision, and truncation-safe.* Whether routing measurably improved is a
should-trigger/should-not-trigger question this spec deliberately does not answer — see
`## Out of Scope`.

**What it costs, and why that cost is the spec rather than an edit.** The eleven descriptions
total 935 characters today. At the 400–650 band `## Design` sets they land near 5,450, taking the
surface from 12,726 to roughly **17,200** (~4,300 approximate tokens, from ~3,182). That crosses
`DEFAULT_CEILING`, which equals the current total by construction, so `skills.py budget` exits 1
with `sk-budget-ceiling`. **That is the ratchet working, not a regression** — and this spec is its
**second** firing and the first caused by *description growth* rather than by a new command being
minted, which is a fact about the mechanism the standard does not yet record.

The re-set is therefore a declared part of this spec, not bookkeeping discovered at the end: the
new figure is transcribed from what `budget` printed into the three places that hold it —
`skills.py` `DEFAULT_CEILING`, `context-budget.md`, and `README.md` — and never estimated. Every
number above except the two measured ones (935 and 12,726) is an estimate, and the spec is done
when the run has replaced them.

## Out of Scope

- **Proving the restored triggers actually route.** That is a should-trigger /
  should-not-trigger measurement, owned by `/skill:eval` against a per-command eval fixture —
  and `assets/evals/` holds exactly three case sets today (`skill/agent/new`, `skill/hook/new`,
  `specs/capture`), none of them on the `docs` front. Building nine fixtures and running each
  twice in isolated sub-agents is a larger job than the restoration itself, and
  [context-budget.md](/docs/standards/automation/context-budget.md) §What the collapse measured is
  explicit that cheapness and routability are independent questions. This spec closes the
  conformance gap; the measurement is a follow-up, and until it runs no claim of improved routing
  is made anywhere in this spec.
- **Adding discrimination probes to `functional-checks.sh`.** The natural cheap instrument — one
  probe asserting `"write this down in the docs"` reaches `/docs:learn` and not `/docs:add` — is
  blocked twice over: each probe costs a fresh `claude -p` session, and the script cannot decode
  its own evidence on this platform at all (`fix-functional-checks-encoding`). Deferred to that
  spec landing.
- **Giving `skills.py lint` a way to gate on a selected warning code.** `lint` exits 0 on
  warnings, so every consumer that wants a warning to fail a build must filter the `--json`
  itself — including every `verify:` in this spec's `## Tasks`. A `--code X --fail-on warn` pair
  would fix that for good, and it does not follow from this spec's `## Problem`. The inline filter
  in `## Design` costs nothing and works today; the flag is a follow-up.
- **The other three lint codes.** `sk-step-criterion` (9 commands), `sk-unscoped-bash` (5) and
  every body-level defect are untouched. They are body work; this spec edits **only** frontmatter
  `description` values, plus three transcriptions of one number.
- **Changing the zero-headroom ratchet.** `context-budget.md` §The ratchet fired exactly as
  predicted already prices the shape — every re-set is a three-file bookkeeping change — and
  chooses it deliberately. Re-litigating that is its own spec; this one pays the price and records
  a second data point about when the ratchet fires.
- **The `/skill` → `/automation` rename.** `restructure-claude-front-namespace` (stage `designed`)
  moves `/skill:new` → `/automation:command:new`, `/skill:eval` → `/automation:command:eval` and
  `/docs:harness` → `/automation:harness:align`, and rewrites every moved-path citation across
  `commands/**`. Nothing here anticipates it: descriptions are written for the paths that exist
  today, and that spec's own citation task covers the boundary clauses either way — see
  `## Risks`.
- **Rewriting `README.md`.** Only the three lines transcribing the ceiling figure change.
  `rewrite-readme-for-collapsed-surface` owns the rest of that file.

## Impact

### Standards this spec will write into docs/standards/

- `docs/standards/automation/context-budget.md` — the re-measured ceiling in §The per-surface
  ceiling and the `breakdown` sample, plus a **third** entry in the ratchet's history: the first
  firing caused by description growth rather than by a new command being minted. Its `timestamp`
  moves to the build date, or the doc fires `stale-doc` on its own `commands/**` resource.

### Standards at `authority: background` this spec may resolve

- none — `context-budget.md` is `authority: background` and this spec does **not** graduate it. Its
  own stated condition is a measurement on this plugin plus at least two adopting repos, and it
  rules out exactly what this spec adds: "a bigger number from the same repo is still one repo."

### Product code this spec expects to touch

- `plugins/quenching/commands/docs/{add,define,glossary-backfill,harness,import,import-memory,learn,status}.md`
  and `commands/docs/documentation/build.md` — the frontmatter `description` value **only**; no
  body line changes.
- `plugins/quenching/commands/skill/{new,eval}.md` — same, and the only files outside the `docs`
  front.
- `plugins/quenching/assets/bin/skills.py` — `DEFAULT_CEILING` and its dated changelog comment
  (the constant is the ceiling's home; the two docs transcribe it).
- `plugins/quenching/README.md` — the three lines carrying the figure, and nothing else.
- `plugins/quenching/VERSION`, `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`,
  and the `VERSION` constant in all three shipped scripts — the release lockstep, because a
  shipped script's behaviour changes.

**Nothing in a target repo changes shape.** No installed artefact is rewritten, no migration runs,
and an adopter sees this only as a plugin upgrade. The always-on cost, however, lands on every
session in every repo that installs it — which is the point of pricing it here rather than
discovering it later.

## Validation

All commands run from `plugins/quenching/`. Every check is deterministic and local; the one that
is not (**V7**) is declared conditional rather than dropped. `## Tasks` cites these by id.

**V1 — both target codes are gone, surface-wide.** Must print nothing and exit 0. Checking the
exit code of `lint` alone proves nothing: both codes are `severity: warn`, and `lint` returns
`"ok": true` with them present (measured on `commands/docs/add.md`, exit 0). The filter is the
check.

```bash
python3 assets/bin/skills.py --root . lint --json | python3 -c "import json,sys; \
B=[f for f in json.load(sys.stdin)['findings'] \
   if f['code'] in ('sk-trigger-position','sk-no-boundary')]; \
[print(f['code'], f['command']) for f in B]; sys.exit(1 if B else 0)"
```

**V2 — closing them did not overshoot a cap.** Same shape, codes `sk-metadata-cap` (error, 1,536)
and `sk-description-portable` (warn, 1,024). Must print nothing and exit 0. The 400–650 band means
this should never be close; if it fires, a description is carrying *how it works*.

**V3 — the ceiling was set from the run, not from this spec's estimate.** Must print two **equal**
numbers and exit 0.

```bash
python3 assets/bin/skills.py --root . budget --json | python3 -c "import json,sys; \
d=json.load(sys.stdin); print(d['total'], d['ceiling']); \
sys.exit(0 if d['total']==d['ceiling'] else 1)"
```

`budget` exiting 0 is **not** the check — it exits 0 for any `total <= ceiling`, so a ceiling
transcribed 200 characters high from `## Proposal`'s estimate passes an exit-code gate while
having silently disabled the ratchet for the next command minted. Equality is what proves the
zero-headroom property survived (risk 1).

**V4 — the surface still has the shape it had.** `doctor --json` reports `"commands": 25`,
`"findings": []`, exit 0. This spec adds and removes no command; a change here means a
description edit corrupted frontmatter.

**V5 — the figure agrees in all three places.** `grep -rn "<measured>" assets/bin/skills.py
../../docs/standards/automation/context-budget.md README.md` hits all three files, and no
*current-value* site still reads 12,726. The historical sentences in `context-budget.md` that
narrate `2,083 → 11,565 → 12,726` **must survive** — they are the ratchet's record, and this
spec appends a third transition rather than overwriting the second.

**V6 — the release lockstep holds.** All four print the same new version, and
`.claude-plugin/plugin.json` + `../../.claude-plugin/marketplace.json` carry it too:

```bash
cat VERSION; python3 assets/bin/skills.py --version; python3 assets/bin/specs.py --version
python3 assets/hooks/okf-validate.py --version
```

**V7 — spoken routing did not regress. CONDITIONAL.** `./assets/bin/functional-checks.sh` is the
mandatory instrument for any spec touching `commands/**`, and probe c asserts `/docs:add` against
a description this spec rewrites. It **cannot decode its own evidence on this platform**
(`fix-functional-checks-encoding`): every assertion fails for lack of evidence, indistinguishable
from a surface that did not load. So:

- if that spec has landed, V7 is a hard gate and must exit 0;
- if it has not, the run is recorded **inconclusive** and graded as nothing in either direction,
  per `docs/standards/quality/surface-verification.md` §The four preconditions, item 4. A run that
  cannot read its evidence is never recorded as a pass, and never as a failure.

**V8 — the bundle still conforms.** `python3 assets/hooks/okf-validate.py ../../docs` reports
**0 errors**. Baseline before this spec: 0 errors, 2 warnings (`resource-unresolved` on
`agents.md`, `stale-doc` on `hooks.md`) — both pre-existing and untouched here. Editing
`context-budget.md` without moving its `timestamp` would add a third warning on the same doc this
spec declares, so V8 catches that directly.

**What no check here proves.** That the restored descriptions route better than the bare labels
did. Nothing in this list measures routing, by design — see `## Out of Scope` and accepted risk 7.
A green run means *the routing information the standard mandates is present, allocated without
collision, and truncation-safe*, and nothing more.

## Design

### One allocation table, written before any file is edited

The failure mode that would make this spec worse than doing nothing is **trigger collision**: two
descriptions quoting phrases that cover the same ask, so the model now has two confident
candidates where it previously had a coin-flip between labels.
[doctrine.md](/plugins/quenching/assets/references/skill-new/doctrine.md) names both halves —
"a branch without a trigger is a branch that never fires, and two triggers for the same branch are
sediment".

Collision is only visible across the whole set, so the trigger phrases and boundary clauses for
all eleven commands are drafted as **one table** and reviewed as one artifact, *before* the first
file is touched. Writing them command-by-command is what produces sediment.

The table's rows are the confusable clusters, because a boundary that does not name the nearest
lookalike is decoration:

| Cluster | Commands | What has to discriminate them |
| --- | --- | --- |
| write one thing | `add` · `learn` · `define` | a full concept doc · a fact a human just stated · one glossary term |
| bulk ingestion | `import` · `import-memory` | an external source (files/folders/URLs) · this project's Claude Code memory |
| glossary grain | `define` · `glossary-backfill` | ONE term on demand · a sweep of the whole bundle |
| read vs converge | `status` · `align` | reports and writes nothing · forces the bundle into shape |
| site vs content | `documentation:build` · the rest | the mkdocs config and nav · the pages themselves |
| instruction files | `harness` · `add` | `CLAUDE.md`/`AGENTS.md` pointers · a doc inside the bundle |
| automation front | `skill:new` · `skill:eval` | mint or edit ONE command · measure whether one teaches anything |

### Most of the content already exists, in the repo's own words

`/docs:align`'s description is the only full one on the front, and its `Not for:` clause already
states the distinguishing job of **six** of the nine:

> Not for: adding ONE doc → /docs:add; capturing ONE fact a human just stated → /docs:learn; ONE
> glossary term → /docs:define; importing an external source → /docs:import; reading the bundle
> without changing it → /docs:status; the mkdocs site layer → /docs:documentation:build.

So the work is largely **inverting a clause that already exists**, which is also what keeps the
set consistent: two commands cannot claim the same job if both were written from one sentence that
already separated them. The remaining three (`glossary-backfill`, `harness`, `import-memory`) take
their distinguishing job from the role table in `CLAUDE.md`. Trigger phrases are drawn from the
same vocabulary — never invented to fill a slot, because an invented phrase costs always-on
characters and routes nothing.

### Size budget: 400–650 characters, not `/docs:align`'s 1,018

`/docs:align` (1,018) and the `/specs:*` range (614–974) are **not** the model to copy. Those
descriptions carry prose about *how the command works* — "probes okf-validate.py plus two cheap
out-of-band signals before reading anything", "one inventory, ONE plan, one OK" — which
[context-budget.md](/docs/standards/automation/context-budget.md) §What the description may carry
puts in the "belongs in none of them" list.

Concept + triggers + boundary, and nothing else, sizes at roughly:

```
  leading concept      ~ 80-110   (the nine already have this; it is the whole current cost)
  3-4 quoted triggers  ~150-220
  Not for: 2-4 clauses ~150-250
                       ---------
  per description       400-650
```

**Hard rail: no restored description exceeds 1,024 characters**, the Agent Skills portable limit
(`sk-description-portable`). The band leaves wide margin; the rail is what the `verify:` asserts,
so the margin cannot be spent silently. The 1,536 hard cap (`sk-metadata-cap`, an error) is never
approached.

### The `verify:` shape, and the two traps it exists to avoid

**Trap 1 — `lint` exits 0 on warnings.** Both target codes are `severity: warn`, and warnings do
not set the exit code. Measured: `skills.py lint commands/docs/add.md --json` prints
`"ok": true` with both findings present and exits **0**. A `verify:` that checks the exit code
proves nothing at all.

**Trap 2 — a single-file `lint` re-roots.** Given one file, `lint` resolves the root to that
file's directory, so the finding comes back as `"command": "/add", "path": "add.md"` — not
`/docs:add`. A filter written against the full command path silently matches nothing, which reads
as a pass.

Every `verify:` therefore runs the **whole-surface** lint and filters the JSON by code and by
path. One shape, `$P` being the file under test:

```bash
cd plugins/quenching && python3 assets/bin/skills.py --root . lint --json \
| python3 -c "import json,sys; P='$P'; \
F=json.load(sys.stdin)['findings']; \
B=[f for f in F if f['path']==P and f['code'] in \
  ('sk-trigger-position','sk-no-boundary','sk-metadata-cap','sk-description-portable')]; \
[print(f['code'],f['message']) for f in B]; sys.exit(1 if B else 0)"
```

Four codes, not two: the same call proves the finding closed **and** that closing it did not
overshoot a cap — the one regression this spec can cause on the file it is editing.

### Order is a constraint, not a preference

```
  1. draft the allocation table (all eleven, one artifact)   <- no file edited yet
  2. apply it, one description per task, each verified
  3. run `budget --json`  -> it EXITS 1 with sk-budget-ceiling.  Read the total.
  4. transcribe THAT number into the three places that hold it
  5. re-run `budget`      -> exits 0, total == ceiling, headroom zero again
```

Step 3 cannot move earlier and step 4 cannot be estimated: `context-budget.md` requires the
ceiling be "revised only from a measurement", and every prior revision records the run that
produced it. The three places are `skills.py:166` (`DEFAULT_CEILING`, plus its dated changelog
comment), `context-budget.md` (§The per-surface ceiling, the ratchet section, and the
`breakdown` sample), and `README.md` (three lines).

## Alternatives Considered

| Approach | Cost | What it buys | What it forecloses |
| --- | --- | --- | --- |
| **Do nothing** | 0 | surface stays at 12,726; ratchet stays quiet | nothing — but the standard stays violated on 11 of 25 commands |
| **Copy `/specs:*` sizing** (~850–1,000 each) | ~+9,000 chars → ~22,000 | front-to-front consistency | the diet; propagates a defect |
| **Boundary only, no triggers** | ~+2,400 chars | closes `sk-no-boundary` on 10 | leaves `sk-trigger-position` on 11; no truncation-safe routing |
| **Shrink instead of grow** (two-tier) | negative | ~11,000 chars back | already tried and superseded |
| **Measure first, write only what scores** | 9 eval fixtures × 2 runs | every character evidence-backed | impossible in this order — see below |
| **Restore concept+triggers+boundary at 400–650** ← chosen | ~+4,500 chars → ~17,200 | conformance, discrimination, truncation-safety | nothing; the eval measurement stays available |

**Do nothing** is the one that has to be argued against rather than dismissed, because it is what
has actually been happening since the collapse. It loses on a second-order cost: both codes are
warnings, so the surface reports *clean* while eleven commands violate a standard the repo wrote
down. A checker that reports a defect nobody ever closes teaches everyone to skim its output, and
the next real finding is skimmed with it. Either the standard is enforced or §What the description
may carry should be softened — leaving both in place is the only outcome with no defender.

**Copy `/specs:*` sizing** loses on its own evidence. Those descriptions run 614–974 because they
narrate *how the command works*, which `context-budget.md` explicitly excludes. Copying them
doubles this spec's character cost to propagate a defect. (It also argues the `/specs:*`
descriptions should themselves be trimmed one day — noted, not attempted here.)

**Boundary only** is the closest call, and it is genuinely cheap: the boundary is the half that
does the discriminating, and probe c shows a conventionally-worded ask already reaches its
command without any trigger at all. It loses because the two halves serve different users. The
boundary helps the reader who worded the ask the way the docs do; the quoted trigger helps the one
who did not — and the standard puts triggers in the **second sentence** precisely so truncation
cannot reach them, which is a guarantee a boundary-only description cannot offer. Taking half now
also makes the other half harder later: a second pass re-opens eleven files and fires the ratchet
a second time.

**Shrink instead of grow** was a real spec: `skill-description-tiering` (2026-07-26,
`outcome: abandoned`), which proposed cutting always-on metadata by 87% on the premise that these
commands are operated by typed `/` and a description the human never reads buys nothing. Stated at
its strongest, that premise is still live. It loses on two facts that landed after it:

- It was **superseded, not refuted** — abandoned at its own gate in favour of
  `collapse-skills-into-commands`, with its analysis recorded as holding up. So its argument
  deserves the answer below rather than a citation.
- The surface then chose the other side, deliberately: every command keeps **default invocation**
  (no `user-invocable: false`, no `disable-model-invocation`), so the model is expected to select
  commands from prose — and `context-budget.md` §What the collapse measured records that spoken
  routing *was measured after the collapse and survived*, three natural phrases reaching their
  command by description alone. A description that routes is not metadata the human never reads;
  it is the only thing serving the invocation path the plugin deliberately kept.

**Measure first** is the one this spec would most like to take, and it is not available. An eval
run scores `shouldTrigger` / `shouldNotTrigger` prompts against a description that already
contains the phrases; there is no way to measure the hit rate of a trigger that has not been
written yet. `skill-evaluation.md` §Description tuning draws the same line — measurement
authorizes *tuning* (a trigger is removed only on a measured miss), while writing one is
**authoring**, which needs the human whose intent the command encodes. Write first, measure
after, remove only on a measured miss. That is also why nothing here may later be trimmed for
length.

## Open Decisions

**BLOCKING — the spec's load-bearing assumption is contested, and approval was withheld on it
(2026-07-28).** `## Risks` opens by naming the assumption this spec rests on: that a model routes
better from quoted triggers plus a boundary than from a bare label, at a cost worth paying. The
cost half is now contradicted by a stated constraint that was not in `## Problem`:

> the command surface is expected to grow **~10x** (25 → ~250), and the description reduction was
> **deliberate for that scenario** rather than collateral damage from the collapse.

Scaled from the measured 12,726 over 25 commands, the always-on cost at 250 is ~18,250 characters
(~4,560 tokens) with bare labels, ~131,250 (~32,800 tokens) at this spec's 400–650 band, and
~210,500 (~52,600 tokens) at `/specs:*` sizing. At that scale the per-command always-on
description model does not survive **in any variant**, including doing nothing. This spec would
therefore buy conformance with a standard whose own economics fail one order of magnitude out.

**How it gets decided — one spike, and it gates both directions.** Whether
`disable-model-invocation: true` blocks only autonomous selection, or **also** blocks an explicit
by-name Skill call. This plugin's conductors reach their stages by name
(`/align` → `quenching:docs:align`), which is why `CLAUDE.md` forbids the flag today, and nobody
has established which of the two it is. `functional-checks.sh` check 2 is already that shape.

- **blocked only** → the whole surface can go typed-only at **zero** always-on cost, and this spec
  is moot rather than merely expensive.
- **also blocks by-name** → conductors break, typed-only is dead, and the per-command description
  is the only routing mechanism there is — which revives this spec, at 10x the cost it prices.

**The candidate replacement**, if the spike allows it: typed-only commands (zero description) plus
ONE model-invocable router whose body is the registry `skills.py registry reindex` already
generates into `docs/documentation/reference/automation.md`. Cost goes O(n) → O(1); the routing
problem is not removed but relocated into one description that can be measured and tuned, instead
of 250 that cannot. Two known gaps: `lint` does not skip `sk-trigger-position`/`sk-no-boundary`
for typed-only commands although `budget` already counts them at 0, so the two instruments would
disagree; and `context-budget.md` §What the description may carry would need a second tier.

**This spec is not abandoned and not approved.** Its `## Alternatives Considered` and `## Risks`
are the material a replacement spec needs — in particular it is now the honest statement of the
"restore per-command descriptions" option, with its cost priced, for that spec's own alternatives
table.

---

The four decisions below were settled during shaping and stand on their own terms — they describe
what this spec would do **if** the spike revives it.

1. **Nine commands or eleven** → eleven. `/skill:eval` and `/skill:new` carry the same codes, and
   `restructure-claude-front-namespace` rewrites moved-path citations across *every* command
   regardless, so including them adds no coupling that excluding them avoids.
2. **How big** → 400–650 characters, not `/docs:align`'s 1,018 or the `/specs:*` 614–974. Those
   carry *how it works*, which the binding standard excludes.
3. **Write first or measure first** → write first. A trigger's hit rate cannot be measured before
   the trigger exists; `skill-evaluation.md` scopes measurement to *tuning*, and removal to a
   measured miss.
4. **`verification` policy** → `per-task`, changed from `per-section`. Each task's check is a
   sub-second local script run against one file, so there is no suite cost to amortise.
## Risks

**The load-bearing assumption, stated first.** That a model routes better from quoted trigger
phrases plus a `Not for:` boundary than from a bare `/`-menu label. It is written down as a
standard and it is unmeasured **on this front** — the only routing measurement this repo owns
(three spoken probes, 2026-07-26) tested the *bare* labels and found them working. If the
assumption is false, this spec buys nothing and costs ~4,500 always-on characters in every
session of every adopting repo, forever. Everything below is downstream of it.

| # | Failure story | Likely | Bad | How it is detected | Response |
| --- | --- | --- | --- | --- | --- |
| 1 | the ceiling is re-set from this spec's own estimate instead of the run | med | **high** | `budget` reports `total != ceiling` | mitigated — `## Validation` asserts equality |
| 2 | two descriptions quote overlapping phrases; routing ends up worse than bare labels | med | **high** | nothing mechanical | mitigated — one allocation table, reviewed whole |
| 3 | a restored description steals a phrase `functional-checks.sh` already asserts | med | med | that script — **which cannot run here** | mitigated — design constraint below |
| 4 | descriptions land, ceiling never re-set | low | med | `budget` exits 1 forever after | mitigated — `## Validation` gate |
| 5 | `skills.py` changes without a version bump; installed copies silently keep the old ceiling | med | med | nothing — `/skill:align` compares `--version`, which matched | mitigated — declared bump task |
| 6 | `restructure-claude-front-namespace` lands first; three boundary clauses cite dead paths | low | low | any citation check | **accepted** |
| 7 | the eval follow-up is never run; the characters are paid forever, unmeasured | **high** | med | never, by construction | **accepted — the biggest one** |

**Risk 1 is the one worth the most care**, because the obvious check does not catch it. `budget`
exits 0 whenever `total <= ceiling`, so a ceiling set 200 characters too high from an estimate
passes an exit-code gate while having silently disabled the ratchet — the mechanism can no longer
fire on the next command minted, which is the entire reason it exists. The assertion must be
`total == ceiling`, not `exit == 0`. This spec prints an estimate (~17,200) in two sections, which
is exactly the temptation; both label it an estimate for that reason.

**Risk 3's mitigation is a design constraint on the allocation table**, since its detector is
unavailable: no restored description may introduce a phrase competing with the five
`functional-checks.sh` already asserts —

```
  a  "park a spec for later: …"                                  -> quenching:specs:create
  b  "capture this for the backlog — …"                          -> quenching:specs:create
  c  "add a standard: we always use snake_case for …"            -> quenching:docs:add
  d  "set up something that audits our migrations and reports back" -> quenching:skill:agent:new
  e  "I want something to catch it automatically whenever a migration lands" -> quenching:skill:hook:new
```

Two are live hazards. Probe c asserts `/docs:add` against the description this spec rewrites, so
`/docs:add` must keep an "add a standard"-shaped trigger rather than narrowing to "concept doc".
Probes d and e belong to `/skill:agent:new` and `/skill:hook:new`, which are **not** in scope — so
`/skill:new`'s new triggers must not reach for "set up something…" or "catch it automatically…",
or this spec breaks two assertions in commands it never edited.

**Risk 7 is accepted, not mitigated, and it is what the approval question is really about.** The
follow-up (`/skill:eval` fixtures for the `docs` front) has no owner and no date. Approving this
spec means accepting a recurring, unmeasured always-on cost on the authority of a standard rather
than a measurement — which is the same basis on which `/specs:*` and `/skill:*` were already
restored, and `context-budget.md` is `authority: background` precisely because it has not earned
more. The honest framing: this brings the last front into line with a rule the repo chose, and the
rule is still unproven.

**Reversibility is high, and that is what makes the above acceptable.** The whole change is eleven
frontmatter string values plus one integer constant and its three transcriptions. Reverting is one
`git revert`, with no data migration, no installed state to unwind, and no adopter action beyond a
plugin upgrade.

## Handoff

**State of play.** Nothing built yet. Measured on `main` at 4.2.0, 2026-07-28.

**The numbers you need.** Eleven descriptions total **935** characters today (nine `/docs:*` = 660;
`/skill:eval` 80; `/skill:new` 195). Surface total **12,726** = `DEFAULT_CEILING` exactly, zero
headroom. Target band 400–650 per description; expected new total ~17,200 — **an estimate, and
never the number you write anywhere.** Task 2.1 produces the real one.

**Two mechanical traps, both measured, both already cost a wrong assumption:**

1. `skills.py lint` exits **0** with `severity: warn` findings present. Never gate on its exit
   code — filter `--json` by code (`## Validation` V1/V2).
2. `lint <single-file>` re-roots to that file's directory and reports `"command": "/add"`, not
   `/docs:add`. Run whole-surface lint and filter by `path`.

**Where the content comes from — do not invent it.** `/docs:align`'s existing `Not for:` clause
already names the distinguishing job of six of the nine, in the repo's own words; the other three
(`glossary-backfill`, `harness`, `import-memory`) come from the role table in `CLAUDE.md`. An
invented phrase costs always-on characters in every session forever and routes nothing.

**Conventions in force.** `context-budget.md` §What the description may carry — three things, in
order, and **nothing about how the command works**. That last rule is why `/docs:align` (1,018)
and the `/specs:*` range (614–974) are *not* the model to copy, despite being the obvious
precedent.

**Already tried, do not redo.** Shrinking instead of growing was a real spec
(`skill-description-tiering`, abandoned — superseded by the collapse, *not* refuted). Measuring
before writing is impossible: a trigger's hit rate cannot be scored before the trigger exists.
Both are argued out in `## Alternatives Considered`.

**Do not touch.** Command bodies, `sk-step-criterion`, `sk-unscoped-bash`, the rest of `README.md`,
and the zero-headroom ratchet design itself.

## Tasks

Serial throughout. No task is `[P]`: the whole point of `## Design` §One allocation table is that
the phrase set is decided across all eleven commands at once, and two executors drafting halves in
parallel is exactly the collision this spec exists to avoid. The wall-clock saved would be seconds.

### 1. Restore the routing information

- [ ] 1.1 Write all nine `/docs:*` descriptions as ONE set, in one commit — the full allocation is
      drafted across all eleven before this task's first edit, then applied
      files: plugins/quenching/commands/docs/add.md, plugins/quenching/commands/docs/define.md, plugins/quenching/commands/docs/glossary-backfill.md, plugins/quenching/commands/docs/harness.md, plugins/quenching/commands/docs/import.md, plugins/quenching/commands/docs/import-memory.md, plugins/quenching/commands/docs/learn.md, plugins/quenching/commands/docs/status.md, plugins/quenching/commands/docs/documentation/build.md
      pattern: plugins/quenching/commands/docs/align.md
      verify: ## Validation V1 + V2 + V4
- [ ] 1.2 Write the two automation-front descriptions — `/skill:eval` gains both parts,
      `/skill:new` gains trigger phrases only (it already carries a boundary)
      files: plugins/quenching/commands/skill/eval.md, plugins/quenching/commands/skill/new.md
      pattern: plugins/quenching/commands/skill/agent/new.md
      verify: ## Validation V1 + V2 + V4
- [ ] 1.3 Cross-check the allocation across all eleven: no quoted phrase serves two commands, and
      none competes with the five phrases `functional-checks.sh` already asserts (`## Risks`) —
      in particular `/docs:add` keeps an "add a standard"-shaped trigger, and `/skill:new` reaches
      for neither "set up something…" nor "catch it automatically…"
      files: plugins/quenching/commands/docs/, plugins/quenching/commands/skill/
      verify: ## Validation V1 + V2 + V4

### 2. Re-measure and re-set the ceiling — strictly after every task in 1

- [ ] 2.1 Run `skills.py --root . budget --json` and record the measured `total` in the commit
      message. It is EXPECTED to exit 1 with `sk-budget-ceiling`; that is the ratchet firing, not
      a failure, and this task is complete when the number is captured from the run
      verify: the run's `total` is quoted verbatim in the commit message
- [ ] 2.2 Set `DEFAULT_CEILING` to that measured total, with a dated changelog comment in the same
      style as the two entries above it — naming that this firing was caused by description
      growth, not by a new command
      files: plugins/quenching/assets/bin/skills.py
      verify: ## Validation V3
- [ ] 2.3 Transcribe the figure into `docs/standards/automation/context-budget.md`: §The
      per-surface ceiling, the `breakdown`
      sample, a THIRD entry in the ratchet's history, and move `timestamp` to the build date.
      Leave every historical `2,083 → 11,565 → 12,726` sentence standing
      files: docs/standards/automation/context-budget.md
      verify: ## Validation V5 + V8
- [ ] 2.4 Transcribe the figure into the three `README.md` lines that carry it, and nothing else in
      that file
      files: plugins/quenching/README.md
      verify: ## Validation V5

### 3. Release lockstep

- [ ] 3.1 Bump 4.2.0 → 4.3.0 across all six sites — a shipped script's behaviour changed, and an
      installed copy whose `--version` still matches is never upgraded by `/skill:align`
      files: plugins/quenching/VERSION, plugins/quenching/.claude-plugin/plugin.json, .claude-plugin/marketplace.json, plugins/quenching/assets/bin/skills.py, plugins/quenching/assets/bin/specs.py, plugins/quenching/assets/hooks/okf-validate.py
      pattern: git show f6c8038
      verify: ## Validation V6

### 4. Final verification

- [ ] 4.1 Run V1–V6 and V8 together and record the outputs; run V7 and record it as pass or
      **inconclusive**, never as a failure it cannot distinguish from a broken decoder
      verify: ## Validation V1–V8
