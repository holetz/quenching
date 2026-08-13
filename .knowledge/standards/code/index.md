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
* [file-relative-path-resolution.md](file-relative-path-resolution.md) — every `__file__`-relative
  expression encodes how deep its module sits, so packaging re-evaluates it somewhere else without
  erroring: the two instances measured here failed in opposite directions — one switched an
  embedded-asset lockstep off and exited 0, the other made a subcommand refuse forever — and the
  rule that follows is to assert the resolved path rather than observe that a check passed.
* [frontmatter-parser.md](frontmatter-parser.md) — the YAML subset `common/frontmatter.py` reads:
  the comment rule, the canonical case list its tests hold it to, and the anomaly sidecar — one
  parser now, reading the union of what the three retired scripts used to read separately.
* [superseded-format-recognition.md](superseded-format-recognition.md) — how a recogniser is changed
  when the format it reads is superseded: the new pattern must be asserted against the OLD form,
  because one that describes the new form correctly often matches the old one whole and answers
  confidently with no finding; and a store's recogniser must separate "not mine" from "mine, but
  stale", because sending both to one discard makes a half-migrated front vanish in silence.

## Candidate sub-standards

Break this subject **one concept per file**. The method evaluates each candidate against
the repo, generates the applicable ones (`file:line`-anchored, full OKF frontmatter), and
records the rest below as deferrals (never a silent skip):
`imports` · `format-lint` · `typing` · `symbol-naming` · `dependencies-pins` · `error-handling` · `logging` · `docstrings` · `testing-conventions`.

## Coverage / deferred sub-standards

Per-subject ledger the verify gate reads. A subject is "done" only when every candidate is
**present or listed here** with a one-line why.

- `imports` · `format-lint` · `typing` · `symbol-naming` · `dependencies-pins` · `error-handling` ·
  `logging` · `docstrings` — **deferred, not yet needed.** The repo's only code is one
  zero-dependency stdlib package behind a single `cq` entry point, written in one house style; none
  of these has been contested.
- `testing-conventions` — **deferred, and the reason it was deferred is gone.** This entry read
  "there is no test framework here; what stands in for one is each tool's own `selftest`" until the
  `modularizar-specs-knowledge-components` spec added `tests/` (stdlib `unittest`, no external
  dependency) and retired `selftest` from every pillar. The conventions that suite already follows —
  the case-table-is-the-contract shape, the named-skip discipline in `test_golden.py` — are not
  written down anywhere; they are owed a standard, not another deferral.
- **Present:** `frontmatter-parser` — not on the candidate list above, because it is the contract
  every pillar's own `common/frontmatter.py` import holds to, rather than a convention within one.
- **Present:** `file-relative-path-resolution` — likewise off the list: it governs one construct
  across every module, not a convention inside one.
