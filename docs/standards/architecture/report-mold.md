---
type: standard
title: A front's report is a mold, owned once
description: The shape a front's commands print their report in belongs to ONE section every one of them cites — three fixed bands, an ordered set of columns each command takes a subset of, and every column naming a command executable as printed — and a block whose cells come from a payload is rendered by the TOOL, with the body quoting the output, because a format rewritten in eight bodies goes stale in seven, a table rewritten in three renderers diverges in all three, and no checker sees either
resource: plugins/quenching/assets/references/specs-develop/spec-driven.md, plugins/quenching/commands/specs/*.md, plugins/quenching/assets/bin/quenching/specs/commands/next.py
tags: [architecture, commands, report, output, references, specs]
timestamp: 2026-08-16
audience: both
authority: current
source: branch holetz/specs-report (2026-08-04); the renderer clause, from the listagem-ranqueada-nativa-no-cq-specs spec (2026-08-16), measured over a front of 147 specs — three renderers of one table, 338,875 bytes cut to 8,455 — measured over the eight /quenching:specs:* bodies before and after; the divergence with commands/knowledge/status.md §4 is recorded below and was deliberately left uncorrected
maintainer: quenching
---

# A front's report is a mold, owned once

A front has several commands and **one** reader. What that reader sees at the end of every run is
the most visible product of the whole front, and it is the one part no validator inspects.

## The rule

> The shape a front's commands print their report in belongs to **one** section every one of them
> cites. Each body declares only its own delta: which body blocks, fixed or optional; which columns;
> which next-step candidates and under what condition.

For the `specs` front that section is
`plugins/quenching/assets/references/specs-develop/spec-driven.md`
§The report mold, cited by seven of the eight `/quenching:specs:*` commands.

The mold is **literal**: it carries the rendered block the body copies and substitutes into, not a
description of what the block ought to contain. That choice is not aesthetic — the only two commands
that already had consistent output before this work (the front's router, since retired, and
`/quenching:specs:execute`) were exactly the two carrying a literal block, and the six that
described the report in prose produced six different shapes.

### What the mold fixes

- **Three bands, in this order, always:** header · body · next step.
- **Fixed versus optional is declared, not improvised.** A fixed block with no content prints its
  title and `—`; an optional block with no content is omitted whole. A fixed block that vanishes
  when empty is indistinguishable from a pass that dropped it; an optional one printed empty is
  noise in every run.
- **An ordered set of columns**, from which each command takes a subset — never reordering, never
  inventing. Each column declares the **source** it comes from and when it reads `—`.
- **A mold with a code column serves only output whose code a contract defines.** Loosening that
  column to accommodate output that has no code strips the other citers of the guarantee that makes
  the mold worth having. Output with no code asks for a mold of its own — another sub-section of the
  same section — never an invented code nor a relaxed column.
- **Executable as printed holds for any column that names a command** — the real argument
  substituted; a literal `<slug>` in the output is a defect, and so is a command name without the
  argument it requires. The rule was born in the next-step block and holds identically in every
  column that points the reader at a command: an action the reader has to complete is not an action,
  it is a reminder.
- **A next-step block last**, under the rule above. Exactly one recommended line, and the reason
  tail only when there is more than one line.

## Why one section, and not prose in every body

An output format is a fact the command body *rewrites*. It is the fan-out that
[../quality/computed-fact-prose-fanout.md](../quality/computed-fact-prose-fanout.md) describes: it
changes in the first body, goes stale in the other seven, and `cq components doctor`,
`cq components lint` and `cq knowledge validate` all stay green — none of them sees prose that
describes a shape.

**The measurement, before.** Of the eight bodies, two rendered a literal block and six described the
report in prose. The accumulated result:

| Symptom | Count |
| --- | --- |
| different verbs for the closing line | 6 |
| commands with no next-step suggestion at all | 1 (`/quenching:specs:conclude`, the one that closes the spec) |
| chainings that name the command without the slug | 1 (`/quenching:specs:execute` → `conclude`) |
| ownerless wordings of "verbatim" | 7 |
| shared glyph vocabulary | none |
| tables using the `title` `cq specs` already emitted | none |

The last is the most revealing: `list --json` and `next --front` have always returned `title`, and
no table showed it. Nobody decided to omit it — there was no place where the decision could be
taken once.

## A block whose source is a payload is rendered by the TOOL

The rule above owns the **shape**. This one owns the **renderer**, and it is the same measurement
taken one step further: when a block's cells all come from a payload a tool already emits, the block
is printed by the tool and the body **quotes the output**. A body that assembles those cells —
ordering, counting, eliding — is a second renderer of a fact the tool owns, and two renderers of the
same fact diverge for the same reason eight prose descriptions diverged.

The test is the source of the cells, not the size of the block:

| The source of each cell | Who renders |
| --- | --- |
| a payload the tool already emits (`--table`, `--by-code`) | the **tool**; the body quotes it verbatim |
| a judgment the model makes in this run (a triage's `Reason` column, a proposal) | the **body**, under the shape the mold fixes |

**The measurement.** On 2026-08-16, over a front of 147 specs, **one** ranked table had **three**
hand-written and divergent renderers: a Python heredoc embedded in `/quenching:specs:triage`'s body,
prose describing the columns in `/quenching:specs:status`'s body, and a third variant improvised in
a session because neither of the other two served. All three read `cq specs list --json` — 312,511
bytes, of which 144,057 were `## Overview` prose none of the three printed. The collection step of
`/quenching:specs:status` asked for 338,875 bytes to produce a 45-row table, under a first sentence
that promised to be *"near-free by construction"*.

With the rendering moved into the tool (`cq specs next --front --table`,
`cq specs validate --by-code`), the same three blocks cost **8,455 bytes** — 97.5% less — and are
byte-for-byte the same in every body that asks for them, because there is now a single place where
they are made.

**The cost corollary is not incidental, it is the mechanism.** A body that re-aggregates a payload
needs the whole payload in context; a body that quotes a rendering needs only the rendering. That is
why the rule holds even where there is only **one** consumer: the second renderer it prevents is
expensive before it is divergent.

## Where the mold lives, and why

**The section goes inside a file the bodies already load, not in a file of its own.**

`cq components read` accepts **one file per call**. A mold in a new file would cost `+1 tool call`
per run of every command in the front; as a section of a file all of them already cite, it costs
zero calls — only its own characters.

That stretches the host file's charter, and the price is declared instead of hidden: the H1 names
the new band. A front whose commands share **no** file has no such option, and there the file of
its own is the right answer — the rule is the comparison, not the destination.

**The measured cost, and it is not small.** In the `specs` front: the section costs **9,171 chars**,
and the eight bodies together **grew by 3,615 net chars** instead of shrinking. The mold is not a
context saving; it is the trade of eight divergent and uncheckable descriptions for one definition.
Whoever applies this rule must measure and state the number, never estimate it
([../automation/context-discipline.md](../automation/context-discipline.md)).

**A new band reaches whoever already cites the mold on its own.** `cq components read --sections
"§The report mold"` returns the `###` sub-sections along with the parent section, so adding a
sub-section to the mold requires touching no body's loading — it changes only the body that will
*use* it, to declare its delta. It is the argument above carried further: the mold as a section of a
shared file costs zero calls today and zero calls when it grows.

Seven of the eight bodies cite the host file by its **bare path** and therefore read it whole, which
is by itself drift against the rule of citing by `§`-address. Narrowing them would cut far more than
the mold adds, and that is work of its own with a measurement of its own — it was not done here.

## What the mold does not own

The **language** of the labels. This plugin writes its bodies and references in English, but the
report a command prints follows the target repo's tag
([../agents/communication.md](../agents/communication.md) §What it governs). So every column has a
**canonical name**, which is its address inside the mold, and a **printed label**, which follows the
tag. These stay canonical in any language: the slug, the `stage` values, the record names, the
`sp-*` codes, a spec's fourteen `##` and the command names.

A mold that fixed the labels in English would deliver, in every adopting repo, exactly the failure
that standard names — reading the tag at session start and still reporting in English.

## Known divergence, accepted and uncorrected

Until this branch, `plugins/quenching/commands/knowledge/status.md` §4 was a near-literal copy of
`plugins/quenching/commands/specs/status.md` §4 — the same five sections, the same titles, the same
closing sentence. It was a shared format *in fact*, written twice and owned by no file.

This work touched only the `specs` front, so **the two stopped being mirrors**. That is recorded as
an accepted divergence, not as a silent pending item: the `docs` front adopting the mold is work of
its own, and until then `/quenching:knowledge:status` remains the owner of its own shape. The
alternative — generalizing the mold to three different finding vocabularies in the same move — would
have written a generic contract before there were two proven cases to generalize from.

## Relation to the neighbouring standards

- [read-only-views.md](read-only-views.md) says the read-only view **splits findings by what closes
  them**. This rule gives that split a shape: the findings table, with the `Fecha com` column.
- [shared-mold-keys.md](shared-mold-keys.md) governs what a **shared mold may contain** — there,
  frontmatter keys; here, output blocks. The question is the same: may every citer legitimately emit
  this block?
- [../quality/computed-fact-prose-fanout.md](../quality/computed-fact-prose-fanout.md) is the reason
  the rule exists, and the grep it prescribes is what finds the leftovers when the set of columns
  changes: search for the spelled-out form (the column list), not the concept's name.
