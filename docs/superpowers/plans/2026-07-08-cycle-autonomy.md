# Quenching-Cycle Autonomy Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `quenching-cycle` run to fixpoint with ONE human confirmation at cycle start (code-coupled gates preserved), and cheapen each pass by overlapping `quenching-harness`'s read-only discovery with `quenching-memory-to-docs`' execution.

**Architecture:** This repo's "source code" is prose — skill instructions a future Claude session executes literally. The cycle-authorization contract is defined ONCE in `quenching-cycle/references/cycle.md` (the owner); each of the 4 sub-skills gets a one-sentence exception citing it (never restating the logic). Parallelization is "plan in parallel, write in series": only harness's read-only steps 1–4 run in a background Task agent; all `docs/` writes stay one-stage-at-a-time.

**Tech Stack:** Markdown skill files (prose-as-code), two stdlib-only Python scripts (version constants only), JSON manifests.

**Spec:** `docs/superpowers/specs/2026-07-08-cycle-autonomy-design.md` (approved). Decision IDs (D1–D11) referenced below come from its §2 table.

## Global Constraints

- No test suite exists. Verification = exact commands in each task (validator run, `--version` checks, `wc -c` / `wc -l` counts, grep coherence sweeps). Run them; do not skip.
- Every edited `SKILL.md` frontmatter `description` must stay **under 1,536 characters** (Claude Code truncates beyond it).
- Every skill body must stay **under 500 lines**.
- **Never add `context: fork` to any skill** (hard repo rule).
- Shared procedure lives ONCE in its owner (`cycle.md`); sub-skills cite `cycle.md` — never restate contract logic.
- Code-coupled confirmations are NEVER suppressed, in any wording you write (D2).
- Version bump: 0.9.0 → **0.10.0**, in lockstep across `plugin.json`, `VERSION`, `marketplace.json`, and the `VERSION` constants in `okf-validate.py` + `okf-visualize.py` (D11).
- All file paths below are relative to the repo root `/home/unicred/Projetos/claude-quenching`.
- Edits are exact-string replacements (Edit tool semantics): old text must match verbatim, including indentation.
- Commit after each task. Commit messages end with `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`.

---

### Task 1: cycle.md — the cycle-authorization contract + parallel-prep pipeline

The owner file. Everything else (Tasks 2–5) cites what this task creates, so it lands first.

**Files:**
- Modify: `plugins/claude-quenching/skills/quenching-cycle/references/cycle.md`

**Interfaces:**
- Produces: section heading `## The cycle-authorization contract` and subsection heading `### Parallel prep: overlap harness discovery with the memory drain` — Tasks 2–5 cite these as "cycle.md §contract" and "cycle.md §Parallel prep". Do not rename them.

- [ ] **Step 1: Add the parallel-prep subsection to the pass-pipeline section**

In `plugins/claude-quenching/skills/quenching-cycle/references/cycle.md`, find this exact text (end of the `## The pass pipeline` section):

```markdown
Re-validation is implicit: Stage 1 runs `okf-validate.py` as its own Step 5, and the cycle
re-runs the checker in its re-assessment (SKILL.md Step 5). A stage the assessment found empty is
**skipped** this pass — the chain is "each applicable stage in order," not "all four every pass."
```

Replace with (original paragraph kept, subsection appended):

```markdown
Re-validation is implicit: Stage 1 runs `okf-validate.py` as its own Step 5, and the cycle
re-runs the checker in its re-assessment (SKILL.md Step 5). A stage the assessment found empty is
**skipped** this pass — the chain is "each applicable stage in order," not "all four every pass."

### Parallel prep: overlap harness discovery with the memory drain

When the assessment finds work for **both** content feeders in the same pass (Stages 2 AND 3
non-empty), the cycle overlaps Stage 3's read-only prefix with Stage 2's execution — plan in
parallel, write in series:

1. Stage 1 (`quenching-align`) completes first, as always.
2. The cycle dispatches **one read-only `Task` sub-agent in the background** (`model: sonnet` —
   MOVE/KEEP classification is real judgment, the same rationale as the assessment agent)
   instructed to execute steps 1–4 of `quenching-harness/SKILL.md` **as written there**
   (inventory, unit parse, classification, blast-radius sweep) and return the draft
   `file → unit → verdict → destination` table. The logic stays in its owner; the cycle only
   runs the read-only prefix ahead of schedule.
3. In parallel, the orchestrator runs `quenching-memory-to-docs` to completion, inline.
4. The cycle then invokes `quenching-harness`, handing it the pre-collected table **plus the
   list of docs Stage 2 just created**. Harness runs its **staleness delta-recheck** before
   writing: a doc Stage 2 landed can flip a unit's verdict from MOVE to **DEDUPE** (the fact
   now has a doc) — re-verify (a cheap `Grep` for coverage) only the units whose home/subject
   intersects the new docs; the rest of the table stands.
5. **Writes to `docs/` are one stage at a time, always** — harness's writes start only after
   memory-to-docs' writes have finished. Two stages read-modify-writing the same shared files
   (a home's `index.md`, `docs/log.md`, `knowledge/glossary.md`) is a race with no lock; the
   serial-write rule is an invariant, not an optimization choice.

When only ONE feeder has work, run it in the normal serial flow — dispatching a discovery agent
with nothing to overlap only costs tokens. The stages' own internal fan-outs (memory slice
classification, knowledge-scan home slices) are unchanged.
```

- [ ] **Step 2: Add the cycle-authorization contract section**

In the same file, find this exact text (the heading that follows the routing table):

```markdown
## The convergence contract
```

Replace with (new section inserted before it):

```markdown
## The cycle-authorization contract

The cycle asks for ONE human confirmation, at cycle start, that authorizes the entire run — up
to the pass cap or convergence. This section is the contract's single normative home: the four
stage skills cite it (each carries one exception sentence pointing here) and never restate it.

**What the authorization covers** — every routine write a stage performs: frontmatter stamps,
new concept docs, index/log/glossary entries, memory migration + deletion (after its
write-then-verify self-check), harness unit cuts (after theirs) — as long as it touches no
product code.

**What it NEVER covers** — any rename or edit whose blast radius reaches **product code** (a
path constant, an import, a docstring). A code-coupled item gates individually, always, exactly
as when the stage runs standalone. After the initial OK this is the only possible stop.

**What it does not change** — the stages' safe-write invariants (write-then-verify-then-delete
for memory, write-then-verify-then-cut for harness) do not depend on who authorized the run and
remain in force. Scope surprises do not re-gate: a later pass discovering more work than the
preview estimated proceeds under the same authorization, bounded by the pass cap and the
stages' own invariants.

**How the cycle signals the mode** — it declares, in the invocation of each stage: *"Running
under quenching-cycle authorization granted at cycle start — skip your plan-confirmation pause;
present your plan as narration and execute; code-coupled items still gate individually."* A
stage invoked WITHOUT this declaration (standalone) keeps its normal plan → OK gate.

**Narration replaces the gate, not the plan** — a cycle-authorized stage still presents its
full plan table before writing; the user watching the session sees everything and types
nothing.

## The convergence contract
```

- [ ] **Step 3: Verify the two anchors exist exactly once each**

Run:
```bash
grep -c '^## The cycle-authorization contract$' plugins/claude-quenching/skills/quenching-cycle/references/cycle.md
grep -c '^### Parallel prep: overlap harness discovery with the memory drain$' plugins/claude-quenching/skills/quenching-cycle/references/cycle.md
grep -c '^## The convergence contract$' plugins/claude-quenching/skills/quenching-cycle/references/cycle.md
```
Expected: `1`, `1`, `1` (one line each).

- [ ] **Step 4: Commit**

```bash
git add plugins/claude-quenching/skills/quenching-cycle/references/cycle.md
git commit -m "feat(cycle): cycle-authorization contract + parallel-prep pipeline in cycle.md

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 2: quenching-cycle/SKILL.md — one OK per cycle

**Files:**
- Modify: `plugins/claude-quenching/skills/quenching-cycle/SKILL.md`

**Interfaces:**
- Consumes: `cycle.md §contract` and `cycle.md §Parallel prep` headings from Task 1.
- Produces: nothing later tasks consume; this file's doctrine/workflow must agree with Task 1's contract wording.

- [ ] **Step 1: Update the frontmatter description**

Find this exact text (inside the `description:` block, lines 11–13 of the file):

```
  align/memory/harness/glossary end to end". Each pass: one read-only assessment, one OK,
  the applicable stages run in order under their own doctrines and confirmations,
  re-assess; stops at the fixpoint (every stage empty AND the validator clean), a pass
```

Replace with:

```
  align/memory/harness/glossary end to end". ONE OK at cycle start authorizes the whole
  run (code-coupled items still gate individually); each pass: one read-only assessment,
  the applicable stages run in order with plans narrated,
  re-assess; stops at the fixpoint (every stage empty AND the validator clean), a pass
```

- [ ] **Step 2: Verify the description stays under 1,536 characters**

Run:
```bash
python3 - <<'EOF'
import re
text = open('plugins/claude-quenching/skills/quenching-cycle/SKILL.md').read()
m = re.search(r'description: >-\n(.*?)\nwhen_to_use:', text, re.S)
desc = ' '.join(m.group(1).split())
print(len(desc), 'chars —', 'OK' if len(desc) < 1536 else 'OVER CAP: SHORTEN IT')
EOF
```
Expected: a number below 1536 followed by `OK`. If `OVER CAP`, shorten the description (cut example trigger phrases from the middle, never the "Not for:" boundary or the first two sentences) and re-run.

- [ ] **Step 3: Replace the "One OK per pass" doctrine bullet**

Find this exact text:

```markdown
- **One OK per pass; the pass is the unit.** Each pass is: read-only assessment → present **this
  pass's** plan (which stages run, what each touches, in counts) → **one OK** → run the stages in
  order → re-assess. The cycle **adds** a pass-level confirmation; it never **removes** a
  sub-skill's own. A code-coupled rename inside `quenching-align`/`quenching-harness` still
  surfaces as **its own** confirmation item — the sub-skill enforces that and the cycle must not
  suppress it.
```

Replace with:

```markdown
- **One OK per cycle; the cycle run is the unit.** The gate runs ONCE, before Pass 1: present
  the initial assessment (which stages have work, in counts) and ask for the OK that authorizes
  up to the pass cap of passes, under the cycle-authorization contract in
  [references/cycle.md](references/cycle.md) — later passes run without a gate, narrating their
  plan. The authorization absorbs each stage's routine plan pause; it never absorbs a
  **code-coupled** item: a rename inside `quenching-align`/`quenching-harness` whose blast
  radius reaches product code still surfaces as **its own** confirmation, always — the
  sub-skill enforces that and the cycle must not suppress it.
```

- [ ] **Step 4: Replace workflow Step 3 (the gate)**

Find this exact text:

```markdown
### 3. Present THIS pass's plan → gate on ONE OK
Show, in pipeline order, which stages will run this pass and what each will touch — **counts and
scope, not full diffs** (each sub-skill presents its own detailed plan when it runs). Flag that
any code-coupled rename inside `align`/`harness` will surface as its own confirmation item. Wait
for **one** OK. The OK authorizes running this pass's stages; it does **not** pre-authorize the
sub-skills' code-coupled items.
```

Replace with:

```markdown
### 3. Present the CYCLE plan → gate on ONE OK (once, before Pass 1)
Runs once per cycle, not per pass. Show, in pipeline order, which stages have work and what each
will touch — **counts and scope, not full diffs** (each sub-skill still presents its own
detailed plan, as narration, when it runs). State explicitly: *"this authorizes up to <pass cap>
passes running the stages below; any item that touches product code still pauses for its own
confirmation, always."* Wait for **one** OK — it grants the cycle-authorization contract
([references/cycle.md](references/cycle.md)) for the whole run; it does **not** pre-authorize
the sub-skills' code-coupled items. Later passes skip this step and only narrate their plan.
```

- [ ] **Step 5: Update workflow Step 4 (invocation + parallel prep)**

Find this exact text:

```markdown
### 4. Run the pass — invoke each applicable stage, in order
On OK, invoke the sub-skills via the **Skill** tool in dependency order, **skipping** any stage the
assessment found empty:
```

Replace with:

```markdown
### 4. Run the pass — invoke each applicable stage, in order
Invoke the sub-skills via the **Skill** tool in dependency order, **skipping** any stage the
assessment found empty and declaring the cycle-authorization mode to each
([references/cycle.md](references/cycle.md) §contract). When BOTH content feeders (stages 2 and
3) have work this pass, use the parallel-prep flow (cycle.md §Parallel prep): dispatch the
read-only harness-discovery `Task` agent in the background once stage 1 completes, run stage 2
inline, then hand stage 3 the pre-collected table plus stage 2's created-docs list for its
staleness delta-recheck — writes stay one stage at a time, always:
```

- [ ] **Step 6: Update workflow Step 5's loop-back (no re-gate)**

Find this exact text:

```markdown
- **Pass changed something** → loop back to Step 3 for the next pass. A fresh assessment may
```

Replace with:

```markdown
- **Pass changed something** → run the next pass (back to Step 4) under the same authorization —
  no new OK; narrate the new pass's stages and counts. A fresh assessment may
```

- [ ] **Step 7: Update the invariants**

Find this exact text:

```markdown
- Never suppress a sub-skill's own confirmation — above all a **code-coupled rename**. The cycle
  adds a pass-level OK; it never removes a stage's.
```

Replace with:

```markdown
- Never suppress a sub-skill's **code-coupled** confirmation. The cycle's single upfront OK
  absorbs the stages' routine plan pauses (cycle.md §contract) — it never absorbs a
  code-coupled item, and never widens to product code.
- Never let two stages write `docs/` concurrently — parallel prep is read-only; writes are one
  stage at a time (cycle.md §Parallel prep).
```

- [ ] **Step 8: Verify body length and internal coherence**

Run:
```bash
wc -l plugins/claude-quenching/skills/quenching-cycle/SKILL.md
grep -n 'One OK per pass\|pass-level OK\|pass-level confirmation' plugins/claude-quenching/skills/quenching-cycle/SKILL.md
grep -c 'cycle-authorization' plugins/claude-quenching/skills/quenching-cycle/SKILL.md
```
Expected: line count well under 500; the second grep returns **nothing** (no stale per-pass-OK language survives); the third returns ≥ 3.

- [ ] **Step 9: Commit**

```bash
git add plugins/claude-quenching/skills/quenching-cycle/SKILL.md
git commit -m "feat(cycle): one OK per cycle — gate once before pass 1, narrate later passes

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 3: Propagate the exception sentence to align, memory-to-docs, knowledge-scan

Three sub-skills, same pattern (D3): ONE exception sentence in the confirmation doctrine bullet + a short appendix on the matching invariant. Each cites `cycle.md §contract`; none restates logic. (`quenching-harness` is Task 4 — it has an extra handoff duty.)

**Files:**
- Modify: `plugins/claude-quenching/skills/quenching-align/SKILL.md`
- Modify: `plugins/claude-quenching/skills/quenching-memory-to-docs/SKILL.md`
- Modify: `plugins/claude-quenching/skills/quenching-knowledge-scan/SKILL.md`

**Interfaces:**
- Consumes: `## The cycle-authorization contract` heading in `quenching-cycle/references/cycle.md` (Task 1). All relative links below resolve from each skill's own directory: `../quenching-cycle/references/cycle.md`.

- [ ] **Step 1: quenching-align — doctrine exception**

In `plugins/claude-quenching/skills/quenching-align/SKILL.md`, find this exact text:

```markdown
- **Force with ONE confirmation.** Present the **complete** plan; a single OK executes the
  whole batch. **Exception:** a rename whose blast radius reaches **product code** (path
  constants, imports, docstrings) is a **distinct** confirmation item with its scope shown —
  **never** folded into the batch OK.
```

Replace with:

```markdown
- **Force with ONE confirmation.** Present the **complete** plan; a single OK executes the
  whole batch. **Exception:** a rename whose blast radius reaches **product code** (path
  constants, imports, docstrings) is a **distinct** confirmation item with its scope shown —
  **never** folded into the batch OK. **Exception — cycle-authorized runs:** invoked by
  `quenching-cycle` under its cycle-authorization contract
  ([../quenching-cycle/references/cycle.md](../quenching-cycle/references/cycle.md)), the plan
  is presented as narration, not a gate; a code-coupled item still confirms on its own, always.
```

- [ ] **Step 2: quenching-align — invariant appendix**

Find this exact text:

```markdown
- Never delete or rename without OK; code-coupled renames get their own confirmation. A slug
  translation and a cluster-fold are renames — same rule.
```

Replace with:

```markdown
- Never delete or rename without OK; code-coupled renames get their own confirmation. A slug
  translation and a cluster-fold are renames — same rule. A cycle-authorized run
  (cycle.md §contract) replaces only the batch gate with narration — never a code-coupled
  item's own OK.
```

- [ ] **Step 3: quenching-memory-to-docs — doctrine exception**

In `plugins/claude-quenching/skills/quenching-memory-to-docs/SKILL.md`, find this exact text:

```markdown
- **Plan first, execute on one confirmation.** Cover **every** memory, classify each, and present
  ONE table — every memory → its target home + doc path + whether it will be deleted. Execute the
  whole batch on a single OK. This is invasive (it writes docs **and** deletes memory); the user
  sees the full blast radius before anything moves.
```

Replace with:

```markdown
- **Plan first, execute on one confirmation.** Cover **every** memory, classify each, and present
  ONE table — every memory → its target home + doc path + whether it will be deleted. Execute the
  whole batch on a single OK. This is invasive (it writes docs **and** deletes memory); the user
  sees the full blast radius before anything moves. **Exception — cycle-authorized runs:**
  invoked by `quenching-cycle` under its cycle-authorization contract
  ([../quenching-cycle/references/cycle.md](../quenching-cycle/references/cycle.md)), the plan is
  presented as narration, not a gate — the write-then-verify-then-delete contract is unchanged.
```

- [ ] **Step 4: quenching-memory-to-docs — invariant appendix**

Find this exact text:

```markdown
- Never skip the single up-front plan+confirmation — this writes docs and deletes memory.
```

Replace with:

```markdown
- Never skip the single up-front plan+confirmation — this writes docs and deletes memory. A
  cycle-authorized run (cycle.md §contract) replaces the gate with narration; the plan is still
  presented in full and write-then-verify-then-delete still holds.
```

- [ ] **Step 5: quenching-knowledge-scan — doctrine exception**

In `plugins/claude-quenching/skills/quenching-knowledge-scan/SKILL.md`, find this exact text:

```markdown
- **Plan first, one confirmation.** Merge every slice into ONE consolidated list before any
  write (mirrors `quenching-align`/`quenching-memory-to-docs`'s posture).
```

Replace with:

```markdown
- **Plan first, one confirmation.** Merge every slice into ONE consolidated list before any
  write (mirrors `quenching-align`/`quenching-memory-to-docs`'s posture). **Exception —
  cycle-authorized runs:** invoked by `quenching-cycle` under its cycle-authorization contract
  ([../quenching-cycle/references/cycle.md](../quenching-cycle/references/cycle.md)), the
  consolidated plan is presented as narration, not a gate — this skill has no code-coupled
  items, so cycle-authorized means zero pauses.
```

- [ ] **Step 6: quenching-knowledge-scan — invariant appendix**

Find this exact text:

```markdown
- Never skip the single consolidated confirmation or present per-slice lists — every slice
  merges into ONE plan before any write.
```

Replace with:

```markdown
- Never skip the single consolidated confirmation or present per-slice lists — every slice
  merges into ONE plan before any write. A cycle-authorized run (cycle.md §contract) replaces
  the gate with narration but still merges everything into ONE presented plan.
```

- [ ] **Step 7: Verify the three files**

Run:
```bash
for f in quenching-align quenching-memory-to-docs quenching-knowledge-scan; do
  echo "== $f =="
  grep -c 'cycle-authorized' "plugins/claude-quenching/skills/$f/SKILL.md"
  grep -c 'quenching-cycle/references/cycle.md' "plugins/claude-quenching/skills/$f/SKILL.md"
  wc -l < "plugins/claude-quenching/skills/$f/SKILL.md"
done
```
Expected per file: `cycle-authorized` count = 2 (doctrine + invariant), link count ≥ 1, line count under 500.

- [ ] **Step 8: Verify each relative link resolves**

Run:
```bash
ls plugins/claude-quenching/skills/quenching-cycle/references/cycle.md
```
Expected: the path prints (it exists — all three skills link to it via `../quenching-cycle/references/cycle.md`, which resolves from `plugins/claude-quenching/skills/<skill>/`).

- [ ] **Step 9: Commit**

```bash
git add plugins/claude-quenching/skills/quenching-align/SKILL.md \
        plugins/claude-quenching/skills/quenching-memory-to-docs/SKILL.md \
        plugins/claude-quenching/skills/quenching-knowledge-scan/SKILL.md
git commit -m "feat(skills): cycle-authorized exception in align, memory-to-docs, knowledge-scan

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 4: quenching-harness — exception + pre-collected discovery handoff

Same exception pattern as Task 3, plus harness's extra duty (D8/D9): accept the cycle's pre-collected steps 1–4 table and delta-recheck it against docs created since collection.

**Files:**
- Modify: `plugins/claude-quenching/skills/quenching-harness/SKILL.md`

**Interfaces:**
- Consumes: `cycle.md §contract` and `cycle.md §Parallel prep` (Task 1). Relative link from this skill's dir: `../quenching-cycle/references/cycle.md`.

- [ ] **Step 1: Doctrine exception + handoff duty**

In `plugins/claude-quenching/skills/quenching-harness/SKILL.md`, find this exact text:

```markdown
- **Plan first, execute on one confirmation.** Read every harness file, classify every unit, and
  present **ONE** table — file → unit → verdict → destination. A single OK executes the batch; an
  edit whose blast radius reaches **product code** is its own confirmation item.
```

Replace with:

```markdown
- **Plan first, execute on one confirmation.** Read every harness file, classify every unit, and
  present **ONE** table — file → unit → verdict → destination. A single OK executes the batch; an
  edit whose blast radius reaches **product code** is its own confirmation item. **Exception —
  cycle-authorized runs:** invoked by `quenching-cycle` under its cycle-authorization contract
  ([../quenching-cycle/references/cycle.md](../quenching-cycle/references/cycle.md)), the plan is
  presented as narration, not a gate; a product-code edit still confirms on its own, always. The
  cycle may hand this skill a **pre-collected steps 1–4 table** (gathered read-only while
  `quenching-memory-to-docs` ran — cycle.md §Parallel prep); before writing, re-verify any unit
  whose home/subject intersects the docs that run just created — a fresh doc can flip a MOVE
  into a DEDUPE (the staleness delta-recheck); the rest of the table stands.
```

- [ ] **Step 2: Invariant appendix**

Find this exact text:

```markdown
- Never skip the single up-front plan + confirmation; a product-code edit confirms on its own.
```

Replace with:

```markdown
- Never skip the single up-front plan + confirmation; a product-code edit confirms on its own. A
  cycle-authorized run (cycle.md §contract) replaces the batch gate with narration — never the
  product-code item's own OK — and a pre-collected table is delta-rechecked before any write.
```

- [ ] **Step 3: Verify**

Run:
```bash
grep -c 'cycle-authorized' plugins/claude-quenching/skills/quenching-harness/SKILL.md
grep -c 'delta-recheck' plugins/claude-quenching/skills/quenching-harness/SKILL.md
wc -l < plugins/claude-quenching/skills/quenching-harness/SKILL.md
```
Expected: `2`, `2`, under 500.

- [ ] **Step 4: Commit**

```bash
git add plugins/claude-quenching/skills/quenching-harness/SKILL.md
git commit -m "feat(harness): cycle-authorized exception + pre-collected discovery delta-recheck

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 5: Root CLAUDE.md — keep the context:fork rule honest

The rule's rationale still holds (standalone runs still gate; code-coupled still pauses mid-flow), but "Every sweep skill gates on a mid-flow confirmation" would now lie for cycle-authorized runs. Reword without weakening the rule.

**Note:** `CLAUDE.md` is currently **untracked** in git (`?? CLAUDE.md` in status). Committing this task tracks the whole file for the first time — that is intended (the file is the project's checked-in instructions per its own header).

**Files:**
- Modify: `CLAUDE.md` (repo root)

**Interfaces:**
- Consumes: the §cycle-authorization heading name from Task 1 (cited in prose, not linked).

- [ ] **Step 1: Reword the fork rule**

In `CLAUDE.md`, find this exact text:

```markdown
- **Never add `context: fork` to these skills.** Every sweep skill gates on a mid-flow
  confirmation (one plan → one OK), which a forked context cannot present.
```

Replace with:

```markdown
- **Never add `context: fork` to these skills.** Every sweep skill gates on a mid-flow
  confirmation (one plan → one OK) when run standalone — and even a cycle-authorized run
  (`quenching-cycle/references/cycle.md` §cycle-authorization) must still surface code-coupled
  confirmations mid-flow, which a forked context cannot present.
```

- [ ] **Step 2: Verify**

Run:
```bash
grep -A3 'Never add .context: fork' CLAUDE.md
```
Expected: the new four-line wording, mentioning both "standalone" and "cycle-authorization".

- [ ] **Step 3: Commit (tracks CLAUDE.md for the first time)**

```bash
git add CLAUDE.md
git commit -m "docs: CLAUDE.md — fork rule wording covers cycle-authorized runs (first tracked commit of CLAUDE.md)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 6: Version bump 0.9.0 → 0.10.0 + full verification sweep

Lockstep bump (D11) across the five version carriers, then the whole spec-§6 verification suite.

**Files:**
- Modify: `plugins/claude-quenching/VERSION`
- Modify: `plugins/claude-quenching/.claude-plugin/plugin.json:3`
- Modify: `.claude-plugin/marketplace.json:13`
- Modify: `plugins/claude-quenching/assets/hooks/okf-validate.py:84`
- Modify: `plugins/claude-quenching/assets/tools/okf-visualize.py:45`

**Interfaces:**
- Consumes: nothing from other tasks (independent edits), but runs the final coherence sweep over Tasks 1–5's output, so it goes last.

- [ ] **Step 1: Bump the five version carriers**

1. `plugins/claude-quenching/VERSION` — replace entire content `0.9.0` with `0.10.0`.
2. `plugins/claude-quenching/.claude-plugin/plugin.json` — find `  "version": "0.9.0",` → replace with `  "version": "0.10.0",`.
3. `.claude-plugin/marketplace.json` — find `      "version": "0.9.0",` → replace with `      "version": "0.10.0",`.
4. `plugins/claude-quenching/assets/hooks/okf-validate.py` — find `VERSION = "0.9.0"  # kept in lockstep with the plugin VERSION file` → replace with `VERSION = "0.10.0"  # kept in lockstep with the plugin VERSION file`.
5. `plugins/claude-quenching/assets/tools/okf-visualize.py` — find `VERSION = "0.9.0"  # kept in lockstep with the plugin VERSION file` → replace with `VERSION = "0.10.0"  # kept in lockstep with the plugin VERSION file`.

- [ ] **Step 2: Verify lockstep**

Run:
```bash
cat plugins/claude-quenching/VERSION
python3 plugins/claude-quenching/assets/hooks/okf-validate.py --version
python3 plugins/claude-quenching/assets/tools/okf-visualize.py --version
grep '"version"' plugins/claude-quenching/.claude-plugin/plugin.json .claude-plugin/marketplace.json
```
Expected: every line shows `0.10.0`; no `0.9.0` remains in any of the five.

- [ ] **Step 3: Run the skeleton validator (untouched by this feature — must stay clean)**

Run:
```bash
cd plugins/claude-quenching && python3 assets/hooks/okf-validate.py assets/docs; cd ../..
```
Expected: `0 error(s), 0 warning(s)`, exit 0.

- [ ] **Step 4: Coherence sweep across all edited skills**

Run:
```bash
grep -rn 'cycle-authorized\|cycle-authorization' plugins/claude-quenching/skills/ | grep -v 'references/cycle.md'
```
Expected: hits ONLY in the five `SKILL.md` files (cycle, align, memory-to-docs, harness, knowledge-scan) — every hit is a citation (mentions `cycle.md` nearby), none redefines the contract's cover/never-cover terms (those live only in `references/cycle.md`). Manually eyeball each hit line: if any hit restates what the authorization covers, move that text into a citation.

- [ ] **Step 5: Confirm no `context: fork` crept in**

Run:
```bash
grep -rn 'context: fork' plugins/claude-quenching/skills/
```
Expected: no output.

- [ ] **Step 6: Commit**

```bash
git add plugins/claude-quenching/VERSION \
        plugins/claude-quenching/.claude-plugin/plugin.json \
        .claude-plugin/marketplace.json \
        plugins/claude-quenching/assets/hooks/okf-validate.py \
        plugins/claude-quenching/assets/tools/okf-visualize.py
git commit -m "chore: release 0.10.0 — cycle autonomy (one OK per cycle + parallel prep)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Post-implementation: manual sandbox rehearsal (spec §6.5 — not a plan task)

The prose changes can only be behaviorally validated by a live session. After merging, rehearse in a sandbox target repo (fixture with project memory + a fat `CLAUDE.md` + one planted code-coupled rename) and confirm:
(a) exactly 1 OK asked at cycle start; (b) passes 2+ run without stopping; (c) the planted code-coupled rename pauses even though authorized; (d) `quenching-harness` invoked standalone still asks its normal OK; (e) with work in both content feeders, the discovery agent dispatches in the background and harness delta-rechecks against the new docs. Any failure is a wording bug in the corresponding SKILL.md — fix the prose, not the process.
