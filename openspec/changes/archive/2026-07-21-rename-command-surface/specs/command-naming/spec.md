## ADDED Requirements

### Requirement: Verb-first command names reveal the action
Every command in the plugin's surface SHALL be named as a verb (or verb-object) that names
its action, so the `/` menu tells the story without the user reading the description. A
command name MUST NOT be a bare noun that reads as a query, a jargon term when a plain verb
exists, or a name whose apparent object differs from what it acts on.

#### Scenario: Jargon replaced by a plain verb
- **WHEN** the surface exposes the OpenSpec implement action
- **THEN** it is named `opsx:implement` (not `opsx:apply`), and the revise action is
  `opsx:revise` (not `opsx:update`), so the two no longer collide in meaning

#### Scenario: The object is named when the verb alone is ambiguous
- **WHEN** a command's action needs an object to be understood (merging delta specs into the
  main specs)
- **THEN** the command names it — `opsx:sync-specs` (not bare `opsx:sync`)

#### Scenario: A name that lies is corrected
- **WHEN** a command backfills `knowledge/glossary.md` from the whole bundle
- **THEN** it is named `docs:glossary-backfill` (not `docs:knowledge-scan`, which names the
  wrong object)

#### Scenario: A query-shaped name becomes an action
- **WHEN** a command parks one task in the backlog inbox
- **THEN** it is named `opsx:backlog-add` (an action), pairing visibly with `opsx:backlog-triage`

### Requirement: Namespaces are honest by subject
The command surface SHALL be partitioned into namespaces by the artifact each command acts
on: `opsx:` for the OpenSpec change lifecycle, `docs:` for the OKF `docs/` bundle, and
`skill:` for the target repo's `.claude/` automation surface. A command's namespace MUST
match what it touches.

#### Scenario: Automation commands leave the docs namespace
- **WHEN** a command mints or migrates skills under `.claude/skills` + `.claude/commands`
- **THEN** it lives under `skill:` (`skill:new`, `skill:align`), not `docs:`, because it does
  not touch `docs/`

#### Scenario: Bundle commands stay in docs
- **WHEN** a command reads or writes the OKF `docs/` bundle (add a doc, import a source,
  define a term, drain memory into it, converge it)
- **THEN** it lives under `docs:`

### Requirement: The opsx namespace and upstream skill names are preserved
The OpenSpec command namespace SHALL remain `opsx:`, and the six skills adapted 1:1 from the
OpenSpec CLI (`openspec-*` with `metadata.generatedBy`) SHALL keep their skill names even
when their command is renamed, to preserve alignment with the upstream CLI convention.

#### Scenario: Command renamed, skill name kept
- **WHEN** `opsx:apply` is renamed to `opsx:implement`
- **THEN** the wrapper still targets the skill `openspec-apply-change` (unchanged), and the
  1:1 upstream mapping is intact

#### Scenario: Quenching-native skills rename in lockstep
- **WHEN** a `docs:` command is renamed and its skill is quenching-native (no `generatedBy`)
- **THEN** the skill directory and `name:` rename together with the command
  (`docs:insert`→`docs:add` ↔ `quenching-insert`→`quenching-add`)

### Requirement: One skill, one wrapper is preserved
The rename SHALL keep the bijection of 19 skills to 19 command wrappers. No skills are merged
and no wrappers are consolidated behind a flag; the change alters names and namespaces only.

#### Scenario: Count is unchanged after the rename
- **WHEN** the rename is complete
- **THEN** every skill still has exactly one wrapper and every wrapper targets exactly one
  skill

### Requirement: Clean rename without compatibility aliases
The old command and skill names SHALL be removed rather than kept as aliases, because the
surface is discovered through the `/` menu and a stale alias would reintroduce the ambiguity
this change removes. The rename SHALL be recorded once in the bundle's `log.md`.

#### Scenario: Old name no longer resolves
- **WHEN** a user invokes a pre-rename command name (e.g. `docs:insert`)
- **THEN** it does not resolve — only the new name (`docs:add`) exists — and the deprecation
  is recorded in `log.md`
