# assets/hooks/ — the OKF enforcement hook

Self-contained enforcement payload of the `quenching` plugin. Keeps a target
repo's `docs/` bundle aligned to OKF **after** `/docs:align` installs it.

| File | Role |
| --- | --- |
| `okf-validate.py` | The OKF v0.1 conformance checker. Zero dependencies. Runs as a **CLI** (`okf-validate.py <docs-dir>` — used by the skills and the verification step) or as a **hook** (reads the hook JSON on stdin). `--version` prints its version (kept in lockstep with the plugin `VERSION`). |
| `hooks-config.json` | Shared config (block `okfValidate`): `enabled`, `docsDir`, `warnAsError`, `blockOnFail`, `hardBlock`, `deadlineMs`, `stopScan`. Commit it into the target. Per-dev overrides go in `hooks-config.local.json` (gitignored). |
| `settings.snippet.json` | Wiring to **merge** into the target's `.claude/settings.json` — `PostToolUse` + `Stop` by default; an opt-in `PreToolUse` hard-deny block. |

## What it checks (the OKF core)

- **Concept docs** (any `.md` that is not `index.md`/`log.md`): must have parseable
  frontmatter with a **non-empty `type`** (ERROR otherwise); missing recommended
  fields (`title`/`description`/`resource`/`timestamp`) → WARN.
- **`index.md`** (reserved listing): must **not** carry a concept `type` (ERROR).
  A non-root `index.md` must have **no frontmatter** (ERROR). The **root**
  `docs/index.md` may carry frontmatter but only `okf_version` (should be `"0.1"`).
- **`log.md`** (reserved history): `## YYYY-MM-DD` headings, newest first; no `type`.
- **Structural integrity** (whole-tree, CLI + `Stop`; all WARN): `dir-no-index` (a folder
  holds concept docs but has no `index.md`), `index-broken-link` (a listing points to a
  missing within-bundle file/dir), `index-orphan` (a concept doc nothing links to). External
  links, anchors, non-`.md` assets, and out-of-bundle paths are never flagged.

## Behavior

- **PostToolUse** (`Write|Edit`) and **Stop**: **PROPOSE** fixes via `additionalContext`
  (exit 0). `blockOnFail: true` escalates errors to `decision: block`.
- **PreToolUse** (opt-in `hardBlock: true`): **BLOCKS** the two hard violations —
  writing an `index.md` with a `type`, or a concept doc with no `type` — via
  `permissionDecision: "deny"`. Off by default (the plugin proposes, not blocks).

## Cost profile (dirty marker + single read pass)

- **Dirty-gated Stop** (`stopScan: "dirty"`, the default): `PostToolUse` touches a
  marker file in the system temp dir (`okf-dirty-<sha1(project)[:12]>`) on every
  `docs/**` edit; `Stop` scans only when the marker exists, else exits on **one stat**
  (<5 ms). The marker is cleared after any **completed** scan (a fixing edit re-arms
  it) and **kept** when `deadlineMs` aborts a scan mid-walk. Trade-off: a brand-new
  session over an already-dirty bundle does not re-report until the first docs edit —
  set `stopScan: "always"` to restore the unconditional every-turn sweep.
- **Single read pass**: the whole-bundle scan reads each `.md` exactly once
  (`_build_corpus`) and feeds both the per-file conformance checks and the structural
  pass — previously 2–3 reads per file. `deadlineMs` is checked per file *inside* the
  walk, so it bounds real latency instead of only suppressing output.
- **Phase-2 option (not implemented)**: a per-file mtime cache could skip re-parsing
  unchanged frontmatter, but the link graph is whole-corpus (orphans/broken links need
  every file anyway) and the script stays stdlib-only — revisit only if the single-pass
  scan is ever too slow on giant catalogs.

## Install into a target

1. Copy **exactly these three files** — `okf-validate.py`, `hooks-config.json`,
   `settings.snippet.json` — into the target's `.claude/hooks/`. Never copy the
   directory recursively (a stray `__pycache__/` would ride along).
2. Merge `settings.snippet.json` into the target's `.claude/settings.json`.
3. Set `docsDir` if the bundle root is not `docs/`.

`/docs:align` offers to do all three (Step 6, wiring the enforcement hook).

## Upgrade a target

The installed copy is a snapshot. `okf-validate.py --version` prints its version;
compare it with this plugin's `VERSION` file and, when the plugin is newer, overwrite
**only** `okf-validate.py` in the target's `.claude/hooks/` — the target's
`hooks-config.json` holds local knobs and is **preserved** (new knobs fall back to
built-in defaults). `/docs:align` Step 6 performs this comparison and offers the
upgrade when it finds an older installed copy.
