# `scripts/` home — the executable logic invoked by the surface

> Part of the `quenching-management` evolution log. Index, anchor state, and backlog: [../README.md](../README.md). ID convention (R*/Rev*) and routing: [README.md](README.md).
>
> This file collects the rounds (`R*`) and revisions (`Rev*`) that touched the **canonical home of `scripts/`**: the organisation of **deterministic executable logic** at the repo level (build/deploy, generators, checks, maintenance, dev) that the knowledge surface invokes — the "common commands" of CLAUDE.md (dim 1), the scripts that hooks call (dim 8), those that commands/skills carry (dim 9), and what CI runs. **Anchor: dim 8** (hooks-call-scripts is the load-bearing doctrine), crossing dim 1/9.

## Current state

> Active summary of each boundary in this context (what is valid today). Detail and rationale are in the history below.

- **R35 · Canonical `scripts/` taxonomy** *(dim 8 + crosses dim 1/9)* — `scripts/`
  is a **first-class element** with canonical organisation **by PURPOSE**
  (`ci`/`<gen>`/`checks`/`maintenance`/`dev`), a disk-derivable README-map, and a
  single execution convention. **Single source:** [`scripts-taxonomy.md`](../../plugins/claude-quenching/skills/quenching-management/references/scripts-taxonomy.md)
  (sister of `docs-taxonomy.md`: that one governs knowledge, this one governs
  executables). **Strength difference vs. `docs/`:** the locked axis is the
  **PURPOSE** (there is one subfolder per purpose), not the **exact label** (`ci/`
  can be called `build/`) — derive the string from the repo, **lock the separation**.
  **Central boundary:** the **hook is THIN and CALLS the script** — the business
  logic (validate/generate/check) lives in `scripts/`, the hook is the trigger/adapter
  (official docs: *«a separate script file that the hook calls»* + *«use… `${CLAUDE_PROJECT_DIR}`
  to reference scripts»*). Other boundaries: repo-level `scripts/` × **skill-internal
  `scripts/`** (repo executable × skill executable) × `src/` (orchestration ×
  library). **CI-scope by purpose** is the decisive label of `dev/` (OUTSIDE linting)
  vs. the rest (inside). Facet in **dim 8** of the template (new "Canonical home of
  executable logic" block in "What good looks like" + 5 smells + detection +
  remediation + payload), with **cross-ref** in dim 1 ("common commands" are
  invocations of `scripts/`) and dim 9 (command/skill executable → the right
  `scripts/`). **Payload = ORGANISATION scaffold** [`assets/scripts/`](../../plugins/claude-quenching/skills/quenching-management/assets/scripts/)
  (README-map + purpose subfolders with only READMEs/placeholders `<...>`), **NEVER
  concrete scripts** — self-contained invariant: the package ships the structure, not
  the executables (which would couple to a repo). `scripts/` greps in block 8b
  **PENDING measurement vs. fixtures** (no Bash). 15 dimensions (dim 8 facet, not
  dim 16); no MEASURED detection rule changed → harness does not run. **Home where
  Round B (R36) materialised the consumer** — the Stop hook
  [`run-validation.py`](../../plugins/claude-quenching/skills/quenching-management/assets/hooks/run-validation.py) CALLS the `validateScript`
  from this home (`scripts/checks`/`ci`); ruff --fix + format + pyright as the
  documented example for a Python repo, generic runner. See [dim-08-hooks.md](dim-08-hooks.md)
  (R36).

## Round and revision history

> Complete entries (Change · Why · Sources · Rejected/not-done · Next candidate), most recent at the top. A revision (`Rev*`) is nested **under** the round it refines.

### R35 · Canonical `scripts/` taxonomy — the home of executable logic (dim 8 + crosses dim 1/9)

**Change.** Establishes in the methodology a **canonical, organised home for
`scripts/`** — the deterministic executables that the knowledge surface invokes —
as a first-class element, parallel to the `docs/` taxonomy. Concretely:

1. **New reference [`references/scripts-taxonomy.md`](../../plugins/claude-quenching/skills/quenching-management/references/scripts-taxonomy.md)**
   (single source, sister of `docs-taxonomy.md`): the canonical tree by **purpose**
   (`ci/` build&deploy + «X defines Y» · `<gen>/` derived-artifact generators ·
   `checks/` quality · `maintenance/` operational flags-off · `dev/` local tooling
   OUTSIDE linting); the **single execution convention** (derived from the repo —
   `python -m scripts.<package>.<module>` as the Python default, but can be
   `make`/`just`/`npm`); the **README-as-map** derivable from disk
   (module→what-it-does→entry per subfolder); and the **boundaries**: (a) repo-level
   `scripts/` × `.claude/hooks/*.py` — **the hook is THIN and CALLS the script**
   (the business logic lives in `scripts/`, the hook is the trigger); (b) repo-level
   `scripts/` × **skill-internal `scripts/`** (`.claude/skills/<n>/scripts/`) —
   repo executable × that skill's executable; (c) `scripts/` × `src/` (orchestration
   × library). Includes the existing-repo organisation doctrine (propose-move-with-OK,
   install only the purposes that apply) and the strength difference vs. `docs/`:
   locks the **purpose**, not the string.
2. **Facet in dim 8** of the template (`dimensions-template.md`): new "Canonical home
   of executable logic — `scripts/`" block in "What good looks like" (links the
   taxonomy, does not copy the tree — Simplicity First); 5 new smells (deterministic
   logic embedded in the hook that should be a script · script invoked by
   hook/command/CI that does not exist · scripts loose in the root / single bag
   without purpose · README-map lying vs. disk / diverging convention · repo
   executable in the wrong home); detection, remediation, and payload updated.
   **Cross-ref** in **dim 1** (CLAUDE.md "common commands" are invocations of
   `scripts/`; the map cites the single convention + link, the canonical home is
   dim 8) and in **dim 9** (command/skill executable → the right `scripts/`:
   skill-internal × repo).
3. **Portable scaffold payload** [`assets/scripts/`](../../plugins/claude-quenching/skills/quenching-management/assets/scripts/):
   template README-map + skeleton of purpose subfolders (`ci`/`checks`/`maintenance`/`dev`,
   each with only a README declaring the purpose + boundary + CI-scope), all with
   `<...>` placeholders and **NO concrete scripts** — like the `assets/docs/` scaffold.
4. **Propagation:** `assets/README.md` (inventory), `references/installation.md`
   (gap→payload), `references/detection-and-smells.md` (block 8b gained the `scripts/`
   greps: single-bag, script-in-root, hook-inline-logic, non-existent-script,
   no-map — PENDING measurement), `references/README.md` (folder index), References
   list of `SKILL.md`.

**Why.** The knowledge surface **is not just prose** — it invokes executables, and
the method's own doctrine says deterministic logic must live in **code**, not inline.
But until R34 the method **had no canonical organisation** for that logic: hook logic
could live embedded in `.claude/hooks/*.py` and the repo-level `scripts/`
(build/deploy/checks/maintenance/dev) was **invisible to the audit** — the method
audited only half the executable surface. The user asked for a first-class element
«with organisational directions like our docs» — a taxonomy parallel to that of
`docs/`. The target repo is **living proof** (it has `scripts/README.md` with exactly
that purpose-based organisation: `ci`/`catalog`/`checks`/`maintenance`/`dev`,
`python -m scripts.X` convention, README-map, «X defines YAML» and `dev/` outside
Ruff boundaries) — R35 **derives the portable form** from that without copying any
concrete script (which would couple to a repo).

**Dimension vs. facet decision (anti-inflation discipline).** As in R22/R33, did
**not** open «dimension 16»: `scripts/` is a facet of **dim 8** (hooks-call-scripts
is the load-bearing doctrine — it is what makes the home auditable: the thin hook
that calls the script is the direct link to the surface the method already audits),
crossing dim 1 (common commands) and dim 9 (command/skill executable). **15
dimensions maintained**. The canonical reference + the auditable facet (smells +
detection + remediation + payload) deliver the «first-class like docs» without
becoming a loose knob.

**Sources.**
- [Automate actions with hooks — Claude Code Docs](https://code.claude.com/docs/en/hooks-guide) — _official-anthropic · accessed 2026-06-29_. Load-bearing **thin-hook-calls-script** doctrine: *«This example uses a separate script file that the hook calls»* (section «Block edits to protected files»: the hook in `settings.json` invokes `.claude/hooks/protect-files.sh`); *«use absolute paths or `${CLAUDE_PROJECT_DIR}` to reference scripts»* (troubleshooting); *«Make the script executable: `chmod +x …`»*. Confirms that the business logic lives in a **separate script file** that the hook **calls**, not inline.
- [What Is SKILL.md in Claude Skills? Structure, Resources & Loading — Skywork.ai](https://skywork.ai/blog/ai-agent/claude-skills-skill-md-resources-runtime-loading/) — _community · accessed 2026-06-28_ (via [`research/01-agent-skills.md`](../research/01-agent-skills.md):185-188). Conventional Agent Skill layout: *«`scripts/` for executables»*, loaded on demand — anchors the **skill-internal `scripts/`** × repo-level `scripts/` boundary.
- Anchor for purpose-based organisation + execution convention + README-map + CI-scope: `scripts/README.md` of the **target repo** (living proof of the form to derive; not an external normative source — the portable form is derived, not the repo's paths).

**Rejected / not done.**
- **Dimension 16 «scripts»** — `scripts/` is a facet of dim 8 (crosses 1/9), not a new dimension (same discipline as R22/R33; 15 maintained).
- **Locking the NAMES of the subfolders** (as in `docs/`) — rejected: in `scripts/` the canonical axis is **purpose**, not the label (`ci/`≈`build/`, `checks/`≈`quality/`); locking the string would be rigidity without gain. The **purpose separation** is locked.
- **Shipping concrete scripts in the payload** (a real `ci/ruff.py`, a real `checks/…`) — **violates the self-contained/portable invariant** (would couple to a repo). The package ships only the template README/scaffold. A concrete validation runner is **Round B (R36)**, and even there it will be **generic/portable** (inert until the target wires `validateScript`), with ruff --fix + format + pyright as the **documented example** for a Python repo, never hardcoded.
- **Measured `scripts/` greps vs. fixtures** — written in block 8b but **PENDING measurement** (no Bash in this context, like R22-R29/R34). Entered in the review queue.
- **Script content quality criterion/smell** (test coverage, etc.) — out of scope: the method organises the **home** and audits the **wiring/boundary**, not the internal quality of each script (the repo's decision, like the content of each doc in `docs/`).

**Next candidate.** Hook validation payload triggered on edit/before-completion that
invokes the **validation script at the `scripts/checks` (or `ci`) home of the R35
taxonomy** — GENERIC/portable runner (inert until the target wires `validateScript`),
with ruff --fix + ruff format + pyright as the **documented example** for a Python
repo, never hardcoded. (This is **Round B (R36)** coupled to this one — the HOME is
already established here; what remains is the hook that stores the script in it.)
