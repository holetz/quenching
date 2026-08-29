# `standards/quality/`

Quality — *observing correctness over time*: what is verified mechanically, what is left to a
reader, and at which severity.

**Boundary:** *observing correctness*, whatever the subject. In a data repo that means per-row
checks, drift and model monitoring; here it is the repo's own artifacts — the `/docs/` bundle and
the checks that hold it honest. The *modeling* that defines data lives in
[../data-modeling/](../data-modeling/index.md); the model lifecycle in
[../mlops/](../mlops/index.md). One standard per file (files, not sub-folders); each carries
`type: standard` + a derived `resource:`; add each to [../index.md](../index.md).

## Current docs

* [bundle-verification.md](bundle-verification.md) — What the knowledge front machine-checks
  versus what it leaves to a skill's prose self-check, when an invariant is owed a deterministic
  check, where an accepted gap is recorded, and the resource glob-set format
* [citation-verification.md](citation-verification.md) — How citation-check.sh proves a citation
  resolves against the base it claims — half 1 that the old name died and half 2 that the new name
  was born, blind and with no allowlist, and half 3 that the prose the plugin SHIPS promises only
  what the published skeleton delivers, since a command body and a reference are read inside a
  target checkout where our standards do not exist — the three scope rules read from the script's
  own header (the instrument does not measure itself, .specs/ is out of scope, golden/eval
  fixtures are frozen data), the spelling rule half 3 rests on (a markdown link promises a
  destination, a bare inline-code path names a doc the target may not have), that it runs manually
  and is documented rather than gated automatically (Open Decision 2, with a second real use case
  as the trigger to revisit), and why the "every red is a harness defect" precedent stays scoped
  to functional-checks.sh alone until citation-check.sh earns its own evidence (Open Decision 3,
  opportunistic)
* [empty-response-honesty.md](empty-response-honesty.md) — An empty response from a third-party
  transport is two states — one that never arrived and one that legitimately has nothing — and
  only one of them can be proved; the rule to refuse at the choke point where the proof is
  structural, to warn where there is only corroborated suspicion, and to never let the diagnostic
  refuse
* [parse-honesty.md](parse-honesty.md) — A verifier names its own parse failure instead of
  reporting it as a content gap — the sidecar shape that adds the signal without changing a return
  type, why the finding is a warn rather than an error, and the rule that a checker never gains a
  lossy transform without the diagnostic that reports it
* [finding-remedy-applicability.md](finding-remedy-applicability.md) — A declared remedy names an
  action the surface that emitted the finding actually offers — the measured case where the same
  CLI refused both actions it advised, why an inapplicable remedy teaches readers to ignore the
  whole findings output and not just that one item, and the refusal of its own that a case with no
  path still owes
* [prose-sweeps.md](prose-sweeps.md) — A find-and-replace over prose corrupts exactly the
  sentences that talk ABOUT the form being replaced — how to recognise those sites, why the check
  written to guard the sweep cannot see them, and the mitigation that survives both
* [computed-fact-prose-fanout.md](computed-fact-prose-fanout.md) — Any fact a tool computes and
  prose restates — a schema's fields, a surface's command count — fans out the moment it changes,
  and no checker sees it: why the validators are blind by construction, the two independent
  measurements this rule was set from, the grep on the fact's spelled-out form that finds the
  sites while the change is still cheap, a doc's own `description` as the nearest instance with
  its two listing consumers (one hand-maintained, one a GENERATED zone that is stale between
  sweeps by design), and why it belongs to the task that makes the change rather than to a later
  sweep
* [withdrawn-contract-residue.md](withdrawn-contract-residue.md) — When a change removes a
  contract rather than changing a computed value, its prose residue has no canonical spelling to
  grep for — the sites assert it in their own words — so `## Impact` must name the CLASS of
  documents that assert it and derive the file list mechanically; the five misses measured on one
  branch, why naming the file is not enough either, and why the reviewer's question is "what did
  this make false?" rather than "which files changed?"
* [prose-deletion-seams.md](prose-deletion-seams.md) — Removing prose damages the text left
  behind, not only the text never opened — the hard wrap makes the line a unit the sentence does
  not respect, an orphaned continuation is promoted under the neighbouring bullet rather than left
  as litter, and a grant's justification outlives the use that earned it; the three seams measured
  on one branch, why every checker stays green through all three, and the reading that closes them
* [prose-verify-pins-wording.md](prose-verify-pins-wording.md) — A check written as a grep over
  prose does not prove the prose — it pins it to the phrase the check named, and the resulting
  failure is ambiguous between "the text is wrong" and "the check named a phrase nobody agreed
  to"; how to write the assertion, how to read the failure, the third reading that is never
  permitted, and the negative face where the check forbids a string the spec itself requires
  elsewhere
* [selftest-mutation.md](selftest-mutation.md) — A test that has never been observed to fail is
  untested — the mutation pass that earns the claim, one mutation per rule the fixture exists to
  prove, why the pass is run once at authoring rather than wired into CI, and the graduation gate
  the repo's new tests/ suite has not yet cleared
* [unproven-capability-warning.md](unproven-capability-warning.md) — Where a caveat about a
  capability that ships without end-to-end proof belongs — the two failure shapes that decide it,
  the standing fact as a verifier finding and the moment-of-risk line once per process on stderr,
  why a per-operation warning is a permanent context tax and silence is not the alternative, and
  the one edit that retires both together
* [unanswerable-verify-lines.md](unanswerable-verify-lines.md) — A `verify:` whose verdict does
  not come from the state of the code — the pattern the shell mangles before it compares, the YAML
  scalar the parser truncates before it reads, the entry point that exited 0 without running
  anything — and the rule of exercising the line in both directions at the moment it is written,
  never at the moment it has to close
* [surface-verification.md](surface-verification.md) — How a change to the command surface is
  proven — a fresh process because the registry is built at session start, assertions on captured
  tool_use rather than prose, the five preconditions a functional check must satisfy to measure
  what it claims, why the harness belongs to the components front rather than the spec cycle and
  how to scope its cost, and how an ordering property is verified by running a real cycle

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
  whose subject moved underneath it — is covered as the resource-activity figure in
  [bundle-verification.md](bundle-verification.md).
