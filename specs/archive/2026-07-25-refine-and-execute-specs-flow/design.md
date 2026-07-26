# Design — Refino, rito minimo e execucao eficiente no front specs/

## Context

Binding contracts this design must not contradict:

- **[`docs/standards/naming/command-surface.md`](../../docs/standards/naming/command-surface.md)** —
  every skill is `quenching-<front>-<object>-<verb>`, mirrored one-to-one by a wrapper at
  `commands/<front>/[<object>/]<verb>.md`. The bijection is absolute. A new skill therefore forces
  a new wrapper and moves the count 27 ↔ 27 to 28 ↔ 28.
- **[`docs/standards/automation/skills.md`](../../docs/standards/automation/skills.md)** —
  single-axis classification, mirrored wrapper for a domain-bound skill, trigger phrases in the
  description's second sentence, body well under the size cap with shared procedure pushed into
  `references/`, one plan → one OK, and the OKF tail on every mint.
- **`CLAUDE.md` §"Two rules that must survive any refactor"** — never add `context: fork` to these
  skills, because a forked context cannot present the mid-flow confirmations every sweep depends
  on. Any delegation this plan introduces must be compatible with that rule.
- **The 1,536-character per-skill description cap**, shared with every other installed plugin.
  Each new skill is a permanent always-on cost, so the surface may only grow when nothing existing
  can absorb the work.
- **`specs.py` is stdlib-only, self-contained, and loads its schema and templates from
  `assets/specs/` when adjacent, else from embedded fallbacks** — an installed copy under a
  target's `.claude/hooks/` must keep working. Every change here has to survive that copy.

Forces in play: `specs.py` is 862 lines and every feature here adds to it; `parse_tasks` is the
narrowest interface in the front (four fields) and everything downstream is starved by it; and the
three `QUENCHING.md` operator manuals enumerate the command surface, so a single new command has a
six-file blast radius before any behavior changes.

## Decisions

### 1. One `refine` skill with a mode parameter, not four skills

**Chosen:** `quenching-specs-plan-refine` with `interview` (default), `critic`, `premortem`, and
`alternatives` modes, each mode's script living in `references/techniques.md`.

The classification test in `automation/skills.md` asks which single front the skill acts on: the
answer is `specs/`, and the *object* is a plan, so `quenching-specs-plan-refine` is the only name
the taxonomy allows. The technique is not a different axis — it is a parameter of the same action.

*Alternatives weighed:*
- **Four skills** (`refine-interview`, `refine-critic`, …), the shape the reference commands in
  `Downloads/commands` use and closest to BMAD's elicitation menu. Rejected: four always-on
  descriptions (~6 KB of the shared cap) for four variants of one verb, and the wrapper bijection
  would put four near-identical files under `commands/specs/plan/`.
- **Fold into `quenching-specs-plan-update`.** Rejected: `update` is reactive — the human states
  the edit and the skill reconciles. `refine` is generative — it produces the questions. Opposite
  direction of initiative; merging them makes a skill that both waits and interrogates, which is
  exactly the ambiguity the taxonomy's verb-first rule forbids.
- **Fold into `quenching-specs-explore`.** Rejected: `explore` is pre-commitment and unbounded by
  design; `refine` targets a specific artifact of a specific plan and must terminate. Different
  stop conditions cannot share a skill.

### 2. Refinement is recorded and warned about, never gating

**Chosen:** `.specs.json` gains `refined: {mode, date}`; `specs.py validate` emits `sp-unrefined`
at **warn** severity when a plan has a `tasks.md` and no record. `applyReady` is untouched.

*Alternative:* gate `applyReady` on refinement, the way spec-kit's issue #2496 argues `/clarify`
should be a regular step. Rejected: it would break every existing plan in every installed repo on
upgrade, and it contradicts the front's own doctrine that a sweep never blocks on a judgment call.
A warning that surfaces in `/specs:status` gets the behavior without the breakage.

### 3. `design.md` becomes required-with-explicit-fallback

**Chosen:** keep the file always present; add `## Alternatives Considered` and `## Open Decisions`;
require an explicit `- none — <reason>` where a section is empty. `specs.py validate` gains a check
that the file is not a bare scaffold.

The current "optional, delete it rather than pad it" reads as discipline but destroys information:
an absent `design.md` cannot distinguish *considered, none* from *never thought about it*. The
reference commands solve this with `- nenhuma — única abordagem viável`, and an explicit null is
strictly more information than a missing file.

*Alternative:* keep `design.md` optional and move `## Alternatives` into `proposal.md`. Rejected:
it overloads the proposal, which is the artifact meant to be readable in one sitting, and it
splits the design rationale across two files.

**Consequence to accept:** `compute_next` must now emit a design action (defect 1), and
`applyRequires` still must **not** include `design` — a required *section set* is not the same as
a required *dependency*, and adding it to `applyRequires` would strand every existing plan.

### 4. `tasks.md` metadata as indented lines under the checkbox

**Chosen:**

```markdown
- [ ] 3.2 Add rate limiting to the auth middleware
      files: src/middleware/auth.ts, src/config/limits.ts (new)
      pattern: src/middleware/cors.ts
      verify: pnpm test middleware/
```

`CHECKBOX_RE` already ignores non-matching lines, so **every existing `tasks.md` keeps parsing
unchanged** and the metadata is purely additive. It also stays readable as plain markdown, which
matters because a human reviews `tasks.md` before apply.

*Alternatives weighed:*
- **One file per task** (`02-tasks/NN-slug.md`), the BMAD story-file and `sdd-executar` shape. It
  is the strongest form of context engineering — the executor needs nothing else — but it replaces
  `tasks.md` outright, breaks `specs.py task --check`, breaks every archived plan, and turns a
  one-file review into an N-file review. Rejected for this plan; the indented form carries the
  same four facts at a fraction of the blast radius.
- **YAML frontmatter per task or a fenced block.** Rejected: unreadable inline, and it would make
  `tasks.md` a machine format when its whole value is being human-reviewable.

### 5. Chaining, not an express-lane skill

**Chosen:** `from-claude` accepts an inline plan, gains `AskUserQuestion` + `Skill`, and offers to
chain into apply; `apply` offers to chain into archive at 100%.

*Alternative:* a `quenching-specs-plan-quick` skill that runs propose → branch → apply → archive
under one confirmation. Rejected **for now**: it costs a 29th always-on description to deliver what
chaining delivers with zero new surface. It is recorded in `## Open Decisions` and revisited only
if the friction survives this change.

### 6. Executors may be delegated; the orchestrator never is

**Chosen:** a per-task executor sub-agent is permitted when the task declares `files:` and touches
no `docs/`, pinned to the session model (never `haiku` — it writes production code). The
orchestrator keeps, without exception: plan selection, every confirmation, every
`specs.py task --check` flip, every `docs/standards/` write, and the decision to pause.

This does **not** violate the never-fork rule. That rule forbids `context: fork` on the *skill*,
which would move the confirmation-bearing conversation itself out of reach. Dispatching a `Task`
for a bounded, file-scoped unit of work leaves the orchestrator in the live conversation, exactly
as `quenching-docs-glossary-backfill` and `quenching-docs-import` already do. The rule and this
decision are about different things, and the standard must say so explicitly so a future sweep
does not "fix" one into the other.

### 7. Parallelism is opt-in and must be earned

**Chosen:** two tasks may run concurrently only when a `[P]` marker was set at propose time **and**
their declared `files:` sets are disjoint **and** neither writes `docs/`. Serial remains the
default; the marker is never inferred at runtime.

Without proven file disjunction, parallel execution trades wall-clock for merge conflict and loses
on both. The `[P]` marker is borrowed from spec-kit; the disjunction requirement is the part
spec-kit leaves to the model and this front should not.

### 8. The verification policy is declared per plan

**Chosen:** `propose` records `verification: per-task | per-section | end-of-plan` in
`.specs.json`, defaulting to `per-section`.

*Alternative:* a single global policy (always test per task, as `sdd-executar` does). Rejected: it
is right for a fast suite and wrong for a slow one, and the plan's author is the only party who
knows which this repo has. Declaring it at propose time means `apply` never has to guess and never
has to ask mid-implementation.

Code review splits by cost the same way: the cheap four-item diff self-review (reuse, useless
defense, obvious comment, dead code) runs **per task** inside the executor, and a full-diff review
runs **once** over the branch at the end of the plan — never per task, where it would triple the
cost of a three-line change.

### 9. Attempt state lives in `.specs.json`, not in the checkbox

**Chosen:** record per-task attempt counts and last error in `.specs.json`; `next` skips a task
that burned its budget and reports it as blocked.

*Alternative:* a third checkbox glyph (`- [!]`), or the `.fail.md` rename `sdd-executar` uses.
Rejected: `- [!]` breaks `CHECKBOX_RE` for every existing consumer and would not survive a human
editing `tasks.md` by hand; the rename scheme depends on the one-file-per-task layout decision 4
already rejected.

## Alternatives Considered

Recorded per decision above (each `Alternatives weighed` block). At the plan level, one whole-shape
alternative was weighed and rejected:

- **Adopt the `Downloads/commands` SDD pipeline wholesale** (`objetivo` → `plano` → `tasks` →
  `executar` with its own `.sdd/` tree). Rejected: it is a parallel, second spec-driven front with
  its own layout, its own status command, and no OKF bridge — it would duplicate `specs/` rather
  than improve it. Its *mechanisms* (one question at a time with a recommendation, accumulate and
  apply once, per-task validation loop, failure budget, diff self-review, commit per task) are
  what this plan imports; its *structure* is not.

## Open Decisions

- **Whether `quenching-specs-plan-quick` is still needed** after chaining lands — decide by using
  the chained path on real small work for two weeks, not by argument.
- **Whether `sp-unrefined` should ever escalate to `error`** — revisit once there is evidence about
  how often plans reach apply unrefined.
- ~~**Where the executor prompt template lives**~~ — **RESOLVED at task 5: a reference.** The
  `SKILL.md` body was 186 lines before this plan; the validation loop, commit doctrine, two-level
  review split, and delegation rules would have taken it past 350. It all went to
  `quenching-specs-plan-apply/references/execution.md`, and the body cites it — which is also what
  the plugin's own doctrine asks for (shared procedure lives in `references/`, never restated in
  the body). Final body: 286 lines.
- ~~**Whether `[P]` parallelism ships in this plan or the next**~~ — **RESOLVED at task 6: it
  ships.** The earlier sections did not overrun, and the risk turned out to be smaller than
  estimated because the check is mechanical rather than judged: `specs.py parallel` verifies each
  group's `files:` sets are disjoint and exits 0/1, so nothing about `[P]` rests on prose. Tasks
  6.3 and 6.4 are therefore implemented, not struck. A group is bounded to one `## N.` section —
  discovered while testing, since a run straddling two sections marked a genuinely disjoint pair
  ineligible because of a conflict in the next section.

## Risks

- **Surface growth is permanent.** A 28th skill spends shared always-on budget forever.
  *Mitigation:* exactly one new skill; the analyze/quick/per-technique candidates are all
  explicitly out of scope, and the deterministic half of `analyze` goes into `validate` instead.
- **`tasks.md` metadata could break archived plans.** *Mitigation:* the indented form is additive
  and `CHECKBOX_RE` already skips unmatched lines; a backward-compatibility check over existing
  fixtures is a named validation item.
- **`specs.py` bloat.** Six features land in one 862-line stdlib script. *Mitigation:* if it passes
  ~1,200 lines, split the backlog-zone renderer into a module rather than growing one file past
  reviewability — and note it, do not do it silently.
- **Delegation could be misread as permission to fork.** *Mitigation:* decision 6's distinction is
  written into `docs/standards/workflows/task-execution.md` as normative text, not left in this
  design note, so a future sweep reads it as a contract.
- **Commit-per-task changes behavior in repos with commit hooks or signing.** *Mitigation:* the
  dirty-tree precondition and the commit step both surface what they will do before the first one;
  never `--no-verify`, never `--no-gpg-sign`.
- **The plan is large and could half-land.** *Mitigation:* the task sections are ordered so each is
  independently shippable — defects first (sections 1–2), then templates and tooling, then the new
  skill, then execution, then release. Stopping after any section leaves a coherent state.
- **Version lockstep is easy to miss** across five files. *Mitigation:* an explicit release task
  with the lockstep list and a verification item that runs all three `--version` checks.
