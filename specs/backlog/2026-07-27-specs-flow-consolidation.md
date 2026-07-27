---
slug: specs-flow-consolidation
title: "Consolidate the specs/ front around one router, and fold align-and-update into align"
verification: per-section
---

# Consolidate the specs/ front around one router, and fold align-and-update into align

<!-- ONE spec is ONE file for its whole lifecycle. Phases enrich it; they never split it.

     `specs.py new` stamps the frontmatter and `## Problem` ALONE — a captured spec is four
     lines of body, not a thirteen-heading skeleton. Every other heading below is created on
     first write by `specs.py section <slug> "<Heading>" --write`, which inserts it in the
     canonical position with the guidance comment kept here.

     THE PHASE-SCOPED EXPLICIT-NONE RULE. A heading is required — and required to carry
     `- none — <reason>` when it has nothing in it — only once ITS OWN phase gate is reached:

       new (capture)        `## Problem`
       promote -> ready/    the nine definition sections (`## Problem` .. `## Risks`)
                            AND `## Tasks`
       ready/  (warn only)  `## Handoff` non-empty
       promote -> archive/  `## Outcome`

     Before its gate, a heading's absence is NOT an omission — it is a not-yet. After its
     gate, three rules decide whether a section counts as filled:

       1. `- none — <reason>` counts as filled. An omission and a null are different facts.
       2. A heading present with an EMPTY body is malformed and refuses. It is neither an
          answer nor a not-yet.
       3. An absent heading before its gate is legal.

     Headings are a PARSED contract — canonical English, exactly as written here. Body prose
     follows the repo's language. A heading outside this set is a stray and validate flags it.

     AUDIENCE. Each section names who reads it. `## Problem`/`## Proposal`/`## Design` are for
     the human — examples and plain language belong there. `## Handoff`/`## Tasks` are for
     agents — terse, with `files:`/`verify:`/`pattern:` metadata. An orchestrator never sends
     the human sections to an executor; that is what lets one file serve both audiences
     without bloating agent context. -->

## Problem

<!-- AUDIENCE: human. Gate: new (capture).

     The problem or opportunity this spec answers, and why now. This is the only section a
     freshly captured spec carries — write it even if it is two sentences. -->

The `specs/` front has eleven commands and the operator still has to answer *"which one do I run
now?"* before every single step. That question has no cheap answer today: it depends on the plan's
folder, its filled sections, whether a discovery is open, and whether anyone has prioritized
anything. The cost is paid on every interaction, by a human, from memory.

Three specific things make it worse:

- **`backlog/` lies.** It holds both a one-line capture and a fully designed, refined spec. It is
  not an inbox; it is "not building yet". The `backlog/` ↔ `ready/` split therefore buys one real
  thing — `git mv` as the recorded human OK to build — at the cost of a second folder, a split
  listing, a `promote` that refuses often, and a name that describes neither side.
- **`/specs:align-and-update` conducts almost nothing.** Its pipeline is align → archive → triage,
  and archive needs fresh human intent per plan, so in practice it is a structural align plus a
  sweep. The 2×4 matrix in `CLAUDE.md` gives it equal billing with `/docs:align-and-update`, which
  genuinely loops (memory → harness → glossary).
- **Every align pays a full inventory before knowing whether there is work.** The three tools
  (`specs.py doctor`, `okf-validate.py`, `skills.py doctor`) already answer that question with an
  exit code, and no align consults them first. An align over a clean `specs/` should be free, and
  today it is not — which is why nobody runs it as the repo grows.

Separately, execution loses the code↔plan link. `/specs:apply` commits one task at a time under a
`plan/<name>: <id> <title>` convention, and that convention is the *only* record of which commit
implemented which task. A target repo that wants its own commit message format has to choose
between its convention and that link.

## Proposal

<!-- AUDIENCE: human. Gate: promote -> ready/.

     The change at a high level, in bullet points. What will be true afterwards that is not
     true now. -->

Reshape the front around a single entry point, and reduce the whole plugin surface from **28 to 22
commands**.

- **`specs/backlog/` + `specs/ready/` fold into `specs/plans/`.** `archive/` is untouched. `ready`
  becomes a *derived* stage (the ten gate sections filled) plus an `approved: {date}` frontmatter
  stamp written only on a human's word — the one fact the `git mv` carried that no derivation can
  reproduce.
- **The eleven `/specs:*` commands become eight**: `align`, `create`, `develop`, `execute`,
  `conclude`, `status`, `triage`, `continue`. `capture` + `from-claude` → `create`; `explore` +
  `refine` + the per-plan half of `triage` → `develop`; `apply` → `execute`; `archive` + the
  end-of-plan review + the merge → `conclude`; `align-and-update` is deleted.
- **`/specs:continue` is the router.** With or without a slug, it reads the front, ranks the
  candidates, and hands off to one of the four working commands. It is the answer to "which command
  now?", and it must be near-free.
- **`align-and-update` is folded into `align` on all four fronts.** The 2×4 matrix becomes a 1×4
  column: `/docs:align`, `/specs:align`, `/skill:align`, `/align`. A new doctrine rule makes the
  merge safe: **an align that finds nothing costs one tool call and says so** — the probe comes
  before the inventory.
- **Git bookkeeping becomes explicit and readable.** Each task line carries `commit: <sha>`, written
  mechanically by `specs.py task --check --commit`; frontmatter carries `branch: {base, work}` and
  `merge: {strategy, commit}`. Commit message format is read from `docs/standards/git/**` when the
  target declares it, with the plugin's defaults living in a reference — read if present, **never
  installed**.
- **`docs/` writing splits on declared vs emergent.** `execute` writes the doc a task explicitly
  names; `conclude` writes the doc the work revealed. Emergent findings cost one line during
  execution (`specs.py discover`) and zero authoring.

Afterwards, the frontmatter reads as the plan's history in order, and every record in it is a human
judgment that nothing else can answer.

## Out of Scope

<!-- AUDIENCE: human. Gate: promote -> ready/.

     What this spec deliberately does NOT do, and why it was ruled out.

     Empty is written `- none — <reason>`. "We drew the boundary and nothing fell outside it"
     and "nobody ever drew the boundary" are different answers, and an absent section cannot
     tell them apart. -->

- **The thirteen canonical sections are not touched.** Every heading, its order, its audience and
  its gate survive. The fold changes folders and stages, not the spec artifact.
- **`specs/archive/` is never migrated, renamed, or re-stamped.** Archived plans are history; the
  v2→v3 migration touches `backlog/` and `ready/` only.
- **No `docs/standards/git/**` files are installed into any target.** The plugin ships defaults in a
  reference and reads the target's if it has them. Installing git opinions into a target's `docs/`
  would be `/specs:*` reaching into `/docs:align`'s territory.
- **`/docs:*` and `/skill:*` command bodies are not otherwise redesigned.** They are touched only
  where the align fold and the command-count change reach them.
- **The `okf-validate.py` checker gains no new logic.** `--listing-root` is already generic; only the
  path it is pointed at changes.
- **No Node, no new dependency, no new tool.** The three stdlib scripts stay three.

## Impact

<!-- AUDIENCE: human + PARSED. Gate: promote -> ready/.

     Declared scope for human review. The `### Standards this spec will write into
     docs/standards/` sub-heading below is PARSED by `specs.py validate`: every
     `docs/standards/**.md` path bulleted under it must be named by a `## Tasks` item, or
     validate emits `sp-impact-uncovered` (warn). Keep that heading text verbatim — it is the
     anchor.

     Example of a parsed bullet:
       - `docs/standards/naming/command-surface.md` — the bijection rule for wrappers

     The sibling sub-headings are prose for the reader and are deliberately NOT parsed: they
     name paths the spec never promised to write. A spec with no such sub-heading declares
     nothing and is never flagged — the check is opt-in by writing the heading. -->

### Standards this spec will write into docs/standards/

- `docs/standards/workflows/plan-lifecycle.md` — the single-folder lifecycle: `plans/` + `archive/`,
  `ready` as a derived stage, and the rule that **frontmatter records human judgments while the
  filesystem, git and section presence record everything else**.
- `docs/standards/workflows/plan-git-record.md` — the per-task `commit:` field, the `branch` /
  `merge` frontmatter, the squash caveat, and the read-if-present contract for
  `docs/standards/git/**`.
- `docs/standards/architecture/align-surface.md` — one align per front (the 1×4 column) and the
  probe-before-inventory rule that makes a no-op align free.

### Standards at `authority: background` this spec may resolve

- none — no `authority: background` doc in this bundle covers the specs front's shape.

### Product code this spec expects to touch

- `plugins/quenching/assets/bin/specs.py` — the rails: folders, stages, `--commit`, `next --front`,
  `plans reindex`, the v2→v3 migration, and the embedded template constant.
- `plugins/quenching/assets/specs/schema.json` — the phase set, the derived stages, the frontmatter
  vocabulary.
- `plugins/quenching/commands/specs/*.md` — eleven files in, eight out.
- `plugins/quenching/commands/{align,docs/align,skill/align}.md` — the align fold.
- `plugins/quenching/assets/references/**` — re-homing and rewriting the contracts the deleted
  commands owned.
- `CLAUDE.md`, the three `QUENCHING.md` manuals, `plugins/quenching/README.md` — the surface is
  enumerated in all of them.

## Validation

<!-- AUDIENCE: human + agent. Gate: promote -> ready/.

     How anyone confirms this spec actually worked: the commands to run and the output they
     must produce, the fixtures to check, the invariants that must still hold afterwards.

     This section is LOAD-BEARING: a `## Tasks` item with no `verify:` line falls back to it.

     Empty is written `- none — <reason>`, which is a claim that the spec is unverifiable by
     construction. Make it on purpose or fill it in. -->

Run from `plugins/quenching/`:

```bash
cat VERSION && python3 assets/bin/specs.py --version \
  && python3 assets/bin/skills.py --version && python3 assets/hooks/okf-validate.py --version
python3 assets/hooks/okf-validate.py assets/docs                      # 0 error(s), 0 warning(s)
python3 assets/hooks/okf-validate.py assets/specs/plans --listing-root # 0 error(s), 0 warning(s)
python3 assets/bin/skills.py --root . doctor --json                   # 22 commands, no findings
python3 assets/bin/skills.py --root . lint --json                     # exit 0
python3 assets/bin/skills.py selftest                                 # the layout rule's fixture
./assets/bin/functional-checks.sh                                     # exit 0 = all assertions passed
```

Three invariants that the commands above do **not** cover and must be checked explicitly:

1. **The v2→v3 migration is lossless.** In a throwaway workspace with specs in both `backlog/` and
   `ready/`, `specs.py migrate` must move every file into `plans/` with its basename unchanged,
   leave `archive/` byte-identical, and exit 2 on a second run.
2. **`specs.py` round-trips the new fields.** `new` → `section --write` → `task --check --commit` →
   `status --json` must report the commit against the right task id, and `promote --to archive`
   must still refuse on open boxes without `--force`.
3. **`functional-checks.sh` is the only proof the surface loads.** No change under `commands/**` is
   testable in the session that writes it. It must be re-run after the command fold *and* after the
   align fold, because both change registry names a conductor reaches by.

## Design

<!-- AUDIENCE: human. Gate: promote -> ready/.

     The choices made and their rationale, plus the background and binding contracts this
     design must not contradict. For each decision: what was chosen, why, and what was
     weighed against it.

     Empty is written `- none — <reason>` (e.g. "mechanical change, no design surface"). -->

### The organizing principle

> **Frontmatter records human judgments. The filesystem, git, and section presence record
> everything else.**

This generalizes the existing low-churn frontmatter doctrine rather than breaking it, and it
resolves three separate questions at once — where the "OK to build" goes, how `conclude` becomes
resumable, and which git facts get stored. Each field passes the test by being something no
derivation can answer:

| Field | Written by | Why it cannot be derived |
| --- | --- | --- |
| `slug`, `title`, `verification` | `create` | declared identity and policy |
| `priority: {level, criticality, complexity, date}` | `triage` | a human's ranking |
| `refined: {mode, date}` | `develop` | that a real interrogation happened |
| `approved: {date}` | `develop`, or `execute` inline | that a human said go |
| `branch: {base, work}` | `execute` | after a merge, git cannot say what the base was |
| `reviewed: {date}` | `conclude` | that a human read the whole diff |
| `merge: {strategy, commit}` | `conclude` | the strategy was a choice; the sha is its result |
| `outcome` | `conclude` | a human's verdict |

Reading the frontmatter top to bottom narrates the plan's history in order, and each command in the
flow leaves exactly one stamp.

### Why `plans/` and not three folders

`backlog/` already holds every definition stage, so the folder split does not separate "raw" from
"ready" — the derived stages do that, and they already work (`captured`/`proposed`/`designed`/
`refined`). The one thing the `git mv` carried that no derivation reproduces is *a human said go*,
and that is exactly what `approved: {date}` persists — same shape as `refined: {mode, date}`, which
already proves the pattern. A conversational-only gate would not survive a compaction.

`execute` on an unapproved plan **does not refuse**: it asks inline, stamps, and proceeds. Refusing
would rebuild the `promote` this fold removes.

### Why `explore` disappears into `develop`

Thinking about a problem and structuring a raw plan are the same activity. A plan with only
`## Problem` filled *is* the state explore serves, and explore's output was always structure.

Folding it also deletes the `## Landing` machinery, which exists solely because exploration dies in
conversation context — with a plan file created first, there is always somewhere to land.

`develop` is therefore **one loop**, not a four-mode dispatcher: one question at a time with an
inline recommendation, accumulated and applied in a single edit. The plan's derived stage selects
the question bank:

| Stage | What `develop` asks | Absorbed from |
| --- | --- | --- |
| raw (only `## Problem`) | generative — what is this, why now, what shape, what is excluded | `explore` |
| `proposed` | adversarial — alternatives, premortem, critique | `refine` |
| `designed` | fill the gate's gaps; declare `## Impact`, `## Validation`, `verification` | `develop` |
| open `## Discoveries` | resolve — promote or dismiss | per-plan half of `triage` |
| gate met | offer the `approved` stamp | what remains of `promote` |

The accepted cost: thinking now costs a file, so explorations that go nowhere become
`outcome: abandoned` stubs. That path already exists, already allows open tasks, and already distils
at most a background note — and it is strictly better than an exploration that evaporates.

### Why the per-task commit sha is stored, and where

It goes on the **task line**, in the metadata grammar that already exists:

```markdown
- [x] 3.2 Validate the token — files: src/auth.py — verify: pytest tests/auth — commit: abc1234
```

The low-churn doctrine governs **frontmatter**; `## Tasks` has always been the churn zone, its
checkboxes already flip, and `specs.py task --check` already rewrites that line mechanically. One
optional field in a regex that already runs.

Divergence is already impossible: `execution.md` forbids amending an earlier task's commit and
forbids force-push, so a recorded sha cannot go stale.

**The squash caveat is real and must be handled honestly.** If `conclude` squashes, every per-task
sha lives only on the branch. `conclude` therefore records `merge: {strategy, commit}`, states the
strategy in `## Outcome`, and — when the strategy is squash — offers **not** to delete the branch,
which is the only way the per-task shas stay resolvable.

### Why the align fold needs the probe rule

Merging content stages into `align` is only safe if a no-op align is free; otherwise the merged
command is too expensive to run as the repo grows, which is the whole point of running it. The
three tools already answer "is there work?" with an exit code:

```
/specs:align
  └─ specs.py doctor --json && specs.py validate --json     ← one call
       exit 0 → "specs/ conformant, N plans, nothing to align."  STOP
       exit ≠0 → inventory → one plan → one OK → apply → re-verify
```

This inverts today's order, where a full read-only inventory runs before anything knows whether
there is work. The rule belongs in `align-all/sweep-doctrine.md` beside "convergence over
accommodation".

**`docs/` is the partial exception.** The cheap probe covers the structural half; draining memory is
an `ls` and the harness is one file read, but glossary-backfill is an inherently expensive bundle
sweep. It becomes **offered**, never automatic, gated on a cheap signal (doc count against glossary
size).

`align-and-update-all/convergence.md` does not die: its cycle-authorization half (one human OK for
the whole repo) still belongs to `/align`, and its fixpoint half moves inside `/docs:align`, the
only front with a real loop left. The file shrinks and re-homes to `align-all/`.

### Contracts this design must not contradict

- **Never add `context: fork`** to any of these commands — a forked context cannot present the
  mid-flow confirmations.
- **Never downgrade `/docs:import-memory` classifiers to `haiku`.**
- `commands/**` stays the only registered tree; nothing but entry points may live in it.
- The `description` cap is 1,536 characters with trigger phrases in the second sentence.
- Templates are duplicated between `assets/specs/templates/spec.md` and the constant inside
  `specs.py` — **edit both or neither**.

## Alternatives Considered

<!-- AUDIENCE: human. Gate: promote -> ready/.

     Whole-shape alternatives rejected at the spec level, each with the reason it lost.
     Per-decision alternatives can stay inside `## Design`; this section is for the ones that
     would have changed the spec's shape.

     Empty is written `- none — <reason>`. -->

- **Keep `ready/` as a third folder.** Rejected: it preserves exactly the split the fold exists to
  remove, and the one fact it carried is cheaper as a frontmatter stamp.
- **Make `ready` purely derived, with no `approved` stamp.** Rejected: the agent can satisfy every
  section itself (`- none — no risk` counts as filled), so the gate would stop being a human
  decision, and a conversational-only OK does not survive a compaction.
- **Record the task→commit map by grepping a `Plan-Task:` git trailer instead of storing the sha.**
  Rejected by the operator: it keeps `specs.py` simpler to store the sha directly, and storing it
  frees the target repo to own its commit message format entirely without the plugin needing an
  anchor inside the message.
- **Keep `explore` as a separate command.** Rejected: a raw plan is the artifact explore was always
  producing, and a plan-scoped `develop` covers it without the `## Landing` machinery.
- **Name the prioritization sweep `priorize`.** Rejected: it is not canonical English, and `triage`
  already means exactly "sort by urgency". Keeping the name avoids a rename across three
  `QUENCHING.md` manuals and every citation.
- **Split this into two specs — the specs front, and the align fold.** Rejected for now, because
  `/specs:align-and-update` dies in both and the seam would be a cross-spec dependency. Section 4 of
  `## Tasks` is kept separable in case this is revisited (see `## Open Decisions`).
- **Write all `docs/` at `conclude`.** Rejected: tasks whose whole point is writing a named standard
  would become unexecutable. The line is declared (task names the path → `execute`) vs emergent
  (work revealed it → `conclude`).

## Open Decisions

<!-- AUDIENCE: human. Gate: promote -> ready/.

     What is deliberately still undecided, and how each will be decided — the evidence or the
     moment that settles it, not "TBD". -->

- **Does `/align` still need to loop across fronts?** With one align per front, the cross-front
  command may be a single ordered pass (docs → specs → skill). Settled when section 4's first task
  rewrites `commands/align.md` and the fixpoint either has something to converge on or does not.
- **How much of `convergence.md` survives.** Decided while writing section 4: whatever `/align` and
  `/docs:align` actually cite stays; the rest is deleted rather than re-homed.
- **Whether this repo declares its own `docs/standards/git/**`.** It would dogfood the read-if-present
  path, but it is not required by any task here. Decided after section 2 lands, when the default
  reference exists and the cost of a repo-local override is visible.
- **Whether section 4 (the align fold) is peeled into its own spec.** Decided at the section 3/4
  boundary: if section 3 lands and the diff is already large, peel it — the `## Tasks` grouping is
  built to allow that.
- **Whether `triage`'s output is enough for `continue` to recommend, or only to list.** Settled by
  the first real run of `continue` against a `plans/` folder with mixed staleness.

## Risks

<!-- AUDIENCE: human. Gate: promote -> ready/.

     What could go wrong, and the mitigation for each. A risk taken knowingly is written
     `ACCEPTED — <why>`; a silent failure mode is the shape to hunt for. -->

- **The surface is unreachable and every check still passes.** The command registry is built at
  session start, so no change under `commands/**` is testable in the session that writes it — a run
  can be entirely green while every body is unreachable. *Mitigation:* `functional-checks.sh` after
  section 3 and again after section 4; it is the only check that spawns a fresh `claude -p` and
  asserts on captured tool calls.
- **The template drifts from its embedded copy in `specs.py`.** A silent failure: an installed copy
  under a target's `.claude/hooks/` stamps a different file than the plugin does. *Mitigation:* a
  task that touches one must touch both, and a `verify:` that diffs them.
- **`migrate` eats or renames archived plans.** *Mitigation:* `archive/**` is never touched, asserted
  by a byte-identical check in the throwaway-workspace validation, and `migrate` exits 2 on an
  already-v3 target.
- **A squash merge orphans every per-task sha.** *Mitigation:* `conclude` records the merge strategy,
  says so in `## Outcome`, and offers to keep the branch when squashing. `ACCEPTED` beyond that —
  the operator chose readability in the plan over a message-embedded anchor.
- **`develop` triggers worse than the three commands it replaces.** One description under 1,536
  characters must now route generative, adversarial, and gap-filling asks. *Mitigation:* measure it
  with `/skill:eval` on should-trigger / should-not-trigger rates, not on taste.
- **`develop`'s body blows the length budget.** 125 + 243 + 141 lines merged against a "well under
  500" guideline. *Mitigation:* the body is a dispatcher; each stage's question bank lives in
  `assets/references/specs-develop/`.
- **The plugin's own `specs/` workspace is mid-migration while the tooling that migrates it is being
  rewritten.** *Mitigation:* section 1 lands and is verified in a throwaway workspace before this
  repo's own `specs/` is folded.
- **`plans/` accumulates dead exploratory stubs**, making `continue`'s ranking noisy. *Mitigation:*
  `triage` stops being optional hygiene and becomes the input `continue` consumes; a stub that goes
  nowhere is archived `abandoned`.

## Tasks

<!-- AUDIENCE: agent. Gate: promote -> ready/.

     Checkboxes `- [ ] <id> <text>` grouped under `### N. <Section>` headings.
     `specs.py task --spec <slug> --check <id>` flips one mechanically — NEVER hand-edit the
     `[ ]` / `[x]` character.

     A checkbox MAY carry indented metadata lines directly beneath it:

       - [ ] 3.2 Add rate limiting to the auth middleware
             files: src/middleware/auth.ts, src/config/limits.ts (new)
             pattern: src/middleware/cors.ts
             verify: pnpm test middleware/

     files:    the paths this task may touch. Declaring them is what PERMITS the task to be
               handed to an executor sub-agent, and what makes a `[P]` marker checkable.
     pattern:  an existing file to imitate — the cheapest context an executor can be given.
     verify:   the command that proves the task done. WHEN it runs is the `verification`
               frontmatter policy, not this section's business. With no `verify:` line the
               task falls back to `## Validation`.

     `[P]` right after the id marks a task parallel-eligible:

       - [ ] 3.3 [P] Add the rate-limit config loader

     Set HERE, at definition time, and NEVER inferred while building. Honoured only when the
     marked tasks' `files:` sets are provably disjoint and none writes into `docs/` —
     `specs.py parallel` checks the disjunction mechanically rather than judging it in prose.
     Serial execution is the default and needs no marker.

     A BLOCKED task is a visible marker, not a hidden counter:

       - [!] 2.3 Implement the gate check — blocked: schema.json has no `ready` set yet

     Written by the orchestrator when it decides to stop retrying; `next` skips it. There is
     no attempt budget — an honest written reason serves better than a counter nobody sees. -->

### 1. The rails — schema, folders, migration

- [ ] 1.1 Fold the phase set in `schema.json`: `plans` + `archive`, `ready` as a derived stage over
      the ten gate sections, `approved` in the frontmatter vocabulary
      files: plugins/quenching/assets/specs/schema.json
      verify: python3 -c "import json;d=json.load(open('plugins/quenching/assets/specs/schema.json'));assert [p['id'] for p in d['phases']]==['plans','archive']"
- [ ] 1.2 Add the new frontmatter records to `schema.json`: `priority`, `approved`, `branch`,
      `reviewed`, `merge` — each optional, each write-once
      files: plugins/quenching/assets/specs/schema.json
      verify: python3 plugins/quenching/assets/bin/specs.py validate --json
- [ ] 1.3 Teach `specs.py` the `plans/` folder end to end — `new`, `list`, `status`, `section`,
      `promote` (plans→archive only), `next`, `task`, `discover`, `parallel`, `validate`, `doctor`
      files: plugins/quenching/assets/bin/specs.py
      verify: cd /tmp && rm -rf sq && mkdir -p sq/specs && cd sq && python3 $OLDPWD/plugins/quenching/assets/bin/specs.py new demo --title T && python3 $OLDPWD/plugins/quenching/assets/bin/specs.py list --json
- [ ] 1.4 Rename `backlog reindex` to `plans reindex` and move the seed listing to
      `assets/specs/plans/index.md`; drop `assets/specs/ready/.gitkeep`
      files: plugins/quenching/assets/bin/specs.py, plugins/quenching/assets/specs/plans/index.md, plugins/quenching/assets/specs/backlog/index.md, plugins/quenching/assets/specs/ready/.gitkeep
      verify: python3 plugins/quenching/assets/hooks/okf-validate.py plugins/quenching/assets/specs/plans --listing-root
- [ ] 1.5 Rewrite `specs.py migrate` as the v2→v3 fold: `backlog/` + `ready/` → `plans/`, basenames
      unchanged, `archive/**` untouched, exit 2 on an already-v3 target
      files: plugins/quenching/assets/bin/specs.py
      verify: bash -c 'set -e; d=$(mktemp -d); mkdir -p $d/specs/backlog $d/specs/ready $d/specs/archive; touch $d/specs/backlog/2026-01-01-a.md $d/specs/ready/2026-01-02-b.md; python3 plugins/quenching/assets/bin/specs.py --root $d/specs migrate; test -f $d/specs/plans/2026-01-01-a.md && test -f $d/specs/plans/2026-01-02-b.md; ! python3 plugins/quenching/assets/bin/specs.py --root $d/specs migrate'

### 2. The rails — new surface for the router and the git record

- [ ] 2.1 Add `task --check <id> --commit <sha>`: write `commit:` into the task's metadata grammar
      mechanically, never by string surgery
      files: plugins/quenching/assets/bin/specs.py
      verify: python3 plugins/quenching/assets/bin/specs.py task --help
- [ ] 2.2 Surface commits, `approved`, `reviewed` and `priority` in `status --json`, so `conclude`
      and `continue` never re-parse the file
      files: plugins/quenching/assets/bin/specs.py
      verify: python3 plugins/quenching/assets/bin/specs.py status --spec specs-flow-consolidation --json
- [ ] 2.3 Add `next --front`: the ranked candidate list with a reason per candidate (executing,
      closest to done, priority, age) — **the only place ranking logic lives**
      files: plugins/quenching/assets/bin/specs.py
      verify: python3 plugins/quenching/assets/bin/specs.py next --front --json
- [ ] 2.4 Update `assets/specs/templates/spec.md` and the embedded template constant in `specs.py`
      **in lockstep**, and add a check that they cannot drift
      files: plugins/quenching/assets/specs/templates/spec.md, plugins/quenching/assets/bin/specs.py
      verify: python3 -c "import re,pathlib;s=pathlib.Path('plugins/quenching/assets/bin/specs.py').read_text();t=pathlib.Path('plugins/quenching/assets/specs/templates/spec.md').read_text();assert t.strip() in s, 'template drift'"
- [ ] 2.5 Bump `VERSION`, `plugin.json`, `marketplace.json` and the `VERSION` constant in all three
      scripts together
      files: plugins/quenching/VERSION, plugins/quenching/.claude-plugin/plugin.json, .claude-plugin/marketplace.json, plugins/quenching/assets/bin/specs.py, plugins/quenching/assets/bin/skills.py, plugins/quenching/assets/hooks/okf-validate.py
      verify: bash -c 'cd plugins/quenching; v=$(cat VERSION); for s in assets/bin/specs.py assets/bin/skills.py assets/hooks/okf-validate.py; do test "$(python3 $s --version)" = "$v" || test "$(python3 $s --version)" = "specs.py $v" || python3 $s --version | grep -q "$v"; done'

### 3. The specs front — eleven commands become eight

- [ ] 3.1 Write `commands/specs/create.md` — `capture` + `from-claude`, with the effort rule:
      effort proportional to input, **never interrogates**
      files: plugins/quenching/commands/specs/create.md, plugins/quenching/commands/specs/capture.md, plugins/quenching/commands/specs/from-claude.md
      pattern: plugins/quenching/commands/specs/capture.md
- [ ] 3.2 Write `commands/specs/develop.md` as a one-loop dispatcher, with the stage-selected
      question banks moved into `assets/references/specs-develop/`
      files: plugins/quenching/commands/specs/develop.md, plugins/quenching/commands/specs/explore.md, plugins/quenching/commands/specs/refine.md, plugins/quenching/assets/references/specs-develop/, plugins/quenching/assets/references/specs-refine/techniques.md
      verify: python3 plugins/quenching/assets/bin/skills.py --root plugins/quenching lint plugins/quenching/commands/specs/develop.md --json
- [ ] 3.3 Write `commands/specs/execute.md` from `apply.md`: no end-of-plan review, no merge, writes
      only the `docs/` a task explicitly names, records `branch` and per-task `commit:`
      files: plugins/quenching/commands/specs/execute.md, plugins/quenching/commands/specs/apply.md, plugins/quenching/assets/references/specs-apply/execution.md
      pattern: plugins/quenching/commands/specs/apply.md
- [ ] 3.4 Write `commands/specs/conclude.md`: branch review → emergent `docs/` → merge (strategy
      offered, squash keeps the branch) → archive + distil; resumable from `reviewed`/`merge`/git
      files: plugins/quenching/commands/specs/conclude.md, plugins/quenching/commands/specs/archive.md, plugins/quenching/assets/references/specs-archive/distill.md
- [ ] 3.5 Write the git contract reference: the plugin's default commit/branch/merge conventions and
      the read-if-present rule for `docs/standards/git/**` — kebab-case, never installed
      files: plugins/quenching/assets/references/specs-execute/git.md
- [ ] 3.6 Write `commands/specs/continue.md` — the router: `next --front`, offer the ordering, hand
      off to one of the four; suggests `triage` when the ranking has nothing to stand on
      files: plugins/quenching/commands/specs/continue.md
- [ ] 3.7 Reduce `commands/specs/triage.md` to the prioritization sweep and have it write
      `priority: {level, criticality, complexity, date}`
      files: plugins/quenching/commands/specs/triage.md
- [ ] 3.8 Rewrite `commands/specs/align.md` around the probe-first rule, and delete
      `commands/specs/align-and-update.md` with its `cycle.md`
      files: plugins/quenching/commands/specs/align.md, plugins/quenching/commands/specs/align-and-update.md, plugins/quenching/assets/references/specs-align-and-update/cycle.md, plugins/quenching/assets/references/specs-align/conformance.md
- [ ] 3.9 Update `commands/specs/status.md` for `plans/`, the new records, and the near-free contract
      files: plugins/quenching/commands/specs/status.md
- [ ] 3.10 Update every `specs/`-front citation path and the shared facts file for the fold
      files: plugins/quenching/assets/references/specs-develop/spec-driven.md, plugins/quenching/assets/references/specs-capture/backlog-zone.md
      verify: bash -c '! grep -rn "specs/backlog\|specs/ready\|/specs:capture\|/specs:apply\|/specs:refine\|/specs:explore\|/specs:from-claude\|/specs:archive" plugins/quenching/commands plugins/quenching/assets/references'
- [ ] 3.11 Prove the new surface actually loads
      verify: cd plugins/quenching && ./assets/bin/functional-checks.sh

### 4. The align fold — one align per front

- [ ] 4.1 Add the probe-before-inventory rule to the shared sweep doctrine
      files: plugins/quenching/assets/references/align-all/sweep-doctrine.md
- [ ] 4.2 Fold `/docs:align-and-update` into `commands/docs/align.md`: probe first, memory and
      harness as conditional stages, glossary-backfill **offered** not automatic
      files: plugins/quenching/commands/docs/align.md, plugins/quenching/commands/docs/align-and-update.md, plugins/quenching/assets/references/docs-align-and-update/
- [ ] 4.3 Fold `/skill:align-and-update` into `commands/skill/align.md` — the doctrine audit becomes
      a read-only stage of the align
      files: plugins/quenching/commands/skill/align.md, plugins/quenching/commands/skill/align-and-update.md
- [ ] 4.4 Rewrite `commands/align.md` as the one cross-front command and delete
      `commands/align-and-update.md`; re-home what survives of `convergence.md` into `align-all/`
      files: plugins/quenching/commands/align.md, plugins/quenching/commands/align-and-update.md, plugins/quenching/assets/references/align-and-update-all/convergence.md, plugins/quenching/assets/references/align-all/
- [ ] 4.5 Prove the surface is 22 commands, clean, and still loads
      verify: cd plugins/quenching && python3 assets/bin/skills.py --root . doctor --json && python3 assets/bin/skills.py --root . lint --json && python3 assets/bin/skills.py selftest && ./assets/bin/functional-checks.sh

### 5. Documentation and the operator manuals

- [ ] 5.1 Write `docs/standards/workflows/plan-lifecycle.md` — the single-folder lifecycle, the
      derived `ready`, and the frontmatter-records-human-judgments rule
      files: docs/standards/workflows/plan-lifecycle.md, docs/standards/workflows/index.md
      pattern: docs/standards/workflows/plan-artifacts.md
- [ ] 5.2 Write `docs/standards/workflows/plan-git-record.md` — the per-task `commit:`, the
      `branch`/`merge` records, the squash caveat, the read-if-present `docs/standards/git/**`
      files: docs/standards/workflows/plan-git-record.md, docs/standards/workflows/index.md
- [ ] 5.3 Write `docs/standards/architecture/align-surface.md` — the 1×4 column and
      probe-before-inventory
      files: docs/standards/architecture/align-surface.md, docs/standards/architecture/index.md
      pattern: docs/standards/architecture/plugin-layout.md
- [ ] 5.4 Update the three `QUENCHING.md` operator manuals — all three enumerate the command surface
      files: plugins/quenching/assets/docs/QUENCHING.md, plugins/quenching/assets/specs/QUENCHING.md, plugins/quenching/assets/claude/QUENCHING.md
- [ ] 5.5 Rewrite the surface tables in `CLAUDE.md` and `plugins/quenching/README.md`: 28 → 22, the
      2×4 matrix → the 1×4 column, the eight `/specs:*` commands
      files: CLAUDE.md, plugins/quenching/README.md
- [ ] 5.6 Migrate this repo's own `specs/` workspace and log the change
      files: specs/, docs/log.md
      verify: cd plugins/quenching && python3 assets/hooks/okf-validate.py ../../docs && python3 assets/bin/specs.py --root ../../specs validate --json
