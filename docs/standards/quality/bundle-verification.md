---
type: standard
title: Bundle verification
description: What the docs/ front machine-checks versus what it leaves to a skill's prose self-check, when an invariant is owed a deterministic check, where an accepted gap is recorded, and the resource glob-set format
resource: plugins/quenching/assets/hooks/okf-validate.py, plugins/quenching/assets/references/docs-align/conformance.md, plugins/quenching/commands/docs/status.md
tags: [quality, verification, okf, validator, conformance]
timestamp: 2026-07-30
audience: both
authority: current
source: docs-verification-layer plan (sections 2-4)
maintainer: quenching
---

# Bundle verification

What the `docs/` front proves mechanically, what it leaves to a skill reading its own work, and
how to tell which a given invariant deserves. `assets/hooks/okf-validate.py` is the
implementation; `quenching-docs-align/references/conformance.md` is the code-by-code contract.
This standard is the rule *behind* both.

## An invariant restated in more than two skills is owed a deterministic check

The rule this front learned the hard way. The glossary tail step — "after a capture, check whether
the new concept introduced a term that belongs in `knowledge/glossary.md`" — is specified in **six**
places: `homes.md` §Enriching the glossary, `quenching-docs-add`, `quenching-docs-learn`,
`quenching-docs-import-memory`, `quenching-docs-define`, and `quenching-specs-archive`'s
`distill.md`. Across two real distillation runs it produced **zero** entries.

An invariant written six times and executed zero times is not under-specified. It is evidence that
prose restatement does not enforce, and the seventh restatement would not have either. Past two
skills, the honest options are a **deterministic check** or an accepted gap recorded as one — never
a third paragraph.

The same held for `resource:`: four skills forbade inventing one, and nothing checked that it
pointed at anything. The repo's own shipped seed carried a self-pointing `resource: docs/**`, in
violation of the rule it was meant to demonstrate, for as long as only prose guarded it.

**Corollary.** When a check lands, the prose it replaces gets *cut*, not kept as belt-and-braces.
Two enforcers for one invariant is how they drift.

## Accepted gaps, recorded as such

The other honest option above, and the one that needs a home — an accepted gap that is merely
*believed* is indistinguishable from an oversight. An invariant belongs here when it is real, when
no deterministic check can reach it, and when the reason is **structural rather than unfinished
work**.

**Import provenance is an identity, not a derivation anything here can verify.** `/docs:import`
stamps `source_uri:` — the exact URI of the source unit — on every doc it creates, and that key is
what a later run greps to find the doc it already minted for that unit. Nothing checks it, and
nothing in this front can:

- **Whether the value is truthful** is decidable only against the source, at the instant it was
  read. This validator never fetches anything: its hook paths spawn no subprocess, and its CLI mode
  shells out only to `git`, read-only. A stamped URI is therefore trusted the way a `source:` line
  is trusted — by the run that wrote it.
- **Whether the source has since changed** is not merely unchecked, it is uncheckable *here*.
  "Unchanged versus changed" requires fetching the source and comparing; a checker that never
  fetches can only compare a doc against itself. Drift detection, if it is ever built, belongs to
  the run that already holds the unit in context — the import itself — and not to the validator.
  This is the general rule: **a check may only be asked for what its own inputs can decide.**
- **An absent or malformed `source_uri:` is deliberately not a finding.** Born at ERROR it is
  forbidden outright above; born at WARN it would fire on every authored doc that legitimately has
  no external origin — permanent noise, which is the same criterion that keeps
  `TYPES_WITHOUT_RESOURCE` exempt.
- **A unit collapsed from several seeds carries only one origin.** `sources.md` §Dedup item 1
  merges two source sections describing the same concept into a single unit, but `source_uri:` is
  single-valued by contract — one value on one line is what makes the exact lookup an equality
  test rather than a parse. The surviving unit is stamped with one seed's URI, so on a later
  import the *other* seed misses that lookup and falls through to resemblance, which is the
  judgement the key exists to avoid. Measured 2026-07-30: a unit collapsed out of two overlapping
  local seeds matched by concept, not by URI, on the second run. Accepted rather than closed — a
  list-valued key would buy that one seed its exactness at the cost of the property every lookup
  depends on.

What was done instead is the cut the corollary demands. The rule that an imported doc records where
it came from used to be written in **four** places — `sources.md`, `/docs:import` twice over, and
the operator manual. It now has one owner, `sources.md` §Attribution, and the other three cite it.
Removing three restatements is worth more than a fifth would have been, and this entry is what
makes the remaining hole *known* rather than merely unfilled.

## What is machine-checked, and at which severity

| Class | Codes | Severity | Blocking? |
| --- | --- | --- | --- |
| Structure | `no-frontmatter`, `broken-frontmatter`, `missing-type`, `index-has-type`, `index-has-frontmatter`, `log-has-type` | ERROR | fails conformance |
| Recommended fields | `missing-title` / `-description` / `-resource` / `-timestamp` | WARN | no |
| Structural integrity | `dir-no-index`, `index-broken-link`, `index-orphan`, `glossary-broken-link` | WARN | **yes**, in the skills' verify gate |
| Resource integrity | `resource-unresolved`, `resource-self` | WARN | **yes**, in the skills' verify gate |
| Staleness | `stale-doc` | WARN | **no** — advisory |

**Why so much is WARN-but-blocking.** OKF says a consumer MUST tolerate a broken link and MAY
synthesize a missing index, so escalating these to ERROR would break the exit-code contract for
every repo that was conformant when written. The plugin is stricter than OKF *for the bundles it
aligns*, and expresses that in the skills' verify gate rather than in the exit code — a distinction
worth keeping, because the two audiences differ.

**No new check is introduced at ERROR.** A check born at ERROR makes previously passing target
repos start failing on upgrade, for docs nobody touched. Convergence over accommodation governs
what a **sweep fixes**, not what a **validator escalates**.

**Advisory is a real category, and must stay small.** `stale-doc` reports a doc that *may* still be
correct — code moves under a rule that did not change. Folding it into the must-fix set would make
that set unusable, because every mature bundle carries one. A check that cannot distinguish "wrong"
from "worth a look" belongs here or nowhere.

## What stays a skill's prose self-check

Machine checks answer *shape*. They cannot answer:

- whether a doc is filed in the **right home**, or whether its `type` is the honest one;
- whether prose is accurate, or whether two standards **contradict** each other (a semantic pass,
  not a deterministic one);
- whether a term is genuinely **repo-specific** rather than dictionary vocabulary;
- whether an installed-but-empty home *should* hold something — which depends on what the repo
  actually does.

These stay with the skills, and the front reports them as **figures rather than findings** where it
can: bundle density (concept docs per home, glossary size, empty homes) appears in `/docs:status`
as a table with **no finding code**. Coding it would make permanent noise of a repo that
legitimately has no `mlops/`; omitting it would hide a bundle that passes every check while knowing
nothing. A figure informs without accumulating as a defect to chase.

## The `resource` glob-set format

`resource:` is a **comma-separated list** of repo-root-relative paths and globs — a plugin
convention, not an OKF rule, and undocumented until this standard. Three of the five values in this
repo's own bundle are lists.

- Wildcards are **`*` and `**` only**. `*` matches within one path segment; `**` matches any number
  of segments. Braces, character classes and `?` are **not** implemented: an entry carrying one is
  classified `unknown` and never reported as a violation, since flagging syntax nobody writes would
  make the must-fix set unusable.
- Matching is **segment-wise everywhere**, including the `:(glob)` pathspec passed to `git log`.
  Plain `fnmatch` and git's default wildmatch both let `*` cross a `/`, which would silently widen
  every shallow scope — so one glob means one thing across the whole checker.
- **A glob, not a `file:line` anchor.** Doctrine once instructed deriving `resource` from
  `file:line`; zero of five real values ever did. A line number says *where the rule is written* and
  rots on any insertion above it; a glob says *what the doc governs*, which is also exactly the
  input a staleness check needs.
- **A doc must not point at itself.** A self-scoped doc governs nothing and is eternally fresh,
  which silently disables `stale-doc` for it.
- **Except a bundle aggregate.** A scope containing the bundle *root* is legitimate:
  `knowledge/glossary.md` really does govern the whole bundle, so `resource: docs/**` is truthful
  and narrowing it to look tidier would be the fabrication. This is the `TYPES_WITHOUT_RESOURCE`
  exemption generalized — one mechanism, not two.

## Where verification runs

| Mode | Runs | Notes |
| --- | --- | --- |
| CLI | everything, including `stale-doc` | the on-demand sweep; `/docs:status` reads it |
| `PostToolUse` | one file's per-doc checks | never structural, never `stale-doc` |
| `Stop` | whole tree, dirty-gated | never `stale-doc` |
| `PreToolUse` | the two hard violations, opt-in | `hardBlock: true` only |

`stale-doc` shells out to `git log` once per doc — fine on demand, unacceptable under the `Stop`
deadline — so it is **CLI-only by default-off**, not by an opt-out a future caller could forget. A
tree that is not a git checkout skips it **silently**: a check that cannot be computed reports
nothing rather than a finding it cannot stand behind.
