## ADDED Requirements

### Requirement: Read-only inventory before any plan
`quenching-skill-align` SHALL inventory the target repo's automation surface —
`.claude/skills/`, `.claude/commands/`, and directory-scoped `**/.claude/skills/` — without
writing anything, recording for each item its current name, its classification on the
taxonomy axis (domain-bound × generic), and its conformance gaps.

#### Scenario: Inventory pass
- **WHEN** `quenching-skill-align` starts
- **THEN** it produces a read-only inventory table (skill/command, classification,
  gaps) and no file has been created, renamed, or modified

### Requirement: One consolidated migration plan, one confirmation
`quenching-skill-align` SHALL present ONE consolidated migration plan — renames to the
canonical naming, mirrored wrappers to create or rewrite, taxonomy rule and registry to
create when missing — applied on a single confirmation. A rename whose current name is
referenced by product code or scripts SHALL get its own individual confirmation.

#### Scenario: Plan applied on OK
- **WHEN** the user confirms the plan
- **THEN** all renames, wrapper creations, and OKF artifact creations happen in that pass

#### Scenario: Code-coupled rename
- **WHEN** a skill or command name to be changed is referenced by product code, CI, or
  scripts
- **THEN** that rename is confirmed individually before being applied, even inside an
  authorized run

### Requirement: Convergence to the taxonomy
After an applied plan, every domain-bound skill SHALL carry the flattened-path name and a
mirrored command wrapper, and every generic skill SHALL carry a verb-object name with no
mirrored path.

#### Scenario: Misnamed domain-bound skill
- **WHEN** the inventory finds a skill serving `communications/teams/` named `teams-post`
- **THEN** the plan renames it `communications-teams-<verb>` and creates
  `.claude/commands/communications/teams/<verb>.md`

#### Scenario: Wrongly mirrored generic skill
- **WHEN** the inventory finds a generic skill exposed under a nested folder command path
- **THEN** the plan flattens it (verb-object name, flat command or none)

### Requirement: MERGE, never clobber, never delete
`quenching-skill-align` SHALL preserve existing skill bodies — only names, placement, and
description/frontmatter conformance change. A skill it cannot classify is kept and reported
(keep-and-report), and no skill is ever deleted without the human stating it is obsolete.

#### Scenario: Unclassifiable skill
- **WHEN** a skill serves several unrelated folders at once and fits neither axis value
  cleanly
- **THEN** it is kept untouched and listed in the plan as unroutable, with the observed
  reason

#### Scenario: Deletion requires human word
- **WHEN** the sweep suspects a skill is obsolete
- **THEN** it flags it in the plan but does not delete it unless the user states it is
  obsolete

### Requirement: OKF artifacts created when missing
When the repo carries an OKF bundle and `docs/standards/automation/skills.md` or
`docs/documentation/reference/automation.md` is absent, the plan SHALL include creating
them from the templates; the registry's GENERATED zone is populated from the
post-migration state.

#### Scenario: First alignment in an OKF repo
- **WHEN** the sweep runs in an OKF repo that has skills but neither rule nor registry
- **THEN** the applied plan leaves both artifacts in place, the registry listing the
  migrated surface, and a `log.md` entry recording the migration

### Requirement: Post-apply verification
After applying, `quenching-skill-align` SHALL regenerate the registry's GENERATED zone and
verify that every command wrapper resolves to an existing skill and that the registry
matches `.claude/skills/` exactly; any residue is reported, never silently dropped.

#### Scenario: Dangling wrapper
- **WHEN** verification finds a command wrapper pointing at a skill name that no longer
  exists
- **THEN** the wrapper is fixed to the new name (or the mismatch is reported if ambiguous)

#### Scenario: Clean convergence
- **WHEN** verification finds no mismatch
- **THEN** the run reports the migrated counts and ends with registry, wrappers, and
  skills in agreement
