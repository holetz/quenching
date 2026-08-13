---
type: standard
title: The seams a prose deletion opens
description: Removing prose damages the text left behind, not only the text never opened — the hard wrap makes the line a unit the sentence does not respect, an orphaned continuation is promoted under the neighbouring bullet rather than left as litter, and a grant's justification outlives the use that earned it; the three seams measured on one branch, why every checker stays green through all three, and the reading that closes them
resource: plugins/quenching/**
tags: [quality, deletion, prose, refactoring, review]
timestamp: 2026-08-10
audience: both
authority: current
source: remover-a-capability-quenching-md spec (2026-08-08) — three defects found at the branch review of a removal that deleted 2588 lines across 27 files; all three sat in files the tasks had opened and edited, which is what distinguishes them from withdrawn-contract-residue.md's misses
maintainer: quenching
---

# The seams a prose deletion opens

Two standards already cover what a removal leaves *unedited*:
[withdrawn-contract-residue.md](withdrawn-contract-residue.md) — the sites the branch never
opened, asserting the withdrawn contract in their own words — and
[prose-sweeps.md](prose-sweeps.md), where a *replacement* corrupts the sentences that talk about
the form being replaced.

This one covers the complement, and it is the one a reviewer least expects: **the sites the branch
did open, and edited, and got wrong in the editing.** The unit a deletion operates on is not the
unit the prose is written in, and the gap between them is where all three seams below live.

## The measurement

One branch removed a whole capability — 2588 lines across 27 files, 20 tasks, every task
self-reviewed. A grep for the removed artefact's name came back empty, and every gate was green.
The branch review found three defects, one per seam:

| # | Site | What the edit did | What the file then said |
| --- | --- | --- | --- |
| 1 | `plugins/quenching/README.md` | deleted a wrapped line whose first two words ended the *previous* sentence | *"…contradicting every other statement that the inbox is outside"* — then a new paragraph |
| 2 | the knowledge front's `align.md` (then still `commands/docs/`) | deleted a bullet, kept its three indented continuation lines | the continuation reattached to the **preceding** bullet, telling a live command to list a file that no longer exists |
| 3 | the components front's `align.md` (then still `commands/skill/`) | deleted the only thing a `Bash(cp:*)` grant was for | the body still justified the grant by *"the manual install"*, and the grant was still in `allowed-tools` |

## Seam 1 — the line is the tool's unit, the sentence is the reader's

Hard-wrapped prose puts sentence boundaries mid-line. `git diff`, a `sed` range and the model's own
"delete that line" all operate on lines, so a line that *begins* with the tail of the previous
sentence takes that tail with it:

```
  descriptions said "OKF backlog", contradicting every other statement that the inbox is outside
  the bundle. The `/docs:*` command count in the row said nine while the ...
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ what had to go
  ^^^^^^^^^^^ what went with it
```

The result is a truncated sentence that is still well-formed markdown, still renders, and still
passes every structural check. **Delete the span, not the line** — and when the deletion ends
mid-line, re-read the surviving line as a sentence rather than as a diff hunk.

## Seam 2 — an orphaned continuation is promoted, not left behind

Deleting a list item and keeping its continuation lines does not leave inert text. Indentation is
positional: the orphan reattaches to whatever item now precedes it, and inherits that item's
authority. In the case measured, three lines about a payload's OKF exemption landed under the
`knowledge/` scaffolding bullet of a live command body — instructing a future session to list a
file the same branch had deleted.

This is strictly worse than litter, and it is why the seam is worth a rule of its own: the deletion
did not merely fail to remove something, it **created a wrong instruction in a place that was
previously correct**. A reviewer scanning for what survived will not find it, because the text is
not where it used to be.

**The unit of deletion for a list item is the item and everything indented under it**, to the next
sibling or the end of the block.

## Seam 3 — a justification outlives the use it justified

Capabilities are granted in one place and justified in another. Removing the work that needed a
capability leaves both: the grant, which is now wider than
[skills.md](../automation/skills.md) §`allowed-tools` is always scoped permits, and the sentence
justifying it, which now describes work nobody does.

The general form: **an artefact removed for being unused takes its enabling declarations with it.**
`allowed-tools` entries are the instance this repo measured; the class also holds a dependency
whose only importer went away, and a config key whose only reader was deleted. Ask of every
removal *what was only there because of this?* — the answer is rarely nothing, and it is never
found by grepping for the removed thing's name, since a grant names a capability, not its purpose.

## Why every checker stays green

Same structural blindness the two sibling standards tabulate, for the same reason. All three
defects are well-formed prose:

- `cq knowledge` reads valid frontmatter and valid links; a truncated sentence is neither.
- `cq components lint` reports an **unscoped** `Bash`, not a scoped grant with nothing to do —
  measuring whether a grant is used would mean reading the body, which is the thing being deferred.
- `cq components doctor` counts commands and their entry points; a promoted orphan is inside a body.
- The per-task self-review sees one task's diff, and each of the three edits was correct **as its
  own hunk** — the damage is to the text the hunk did not touch.

The reviewer's question in
[withdrawn-contract-residue.md](withdrawn-contract-residue.md) §The reviewer's question —
*what did this branch make false?* — finds these too, but only if it is asked of the files the
branch **did** change, and of the lines adjacent to each deletion rather than of the deletion
itself.

## In practice

- **Read each deletion's seam**, not each deletion. For every hunk that removes prose, read the
  line before and the line after in the *result*, as prose.
- **Delete list items whole**, continuation lines included.
- **Ask what was only there because of this** — grants, imports, config keys, and the sentences
  that justify them.
- A removal branch's review is therefore not only *what still asserts the removed thing?* but
  *what did removing it break in the text that stayed?*
