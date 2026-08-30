---
type: standard
title: Proof front
description: The target repository's canonical verification surface — layered tests, explicit fixture reach, measured source roots, a coverage ratchet, order evidence and a CI gate
resource: docs/standards/architecture/align-surface.md, docs/standards/quality/selftest-mutation.md, docs/standards/quality/surface-verification.md, plugins/quenching/assets/references/proof-align/target-structure.md, plugins/quenching/assets/references/proof-align/layer-contract.md, plugins/quenching/assets/references/proof-align/gate-contract.md
tags: [architecture, proof, tests, coverage, verification]
timestamp: 2026-08-30
audience: both
authority: current
source: spec 1047 — Declare the proof front
maintainer: quenching
---

# Proof front

The proof front is the verification surface a target repository converges toward. It makes the
suite's layers, fixtures, measured source roots, order evidence and CI gate explicit without
dictating which tests a product must have. The front is a contract for evidence, not a promise
that every adopting repository already has every layer.

<!-- rules -->

## The canonical tree

An adopting repository has one proof root, `tests/` by default. The root owns the suite's entry
contract and its generated index; layer directories own the tests and their derived markers:

```text
tests/
├── README.md             # generated proof-front index and declared scope
├── conftest.py           # thin bootstrap only
├── fixtures/             # shared fixtures used by more than one test module
├── unit/                 # isolated functions and classes
├── contract/             # repository-facing interfaces and schemas
├── data/                 # optional; only when the repo declares a data layer
└── integration/          # sessions, services and external boundaries
```

The names `unit`, `contract`, `data` and `integration` are the recommended layer vocabulary. A
repository may use another layer name when its proof standard declares the meaning and the
directory projects one stable marker. `data/` is conditional: a repository that declares no data
transformation or data-product boundary does not create an empty data layer merely to satisfy the
tree.

The target-structure, layer and gate details are self-contained in the proof-front references:

- [target structure](../../../plugins/quenching/assets/references/proof-align/target-structure.md)
  owns the tree, root and bootstrap shape;
- [layer contract](../../../plugins/quenching/assets/references/proof-align/layer-contract.md)
  owns layer meaning, derived markers and fixture reach;
- [gate contract](../../../plugins/quenching/assets/references/proof-align/gate-contract.md)
  owns measured surfaces, floors, order evidence, CI and entry-point proof.

## Layers and derived markers

Every test belongs to one layer directory. Its runner marker is derived from that directory during
collection; authors do not apply a second, hand-written layer marker. A test that genuinely spans
boundaries belongs to the narrowest contract that can state its assertion, while the wider reach
of its fixtures is declared separately.

The layer contract distinguishes four concerns:

1. **Classification:** the directory says what kind of evidence the test supplies.
2. **Projection:** collection derives the marker from the directory, so the directory and marker
   cannot silently disagree.
3. **Fixture ownership:** a fixture used by one module stays there; a fixture reused by multiple
   modules belongs in `tests/fixtures/` with its reach recorded.
4. **Data conditionality:** a `data/` layer is present only when the repository declares a data
   boundary; its absence is not a defect for a repository without one.

The layer contract defines `pf-unlayered`, `pf-unmarked`, `pf-loose-fixture` and
`pf-fat-conftest`. This standard names the codes and their owner; it does not duplicate their
finding logic.

The `data` layer is therefore **recommended when declared, never mandatory by the plugin**. The
repository's own source and product boundaries decide whether data transformations are a distinct
kind of evidence. A target that declares that boundary may not silently omit the layer; a target
that does not declare it does not create an empty directory for symmetry.

## Fixture reach

Every shared fixture declares the furthest state it may touch. The closed enumeration is:

| Reach | Meaning |
| --- | --- |
| `nothing` | Pure values or factories; no repository, process or service state. |
| `tree` | Filesystem state inside the test tree or a temporary checkout. |
| `session` | A process, database session, Spark session or equivalent runtime. |
| `workspace` | A shared external workspace, service, catalog or other environment boundary. |
| `custom:<reason>` | An explicit escape whose reason is reported and not graded by the default gate. |

`custom:<reason>` is an escape valve, not a fifth inferred class. A verifier reports it so a human
can decide whether a new reach is warranted; it does not award or remove proof credit on its own.

## The measured surface

The proof front declares which source roots are measured by the suite. Coverage, floor and ratchet
claims apply to that declared set only; an unmeasured product surface cannot borrow the suite's
coverage number. The generated `tests/README.md` records the roots and the command that measures
them.

A **coverage ratchet** is monotonic per source root: after a successful gate, the recorded floor
may rise to the measured value but may never fall. The front does not impose a universal
percentage. A repository with no meaningful measurable source root records that decision and its
reason rather than publishing an empty green number.

## Gate rules

The verification gate carries five rules:

1. The measured surface is declared and every floor names the source root it protects.
2. The suite runs all declared layers; an empty declared layer is reported, while a conditional
   layer that the repository does not claim is omitted.
3. The gate does not stop at the first failure; it emits the evidence needed to repair the suite
   as a whole.
4. Order independence is exercised with randomized or otherwise declared ordering evidence, not
   assumed from one serial run.
5. CI runs the same proof contract and the active operations entry points that the repository
   presents as part of its interface have an explicit test or an explicit not-applicable record.

The gate contract defines `pf-unmeasured-surface`, `pf-no-floor`, `pf-stop-first`,
`pf-order-unproven`, `pf-no-ci`, `pf-empty-layer` and the conditional `pf-untested-entrypoint`.

## Finding ownership

The proof vocabulary is stable across target repositories. Each code has one owning reference so
the standard remains a map rather than a second checker specification:

| Codes | Owner |
| --- | --- |
| `pf-unlayered`, `pf-unmarked`, `pf-loose-fixture`, `pf-fat-conftest` | layer contract |
| `pf-unmeasured-surface`, `pf-no-floor`, `pf-stop-first`, `pf-order-unproven`, `pf-no-ci`, `pf-empty-layer`, `pf-untested-entrypoint` | gate contract |

The gate treats `pf-untested-entrypoint` as conditional on the target declaring an operations
front. A repository without that front records the condition as not applicable; it does not create
a synthetic operations test to make the proof count look complete.

## Why the name is `proof` and not `tests`

`tests` names an implementation location; `proof` names the evidence the location is responsible
for producing. The distinction follows the one-axis naming test in
[command-surface.md](../naming/command-surface.md): this front owns a kind of repository evidence,
not every file that happens to end in `_test` or `test_`. A target may keep compatibility paths or
additional test tools, but the proof front gives the evidence a stable contract and a name that can
be used by aligners, CI and documentation without pretending that a directory alone proves
anything.

## Why layers are declared rather than files imposed

The front declares layer meanings and gate evidence; it does not impose a file list on a target
whose product boundaries are different. This is the same scope boundary that
[align-surface.md](align-surface.md) applies to every local front: the align converges artifacts
that have an applicable contract and reports source gaps, but it does not invent a capability to
make a count look complete. A layer is consequently required only when the repository claims that
kind of evidence, while a declared layer must have a readable meaning and a non-empty proof plan.

## Boundary with the rest of the plugin

The proof front owns the target repository's test evidence. The aligned-front column and the
probe-before-inventory rule are owned by
[align-surface.md](align-surface.md); command naming and invocation are owned by the command
surface standard. The proof front may test those surfaces, but it does not re-home their contracts
or become a second automation router.

<!-- rationale -->

The target tree is a recommendation with explicit conditionality because a layer is useful only
when it names a kind of evidence the repository actually produces. A directory without a meaning
is ceremony, and an empty required directory teaches a verifier to reward shape instead of proof.

Derived markers keep the two ways of naming a layer from drifting. Fixture reach is separate because
the same test layer can use a pure value, a temporary tree or a shared workspace; putting that
dimension into the layer name would multiply directories without making isolation clearer.

The measured-surface and ratchet rules prevent a percentage from becoming a portable claim detached
from the code it measures. Order and CI rules complete the evidence boundary: a suite that passes
only in one file order or only on a developer machine has not proved the interface it advertises.

The front follows the architecture principle in [align-surface.md](align-surface.md): one local
front has one owner and one probe. It therefore exposes proof as a target tree and gate while
leaving the conductors that invoke it to their own command contracts.
