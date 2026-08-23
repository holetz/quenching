# Spec-driven facts — the single-file lifecycle, the gates, the `cq specs` tool, the report mold

**This file is the single owner
of the spec-driven facts** — the provider document's format, the gates, the
derived stages, the executor contract, the `cq specs` tool surface, and the shape every
`quenching-specs-*` command reports in — and every
`quenching-specs-*` command cites these sections instead of restating them. The OKF bridge (what
durable knowledge crosses from a spec into `knowledge/` and how) lives with the close-out command
([specs-conclude/distill.md](../../references/specs-conclude/distill.md)).

**A spec is provider-owned.** GitHub issues and Azure Boards work items are the source of truth;
the provider document carries the same thirteen sections, frontmatter records, and derived stages
throughout its lifecycle. Only *where and how* it is serialized differs, which is why every
command drives `cq specs` rather than a repository path.

What every provider owes that model — the five primitives, the obligation to reassemble the whole
canonical document on read, and refusal on unsupported selection — is owned by
`/.knowledge/standards/architecture/spec-backend.md` and never restated here.

## Contents

`cq components read <this file>` returns the heading index; `--sections` addresses one.

## The provider-owned document

<!-- rules -->

**One spec is ONE canonical provider document for its entire lifecycle.** Phases enrich it; they
never split it. Its issue or work-item body is the serialized source, and `cq specs` reconstructs
the complete document on every read. Provider state, not a repository path, carries the lifecycle
stage and outcome.

Isolation-while-building is what a **branch or worktree** provides, with real merge, history, and
reversion (what crosses into `knowledge/`: §Boundary).

The provider owns the locator and lifecycle transition. `promote` updates provider state rather
than moving anything in the target repository. What does not change is anything a command can
observe through `cq specs`.

<!-- rationale -->

**Why one provider document.** A `backlog/` ↔ `ready/` split bought exactly one fact no derivation
reproduces: *that this spec may be built*. Everything else it implied — that the spec is complete
enough to build — is computable from the sections themselves, and now is (§Derived stages). That
authorization is `approved:` in frontmatter, with `by:` naming whose it is, so the fact survived and
the folder did not.

## Identity: the slug and the provider locator

<!-- rules -->

**Every spec has a stable `<slug>` identity.** The capture date is `date:` in the frontmatter,
written **once, at creation**; provider transitions never rename the slug.

**Identity is the slug, not the locator.** Every cross-reference names the bare slug; `cq specs`
resolves it to the one provider document with that identity — and then, if nothing
matched exactly, by title and by one close match above a threshold, announcing that it approximated.
**Two matches is a refusal (exit 2) at every rung**, never a guess. This is what makes repeated
folder moves survivable.

<!-- rationale -->

**Why the date is not part of the slug.** A leading date makes a plain listing chronological,
which is useful only when every spec is a repository file. It stops being payable when the front
is provider-owned and the locator is not a filename:
moment the front could live somewhere without filenames: an external backend had to mint a
synthetic basename purely to carry a date, and the one native value that could have replaced it —
an issue's `created_at` — is when the ISSUE was made, which a migration sets to the migration's own
day. Measured on this repository: deriving it that way would have rewritten 68 of 70 capture dates
to a single afternoon. So the date is declared in the document, where every backend reads it
through the one shared derivation, and `next --front` sorts on it rather than on a listing's order.

## Frontmatter

<!-- rules -->

Write-once, low-churn fields only. Machine state a human never reads does not belong in a spec.

**Frontmatter records human judgments. The filesystem, git and section presence record everything
else.**

| Key | Required | Written by | Meaning |
| --- | --- | --- | --- |
| `slug` | always | `create` | the identity key every command and cross-reference names |
| `title` | always | `create` | one human-readable line |
| `date` | always | `create` | `YYYY-MM-DD`, the capture date — stamped once and never rewritten (why it is not the basename's prefix: §Identity) |
| `verification` | **optional** | `create` / `develop` | `per-task` · `per-section` · `end-of-plan` — when `verify:` runs. Absent means the default (`per-section`), applied on read; written after capture with `cq specs verification`, **never** by editing the frontmatter |
| `priority` | once ranked | `triage` | `{level, criticality, complexity, date}` — a human's ranking against every other spec. `complexity` alone is also written at capture, by `create` — the one field of this record a second command may write (`assets/specs/schema.json`'s `complexity.writtenBy: [triage, create, develop]`) |
| `refined` | once interrogated | `develop` | `{mode, date}` — that a real interrogation happened, and which bank ran it |
| `approved` | once approved | `develop`, or `execute` inline | `{date, by}` — **that this spec may be built, and on whose authority**: `by: human` is a person's word, `by: low-gear` the level's; absent reads as `human` |
| `branch` | once building | `execute` | `{base, work}` — after a merge, git cannot say what the base was |
| `pr` | once opened | `conclude` | `{number, url, date}` — a PR opened but not yet merged, distinct from `merge.pr`, which is stamped only once the merge already happened. Restamped if the PR is recreated |
| `reviewed` | once reviewed | `conclude` | `{date}` — that a human read the whole branch diff |
| `merge` | once merged | `conclude` | `{strategy, subject, pr}` — the strategy was a choice, the subject names the merge it produced. Known BEFORE the merge, so the stamp lands on the work branch and the merge is the last action. `rebase`/`fast-forward` create no merge commit, so the subject is an explicit none. `pr` names the pull request the PR route opened — absent on every local conclusion, and **refused** under `fast-forward` (`sp-merge-pr-no-route`), the one strategy `gh pr merge` cannot perform |
| `outcome` | at archive | `conclude` | `done` · `abandoned` — stamped by `promote --to archive` |

Read top to bottom, the optional records **narrate the spec's history**: ranked, interrogated,
approved, isolated (or explicitly not), PR opened, reviewed, merged, closed. Not "built" — `branch`
narrates whether isolation was taken, never that the work finished; "built" is the derived stage
`executing`, which a spec built in place — `branch.work` equal to `branch.base` — still reaches
exactly the same way an isolated one does. An absent record is a *not-yet*, never a defect.

`writeOnce: true` (`approved`, `branch`, `merge`, `outcome`) marks an irreversible transition, where
rewriting the value would falsify something that already happened. `writeOnce: false` (`priority`,
`refined`, `pr`, `reviewed`) marks a standing judgment its **owning command** may restamp — which is
why those four carry their own `date`. In neither case may a command other than the owner touch the
record. The declared shapes live in `assets/specs/schema.json` under `frontmatter.records`.

**There is no `created` field**: `date:` is that fact, and one truth never gets
two declared sources. Nor a `phase` field (the folder is that fact), nor a `ready` field (the ten
gate sections are that fact). `slug` is the deliberate exception — it is the identity key, so a
mirror inside the file is worth its keep, and `validate` compares it to the filename suffix. A
merely derived fact earns no such mirror.

There is no attempt counter and no `.specs.json`.

**Four more keys — `tags`, `assignee`, `start`, `target` — are STATE, never records.** Each is a
first-level frontmatter key with its own deterministic verb (`cq specs tags|assignee|start|target
<slug> [value]`), not a `{field: value}` record and not owned by one lifecycle command. `tags` is
also written at capture — `cq specs new --tags` folds a resolved `subjects.<KEY>`'s own fixed tags
in automatically, so the whole list still lands in ONE write rather than the capture's own tags
followed by a second, separate `cq specs tags` call. Where a
backend has a faithful native counterpart — issue labels/assignees on `github`,
`System.Tags`/`System.AssignedTo`/`Microsoft.VSTS.Scheduling.StartDate`/`TargetDate` on
`azure-boards` — that counterpart IS the storage: reassembled on every read, never kept in the
document too, so a human's edit on the tracker is the spec's new value on the next read.
`start`/`target` have no such counterpart on `github` and stay in the document there, exactly as
`date:` does everywhere (`knowledge/standards/architecture/spec-backend.md` §Armazenado não é
projetado has the full test).

**`summary:` is ONE line, and it is the only short thing a spec carries.** It has its own verb
(`cq specs summary <slug> [value]`) and is **not** one of the four STATE keys above: those are
projected onto a native surface and reassembled from it on read, and `summary` has no native
counterpart on any backend — it stays in the document everywhere, exactly as `title:` and `date:`
do. It is not a record either: there is no `{field: value}` shape and no `writtenBy`/`writeOnce`
rule, which is the same argument `verification` already makes for the one scalar that came before
it. `title:` names the change; `summary:` is what a listing prints when it has
one row per spec and no room to explain anything. It exists because every consumer that needed
that line used to build it by reading the spec — measured on a 45-spec front, three commands had
three different hand-written renderings of the same ranked table, and each one paid to read what
none of them stored. Written with the capture itself (`cq specs new --summary`, from `## Problem`), refreshed by every
`quenching-specs-develop` bank in the same edit, and never inferred:
a listing with no `summary:` falls back to `title:` and **says how many rows did**, so the gap is
visible rather than silently papered over.

## The thirteen sections

<!-- rules -->

The canonical set, in canonical order. **Headings are a parsed contract** — canonical English, like
frontmatter keys. A heading outside this set is a **stray** and `validate` flags it. Which language
the body prose is written in is owned by the bundle's `knowledge/standards/agents/communication.md`.

| # | Heading | Phase | Moment |
| --- | --- | --- | --- |
| 1 | `## Problem` | definition | decision |
| 2 | `## Proposal` | definition | build |
| 3 | `## Out of Scope` | definition | build |
| 4 | `## Impact` | definition | build + **parsed** |
| 5 | `## Validation` | definition | close (plus the agent's `verify:` fallback) |
| 6 | `## Design` | definition | build |
| 7 | `## Alternatives Considered` | definition | decision |
| 8 | `## Open Decisions` | definition | decision |
| 9 | `## Risks` | definition | decision |
| 10 | `## Handoff` | execution | build |
| 11 | `## Tasks` | execution | build |
| 12 | `## Discoveries` | execution | — (no moment) |
| 13 | `## Outcome` | archive | close |

**Every section declares its moment, and that is load-bearing.** `## Proposal` / `## Out of Scope`
/ `## Design` / `## Impact` / `## Handoff` / `## Tasks` are the `build` set — exactly what
`quenching-specs-execute` step 4 sends an executor (`cq specs section <slug> --moment build`).
`## Problem` / `## Alternatives Considered` / `## Open Decisions` / `## Risks` are
`decision` — the human's, weighing whether to build at all. `## Validation` / `## Outcome` are
`close` — `quenching-specs-conclude`'s. `## Discoveries` carries no moment: captured
indiscriminately while building, it is resolved later by `quenching-specs-develop`'s triage sweep, on its own
schedule.

- **`## Validation`** is the fallback for a task with no `verify:` line.
- **`## Impact`** is machine-parsed (see below). Removing the heading silently disables a check.
<!-- rationale -->

The moments replace an earlier human/agent binary that named *who* read a section without
saying *when* — `## Design` was human-only under it, yet an executor needs the decisions that stop
a task from "fixing" something deliberate, which is exactly why it is `build` now.

## The gates and the stage-scoped explicit-none rule

<!-- rules -->

A section is required — and required to carry an explicit `- none — <reason>` when it has nothing
in it — **only once its own gate is reached**. Before its gate, a heading's absence is not an
omission; it is a *not-yet*.

| Gate | Required sections |
| --- | --- |
| `new` (creation) | `## Problem` |
| `ready` (**derived**) | the nine definition sections (`## Problem` … `## Risks`) **and `## Tasks`** |
| `ready` (warning only) | `## Handoff` non-empty |
| `promote → archive/` | `## Outcome` |

**`ready` is a derived stage, not a folder, and it refuses nothing.** Filling those ten sections is
what makes a spec ready; no file moves, so there is nothing to refuse. It is a **floor** that
`quenching-specs-execute` reports against — and the tool simply has no task to hand out until the ten are
filled, which is where the old promote's teeth went. The OK to build is a separate fact,
`approved:`, asked for inline rather than encoded in a folder — or, under the `low` gear alone,
stamped by the pass itself with `by: low-gear`, the human having authorized the mode rather than
this spec.

`## Tasks` is in that set because nothing may be built with nothing to execute.

Three rules decide whether a section counts as filled:

1. **`- none — <reason>` counts as filled.** An omission and a null are different facts, and an
   explicit null is strictly more information than an absent heading. It costs one line.
2. **A present-but-empty heading is malformed and refuses.** It is neither an answer nor a
   not-yet.
3. **An absent heading before its gate is legal.** `cq specs new` stamps `## Problem` and nothing
   else — a captured spec is four lines of body, not a thirteen-heading skeleton.

The sets live in `assets/specs/schema.json` and are read by **both** `promote` and `validate` — one
source, two consumers (the ten gate sections: §Derived stages).

<!-- rationale -->

**Why the rule is scoped rather than absolute.** Applied absolutely it would kill the derived
stage: since `- none — <reason>` counts as filled, a freshly created spec carrying thirteen
`- none` sections would derive as `designed` and clear the whole ready gate without anyone having
thought anything. Stage-scoping is the version where both rules survive.

Admitting a present-but-empty heading (rule 2) would reintroduce the ambiguity this rule exists to
remove.

## Derived stages

<!-- rules -->

Sub-stages are **computed from section completeness, never declared**. Declared state is forgotten
on edit and goes stale; derived state regresses automatically when a section empties. The
computation reads **heading presence**, never a three-state body.

Resolution is **last match wins**, so a spec always reports the most advanced stage it has earned.

| Stage | Derived from |
| --- | --- |
| `captured` | only `## Problem` filled |
| `proposed` | `## Proposal` filled |
| `designed` | `## Design` filled |
| `refined` | a `refined` record in frontmatter |
| `ready` | the ten gate sections filled (`gate: true` — the single source of that set) |
| `approved` | an `approved` record in frontmatter |
| `executing` | any `[x]` or `[!]` box, or `## Handoff` filled |

`approved` sorts after `ready` because a human may say go before every section is filled — `execute`
asks inline and stamps rather than refusing. `executing` sorts last because it dominates all of
them.

`cq specs list` and `cq specs next --front` both group by these stages, deriving them from disk
on every call.

## `## Impact` — the one parsed declaration

<!-- rules -->

`## Impact` is declared scope for human review, with exactly one machine-checked part:

```markdown
### Standards this spec will write into knowledge/standards/

- `knowledge/standards/auth/session-tokens.md` — how a session token is minted and revoked
```

`parse_impact_standards()` reads the `knowledge/standards/**.md` paths bulleted under **that heading and
only that heading**, and `validate` emits `sp-impact-uncovered` (warn) for any path no `## Tasks`
item names.

Two exclusions are deliberate: the **sibling sub-headings are not parsed** (a background standard
the spec *may* resolve, and the product code it touches, name paths the spec never promised to
write), and an unfilled `<placeholder>` declares nothing. A spec with no such sub-heading declares
nothing and is never flagged — **the check is opt-in by writing the heading**.

A bullet may carry a `§`address beside its path —
`knowledge/standards/automation/skills.md §The verifier` — naming exactly which sections of that
standard the task must honor. `parse_impact_standards()` already tolerates it: the regex matches
only the `knowledge/standards/**.md` path and ignores the rest of the line, addressed or not. Without an
address, `quenching-specs-execute` step 4 reads the file whole — the address is an
assertion the spec's own author makes, never an economy the executor infers on its own.

## `## Tasks` and the `[!]` blocked marker

<!-- rules -->

Checkboxes `- [ ] <id> <text>` grouped under `### N. <Section>` headings, carrying optional
`files:` / `verify:` / `pattern:` / `subject:` / `[P]` metadata. `cq specs task --check <id>` flips a
box mechanically — **never by string surgery**.

`subject:` is written by `task --check --subject <line>` and records **the subject of the commit
that implements that task**, resolved with `git log --grep --fixed-strings`. It lives on the task
line rather than as a trailer inside the commit message, which leaves the target repo's message
format entirely its own. Because the subject is known BEFORE the commit, the box is ticked into
that commit and there is no per-task bookkeeping commit; and it cannot go stale, because amending
a recorded commit and force-pushing are both forbidden
([execution.md](../../references/specs-execute/execution.md) §The commit).
A spec built before this change carries `commit: <sha>`; both forms are read and neither is
backfilled.
`## Tasks` is the file's churn zone by design — its boxes already flip — so the low-churn doctrine
that governs frontmatter does not reach it.

A blocked task is a **visible marker, not a hidden counter**:

```markdown
- [!] 2.3 Implement the gate check — blocked: schema.json has no `ready` set yet
```

Written by the orchestrator when it decides to stop retrying; `next` skips it. **There is no
attempt limit.**

`[P]` marks a parallel-eligible group, honoured only when the group's `files:` sets are provably
disjoint (`cq specs parallel`). Serial by default.

<!-- rationale -->

The attempt counter's only value was stopping unattended retry loops, and an honest written reason
serves that better than a counter nobody sees — and it is readable by the human who has to unblock
it.

## The executor contract

<!-- rules -->

**The orchestrator is the spec's only writer.** An executor receives:

- its task line (with `files:` / `verify:` / `pattern:`),
- `## Handoff`'s global block plus the `### N.` block of its own section — never a
  section that already closed, and never the whole `## Handoff`,
- the touched subjects' `knowledge/standards/` contracts.

It does **not** receive the `decision`-moment sections (`## Problem` /
`## Alternatives Considered` / `## Open Decisions` / `## Risks`), nor the rest of the `build` set
verbatim. The orchestrator itself reads the `build` set at step 4
(`cq specs section <slug> --moment build --scope current`) — the other five sections whole, and
`## Handoff` already cut to the same global-plus-own-section slice the bullet above promises an
executor, so **neither side depends on an agent remembering to narrow it**; a `## Design` decision
that bears on the task reaches the executor distilled into the task line or `## Handoff`, never as
the section itself. It returns
a structured result — status, diff summary, `verify:` output, discoveries, handoff deltas — and
**never writes the spec**. The orchestrator applies everything via `cq specs` (`task --check`, `discover`,
`section --write`), runs `verify:` itself, and commits: **whoever commits, verifies.**

Discoveries are **captured indiscriminately**; whether one is worth acting on is a later judgment,
not the executor's. They are born in the origin spec's `## Discoveries` and resolved in place by
`quenching-specs-develop`'s discoveries bank — `promoted: <new-slug>`, `folded: <section>`, or
`dismissed: <reason>` — so provenance is never lost and the human pays the decision cost in batch.

`## Handoff` refresh is **bound to events, not judgment**: the orchestrator rewrites it on four of
them — the run pauses, a task is written blocked, a discovery is recorded, the run's last commit
lands — and on nothing else. Each names an act the executor just performed, never an assessment it
has to make, which is what lets the rule hold in an unattended run; staleness is this section's
failure mode, and `validate` warns when a spec past the ready gate has an empty `## Handoff`. What a
rewrite touches is scoped the same way what an executor reads is: `cq specs section <slug> Handoff
--write --scope global` for the evergreen block, `--scope current` for the block of the section
whose tasks are still open. A section's block is never targeted again once its last task commits —
that IS the close, no separate flag marks it — so a run that has moved on to `### 4.` never pays to
resend `### 1.` through `### 3.` again.

<!-- rationale -->

One writer with mechanical writes is also what makes one file safe under parallelism.

## The `cq specs` tool surface

<!-- rules -->

Uniform contract: `--json` on every subcommand; strict exit codes — **0** ok · **1** findings ·
**2** refusal. A command branches on the exit code and the JSON, never on prose.

`cq specs` is **stdlib-only Python**, in the same mold as `cq knowledge validate`: no runtime to install
and no dependency to declare. An external backend's transport is `subprocess` over the vendor's own
`gh` / `az`, so auth, paging and API errors are not this plugin's code — and the cost of that trade
is declared rather than hidden: such a backend does not work without the binary installed, and a
missing one is a **refusal (exit 2) naming it, never a traceback**.

| Command | Use |
| --- | --- |
| `cq specs new <slug> [--title T] [--verification P] [--subject KEY] [--type KEY] [--summary LINE] [--tags LIST] [--complexity LEVEL]` | scaffold `plans/<slug>.md` with `## Problem` as its only section by default; the capture date is stamped into `date:` here and never again. `--subject` applies a declared `subjects.<KEY>`'s parent (where the backend has one) and fixed tags — folded into `--tags` where both are given, never overwritten by it. `--summary`/`--complexity` write the scalar/record the same way `summary`/`record priority` do. Stdin, read when it is not a tty, carries N sections in the SAME multi-heading stream `section --write` reads and writes — the stream self-declares by opening on a canonical `## <Heading>`, with no single implied heading to fall back on, so an unopened or malformed stream refuses (`sp-stray-heading`/`sp-write-duplicate-heading`) before `create_spec` ever runs |
| `cq specs list [--json]` | every spec, by folder and derived stage |
| `cq specs status --spec <slug> [--json]` | sections present, derived stage, task progress with recorded subjects, the records, and the outstanding gates |
| `cq specs section <slug> "<heading>[,<heading>…]" [--write]` | deterministic partial read of N sections in ONE call, returned in the order asked; `--write` writes N in one call too, each created in canonical position — the bodies arrive on stdin delimited by the same `## <Heading>` lines the read prints, and the set the stream carries must equal the set declared here or the call refuses without writing any of them. A stream that does not open on a canonical heading is one raw body under the one heading declared, exactly as before |
| `cq specs show --spec <slug> [--task ID]… [--full]` | what `section` cannot say: the map of which headings and task ids exist (the default), ONE task's line and metadata, the whole document **only** under `--full`. Section bodies are `section`'s |
| `cq specs record <slug> <name> [--set FIELD=VALUE]…` | read or **merge** ONE frontmatter record; fields not named survive, write-once records refuse (exit 2) with the value they hold |
| `cq specs tags\|assignee\|start\|target <slug> [value]` | read one of the four STATE keys, or set it — never a record; `tags` **replaces** the whole list, it does not append |
| `cq specs summary <slug> [value]` | read or set the spec's ONE-line précis — the `Summary` column of every ranked listing. A declared scalar with its own verb, neither a record nor a projected STATE key |
| `cq specs verification <slug> [<policy>]` | read the policy in force — and whether anything declared it — or set it. The post-capture writer: `new --verification` answers at the one moment nobody has an opinion yet |
| `cq specs config [--json]` | the repo's declared parameters — the backend, the specs branch, `worktreeSetup`, `azureStates`, `azurePlacement`, `azureColumns`, `subjects`, `tagCatalog` |
| `cq specs promote <slug> --to archive [--outcome done\|abandoned] [--force]` | the one gated transition left; **exit 2** with the missing list, else `git mv` |
| `cq specs next --spec <slug> [--json]` | THE single next action, carrying the task's `verify`/`files`/`pattern`/`[P]`; skips `[!]` |
| `cq specs next --front [--json] [--table] [--columns C,C] [--order rank\|priority]` | the **ranked candidate list** — the only place ordering logic lives. `--table` prints §The spec table itself, so a command quotes a rendering instead of re-aggregating a payload; `--columns` omits columns, never reorders them; `--order priority` swaps the four-factor ranking for the human's `priority.level` alone. `--table` with `--json` refuses (exit 2) — a table IS the human rendering |
| `cq specs task --spec <slug> --check ID [--subject LINE] [--commit SHA] \| --uncheck ID \| --block ID --reason MSG` | flip, record, or block a checkbox mechanically; `--commit` is **additive** to `--subject`, never its replacement |
| `cq specs discover <slug> <text>` | append one line to `## Discoveries` |
| `cq specs parallel --spec <slug> [--json]` | verify each `[P]` group's `files:` sets are disjoint — **exit 1** when any group is ineligible |
| `cq specs validate [--spec <slug>] [--by-code]` | the canonical heading set, the stage-scoped rule, filename conformance, the `sp-*` vocabulary. `--by-code` renders the same sweep as one line per `(code, severity)` with the count and the specs — grouped, never filtered |
| `cq specs doctor` | workspace shape — the two folders, strays, older layouts; remedies **declared** for the command to apply |
| `cq specs migrate` | one-way fold to the current layout (`backlog/` + `ready/` → `plans/`, and v1 three-file folders → one file); **exit 2** when there is nothing to migrate; `specs/archive/**` never touched |
| `cq specs export --spec <slug> \| --all [--out DIR]` | dump the canonical markdown to disk — **write-only**; nothing reads it back and nothing syncs it, so it is a rescue copy for an external backend and never a second store |
| `cq specs selftest` | prove the embedded schema and template have not drifted from their asset files |

`--outcome` is the only content a promote ever writes.

**Archiving a spec with open tasks refuses.** `--outcome done` with unchecked `- [ ]` boxes exits 2
and lists them, overridable with `--force`; `--outcome abandoned` is always allowed, because
closing out a spec that will not be built is exactly the case where open tasks are expected.

There is no `init` (scaffold is an asset copy — the align's job). There is no `store` subcommand
either: the declared backend is read by `cq specs config`, never switched by a command mid-flight.

Templates live in `assets/specs/templates/spec.md` and are stamped by `cq specs new` — with the
same content embedded as a fallback constant in `cq specs` itself, so an installed copy under a
target's `.agents/hooks/` with no adjacent assets stamps an identical file. **Edit both or
neither.** A template's scaffold content must stay invisible to `has_real_content()`: only headings
and HTML comments, with any example inside a comment or written as a `<placeholder>`.

### Resolving the tool

Owned by
[align/tool-resolution.md](../../references/align/tool-resolution.md)
§Resolving the tool: define the per-call wrapper there, then invoke the bundled `cq specs`
function in the same Bash call — **one door onto one file, and no third rung**.

## Boundary: `specs/` vs the OKF `knowledge/` bundle

<!-- rules -->

**This section is the single normative owner of the boundary.** Every other statement of it cites
this section.

- `specs/plans/` — **the in-flight unit of work**: a spec's problem, design, and task checklist
  while it is being defined and built. Owned by the `quenching-specs-*` commands; leaves for `archive/` when
  it is concluded.
- `knowledge/standards/` — **how WE build** (binding contracts: naming, architecture, code);
  `knowledge/concepts/` — generic understanding. A spec writes its durable rule **directly** into
  `knowledge/standards/` (`authority`-graded) **when a task explicitly names it**, and `quenching-specs-conclude`
  routes what the work merely *revealed*
  ([distill.md](../../references/specs-conclude/distill.md)) — never by bulk
  copy.

The spec **is** the change: what it proves out lands in `knowledge/` as it is built, honestly graded
(`authority: background` for an agreed-but-unproven rule, `current` for one the spec implemented
and proved). There is no second store for it to duplicate.

## The report mold

<!-- rules -->

**Every `quenching-specs-*` command's terminal report is built from the blocks below**, and a command body
declares only its own deltas: which body blocks it emits, which columns they carry, and which
next-step candidates exist under which condition. The mold is **literal — copy a block and
substitute**, never compose a shape per command.

<!-- rationale -->

Measured across the eight bodies before this section existed: two rendered a literal block and six
described their report in prose, producing six different closing verbs, no shared glyph, an `Age`
column with no declared source, and `title` unused by every table although `cq specs` had been
emitting it all along. A shape restated in eight bodies is the fan-out
`/.knowledge/standards/quality/computed-fact-prose-fanout.md` describes — it ages in seven the
moment it changes in one, with every checker green.

### The three bands

<!-- rules -->

Three bands, in this order, always: **header · body · next step**.

- The header and the next-step block are **fixed** — always printed.
- Each body block is declared fixed or optional by the command emitting it.
- **A fixed block with nothing in it prints its title and `—`; an optional block with nothing in it
  is omitted whole.**

| Glyph | Means |
| --- | --- |
| `→` | the recommended row, or the recommended next-step line |
| `✓` | a stage that passed |
| `!` | blocked, or a section present and empty |
| `·` | a field separator |
| `—` | no value — a **not-yet**, never a defect |
| `…` | elision (`… N more`) |

`✓ ! ·` are the three `cq specs status` already prints for section state, and mean the same here.

<!-- rationale -->

The empty-fixed / omit-optional split is the rule `commands/docs/status.md` carries and its `specs/`
sibling does not. A fixed block that vanishes when empty is indistinguishable from a pass that
dropped it; an optional block printed empty is noise on every run.

### The header line

<!-- rules -->

One line, then the body. Two forms — front-wide:

```
## The specs front — 6 specs in plans/
```

One spec:

```
## session-tokens — Budget tokens per session
executing · 5/9 tasks · https://github.com/o/r/issues/41
```

**The third field is the locator the tool returned** — the `path` field `cq specs new`, `status`,
`list`, `next --front` and `section --write` all carry — never a filename the body assembled. Under
`github` returns an issue URL; `azure-boards` returns the work-item URL.

<!-- rationale -->

A body that prints a path the backend never wrote sends a human to a file that does not exist.
`quenching-specs-create` carried that rule alone, and all four single-spec commands print a locator.

### The spec table

<!-- rules -->

One ordered column set. **A command omits any column, never reorders, and never invents one.**

**The tool renders it; a command quotes what the tool printed.**
`cq specs next --front --table [--columns C,C] [--order rank|priority]` prints this table, and
`--columns` is the mechanism for the omission rule above — the order is the tool's, so a subset
cannot come back reordered. A command that composes these cells itself is a second renderer of one
ranking, which is the fan-out
`knowledge/standards/architecture/report-mold.md` forbids and which this table had three of before
the flag existed.

| Column | Source | `—` when |
| --- | --- | --- |
| `Spec` | `next --front .candidates[].slug`, `list[].slug` | never |
| `Summary` | `summary:` — the spec's own one line, falling back to `title:` where none is written, with the count of rows that fell back printed under the table | never |
| `Stage` | `.stage` — one of the nine derived stages | never |
| `Tasks` | `tasks.checked`/`tasks.total`, then `· N blocked` | `total` is 0 |
| `Priority` | `records.priority.level` and `.criticality` | the record is unset |
| `Complexity` | `records.priority.complexity` — how much a human must be in the loop | the spec was never ranked |
| `Records` | which of the seven are set | none is |
| `Age` | `next --front[].ageDays`, **or** days since `list[].date` | never |
| `State` | `sp-spec-blocked`, `sp-spec-complete`, the branch fact, `sp-spec-stale` with the age, else `—` | nothing to say |

```
| Spec | Summary | Stage | Tasks | Priority | Complexity | Age | State |
| --- | --- | --- | --- | --- | --- | --- | --- |
| → session-tokens | Sessions never expire, so a stolen token is good forever | executing | 5/9 | 1 · high | medium | 3d | on this branch |
| rate-limit-api | Rate limit the public API | ready | 0/12 | 2 · high | low | 9d | — |
| webhook-retries | A failed webhook is dropped and nobody is told | proposed | — | — | — | 21d | — |
```

**`Summary` is the old `Title` column, re-sourced.** Two columns would print the same string on
every spec whose `summary:` is unwritten, which on adoption is most of them — so there is one
column, with the fallback declared and counted rather than hidden.

Which command carries which:

| Command | Columns |
| --- | --- |
| `quenching-specs-status` | `Spec` `Summary` `Stage` `Tasks` `Records` `Age` `State` |
| `quenching-specs-triage`, the proposal | `Spec` `Summary` `Stage` `Tasks`, `Priority` and `Complexity` showing the **current** values, plus `Proposed level` `Proposed criticality` `Proposed complexity` `Reason` — the four proposal columns are the model's judgment and the only ones it composes |
| `quenching-specs-triage`, the report | `--order priority`, the four proposal columns dropped, `Priority` and `Complexity` now showing the approved values |
| `quenching-specs-align` | none — it reports findings, not front state |

**`Complexity` is its own column because it answers its own question.** `level` and `criticality`
rank a spec against the others; `complexity` says how much a human has to be in the loop while it is
built — the criterion
[specs-cycle/gears.md](../../references/specs-cycle/gears.md) §Deriving the
gears plan states. Folding it into the `Priority` cell would read as a third rank, and a reader
scanning for which specs cannot be run unattended would have to parse three axes out of one field.
The two empty together, never one without the other: `quenching-specs-triage` floors a guess at
`medium` rather than omitting it, so a `—` here means the spec was never ranked at all — never that
it is easy.

**`Age` names the call it came from.** `list --json` has no `ageDays` and `next --front` does; both
are days since the spec's `date`, and `date` is in `list`, so either derives it — but say which,
because a figure with no source is one nobody can check.

**`State` mixes two populations, and they are not interchangeable.** `sp-spec-complete`,
`sp-spec-blocked` and `sp-spec-stale` are **prose-only codes** the agent computes from `tasks` and
`Age`; `cq specs` never emits them. A code the tool does emit is quoted, never invented; a
prose-only code is never presented as tool output.

### The findings table

<!-- rules -->

One row per finding, for the split by what closes each that a read-only view owes
(`/.knowledge/standards/architecture/read-only-views.md`):

```
| Spec | Code | What it is | Closed by |
| --- | --- | --- | --- |
| rate-limit-api | `sp-empty-section` | `## Risks` present and empty | nobody — a human writes it |
| session-tokens | `sp-spec-complete` | every box ticked | `quenching-specs-conclude session-tokens` |
| — | `sp-stray-file` | `plans/notes.txt` | `quenching-specs-align` |
```

Every code is one
[specs-align/conformance.md](../../references/specs-align/conformance.md)
defines — never invented, never softened. A front-wide finding leaves `Spec` as `—`.

### The observations table

<!-- rules -->

What a sweep **noticed but does not rank** — a near-duplicate pair, an overlap of scope between two
specs, a sequencing one spec imposes on another, a finding another spec has already fixed. It
carries no `sp-` code, so it is never a row of §The findings table: every code there is one
[specs-align/conformance.md](../../references/specs-align/conformance.md)
defines, and inventing one to fill the column puts a finding the align does not fix into the align's
own vocabulary.

```
| Observation | Specs | Recommended action |
| --- | --- | --- |
| one root cause, three specs | fix-load-config-root-argument, corrigir-load-config-resolvendo-repo-pelo-cwd | `quenching-specs-conclude corrigir-load-config-resolvendo-repo-pelo-cwd` |
| overlapping scope | reduce-execute-conclude-cost, cut-conclude-run-cost | `quenching-specs-develop cut-conclude-run-cost` |
| the original defect is already fixed | isolate-functional-checks-probes | nobody — a human decides whether it still has a subject |
```

- **`Observation` is what the sweep noticed, in one phrase** — the *kind* of thing it is, taken from
  the sweep's own reading of the front, never a retelling of the other two columns. It never reads
  `—`: an observation with nothing to say is not a row.
- **`Recommended action` is runnable as printed**, exactly as §The next-step block is: the
  plugin-prefixed slash spelling
  ([align/sweep-doctrine.md](../../references/align/sweep-doctrine.md) §7)
  **with its real argument substituted**. A literal `<slug>` reaching the output is a defect, and so
  is a bare command name whose argument the reader has to reconstruct from the rest of the row.
- **An observation no command closes says what a human must decide** — `nobody — <the decision>` —
  rather than naming a command that does not fit it.
- **`Specs` carries every spec the observation spans**, comma-separated. An observation over three
  specs that names one has lost the fact that made it an observation; a front-wide one reads `—`.
- The block is **optional**: omitted whole when there are none, never printed empty.

Which of the two tables a row belongs to is decided by the code, never by the command emitting it: a
finding carrying an `sp-` code goes to §The findings table, and anything the sweep merely noticed
comes here.

### The next-step block

<!-- rules -->

Always last. Nothing is printed after it.

```
Next step
→ quenching-specs-execute session-tokens   — 5/9 tasks, 3.2 is open
  quenching-specs-develop session-tokens   — 2 open discoveries
  quenching-specs-triage                   — 4 specs carry no priority
```

- **Runnable as printed** — the real slug substituted. A literal `<slug>` reaching the output is a
  defect.
- Exactly one `→` line.
- **The `— reason` tail appears only when there is more than one line.** A single candidate needs no
  justification.
- The printed spelling is the plugin-prefixed slash. A body that then *invokes* passes the registry
  name, without the leading slash, to the `Skill` tool — two spellings of one command, and the three
  forms are owned by
  [align/sweep-doctrine.md](../../references/align/sweep-doctrine.md) §7,
  which this mold selects from rather than restates.
- **The block is a suggestion, never an offer** — with two named exceptions, both printing the
  block and *then* opening an `AskUserQuestion` rather than stopping: `quenching-specs-execute` at
  100%, and `quenching-specs-create`, whose closing screen is exactly that offer (§The one screen
  in its own body) — develop it now, with or without questions, or stop here. `quenching-specs-status`
  and `quenching-specs-align` print the block and stop — no plan, no "shall I". The form is
  identical across all four; only what follows it differs.

<!-- rationale -->

Before this block: `quenching-specs-conclude` printed no forward step at all, and `quenching-specs-execute`'s chain
into it named the command without the slug — so the two commands that end a spec's lifecycle
printed the least runnable suggestions in the surface, at the moment a human most needs one.

### Quoting a tool's own output

<!-- rules -->

**Verbatim means a fenced block, unrewritten, unsummarized, carrying the exit code.** It covers
`cq specs`, `git`, and any check a body runs.

**An inconclusive result is named as inconclusive, never counted as passed.** A check that cannot
tell *this failed* from *this could not be measured* has returned no verdict.

<!-- rationale -->

Seven wordings of *verbatim* were in circulation across create, align, status, execute, conclude and
triage with no owner, and the inconclusive rule existed only in `quenching-specs-conclude` — the one command
where acting on a false green is unrecoverable, but not the only one that runs checks.

### What is translated and what is not

<!-- rules -->

This file is English; **the report a command prints is not**. It follows the target repo's declared
tag ([/.knowledge/standards/agents/communication.md](/.knowledge/standards/agents/communication.md) §What it
governs). So each column has a **canonical name**, which is its address above, and a **printed
label**, which follows the tag.

- **Translated:** band titles, column labels, reasons, state text, `Next step`.
- **Canonical whatever the tag:** the slug · `stage` values · record names · `sp-*` codes · the
  thirteen `##` headings · command names.

The same header row in a repo declaring `pt-BR`:

```
| Spec | Título | Estágio | Tarefas | Prioridade | Idade | Estado |
```

The labels moved; nothing a grep depends on did.

<!-- rationale -->

A column label is prose, not one of the six canonical categories that standard fixes, so it
translates like the rest of the report. Leaving the labels English would be the exact failure it
names — reading the tag at session start and still reporting in English.

## The native-only claim, and why it was traded

**Nothing cites this section.** It is kept off every address a command loads, so it costs the reader
nothing and stays on disk in full.

<!-- rationale -->

This front once declared itself *entirely native — no external CLI, no Node runtime, no main spec
store, no delta format*. Three of those four still hold, and the wording above is what survives them:
stdlib-only Python is unconditional; there is still exactly ONE store, now whichever backend was
declared; and a backend that serialises natively is a mapping inside one implementation, not a delta
bridging two copies that can disagree.

The clause that was traded is **no external CLI**, and it was traded on purpose: putting an external
backend's transport on the vendor's own `gh` / `az` moves auth, paging and API errors out of this
plugin entirely. Worth knowing because the claim reads like a principle and was in fact a
measurement — the alternative was this plugin owning an HTTP client per tracker.
