---
name: quenching-skill-align-and-update
description: >-
  Aligns AND updates the .claude/ front: runs quenching-skill-align, then a
  read-only doctrine audit of every skill body, pass after pass, until a full pass changes
  nothing and the registry matches .claude/skills/ exactly. Use when the user asks to "align
  and update the skills", "bring the automation surface up to date", "audit the skills
  against the doctrine", "run the full skill cycle", or "tidy .claude end to end". Where
  quenching-skill-align only fixes NAMES, wrappers, and frontmatter, this also AUDITS each
  body against the writing doctrine — skills.py lint for the decidable half, a read for the
  rest — and reports every violation with the /skill:new invocation that fixes it, because
  rewriting a body is authoring, which needs a human. ONE OK at run start. Not for: names and
  wrappers only, one pass →
  quenching-skill-align; editing ONE skill → quenching-skill-new; the docs/ front →
  quenching-docs-align-and-update; the specs/ front → quenching-specs-align-and-update; all three →
  quenching-align-and-update-all.
when_to_use: >-
  aligning AND updating the .claude/ front — migration plus a doctrine audit of every body,
  looped until stable.
allowed-tools: Read, Grep, Glob, Bash, Write, Edit, Skill
user-invocable: false
---

# quenching-skill-align-and-update — align AND update the `.claude/` front

The **`.claude/` front's conductor**, peer of `quenching-docs-align-and-update` (`docs/`) and
`quenching-specs-align-and-update` (`specs/`). The name says what separates it from
`quenching-skill-align`: align fixes **names, wrappers, and frontmatter** and is bound by an
invariant never to alter a skill **body**; this conductor adds the audit of exactly that — every
body read against the writing doctrine, every violation reported with the invocation that fixes
it.

The cycle-authorization contract, the convergence condition, and the anti-spin guards are shared
with every conductor and live in
[../quenching-align-and-update-all/references/convergence.md](../quenching-align-and-update-all/references/convergence.md).
The doctrine the audit judges against and the taxonomy the migration applies live once, in
[../quenching-skill-new/references/doctrine.md](../quenching-skill-new/references/doctrine.md) and
[../quenching-skill-new/references/taxonomy.md](../quenching-skill-new/references/taxonomy.md) — cited
here, never restated. This front's pipeline is two stages, so it lives inline below rather than
in a `references/cycle.md`.

## The pass pipeline

| # | Stage | Concern | Auto-closes? |
| --- | --- | --- | --- |
| 1 | `quenching-skill-align` | **structure** — canonical names, mirrored wrappers, frontmatter conformance, the taxonomy rule and the registry, the GENERATED zone | **Yes** |
| 2 | doctrine audit (read-only, this skill) | **content** — every `SKILL.md` body judged against the writing doctrine | **No** — reported, routed to `/skill:new` |

**Why this front is honestly short.** The `docs/` and `specs/` fronts each have out-of-band
stores to drain (project memory, harness files, completed changes) — this one does not. Stage 1
is idempotent, so the front reaches a fixpoint in **1–2 passes**, essentially always. The loop is
not ceremony: a rename in Stage 1 shifts the registry and can dangle a wrapper, and re-assessing
catches that in the same run instead of leaving it for the next invocation. But this conductor
will not pretend to more work than the front has, and its report says so.

## Doctrine

- **Conduct, never reimplement.** Stage 1 is `quenching-skill-align` invoked via the Skill tool,
  under its own doctrine and its own confirmation for code-coupled renames. This conductor never
  renames a skill, writes a wrapper, or edits a registry zone itself.
- **Audit, never rewrite — and the tool does not change that.** Stage 2 gaining `lint` gains it a
  faster, more honest *reading*; it gains no write. A body that violates the doctrine is a
  finding, not a fix: rewriting it is **authoring**, and authoring needs the human whose intent
  the skill encodes. The report names the file, the violated rule (by `sk-*` code where the tool
  decided it), and the exact `/skill:new <name>` invocation that opens the edit. This is the same
  anti-fabrication boundary every conductor holds
  ([convergence.md](../quenching-align-and-update-all/references/convergence.md) §Per-item
  skills are stage tools).
- **One OK per run.** The gate fires once, before Pass 1, under the shared contract
  ([convergence.md](../quenching-align-and-update-all/references/convergence.md)
  §cycle-authorization). It absorbs Stage 1's routine plan pause; it never absorbs a code-coupled
  rename. Stage 2 writes nothing, so it needs no authorization at all.
- **The registry ends the run honest.** Convergence for this front is a set of exit codes, not a
  judgement: `registry reindex` reports `changed: false`, and `doctor` and `lint` exit 0 or each
  surviving finding is named in the report by its code.

- **The legacy `openspec-*` surface is not this front's.** `.claude/skills/openspec-*/` and
  `.claude/commands/opsx/` are legacy CLI artifacts that belong to `quenching-specs-align` (which
  removes them when migrating a legacy `openspec/` workspace) — Stage 1 already sets them aside,
  and the audit skips them too. A native `specs/` repo has none.

## Resolving the tool

Resolve `skills.py` the way the `specs/` front resolves `specs.py`:
`${CLAUDE_PLUGIN_ROOT}/assets/bin/skills.py` first, then a copy installed into the target's
`.claude/hooks/skills.py`, else the declared **manual** fallback — apply the same checks by hand
and **say in the report that the check was manual**. Invoke with `python3`/`py`; branch on the
**exit code** (0 ok · 1 findings · 2 refusal) and the `--json`, never on prose. Stage 2 runs it
**read-only**: `lint` and `doctor` write nothing, and `registry reindex` is Stage 1's to call.

## Workflow (one run OK → assess → pass → re-assess → loop)

### 1. Preflight — is there a surface to cycle?
`Glob` `.claude/skills/*/SKILL.md`, `.claude/commands/**/*.md`, and directory-scoped
`**/.claude/skills/*/SKILL.md`. If the surface is **empty** (no skills, no commands), stop and
say so — there is nothing to migrate and nothing to audit; scaffolding a taxonomy for zero skills
is ceremony. Note whether an OKF bundle exists (`docs/index.md` with `okf_version`); without one
the rule and registry stay out of scope, the migration still applies, and `quenching-docs-align` is
suggested once.
**Done when:** the surface is counted, the bundle's presence recorded, and nothing written.

### 2. Assess the pass (read-only)
Two lists, no sub-agents (the surface is small and each item is one file). Both halves of the
assessment start from the same two commands — the tool reads nothing this skill would not, and
running it here costs one call instead of a reader holding 30 files in their head:
```bash
skills.py doctor --json   # Stage 1's structural work, by sk-* code
skills.py lint --json     # the mechanically decidable half of Stage 2
```
- **Stage 1 work** — every `doctor` finding, plus a missing taxonomy rule or registry and a stale
  GENERATED zone (`registry reindex` reporting `changed: true`). Set aside every legacy
  `openspec-*` skill and `opsx/` wrapper as out of scope, including from the tool's findings.
- **Stage 2 findings** — `lint`'s per-body codes carry the decidable half: `sk-body-length`,
  `sk-step-criterion`, `sk-trigger-position`, `sk-no-boundary`, `sk-description-portable`,
  `sk-metadata-cap`. Then **read** each remaining body for what no parser can judge — the no-op
  test, sediment, sprawl, positive prescription, and whether shared procedure is cited rather
  than restated ([doctrine](../quenching-skill-new/references/doctrine.md)). A code and a read
  are different evidence and the report keeps them apart: a code names a threshold crossed, a
  read names a claim about behaviour.

If **both** lists are empty **and** `registry reindex` reports `changed: false` → already
converged, skip to Step 6.
**Done when:** `doctor` and `lint` have run, both lists are complete, and no file changed.

### 3. Present the RUN plan → gate on ONE OK (once, before Pass 1)
One table for Stage 1 (counts and scope — the sweep presents its own detailed plan as narration
when it runs), then, separately and labelled **"reported, not applied"**, the Stage 2 findings:
`skill · violated rule · one-line evidence · the /skill:new invocation that fixes it`. State
explicitly: *"this authorizes up to <pass cap> passes of the migration; the doctrine audit only
reports; a rename touching product code still confirms on its own."* Wait for **one** OK. Later
passes skip this step and only narrate.
**Done when:** the user has answered; declined → nothing written, run ends.

### 4. Run the pass
Invoke `quenching-skill-align` via the **Skill** tool, declaring the authorization mode verbatim
per [convergence.md](../quenching-align-and-update-all/references/convergence.md)
§cycle-authorization. Record what it reports it changed. Stage 2 requires no invocation — its
findings were produced read-only in Step 2 and carry forward to the report unchanged.
**Done when:** Stage 1 has finished or been skipped as empty.

### 5. Re-assess → decide (loop or stop)
Re-run the Step 2 assessment, then:
- **Pass changed something** → run the next pass under the same authorization. This is where a
  Stage 1 rename that dangled a wrapper or shifted the registry gets caught.
- **Pass changed nothing AND the registry matches disk AND every wrapper resolves** →
  **converged.** Go to Step 6.
- **Pass changed nothing BUT findings remain** → **residue** (doctrine violations, unroutable
  skills, obsolete-suspects awaiting the human's word). Stop; do not spin.
- Respect the **pass cap** (default 5) — this front should never approach it; if it does, say so,
  it means Stage 1 keeps producing follow-on work and that is worth reporting.
**Done when:** the loop has stopped for a stated reason.

### 6. Report + one log entry
Report: passes run; renamed / wrappers created / flattened / rule + registry created; the
verification triple as the tool stated it (`registry reindex` → `changed: false` · `doctor` exit
0 · `lint` exit 0, or each surviving code); and the **doctrine findings** — the `sk-*` codes and
the read-only judgements listed apart — each with its `/skill:new` invocation. Say
plainly when the front converged in one pass — that is the expected outcome here, not a
shortfall. In a repo with an OKF bundle, append **one** entry to `docs/log.md` per **Appending
to `log.md`** in
[../quenching-docs-add/references/homes.md](../quenching-docs-add/references/homes.md):
`**Update**: [Automation](/docs/documentation/reference/automation.md) — aligned and updated the
skill surface in N passes; M doctrine findings deferred`.
**Done when:** counts, the verification triple, and every deferred finding are reported.

## Invariants to never violate

- Never alter a skill **body** — Stage 2 is read-only, always. A doctrine violation is reported
  with its fix invocation, never rewritten in place.
- Never delete a skill without the human stating it is obsolete; never force an unroutable skill
  onto the axis.
- Never touch a legacy `openspec-*` skill or an `opsx/` wrapper — that surface is `quenching-specs-align`'s.
- Never suppress Stage 1's code-coupled confirmation, and never widen the run to product code.
- Never reimplement the migration here — **invoke** `quenching-skill-align` via the Skill tool.
- Never hand-edit inside the registry's GENERATED markers, and never end a run with the zone
  disagreeing with `.claude/skills/`.
- Never inflate the report: if the front converged in one pass with nothing to do, say exactly
  that.
- Never hand this SKILL.md `context: fork` — the run gate is mid-flow.
