---
description: Align the whole repository — /docs/, /.design/, then .claude/, ops and proof — on ONE confirmation, looped until nothing changes anywhere. Triggers on "align the repo", "align everything", "align and update everything", "set up quenching here", "converge this repository", "run all the aligns", "fix both fronts", or "fix all fronts". Probes the five aligned fronts read-only, asks once, then invokes each applicable front's align in dependency order. Authorization nests one level — each front align inherits the OK and never re-asks, while taste arbitration, a code-coupled rename and an irreversible close keep their own human choice. Conducts, never reimplements. Not for: aligning one front → its `/quenching:*:align` command; changing product code → the owning spec.
argument-hint: [optional-scope]
allowed-tools: Read, Grep, Glob, Bash(python3:*), Bash(py:*), Skill
---

# /align — one confirmation, the whole repository

**Input**: `$ARGUMENTS` (an optional scope; omit to align the whole repository).

| # | Front | Align | What converges |
| --- | --- | --- | --- |
| 1 | `/docs/` — the OKF bundle | `/quenching:knowledge:align` | homes, frontmatter stamps, every `index.md`, the validator — then project memory, the harness, the glossary |
| 2 | `/.design/` — the design source | `/quenching:design:align` | DTCG source, product/design/medium projections, sidecar, adapters, assets and non-web drift |
| 3 | `.claude/` — the automation surface | `/quenching:components:align` | command paths on the taxonomy axis, collapsed pairs, the rule + registry, the GENERATED zone — then the read-only doctrine audit |
| 4 | `ops` — the operations surface | `/quenching:ops:align` | declared operation roots, entry-point inventory, registry and lifecycle/write-policy findings |
| 5 | `proof` — the verification surface | `/quenching:proof:align` | test layers, fixture ownership, gate evidence, measured surfaces and the coverage floor |

**The `specs` front has no align, and that is not an omission.** Its canonical documents live in the
repository provider — GitHub Issues or Azure Boards — so there is no local workspace to converge:
`remover-backend-local-do-plugin` retired the local backend and the front's align with it. What
survived as commands is `/quenching:specs:status` (read the front, writes nothing) and
`/quenching:specs:triage` (rank it, on the human's own confirmation), and neither is an align —
this conductor never invokes them in place of one.

Align probes first.

Resolve `cq` — written bare in the probe below — per
[tool-resolution.md](${CLAUDE_PLUGIN_ROOT}/assets/references/align/tool-resolution.md)
§Resolving the tool. Branch on the **exit code**
(0 ok · 1 findings · 2 refusal) and the `--json`, never on prose.

## Doctrine

- **Order is a dependency, not a preference.** `/docs/` → `/.design/` → `.claude/` → `ops` → `proof`.
  Never run a later front before an earlier one.
- **Loop across fronts.**
- **Conduct, never reimplement.** The conductor sequences, gates, and reports. If a front's
  behaviour must change, change that front's align — the same ONE-authority-per-concern rule that
  keeps each align from re-deriving its own stages' logic.
- **Front presence decides the pass; only `/docs/` is installed unasked.** An absent `/docs/` bundle
  is *the* thing this plugin installs, so front 1 always runs. An absent `/.design/` front runs
  only when the request names design/setup or portable product/design artifacts already signal it;
  otherwise it is reported as available. An empty `.claude/` surface skips front 3 rather than
  scaffolding a taxonomy for nothing. `ops` and `proof` are conditional too: their declared roots
  or the conventional-root probes in step 1 decide applicability, while an absent front is only
  reported as available.
- **Converge or report — never spin.** Cross-front pass cap **3** (each front align keeps its own
  internal cap of 5). An empty pass with residual findings is **residue**: stop, and report it
  front by front with the command that owns each item.

## Workflow (probe → ONE OK → five local fronts → re-probe → loop)

### 1. Probe the five local fronts (read-only, cheap)
If `$ARGUMENTS` names a front or a path inside one, resolve it to that front and probe only that
front; report the other fronts as skipped by scope. With no argument, probe all and preserve
the dependency order below.
Presence and rough scale only:
- **`/docs/`** — does the bundle root exist (`/docs/index.md` with `okf_version`)? Run
  `cq knowledge validate /docs --json` and keep
  the finding counts; note whether the project memory dir
  (`~/.claude/projects/<cwd>/memory/`) holds files and which harness files exist.
- **`/.design/`** — run `cq --root . design status --json` when installed; when absent, run
  `cq --root . design align --check --json` only if the request or existing portable artifacts
  signal this front. Record root PRODUCT/DESIGN provenance and any pending import/build choice.
- **.claude/** — `cq components doctor --json` for the command count and its findings; `Glob`
  `.claude/skills/*/SKILL.md` and directory-scoped `**/.claude/skills/*/SKILL.md` for legacy pairs,
  noting how many are legacy CLI-generated `openspec-*` shadow copies.
- **`ops`** — read `.claude/quenching.json` for `opsRoot`; when it is absent, inspect only the fixed
  conventional roots `scripts/`, `tools/`, `bin/` and `script/` for an executable entry point. A
  declared root or a conventional root with an executable entry point makes the front applicable;
  neither means *not applicable*, with a one-line invitation to declare it. Do not turn that
  invitation into a plan item.
- **`proof`** — read `.claude/quenching.json` for `proofRoot`; when it is absent, inspect only
  `tests/` and `test/` for a test module. A declared root or a conventional root with a test module
  makes the front applicable; neither means *not applicable*, with the same one-line invitation.
  An applicable but undeclared front is adoption work, not drift, until its own align is invoked.

**All applicable fronts probe clean** → say so and stop, before any plan: *"all applicable fronts conformant
— nothing to align."*
**Done when:** each front is marked *present / absent / not applicable* with its counts, and
nothing has been written.

### 2. Present the RUN plan → gate on ONE OK (once, before pass 1)
One short table: front · state · what its align will do, including which of its **content stages**
have work (counts and scope, **not** full diffs — each align still presents its own detailed plan
as narration when it runs) · skipped-and-why.

State plainly: *"this authorizes up to 3 cross-front passes of every stage below; each front align
inherits this OK and will not ask again; taste arbitration, a rename touching product code and each
spec's close-out still require their own human choice."* Wait for **one** OK.
**Done when:** the user has answered; declined → nothing written, run ends.

### 3. Front 1 — `/quenching:knowledge:align` (the `/docs/` bundle)
Invoke via the **Skill** tool under its registry name **`quenching:knowledge:align`** — the command path
prefixed by the plugin. Every front below is named the same way; the forms and the condition
on each are [sweep-doctrine.md](${CLAUDE_PLUGIN_ROOT}/assets/references/align/sweep-doctrine.md)
§7. Citing a command.
Declare the authorization mode verbatim per
[convergence.md](${CLAUDE_PLUGIN_ROOT}/assets/references/align/convergence.md)
§The cycle-authorization contract, naming *this* command as the grantor: *"Running under /align authorization
granted at run start — skip your plan-confirmation pause; present your plan as narration and
execute; code-coupled and irreversible items still gate individually."*

It loops the `docs` front to its own fixpoint. Record what it changed and its residual validator
findings. A hard failure here (the bundle could not be established) **stops the run** — fronts 2
through 5 write into or depend on the bundle.
**Done when:** the align has finished and its outcome is recorded.

### 4. Front 2 — `/quenching:design:align` (the `/.design/` source)
Skip when the front is absent and neither scope nor existing portable artifacts signal adoption.
Otherwise invoke **`quenching:design:align`** with the inherited declaration. Product truth and
design standards land in the bundle front 1 established; taste arbitration remains a human choice,
not a second authorization. A hard failure to establish valid DTCG stops front 3.
**Done when:** the design align has converged or been skipped with a stated reason.

### 5. Front 3 — `/quenching:components:align` (the `.claude/` surface)
Skip if the surface is empty (nothing to migrate). Otherwise invoke **`quenching:components:align`**
with the same declaration. Its rule + registry creation lands in the bundle front 1 just aligned —
verify both earlier fronts held before invoking. Record its counts and its **doctrine findings**
(read-only, routed to `/quenching:components:command:new`).
**Done when:** the align has finished or been skipped with a stated reason.

### 6. Front 4 — `/quenching:ops:align` (the `ops` surface)
Skip when the applicability probe says the operations front is absent. Otherwise invoke
`quenching:ops:align` after the components front, under the inherited declaration. Its findings
and registry output feed the proof front's conditional entry-point check.
**Done when:** the align has finished or been skipped with a stated reason.

### 7. Front 5 — `/quenching:proof:align` (the `proof` surface)
Skip when the applicability probe says the proof front is absent. Otherwise invoke
`quenching:proof:align` after the ops front, under the inherited declaration. It consumes the ops
inventory when that front is configured and reports its own layer and gate residue.
**Done when:** the align has finished or been skipped with a stated reason.

### 8. Re-probe across fronts → decide (loop or stop)
Re-run step 1's probe **plus** the cross-front edges: did front 2 add product/design standards, did
front 3 create the automation rule/registry, or did front 4/5 add listings or proof resources
(either → `/docs/` listings to regenerate)?
Then decide by the four outcomes in
[convergence.md](${CLAUDE_PLUGIN_ROOT}/assets/references/align/convergence.md)
§The convergence contract: **progress** → another cross-front pass from step 3 under the same
authorization, narrating what each front will do this time (fronts whose input is unchanged will
probe clean and cost one call each); **converged** → step 9; **residue** → stop and report;
**cross-front pass cap of 3 reached** → stop and report what remains.

A front align's own read-only findings — the doctrine audit, the cycle actions it can only report —
are **not** progress and never justify another cross-front pass.
**Done when:** the loop has stopped for a stated reason.

### 9. Consolidated report
One report, front by front: passes run, what each front's stages did in total, its ending verify
state (validator findings · `doctor`/`validate` · registry-vs-disk), and — explicitly — everything
**deferred**, each with the command that closes it (`/quenching:knowledge:add`, `/quenching:knowledge:learn`, `/quenching:knowledge:define`,
`/quenching:specs:develop`, `/quenching:specs:conclude`, `/quenching:design:genre:new`,
`/quenching:components:command:new`). Name the cross-front edges that actually fired,
so the loop's value is visible.

This command writes **nothing** of its own — not even a record that it ran. Every write belongs
to the front align that made it, and the report is where this run is accounted for.
**Done when:** every front's outcome and every deferral is stated.

## Invariants to never violate

- Never run the fronts out of order, and never continue when an earlier front failed to establish
  what the next front writes into or consumes.
- Never ask for a second authorization, and never let a front align re-gate — authorization nests
  one level ([convergence.md](${CLAUDE_PLUGIN_ROOT}/assets/references/align/convergence.md)
  §The cycle-authorization contract). Equally, never suppress the interruptions the contract never
  covers: taste arbitration, code-coupled renames and irreversible closes.
- Never reimplement a front's or a stage's logic here — **invoke** the front align via the Skill
  tool, always.
- Never act on a front's reported residue (concluding a spec it only listed, minting a command or
  genre, writing a standard) — carry it into the report and name the command that owns it.
- Never scaffold a `.claude/` taxonomy for an empty surface; never silently install a visual world
  when design adoption was not requested or signalled.
- Never loop past the cross-front pass cap of 3, never re-run a pass that just changed nothing, and
  never widen scope to force a clean number.
- Never hand this command file `context: fork` — the gate and every nested confirmation are
  mid-flow.
