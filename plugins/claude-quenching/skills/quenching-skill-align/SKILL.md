---
name: quenching-skill-align
description: >-
  Sweeps a target repo's existing automation surface — .claude/skills/,
  .claude/commands/, and directory-scoped **/.claude/skills/ — and migrates it to the
  single taxonomy axis in ONE consolidated plan applied on a single confirmation. Use
  when the user asks to "organize the skills", "migrate the skills to the taxonomy",
  "align the commands to the monorepo", "clean up .claude/skills", or "standardize the
  automation surface". Read-only inventory first (name, axis classification, conformance
  gaps per item), then one plan — renames to canonical names, mirrored wrappers to create
  or rewrite, the taxonomy rule and the registry created from the templates when missing
  — with a code-coupled rename confirmed individually; skill bodies are preserved (MERGE),
  an unclassifiable skill is kept and reported, and nothing is deleted without the human
  stating it is obsolete. After applying it regenerates the registry's GENERATED zone and
  verifies every wrapper resolves and the registry matches .claude/skills/ exactly. Not
  for: creating or editing ONE skill → quenching-skill-new; aligning the docs/ bundle itself
  → quenching-docs-align; the specs/ front → quenching-specs-align; all three fronts at
  once → quenching-align-all; also auditing every body against the doctrine, looped →
  quenching-skill-align-and-update.
when_to_use: >-
  migrating a repo's whole existing skill/command surface to the taxonomy in one plan →
  one OK. The per-item mint/edit is quenching-skill-new.
allowed-tools: Read, Grep, Glob, Bash, Write, Edit
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
- **The registry ends the run honest.** The GENERATED zone is regenerated from the
  post-migration surface and verified against `.claude/skills/` before the run ends;
  residue is reported, never silently dropped.

## Workflow

### 1. Inventory the surface (read-only)
`Glob` `.claude/skills/*/SKILL.md`, `.claude/commands/**/*.md`, and directory-scoped
`**/.claude/skills/*/SKILL.md`. Set aside every legacy `openspec-*` skill and `opsx/` wrapper —
they are `quenching-specs-align`'s (Doctrine §the legacy `openspec-*` surface); list them as *out of
scope, owned by `/specs:align`* and drop them from the working set. For each remaining item record:
current name, axis classification
per the test ([taxonomy](../quenching-skill-new/references/taxonomy.md) §axis — several
unrelated folders → unroutable), and its gaps (non-canonical name, missing or wrongly
nested wrapper, a generic skill mirrored under a folder path, description over the cap or
without triggers, missing frontmatter). Read `docs/standards/automation/skills.md` if
present — it governs; note whether the rule and the registry
(`docs/documentation/reference/automation.md`) exist, and whether `docs/index.md` carries
`okf_version` (no bundle → rule/registry stay out of scope, migration still applies).
**Done when:** the inventory table (item · classification · gaps) is complete and no file
changed.

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
the molds when missing (rule born `authority: background`), the operator manual
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
confirmed rename, and install the operator manual from
`${CLAUDE_PLUGIN_ROOT}/assets/claude/QUENCHING.md` to `.claude/QUENCHING.md` under the
four-branch manual-install rule in
[../quenching-docs-align/SKILL.md](../quenching-docs-align/SKILL.md) §4 (cited, never restated).
**Done when:** every confirmed row is applied.

### 5. Verify and report
Regenerate the registry's GENERATED zone from the post-migration
`.claude/skills/*/SKILL.md` frontmatter ([taxonomy](../quenching-skill-new/references/taxonomy.md)
§registry). Then verify: every command wrapper resolves to an existing skill (a dangling
wrapper is fixed to the new name, or reported if ambiguous); the zone matches
`.claude/skills/` exactly; every renamed reference site compiles/greps clean. In an OKF
repo, append ONE consolidated `log.md` entry (the migration, with counts) and confirm the
registry is indexed, per
[../quenching-docs-add/references/homes.md](../quenching-docs-add/references/homes.md).
Report: renamed / wrappers created / flattened / rule+registry created / unroutable /
flagged. **Done when:** registry, wrappers, and skills agree, and the counts are reported.

## Invariants

- Never modify anything before the plan's OK; a code-coupled rename never rides the batch. A
  cycle-authorized run replaces only the batch gate with narration — never a code-coupled
  item's own OK.
- Never rename, reclassify, or remove a legacy `openspec-*` skill or an `opsx/` wrapper — that
  surface is `quenching-specs-align`'s; note it and move on.
- Never alter a skill body — only names, placement, and frontmatter conformance.
- Never delete a skill without the human stating it is obsolete; never force an
  unroutable item onto the axis.
- Never leave the GENERATED zone stale — regenerate and verify before the run ends.
- Never overwrite a `.claude/QUENCHING.md` whose `claude-quenching` banner a human removed —
  keep it and report it.
- Never hand this SKILL.md `context: fork` — both gates are mid-flow.
