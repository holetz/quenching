---
description: Align the whole repository — /docs/, /.design/, then .claude/, ops and proof — on ONE confirmation, looping until nothing changes. Triggers on "align the repo", "align everything", "align and update everything", "set up quenching here", "converge this repository", "run all the aligns", "fix both fronts", or "fix all fronts". Not for: aligning one front → its `/quenching:*:align` command; changing product code → the owning spec.
argument-hint: [optional-scope]
allowed-tools: Read, Grep, Glob, Bash(python3:*), Bash(py:*), Skill
---

# /align — one confirmation, the whole repository

**Input**: `$ARGUMENTS` (an optional scope; omit to align the whole repository).

## Execution order

This table is the **one executable declaration** of the local-front order. The `Depends on`
column is a dependency edge, not a display ordinal: a later front is never invoked before the
front named in that cell has completed its inherited authorization.

| Front | Route | Depends on |
| --- | --- | --- |
| `knowledge` — `/docs/` | `/quenching:knowledge:align` | applicability |
| `design` — `/.design/` | `/quenching:design:align` | `knowledge` |
| `components` — `.claude/` | `/quenching:components:align` | `design` |
| `ops` — operations surface | `/quenching:ops:align` | `components` |
| `proof` — verification surface | `/quenching:proof:align` | `ops` |

The `specs` provider flow and the `git` pillar have no row: neither owns a local tree that this
conductor converges. Their commands remain available through their own namespaces.

Every applicable front must expose the common front mold at
`${CLAUDE_PLUGIN_ROOT}/assets/references/front-align/mold.md`. The conductor sequences and reports;
it never reimplements a front's verifier or repair logic.

## Workflow

### Applicability

Probe every declared front in the table before inventory. If `$ARGUMENTS` names a front or a path
inside one, probe only that front and mark the others skipped by scope.

- **`knowledge`** — run `cq knowledge validate /docs --json`; record the bundle, validator counts,
  project memory and harness files.
- **`design`** — run `cq --root . design status --json` when installed; when absent, run
  `design align --check --json` only when scope or root `PRODUCT.md`/`DESIGN.md` artifacts signal
  adoption.
- **`components`** — run `cq components doctor --json`; inspect command skills for legacy pairs.
- **`ops`** — read `.claude/quenching.json` for `ops.opsRoot`; when absent, inspect only
  `scripts/`, `tools/`, `bin/` and `script/` for an executable entry point.
- **`proof`** — read `.claude/quenching.json` for `proof.proofRoot`; when absent, inspect only
  `tests/` and `test/` for a test module.

Use **not applicable** only when the probe found no declared root or conventional signal. Use
**skipped** only for explicit scope exclusion or an earlier hard failure. A present front with no
findings is **conformant**.

If all applicable fronts are conformant, report *"all applicable fronts conformant — nothing to
align"* and stop before presenting a plan. An applicable but undeclared `ops` or `proof` front is
adoption work, not drift, until its own align is invoked.

### Authorization

Present one short plan: front, state, work in its content stages, counts and scope, plus skipped
fronts and their reasons. State plainly:

> This authorizes up to 3 cross-front passes of every stage below; each front align inherits this
> OK and will not ask again. Taste arbitration, a rename touching product code and each spec's
> close-out still require their own human choice.

Wait for one OK. A decline writes nothing.

### Front: `knowledge`

Invoke `/quenching:knowledge:align` through the Skill tool under its registry name, with the
inherited authorization:

> Running under `/align` authorization granted at run start — skip your plan-confirmation pause;
> present your plan as narration and execute; code-coupled and irreversible items still gate
> individually.

The knowledge align loops the `/docs/` bundle to its own fixpoint. Record its changes and residual
validator findings. A hard failure establishing the bundle stops the conductor because later fronts
write into or depend on it.

### Front: `design`

When `/.design/` is absent and neither scope nor portable artifacts signal adoption, report this
front not applicable. Otherwise invoke `/quenching:design:align` with the inherited authorization.
Product truth and design standards land in the knowledge bundle; source arbitration and visual taste
remain human choices. A hard failure establishing valid DTCG stops later fronts.

### Front: `components`

When the automation surface is empty, skip it rather than scaffolding a taxonomy. Otherwise invoke
`/quenching:components:align` with the inherited authorization after `design` has completed. Its
rule and registry changes belong to the knowledge bundle; its doctrine findings remain report-only.

### Front: `ops`

When the applicability probe finds no operations signal, report `ops` not applicable. Otherwise
invoke `/quenching:ops:align` after `components`, with the inherited authorization. Its inventory
and registry feed the proof front's conditional entry-point check.

### Front: `proof`

When the applicability probe finds no proof signal, report `proof` not applicable. Otherwise invoke
`/quenching:proof:align` after `ops`, with the inherited authorization. It consumes the operations
inventory when configured and reports its own layer and gate residue; it never runs a target suite.

### Re-probe and convergence

Re-run the applicability probes and cross-front edges after a pass. Check whether design added
product/design standards, components changed the automation registry, ops changed the operations
inventory or registry for `/docs/`, or proof gained resources for generated listings. A changed edge
justifies another pass under the same authorization; an unchanged pass with residue is residue, not
a reason to spin. Stop at convergence, residue, or the cap of 3 cross-front passes.

### Report

Report passes, each front's ending verifier state, validator/doctor findings, registry-vs-disk state,
cross-front edges that fired, and every deferred decision with its owning command. This conductor
writes nothing of its own; each front owns its writes and its report is the account of its run.

## Invariants

- Never run a front before its dependency in the declaration table has completed.
- Never ask for a second authorization or suppress an interruption the front contract still owns.
- Never reimplement a front's stages, verifier or repairs here; invoke its align through Skill.
- Never act on residue owned by `/quenching:knowledge:add`, `/quenching:knowledge:learn`,
  `/quenching:knowledge:define`, `/quenching:specs:develop`, `/quenching:specs:conclude`,
  `/quenching:design:genre:new`, or `/quenching:components:command:new`.
- Never scaffold an empty `.claude/` surface or silently install a visual world.
- Never loop past 3 passes or widen scope to force a clean number.
- Never hand this command `context: fork`; the gate and nested confirmations are mid-flow.
