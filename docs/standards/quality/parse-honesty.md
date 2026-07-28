---
type: standard
title: Parse honesty
description: A verifier names its own parse failure instead of reporting it as a content gap — the sidecar shape that adds the signal without changing a return type, why the finding is a warn rather than an error, and the rule that a checker never gains a lossy transform without the diagnostic that reports it
resource: plugins/quenching/assets/bin/skills.py, plugins/quenching/assets/bin/specs.py, plugins/quenching/assets/hooks/okf-validate.py
tags: [quality, verification, parsing, findings, severity]
timestamp: 2026-07-28
audience: both
authority: current
source: fix-skills-py-description-truncation spec (task 3.1) — proved by the three tools' selftests in tasks 2.1-2.3
maintainer: quenching
---

# Parse honesty

**A verifier that misreports its own parse failure is worse than one that refuses.** When a tool
cannot faithfully read its input, the finding it emits must name the *misread*, not the
*consequence* — because the consequence looks exactly like an ordinary content defect, and the
person acting on it will fix the wrong thing.

The sibling [../code/frontmatter-parsing.md](../code/frontmatter-parsing.md) owns the mechanics —
which YAML subset the three shipped tools read, the comment rule, the canonical case list. This
standard owns the obligation those mechanics exist to satisfy.

## The failure this exists to prevent

`skills.py` truncated every frontmatter value at its first `#`. A command whose `description`
mentioned a heading lost everything after it — including the trigger phrases and the `Not for:`
boundary that live in the tail.

What `lint` then reported was `sk-no-description`, or a description "under" the character cap, or a
missing boundary. Every one of those is **true of the string the tool held** and **false of the file
on disk**. The author reads "no description", opens a file that visibly has one, and either distrusts
the checker or edits prose that was never wrong. The defect was invisible precisely because the tool
had a confident, plausible thing to say instead.

Generalised: **a lossy read followed by a content check turns a parser bug into a content finding.**
The content check is not at fault and cannot detect this — by the time it runs, the evidence is gone.

## The rule

> A tool that transforms its input before checking it MUST be able to report what the transform
> removed or could not represent, as a finding of its own, at the point where findings are read.

Three consequences, in the order they bind:

1. **The diagnostic ships with the transform, never after it.** `okf-validate.py` stripped no
   comments at all, which made it the one tool that could not truncate. It was given the comment
   rule and `okf-frontmatter-unparsed` in the same change — adding a prose-loss path to a hook that
   fires on every `docs/**` write in every target repo, without the means to say when it fired,
   would have been strictly worse than leaving it alone.
2. **The diagnostic runs before the content checks it would otherwise be mistaken for.** In all
   three tools the anomaly finding is emitted ahead of the required-field checks, so a reader sees
   the cause above the symptom rather than below it.
3. **A tool with no way to prove it implements the rule does not get the rule.** `okf-validate.py`
   had no `selftest`; it gained one in the same change.

## The shape: a sidecar, not a changed return type

Add a **second function** returning the diagnostics, and leave the parser's signature alone:

```python
parse_frontmatter(text)      -> dict          # unchanged; every existing caller still works
frontmatter_anomalies(text)  -> list[dict]    # what the parse could not represent
```

The alternative — returning `(value, understood)` from the parser — was rejected across nine call
sites. It is not merely churn: it forces **every** caller to decide what an un-understood input
means, including callers in the middle of a cycle (`specs.py status`, `next`, `triage`) that today
refuse nothing and must not start. The signal is only *read* in two places, so it should only be
*asked for* in two places.

The sidecar also keeps the honest property that the parser is still allowed to guess. It does guess —
it strips the comment — and the sidecar is what makes the guess visible.

## Severity: warn, and why not error

**These findings are warnings.** The tool is reporting a suspicion it cannot resolve, not a
violation it has proved:

- a deliberate trailing comment and accidentally lost prose are **byte-identical**;
- a duplicate key resolves *somehow* — this parser takes the last, and nothing guarantees Claude
  Code's loader agrees, which is exactly why it is worth saying and exactly why it cannot be called
  an error.

Erroring would fail conformant repositories over a legitimate comment. Staying silent is what
produced the original defect. Warn is the only severity that fits a statement of the form *"I read
this, and I might have read it wrong."*

This matches the fail-open contract `skills.py parse_frontmatter_hooks` already stated for the
`hooks:` block: a parser that silently misreads is worse than one that admits it cannot read.

## Naming the limit is not the same as removing it

A diagnostic that says *"this parser does not read block records"* discharges the obligation. Teaching
the parser to read them is a **separate** decision with its own cost, and one that
[../code/frontmatter-parsing.md](../code/frontmatter-parsing.md) rules out for these tools.

So the anomaly set is a floor: each tool exempts the forms it genuinely reads and reports the rest.
`okf-validate.py` reads top-level scalars only, so a block list is as unreadable to it as prose and
it says so; `specs.py` reads block records and stays quiet about them. Both are honest, and they
disagree about nothing in the canonical list.

## Where this applies

Any checker in this repository that reads a file into a narrower model than the file can express:
the three frontmatter parsers today, and the description/body extraction any future one adds. It is
the parsing-side counterpart of the two verification standards —
[surface-verification.md](surface-verification.md) is about a check that cannot observe its subject
at all, [bundle-verification.md](bundle-verification.md) about which invariants are owed a
deterministic check. This one is about a check that *can* observe its subject, and must not
misdescribe what it saw.

**It does not apply to a tool reading less on purpose and checking nothing about it.** `skills.py`
never inspects `argument-hint`; not modelling it is a scope decision, not a misread. The obligation
attaches the moment a value is *used* in a finding.
