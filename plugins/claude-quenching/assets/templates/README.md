# assets/templates/ — the OKF molds

Frontmatter + body molds the skills stamp/apply. They live **outside** the `docs/` bundle
(so they are not themselves validated), and each produces an OKF-conformant concept doc when
filled. `quenching-add` picks the mold by home → `type` (see `quenching-add/references/homes.md`).

| Mold | Produces | `type` |
| --- | --- | --- |
| `concept-front.md` | any concept doc (generic frontmatter) | *(per home)* |
| `standard-front.md` | `standards/**/<concept>.md` | `standard` |
| `catalog/system.md` | `catalog/<system>/access.md` | `system` |
| `catalog/schema.md` | `catalog/<system>/<catalog>/<schema>.md` | `schema` |
| `catalog/table.md` | `catalog/<system>/<catalog>/<schema>/<table>.md` | `table` |
| `backlog/task.md` | `openspec/backlog/<task-slug>.md` (**outside** the OKF bundle) | `task` |
| `vision/area.md` | `vision/<area>.md` | `vision` |
| `sidecar.md` | `reference/regulations/**` extract | `sidecar` |
| `index.md.tmpl` | a folder's reserved `index.md` listing (no frontmatter; root carries only `okf_version`) | *(reserved)* |
| `log.md.tmpl` | a bundle's reserved `log.md` history | *(reserved)* |
| `harness/claude-root.md` | a repo-root `CLAUDE.md` thin pointer over the bundle | *(harness — exempt)* |
| `harness/claude-subfolder.md` | a subfolder `CLAUDE.md` nearest-file pointer | *(harness — exempt)* |
| `automation/skill.md` | `.claude/skills/<skill-name>/SKILL.md` (**outside** the OKF bundle) | *(not an OKF concept)* |
| `automation/command.md` | `.claude/commands/<folder-path>/<verb>.md` thin wrapper (**outside** the OKF bundle) | *(not an OKF concept)* |
| `automation/registry.md` | `documentation/reference/automation.md` (the derived skill registry) | `documentation` |
| `automation/skills-standard.md` | `standards/automation/skills.md` (the taxonomy rule, born `authority: background`) | `standard` |

The **harness molds** (`harness/`) produce **exempt** files — `CLAUDE.md`/`AGENTS.md` carry **no
frontmatter and no `type`** (harness pointers, not OKF concepts — okf-spec strict-7; the validator
skips them). `quenching-harness` applies them when it refactors a repo's harness files into thin
pointers over the bundle.

The **automation molds** (`automation/`) are the `quenching-skill` /
`quenching-skill-align` family: the skill and command-wrapper molds land under `.claude/`
(outside the bundle — never validated), while the registry and taxonomy-standard molds are
OKF concept docs the pair maintains in the bundle; the registry's
`<!-- GENERATED:BEGIN/END -->` zone is derived from `.claude/skills/*/SKILL.md` and only
those two skills write inside its markers (taxonomy owner:
`quenching-skill/references/taxonomy.md`).

## Stamp discipline

- **`type` non-empty** on every concept — the one OKF hard requirement.
- **`resource` derived, never invented** — for a standard, from the doc's `file:line`
  anchors; empty/self-pointing is disallowed.
- **MERGE, never clobber** — fill a missing key, preserve a filled or third-party one.
- **Legacy field migration** — `summary:` → `description:`, `updated:` → `timestamp:`.
- **Canonical English enums** — `audience: both|agent|human`, `authority: current|background`.
