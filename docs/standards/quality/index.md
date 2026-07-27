# `standards/quality/`

Quality — *observing correctness over time*: what is verified mechanically, what is left to a
reader, and at which severity.

**Boundary:** *observing correctness*, whatever the subject. In a data repo that means per-row
checks, drift and model monitoring; here it is the repo's own artifacts — the `docs/` bundle and
the checks that hold it honest. The *modeling* that defines data lives in
[../data-modeling/](../data-modeling/index.md); the model lifecycle in
[../mlops/](../mlops/index.md). One standard per file (files, not sub-folders); each carries
`type: standard` + a derived `resource:`; add each to [../index.md](../index.md).

## Current docs

* [bundle-verification.md](bundle-verification.md) — what the `docs/` front machine-checks versus
  what it leaves to a skill's prose self-check, when an invariant is owed a deterministic check,
  and the `resource` glob-set format.
* [surface-verification.md](surface-verification.md) — how a change to the command surface is
  proven: a fresh process because the registry is built at session start, assertions on captured
  `tool_use` rather than prose, and the three preconditions a functional check must satisfy.

## Candidate sub-standards

Break this subject **one concept per file**. The method evaluates each candidate against
the repo, generates the applicable ones (`file:line`-anchored, full OKF frontmatter), and
records the rest below as deferrals (never a silent skip):
`row-checks` · `data-drift` · `model-monitoring` · `stability`.

## Coverage / deferred sub-standards

Per-subject ledger the verify gate reads. A subject is "done" only when every candidate is
**present or listed here** with a one-line why.

- `row-checks` — **deferred, not applicable.** This repository holds no data: it is markdown
  skills plus two stdlib Python scripts. There are no rows to check.
- `data-drift` — **deferred, not applicable.** Same reason; no dataset exists to drift.
- `model-monitoring` — **deferred, not applicable.** No model is trained or served here.
- `stability` — **deferred, not applicable** in its data sense. The analogous concern — a doc
  whose subject moved underneath it — is covered as `stale-doc` in
  [bundle-verification.md](bundle-verification.md).
