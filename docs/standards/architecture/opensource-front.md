---
type: standard
title: Opensource front
description: The target repository's license, community and governance artifacts, written only from pinned templates through cq opensource apply, and the read-only aggregate of every owner's open source catalog answers into a conservative baseline level with stable os-* findings
resource: plugins/quenching/commands/opensource/**, plugins/quenching/assets/bin/quenching/opensource/**, plugins/quenching/assets/opensource/templates/**, plugins/quenching/assets/references/opensource-align/**, plugins/claude/quenching-opensource/**
tags: [architecture, opensource, governance, community, license]
timestamp: 2026-10-17
audience: both
authority: current
source: spec 1637 (epic 1627) — route, aggregate, level, apply and template sha256 proved by test_opensource_front.py; module resolution measured with the nine principal modules on PATH
maintainer: quenching
---

# Opensource front

The opensource front is the repository surface that carries a project's license, contribution
process, code of conduct, support and governance text, code owners, issue and pull request
templates, citation and funding files. It is the eighth local front: it converges a tree of
artifacts it owns, and it reports — never re-measures — the open source catalog controls the other
fronts own.

<!-- rules -->

## Mold adoption and name

The front adopts the common minimum from [`front-mold.md`](front-mold.md): a stable `doctor` and
`status`, typed exits (0 clean, 1 findings, 2 refusal) and one disposition band per code, mapped in
`plugins/quenching/assets/references/opensource-align/bands.md`. Its name is `opensource` and its
finding prefix `os-` is reserved to it. New open source questions land in this front; the
`security`, `delivery`, `toolchain` and `proof` fronts keep only the catalog answers they already
own.

## The route

`cq opensource` has three verbs:

| Verb | Writes | Answers |
| --- | --- | --- |
| `status` | nothing | every owner's catalog block, the baseline level, the artifact rows, findings and advisories |
| `doctor` | nothing | `status` plus applicability and template integrity |
| `apply --artifact <name> [--var k=v]... [--dry-run]` | one artifact | the written target, its source template and the placeholders substituted |

## The aggregate never measures

`status` calls `owner_controls(owner, root)` for every owner `controls.json` declares — the same
function each owning front already embeds — and only assembles the result. It never calls another
front's CLI, so a disabled module cannot take the aggregate down, and it never adds a probe for a
control another owner holds. A requirement of another owner appears in that owner's block with the
command that closes it, never as an `os-*` finding. `present` is candidate evidence, never
conformance.

## The baseline level is conservative

For each level N, the active, non-optional requirements whose `levels` carry N decide its state:
all `present` → `met`; any `missing` → `unmet`; no `missing` but any `not-measured` or `refused` →
`unknown`. The attained level is the largest N such that levels 1..N are all `met`, else 0, and
each level lists its `blocking` requirement ids. A requirement only a provider answers stays
`not-measured`, so the level is `unknown` rather than rounded up until a provider probe exists.

## Findings and applicability

Exit 1 only when a non-optional control the catalog gives to `opensource` has a `missing`
requirement. An optional control and an artifact no control names produce an `info` advisory that
never changes the exit code. `doctor` reports `applicable` when the root carries a `LICENSE*` or
`COPYING*` file or `shared.profiles.installed` names `opensource`, and `not-applicable` otherwise;
the root conductor reports and skips a `not-applicable` front, while
`/quenching-opensource:opensource:align` invoked directly runs anyway. No configuration namespace
exists: the owner's answers live in the align plan and in the written artifacts.

## Writing through the route, from pinned templates

Every artifact is written by `cq opensource apply`, never by the model. It copies the template
byte for byte, substitutes only the placeholders `sources.json` declares for it, and refuses with
exit 2 when the target exists (`os-target-exists`), a declared placeholder has no value
(`os-var-missing`), a value names no placeholder (`os-var-unknown`), the artifact is unknown
(`os-artifact-unknown`) or the license has no vendored text (`os-license-unvendored`). It never
overwrites.

Upstream templates — Contributor Covenant 2.1, DCO 1.1 and the SPDX texts of `MIT` and
`Apache-2.0` — are pinned by URL, license and sha256 in `sources.json`; a template whose bytes no
longer hash to its pin is `os-template-drift`: `doctor` reports it as an error finding and
`apply` refuses that template. Upstream text is never adapted beyond the placeholders upstream itself declares. The authored
templates (contributing with the DCO sign-off, support, governance, code owners, issue and pull
request templates, citation, funding) are short and carry no pin.

## The owner's choices stay the owner's

The license, the maintainers, the code owners, the conduct contact, the citation authors and the
funding account are the target owner's answers. The align asks for them in its one plan and writes
them as declared; it never proposes a default, and a batch authorization never covers them.

## The module

The front ships as the published module `quenching-opensource`, generated from `plugins/quenching`.
It owns the `opensource` commands and the `opensource` package, ships the `common` and `controls`
packages and the `opensource-controls` and `opensource-align` references as generated support, and
is not the owner of the `cq` on `PATH`: with the module disabled, `cq opensource` exits 2 naming the
module to enable.

<!-- rationale -->

Aggregating instead of measuring keeps one answer per control: the catalog gives every control
exactly one owner, and a second probe here would let two fronts disagree about the same evidence.
Writing through the route keeps upstream texts byte-identical, which a model-produced copy cannot
promise, and the sha256 pin turns an accidental edit of a vendored text into a finding rather than
a silent divergence.
