# `standards/ci-cd/`

Build and deploy — how code becomes a running artifact, "code defines YAML", manifest
generation, pipeline stages, versioning/release.

**Boundary:** the *build/deploy* path; the job/task framework that runs the work lives in
[../workflows/](../workflows/index.md); deploy *targets* and governance live in
[../platform/](../platform/index.md). One standard per file (files, not sub-folders); each
carries `type: standard` + a derived `resource:`; add each to [../index.md](../index.md).

## Current docs

* [versioning-release.md](versioning-release.md) — the four version strings a release bumps
  together, and why two independent consumers (Claude Code's upgrade detection, and each align
  comparing an installed tool's `--version`) make a partial bump fail in two different ways.

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
- `pipeline-stages` — **deferred, not applicable.** There is no CI pipeline for the plugin itself;
  the verification gates are the test suite and `functional-checks.sh`, run locally.
