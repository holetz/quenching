# `assets/` — everything Claude Code must not surface as an entry point

That sentence is the whole membership rule, and it is the standard's
([plugin-layout.md](../../../.docs/standards/architecture/plugin-layout.md)), not a local one.
`commands/**` is the only tree Claude Code registers — every `.md` under it *is* a command, since
the path is the identity — so anything that is not an entry point lives here: the installable
payload, the shared procedure the bodies cite, the measured case sets, the harnesses that grade
this checkout.

The **installable payload is a subset of that, not the whole of it.** This README used to open by
calling the folder "the installable payload"; that narrower definition was replaced when shared
procedure moved in, and the wider one is what the inventory below is organized by.

Everything here is reached by absolute path — `${CLAUDE_PLUGIN_ROOT}/assets/…` — never relatively,
because a relative path encodes the depth of the *citing* file and `commands/align.md` and
`commands/docs/documentation/build.md` would need different strings for the same target.

## Inventory — four reasons a file sits here

| Reason | Subtrees |
| --- | --- |
| **Payload copied whole** by an align into a target repo | `docs/` `specs/` `claude/` `mkdocs/` |
| **Payload applied per insert** — a mold stamps one file at a time, the mold itself never lands | `templates/` |
| **Tool the plugin executes** during a command | `bin/cq` (the four pre-refactor scripts under `bin/` and `hooks/` are retained, unwired, until they are retired) |
| **Development artifact of this repository** — never installed anywhere | `references/` `evals/` `checks/` |

### Payload copied whole

| Path | What it is | Installs into the target as |
| --- | --- | --- |
| `docs/` | the canonical **OKF bundle skeleton** — 23 reserved `index.md` listings (only the root carries frontmatter, and only `okf_version`), `standards/CLAUDE.md`, the 5 `.pages` nav files inside `documentation/**`, and the fixed `knowledge/glossary.md` term-lookup seed | the target's `/.docs/`, only the homes that apply |
| `specs/plans/.gitkeep` | keeps the active-spec folder in git while empty — the folder IS the listing, and `cq specs list` derives it from disk | `/.specs/plans/` |
| `specs/archive/.gitkeep` | keeps the closed-spec folder in git while empty | `/.specs/archive/` |
| `mkdocs/` | the **site layer** payload — `mkdocs.yml.tmpl`, `requirements.txt`, opt-in `ci-github-pages.yml` (the `.pages` nav files ship inside `/.docs/documentation/**`) | the target's repo **root**, outside `/.docs/` |

Two files under `hooks/` used to belong to this table and no longer do — **nothing copies or
merges them into a target any more**, since the plugin's own `hooks/hooks.json` wires the checker
and `${CLAUDE_PLUGIN_ROOT}` resolves it:

| Path | What it is | Reaches a target? |
| --- | --- | --- |
| `hooks/hooks-config.json` | the checker's config (block `okfValidate`) — the shipped copy is the **defaults reference**; the settings the checker actually reads come from the *target's* own `.claude/hooks/hooks-config.json`, if a human writes one | **no** |
| `hooks/settings.snippet.json` | a **reference copy** of what `hooks/hooks.json` declares, kept for reading | **no** — zero consumers |

`specs/schema.json` and `specs/templates/spec.md` sit in this tree but are a hybrid: they ship
*and* they are read at runtime by `cq specs`, whose `specs/schema.py` carries a byte-identical
embedded copy of each so an installed lone tool still works. `python3 -m unittest discover -s
tests -k assets` exists to prove the two have not drifted — edit both or neither.

### Payload applied per insert

`templates/` — the molds. `/quenching:knowledge:add` picks one by home → `type`,
`/quenching:components:harness:align` applies the `harness/` pair, the `/quenching:components:*`
family applies `automation/`. The mold's *content* reaches the target; the file itself never does.
Inventory and stamp discipline: [templates/README.md](templates/README.md).

A mold is under a citation rule of its own — **it cites nothing it does not also install**, because
it lands in a repo that has none of this one's `/.docs/`. That is why a mold and this plugin's own
copy of the same standard legitimately differ in wording.

### Tools the plugin executes

| Path | Role | Installed into a target? |
| --- | --- | --- |
| `bin/cq` | every pillar's deterministic rails — `specs`, `knowledge` (the OKF v0.1 conformance checker, CLI **and** hook) and `components` (the `.claude/` front's `doctor` / `lint` / `drift`), plus `components session`, which reads a session transcript as evidence for `/quenching:components:command:retro` | **no** — the plugin's own `hooks/hooks.json` and every command body invoke it by `${CLAUDE_PLUGIN_ROOT}` |

**`cq` is not installed anywhere.** Resolution is plugin-first with no fallback and no manual rung
([references/align/tool-resolution.md](references/align/tool-resolution.md)), so a copy under a
target's `.claude/hooks/` is legacy debris from before that change — reported by `cq components
drift` and offered for removal by the matching align, never overwritten.

**One entry point now serves every event.** A hook event and a command body both shell out to
`bin/cq`; `hooks/hooks.json` names `cq knowledge hook` at `PostToolUse` and `Stop`, and every
command body reaches the same file for its own pillar. The four scripts this package replaced
still sit byte-for-byte under `hooks/` and `bin/` — unwired, invoked by nothing — until they are
retired.

### Development artifacts of this repository

| Subtree | What it is |
| --- | --- |
| `references/` | the **shared procedure** — owned once, cited by absolute path from the command bodies rather than restated. One folder per owning command, named for that command's path with `/` → `-`; other commands may cite it (`references/align/` serves seven). |
| `evals/` | the **measured case sets** written by `/quenching:components:command:eval` — `evals.json` plus a timestamped run directory. The tree mirrors the command's path with the slashes kept, so `commands/components/hook/new.md` ↔ `evals/components/hook/new/`, and renaming a command renames its eval folder in the same step. |
| `checks/` | the **harnesses that grade this checkout** out of process — `functional-checks.sh` (the command registry is built at session start, so no change under `commands/**` is testable in the session that writes it) and `conclude-order-check.sh` (order is a property only a real git history exhibits). Never installed, outside the lockstep. |

## The signature

The `/.docs/` tree is the **portable signature** — every repo the plugin aligns ends with the same
homes, the same reserved `index.md` listings, the same `type` vocabulary. The skeleton is
**conformant by construction**: `python3 bin/cq knowledge validate assets/docs` over it reports **0
errors, 0 warnings**.

## How the commands use it

- **`/quenching:knowledge:align`** scaffolds the applicable homes from `docs/` (including the fixed
  `knowledge/glossary.md` seed), stamps frontmatter with `templates/`, offers to wire `hooks/`
  (step 6) and stamps `mkdocs/` **once** (step 7).
- **`/quenching:knowledge:add`** picks a mold from `templates/` by home → `type`, updates the bundle's
  `index.md`, and rows any new repo-specific term into `knowledge/glossary.md`.
- **`/quenching:knowledge:define`** adds/refines one entry in the fixed `knowledge/glossary.md` term lookup
  (alphabetical, MERGE never clobber); `/quenching:knowledge:learn` and `/quenching:knowledge:import-memory` run the same
  enrichment as a tail step; `/quenching:knowledge:glossary-backfill` backfills it in bulk from a whole-bundle sweep.
- **`/quenching:knowledge:documentation:build`** owns `mkdocs/` after that first stamp: every install, config
  merge, `.pages` regeneration and `mkdocs build --strict` verification is its.
- **`/quenching:components:harness:align`** applies the `templates/harness/` molds to rewrite a repo's `CLAUDE.md` /
  `AGENTS.md` as thin pointers over the bundle, moving inlined knowledge into its home.
- **`/specs:align`** copies the `specs/` seed; `/specs:*` drive the cycle through `cq specs`.
- **`/quenching:components:align`** offers to remove a legacy tool copy under a target's
  `.claude/hooks/`; the `/quenching:components:*` minters apply `templates/automation/`.

## Install discipline

1. **Copy** only the homes that apply (a repo without data gets no `catalog/`).
2. **Adapt** boundary lines and the derived listings to the repo; keep the surface **English**
   (folder names, slugs, keys, enums) — body prose follows the repo's language.
3. **Never** overwrite a target's generated artifacts (AUTO-GENERATED catalog, manifests).
4. If the repo already had an equivalent, **deprecate it** — do not remove without OK.
