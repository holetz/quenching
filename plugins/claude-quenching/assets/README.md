# assets/ — the installable payload

Everything the `claude-quenching` skills stamp into a target repo lives here. This is what
makes the plugin **self-contained**: the skills carry their own skeleton, molds, and validator
and copy them out — they depend on no external skill. Both skills reach this payload via
`${CLAUDE_PLUGIN_ROOT}/assets/...`.

> **These files are inert in this plugin.** They sit under `assets/` (≥2 levels below a
> `SKILL.md`), so Claude Code does not discover them as live skills — they are
> templates/payloads, applied when a skill runs.

## Inventory

| Path | What it is | Installs into the target |
| --- | --- | --- |
| `docs/` | the canonical **OKF bundle skeleton** — 27 `index.md` listings, root `okf_version`, `log.md` seeds, `standards/CLAUDE.md`, 4 channel molds, and the fixed `knowledge/glossary.md` term-lookup seed | the target's `docs/` (only the homes that apply) |
| `docs/QUENCHING.md` | the **operator manual** for the `docs/` front — commands, confirmation rules, the hook, recipes, finding-code troubleshooting | the target's `docs/QUENCHING.md` |
| `specs/backlog/index.md` | the **task inbox** seed (derived zone + Completed ledger) | the target's `specs/backlog/` |
| `specs/QUENCHING.md` | the **operator manual** for the `specs/` front — the plan lifecycle, the `/specs:*` commands, the `specs.py` tool, the OKF bridge, the backlog contract | the target's `specs/QUENCHING.md` |
| `claude/QUENCHING.md` | the **operator manual** for the `.claude/` front — the taxonomy axis, mirroring, the rule + registry, hook/settings hygiene | the target's `.claude/QUENCHING.md` |
| `templates/` | the **molds** — `concept-front`, `standard-front`, `catalog/{system,schema,table}`, `backlog/task` (→ `specs/backlog/`), `vision/area`, `sidecar`, `harness/{claude-root,claude-subfolder}`, `index.md.tmpl`, `log.md.tmpl` | applied per insert (not copied wholesale) |
| `mkdocs/` | the **site layer** payload — `mkdocs.yml.tmpl`, `requirements.txt`, opt-in `ci-github-pages.yml` (the `.pages` nav files ship inside `docs/documentation/**`) | the target's repo **root**, outside `docs/` |
| `hooks/okf-validate.py` | the zero-dependency **OKF conformance checker** (CLI + hook) | `.claude/hooks/` |
| `hooks/hooks-config.json` | the checker's config (block `okfValidate`) | `.claude/hooks/` |
| `hooks/settings.snippet.json` | hook wiring (`PostToolUse` + `Stop`; opt-in `PreToolUse`) | merge into `.claude/settings.json` |

## The signature

The `docs/` tree is the **portable signature** — every repo the plugin aligns ends with the
same homes, the same reserved `index.md` listings, the same `type` vocabulary, the same
`log.md` shape. The skeleton is **conformant by construction**: running
`python3 hooks/okf-validate.py docs` over it reports **0 errors, 0 warnings**.

## How the skills use it

- **`quenching-docs-align`** scaffolds the applicable homes from `docs/` (including the fixed
  `knowledge/glossary.md` seed), stamps frontmatter with `templates/`, and offers to wire `hooks/`.
- **`quenching-docs-add`** picks a mold from `templates/` by home → `type`, updates the bundle's
  `index.md`/`log.md`, and rows any new repo-specific term into `knowledge/glossary.md`.
- **`quenching-docs-define`** adds/refines one entry in the fixed `knowledge/glossary.md` term lookup
  (alphabetical, MERGE never clobber); `quenching-docs-learn` / `quenching-docs-import-memory` run the
  same enrichment as a tail step; `quenching-docs-glossary-backfill` backfills it in bulk from a
  whole-bundle sweep.
- **`quenching-docs-documentation-build`** owns `mkdocs/`: `quenching-docs-align` (step 7) stamps it
  **once** while scaffolding, and every install, config merge, `.pages` regeneration, and
  `mkdocs build --strict` verification after that is that skill's.
- **`quenching-docs-harness`** applies the `templates/harness/` molds to rewrite a repo's
  `CLAUDE.md`/`AGENTS.md` as thin pointers over the bundle, moving inlined knowledge into its home.
- **Each of the three aligns installs its front's `QUENCHING.md`** — `quenching-docs-align` →
  `docs/`, `quenching-specs-align` → `specs/`, `quenching-skill-align` → `.claude/` — under the
  four-branch rule owned by `quenching-docs-align` (SKILL.md §4): absent → install · older banner →
  overwrite · same-or-newer → leave · **banner removed by a human → keep and report**. The
  banner's `<VERSION>` placeholder is filled from `VERSION` at copy time, so releases need no
  extra lockstep. `QUENCHING.md` is an **exempt** basename in the validator — never stamped,
  never converted to `index.md`.

## Install discipline

1. **Copy** only the homes that apply (a repo without data gets no `catalog/`).
2. **Adapt** boundary lines and the derived listings to the repo; keep the surface **English**
   (only `audience: human` docs follow the repo's language).
3. **Never** overwrite a target's generated artifacts (AUTO-GENERATED catalog, manifests).
4. If the repo already had an equivalent, **deprecate it** — do not remove without OK.
