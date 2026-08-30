---
type: concept
title: Test layering separates location, reach and execution order
description: A test directory answers which layer owns a test, a derived marker answers how a runner selects it, a coverage ratchet preserves progress over a declared surface, and randomized collection exposes order dependence
resource: docs/standards/architecture/proof-front.md, https://docs.pytest.org/en/stable/example/markers.html
tags: [testing, automation, layers, coverage, fixtures, order-independence]
timestamp: 2026-08-30
audience: both
authority: background
source: proof-front contract — the measured suite shape and the generic rationale captured while defining spec 1047
maintainer: quenching
---

# Test layering separates location, reach and execution order

A test suite becomes easier to select when three questions have different answers. The directory
says which layer owns the test. The marker says how the runner may select it. The fixture library
says where setup shared by several modules lives. Combining those questions in one hand-applied
label makes the suite depend on memory; keeping them separate makes the structure inspectable.

## Directory and marker answer different questions

A directory is durable ownership. `tests/unit/` can mean that a test belongs to the unit layer even
when a contributor never remembers a marker spelling. A marker is a run-time selection handle:
`pytest -m unit` asks the runner to select tests with that marker. When a collection hook derives
the marker from the directory, the two declarations cannot disagree and a newly added test gets a
layer by choosing its home.

The directory remains the source of the layer identity. The marker is a projection for the test
runner, not a second choice for the author to keep aligned. Registering derived markers and enabling
strict marker checking then turns a misspelled selection into a visible configuration error.

## A coverage ratchet preserves direction

A coverage percentage is useful only when its measured surface is the one the repository means to
protect. A ratchet stores the current floor per source root and permits the gate to move upward,
never downward. A fixed target such as `80%` produces a different incentive: when the real code is
below it, authors can add cheap tests around already-covered branches just to cross the threshold,
while the unmeasured product remains untouched.

The ratchet therefore records progress from the repository's current evidence. The gate names the
roots it measures, checks each root against its stored floor, and updates the floor only after a
successful run. A lower result is a regression even when the total percentage looks unchanged.

## Randomized order tests a boundary a green run cannot

Repeatedly running a stable suite repeats its collection order. It does not test whether one test's
mutation leaks into the next test, whether a process-wide registry is reset, or whether a fixture
depends on a side effect that happened earlier. A randomized-order pass changes that hidden input
while keeping the assertions and code fixed.

One passing permutation is evidence, not a proof of every permutation. Repeating the pass across
different seeds gives the repository a concrete check for order dependence and makes the seed part
of a failure report. The useful claim is therefore bounded: the suite passed under the sampled
orders, not that order dependence is impossible.

## Fixture libraries prevent structural copies

When two test modules need the same setup, a shared fixture belongs in the fixture library visible to
both modules. Defining the same fixture name in two modules is a structural copy even when the two
bodies happen to be identical today; the copies can drift independently tomorrow. A root
`conftest.py` may bootstrap the test environment, while domain fixtures stay in the library where
their ownership and reuse are visible.
