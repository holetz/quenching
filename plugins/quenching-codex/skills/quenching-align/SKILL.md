---
name: quenching-align
description: "Align the whole repository — /docs/ then .agents/ — on ONE confirmation, looped until nothing changes anywhere. Triggers on \"align the repo\", \"align everything\", \"align and update everything\", \"set up quenching here\", \"converge this repository\", \"run all the aligns\", \"fix both fronts\". Probes the two aligned fronts read-only, asks once, then invokes each front's align in dependency order. Authorization nests one level — each front align inherits the OK and never re-asks, while a code-coupled rename and an irreversible close still gate on their own. Conducts, never reimplements: every write is made by the front align it invokes."
---

<!-- GENERATED FROM plugins/quenching/commands/align.md -->


# /align — one confirmation, the whole repository

**Input**: `$ARGUMENTS` (an optional scope; omit to align the whole repository).

| # | Front | Align | What converges |
| --- | --- | --- | --- |
| 1 | `/docs/` — the OKF bundle | `quenching-knowledge-align` | homes, frontmatter stamps, every `index.md`, the validator — then project memory, the harness, the glossary |
| 2 | `.agents/` — the automation surface | `quenching-components-align` | command paths on the taxonomy axis, collapsed pairs, the rule + registry, the GENERATED zone — then the read-only doctrine audit |

**The `specs` front has no align, and that is not an omission.** Its canonical documents live in the
repository provider — GitHub Issues or Azure Boards — so there is no local workspace to converge:
`remover-backend-local-do-plugin` retired the local backend and the front's align with it. What
survived as commands is `quenching-specs-status` (read the front, writes nothing) and
`quenching-specs-triage` (rank it, on the human's own confirmation), and neither is an align —
this conductor never invokes them in place of one.

Align probes first.

Resolve `cq` — written bare in the probe below — per
[tool-resolution.md](../../references/align/tool-resolution.md)
§Resolving the tool. Branch on the **exit code**
(0 ok · 1 findings · 2 refusal) and the `--json`, never on prose.

## Doctrine

- **Order is a dependency, not a preference.** `/docs/` → `.agents/`.
  Never run a later front before an earlier one.
- **Loop across fronts.**
- **Conduct, never reimplement.** The conductor sequences, gates, and reports. If a front's
  behaviour must change, change that front's align — the same ONE-authority-per-concern rule that
  keeps each align from re-deriving its own stages' logic.
- **Front presence decides the pass; only `/docs/` is installed unasked.** An absent `/docs/` bundle
  is *the* thing this plugin installs, so front 1 always runs. An empty `.agents/` surface (no
  commands, no skills) skips front 2 with a
  note rather than scaffolding a taxonomy for nothing.
- **Converge or report — never spin.** Cross-front pass cap **3** (each front align keeps its own
  internal cap of 5). An empty pass with residual findings is **residue**: stop, and report it
  front by front with the command that owns each item.

## Workflow (probe → ONE OK → two fronts → re-probe → loop)

### 1. Probe the two fronts (read-only, cheap)
If `$ARGUMENTS` names a front or a path inside one, resolve it to that front and probe only that
front; report the other front as skipped by scope. With no argument, probe both and preserve
the dependency order below.
Presence and rough scale only:
- **`/docs/`** — does the bundle root exist (`/docs/index.md` with `okf_version`)? Run
  `cq knowledge validate /docs --json` and keep
  the finding counts; note whether the project memory dir
  (`~/.codex/projects/<cwd>/memory/`) holds files and which harness files exist.
- **.agents/** — `cq components doctor --json` for the command count and its findings; `Glob`
  `.agents/skills/*/SKILL.md` and directory-scoped `**/.agents/skills/*/SKILL.md` for legacy pairs,
  noting how many are legacy CLI-generated `openspec-*` shadow copies.

**Both fronts probe clean** → say so and stop, before any plan: *"both fronts conformant
— nothing to align."*
**Done when:** each front is marked *present / absent / not applicable* with its counts, and
nothing has been written.

### 2. Present the RUN plan → gate on ONE OK (once, before pass 1)
One short table: front · state · what its align will do, including which of its **content stages**
have work (counts and scope, **not** full diffs — each align still presents its own detailed plan
as narration when it runs) · skipped-and-why.

State plainly: *"this authorizes up to 3 cross-front passes of every stage below; each front align
inherits this OK and will not ask again; only a rename touching product code and each spec's
close-out still confirm on their own."* Wait for **one** OK.
**Done when:** the user has answered; declined → nothing written, run ends.

### 3. Front 1 — `quenching-knowledge-align` (the `/docs/` bundle)
Invoke via the **Skill** tool under its registry name **`quenching:knowledge:align`** — the command path
prefixed by the plugin. Every front below is named the same way; the three forms and the condition
on each are [sweep-doctrine.md](../../references/align/sweep-doctrine.md)
§7. Citing a command.
Declare the authorization mode verbatim per
[convergence.md](../../references/align/convergence.md)
§The cycle-authorization contract, naming *this* command as the grantor: *"Running under /align authorization
granted at run start — skip your plan-confirmation pause; present your plan as narration and
execute; code-coupled and irreversible items still gate individually."*

It loops the `docs` front to its own fixpoint. Record what it changed and its residual validator
findings. A hard failure here (the bundle could not be established) **stops the run** — fronts 2
and 3 write into the bundle.
**Done when:** the align has finished and its outcome is recorded.

### 4. Front 2 — `quenching-components-align` (the `.agents/` surface)
Skip if the surface is empty (nothing to migrate). Otherwise invoke **`quenching:components:align`**
with the same declaration. Its rule + registry creation lands in the bundle front 1 just aligned —
verify the front order held before invoking. Record its counts and its **doctrine findings**
(read-only, routed to `quenching-components-command-new`).
**Done when:** the align has finished or been skipped with a stated reason.

### 5. Re-probe across fronts → decide (loop or stop)
Re-run step 1's probe **plus** a check of the cross-front edge: did front 2 create the rule or
registry (→ `/docs/` listings to regenerate)? Then decide by the four outcomes in
[convergence.md](../../references/align/convergence.md)
§The convergence contract: **progress** → another cross-front pass from step 3 under the same
authorization, narrating what each front will do this time (fronts whose input is unchanged will
probe clean and cost one call each); **converged** → step 6; **residue** → stop and report;
**cross-front pass cap of 3 reached** → stop and report what remains.

A front align's own read-only findings — the doctrine audit, the cycle actions it can only report —
are **not** progress and never justify another cross-front pass.
**Done when:** the loop has stopped for a stated reason.

### 6. Consolidated report
One report, front by front: passes run, what each front's stages did in total, its ending verify
state (validator findings · `doctor`/`validate` · registry-vs-disk), and — explicitly — everything
**deferred**, each with the command that closes it (`quenching-knowledge-add`, `quenching-knowledge-learn`, `quenching-knowledge-define`,
`quenching-specs-develop`, `quenching-specs-conclude`, `quenching-components-command-new`). Name the cross-front edges that actually fired,
so the loop's value is visible.

This command writes **nothing** of its own — not even a record that it ran. Every write belongs
to the front align that made it, and the report is where this run is accounted for.
**Done when:** every front's outcome and every deferral is stated.

## Invariants to never violate

- Never run the fronts out of order, and never continue when front 1 failed to establish the
  bundle front 2 writes into.
- Never ask for a second authorization, and never let a front align re-gate — authorization nests
  one level ([convergence.md](../../references/align/convergence.md)
  §The cycle-authorization contract). Equally, never suppress the two interruptions the contract never covers: code-coupled
  renames and irreversible closes.
- Never reimplement a front's or a stage's logic here — **invoke** the front align via the Skill
  tool, always.
- Never act on a front's reported residue (concluding a spec it only listed, minting a command,
  writing a standard) — carry it into the report and name the command that owns it.
- Never scaffold a `.agents/` taxonomy for an empty surface.
- Never loop past the cross-front pass cap of 3, never re-run a pass that just changed nothing, and
  never widen scope to force a clean number.
- Never hand this command file `context: fork` — the gate and every nested confirmation are
  mid-flow.
