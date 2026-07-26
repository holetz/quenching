# Baseline — the docs/ front before any check is added

Recorded by task 1.2 with `okf-validate.py` at v1.1.0, before section 2 touches it, so a new
check that regresses an existing surface is visible as a diff against a number rather than an
impression.

On this machine `python3`/`py` resolve to the Windows Store stub; every command below was run
with the real interpreter at
`C:\Users\<user>\AppData\Local\Programs\Python\Python312\python.exe` (CLAUDE.md §Verifying
changes).

## Conformance — every surface clean at v1.1.0

| Surface | Command | Result |
| --- | --- | --- |
| Shipped skeleton | `okf-validate.py assets/docs` | 0 error(s), 0 warning(s) · exit 0 |
| Backlog listing root | `okf-validate.py assets/specs/backlog --listing-root` | 0 error(s), 0 warning(s) · exit 0 |
| This repo's own bundle | `okf-validate.py docs` | 0 error(s), 0 warning(s) · exit 0 |
| Task 1.1 fixture | `okf-validate.py <fixture>/docs --json` | `[]` · exit 0 |

The fixture line is the control the rest of the plan depends on: it is **clean today**, so each
code added in sections 2 and 3 must surface as exactly one new finding, with no pre-existing
noise to disentangle it from.

## Version lockstep

`VERSION` 1.1.0 · `specs.py --version` 1.1.0 · `okf-validate.py --version` 1.1.0 — agree.

## Density — the signal that motivated the plan

Measured over this repository's own `docs/` bundle.

| Metric | Count |
| --- | ---: |
| Markdown files | 33 |
| `index.md` listings | 24 |
| `log.md` | 2 |
| Exempt (`CLAUDE.md`, `QUENCHING.md`) | 2 |
| **Concept docs** | **5** |
| Glossary terms | 4 |

| Home | Concept docs |
| --- | ---: |
| `standards/` | 4 |
| `knowledge/` | 1 |
| `catalog/` | 0 |
| `documentation/` | 0 |
| `reference/` | 0 |
| `vision/` | 0 |

Four of six homes are installed and empty — the shape the proposal calls "structural conformance
compatible with a knowledge base that knows nothing". All four validate clean.

## Two drifts from the proposal's stated figures

The proposal was written on 2026-07-25 against a tree that has since moved. Neither changes the
plan's argument; both change a number a later task asserts.

- **Glossary: 4 terms, not 1.** The proposal's "still carries the shipped seed placeholder as its
  only entry" was true when written. The archived `refine-and-execute-specs-flow` distillation
  (commit `3c18cee`) replaced the placeholder with four real terms — verification policy, failure
  budget, `[P]` marker, refinement record. **Task 4.5 asserts a one-entry glossary and must be
  read as four.** The shipped seed at `assets/docs/knowledge/glossary.md` is untouched by that
  commit and still carries both the placeholder and the self-pointing `resource: docs/**` that
  task 3.4 fixes.
- **`index.md`: 24, not 21.** The `standards/` subject subfolders each carry their own listing.
  No task asserts this figure; it is recorded so the next reader does not re-derive it.
