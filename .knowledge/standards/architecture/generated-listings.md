---
type: standard
title: Generated listings — a derived listing only pays for itself when a program can prove it is fresh
description: A listing regenerated from disk is a second source of a fact something else already derives, so it earns its keep only where nothing else derives that fact and a checker can decide freshness; the decision criterion is whether a command already answers the same question on demand, the /.knowledge/ bundle index.md files are the counterexample that bounds the rule, and a convergence condition may name only what a checker decides
resource: plugins/quenching/assets/knowledge/**/index.md, plugins/quenching/assets/bin/quenching/components/**, plugins/quenching/assets/bin/quenching/specs/**, plugins/quenching/assets/references/specs-align/conformance.md, plugins/quenching/assets/references/align/convergence.md
tags: [architecture, listings, derived-state, verification, convergence]
timestamp: 2026-08-10
audience: both
authority: current
source: decide-plans-index-need spec (task 6.1) — the retirement of /.specs/plans/index.md is the case that proved it
maintainer: quenching
---

# Generated listings — a derived listing only pays for itself when a program can prove it is fresh

A **generated listing** is a file, or a marked zone inside one, that some command rebuilds from
what a directory holds. It is convenient, and it is always a **second source** of a fact the disk
already carries. That is not automatically wrong — but it has to be paid for, and this is the price.

## The rule

**A generated listing earns its keep only when a program can prove it is fresh.**

Freshness is the whole question because staleness is a generated listing's only failure mode, and
it is silent. The file stays well-formed, its links keep resolving, every validator keeps passing —
it just stops being true. A reader trusts it precisely because it looks maintained.

## The decision criterion, applied before writing any code

Ask one question:

> **Is there already a command that derives this same fact from disk, on demand?**

- **Yes → the listing is duplication, and its checker is pure cost.** Do not write the listing.
  Anything spent verifying it is spent guarding a copy that did not need to exist.
- **No → the listing IS the source, and a checker is mandatory.** It is not a nicety; without one
  the listing is an unverified claim, and the thing it lists is unreachable when it drifts.

The question is answerable before a line is written, which is what makes it a design rule rather
than a review comment.

## The counterexample that bounds the rule

The `/.knowledge/` bundle's `index.md` files are generated listings that **do** pay for themselves, and
the contrast is exact:

| | `/.knowledge/**/index.md` | the retired `/.specs/plans/index.md` |
| --- | --- | --- |
| Does a command derive the same fact on demand? | **No.** Nothing enumerates the bundle. | **Yes** — `cq specs list` and `cq specs status` read `plans/` directly. |
| What the listing is | the bundle's **only** navigation — a doc no index reaches is invisible | a table duplicating what the tool already returned |
| Checker | `index-orphan` / `dir-no-index` / `index-broken-link`, structural contract | four `sp-*` codes guarding a copy |
| Verdict | keeps its checker | artifact and checker both retired |

So the rule does not say *generated listings are bad*. It says the checker is justified by the
listing being the **source**, never by the listing merely existing.

## The corollary: a convergence condition may name only what a checker decides

A sweep's convergence condition is where this fails most expensively, because the failure reads as
rigour.

The `specs` front's condition once required that the generated zone "matches disk". **Nothing
computed that.** The specs pillar emitted no `changed` field for any command to read — while
the components pillar did emit one, which is why the identical clause was sound for the `.claude/` front and
hollow here. Two references and a command body instructed the reader to branch on a field the tool
had never produced.

The measured result, on this repository on 2026-07-30: a spec listed under the wrong stage, and the
entire verification stack reporting the front as conformant. The one clause that could actually rot
was the one clause left to a human's eye.

**A clause a program cannot evaluate is not a stricter standard — it is an unverified one**, and it
is worse than an absent clause, because it is read as coverage. State convergence in exit codes, or
do not state it.

## Where this sits

[bundle-verification.md](../quality/bundle-verification.md) decides which invariants are owed a
deterministic check at all; this standard asks the prior question of whether the artifact under
check should exist. When the answer is that it should not, the removal follows
[retiring-a-reserved-artifact.md](retiring-a-reserved-artifact.md) — drop the checker, keep the
reservation, and leave a surviving copy in a target repo exactly as found.

It shares its premise with [../quality/parse-honesty.md](../quality/parse-honesty.md): both refuse
to let a tool's silence read as a clean result. There, a parse failure is named rather than reported
as a content gap; here, a listing nothing can verify is retired rather than counted as verified.

`authority: current` because the retirement it governs was carried out under it: the artifact, its
four finding codes, the `--listing-root` mode that read them and the subcommand that wrote it were
all removed together, and the guard against their return is a mutation-checked assertion in each
tool's `selftest` rather than a paragraph.
