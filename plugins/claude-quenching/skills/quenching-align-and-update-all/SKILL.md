---
name: quenching-align-and-update-all
description: >-
  Aligns AND updates ALL THREE fronts of a repository, looped to a cross-front fixpoint: runs
  quenching-docs-align-and-update (docs/), then quenching-specs-align-and-update (specs/), then
  quenching-skill-align-and-update (.claude/), pass after pass, until a whole pass changes
  nothing anywhere. Use when the user asks to "align and update everything", "bring the whole
  repo up to date", "run the full quenching cycle on every front", "converge the repo end to
  end", or "do everything until nothing is left". ONE OK at run start authorizes the whole
  run; each front conductor inherits it and passes it down, so the human confirms once —
  only code-coupled renames and plan archives still interrupt. It loops across fronts
  because they feed each other: an archive distils knowledge into docs/, which the
  glossary must then index. Not for: structure only, one pass,
  no loop → quenching-align-all; one front → quenching-docs-align-and-update /
  quenching-specs-align-and-update / quenching-skill-align-and-update.
when_to_use: >-
  aligning AND updating all three fronts, looped to a cross-front fixpoint.
allowed-tools: Read, Grep, Glob, Bash, Skill
user-invocable: false
---

# quenching-align-and-update-all — every front, until nothing changes anywhere

The top of the plugin's conductor hierarchy. Four skills sit below it, and the whole surface is
one 2×4 matrix — every front has an **align** (structure, one pass) and an **align-and-update**
(structure + content, looped), and the two rightmost columns run all three fronts:

| Front | Align (one pass) | Align-and-update (looped) |
| --- | --- | --- |
| `docs/` — the OKF bundle | `/docs:align` | `/docs:align-and-update` |
| `specs/` — the spec-driven workspace | `/specs:align` | `/specs:align-and-update` |
| `.claude/` — the automation surface | `/skill:align` | `/skill:align-and-update` |
| **all three** | **`/align`** | **`/align-and-update`** ← this skill |

It runs one read-only probe, asks for **one** confirmation, then invokes the three front
conductors in dependency order — and **loops**, because the fronts feed each other. It never
edits a doc, a change, or a skill itself: every write is made two levels down, by the stage skill
its front conductor invokes, under that stage's own doctrine.

This skill **owns** the contract every conductor shares —
[references/convergence.md](references/convergence.md): the cycle-authorization rules, the
convergence condition, the anti-spin guards, and why per-item skills are never stages. Each
front's own pipeline lives with that front's conductor.

## Doctrine

- **Order is a dependency, not a preference.** `docs/` → `specs/` → `.claude/`, the same
  order `quenching-align-all` uses and for the same reasons: the other two fronts write OKF
  artifacts *into* the bundle, and when migrating a legacy `openspec/` workspace the `specs/`
  front clears the CLI shadow copies the `.claude/` front would otherwise inventory. Never run
  a later front before an earlier one.
- **Loop across fronts, because they feed each other.** This is what separates this skill from
  three sequential front conductors. The concrete edges:
  - `quenching-specs-align-and-update` **archives** a change → its distillation pass mints docs into
    `docs/` → the `docs/` front's `quenching-docs-glossary-backfill` must now index those terms.
  - `quenching-skill-align-and-update` **creates** the rule and registry in `docs/` → the
    `docs/` front's `index.md` and `log.md` must list them.
  - `quenching-docs-align-and-update`'s **harness** stage moves a fact into `docs/` that the
    `specs/` front's plans should now cite from `docs/` instead of restating.
  A single pass would leave every one of those half-done. The loop is the point.
- **One OK for the whole repo; authorization nests one level.** The gate fires **once**, before
  Pass 1. Each front conductor **inherits** it and passes it down verbatim to its stages — it
  does not ask again ([convergence.md](references/convergence.md) §Nesting). After that OK, the
  only possible interruptions are the two the contract never covers: a **code-coupled** rename,
  and a **change archive**.
- **Conduct, never reimplement.** Two levels of delegation, zero re-derived logic. If a front's
  behavior must change, change that front's conductor; if a stage's must, change that stage.
- **Front presence decides the pass.** An absent `docs/` bundle is what this plugin installs, so
  Front 1 always runs. An absent `specs/` is an explicit opt-in line in the plan — scaffolding
  it imposes a spec-driven workflow. An empty `.claude/` surface skips Front 3 with a
  note.
- **Converge or report — never spin.** Cross-front pass cap **3** (each front conductor keeps its
  own internal cap of 5). An empty pass with residual findings is **residue**: stop, and report it
  front by front with the skill that owns each item.

## Workflow (probe → ONE OK → three fronts → re-assess → loop)

### 1. Probe the three fronts (read-only, cheap)
Presence and rough scale only — each front conductor does its own full assessment:
- **docs/** — bundle root present? Run
  `${CLAUDE_PLUGIN_ROOT}/assets/hooks/okf-validate.py <docs> --json`; note finding counts, whether
  the project memory dir (`~/.claude/projects/<cwd>/memory/`) holds files, and which harness files
  exist.
- **specs/** — root present? `specs.py list --json` for change count and how many read complete;
  `Glob` `specs/backlog/*.md` for task count.
- **.claude/** — `Glob` the skills and commands; count them and the legacy `openspec-*` shadow copies.
**Done when:** each front is marked *present / absent / not applicable* with its counts, and
nothing has been written.

### 2. Present the RUN plan → gate on ONE OK (once, before Pass 1)
One table: front · state · which of its stages have work (counts and scope, **not** full diffs).
Name the specs changes proposed for archiving. An absent `specs/` appears as its own opt-in
line. State explicitly: *"this authorizes up to 3 cross-front passes of every stage below; each
front conductor inherits this OK and will not ask again; only a rename touching product code and
each change archive still confirm on their own."* Wait for **one** OK.
**Done when:** the user has answered; declined → nothing written, run ends.

### 3. Front 1 — `quenching-docs-align-and-update` (the `docs/` front)
Invoke via the **Skill** tool, declaring the authorization mode verbatim per
[convergence.md](references/convergence.md) §cycle-authorization, naming *this* conductor as the
grantor. It loops the `docs/` front to its own fixpoint. Record what it changed and its residue.
A hard failure here (the bundle could not be established) **stops the run** — the other two fronts
write into the bundle.
**Done when:** the front conductor has finished and its outcome is recorded.

### 4. Front 2 — `quenching-specs-align-and-update` (the `specs/` front)
Skip if the front is absent and the scaffold line was declined. Otherwise invoke it with the same
declaration. Record its
counts, **which changes were archived** (their distillations are the main cross-front feed into
Front 1's next pass), and its report-only residue verbatim. A failure here is **reported, not
fatal** — Front 3 still runs.
**Done when:** the front conductor has finished or been skipped with a stated reason.

### 5. Front 3 — `quenching-skill-align-and-update` (the `.claude/` front)
Skip if the surface is empty. Otherwise invoke it with the same declaration. Record its counts and
its doctrine findings (report-only, routed to `/skill:new`).
**Done when:** the front conductor has finished or been skipped with a stated reason.

### 6. Re-assess across fronts → decide (loop or stop)
Re-run the Step 1 probe **plus** a check of the specific cross-front edges: did Front 2 archive
anything (→ new `docs/` content for Front 1's glossary stage)? did Front 3 create the rule or
registry (→ `docs/` listings to regenerate)? Then:
- **Any front changed something** → run another cross-front pass (back to Step 3) under the same
  authorization, narrating what each front will do this time. Fronts whose input is unchanged
  will report "nothing to do" and cost one assessment each.
- **No front changed anything AND all three verify clean** → **converged.** Go to Step 7.
- **No front changed anything BUT findings remain** → **residue.** Stop; do not spin.
- Respect the cross-front **pass cap of 3**.
**Done when:** the loop has stopped for a stated reason.

### 7. Consolidated report + one log entry
One report, front by front: passes run, what each front's stages did in total, its ending verify
state (validator findings · doctor/validate · registry-vs-disk), and — explicitly — everything
**deferred**, each with the command that closes it (`/docs:add`, `/docs:learn`, `/specs:plan:update`,
`/specs:plan:propose`, `/skill:new`). Name the cross-front edges that actually fired, so the loop's
value is visible. Append **one** entry to `docs/log.md` per **Appending to `log.md`** in
[../quenching-docs-add/references/homes.md](../quenching-docs-add/references/homes.md):
`**Update**: [Repository](/docs/index.md) — aligned and updated all fronts in N passes
(docs/specs/skills); M deferred`.
**Done when:** every front's outcome and every deferral is stated, and the entry is written.

## Invariants to never violate

- Never run the fronts out of order, and never continue when Front 1 failed to establish the
  bundle the other two write into.
- Never ask for a second authorization, and never let a front conductor re-gate — authorization
  nests one level ([convergence.md](references/convergence.md) §Nesting). Equally, never suppress
  the two interruptions the contract never covers: code-coupled renames and change archives.
- Never reimplement a front's or a stage's logic here — **invoke** the front conductor via the
  Skill tool, always.
- Never act on a front's reported residue (archiving a declined change, minting a skill, writing
  a standard) — carry it into the report and name the skill that owns it.
- Never scaffold `specs/` without its own explicit line in the plan, and never scaffold a
  `.claude/` taxonomy for an empty surface.
- Never loop past the cross-front pass cap of 3, and never re-run a pass that just changed
  nothing.
- Never hand this SKILL.md `context: fork` — the gate and every nested confirmation are mid-flow.
