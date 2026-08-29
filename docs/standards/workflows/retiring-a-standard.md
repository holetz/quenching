---
type: standard
title: Retiring a standard — removal, the stamp, and the review as the net
description: How a bundle standard is retired — removal, never deprecation (the verb is `git rm`; a doc that survives annotated becomes a ritual nobody acts on); the inheriting doc carries the `retired with <doc> (<spec>, <data>)` stamp in its `source:` and in its body; the citation sweep is human and `## Impact` must name the class of docs that cite it; the listing's GENERATED zone is rebuilt in the same movement; and the branch review is the net — with resource activity read as a figure, never as a failure
resource: /docs/**, /.specs/**
tags: [workflows, docs, bundle, retirement]
timestamp: 2026-08-27
audience: both
authority: background
source: extensible-surface-and-budget-retirement plan, executed at close-out — tasks 2.1–2.3 deleted context-budget.md and re-pointed its citations, the inheriting note in context-discipline.md, and the review that caught the strays (2026-08-06); the missing index row this procedure lists first was itself the one stray the review did not catch
maintainer: quenching
---

# Retiring a standard — removal, the stamp, and the review as the net

Retiring a bundle standard is **removal, not deprecation**. A doc that survives annotated
(`deprecated:`, a footnote, some "historical" prose) becomes a ritual nobody acts on: the reader
goes on paying for the text every session, with no way to know the rule was retired. The verb for
retiring is `git rm`; what stays is what the inheriting doc records (below).

The procedure below has been executed once in this home — `context-budget.md`, retired on
2026-08-06 by the `extensible-surface-and-budget-retirement` spec — and the error it lists first
is the stray that that spec's own review let through. It is not a proof of repeatability
(`authority: background`), it is the record of what happened.

## The procedure

1. **The retiring spec lists what cites the doc, and `## Impact` names the CLASS of the docs that
   cite it** — see [withdrawn-contract-residue.md](../quality/withdrawn-contract-residue.md). The
   opposite was measured: a citation of a removed contract has no canonical spelling to grep for,
   each site asserts it in its own words. The citations the spec knows about are re-pointed as
   tasks; the ones it does not know about are what the review catches.
2. **The listing is rebuilt in the same movement.** The installed standard goes into the subfolder
   (the home's `index.md`) AND into the `GENERATED` zone of `standards/index.md` — both, in the same
   commit as the `git rm`. A doc whose row is missing from the GENERATED zone is an `index-orphan`
   that **no checker sees** (the resource-activity figure only speaks where a `resource:` names the
   file, and it has never been a finding — the zone is validated by nobody). That is exactly what
   happened on the first execution: the subfolder was updated, the zone was not, and the review did
   not catch it.
3. **The inheriting doc carries the stamp.** The doc that inherits the ground of the one that left
   records, in its `source:` and in its body: `retired with <retired doc> (<spec>, <data>)`. It is
   the only place where the history of what vanished stays alive — and it is what the future reader
   consults to find out what happened and why. On the first execution, `context-discipline.md` came
   to close with "The measurement history behind the integral, 344-turn run included, retired with
   context-budget.md; this file owns what to *do* about it".
4. **The stray sweep is human, and the branch review is the net.** No checker separates a citation
   that talks ABOUT the retired doc (correct as it stands, history) from one that invokes it as a
   live rule — the same mention/use judgment [prose-sweeps.md](../quality/prose-sweeps.md)
   declares invisible to a regex. The inheriting doc's resource activity is a figure, never a
   finding and much less a gate failure; whoever retires assumes the conclude's review will find one
   or two orphan sites — on the
   first execution there were four (the glossary ×2, one installed payload, one command body).

## What retirement is not

- **It is not a version bump.** The four-artifact lockstep is the release's act
  ([versioning-release.md](../ci-cd/versioning-release.md) — the bump happens on the primary branch,
  at the release, never at the conclude and never as a task). Retiring a standard does not touch
  VERSION.
- **It is not the same as retiring a reserved file.** A retired reserved artifact **keeps** its
  slot in `RESERVED` and its skip in the hard block
  ([retiring-a-reserved-artifact.md](../architecture/retiring-a-reserved-artifact.md)) — because
  silently unreserving turns every surviving file into a malformed one. A bundle standard has no
  consumers that need disarming; it simply stops existing.
- **It is not rewriting history.** The retired doc is still in git; what the repo gains is a reader
  who no longer pays for the text. Rewriting the past (amend, force-push) is forbidden for
  independent reasons — the removal is an ordinary commit like any other.
