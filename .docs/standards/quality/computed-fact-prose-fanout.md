---
type: standard
title: A computed fact's prose fan-out
description: Any fact a tool computes and prose restates — a schema's fields, a surface's command count — fans out the moment it changes, and no checker sees it: why the validators are blind by construction, the two independent measurements this rule was set from, the grep on the fact's spelled-out form that finds the sites while the change is still cheap, and why it belongs to the task that makes the change rather than to a later sweep
resource: plugins/quenching/assets/specs/schema.json, plugins/quenching/assets/bin/specs.py, plugins/quenching/commands/**
tags: [quality, schema, records, documentation, sweeps]
timestamp: 2026-08-03
audience: both
authority: current
source: rework-specs-isolate-flow plan (2026-08-03), from two independent measurements on one branch — `merge:` gained one field, `pr`, and four prose sites still spelled the record as `{strategy, subject}` in four homes; the same branch retired one command, and ten sites across four files still counted twenty-six. Every checker green in both cases
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
| `specs.py validate` | records **as written** in a document | prose that *describes* the record is not a record |
| `okf-validate.py` | a doc's shape — frontmatter, links, index membership | the sentence is well-formed and links fine; it is merely wrong |
| `okf-validate.py` `stale-doc` | a doc whose `timestamp` predates a commit under its `resource` | fires only where the doc's `resource` happens to name the schema file — the README and the glossary do not |

So the gate is green in every dimension the repo measures, and the product ships documentation that
teaches a record shape that no longer exists.

**The count is the point.** Measured on the change this standard came from: **one** field added to
`merge:` left **four** prose sites stale, in four different homes — a `standards/` doc, the operator
manual `specs.py` embeds in every adopting repo (plus its generated copy), the product README, and
the glossary. Three of the four were never named by the spec's `## Impact`; one was named there and
written only halfway, because the field arrived in a later section than the task that owned the
file.

**A second, independent measurement on the same branch, from a different trigger.** The same change
**retired a command**, and the count of commands is the same kind of fact as the shape of a record —
written once in code, described many times in prose. Ten sites still said *twenty-six commands* and
*nine `/specs:*` commands*, across four files, while `skills.py doctor` reported the true figure of
25 with no findings and every grep the spec's own gate ran came back empty. The trigger differs; the
failure and the mitigation do not.

Generalise it that way: **any fact a tool computes and prose restates** — a schema's fields, a
surface's count, an enum's members — fans out the moment it changes, and the checker that owns the
fact is precisely the one that cannot see the restatements.

## Grep the fact's literal form, in the task that changes it

The mitigation is cheap and has to happen while the change is still open:

```bash
grep -rn "merge: {strategy" --include='*.md' /.docs/ plugins/ README.md
```

Search for the **spelled-out form** — the brace list, the field names in sequence — not for the
record's name. `merge` alone matches every sentence about merging; `merge: {strategy` matches
exactly the sites that enumerate the fields, which is exactly the set that just went stale.

**It belongs to the task that makes the change**, not to a sweep afterwards, for the same reason
`base` is captured at isolation rather than at conclude: the person adding the field is the only one
who knows what the field means, and the set of sites is smallest and cheapest to fix before the rest
of the branch is written on top of it.

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
