# `standards/ci-cd/`

Build and deploy — how code becomes a running artifact, "code defines YAML", manifest
generation, pipeline stages, versioning/release.

**Boundary:** the *build/deploy* path; the job/task framework that runs the work lives in
[../workflows/](../workflows/index.md); deploy *targets* and governance live in
[../platform/](../platform/index.md). One standard per file (files, not sub-folders); each
carries `type: standard` + a derived `resource:`; add each to [../index.md](../index.md).

## Current docs

* [versioning-release.md](versioning-release.md) — The source version surfaces that
  `cq specs release` bumps together, with the HUD manifest and every Claude marketplace entry moved to the same version

## Candidate sub-standards

Break this subject **one concept per file**. The method evaluates each candidate against
the repo, generates the applicable ones (`file:line`-anchored, full OKF frontmatter), and
records the rest below as deferrals (never a silent skip):
`build` · `deploy` · `manifest-generation` · `pipeline-stages` · `versioning-release`.

## Coverage / deferred sub-standards

Per-subject ledger the verify gate reads. A subject is "done" only when every candidate is
**present or listed here** with a one-line why.

- `versioning-release` — **present**: [versioning-release.md](versioning-release.md).
- `build` — **deferred, not applicable.** There is no build step: the plugin ships markdown
  command bodies and one dependency-free stdlib Python package, copied as-is.
- `deploy` — **deferred for product code.** Distribution is `cq deploy` into a target repository
  plus the HUD's marketplace upgrade; `cq deploy` is surface installation, not a product
  deployment, and nothing reaches a running environment.
- `manifest-generation` — **deferred.** Both manifests (`plugin.json`, `marketplace.json`) are
  hand-edited and small; nothing generates them today.
- `pipeline-stages` — **present, inline.** `.github/workflows/ci.yml` is the plugin's own pipeline:
  it runs on pushes to `main` and on pull requests (never on the `quenching` specs-store branch),
  with one run per ref (`concurrency` cancels superseded runs) and a timeout per job. Jobs: `gate`
  (Python 3.11 and 3.13 matrix; the 3.11 cell runs `scripts/verify_repo.sh` — one randomized,
  parallel suite pass under `pytest-randomly`/`pytest-xdist`/`pytest-cov`, measured against
  `.coverage-floor.json`, then the doctors and builds — and the 3.13 cell runs the same suite alone
  as a compatibility check, because the deterministic checks read interpreter-independent files),
  `lint` (`ruff check`, rules E and F configured in `pyproject.toml`) and `functional` (static only:
  `functional-checks.sh --selfcheck` and `--selftest`; CI has no `claude` CLI and measures no surface
  load, which runs under `QUENCHING_FUNCTIONAL=1 bash scripts/verify_repo.sh` and is required by `/release`).
  Actions are pinned by full commit SHA with the tag in a comment.

## The gate's temp root and worker count

The suite writes several hundred megabytes of temporary files per run. `scripts/verify_repo.sh`
resolves one root through `scripts/toolchain/tmproot.py` and exports it as `TMPDIR`/`TEMP`/`TMP`
before pytest starts, so every `tempfile` call, every xdist worker and every `git` child inherits it
with no test edited. The root is `$XDG_RUNTIME_DIR`, `/dev/shm` or a Windows Dev Drive when one of
them is a writable tmpfs that allows executing a temporary program and has at least 512 MB free;
otherwise it is the system temp dir and the gate prints a `NOTICE`. Each run creates
`quenching-gate-<pid>-XXXXXX` under the root and removes it on exit, including SIGINT and SIGTERM.
`COVERAGE_FILE` stays in `.quenching/coverage/`, outside that directory, because the trap would
otherwise delete the worker data before the report is combined and `cq proof ratchet` reads it.
`QUENCHING_TEST_TMPDIR` overrides the root, and `QUENCHING_TEST_WORKERS` sets the worker count
(`auto` by default) so concurrent gates can share the cores. A pytest spawned from inside a test
inherits its parent's slots and runs serially instead of queuing behind them. A direct `pytest` run
gets the same root from `quenching/tests/_paths.py`.

## Three tiers of test runs

The gate stays the only gate; what changes is how much of the suite it runs at each stage. A
narrower scope never replaces CI: `quenching/assets/bin/quenching/git/pull.py` reads every check and
refuses to merge anything but green, so the full run happens before the merge even when the local
close was scoped.

| Stage | Command | Suite |
| --- | --- | --- |
| a task | `python3 -m scripts.toolchain.test --affected` | the diff's tests; the `integration` layer is deferred and counted |
| a spec's close | `QUENCHING_TEST_SCOPE=affected bash scripts/verify_repo.sh` | the same selection inside the whole gate; the coverage floor reports `SKIPPED` |
| CI and `/release` | `bash scripts/verify_repo.sh` with `QUENCHING_FULL_GATE=1` | everything, `integration` included, the floor enforced |

`scripts/toolchain/affected.py` maps each source surface to the tests that cover it, adds the tests
whose direct imports reach a changed module, and takes the diff from the merge base plus the working
tree plus untracked files. It answers "the whole suite" whenever it cannot be sure — a global file
(`pyproject.toml`, `scripts/toolchain/`, `quenching/assets/bin/quenching/common/`,
`quenching/references/`), a path no rule covers, a rule naming a test that no longer exists, a
deleted test, an unresolvable base — and prints the reason instead of guessing. A change under
`site/` selects nothing: the close prints `the diff reaches no test` rather than a green over an
empty run, and a `docs/` change runs the tests that read the navigation.

`QUENCHING_TEST_BASE` moves the merge base of either mode (default `origin/main`), which is what a
task lane points at `HEAD` to measure its own working tree. `QUENCHING_TEST_SCOPE` accepts only
`full` and `affected`; `QUENCHING_FULL_GATE=1` overrides a scope that leaked into the shell and is
what `/release` passes, so a tag is never decided on a subset.
