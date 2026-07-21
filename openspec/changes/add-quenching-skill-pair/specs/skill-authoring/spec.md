## ADDED Requirements

### Requirement: Single-axis classification
`quenching-skill` SHALL classify every requested skill on exactly one axis — **domain-bound**
(serves one folder of the target repo) or **generic** (serves the repo as a whole) — and
SHALL derive all naming and placement from that classification alone.

#### Scenario: Domain-bound automation
- **WHEN** the user requests a skill for work that lives in one repo folder (e.g. creating
  communications under `communications/teams/`)
- **THEN** the skill is classified domain-bound and named as the flattened folder path plus
  a verb (`communications-teams-create`)

#### Scenario: Generic automation
- **WHEN** the requested automation serves the repo as a whole (e.g. generating release notes)
- **THEN** the skill is classified generic and named verb-object (`release-notes`), with no
  folder path in the name

### Requirement: Mirrored command wrapper for domain-bound skills
For every domain-bound skill, `quenching-skill` SHALL create a thin command wrapper at
`.claude/commands/<folder-path>/<verb>.md` that invokes the skill, so it is invocable as
`/<folder>:<subfolder>:<verb>` (native `:` separator). Generic skills MUST NOT be mirrored —
they get a flat command or none.

#### Scenario: Mint creates the mirror
- **WHEN** `quenching-skill` mints `communications-teams-create`
- **THEN** `.claude/commands/communications/teams/create.md` exists, contains only the
  invocation of the skill (plus argument hint), and `/communications:teams:create` resolves

#### Scenario: Generic skill stays flat
- **WHEN** `quenching-skill` mints a generic skill
- **THEN** no nested command path is created for it

### Requirement: Writing doctrine applied to every SKILL.md
Every `SKILL.md` minted or edited SHALL follow the writing doctrine kept in
`quenching-skill/references/`: description front-loads the leading concept with one trigger
per distinct branch; steps carry checkable completion criteria; every line passes the no-op
test; prescriptions are positive (state the target behavior, not the prohibition); on-demand
doctrine is pushed to `references/` files.

#### Scenario: Drafting a conformant SKILL.md
- **WHEN** `quenching-skill` drafts or edits a `SKILL.md`
- **THEN** the description opens with the skill's leading concept followed by its triggers,
  each step states how to verify it is done, and the self-check flags any line that changes
  no behavior

### Requirement: Taxonomy rule read before minting
`quenching-skill` SHALL read `docs/standards/automation/skills.md` (the taxonomy rule)
before classifying, and SHALL follow it when present. When the repo carries an OKF bundle
and the rule is absent, the skill SHALL offer to create it from the template as part of the
plan.

#### Scenario: First run in an OKF repo
- **WHEN** `quenching-skill` runs in a repo with an OKF bundle and no
  `docs/standards/automation/skills.md`
- **THEN** the plan includes creating the rule from the template, and the mint proceeds
  under it after the single confirmation

#### Scenario: Repo without an OKF bundle
- **WHEN** the target repo has no `docs/index.md` with `okf_version`
- **THEN** the mint still proceeds (skill + wrapper only), the OKF tail is skipped, and the
  skill suggests `quenching-align` once

### Requirement: Derived automation registry
`quenching-skill` SHALL maintain the registry at
`docs/documentation/reference/automation.md` (`type: documentation`): its GENERATED zone is
regenerated from `.claude/skills/*/SKILL.md` frontmatter in the tail of every mint or edit,
and only the owning skills write inside the zone markers.

#### Scenario: Mint updates the registry
- **WHEN** a mint or edit completes in an OKF repo
- **THEN** the GENERATED zone lists every skill with its command, target folder (or
  "generic"), and typical trigger — including the one just minted

#### Scenario: Drift detection
- **WHEN** the self-check diffs the GENERATED zone against `.claude/skills/*/SKILL.md`
- **THEN** any mismatch is reported and the zone is regenerated before the run completes

### Requirement: One plan, one confirmation
`quenching-skill` SHALL present ONE plan (classification, names, files to write, OKF tail)
and apply it only after a single confirmation. Nothing is written before the OK.

#### Scenario: User confirms
- **WHEN** the user answers OK to the plan
- **THEN** all writes (skill, wrapper, OKF artifacts, log) happen in that pass

#### Scenario: User declines
- **WHEN** the user declines the plan
- **THEN** no file is created or modified

### Requirement: OKF tail on every mint
After writing the skill and wrapper in an OKF repo, `quenching-skill` SHALL append a
`log.md` entry, offer a glossary entry when the skill coins a new repo-specific term, and
run a self-check (registry diff, wrapper resolves, description within the per-skill cap).

#### Scenario: Skill coins a term
- **WHEN** the minted skill names a new repo-specific concept
- **THEN** the skill offers ONE `knowledge/glossary.md` entry for it (user decides)
