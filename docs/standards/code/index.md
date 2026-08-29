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

* [canonical-set-parsing.md](canonical-set-parsing.md) — How the shipped tools consume a declared
  set — slice it by declared membership and never by position, because an ordinal index is a claim
  about the set's shape that nothing re-checks when the set grows; why a byte-for-byte lockstep
  check proves the copies agree but never that the code reading them still means the same thing,
  so a membership invariant is owed its own assertion; and why a case list must exercise the
  function that ships rather than a copy of its rule written inside the selftest
* [conditional-projection-guards.md](conditional-projection-guards.md) — A projection that falls
  back to "store it whole" when its shape check refuses is invisible on the way down — so the
  guard must be asserted against the shape the contract writes TODAY, and a contract change that
  removes a frontmatter key has to be traced into every guard that named it, because the failure
  is a silent loss of a capability rather than an error anyone sees
* [file-relative-path-resolution.md](file-relative-path-resolution.md) — Every `__file__`-relative
  expression silently encodes how deep its module sits; moving a script into a package re-
  evaluates it somewhere else without erroring, and the two instances this repo measured failed in
  opposite directions — one turned a lockstep check off and exited 0, the other made a subcommand
  refuse forever
* [frontmatter-parser.md](frontmatter-parser.md) — The YAML subset `common/frontmatter.py` reads —
  the comment rule (a `#` opens a comment only at the start of a value or after whitespace, and
  never inside a quoted scalar), the canonical case list its tests hold it to, the anomaly
  sidecar, and why the union it now reads is wider than any of the three parsers it replaced
* [optional-payload-fields.md](optional-payload-fields.md) — Optional `cq specs` JSON fields use
  `null` for the absence of a usable answer, never a sentinel; the former `overview` projection
  and `summary` field are retired, and any future body projection must name one source and one
  shared detector
* [root-override-validation.md](root-override-validation.md) — Specs are provider-owned, so a root
  override cannot redirect them to a repository store; provider selection comes from the
  repository remote, unsupported legacy root settings refuse, and diagnostics report the same
  configuration fact without inventing a local tree
* [superseded-format-recognition.md](superseded-format-recognition.md) — How a recogniser is
  changed when the format it reads is superseded — the new pattern must be asserted against the
  OLD form, because a pattern that describes the new one correctly often matches the old one whole
  and yields a confident wrong answer with no finding; and a store's recogniser must separate "not
  mine" from "mine, but stale", because sending both to the same discard makes a half-migrated
  front vanish in silence

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
- **Present:** `optional-payload-fields` — off the list for the same reason: it governs the shape
  of one JSON field a payload projects, not a code convention that spans this package.
