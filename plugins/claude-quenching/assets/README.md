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
| `templates/` | the **molds** — `concept-front`, `standard-front`, `catalog/{system,schema,table}`, `backlog/task` (→ `openspec/backlog/`), `vision/area`, `sidecar`, `harness/{claude-root,claude-subfolder}`, `index.md.tmpl`, `log.md.tmpl` | applied per insert (not copied wholesale) |
| `hooks/okf-validate.py` | the zero-dependency **OKF conformance checker** (CLI + hook) | `.claude/hooks/` |
| `hooks/hooks-config.json` | the checker's config (block `okfValidate`) | `.claude/hooks/` |
| `hooks/settings.snippet.json` | hook wiring (`PostToolUse` + `Stop`; opt-in `PreToolUse`) | merge into `.claude/settings.json` |

## The signature

The `docs/` tree is the **portable signature** — every repo the plugin aligns ends with the
same homes, the same reserved `index.md` listings, the same `type` vocabulary, the same
`log.md` shape. The skeleton is **conformant by construction**: running
`python3 hooks/okf-validate.py docs` over it reports **0 errors, 0 warnings**.

## How the skills use it

- **`quenching-align`** scaffolds the applicable homes from `docs/` (including the fixed
  `knowledge/glossary.md` seed), stamps frontmatter with `templates/`, and offers to wire `hooks/`.
- **`quenching-add`** picks a mold from `templates/` by home → `type`, updates the bundle's
  `index.md`/`log.md`, and rows any new repo-specific term into `knowledge/glossary.md`.
- **`quenching-define`** adds/refines one entry in the fixed `knowledge/glossary.md` term lookup
  (alphabetical, MERGE never clobber); `quenching-learn` / `quenching-import-memory` run the
  same enrichment as a tail step; `quenching-glossary-backfill` backfills it in bulk from a
  whole-bundle sweep.
- **`quenching-harness`** applies the `templates/harness/` molds to rewrite a repo's
  `CLAUDE.md`/`AGENTS.md` as thin pointers over the bundle, moving inlined knowledge into its home.

## Install discipline

1. **Copy** only the homes that apply (a repo without data gets no `catalog/`).
2. **Adapt** boundary lines and the derived listings to the repo; keep the surface **English**
   (only `audience: human` docs follow the repo's language).
3. **Never** overwrite a target's generated artifacts (AUTO-GENERATED catalog, manifests).
4. If the repo already had an equivalent, **deprecate it** — do not remove without OK.
