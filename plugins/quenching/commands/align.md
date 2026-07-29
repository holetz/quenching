---
description: Align the whole repository — docs/ then specs/ then .claude/ — on ONE confirmation, looped until nothing changes anywhere. Triggers on "align the repo", "align everything", "align and update everything", "set up quenching here", "converge this repository", "run all the aligns", "fix all three fronts". Probes the three fronts read-only, asks once, then invokes each front's align in dependency order and loops across them, because they feed each other: a spec's distillation is glossary work, and the skill front's registry is a docs/ listing. Authorization nests one level — each front align inherits the OK and never re-asks, while a code-coupled rename and an irreversible close still gate on their own. Conducts, never reimplements: every write is made by the front align it invokes. Not for: one front only → /docs:align, /specs:align, /skill:align; reading without changing → /docs:status, /specs:status; the next action on one spec → /specs:continue.
argument-hint: [optional-scope]
allowed-tools: Read, Grep, Glob, Bash(python3:*), Bash(py:*), Skill
---

# /align — one confirmation, the whole repository

**Input**: `$ARGUMENTS` (an optional scope; omit to align the whole repository).

The plugin acts on **three** surfaces of a repository, and each has exactly one align that forces
it into the plugin's canonical shape and then keeps filling it. This command is the **fourth**: the
one that spans all three.

| # | Front | Align | What converges |
| --- | --- | --- | --- |
| 1 | `docs/` — the OKF bundle | `/docs:align` | homes, frontmatter stamps, every `index.md`, the validator — then project memory, the harness, the glossary |
| 2 | `specs/` — the spec-driven workspace | `/specs:align` | scaffold, doctor/validate, spec + archive names, the `plans/` inbox and its derived zone — then the close-outs and the ranking |
| 3 | `.claude/` — the automation surface | `/skill:align` | command paths on the taxonomy axis, collapsed pairs, the rule + registry, the GENERATED zone — then the read-only doctrine audit |

The surface is **one column, not a matrix**: there is no separate "align-and-update" anywhere. An
align probes first, so a conformant front costs a couple of tool calls and says so
([sweep-doctrine](${CLAUDE_PLUGIN_ROOT}/assets/references/align/sweep-doctrine.md) §Probe before
the inventory) — which is what made it safe for each align to carry its own content stages instead
of needing a second command nobody remembered to run.

This command is the **conductor** over the three. It runs one read-only probe, asks for **one**
confirmation, invokes the three aligns in dependency order, and **loops**, because the fronts feed
each other. It never edits a doc, a spec, or a command itself: every write is made by the align it
invokes, under that align's own doctrine and its own confirmation for code-coupled items.

It **owns** the two contracts every align shares, and they live beside each other in
`${CLAUDE_PLUGIN_ROOT}/assets/references/align/`:

- [sweep-doctrine.md](${CLAUDE_PLUGIN_ROOT}/assets/references/align/sweep-doctrine.md) — probe
  before the inventory, convergence over accommodation, one plan → one OK with code-coupled items
  gating individually, the two-scan blast-radius procedure, MERGE-never-clobber,
  never-delete-on-a-guess, align-conformance-report-the-cycle.
- [convergence.md](${CLAUDE_PLUGIN_ROOT}/assets/references/align/convergence.md) — the
  cycle-authorization contract, the convergence condition, the anti-spin guards, and why per-item
  commands are never stages.

They live here because this is the command that spans all three fronts; each align cites them as
its doctrine and states only its own front's deltas. A change to how a sweep behaves is one edit
here, not three edits that must stay in agreement.

## Doctrine

- **Order is a dependency, not a preference.** `docs/` → `specs/` → `.claude/`:
  - **docs first** — both other fronts write OKF artifacts into the bundle (the skill front's
    rule `docs/standards/automation/skills.md` and registry
    `docs/documentation/reference/automation.md`; the `docs/standards/` docs a spec's
    distillation mints). None can land in a tree that is not there.
  - **specs before skills** — when migrating a legacy `openspec/` workspace, `/specs:align`
    removes the CLI-generated `.claude/skills/openspec-*` + `.claude/commands/opsx/` shadow
    copies, so `/skill:align` inventories an already-clean surface instead of classifying plugin
    duplicates onto the taxonomy axis (a native `specs/` repo has no such copies, so the order is
    harmless there and still holds).
  Never run a later front before an earlier one.
- **Loop across fronts, because they feed each other.** This is the whole reason this command is
  not three invocations typed in a row. The concrete edges:
  - `/specs:align` **concludes** a spec → its distillation mints docs into `docs/` → the `docs/`
    front's glossary stage must now index those terms.
  - `/skill:align` **creates** the rule and registry in `docs/` → the `docs/` front's `index.md`
    must list them.
  - `/docs:align`'s **harness** stage moves a fact into `docs/` that a `specs/` spec should now
    cite instead of restating.
  A single cross-front pass would leave every one of those half-done.
- **One OK for the whole repo; authorization nests one level.** The gate fires **once**, before
  pass 1. Each front align **inherits** it and passes it down verbatim to its own stages — it does
  not ask again
  ([convergence.md](${CLAUDE_PLUGIN_ROOT}/assets/references/align/convergence.md) §Nesting).
  After that OK, the only possible interruptions are the two the contract never covers: a
  **code-coupled** rename, and an **irreversible close** (concluding a spec).
- **Conduct, never reimplement.** The conductor sequences, gates, and reports. If a front's
  behaviour must change, change that front's align — the same ONE-authority-per-concern rule that
  keeps each align from re-deriving its own stages' logic.
- **Front presence decides the pass; only `docs/` is installed unasked.** An absent `docs/` bundle
  is *the* thing this plugin installs, so front 1 always runs. An absent `specs/` is **offered as
  its own line in the plan** — scaffolding it imposes a spec-driven workflow, so it is opt-in,
  never a side effect. An empty `.claude/` surface (no commands, no skills) skips front 3 with a
  note rather than scaffolding a taxonomy for nothing.
- **Converge or report — never spin.** Cross-front pass cap **3** (each front align keeps its own
  internal cap of 5). An empty pass with residual findings is **residue**: stop, and report it
  front by front with the command that owns each item.

## Workflow (probe → ONE OK → three fronts → re-probe → loop)

### 1. Probe the three fronts (read-only, cheap)
Presence and rough scale only — **not** a full inventory, which each align does for itself, and
each already probes before paying for one:
- **docs/** — does a bundle root exist (`docs/` or the repo's variant, `index.md` /
  `okf_version`)? Run `${CLAUDE_PLUGIN_ROOT}/assets/hooks/okf-validate.py <docs> --json` and keep
  the finding counts; note whether the project memory dir
  (`~/.claude/projects/<cwd>/memory/`) holds files and which harness files exist.
- **specs/** — does a `specs/` root exist? If yes, `specs.py doctor --json` and
  `specs.py list --json` for the spec count and how many read complete.
- **.claude/** — `skills.py doctor --json` for the command count and its findings; `Glob`
  `.claude/skills/*/SKILL.md` and directory-scoped `**/.claude/skills/*/SKILL.md` for legacy pairs,
  noting how many are legacy CLI-generated `openspec-*` shadow copies (front 2 clears those when
  migrating a legacy `openspec/` workspace).
- **the installed tools** — one call, spanning all three fronts:
  ```bash
  python3 "${CLAUDE_PLUGIN_ROOT}/assets/bin/skills.py" drift --json
  ```
  It reports each installed copy under `.claude/hooks/` against the version this plugin ships —
  **in both directions** — and whether `okf-validate.py` is actually invoked by a `hooks` block.
  Run it from the **plugin path**, never from `.claude/hooks/skills.py`: an installed copy answers
  from the same stale `VERSION` it is being asked about, and refuses (exit 2) rather than lie.
  `sk-tool-behind` and `sk-tool-unwired` are errors and belong in the plan; `sk-tool-ahead`,
  `sk-tool-unreadable` and `sk-tool-absent` are warnings to report. Each finding names the align
  that fixes it, so the row goes to that front's section of the step-2 plan — **this command never
  installs or overwrites a tool itself.**

**All three fronts probe clean** → say so and stop, before any plan: *"all three fronts conformant
— nothing to align."* A drift error is **not** clean: an install offer belongs in the plan even
when the three fronts' own findings are empty. That is the cheapest complete answer this command
can give, and giving it is the point of probing here rather than inside three separate runs.
**Done when:** each front is marked *present / absent / not applicable* with its counts, and
nothing has been written.

### 2. Present the RUN plan → gate on ONE OK (once, before pass 1)
One short table: front · state · what its align will do, including which of its **content stages**
have work (counts and scope, **not** full diffs — each align still presents its own detailed plan
as narration when it runs) · skipped-and-why. Name the specs proposed for conclusion. An absent
`specs/` appears as an explicit opt-in line (*"scaffold `specs/`? — declining skips front 2"*).

State plainly: *"this authorizes up to 3 cross-front passes of every stage below; each front align
inherits this OK and will not ask again; only a rename touching product code and each spec's
close-out still confirm on their own."* Wait for **one** OK.
**Done when:** the user has answered; declined → nothing written, run ends.

### 3. Front 1 — `/docs:align` (the `docs/` bundle)
Invoke via the **Skill** tool under its registry name **`quenching:docs:align`** — the command path
prefixed by the plugin. Every front below is named the same way: a bare `/docs:align` is what a
human types, not what the Skill tool resolves. Declare the authorization mode verbatim per
[convergence.md](${CLAUDE_PLUGIN_ROOT}/assets/references/align/convergence.md)
§cycle-authorization, naming *this* command as the grantor: *"Running under /align authorization
granted at run start — skip your plan-confirmation pause; present your plan as narration and
execute; code-coupled and irreversible items still gate individually."*

It loops the `docs/` front to its own fixpoint. Record what it changed and its residual validator
findings. A hard failure here (the bundle could not be established) **stops the run** — fronts 2
and 3 write into the bundle.
**Done when:** the align has finished and its outcome is recorded.

### 4. Front 2 — `/specs:align` (the `specs/` workspace)
Skip if the front was marked absent and the scaffold line was declined. Otherwise invoke
**`quenching:specs:align`** with the same declaration. Record its counts, **which specs were
concluded** (their distillations are the main cross-front feed into front 1's next pass), and its
reported-not-applied residue verbatim — those flow into the final report unchanged, never acted on
here. A failure in this front is **reported, not fatal**: front 3 still runs, and the report says
the command surface was inventoried with legacy shadow copies possibly still present.
**Done when:** the align has finished or been skipped with a stated reason.

### 5. Front 3 — `/skill:align` (the `.claude/` surface)
Skip if the surface is empty (nothing to migrate). Otherwise invoke **`quenching:skill:align`**
with the same declaration. Its rule + registry creation lands in the bundle front 1 just aligned —
verify the front order held before invoking. Record its counts and its **doctrine findings**
(read-only, routed to `/skill:new`).
**Done when:** the align has finished or been skipped with a stated reason.

### 6. Re-probe across fronts → decide (loop or stop)
Re-run step 1's probe **plus** a check of the specific cross-front edges: did front 2 conclude
anything (→ new `docs/` content for front 1's glossary stage)? did front 3 create the rule or
registry (→ `docs/` listings to regenerate)? Then decide by the four outcomes in
[convergence.md](${CLAUDE_PLUGIN_ROOT}/assets/references/align/convergence.md)
§The convergence contract: **progress** → another cross-front pass from step 3 under the same
authorization, narrating what each front will do this time (fronts whose input is unchanged will
probe clean and cost one call each); **converged** → step 7; **residue** → stop and report;
**cross-front pass cap of 3 reached** → stop and report what remains.

A front align's own read-only findings — the doctrine audit, the cycle actions it can only report —
are **not** progress and never justify another cross-front pass.
**Done when:** the loop has stopped for a stated reason.

### 7. Consolidated report
One report, front by front: passes run, what each front's stages did in total, its ending verify
state (validator findings · `doctor`/`validate` · registry-vs-disk), and — explicitly — everything
**deferred**, each with the command that closes it (`/docs:add`, `/docs:learn`, `/docs:define`,
`/specs:develop`, `/specs:conclude`, `/skill:new`). Name the cross-front edges that actually fired,
so the loop's value is visible.

State which **operator manuals** each front installed, refreshed, or left alone
(`docs/QUENCHING.md`, `specs/QUENCHING.md`, `.claude/QUENCHING.md`) — each front writes its own;
this command only reports them, and points a first-time adopter at `docs/QUENCHING.md` as the place
to start.

This command writes **nothing** of its own — not even a record that it ran. Every write belongs
to the front align that made it, and the report is where this run is accounted for.
**Done when:** every front's outcome and every deferral is stated.

## Invariants to never violate

- Never run the fronts out of order, and never continue when front 1 failed to establish the
  bundle the other two write into.
- Never ask for a second authorization, and never let a front align re-gate — authorization nests
  one level ([convergence.md](${CLAUDE_PLUGIN_ROOT}/assets/references/align/convergence.md)
  §Nesting). Equally, never suppress the two interruptions the contract never covers: code-coupled
  renames and irreversible closes.
- Never reimplement a front's or a stage's logic here — **invoke** the front align via the Skill
  tool, always.
- Never act on a front's reported residue (concluding a spec it only listed, minting a command,
  writing a standard) — carry it into the report and name the command that owns it.
- Never scaffold `specs/` without its own explicit line in the plan, and never scaffold a
  `.claude/` taxonomy for an empty surface.
- Never loop past the cross-front pass cap of 3, never re-run a pass that just changed nothing, and
  never widen scope to force a clean number.
- Never hand this command file `context: fork` — the gate and every nested confirmation are
  mid-flow.
