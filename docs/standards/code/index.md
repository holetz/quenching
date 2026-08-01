# `standards/code/`

Code conventions — imports, formatting/lint, typing, **symbol** naming, dependency
pins, error handling, logging, docstrings, testing conventions.

**Boundary:** `code/` governs **symbols** (code); **data** naming (tables/columns) lives
in [../naming/](../naming/index.md). One standard per file — flat files by default, but when a
subject fractures into a cluster of siblings (e.g. symbol naming across classes / functions /
modules / variables), fold it into a subfolder (`symbol-naming/{classes,functions,…}.md`) with
its own `index.md`, rather than a run of `symbol-naming-*.md` files. Each standard carries
`type: standard` + a derived `resource:`; add each to [../index.md](../index.md).

## Current docs

* [canonical-set-parsing.md](canonical-set-parsing.md) — how a declared set is consumed: slice it by
  declared membership and never by position, why a byte-for-byte lockstep check proves the copies
  agree but never that the code reading them still means the same, so a membership invariant is owed
  its own assertion, and why a case list must exercise the function that ships rather than a copy of
  its rule written inside the selftest.
* [frontmatter-parsing.md](frontmatter-parsing.md) — the YAML subset the three shipped tools read:
  the comment rule, the canonical case list all three must decide identically, the anomaly set each
  must be able to name, and the three-copy lockstep obligation that stands in for the shared module
  they cannot have.

## Candidate sub-standards

Break this subject **one concept per file**. The method evaluates each candidate against
the repo, generates the applicable ones (`file:line`-anchored, full OKF frontmatter), and
records the rest below as deferrals (never a silent skip):
`imports` · `format-lint` · `typing` · `symbol-naming` · `dependencies-pins` · `error-handling` · `logging` · `docstrings` · `testing-conventions`.

## Coverage / deferred sub-standards

Per-subject ledger the verify gate reads. A subject is "done" only when every candidate is
**present or listed here** with a one-line why.

- `imports` · `format-lint` · `typing` · `symbol-naming` · `dependencies-pins` · `error-handling` ·
  `logging` · `docstrings` — **deferred, not yet needed.** The repo's only code is three
  zero-dependency stdlib scripts written in one house style; none of these has been contested.
- `testing-conventions` — **deferred, covered elsewhere for now.** There is no test framework here;
  what stands in for one is each tool's own `selftest` and
  [../quality/surface-verification.md](../quality/surface-verification.md).
- **Present:** `frontmatter-parsing` — not on the candidate list above, because it is a contract
  *between* the three scripts rather than a convention within one.
