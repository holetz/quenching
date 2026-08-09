---
type: standard
title: A withdrawn contract's prose residue
description: When a change removes a contract rather than changing a computed value, its prose residue has no canonical spelling to grep for — the sites assert it in their own words — so `## Impact` must name the CLASS of documents that assert it and derive the file list mechanically; the five misses measured on one branch, why naming the file is not enough either, and why the reviewer's question is "what did this make false?" rather than "which files changed?"
resource: plugins/quenching/commands/**, plugins/quenching/assets/**
tags: [quality, sweeps, documentation, specs, impact]
timestamp: 2026-08-03
audience: both
authority: current
source: enxugar-create-e-eliminar-o-rung-hooks plan (2026-08-03) — five misses on one branch withdrawing the installed-tool contract: three caught during execution and recorded as `## Discoveries`, two more only at the branch review, one of them in a file `## Impact` had named and half-covered
maintainer: quenching
---

# A withdrawn contract's prose residue

The sibling case to [computed-fact-prose-fanout.md](computed-fact-prose-fanout.md), and the harder
one. There, a tool computes a fact and prose restates it, so the fact has a **canonical spelling**
— `merge: {strategy`, *twenty-six commands* — and one grep finds every site that just went stale.

A **withdrawn contract** has no such spelling. When a change removes a rule rather than changing a
value, the documents asserting it wrote it in their own words, in whatever register their reader
needed. Nothing computes it, so nothing can be greped for.

## The measurement

One branch withdrew a single contract — *the aligns install this plugin's three tools into a
target's `.claude/hooks/`* — and replaced it with plugin-first resolution. Five sites still asserted
the withdrawn contract, in five different wordings:

| # | Site | How it said it | Caught by |
| --- | --- | --- | --- |
| 1 | `commands/specs/isolate.md` | a citation to the section that carried the fallback | execution |
| 2 | `commands/align.md` | named findings the change deleted, and told the human an INSTALL offer belonged in the plan | execution |
| 3 | embedded manuals | `${CLAUDE_PLUGIN_ROOT}` line citations | execution |
| 4 | `assets/README.md` | "Installed into a target? **yes, by `/docs:align`**", plus four more rows | branch review |
| 5 | `/.docs/standards/architecture/plugin-layout.md` | a placement justified by an adjacency the same branch removed | branch review |

None of the five shared a substring with any other. A grep for the class would have had to guess
"install", "installed", "copies", "merges", "offers the overwrite", "beside the config it loads" —
which is not a grep, it is the reading the reviewer ends up doing anyway.

**Measured a second time, on a different branch (2026-08-08).** A removal of a whole capability ran
a literal grep for the artefact's own name, `QUENCHING.md`, and came back empty — while four sites
still cited it as *"the operator manual"*, a phrase the artefact's name does not contain. Three of
the four were live instructions pointing at a file that would no longer exist; the fourth was a
historical mention, correct as written. The grep found the uses that spelled the name and none of
the ones that described the thing, which is this standard's claim restated in the one register it
had not yet been measured in: **a name is not a spelling of the class either.** The four sites were
recorded as `## Discoveries` during execution and closed before the review.

## `## Impact` must name the class, not its instances

Every one of the first three misses has the same shape: `## Impact` enumerated **instances of a
class** and the class had one more member than the author counted.

- It named four command bodies citing a section. There were five — `isolate.md` was the fifth.
- It named "the three front aligns". There were four things restating the contract; the repo-wide
  conductor was the fourth.

So: **declare the membership rule, then derive the list from it in the task**, and let the
derivation be the thing the task runs.

```bash
grep -rln 'tool-resolution.md' --include='*.md' plugins/ /.docs/
```

A list written from memory is a claim about a set nobody enumerated. A list derived from a rule is
reproducible by the next reader, and it re-derives correctly when a member is added later — which
is the property the enumeration never had.

## Naming the file is not enough

Miss #5 is the one that bounds the rule. `plugin-layout.md` **was** named in `## Impact`, and the
task did edit it — the paragraph the author was thinking of. Three other paragraphs in the same
file rested on the same withdrawn contract and survived, including the justification for a file's
location that the very same branch had invalidated.

A withdrawn contract's residue is not distributed one-per-file. Once a document is in scope, the
unit of work is **every assertion it makes about the withdrawn thing**, not the passage that
prompted the file's inclusion.

## The reviewer's question

This is why the branch review reads for coherence rather than diffing a checklist, and the question
that finds this class is not *which files changed?* but:

> **What did this branch make false?**

The two answers differ exactly on the files the branch never opened — which is where misses #4 and
#5 lived, and which no per-task self-review can reach by construction, since a task only ever sees
its own diff.

**No checker can close this.** Every verifier stayed green through all five: the tools' selftests
pass, `okf-validate.py` reads a well-formed sentence that is merely wrong, and `stale-doc` fires
only where a doc's `resource:` happens to name a changed path — `assets/README.md` carries no
frontmatter at all. Same structural blindness the sibling standard tabulates, same conclusion: the
mitigation is authored discipline at the moment of the change, not a gate afterwards.
