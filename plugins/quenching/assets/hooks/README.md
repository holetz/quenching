# assets/hooks/ — the OKF enforcement hook

Self-contained enforcement payload of the `quenching` plugin. Keeps a target
repo's `/.docs/` bundle aligned to OKF. **Nothing here is installed into a target** —
the plugin's own `hooks/hooks.json` wires the checker at
`${CLAUDE_PLUGIN_ROOT}/assets/hooks/okf-validate.py`, so it works in every repo that
has the plugin.

| File | Role |
| --- | --- |
| `okf-validate.py` | The OKF v0.1 conformance checker. Zero dependencies. Runs as a **CLI** (`okf-validate.py /.docs` — used by the skills and the verification step) or as a **hook** (reads the hook JSON on stdin). `--version` prints its version (kept in lockstep with the plugin `VERSION`). |
| `hooks-config.json` | The **defaults reference** for the `okfValidate` block: `enabled`, `warnAsError`, `blockOnFail`, `hardBlock`, `deadlineMs`, `stopScan`. A target that wants to override them maintains its own `.claude/hooks/hooks-config.json`. |
| `settings.snippet.json` | The wiring, kept as a **reference copy** of what `hooks/hooks.json` declares. Nothing merges it into a target any more. |

## What it checks (the OKF core)

- **Concept docs** (any `.md` that is not `index.md`/`log.md`): must have parseable
  frontmatter with a **non-empty `type`** (ERROR otherwise); missing recommended
  fields (`title`/`description`/`resource`/`timestamp`) → WARN.
- **`index.md`** (reserved listing): must **not** carry a concept `type` (ERROR).
  A non-root `index.md` must have **no frontmatter** (ERROR). The **root**
  `/.docs/index.md` may carry frontmatter but only `okf_version` (should be `"0.1"`).
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
  `/.docs/**` edit; `Stop` scans only when the marker exists, else exits on **one stat**
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

## Configuring a target

Nothing is copied and nothing is merged. The bundle root is the fixed `/.docs/` convention —
no config names it. The knobs (`enabled`, `warnAsError`, `blockOnFail`, `hardBlock`,
`deadlineMs`, `stopScan`, `ignoreGlobs`) are read from the target's own
`.claude/hooks/hooks-config.json` when it maintains one by hand. The copy in this
directory is the **defaults reference**, not something an align installs.

## Legacy copies

A repo that accepted the old install offer still has `okf-validate.py` under
`.claude/hooks/`, plus wiring in its `.claude/settings.json` pointing at it. Nothing
resolves to that copy any more, so it fires only because the old `settings.json` entry
still names it — the same checker running twice, one of them frozen at whatever version
it was installed at. `skills.py drift` reports it and `/docs:align` §5 offers to remove
it.
