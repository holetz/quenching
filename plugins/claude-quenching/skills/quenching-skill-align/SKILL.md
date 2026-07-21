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
  for: creating or editing ONE skill → quenching-skill; aligning the docs/ bundle itself
  → quenching-align.
when_to_use: >-
  migrating a repo's whole existing skill/command surface to the taxonomy in one plan →
  one OK. The per-item mint/edit is quenching-skill.
allowed-tools: Read, Grep, Glob, Bash, Write, Edit
user-invocable: false
---

# quenching-skill-align — force the automation surface onto the taxonomy

The sweep counterpart of `quenching-skill`: where the mint keeps each **new** skill
conformant, this skill converges everything that **already exists**. The axis, naming,
mirroring, and registry format live in
[../quenching-skill/references/taxonomy.md](../quenching-skill/references/taxonomy.md);
the writing doctrine judged against is
[../quenching-skill/references/doctrine.md](../quenching-skill/references/doctrine.md) —
both owned by the sibling and cited here, never restated. Molds live at
`${CLAUDE_PLUGIN_ROOT}/assets/templates/automation/`.

## Doctrine

- **Inventory first, read-only.** Nothing is created, renamed, or modified until the plan
  is confirmed — the inventory pass only records.
- **One plan, one OK; a code-coupled rename confirms on its own.** A rename whose current
  name is referenced by product code, CI, or scripts is its own confirmation item — the
  same contract as `quenching-align`.
- **MERGE, never clobber, never delete.** Only names, placement, and
  description/frontmatter conformance change; bodies are preserved verbatim. A skill the
  axis cannot classify is **kept and reported** (unroutable, with the observed reason);
  a suspected-obsolete skill is flagged, and deleted only when the human states it is
  obsolete.
- **The registry ends the run honest.** The GENERATED zone is regenerated from the
  post-migration surface and verified against `.claude/skills/` before the run ends;
  residue is reported, never silently dropped.

## Workflow

### 1. Inventory the surface (read-only)
`Glob` `.claude/skills/*/SKILL.md`, `.claude/commands/**/*.md`, and directory-scoped
`**/.claude/skills/*/SKILL.md`. For each item record: current name, axis classification
per the test ([taxonomy](../quenching-skill/references/taxonomy.md) §axis — several
unrelated folders → unroutable), and its gaps (non-canonical name, missing or wrongly
nested wrapper, a generic skill mirrored under a folder path, description over the cap or
without triggers, missing frontmatter). Read `docs/standards/automation/skills.md` if
present — it governs; note whether the rule and the registry
(`docs/documentation/reference/automation.md`) exist, and whether `docs/index.md` carries
`okf_version` (no bundle → rule/registry stay out of scope, migration still applies).
**Done when:** the inventory table (item · classification · gaps) is complete and no file
changed.

### 2. Sweep the blast radius
`git grep` (plus `grep -rn --no-ignore` for gitignored surfaces) each name slated for
rename — skill names and command paths — across product code, CI, and scripts. Every hit
makes that rename a **code-coupled** item gated on its own OK. **Done when:** each planned
rename is marked coupled or free, with its hits.

### 3. Present ONE consolidated plan → gate
One table: renames (old → canonical new, coupled ones marked), wrappers to create or
rewrite (and wrongly mirrored generic skills to flatten), rule + registry creations from
the molds when missing (rule born `authority: background`), unroutables kept-and-reported
with reasons, obsolete-suspect flags (no deletion proposed without the human's word).
Wait for the single confirmation; code-coupled items each await their own.
**Done when:** the user has answered; declined → nothing written, run ends.

### 4. Apply
Execute the confirmed plan: rename skill folders, update each renamed skill's `name:`,
create/rewrite wrappers from `automation/command.md` (one sentence, Skill tool,
`$ARGUMENTS`), fix frontmatter gaps per the doctrine (description within the cap,
triggers second sentence — bodies untouched), write rule and registry from their molds
when planned, update each code-coupled reference site alongside its individually
confirmed rename. **Done when:** every confirmed row is applied.

### 5. Verify and report
Regenerate the registry's GENERATED zone from the post-migration
`.claude/skills/*/SKILL.md` frontmatter ([taxonomy](../quenching-skill/references/taxonomy.md)
§registry). Then verify: every command wrapper resolves to an existing skill (a dangling
wrapper is fixed to the new name, or reported if ambiguous); the zone matches
`.claude/skills/` exactly; every renamed reference site compiles/greps clean. In an OKF
repo, append ONE consolidated `log.md` entry (the migration, with counts) and confirm the
registry is indexed, per
[../quenching-add/references/homes.md](../quenching-add/references/homes.md).
Report: renamed / wrappers created / flattened / rule+registry created / unroutable /
flagged. **Done when:** registry, wrappers, and skills agree, and the counts are reported.

## Invariants

- Never modify anything before the plan's OK; a code-coupled rename never rides the batch.
- Never alter a skill body — only names, placement, and frontmatter conformance.
- Never delete a skill without the human stating it is obsolete; never force an
  unroutable item onto the axis.
- Never leave the GENERATED zone stale — regenerate and verify before the run ends.
- Never hand this SKILL.md `context: fork` — both gates are mid-flow.
