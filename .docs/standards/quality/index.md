# `standards/quality/`

Quality — *observing correctness over time*: what is verified mechanically, what is left to a
reader, and at which severity.

**Boundary:** *observing correctness*, whatever the subject. In a data repo that means per-row
checks, drift and model monitoring; here it is the repo's own artifacts — the `/.docs/` bundle and
the checks that hold it honest. The *modeling* that defines data lives in
[../data-modeling/](../data-modeling/index.md); the model lifecycle in
[../mlops/](../mlops/index.md). One standard per file (files, not sub-folders); each carries
`type: standard` + a derived `resource:`; add each to [../index.md](../index.md).

## Current docs

* [bundle-verification.md](bundle-verification.md) — what the `knowledge` front machine-checks versus
  what it leaves to a skill's prose self-check, when an invariant is owed a deterministic check,
  where an accepted gap is recorded, and the `resource` glob-set format.
* [parse-honesty.md](parse-honesty.md) — a verifier names its own parse failure instead of reporting
  it as a content gap: the sidecar that adds the signal without changing a return type, why the
  finding is a warn, and why a lossy transform never ships without the diagnostic for it.
* [prose-sweeps.md](prose-sweeps.md) — a mechanical find-and-replace over prose corrupts exactly the
  sentences that talk *about* the form being swept, the checker that guards the sweep reports them
  clean, and the mitigation is to write a mention as a placeholder rather than an instance.
* [computed-fact-prose-fanout.md](computed-fact-prose-fanout.md) — any fact a tool computes and
  prose restates ages every site that spells it out, and no checker sees it: why each validator is
  blind by construction, the two measurements the rule was set from, the grep on the fact's literal
  form that finds the sites, and why it belongs to the task that makes the change.
* [withdrawn-contract-residue.md](withdrawn-contract-residue.md) — the sibling case where nothing
  computes the fact: a *removed* contract's residue has no canonical spelling to grep, so `## Impact`
  must name the class of documents asserting it and derive the list mechanically — the five misses
  measured on one branch, why naming the file is not enough either, and the reviewer's question.
* [prose-deletion-seams.md](prose-deletion-seams.md) — the complement to both: a deletion damages
  the text it leaves behind, not only the text it never opened — the hard wrap makes the line a unit
  the sentence does not respect, an orphaned continuation is promoted under the neighbouring bullet,
  and a grant's justification outlives the use that earned it.
* [selftest-mutation.md](selftest-mutation.md) — a test that has never been observed to fail is
  untested: the authoring-time mutation pass, one mutation per rule the fixture exists to prove,
  and the gate the repo's tests/ suite has not yet cleared, rule by rule.
* [unproven-capability-warning.md](unproven-capability-warning.md) — where a caveat about a
  capability that ships without end-to-end proof belongs: the two failure shapes that decide it, the
  standing fact as a verifier finding and the moment-of-risk line once per process on stderr, why a
  per-operation warning is a permanent context tax and silence is not the alternative, and the one
  edit that retires both together.
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
