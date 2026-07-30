# `assets/` — everything Claude Code must not surface as an entry point

That sentence is the whole membership rule, and it is the standard's
([plugin-layout.md](../../../docs/standards/architecture/plugin-layout.md)), not a local one.
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
| **Payload copied whole** by an align into a target repo | `docs/` `specs/` `claude/` `mkdocs/` · `hooks/hooks-config.json` · `hooks/settings.snippet.json` |
| **Payload applied per insert** — a mold stamps one file at a time, the mold itself never lands | `templates/` |
| **Tool the plugin executes** during a command | `bin/` · `hooks/okf-validate.py` |
| **Development artifact of this repository** — never installed anywhere | `references/` `evals/` `checks/` |

### Payload copied whole

| Path | What it is | Installs into the target as |
| --- | --- | --- |
| `docs/` | the canonical **OKF bundle skeleton** — 23 reserved `index.md` listings (only the root carries frontmatter, and only `okf_version`), `standards/CLAUDE.md`, the 5 `.pages` nav files inside `documentation/**`, and the fixed `knowledge/glossary.md` term-lookup seed | the target's `docs/`, only the homes that apply |
| `docs/QUENCHING.md` | the **operator manual** for the `docs/` front — commands, confirmation rules, the hook, recipes, finding-code troubleshooting | `docs/QUENCHING.md` |
| `specs/plans/index.md` | the **active-spec zone** seed (the listing with its `GENERATED` markers) | `specs/plans/` |
| `specs/archive/.gitkeep` | keeps the closed-spec folder in git while empty | `specs/archive/` |
| `specs/QUENCHING.md` | the **operator manual** for the `specs/` front — the spec lifecycle, the `/specs:*` commands, the `specs.py` tool, the OKF bridge | `specs/QUENCHING.md` |
| `claude/QUENCHING.md` | the **operator manual** for the `.claude/` front — the taxonomy axis, mirroring, the rule + registry, hook/settings hygiene | `.claude/QUENCHING.md` |
| `mkdocs/` | the **site layer** payload — `mkdocs.yml.tmpl`, `requirements.txt`, opt-in `ci-github-pages.yml` (the `.pages` nav files ship inside `docs/documentation/**`) | the target's repo **root**, outside `docs/` |
| `hooks/hooks-config.json` | the checker's config (block `okfValidate`) | `.claude/hooks/` |
| `hooks/settings.snippet.json` | hook wiring (`PostToolUse` + `Stop`; opt-in `PreToolUse`) | merge into `.claude/settings.json` |

`specs/schema.json` and `specs/templates/spec.md` sit in this tree but are a hybrid: they ship
*and* they are read at runtime by `bin/specs.py`, which carries a byte-identical embedded copy of
each so an installed lone script still works. `specs.py selftest` exists to prove the two have not
drifted — edit both or neither.

### Payload applied per insert

`templates/` — the molds. `/docs:add` picks one by home → `type`, `/docs:harness` applies the
`harness/` pair, the `/skill:*` family applies `automation/`. The mold's *content* reaches the
target; the file itself never does. Inventory and stamp discipline: [templates/README.md](templates/README.md).

A mold is under a citation rule of its own — **it cites nothing it does not also install**, because
it lands in a repo that has none of this one's `docs/`. That is why a mold and this plugin's own
copy of the same standard legitimately differ in wording.

### Tools the plugin executes

| Path | Role | Installed into a target? |
| --- | --- | --- |
| `hooks/okf-validate.py` | the OKF v0.1 conformance checker — CLI **and** hook | yes, by `/docs:align`, into `.claude/hooks/` |
| `bin/specs.py` | the `specs/` front's deterministic rails | yes, by `/specs:align` |
| `bin/skills.py` | the `.claude/` front's `doctor` / `lint` / `drift` | yes, by `/skill:align` |
| `bin/session.py` | reads a session transcript as evidence for `/skill:retro` | **no** — its input is `~/.claude/projects/**`, the operator's machine, so a target has nothing to hold |

**Where an executable lives is decided by how it is invoked, not by whether it ships.**
`okf-validate.py` sits in `hooks/` because it loads `hooks-config.json` from its own directory —
separating the two breaks config loading in every installed copy. `bin/` is the Python the plugin
runs during a command. The first three are the version lockstep's artifacts 4–6; `session.py`
carries a `VERSION` for the uniform `--version` contract but stays outside the six, and says so in
its own docstring.

### Development artifacts of this repository

| Subtree | What it is |
| --- | --- |
| `references/` | the **shared procedure** — owned once, cited by absolute path from the command bodies rather than restated. One folder per owning command, named for that command's path with `/` → `-`; other commands may cite it (`references/align/` serves seven). |
| `evals/` | the **measured case sets** written by `/skill:eval` — `evals.json` plus a timestamped run directory. The tree mirrors the command's path with the slashes kept, so `commands/skill/hook/new.md` ↔ `evals/skill/hook/new/`, and renaming a command renames its eval folder in the same step. |
| `checks/` | the **harnesses that grade this checkout** out of process — `functional-checks.sh` (the command registry is built at session start, so no change under `commands/**` is testable in the session that writes it) and `conclude-order-check.sh` (order is a property only a real git history exhibits). Never installed, outside the lockstep. |

## The signature

The `docs/` tree is the **portable signature** — every repo the plugin aligns ends with the same
homes, the same reserved `index.md` listings, the same `type` vocabulary. The skeleton is
**conformant by construction**: `python3 hooks/okf-validate.py docs` over it reports **0 errors, 0
warnings**.

## How the commands use it

- **`/docs:align`** scaffolds the applicable homes from `docs/` (including the fixed
  `knowledge/glossary.md` seed), stamps frontmatter with `templates/`, offers to wire `hooks/`
  (step 6) and stamps `mkdocs/` **once** (step 7).
- **`/docs:add`** picks a mold from `templates/` by home → `type`, updates the bundle's
  `index.md`, and rows any new repo-specific term into `knowledge/glossary.md`.
- **`/docs:define`** adds/refines one entry in the fixed `knowledge/glossary.md` term lookup
  (alphabetical, MERGE never clobber); `/docs:learn` and `/docs:import-memory` run the same
  enrichment as a tail step; `/docs:glossary-backfill` backfills it in bulk from a whole-bundle sweep.
- **`/docs:documentation:build`** owns `mkdocs/` after that first stamp: every install, config
  merge, `.pages` regeneration and `mkdocs build --strict` verification is its.
- **`/docs:harness`** applies the `templates/harness/` molds to rewrite a repo's `CLAUDE.md` /
  `AGENTS.md` as thin pointers over the bundle, moving inlined knowledge into its home.
- **`/specs:align`** copies the `specs/` seed; `/specs:*` drive the cycle through `bin/specs.py`.
- **`/skill:align`** installs `bin/skills.py` and the `.claude/` manual; the `/skill:*` minters
  apply `templates/automation/`.
- **Each of the three aligns installs its front's `QUENCHING.md`** — `/docs:align` → `docs/`,
  `/specs:align` → `specs/`, `/skill:align` → `.claude/` — under the four-branch rule owned by
  `/docs:align`: absent → install · older banner → overwrite · same-or-newer → leave · **banner
  removed by a human → keep and report**. The banner's `<VERSION>` placeholder is filled from
  `VERSION` at copy time, so releases need no extra lockstep. `QUENCHING.md` is an **exempt**
  basename in the validator — never stamped, never converted to `index.md`.

## Install discipline

1. **Copy** only the homes that apply (a repo without data gets no `catalog/`).
2. **Adapt** boundary lines and the derived listings to the repo; keep the surface **English**
   (only `audience: human` docs follow the repo's language).
3. **Never** overwrite a target's generated artifacts (AUTO-GENERATED catalog, manifests).
4. If the repo already had an equivalent, **deprecate it** — do not remove without OK.
