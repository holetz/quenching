# The automation taxonomy — one axis, canonical names, mirrored commands

The classification, naming, mirroring, and registry rules for a target repo's **local
automation surface** (`.claude/skills/` + `.claude/commands/`). `quenching-skill-new` applies
them per mint/edit; `quenching-skill-align` applies them to the whole surface. In a target
repo the rule itself lives at `docs/standards/automation/skills.md` (stamped from
`assets/templates/automation/skills-standard.md`); this file is the plugin-side owner both
skills load, and the standard the target carries says the same thing.

**Three facts this file no longer states, because each has one owner that executes.** The
invocation/permission decision table and the scoped-`allowed-tools` rule live in
`docs/standards/automation/skills.md`; the metadata caps and the surface ceiling in
`docs/standards/automation/context-budget.md`; the registry zone's row format in
`skills.py registry reindex`. Findings arrive as `sk-*` codes and are named by code, never by
restated threshold.

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
listing of the local automation surface.

**`skills.py registry reindex` owns the zone's format.** The row shape, the column
order, the sort, and the placeholders are the tool's, exactly as `specs.py backlog
reindex` owns the backlog listing's — so the format is stated in one place that
executes, not in prose two skills reproduce by hand. To see the current shape, run the
tool; to change it, change the tool.

What this file still owns, because no tool decides it:

- **Where the zone may live.** Between `<!-- GENERATED:BEGIN -->` and
  `<!-- GENERATED:END -->`, and nowhere else. **Curated prose** — how the surface is
  organized, a link to the rule, pointers to installed plugins — lives **outside** the
  markers and is never touched by regeneration. A registry with no markers is
  `sk-no-zone`: the tool refuses rather than placing a table at a guessed anchor inside
  prose a human wrote.
- **What the zone is derived from.** The local `.claude/skills/*/SKILL.md` frontmatter,
  and only that: the zone lists the repo's **own** surface. Commands contributed by
  installed plugins (`/specs:*`, marketplace plugins) stay out of it and may be pointed
  at from the curated prose.
- **Who may run the regeneration.** `quenching-skill-new` (in its OKF tail) and
  `quenching-skill-align` (in its verify step). Neither writes between the markers by
  hand, and neither composes the table itself — a skill that generates a derived table
  and then diffs it against its own source is one reader checking its own arithmetic,
  which is the failure this tool exists to remove. Both end their run on a second
  `registry reindex` reporting `changed: false`; a hand edit inside the markers is
  therefore repaired, not accumulated.
