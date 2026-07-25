---
name: quenching-specs-plan-abandon
description: >-
  Closes out a plan that will NOT be built — the exit quenching-specs-plan-archive cannot give,
  because archiving distils a plan's decisions into docs/standards/ as if they had been proved.
  Use when the user says "abandon this plan", "we're not doing this", "drop the plan", "cancel
  it", "this one's dead", or "close it without shipping it". Confirms the decision is the
  human's, moves the plan to specs/archive/YYYY-MM-DD-<name>/ with an ABANDONED.md marker (never
  distils a proved standard, never ticks a task), offers to REOPEN the seed task it retired into
  the Completed ledger at propose time — the one real hole in the task lifecycle — and offers a
  narrow harvest of what was learned by NOT building it (a note at authority: background, a
  knowledge doc). Its own confirmation, always: it is irreversible in the sense the cycle
  contract means. Not for: a completed plan → quenching-specs-plan-archive; revising a plan you
  still intend to build → quenching-specs-plan-update; pausing without deciding → leave it,
  quenching-specs-status reports it stale.
when_to_use: >-
  closing out a plan that will not be built, without distilling a proved rule — and reopening
  the backlog task it consumed. A finished plan is quenching-specs-plan-archive; a plan still
  alive is quenching-specs-plan-update.
allowed-tools: Bash(python3:*), Bash(py:*), Bash(mkdir:*), Bash(mv:*), Read, Glob, Grep, Write, Edit, AskUserQuestion
user-invocable: false
---

# quenching-specs-plan-abandon — close out what will not be built

The front's missing exit. `quenching-specs-plan-archive` moves a completed plan out of `specs/`
**and** offers to distil its decisions into `docs/standards/` as durable, proved rules — correct
for a plan that shipped, wrong for one that was dropped. Distilling an abandoned plan's design as a
`standard` would enshrine a rule nobody adopted. Before this skill existed, `sp-plan-stale` said
*"the human decides — revise, archive, or abandon"* and there was nothing to invoke for the third
option.

Quenching-native — this front has no CLI abandon verb; `specs.py` archives, it does not judge
intent.

The spec-driven facts (the `specs/` layout, the plan artifact graph, the `specs.py` tool surface,
the `specs/` ↔ `docs/` boundary) live in
[../quenching-specs-plan-propose/references/spec-driven.md](../quenching-specs-plan-propose/references/spec-driven.md);
the distillation doctrine this skill narrows in
[../quenching-specs-plan-archive/references/distill.md](../quenching-specs-plan-archive/references/distill.md);
the backlog zone and its check in
[../quenching-specs-backlog-add/references/backlog-zone.md](../quenching-specs-backlog-add/references/backlog-zone.md)
(also §Resolving the tool — plugin path → `.claude/hooks/specs.py` → declared manual, invoked with
`python3`/`py`); the ledger's two meanings in
[../quenching-specs-align/references/conformance.md](../quenching-specs-align/references/conformance.md)
§The ledger's two meanings. Cited, never restated.

## Doctrine

- **Abandonment is stated, never inferred.** A stale plan is not an abandoned one, and neither is
  a blocked one, an old one, or one whose author left. This skill runs on a human's word and
  nothing else — no heuristic, no age threshold, no "looks dead to me". A conductor may **never**
  invoke it: `quenching-specs-align-and-update` reports staleness (`sp-plan-stale`) and stops
  there.
- **Never distil as proved.** This front writes a plan's durable rule **straight into
  `docs/standards/`** during apply — but an abandoned plan proved nothing. Any knowledge that
  crosses to `docs/` crosses as `authority: background` at most
  ([distill.md](../quenching-specs-plan-archive/references/distill.md) narrowed by §The narrow
  harvest below): what we learned by **not** building it, never what the plan would have
  established.
- **Branch isolation resolves code and docs; the ledger does not.** When a plan was built with
  the branch or worktree `quenching-specs-plan-apply` offers, its edits to product code **and** to
  `docs/standards/` live on that branch — abandoning is simply not merging it, and the working
  tree keeps its truth. When a plan was applied **without** isolation, those edits may already sit
  on the main line; abandoning does **not** revert them — that is a separate, human decision this
  skill never makes, and it must be surfaced, never buried. The Completed ledger is the one thing
  isolation does **not** cover: `quenching-specs-plan-propose` writes its row on **main** at
  propose time, so only an explicit reopen here fixes it.
- **The archive is history, including this.** The plan moves to
  `specs/archive/YYYY-MM-DD-<name>/` like any other, and is never edited on the way — except for
  the one file this skill adds beside it, `ABANDONED.md`, recording the date and the stated
  reason. Deleting a plan outright is offered only when the human explicitly asks for deletion
  rather than archival, and never by default: an abandoned plan is the most useful record of a
  road not taken.
- **Reopen what the plan consumed.** `quenching-specs-plan-propose` retires a seed task into the
  Completed ledger at apply-ready — *developed*, not *done*. Abandoning that plan is the moment
  that claim becomes false, and this is the only skill positioned to fix it. Offer to restore the
  task and strike its ledger row, with the original gist recovered from the archived
  `proposal.md`.
- **One confirmation, its own.** Abandonment is an **irreversible cycle action** under
  [convergence.md](../quenching-align-and-update-all/references/convergence.md) §What it NEVER
  covers — it relocates a record of work rather than reshaping it. No authorization, from any
  conductor, ever absorbs it. Present what will move, what would be reopened, and the narrow
  harvest, then wait.

## Workflow

### 1. Select the plan and hear the reason
If no name was given, run `specs.py list --json` and use **AskUserQuestion** to let the user
choose — never guess, and never auto-select even when only one plan is active: abandonment is too
consequential for an inference. Then ask for the **reason** in one sentence, open-ended. The reason
is not ceremony: it is the entire content of `ABANDONED.md`, the only thing a future reader will
have, and it is what decides whether Step 5 has anything to harvest.
**Done when:** a plan name and a stated reason are in hand.

### 2. Read what abandoning would discard
Run `specs.py status --plan "<name>" --json` for the resolved artifact paths and the artifact
graph — branch on the exit code (**0**/**1**/**2**) and the JSON, never on prose. Read
`proposal.md` (for the seed task's gist and the original intent), `design.md` (for decisions that
may outlive the plan), and `tasks.md` (for how far it got). Determine whether the plan was built
under **branch isolation**: if it was applied directly on the main line, its `docs/standards/` and
product-code edits may already be committed — flag that as an open question for the plan, because
abandoning does not remove them. Then search `specs/backlog/index.md`'s Completed ledger for a row
naming this plan.
**Done when:** the discard picture, the not-isolated warning if any, and the ledger row are known.

### 3. Present ONE plan → its own confirmation
Show, in one plan:
- the move — `specs/<name>/` → `specs/archive/YYYY-MM-DD-<name>/`, plus the `ABANDONED.md` that
  will sit beside the artifacts with the date and the reason verbatim;
- the not-isolated warning, when it applies, phrased as an open question and not a proposal (the
  plan's already-committed edits to `docs/standards/` and code will **not** be reverted here);
- the backlog task that would be **reopened** (slug, gist, and the ledger row that would be
  struck) — or "no seed task in the ledger";
- the narrow harvest from Step 5, as candidates only.

Wait for the confirmation. This one is never narration, never batched, never inherited. Declined →
nothing is written, and say the plan was left exactly as it was.
**Done when:** the user has answered.

### 4. Apply — move, mark, reopen
Move the plan into the archive with `specs.py archive <name> --force` (the plan almost always has
open tasks, so `--force` is what carries it past the exit-2 refusal; the tool does the dated
`YYYY-MM-DD-<name>` naming and refuses to overwrite an existing destination — if it reports a
collision, stop and report rather than clobber history). If the tool cannot be resolved, fall back
to `mkdir -p specs/archive` and a manual `mv` to `specs/archive/YYYY-MM-DD-<name>/`, and **say the
move was manual**. Then write `ABANDONED.md` inside the archived folder: the date, the reason
verbatim, who decided if stated, the artifacts that existed, and an explicit line that **the plan
was abandoned, not proved** — no rule it wrote claims `authority: current` on its account. Touch
nothing else inside the folder.

If the reopen was approved: restore `specs/backlog/<task-slug>.md` from the task mold
(`${CLAUDE_PLUGIN_ROOT}/assets/templates/backlog/task.md`), with the gist recovered from
`proposal.md`, the original `timestamp` when the ledger row carries a date, and **no** `priority`
— the task returns **untriaged**, because whatever ranking it had was consumed by a decision that
has now been reversed. Strike its ledger row (the ledger is curated by hand; this is a
human-approved hand edit, not a regeneration). Regenerate the DERIVED zone from disk with
`specs.py backlog reindex` per
[backlog-zone.md](../quenching-specs-backlog-add/references/backlog-zone.md).
**Done when:** the folder has moved, `ABANDONED.md` exists, and the task is either restored or
recorded as not restored.

### 5. The narrow harvest (offer, then stop)
An abandoned plan usually teaches exactly one thing: **why this does not work here**. Harvest only
that, under [distill.md](../quenching-specs-plan-archive/references/distill.md) with two rules
overriding it:

- a rule or constraint the abandonment revealed → `standards/<subject>/` at
  **`authority: background`**, never `current`. Nothing was proved; something was ruled out.
- generic understanding gained → `knowledge/<subject>/`, citing the archived plan.
- a decision the plan **would** have made → **does not cross.** It was not adopted.

An empty harvest is the normal outcome — most abandonments teach nothing durable, and saying so is
the honest report. Mint approved docs under the insert procedure
([../quenching-docs-add/references/homes.md](../quenching-docs-add/references/homes.md)) and log
each in `docs/log.md` as distilled from the abandoned plan. No OKF bundle → skip silently.
**Done when:** the harvest is minted or declared empty.

### 6. Verify and report
Re-run `specs.py doctor` and `specs.py validate` (the plan left `specs/`, so both should be at
least as clean as before) and the backlog check
(`okf-validate.py specs/backlog --listing-root`) when a task was restored. Append **one**
`docs/log.md` entry per **Appending to `log.md`** in
[../quenching-docs-add/references/homes.md](../quenching-docs-add/references/homes.md):
`**Deprecation**: plan <name> — abandoned (<reason, one line>)`. Report: where it went, that its
already-committed edits (if any) were deliberately **not** reverted, whether a task came back, what
was distilled, and the not-isolated warning again if it applied — that one must not be buried.
**Done when:** the verifiers, the log entry, and all the report items are done.

## Invariants to never violate

- Never abandon a plan on inference. Only a human's explicit statement starts this skill, and no
  conductor's authorization ever covers it.
- Never revert a plan's already-committed `docs/standards/` or code edits here — report them and
  let the human decide.
- Never distil a decision as `authority: current` from an abandoned plan; `background` is the
  ceiling, and "nothing durable" is a valid harvest.
- Never edit the archived plan's artifacts — `ABANDONED.md` is the only file added, and the
  archive is never rewritten beyond it.
- Never delete a plan folder unless the human explicitly asked for deletion instead of archival;
  archival is always the default and always offered first.
- Never restore a task with its old `priority` — it returns untriaged, for
  `quenching-specs-backlog-triage` to rank against the world as it now is.
- Never rewrite the Completed ledger beyond striking the one approved row, and never hand-edit
  inside the `backlog/index.md` GENERATED markers.
- Never hand this SKILL.md `context: fork` — the reason prompt and the confirmation are both
  mid-flow.
