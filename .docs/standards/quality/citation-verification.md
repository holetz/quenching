---
type: standard
title: Citation verification
description: How citation-check.sh proves a rename's two halves both landed — the old name died and the new name was born, blind and with no allowlist — the three scope rules read from the script's own header (the instrument does not measure itself, .specs/ is out of scope, golden/eval fixtures are frozen data), that it runs manually and is documented rather than gated automatically (Open Decision 2, with a second real use case as the trigger to revisit), and why the "every red is a harness defect" precedent stays scoped to functional-checks.sh alone until citation-check.sh earns its own evidence (Open Decision 3, opportunistic)
resource: plugins/quenching/assets/checks/citation-check.sh
tags: [quality, verification, citations, automation]
timestamp: 2026-08-12
audience: both
authority: current
source: revisar-politica-de-assets-checks spec (task 1.1)
maintainer: quenching
---

# Citation verification

What it takes to claim a rename actually finished. The sibling
[surface-verification.md](surface-verification.md) covers whether a changed command **loads**;
this standard covers a narrower and cheaper question — whether every citation to a renamed name,
anywhere in the tracked tree, still resolves. `assets/checks/citation-check.sh` is the
implementation.

## The two halves, and why the cheap one is the trap

A rename has two halves. Half 1 measures that the **old** name died — no tracked file still
matches the retired script, namespace or command. Half 2 measures that the **new** name was
**born** — every cited path resolves to a file that exists, and every cited
`quenching:<ns>:<cmd>` corresponds to a body under `commands/**`.

A repository in which every citation points at nothing passes half 1 on its own — that is exactly
what a half-finished rename produces, and it is silent: the command registry is rebuilt at
**session start**, so the session that moves a body is structurally incapable of observing the
breakage it caused. Reading half 1 alone as success is the trap; both halves are required, and
half 2 is the one a rename actually gets wrong.

The sweep is **blind, with no allowlist**: historical mentions are rewritten to the new name like
every other citation, because git history holds the past, the docs describe the present, and a
check with content exceptions is a check people learn to ignore.

## The three scope rules, read from the script's own header

`citation-check.sh`'s header states three scope rules and is the source of truth for them — cited
here as implementation, never copied, because a paraphrase drifts from the regex it describes the
moment either one is edited alone:

1. **The instrument does not measure itself.** A check that greps for a retired string necessarily
   contains that string, so the script's own file is out of scope by construction. To keep that
   from becoming a hole, half 1 first proves it can *see* — a canary (the plugin's own name) that
   must survive every rename — before trusting a zero-hit result as clean rather than blind.
2. **`.specs/` is out of scope.** It is the planning workspace, the record of what was decided, not
   a description of the present — the same exclusion every task-level `verify:` in a spec plan
   applies.
3. **Golden fixtures and eval run logs are data, not citations.** A golden is stdout a pre-refactor
   script actually printed, frozen the day it was captured; an eval run log is a grading record of
   one dated invocation. Both necessarily keep quoting a name that no longer exists, forever, by
   design — measuring them as live citations would fail the fixture format itself, not a rename.

None of the three is an allowlist: no path is exempted by being on a list, and each is a statement
about what a tree is describing (the present vs. a frozen or historical record), not an exception
carved out for convenience.

## Who runs it, and when

**Manual and documented, not gated automatically** — decided by the human, 2026-08-11 (Open
Decision 2 of the spec that wrote this standard). Unlike `functional-checks.sh`
([surface-verification.md](surface-verification.md) §The harness belongs to the components
front), `citation-check.sh` is not wired into `/quenching:components:align`, into
`/quenching:specs:conclude`'s merge gate, or into any spec's `## Validation`. It is run by hand,
from the repo root, when a rename or a repo-wide restructuring makes half-finished citations
plausible — a precedent this repository already has one of
(`modularizar-specs-knowledge-components`, the spec that wrote the script).

**The trigger to revisit this decision is a second real use case**, not a schedule. One dated
manual invocation is a data point, not a pattern; automating on the strength of a single run would
be exactly the kind of unmeasured generalization §Scoped, not general below refuses to make about
the harness's own failure history.

## Scoped, not general: the "every red is a harness defect" rule does not extend here

`surface-verification.md` records a measured fact about `functional-checks.sh` alone: over the
whole `/.specs/archive/` record, every red run that harness ever produced traced to a defect in
itself, none to a surface regression. That fact was earned by a specific measurement, on a specific
harness, and it does not travel to `citation-check.sh` or `conclude-order-check.sh` by proximity —
no equivalent measurement exists for either, and `citation-check.sh` in particular has too little
run history to support one (it entered the tree on 2026-08-09).

There is a structural reason the two are unlikely to fail the same way even once measured:
`citation-check.sh` is deterministic and spends no agent session (~0.26s measured, against
`functional-checks.sh`'s full, non-deterministic `claude -p` runs). The defect class that produced
the harness rule — a cp1252 read, a hardcoded marketplace ref, a turn cap, a probe flaky across
identical runs — has no equivalent in a tool with no LLM in its loop. That is a reason to find the
rule *plausible* here too, never a reason to assert it: this standard does not claim what nobody
has measured.

**Open Decision 3 (2026-08-11) chose the opportunistic route**: no dedicated measurement campaign
for `citation-check.sh` or `conclude-order-check.sh`; a red run's cause is recorded when one
happens, and the rule above is revisited only on that evidence.

## What this does not cover

- **The citation-form rules themselves** — the registry name vs. `/quenching:<ns>:<cmd>` vs. a bare
  slash, and why a bare prefix would misname this repo's own local `/docs:storyteller` — are
  [naming/command-surface.md](../naming/command-surface.md)'s, cited by `citation-check.sh`'s own
  header rather than restated here.
- **Whether a changed command loads.** A citation resolving to a file proves the file exists, not
  that the session can invoke it — [surface-verification.md](surface-verification.md)'s question.
- **The `/.docs/` bundle's own internal link integrity.** `cq knowledge validate` covers a bundle
  citing itself, run as the `verify:` of the docs sweep; `citation-check.sh` measures the bundle
  citing the *plugin*, which has no other instrument — see
  [bundle-verification.md](bundle-verification.md) for the former.
