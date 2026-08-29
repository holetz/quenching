---
type: standard
title: A computed fact's prose fan-out
description: Any fact a tool computes and prose restates — a schema's fields, a surface's command count — fans out the moment it changes, and no checker sees it: why the validators are blind by construction, the two independent measurements this rule was set from, the grep on the fact's spelled-out form that finds the sites while the change is still cheap, a doc's own `description` as the nearest instance with its two listing consumers (one hand-maintained, one a GENERATED zone that is stale between sweeps by design), and why it belongs to the task that makes the change rather than to a later sweep
resource: plugins/quenching/assets/specs/schema.json, plugins/quenching/assets/bin/quenching/specs/**, plugins/quenching/commands/**, plugins/quenching/assets/checks/citation-check.sh
tags: [quality, schema, records, documentation, sweeps]
timestamp: 2026-08-27
audience: both
authority: current
source: rework-specs-isolate-flow plan (2026-08-03), from two independent measurements on one branch — `merge:` gained one field, `pr`, and four prose sites still spelled the record as `{strategy, subject}` in four homes; the same branch retired one command, and ten sites across four files still counted twenty-six. Every checker green in both cases; the `description` instance and its two listing consumers added by revisar-fluxo-do-develop-custo-e-gates at its branch review (2026-08-16), measured on that spec's own task 1.1 — `automation/context-discipline.md` went from two ways to three and both copies still read two; narrowed for the retired-command case by the descontinuar-comando-specs-continue spec (2026-08-16), where `citation-check.sh` half 2 went green→red across three files the branch never opened and the declared gate saw nothing
maintainer: quenching
---

# A computed fact's prose fan-out

A machine-read schema is written once and **described many times**. Adding a key to it is a small,
well-tested edit; the descriptions it invalidates are scattered, untested, and invisible to every
check the repo runs.

## The blindness is structural, not an oversight

Each verifier is doing its job correctly, and none of them can see this:

| Checker | What it validates | Why it is silent here |
| --- | --- | --- |
| the schema's own selftest | that the new key behaves — accepted, refused, defaulted | the key works; that was never in doubt |
| `cq specs validate` | records **as written** in a document | prose that *describes* the record is not a record |
| `cq knowledge` | a doc's shape — frontmatter, links, index membership | the sentence is well-formed and links fine; it is merely wrong |
| `cq knowledge --activity` | a doc whose `timestamp` predates a commit under its `resource` | a FIGURE, not a finding, since 2026-08-27 — and it speaks only where the doc's `resource` happens to name the schema file, so the README and the glossary raise nothing either way |

So the gate is green in every dimension the repo measures, and the product ships documentation that
teaches a record shape that no longer exists.

**The count is the point.** Measured on the change this standard came from: **one** field added to
`merge:` left **four** prose sites stale, in four different homes — a `standards/` doc, the operator
manual `cq specs` embeds in every adopting repo (plus its generated copy), the product README, and
the glossary. Three of the four were never named by the spec's `## Impact`; one was named there and
written only halfway, because the field arrived in a later section than the task that owned the
file.

**A second, independent measurement on the same branch, from a different trigger.** The same change
**retired a command**, and the count of commands is the same kind of fact as the shape of a record —
written once in code, described many times in prose. Ten sites still said *twenty-six commands* and
*nine `/quenching:specs:*` commands*, across four files, while `cq components doctor` reported the true figure of
25 with no findings and every grep the spec's own gate ran came back empty. The trigger differs; the
failure and the mitigation do not.

Generalise it that way: **any fact a tool computes and prose restates** — a schema's fields, a
surface's count, an enum's members — fans out the moment it changes, and the checker that owns the
fact is precisely the one that cannot see the restatements.

## Grep the fact's literal form, in the task that changes it

The mitigation is cheap and has to happen while the change is still open:

```bash
grep -rn "merge: {strategy" --include='*.md' /docs/ plugins/ README.md
```

Search for the **spelled-out form** — the brace list, the field names in sequence — not for the
record's name. `merge` alone matches every sentence about merging; `merge: {strategy` matches
exactly the sites that enumerate the fields, which is exactly the set that just went stale.

**It belongs to the task that makes the change**, not to a sweep afterwards, for the same reason
`base` is captured at isolation rather than at conclude: the person adding the field is the only one
who knows what the field means, and the set of sites is smallest and cheapest to fix before the rest
of the branch is written on top of it.

## A doc's own `description` is a fan-out site, with two known consumers

The rule above reads as though the fact always lives in code. The cheapest instance is closer than
that: **a standard's own `description` is copied into two listings the moment it is written**, and
editing the doc updates neither.

| Consumer | How it is maintained | What a stale copy looks like |
| --- | --- | --- |
| the home's `index.md` (e.g. `standards/automation/index.md`) | by hand, usually a shortened form | a row that summarises a rule the doc no longer states |
| the GENERATED zone of `standards/index.md` | verbatim, rebuilt only by `/quenching:knowledge:align` | the previous `description`, word for word, until a sweep runs |

Neither is caught by `cq knowledge validate` — an out-of-date listing is a well-formed listing.
Measured on `revisar-fluxo-do-develop-custo-e-gates` (2026-08-16), whose task 1.1 rewrote
`automation/context-discipline.md`'s description from *"the only two ways to cut it"* to *"the three
ways"*: both copies still read "two" when the branch reached its review, and the doc's own title had
changed as well.

The second row is the one that surprises: a zone marked GENERATED reads like something a tool keeps
current, and it is — but only when the tool is invoked, which is not part of writing a doc. **A
derived zone is stale between sweeps by design**, so the task that changes the fact still owns the
copy, exactly as the hand-maintained row above it.

## Historical mentions stay, and are the reason a checker cannot be written

Not every hit is a defect. A changelog entry, a `source:` line, or a paragraph narrating what a past
release did is **true about the past** and correct as written — the README's own changelog spells
out `merge: {strategy, subject}` and should keep doing so, because that is what that release
shipped.

That is what keeps this from becoming a validator. Distinguishing "describes the current contract"
from "narrates a past one" is the mention/use judgment
[prose-sweeps.md](prose-sweeps.md) already establishes is invisible to a regex — so a check here
would either flag the history or miss the live sites, and a check that cannot tell wrong from
worth-a-look belongs nowhere
([bundle-verification.md](bundle-verification.md) §Advisory is a real category).

This standard is the sibling of that one, and the failures are opposite: `prose-sweeps.md` is the
sweep you **ran**, corrupting the sentences that talk *about* the form. This is the sweep you
**never ran** over the sentences that talk about the shape.

## Retiring a named thing narrows the rule: change the FORM, keep the FACT

<!-- rules -->

The section above says historical mentions stay, and it is right about the **fact**. It is not a
licence to keep the **spelling**. When the thing that went stale is not a field name but a
*retired command*, a second instrument enters: `assets/checks/citation-check.sh` half 2 asserts
that every cited `/quenching:<ns>:<cmd>` resolves to a body under `commands/**`. That assertion
and "historical mentions stay, verbatim" cannot both hold — a retired command leaves its name in
changelogs and in the rationale of standards, and every one of those reads to the check as a
citation with no body.

So the rule for a retirement is narrower than the rule for a renamed field:

- **The fact is preserved, always.** What a past release shipped, and what a past measurement
  observed, is true and is not deleted or softened.
- **The spelling stops being a live citation.** Name the retired thing as retired — the house
  idiom is already in the plugin's own changelog: *"A **25th command** (an isolation command,
  since retired)"*. `the front router (since retired)` carries the same fact as its old slash-path
  did, and cites nothing. **This section obeys its own rule**, which is why it never spells that
  path out: a standard that quoted the dead name as an example would fail the very check it
  documents.
- **Tense follows.** A sentence about a command that no longer exists is past tense.

**Derive the sites with TWO greps, never one.** The command's own path spelling misses every
sentence that names it in prose or inside an enumeration — measured on the retirement below, one
grep found 18 files and missed four more: both plugin manifests (which wrote
`with continue routing between them`), a shell check whose regex listed the bare name inside an
alternation, and a standard that enumerated it among `` `align`, `conclude`, `continue` ``.

<!-- rationale -->

MEASURED on the `descontinuar-comando-specs-continue` spec (2026-08-16). `citation-check.sh` half
2 read `cited commands: 986 checked, all resolve` on the integration branch and
`1 distinct FAIL` on the work branch — the branch turned a green assertion red, and it did so
through three files it never opened, each holding a legitimately historical sentence. The declared
gate (`components doctor`/`lint`, the unit suite, `knowledge validate`) stayed green throughout;
only this check saw it.

The same run also shows why the two-grep rule is not belt-and-braces: the spec's own `## Impact`
declared the class *and* the derivation, exactly as
[withdrawn-contract-residue.md](withdrawn-contract-residue.md) §`## Impact` must name the class
requires — and the class still had four members past what the first grep enumerated. A derivation
is only as wide as its widest spelling.
