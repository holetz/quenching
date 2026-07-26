---
name: quenching-skill-align
description: >-
  Sweeps a target repo's existing automation surface — .claude/skills/,
  .claude/commands/, and directory-scoped **/.claude/skills/ — and migrates it to the
  single taxonomy axis in ONE plan on a single confirmation. Use
  when the user asks to "organize the skills", "migrate the skills to the taxonomy",
  "align the commands to the monorepo", "clean up .claude/skills", or "standardize the
  automation surface". Read-only inventory first (skills.py doctor + lint, plus the axis no
  tool decides), then ONE plan — renames, mirrored wrappers, the taxonomy rule and registry
  from the molds when missing — a code-coupled rename confirms on its own; bodies are
  preserved (MERGE), an unclassifiable skill kept and reported, nothing deleted without the
  human's word. Not for: editing ONE skill → quenching-skill-new; the docs/ bundle
  → quenching-docs-align; the specs/ front → quenching-specs-align; all three fronts at
  once → quenching-align-all; also auditing every body against the doctrine, looped →
  quenching-skill-align-and-update.
when_to_use: >-
  migrating a repo's whole existing skill/command surface to the taxonomy in one plan → one OK.
allowed-tools: Bash(python3:*), Bash(py:*), Bash(git grep:*), Bash(grep:*), Bash(mkdir:*), Bash(mv:*), Bash(cp:*), Read, Grep, Glob, Write, Edit
user-invocable: false
---

# quenching-skill-align — force the automation surface onto the taxonomy

The sweep counterpart of `quenching-skill-new`: where the mint keeps each **new** skill
conformant, this skill converges everything that **already exists**. The axis, naming,
mirroring, and registry format live in
[../quenching-skill-new/references/taxonomy.md](../quenching-skill-new/references/taxonomy.md);
the writing doctrine judged against is
[../quenching-skill-new/references/doctrine.md](../quenching-skill-new/references/doctrine.md) —
both owned by the sibling and cited here, never restated. Molds live at
`${CLAUDE_PLUGIN_ROOT}/assets/templates/automation/`.

## Doctrine

The sweep contract every align shares — read-only inventory first, one plan → one OK with
code-coupled items gating individually, the cycle-authorized narration exception, the two-scan
blast-radius procedure, MERGE-never-clobber, never-delete-on-a-guess, and
align-conformance-report-the-cycle — lives once in
[../quenching-align-all/references/sweep-doctrine.md](../quenching-align-all/references/sweep-doctrine.md).
Read it as this skill's doctrine. What follows is only what is **specific to `.claude/`**:

- **The legacy `openspec-*` surface is not this sweep's.** `.claude/skills/openspec-*/` and
  `.claude/commands/opsx/` are legacy CLI artifacts a prior `openspec init` left behind — a
  native `specs/` repo has none. When present they belong to `quenching-specs-align`, which
  removes them when migrating a legacy `openspec/` workspace
  ([../quenching-specs-align/references/conformance.md](../quenching-specs-align/references/conformance.md)
  §Shadow copies). Inventory them only to **note** them; never classify them onto the axis,
  rename them, or remove them here.
- **A skill body is never rewritten here.** The shared MERGE rule says bodies are preserved;
  on this front that is the whole point — only names, placement, and description/frontmatter
  conformance change. Auditing a body against the writing doctrine is
  `quenching-skill-align-and-update`'s second stage, not this sweep's.
- **The registry ends the run honest.** `skills.py registry reindex` regenerates the GENERATED
  zone from the post-migration surface, and a second run reporting `changed: false` is what
  proves it matches disk; residue is reported, never silently dropped.

## Resolving the tool

Resolve `skills.py` the way the `specs/` front resolves `specs.py`:
`${CLAUDE_PLUGIN_ROOT}/assets/bin/skills.py` first, then a copy installed into the target's
`.claude/hooks/skills.py`, else the declared **manual** fallback — apply the same checks by hand
and **say in the report that the check was manual**, never silently skip it. Invoke with
`python3`/`py`; branch on the **exit code** (0 ok · 1 findings · 2 refusal) and the `--json`,
never on prose.

**This sweep also installs it** (Step 4), so the repo keeps its verifier after the run ends —
one align per front, each installing its own front's tool.

**Every shell grant is scoped**, per
[`docs/standards/automation/skills.md`](../../../../docs/standards/automation/skills.md)
§`allowed-tools` is always scoped: `python3`/`py` for the tool, `git grep` and `grep` for the
blast-radius sweep (Step 2), `mkdir`/`mv`/`cp` for the renames and the two installs. This skill
touches no repo toolchain, so it has no claim to an unscoped `Bash`.

**What the tool decides, and what it does not.** `doctor` and `lint` decide everything mechanical
— the bijection, names, mirroring, the caps, trigger position, the `Not for:` boundary, body
length, step criteria, unscoped `Bash`. Neither decides the **axis**: naming the one folder a
skill acts on is a claim about what the skill is *for*, which no parser makes. Classification
stays a read.

## Workflow

### 1. Inventory the surface (read-only)
Ask the tool for the mechanical half — it reads nothing this skill would not, and it reports
what a reader would otherwise have to hold in their head:
```bash
skills.py doctor --json   # bijection, non-canonical names, collisions, unmirrored wrappers
skills.py lint --json     # per-skill conformance, one sk-* code per gap
```
`Glob` for what a single-root view does not reach: directory-scoped
`**/.claude/skills/*/SKILL.md` (an accepted variation, classified in place). Set aside every
legacy `openspec-*` skill and `opsx/` wrapper — they are `quenching-specs-align`'s (Doctrine §the
legacy `openspec-*` surface); list them as *out of scope, owned by `/specs:align`* and drop them
from the working set, including from the tool's findings.

Then add the half the tool cannot: for each remaining item, the **axis classification** per the
test ([taxonomy](../quenching-skill-new/references/taxonomy.md) §axis — several unrelated folders
→ unroutable). Read `docs/standards/automation/skills.md` if present — it governs; note whether
the rule and the registry (`docs/documentation/reference/automation.md`) exist, and whether
`docs/index.md` carries `okf_version` (no bundle → rule/registry stay out of scope, migration
still applies).
**Done when:** `doctor` and `lint` have run, the inventory table (item · classification · `sk-*`
gaps) is complete, and no file changed.

### 2. Sweep the blast radius
Run the shared procedure in
[../quenching-align-all/references/sweep-doctrine.md](../quenching-align-all/references/sweep-doctrine.md)
§3 — two repo scans for the whole rename set, never two per rename — over every name slated for
rename: skill names **and** command paths. **This front's delta:** a command path appears in
prose (`/foo:bar` in a README, a runbook, a CI comment) far more often than in code, so a hit
that is only documentation is workspace-internal, while a hit in a script that *invokes* the
command is code-coupled.
**Done when:** each planned rename is marked coupled or free, with its hits.

### 3. Present ONE consolidated plan → gate
One table: renames (old → canonical new, coupled ones marked), wrappers to create or
rewrite (and wrongly mirrored generic skills to flatten), rule + registry creations from
the molds when missing (rule born `authority: background`), **the tool** `.claude/hooks/skills.py`
(install / upgrade / leave — Step 4), the operator manual
`.claude/QUENCHING.md` (install / refresh / leave), unroutables kept-and-reported
with reasons, obsolete-suspect flags (no deletion proposed without the human's word).
Wait for the single confirmation; code-coupled items each await their own.
**Done when:** the user has answered; declined → nothing written, run ends.

### 4. Apply
Execute the confirmed plan: rename skill folders, update each renamed skill's `name:`,
create/rewrite wrappers from `automation/command.md` (one sentence, Skill tool,
`$ARGUMENTS`), fix frontmatter gaps per the doctrine (description within the cap,
triggers second sentence — bodies untouched), write rule and registry from their molds
when planned, update each code-coupled reference site alongside its individually
confirmed rename.

**Install the front's tool**, so the repo keeps its verifier after this run ends: copy
**exactly** `${CLAUDE_PLUGIN_ROOT}/assets/bin/skills.py` into the target's `.claude/hooks/`
(never the directory recursively). If a copy is **already installed**, compare its version
(`python3 .claude/hooks/skills.py --version`) with the plugin's `VERSION` file and overwrite
**only** when the plugin is newer — the same rule `quenching-specs-align` applies to `specs.py`
and `quenching-docs-align` to `okf-validate.py`. A newer installed copy is left alone and
reported: it means the target is ahead of this plugin, which is a fact to state, not a
regression to force.

Then install the operator manual from
`${CLAUDE_PLUGIN_ROOT}/assets/claude/QUENCHING.md` to `.claude/QUENCHING.md` under the
four-branch manual-install rule in
[../quenching-docs-align/SKILL.md](../quenching-docs-align/SKILL.md) §4 (cited, never restated).
**Done when:** every confirmed row is applied, and `.claude/hooks/skills.py` is present at a
version at least the plugin's (or its being newer is reported).

### 5. Verify and report
Regenerate the zone, then let the tool judge the surface the migration produced:
```bash
skills.py registry reindex --json   # the zone, from the post-migration surface
skills.py doctor --json             # the bijection the migration just changed
skills.py lint --json               # the gaps the migration was supposed to close
skills.py registry reindex --json   # `changed: false` — the zone now matches disk
```
An `sk-dangling-wrapper` is repointed to the new name, or reported if ambiguous; every renamed
reference site greps clean. In an OKF repo, append ONE consolidated `log.md` entry (the
migration, with counts) and confirm the registry is indexed, per
[../quenching-docs-add/references/homes.md](../quenching-docs-add/references/homes.md).
Report: renamed / wrappers created / flattened / rule+registry created / unroutable / flagged,
and every `sk-*` finding that survived the run, by code. **Done when:** `doctor` and `lint` exit
0 or each surviving finding is named with its code, the second `registry reindex` reports
`changed: false`, and the counts are reported.

## Invariants

- Never modify anything before the plan's OK; a code-coupled rename never rides the batch. A
  cycle-authorized run replaces only the batch gate with narration — never a code-coupled
  item's own OK.
- Never rename, reclassify, or remove a legacy `openspec-*` skill or an `opsx/` wrapper — that
  surface is `quenching-specs-align`'s; note it and move on.
- Never alter a skill body — only names, placement, and frontmatter conformance.
- Never delete a skill without the human stating it is obsolete; never force an
  unroutable item onto the axis.
- Never leave the GENERATED zone stale, and never write inside its markers by hand — the run
  ends on a `registry reindex` that reports `changed: false`.
- Never overwrite a `.claude/QUENCHING.md` whose `claude-quenching` banner a human removed —
  keep it and report it.
- Never hand this SKILL.md `context: fork` — both gates are mid-flow.
