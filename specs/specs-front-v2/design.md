# Design — Specs front v2 — single-file lifecycle specs

## Context

Shape settled in an explore session (2026-07-25) that stress-tested the single-file premise
against the current model's documented seams. Binding constraints carried over unchanged:
stdlib-only tooling with the uniform contract (`--json` everywhere, exit 0 ok / 1 findings /
2 refusal); one plan → one OK, with code-coupled items gating individually; the
`specs/`↔`docs/` boundary (rules written straight into `docs/standards/` during apply,
distillation at archive); canonical-English parsed surfaces (section headings, frontmatter
keys, slugs) with body prose in the repo's language; never delete on a guess.

## Decisions

1. **One file, and only human-readable state lives in it.** Frontmatter carries write-once,
   low-churn fields only: `slug`, `title`, `verification`, a `refined` record, `outcome`
   (stamped at archive). There is no `created` field: the filename's date prefix (decision 3)
   IS that fact, and decision 2's rule against two declared sources of one truth binds here
   too. `slug` stays — it is the identity key every command and cross-reference names, so a
   checked mirror inside the file is worth its keep (`validate` compares it to the filename);
   a merely derived fact earns no such mirror. Machine state that a human never reads does not
   belong in the spec — which is why decision 6 kills the attempt counter instead of
   relocating it.
2. **Folder = macro-phase, and it is the single truth.** Three folders — `backlog/`
   (definition), `ready/` (execution), `archive/` — and NO phase field in frontmatter. Two
   declared sources of the same fact will diverge; the folder cannot lie. `git mv` is the
   transition, so `git log` narrates the lifecycle.
3. **Identity is the slug, not the path — and the file is `YYYY-MM-DD-<slug>.md` in every
   folder.** Every cross-reference names the bare slug; `specs.py` resolves it to the one file
   whose name ends in `-<slug>.md`, wherever it sits (two matches is a refusal, never a guess).
   This is what makes N folder moves survivable where v1 only ever moved a plan once. The date
   prefix records when the spec was BORN and is written once, at capture: promote moves the
   file, never renames it, so the basename is stable for the whole lifecycle and `git log
   --follow` reads as one history. The prefix earns its place in all three folders, not just
   `archive/` — birth order is the order a human wants in every phase (how long has this sat in
   `backlog/`? how long has this build been open in `ready/`?), and a plain `ls` is the status
   view this whole design is built on, which cannot sort by a frontmatter field.
4. **Sub-stages are derived, never declared.** Within `backlog/`: captured (only `## Problem`
   filled) → proposed (`## Proposal`) → designed (`## Design`) → refined (`refined` record in
   frontmatter). Within `ready/`: executing (any `[x]`/`[!]` box, or `## Handoff` filled).
   `specs.py` computes the stage from section completeness; the generated index groups by it.
   Derived state regresses automatically when a section empties — declared state would lie.
   An **absent** heading means its phase was never reached (decision 13), which is what keeps the
   computation unambiguous: the function reads heading presence, never a three-state body.
5. **`promote` is a gated command, not a raw `mv`.** It validates the destination folder's
   gates — the **section set of the destination phase** (decision 13), each one filled, with
   `- none — <reason>` counting as filled — refuses with exit 2 and the missing list, otherwise
   moves. A heading that exists but is empty is malformed and refuses too: it is neither an
   answer nor a not-yet, and admitting it would reintroduce the ambiguity decision 13 removes.
   Promote to `ready/` IS the human OK — the
   one-plan-one-OK doctrine becomes one auditable file move. Promote to `archive/` replaces
   `archive` and stamps `outcome: done | abandoned` — the only content it ever writes, since
   the filename is fixed at capture (decision 3) and a promote is otherwise a pure `git mv`.
6. **A blocked task is a visible marker, not a hidden counter.** `- [!] <id> <title> —
   blocked: <reason>` in `## Tasks`, written by the orchestrator when it decides to stop
   retrying. `next` skips `[!]`. The five-attempt budget in `.specs.json` is dropped: its only
   value was stopping unattended retry loops, and the orchestrator writing an honest reason
   serves that better than a counter nobody sees.
7. **Discoveries are born in the origin spec and promoted by triage.** During execution the
   orchestrator appends one-liners to the origin's `## Discoveries` (`specs.py discover`) —
   zero human interruption at capture time. The triage sweep reads every active spec's
   `## Discoveries` plus `backlog/`, and resolves each entry to `→ promoted: <new-slug>` or
   `→ dismissed: <reason>`, in place. Provenance is never lost; the human pays the decision
   cost in batch, at a moment of their choosing.
8. **Every section declares its audience.** `## Problem` / `## Proposal` / `## Design` are for
   the human and the planning stages — examples and plain language live there. `## Handoff` /
   `## Tasks` are for agents — terse, with `files:`/`verify:`/`pattern:` metadata.
   `## Outcome` is for the archive reader. An orchestrator never sends the human sections to
   an executor; this is what lets one file serve both audiences without bloating agent context.
9. **The executor contract — the orchestrator is the spec's only writer.** An executor
   receives: its task line (with `files:`/`verify:`/`pattern:`), the whole `## Handoff`
   (small by construction), and the touched subjects' `docs/standards/` contracts. It does NOT
   receive `## Problem`/`## Proposal`/`## Design`. It returns a structured result — status,
   diff summary, verify output, discoveries (captured indiscriminately; worth is triage's
   judgment, not the executor's), handoff deltas. It never writes the spec. The orchestrator
   applies everything via `specs.py` (`task --check`, `discover`, `section --write`), runs
   `verify:` itself, and commits — **whoever commits, verifies**. This is also what makes the
   single file safe under parallelism: one writer, mechanical writes.
10. **Parallelism is inherited unchanged.** `[P]` set at propose time, honoured only when the
    group's `files:` sets are provably disjoint (`specs.py parallel`), serial by default.
11. **`## Handoff` refresh is bound to events, not judgment.** The orchestrator rewrites it
    after each committed task and at every promote; `validate` warns when a `ready/` spec has
    an empty `## Handoff`. Staleness is the section's failure mode, and an event-bound rule is
    the only cure that survives unattended runs.
12. **Big-bang release with a one-way mechanical migration.** `specs.py migrate` folds a v1
    plan folder (proposal + design + tasks + `.specs.json`) into one file and converts a
    backlog task file into a captured-stage spec; `quenching-specs-align` v2 drives it. The
    existing `specs/archive/` is not migrated. No format coexistence, ever.
13. **Thirteen sections, and the explicit-none rule is phase-scoped.** The single file carries the
    full v1 section set — `## Problem`, `## Proposal`, `## Out of Scope`, `## Impact`,
    `## Validation`, `## Design`, `## Alternatives Considered`, `## Open Decisions`, `## Risks`,
    `## Handoff`, `## Tasks`, `## Discoveries`, `## Outcome`. Collapsing to seven read as leanness
    but was a silent contract break in two places: a task with no `verify:` falls back to the
    proposal's `## Validation`, so the fallback would have pointed at a section that no longer
    exists; and `## Impact` is the one machine-parsed declaration
    (`parse_impact_standards()` → `sp-impact-uncovered`), so dropping the heading disables a
    validator check without a line of code changing. The other four are thinking a plan should not
    be free to skip in silence.

    The cost of thirteen sections is paid by **scoping** the explicit-none rule instead of applying
    it absolutely. A heading is required — and required to carry `- none — <reason>` when empty —
    only once **its own phase gate** is reached:

    | Gate | Required sections |
    | --- | --- |
    | `new` (capture) | `## Problem` |
    | `promote → ready/` | the nine definition sections, `## Problem` … `## Risks` |
    | `ready/` (warning only) | `## Handoff` non-empty (decision 11) |
    | `promote → archive/` | `## Outcome` |

    This is what keeps *an omission and a null are different facts* true without making a captured
    spec a thirteen-heading skeleton: before its gate, a heading's absence is not an omission, it
    is a not-yet. `specs.py new` stamps `## Problem` and nothing else; `section --write` creates a
    heading on first write; `promote` is where the boundary must be drawn or explicitly declared
    empty. The per-phase sets live in `schema.json` and are read by both `promote` and `validate`
    (one source, two consumers).
14. **The four current standards are rewritten in place, not superseded.**
    `docs/standards/workflows/plan-artifacts.md` keeps its path and gets a new `title:`, the
    thirteen-section contract, and one short section on reading a v1 plan in `specs/archive/`;
    `workflows/task-execution.md` is edited surgically; `naming/command-surface.md` and
    `automation/skills.md` have their enumerations re-derived. The precedent is this repo's own:
    `naming/command-surface.md` supersedes the openspec-era `command-naming` spec by rewriting one
    file and saying so in the body, not by keeping two. A second doc on one subject makes every
    later reader decide which one binds, and the citations are all listings (glossary, two
    `index.md` GENERATED zones, `log.md`) — cheap to re-point, expensive to fork.

## Alternatives Considered

- **Sidecar `.json` for machine state** — rejected: "one file" stops being true, every folder
  move carries two files, and v1's `.specs.json` is exactly the pattern being retired.
- **A declared `stage:`/`phase:` frontmatter field** — rejected: declared state lies (it is
  forgotten on edit), duplicates either the folder or the sections, and derived state is
  strictly more honest at the cost of one deterministic function in `specs.py`.
- **Format coexistence (v1 and v2 both supported by skills and tool)** — rejected: doubles
  every skill's complexity, which is the opposite of the plan's purpose. One-way migration has
  precedent (openspec → specs) and the blast radius is one repo today.
- **Date prefix only in `archive/`, bare `<slug>.md` while active** — rejected: it grants the
  chronological listing to the one folder where order matters least (archived work is finished)
  and withholds it from `backlog/`, where "how long has this sat?" is the triage question. It
  also makes archiving a move *and* a rename — two naming rules, and a broken rename trail at
  the last hop — to save eleven characters.
- **No prefix anywhere; sort by a `created:` frontmatter field** — rejected: the premise of this
  design is that a plain file listing IS the status view, and no file listing reads frontmatter.
  It would take the tool to answer a question `ls` should answer on its own.
- **One folder per sub-stage (captured/, proposed/, designed/, …)** — rejected: every extra
  column is another path move and more link churn; kanban works with few columns. The human
  gets the fine view from the generated index, the coarse view from three folders.
- **Keeping the five-attempt budget** — rejected: hidden state in a dying file, valuable only
  in unattended loops, and a visible `[!] — blocked: <reason>` serves that case better while
  being readable by the human who has to unblock it.
- **A seven-section set (drop the six v1 sections outright)** — rejected, and it was the shape this
  design started from. It breaks the `verify:` fallback chain (no `## Validation` to fall back to)
  and silently disables `sp-impact-uncovered` (no `## Impact` to parse). Leanness that costs two
  working mechanisms is not leanness.
- **Readmitting only `## Out of Scope` and `## Validation` as top-level sections (nine total)** —
  rejected: it fixes the `verify:` fallback but leaves `## Impact` dead, so the one machine-checked
  declaration in the whole contract disappears while the plan claims to keep the rails. The four
  remaining sections are also not decoration — `## Risks` and `## Open Decisions` are where a plan
  admits what it does not know.
- **Folding `## Out of Scope` and `## Validation` in as parsed sub-headings under `## Proposal` and
  `## Tasks`** — rejected: it preserves a section *count* nobody measures at the price of a second
  addressing mode in `specs.py section` (`section <slug> "Proposal/Out of Scope"`), a `promote`
  gate that must descend into a section, and a derived-stage function that would have to read
  sub-headings it currently ignores. Three mechanisms complicated to keep one number at seven.
- **All thirteen headings stamped at capture, with the explicit-none rule applied absolutely** —
  rejected because it kills the derived stage. Decision 5 makes `- none — <reason>` count as
  filled, so a freshly captured spec with thirteen `- none` sections would derive as `designed` and
  pass every `promote` gate without anyone having thought anything. Phase-scoping (decision 13) is
  the version where both rules survive.
- **Superseding `plan-artifacts.md` with a new `workflows/spec-lifecycle.md`, old doc dropped to
  `authority: background`** — rejected. Its real merit is that `specs/archive/**` keeps its v1
  three-file plans and a reader of those has the full v1 contract to hand; that is bought instead
  with one ~6-line section inside the rewritten file. What it costs is a permanent fork: two docs
  on one subject, four glossary entries to re-point instead of two, and every future reader
  deciding which binds — against a repo precedent (decision 14) that already chose in-place.

## Open Decisions

- **`ready/` vs `active/` as the execution folder's name** — the user's word is `ready`;
  it reads oddly once a plan is mid-execution inside it. Decided at the dogfood migration
  (task 3.3): if the listing reads wrong with a half-built plan in `ready/`, rename before
  release — a one-line constant at that point.
- **The exact v2 skill surface** — how many of the thirteen survive as distinct skills, and
  the final command tree. Decided by task 4.1's mapping doc, reviewed at its checkbox before
  any skill is rewritten.
- **Whether `## Discoveries` entries need a minimal shape** (one line + origin context vs
  free text) — decided while implementing `specs.py discover` (task 2.4): whatever shape the
  triage sweep can parse deterministically wins, and anything demanding executor judgment at
  capture time loses.

## Risks

- **The rewrite lands while THREE v1 plans are live in this repo — and one of them is this
  plan.** `specs/` holds `docs-verification-layer` (0/26), `instrument-and-extend-skill-front`
  (29/46, being built now), and `specs-front-v2` itself. The second-order hazard is the one that
  bites: a migration run mid-plan moves this plan out from under its own apply loop, and the
  remaining tasks would be driven by a **v1** `quenching-specs-plan-apply` (not rewritten until
  4.3) against a **v2** workspace with a **v2** tool — three files, three formats, twelve tasks
  open. Mitigation: the dogfood is split. Task 3.1 folds plans mechanically, task 3.3 proves the
  routine against a **throwaway copy** (so section 4 never assumes an unproven migration), and the
  **real** workspace is migrated by task 6.3, last of all. The whole build therefore runs on stable
  v1 rails.
- **Section headings become the entire parse contract.** A typo'd heading silently orphans a
  section. Mitigation: `validate` checks the canonical heading set and flags strays;
  `promote` refuses on malformed sections, so drift is caught at every gate.
- **`## Handoff` staleness misleads executors.** Mitigation: decision 11's event-bound
  refresh + the `validate` warning for an empty Handoff in `ready/`.
- **Scope creep in the skills rewrite, and a doctrine regression nothing would catch.** Thirteen
  skills is a lot of prose, and by this repo's own doctrine skill bodies ARE the source code, yet
  `skills.py doctor` only proves the bijection and naming — a rewritten body can shed its
  `**Done when:**` criteria or widen a `Bash` grant and still exit 0. The context ceiling makes it
  worse: the surface is at 32093 of 36503 characters always on (88%), so thirteen bodies absorbing
  the thirteen-section contract, the gate table and the executor contract can breach it, and an
  always-on overrun is paid silently by every session in every installed repo. Mitigation: 4.1
  records the pre-rewrite baseline (`budget` + `lint` findings by code) and 4.4 asserts against it
  — no new lint code class, budget under ceiling. Surface shrink stays a goal, not a gate; a skill
  that maps 1:1 is rewritten 1:1 and moves on.
- **`schema.json` becomes the load-bearing artifact.** Once the gates are per-phase section sets
  (decision 13) read by both `promote` and `validate`, a wrong phase→section mapping fails in one
  of two silent ways: too strict blocks every promote, too loose lets an empty spec through every
  gate. Mitigation: task 1.2 writes the mapping as the single source both consumers read, task 2.5
  makes `validate` assert it, and task 6.1's throwaway lifecycle exercise proves the phase-scoped
  rule **in both directions** — a freshly captured spec derives as `captured` and never `designed`,
  and a present-but-empty heading refuses.
- **ACCEPTED — an upgraded target repo may read a v1 workspace as empty rather than as wrong
  format.** v2 `list` globs the three phase folders, and a v1 `specs/<plan>/` tree matches none of
  them, so a skill can conclude the workspace holds nothing when it in fact holds unmigrated work.
  `doctor` detects v1 leftovers and declares `migrate` as the remedy, but `doctor` is opt-in and
  the ordinary path does not pass through it. Accepted: the case is scoped out (proposal.md
  §Out of Scope), the remedy is one command (`/specs:align`), and the three manuals name it (task
  5.1). A silent failure is the worse shape, and this one is being taken knowingly rather than
  discovered.
- **ACCEPTED — the plan runs twenty-two tasks before any verification fires.** The `end-of-plan`
  policy means a wrong `schema.json` mapping, a broken parser, or a failed migration surfaces only
  after the last task, with thirteen skills already written against it. Accepted because the
  alternative is worse: the sections are genuinely coupled — the tool cannot be proven before the
  contract exists, the migration before the tool, the skills before the migration — and a
  per-section policy would have had section 2's terminal `specs.py validate` run v2 code against a
  still-v1 workspace, passing vacuously or blocking forever. Task 6.1's throwaway lifecycle
  exercise is the real proof either way, and it runs before 6.3 touches the live workspace.
