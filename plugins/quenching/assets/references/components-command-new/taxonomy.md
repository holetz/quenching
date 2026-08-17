# The automation taxonomy — one axis, canonical paths, one file per entry point

In a target repo this rule is stamped to `knowledge/standards/automation/skills.md` from
`assets/templates/automation/skills-standard.md`; this file is the plugin-side owner.

**Owned elsewhere — cite, never restate.** The
invocation/permission decision table, the scoped-`allowed-tools` rule, and the description
caps all live in `knowledge/standards/automation/skills.md`; the registry zone's row format in
`cq components registry reindex`. Findings arrive as `sk-*` codes and are named by code, never by
restated threshold.

## The single axis

Every skill is classified on **exactly one axis: what it acts on** — asked as up to two
questions, in order, each with a single honest answer. The first question is a
subject/category; the second is the older domain-bound-vs-generic test, now read against
that category instead of standing alone.

**1. Category/subject — the first question.** Name the one subject the skill belongs to
(`git`, `deploy`, `tests`, ...). A clean, evident answer wins. No evident subject, or
several unrelated ones, means there is no category: fall straight through to the second
question exactly as if this step did not exist — **categorization only applies when it
fits; it is never forced.**

**2. Domain-bound vs generic — the second question, read against the category.**
- **No category** — unchanged from before this rule: **domain-bound** when the skill
  serves ONE folder subtree of the repo (`communications/teams/`, `pipelines/ingest/`);
  **generic** when it serves the repo as a whole; **neither** (keep-and-report) when
  several unrelated folders answer at once.
- **Category, no single real folder tied to the skill** — e.g. `git` for a `commit`
  skill: a subject, not a repo folder. The skill nests flat under the category. **This
  example stays valid even in a repo that also has this plugin installed** — a target's own
  bare-cited `git`-category `commit` command and this plugin's `/quenching:git:commit` coexist
  rather than collide, because the citation forms already separate them
  (`naming/command-surface.md` §Three citation forms): the example is about the target's own
  category, and this plugin's commands are never bare-cited in a repo that did not vendor them.
- **Category, and a real folder tied to the skill** — the folder either **nests** inside
  the category or is **replaced** by it, per the convention already established for that
  category in *that* target repo (below). Several unrelated folders still fit neither and
  keep-and-report, exactly as the no-category case.

No category is ever invented to force a classification a skill does not otherwise earn —
the same keep-and-report exit the old single test used still applies whenever the honest
answer is "several" or "none".

### Reading the nest-vs-replace convention

The convention lives entirely inside the **target repo's own** `.claude/commands/<categoria>/`
— never in the plugin, and never in a dedicated registry file of its own:

- Files already sitting under `.claude/commands/<categoria>/<folder-path>/` (the real
  folder present as a subpath) → the convention already in force is **nest**.
- Files already sitting directly under `.claude/commands/<categoria>/` with no real-folder
  subpath → the convention already in force is **replace**.
- The category has no files yet in that repo, or the two shapes are already mixed
  (ambiguous) → ask the human once. The physical structure that first answer produces
  *becomes* the record — reused in silence for every later skill of that category in that
  repo, with nothing else written down anywhere.

Two repos may read opposite conventions for the same category name without conflict: the
convention is never shared, catalogued, or asked twice for the same category in the same
repo.

## Naming

| Case | Name pattern | Example |
| --- | --- | --- |
| No category, domain-bound | flattened folder path + verb, kebab-case | `communications/teams/` + create → `communications-teams-create` |
| No category, generic | verb-object (or the object alone when the verb is implied), no folder path | `release-notes`, `generate-changelog` |
| Category, no folder tied | `<categoria>/<verb>` (or `<categoria>/<verb-object>`) | `git` + commit → `git/commit` |
| Category, folder nests | `<categoria>/<folder-path>/<verb>` | `deploy` + `infra/terraform/` + apply → `deploy/infra/terraform/apply` |
| Category, folder replaced | `<categoria>/<verb>` | `deploy` + `infra/terraform/` + apply → `deploy/apply` — the category takes the folder's place |

The path alone tells where the command acts: a reader scanning `.claude/commands/`
reconstructs the monorepo map from the domain-bound and category paths, and anything at the
top level is repo-wide by declaration.

## Placement — the path IS the identity

<!-- rules -->
- **One file per entry point.** A `.claude/commands/<path>.md` carries both the description
  that routes to it and the body that runs: a command's path is its whole identity, and
  nothing derives a second name that could disagree with it.
- **A domain-bound command with no evident category lives at**
  `.claude/commands/<folder-path>/<verb>.md`, invocable as `/<folder>:<subfolder>:<verb>` —
  Claude Code's native `:` separator maps one `:` per path segment (a `::` in older notes
  maps to `:`). Mold: `assets/templates/automation/command.md`.
- **A command with an evident category lives at** `.claude/commands/<categoria>/<verb>.md`
  when no real folder ties it, or when that category's established convention in this repo
  is to replace the folder; at `.claude/commands/<categoria>/<folder-path>/<verb>.md` when
  the convention is to nest. Invocable as `/<categoria>:<verb>` or
  `/<categoria>:<subfolder>:<verb>` respectively.
- **A generic command with no evident category is a flat** `.claude/commands/<verb-object>.md`,
  never nested under a folder or category it does not serve.

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
