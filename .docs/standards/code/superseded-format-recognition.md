---
type: standard
title: Recognising a superseded format
description: How a recogniser is changed when the format it reads is superseded — the new pattern must be asserted against the OLD form, because a pattern that describes the new one correctly often matches the old one whole and yields a confident wrong answer with no finding; and a store's recogniser must separate "not mine" from "mine, but stale", because sending both to the same discard makes a half-migrated front vanish in silence
resource: plugins/quenching/assets/bin/quenching/specs/**, plugins/quenching/assets/specs/schema.json
tags: [code, parsing, migration, recognisers, findings, selftest]
timestamp: 2026-08-10
audience: both
authority: current
source: evaluate-spec-creation-flow spec — both halves measured against this repository's own 72 specs while the capture date was moved out of the basename, and both shipped with the assertions that now guard them (`SPEC_FILE_RE`'s lookahead, `LEGACY_DATED_FILE_RE` and `GitHubBackend.legacy_rows`)
maintainer: quenching
---

# Recognising a superseded format

**A format change is not finished when the new form is described. It is finished when the old form
is refused, out loud.** Both halves of that sentence were learned the same afternoon, from two
recognisers that were individually correct and jointly silent.

The sibling [../quality/parse-honesty.md](../quality/parse-honesty.md) owns the neighbouring
obligation — a verifier that misreads its input must name the *misread* rather than the
*consequence*. This standard owns the case that one cannot catch: the read here is **not lossy and
not wrong by its own pattern**. It succeeds, confidently, on input that was never meant for it.

## Half one — the new pattern must be asserted against the old form

A spec's basename went from `YYYY-MM-DD-<slug>.md` to `<slug>.md`, so the pattern became:

```python
SPEC_FILE_RE = re.compile(r"^([a-z0-9]+(?:-[a-z0-9]+)*)\.md$")
```

That describes the new form exactly. It also matches `2026-07-25-decide-agents-md-harness-default.md`
**whole**, because `[a-z0-9]` matches digits and `-` is the separator the pattern already allows. The
date is not rejected; it is absorbed into capture group 1. Measured on this repository's 72 specs,
every one came back with `slug` = `2026-07-25-decide-agents-md-harness-default` and `date` = `""`,
and **nothing reported anything** — no exception, no finding, no warning. A `validate` run over a
corrupted front was green.

> **A pattern that is permissive enough to describe the new form is usually permissive enough to
> match the old one. Refuse the old form explicitly, and assert that refusal.**

```python
SPEC_FILE_RE = re.compile(r"^(?!\d{4}-\d{2}-\d{2}-)([a-z0-9]+(?:-[a-z0-9]+)*)\.md$")
```

The lookahead is the whole fix, and it is load-bearing rather than defensive: it converts silent
identity corruption back into the `sp-bad-filename` finding it always should have been. Note what it
does **not** do — a slug may still legitimately begin with digits (`2026-roadmap`); only the full
date prefix is rejected, because only the full date prefix is the superseded form.

**The assertion is the deliverable, not the pattern.** A recogniser changed without a case that
feeds it the old form has recorded an intention, not a behaviour. The case must assert the
**refusal**, not merely that the new form still passes — the new form passing is exactly what was
true while the bug was live.

## Half two — "not mine" and "mine, but stale" are different answers

The same change had a second recogniser, in the external backends: an issue is a spec when its body
opens with a `quenching-spec` marker naming the file. The loop read

```python
filename, head, parts = hybrid_unwrap(issue.get("body") or "")
m = SPEC_FILE_RE.match(filename)
if not m:
    continue          # <- an ordinary issue AND a stale spec take this branch
```

An ordinary bug report and a spec whose marker still carried the dated basename left through the same
`continue`. That is correct for the bug report and catastrophic for the spec: between the task that
tightened the pattern and the task that rewrote the markers, **the entire front would have been
invisible** — `list` empty, `validate` clean, `next --front` with nothing to rank — and no output
would have said so. An empty front and a fully-migrated front are indistinguishable at a glance,
which is what makes this failure mode survive a human looking straight at it.

> **A record that DECLARES itself in scope and then fails the format is a finding or a separate
> bucket. It is never the same discard as a record that never claimed to be yours.**

The marker is the declaration of intent. Once it parses, the record is ours, and every later failure
is a fact about *our* data:

```python
if not m:
    if LEGACY_DATED_FILE_RE.match(filename):
        legacy.append(...)      # a SPEC, kept apart — `migrate` reads this and nothing else does
    continue
```

Keeping the stale ones in a bucket the read path never serves is the deliberate part: a
half-migrated front that half-works is worse than one that says so. The migration reads that bucket;
every other command behaves as though those records do not exist, so nobody silently operates on a
document under an identity the tool no longer means.

## What this obliges, in order

1. **Write the old form into the case list before changing the pattern.** The case asserts a
   refusal; the pattern is what makes it pass.
2. **Migrate in the same function that drops.** Where the superseded form is the *only* copy of a
   fact — the date prefix was — the fold that removes it must write it to its new home in one call
   no caller can perform half of. Dropping first loses the fact; adding first and dropping later
   leaves two copies free to disagree in between.
3. **Never let the migrated copy win over a declared one.** A record that already carries the new
   field keeps it: a human may have corrected the field, and nobody ever renames a marker to correct
   a date.
4. **Prove the fold offline against the real corpus before writing.** A `--dry-run` that performs the
   whole transform and compares byte for byte answers "will this lose anything" with a measurement
   instead of an argument — and it is the only chance to answer it before the store is rewritten.

## The tell

Both failures share one shape, and it is worth recognising directly: **the tool had a confident,
well-formed thing to say, and the thing was about data that no longer existed in the form it
assumed.** No exception was raised in either case, because no rule was broken — the rules had simply
stopped describing the input. That is why neither could be caught downstream, and why the assertion
has to sit at the recogniser rather than at whatever consumes it.
