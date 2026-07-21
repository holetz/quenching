# The automation taxonomy — one axis, canonical names, mirrored commands

The classification, naming, mirroring, and registry rules for a target repo's **local
automation surface** (`.claude/skills/` + `.claude/commands/`). `quenching-skill` applies
them per mint/edit; `quenching-skill-align` applies them to the whole surface. In a target
repo the rule itself lives at `docs/standards/automation/skills.md` (stamped from
`assets/templates/automation/skills-standard.md`); this file is the plugin-side owner both
skills load, and the standard the target carries says the same thing.

## The single axis

Every skill is classified on **exactly one axis** with two values:

- **Domain-bound** — the skill serves ONE folder subtree of the repo: its reads/writes and
  its subject matter concentrate under that folder (`communications/teams/`,
  `pipelines/ingest/`).
- **Generic** — the skill serves the repo as a whole (release notes, changelog, test
  sweep); no single folder claims it.

**The classification test:** name the one folder the skill acts on. If exactly one folder
answers, it is domain-bound to that folder. If the honest answer is "the repo", it is
generic. If several unrelated folders answer at once, it fits **neither** — keep it
untouched and report it as unroutable with the observed reason (keep-and-report); a forced
classification is worse than none. All naming and placement derive from this
classification alone.

## Naming

| Axis value | Name pattern | Example |
| --- | --- | --- |
| Domain-bound | flattened folder path + verb, kebab-case | `communications/teams/` + create → `communications-teams-create` |
| Generic | verb-object (or the object alone when the verb is implied), no folder path | `release-notes`, `generate-changelog` |

The name alone tells where the skill acts: a reader scanning `.claude/skills/` reconstructs
the monorepo map from the domain-bound names, and anything without a path prefix is
repo-wide by declaration. The flattened path uses `-` between segments and stays verbatim
with the folder's real (kebab-cased) names — the name is derived from the path, never
invented.

## Mirroring — the command wrapper

- **Every domain-bound skill gets a mirrored thin wrapper** at
  `.claude/commands/<folder-path>/<verb>.md`, making it invocable as
  `/<folder>:<subfolder>:<verb>` — Claude Code's native `:` separator maps one `:` per
  path segment (a `::` in older notes maps to `:`). The wrapper is thin (the
  `assets/templates/automation/command.md` mold): frontmatter `description` +
  `argument-hint`, one-sentence body invoking the skill via the Skill tool with
  `$ARGUMENTS`. The skill body lives in `.claude/skills/` only.
- **A generic skill is never mirrored** — no nested command path. It gets a flat command
  (`.claude/commands/<name>.md`) or none at all.
- Discovery story: `/` + tab walks the command tree in folder order, so the mirrored paths
  make the automation surface navigable the same way the repo is.

**Accepted variation (documented, never generated):** directory-scoped skills
(`<folder>/.claude/skills/<name>/`) also bind a skill to a folder and are a conformant way
to express domain-binding — the sweep classifies them in place. The mint always generates
the mirrored-wrapper mechanism above, keeping `.claude/` auditable in one place.

## The registry and its GENERATED zone

The registry at `docs/documentation/reference/automation.md` (`type: documentation`,
stamped from `assets/templates/automation/registry.md`) is the bundle's authoritative
listing of the local automation surface. Its derived zone:

- Sits between the markers `<!-- GENERATED:BEGIN -->` and `<!-- GENERATED:END -->`;
  **curated prose** (how the surface is organized, a link to the rule, pointers to
  installed plugins) lives **outside** the markers and is never touched by regeneration.
- Holds one table: `| Command | Skill | Serves | Typical trigger |`. Per row: the
  invocation (`/communications:teams:create`; `—` for a wrapperless generic skill), the
  skill name, the folder it serves (`communications/teams/` — or `generic`), and the first
  quoted trigger phrase from the skill's description.
- Rows are **ordered by the Command column** (byte order); wrapperless rows (`—`) sort
  last, ordered by Skill.
- Is **derived exclusively** from the local `.claude/skills/*/SKILL.md` frontmatter — the
  zone lists the repo's own surface only; commands contributed by installed plugins
  (`/opsx:*`, marketplace plugins) stay out of the zone and may be pointed at from the
  curated prose.
- Has exactly two writers: **`quenching-skill` and `quenching-skill-align` are the owning
  skills of the zone** — they regenerate it in their tails, and the rule the target repo
  carries declares them its only editors. The self-check in both skills diffs the zone
  against `.claude/skills/*/SKILL.md` and regenerates on any mismatch, so a hand edit
  inside the markers is repaired, not accumulated.
