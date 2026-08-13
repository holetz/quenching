# The automation taxonomy — one axis, canonical paths, one file per entry point

In a target repo this rule is stamped to `knowledge/standards/automation/skills.md` from
`assets/templates/automation/skills-standard.md`; this file is the plugin-side owner.

**Owned elsewhere — cite, never restate.** The
invocation/permission decision table, the scoped-`allowed-tools` rule, and the description
caps all live in `knowledge/standards/automation/skills.md`; the registry zone's row format in
`cq components registry reindex`. Findings arrive as `sk-*` codes and are named by code, never by
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
classification is worse than none.

## Naming

| Axis value | Name pattern | Example |
| --- | --- | --- |
| Domain-bound | flattened folder path + verb, kebab-case | `communications/teams/` + create → `communications-teams-create` |
| Generic | verb-object (or the object alone when the verb is implied), no folder path | `release-notes`, `generate-changelog` |

The path alone tells where the command acts: a reader scanning `.claude/commands/`
reconstructs the monorepo map from the domain-bound paths, and anything at the top level is
repo-wide by declaration.

## Placement — the path IS the identity

<!-- rules -->
- **One file per entry point.** A `.claude/commands/<path>.md` carries both the description
  that routes to it and the body that runs: a command's path is its whole identity, and
  nothing derives a second name that could disagree with it.
- **A domain-bound command lives at** `.claude/commands/<folder-path>/<verb>.md`, invocable
  as `/<folder>:<subfolder>:<verb>` — Claude Code's native `:` separator maps one `:` per
  path segment (a `::` in older notes maps to `:`). Mold:
  `assets/templates/automation/command.md`.
- **A generic command is a flat** `.claude/commands/<verb-object>.md`, never nested under a
  folder path it does not serve.

**`commands/**` is the only tree Claude Code registers**, so nothing that is not an entry
point lives there — shared procedure, references, fixtures and eval cases sit outside it and
are cited by absolute path. A file parked under `commands/` registers as a command with no
description, which `doctor` reports as `sk-no-description`; the layout rule needs no check
of its own.

**Accepted variation (documented, never generated):** directory-scoped surfaces
(`<folder>/.claude/commands/`) also bind a command to a folder and are a conformant way
to express domain-binding — the sweep classifies them in place. The mint always writes into
the repo-root `.claude/`, keeping the surface auditable in one place.

<!-- rationale -->
Claude Code merged custom commands into skills. There is no `SKILL.md` half and no wrapper,
so there is no mirroring rule and no bijection to check.

Discovery story: `/` + tab walks the command tree in folder order, so the paths make the
automation surface navigable the same way the repo is.

## The registry and its GENERATED zone

<!-- rules -->
The registry at `knowledge/documentation/reference/automation.md` (`type: documentation`,
stamped from `assets/templates/automation/registry.md`) is the bundle's authoritative
listing of the local automation surface.

**`cq components registry reindex` owns the zone's format.** The row shape, the column
order, the sort, and the placeholders are the tool's. To see the current shape, run the
tool; to change it, change the tool.

This file owns, because no tool decides it:

- **Where the zone may live.** Between `<!-- GENERATED:BEGIN -->` and
  `<!-- GENERATED:END -->`, and nowhere else. **Curated prose** — how the surface is
  organized, a link to the rule, pointers to installed plugins — lives **outside** the
  markers and is never touched by regeneration. A registry with no markers is
  `sk-no-zone`.
- **What the zone is derived from.** The local `.claude/commands/**/*.md` frontmatter,
  and only that: the zone lists the repo's **own** surface. Commands contributed by
  installed plugins (`/quenching:specs:*`, marketplace plugins) stay out of it and may be pointed
  at from the curated prose.
- **Who may run the regeneration.** `/quenching:components:command:new` (in its OKF tail) and
  `/quenching:components:align` (in its verify step). Neither writes between the markers by
  hand, and neither composes the table itself. Both end their run on a second
  `registry reindex` reporting `changed: false`.

<!-- rationale -->
The format is stated in one place that executes, not in prose two skills reproduce by hand,
exactly as `cq specs backlog reindex` owns the backlog listing's. On `sk-no-zone` the tool
refuses rather than placing a table at a guessed anchor inside prose a human wrote. A skill
that generates a derived table and then diffs it against its own source is one reader
checking its own arithmetic, which is the failure this tool exists to remove; a hand edit
inside the markers is therefore repaired, not accumulated.
