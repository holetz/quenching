# `standards/naming/`

**Naming** conventions — the globally unique, predictable names this repo commits to. The
skeleton is oriented toward data naming (tables/columns/descriptions); this repo has no data, so
its naming surface is the plugin's **command surface** (skills and their command wrappers).

**Boundary:** `naming/` governs naming conventions; **code** symbol naming lives in
[../code/](../code/index.md); the classification/authoring of the skill surface lives in
[../automation/](../automation/index.md). One standard per file (files, not sub-folders); each
carries `type: standard` + a derived `resource:`; add each to [../index.md](../index.md).

## Candidate sub-standards

Break this subject **one concept per file**. The method evaluates each candidate against
the repo, generates the applicable ones (`file:line`-anchored, full OKF frontmatter), and
records the rest below as deferrals (never a silent skip):
`tables` · `columns` · `descriptions` · `schemas-catalogs`.

## Coverage / deferred sub-standards

Per-subject ledger the verify gate reads. A subject is "done" only when every candidate is
**present or listed here** with a one-line why.

- [command-surface.md](command-surface.md) — the plugin's command naming and namespacing (present)
- `tables` · `columns` · `descriptions` · `schemas-catalogs` — not applicable (this repo has no data)
