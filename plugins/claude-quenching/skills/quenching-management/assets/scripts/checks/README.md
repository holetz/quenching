# scripts/checks — quality

**Data/code quality validations** run on demand or in CI: they verify invariants
and **exit with error** (`SystemExit`/exit≠0) when a problem is found, to fail the
pipeline.

**Validates, does not generate or mutate** (distinct from `ci/`/`maintenance/`). This
is the natural home for a **generic validation runner** that a validation hook can
invoke (the hooks-call-scripts doctrine applied to "validate before completing").

## The validation script that the `run-validation.py` hook calls

The Stop hook `run-validation.py` (in `.claude/hooks/`) is **thin**: it only invokes
the **validation script that lives HERE**, configured in
`runValidation.validateScript` (in `hooks-config.json`) — the **validation logic
does not live in the hook**, it lives in this `scripts/checks/<validate>`. Default
empty ⇒ the hook stays **inert** until the repo wires up the path.

> **Example for a Python repo** (the FORM, not a fixed mold): a
> `scripts/checks/validate.py` that receives the changed files as args and runs, in
> order, **`ruff check --fix`** (fix all) + **`ruff format`** + **`pyright`**, exiting
> with error if any problem remains. A Go repo would run `go vet`/`gofmt`; a TS repo,
> `tsc`/`eslint --fix`. The **concrete script belongs to the repo** (it would couple
> to a language if shipped in the package) — write it here and point `validateScript`
> to it.

> Replace/add the real modules and register each one in the map at
> [../README.md](../README.md). Remove this folder if the repo has no custom checks.
