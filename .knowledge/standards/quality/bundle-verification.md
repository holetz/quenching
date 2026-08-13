---
type: standard
title: Bundle verification
description: What the knowledge front machine-checks versus what it leaves to a skill's prose self-check, when an invariant is owed a deterministic check, where an accepted gap is recorded, and the resource glob-set format
resource: plugins/quenching/assets/bin/quenching/knowledge/**, plugins/quenching/assets/references/knowledge-align/conformance.md, plugins/quenching/commands/knowledge/status.md
tags: [quality, verification, okf, validator, conformance]
timestamp: 2026-08-10
audience: both
authority: current
source: docs-verification-layer plan (sections 2-4); the grep-reach rule from collapse-remaining-language-clause-restatements (2026-07-31) — a census invariant that returned 14 against a real population of 19
maintainer: quenching
---

# Bundle verification

What the `knowledge` front proves mechanically, what it leaves to a skill reading its own work, and
how to tell which a given invariant deserves. `assets/bin/cq knowledge` is the
implementation; `quenching-knowledge-align/references/conformance.md` is the code-by-code contract.
This standard is the rule *behind* both.

## An invariant restated in more than two skills is owed a deterministic check

The rule this front learned the hard way. The glossary tail step — "after a capture, check whether
the new concept introduced a term that belongs in `glossary.md`" — is specified in **six**
places: `homes.md` §Enriching the glossary, `quenching-knowledge-add`, `quenching-knowledge-learn`,
`quenching-knowledge-import-memory`, `quenching-knowledge-define`, and `/quenching:specs:conclude`'s
`distill.md`. Across two real distillation runs it produced **zero** entries.

An invariant written six times and executed zero times is not under-specified. It is evidence that
prose restatement does not enforce, and the seventh restatement would not have either. Past two
skills, the honest options are a **deterministic check** or an accepted gap recorded as one — never
a third paragraph.

The same held for `resource:`: four skills forbade inventing one, and nothing checked that it
pointed at anything. The repo's own shipped seed carried a self-pointing `resource: /.knowledge/**`, in
violation of the rule it was meant to demonstrate, for as long as only prose guarded it.

**Corollary.** When a check lands, the prose it replaces gets *cut*, not kept as belt-and-braces.
Two enforcers for one invariant is how they drift.

## A grep invariant measures what the pattern reaches, not what the sentence claims

The section above decides *whether* an invariant is owed a check. This one is about the check once
written: a `grep` invariant states a population in prose and measures a different one, and nothing
reports the gap — the command exits 0 either way.

Measured 2026-07-31 on the language-clause census. The invariant read *"returns **exactly** the
fourteen places in the table"* and was implemented as
`grep -rn -A1 "repo.s language" --include='*.md' --include='*.py' plugins/ docs/`. It returned 14.
The real population was **19 hits across 17 files**. Three whole files were unreachable, for two
different mechanical reasons:

- **Line wrap.** One occurrence had `the repo's` and `language` on separate lines. A single-line
  pattern cannot match it, and `-A1` does not help: it extends a hit already found, so where there
  is no hit there is nothing to extend. The spec had written `-A1` believing it did.
- **Declared scope.** Two files sat outside `plugins/ docs/` — one of them the installed copy of a
  manual, the exact artifact class the sweep existed to keep in sync.

**The number agreed by arithmetic coincidence**, which is the part worth fearing. One file counted
two hits and two files counted zero, so 14 came out of a set that was not the table's. A verify
step passed, a human read "14", and the census was believed closed while two members had never
been looked at.

Three rules follow:

1. **Print the population, not the count.** A check that lists file-and-count per hit makes a wrong
   set visible; one that prints a total hides it behind a number that can be right for the wrong
   reasons.
2. **Match the parse, not a line.** Prose wraps. An invariant over prose is multiline
   (`re.S`, `grep -z`) or it silently under-counts, and under-counting reads as *clean*.
3. **State the scope as the set to be governed**, then check that the roots actually cover it. Here
   `specs/` was governed and unscanned — the omission is invisible from inside the command.

This is the mechanical sibling of the semantic failure in
[prose-sweeps.md](prose-sweeps.md) §*The check that guards the sweep cannot catch this*: there the
check reaches the site and reads it as clean, here it never reaches it at all. Both exit 0.

## Accepted gaps, recorded as such

The other honest option above, and the one that needs a home — an accepted gap that is merely
*believed* is indistinguishable from an oversight. An invariant belongs here when it is real, when
no deterministic check can reach it, and when the reason is **structural rather than unfinished
work**.

**Import provenance is an identity, not a derivation anything here can verify.** `/quenching:knowledge:import`
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
it came from used to be written in **four** places — `sources.md`, `/quenching:knowledge:import` twice over, and
an installed payload. It now has one owner, `sources.md` §Attribution, and the other three cite it.
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

**A rising advisory count is not evidence of anything.** `stale-doc` compares a doc's `timestamp`
against the last commit touching its `resource`, so any branch that edits a governed path *raises*
the count as it goes: the resource moved, the rule did not. This is structural, not a symptom —
a branch cannot touch code a standard governs without ageing that standard by this measure.
Measured 2026-07-30: a branch editing only `plugins/quenching/**` took this bundle from 12
`stale-doc` warnings to 14 without one doc becoming wrong. Read the gate as **zero errors**, never
as a warning total, and name the delta in a report rather than letting it read as a regression.

## What stays a skill's prose self-check

Machine checks answer *shape*. They cannot answer:

- whether a doc is filed in the **right home**, or whether its `type` is the honest one;
- whether prose is accurate, or whether two standards **contradict** each other (a semantic pass,
  not a deterministic one);
- whether a term is genuinely **repo-specific** rather than dictionary vocabulary;
- whether an installed-but-empty home *should* hold something — which depends on what the repo
  actually does.

These stay with the skills, and the front reports them as **figures rather than findings** where it
can: bundle density (concept docs per home, glossary size, empty homes) appears in `/quenching:knowledge:status`
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
  `glossary.md` really does govern the whole bundle, so `resource: /.knowledge/**` is truthful
  and narrowing it to look tidier would be the fabrication. This is the `TYPES_WITHOUT_RESOURCE`
  exemption generalized — one mechanism, not two.

## Where verification runs

| Mode | Runs | Notes |
| --- | --- | --- |
| CLI | everything, including `stale-doc` | the on-demand sweep; `/quenching:knowledge:status` reads it |
| `PostToolUse` | one file's per-doc checks | never structural, never `stale-doc` |
| `Stop` | whole tree, dirty-gated | never `stale-doc` |
| `PreToolUse` | the two hard violations, opt-in | `hardBlock: true` only |

`stale-doc` shells out to `git log` once per doc — fine on demand, unacceptable under the `Stop`
deadline — so it is **CLI-only by default-off**, not by an opt-out a future caller could forget. A
tree that is not a git checkout skips it **silently**: a check that cannot be computed reports
nothing rather than a finding it cannot stand behind.
