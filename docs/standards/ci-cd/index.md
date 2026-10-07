# `standards/ci-cd/`

Build and deploy — how code becomes a running artifact, "code defines YAML", manifest
generation, pipeline stages, versioning/release.

**Boundary:** the *build/deploy* path; the job/task framework that runs the work lives in
[../workflows/](../workflows/index.md); deploy *targets* and governance live in
[../platform/](../platform/index.md). One standard per file (files, not sub-folders); each
carries `type: standard` + a derived `resource:`; add each to [../index.md](../index.md).

## Current docs

* [versioning-release.md](versioning-release.md) — The four source version surfaces that
  `cq specs release` bumps together, with the generated Codex sibling refreshed from the same source version

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
- `deploy` — **deferred, not applicable.** Distribution is the marketplace manifest plus Claude
  Code's own plugin upgrade; nothing is deployed to a running environment.
- `manifest-generation` — **deferred.** Both manifests (`plugin.json`, `marketplace.json`) are
  hand-edited and small; nothing generates them today.
- `pipeline-stages` — **present, inline.** `.github/workflows/ci.yml` is the plugin's own pipeline:
  it runs on pushes to `main` and on pull requests (never on the `quenching` specs-store branch),
  with one run per ref (`concurrency` cancels superseded runs) and a timeout per job. Jobs: `gate`
  (Python 3.11 and 3.13 matrix; `scripts/verify_repo.sh`, which measures coverage against
  `.coverage-floor.json`, then the suite again in randomized order), `lint` (`ruff check`, rules E
  and F configured in `pyproject.toml`) and `functional` (`functional-checks.sh --selfcheck`, then
  the full run where exit 2 is reported as inconclusive and neither passes nor fails the job).
  Actions are pinned by full commit SHA with the tag in a comment.
