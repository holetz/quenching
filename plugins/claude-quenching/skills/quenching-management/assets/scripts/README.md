# scripts

**Repo-level** executable logic, **outside the deployable artifact**: build/deploy,
derived artifact generators, quality checks, operational maintenance, and development
tooling. This is the **canonical home** of executables that the knowledge surface
invokes (the "common commands" in `CLAUDE.md`, the scripts that hooks call, what CI
runs). Organization is **by PURPOSE** (one subfolder per purpose), not by file type.

> General repo conventions: see [root CLAUDE.md](../CLAUDE.md). Replace the
> `<...>` placeholders with the repo's values; remove purpose subfolders that
> do not apply.

## How to run

There is **one** execution convention — `<derive from the repo>`. The most common
pattern in Python repos is running **from the root** with `-m` (so that `scripts.*`
imports resolve):

```bash
python -m scripts.<package>.<module>
```

> Replace with the repo's actual convention if different (`make <target>`,
> `npm run <script>`, `just <recipe>`). The invariant: **one** form, documented here,
> used by the entire surface (CLAUDE.md, hooks, CI).

## Structure (subfolders by purpose)

```
scripts/
├── ci/             # build & deploy — generates the deployable artifact, validates, runs in CI ("X defines Y")
├── <gen>/          # derived artifact generators (catalog/docs/manifest) from the source
├── checks/         # quality validations (exit with error if a problem is found)
├── maintenance/    # ONE-OFF operational routines (flags-off by default)
└── dev/            # LOCAL development tooling (OUTSIDE lint/CI scope)
```

> Install only the purposes that apply (a pure lib may have only `ci/` + `dev/`).
> Labels are derived from the repo: **purpose** is the canonical axis, not the string.

## Script map

This README is a **MAP** (module → what-it-does → entry), derivable from disk — one
table per subfolder. Keep it in sync: a new module gets a line; a removed module
loses its line.

### `ci/` — build & deploy

| Module | What it does | Entry |
| --- | --- | --- |
| `ci/<module>.py` | `<what it generates/validates/deploys>` — "X defines Y" rule: the source generates the artifact, which is **never** edited by hand | `<execution convention>` |

### `<gen>/` — derived artifact generators

| Module | What it does | Entry |
| --- | --- | --- |
| `<gen>/<module>.py` | `<generates derived artifact X from source Y>` (generated ≠ curated) | `<execution convention>` |

### `checks/` — quality

| Module | What it does | Entry |
| --- | --- | --- |
| `checks/<module>.py` | `<validates invariant X>`; exits with error (`SystemExit`) if a problem is found | `<execution convention>` |

### `maintenance/` — one-off operational

> Steps gated by **flags at the top of `main()`**, most **off** by
> default (poka-yoke against accidental destructive execution).

| Module | What it does | Entry |
| --- | --- | --- |
| `maintenance/<module>.py` | `<one-off operational routine: clone/backup/migration>` | `<execution convention>` |

### `dev/` — development tools

> **Outside lint/CI scope** (`scripts/dev/` in the linter's `exclude`): local
> tooling area.

| Module | What it does | Entry |
| --- | --- | --- |
| `dev/<module>.py` | `<local tool: diagnostics/conversion/startup>` | `<execution convention>` |

---

> _Skeleton installed by `quenching-management`. The complete specification
> of the organization (purposes / boundaries / CI scope + the
> thin-hook-calls-script and internal-skill × repo boundary) lives in
> `references/scripts-taxonomy.md` of the method._
