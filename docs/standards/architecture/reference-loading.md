---
type: standard
title: Loading is a call inside the step; citing is preamble prose
description: A body that needs a reference section at step N loads that section at step N, with the literal, copy-pasteable cq components read invocation — a preamble citation says where the rule lives and does not make the session open the file, and the opposite was measured happening across the eight /quenching:specs:* bodies
resource: plugins/quenching/commands/**/*.md
tags: [architecture, references, commands, skills, cq]
timestamp: 2026-08-10
audience: both
authority: current
source: spec plans/alinhar-specs-ao-report-mold.md, Design section decision 2 (proved on 2026-08-05) — before this spec's tasks 1.1-1.3, seven of the eight /quenching:specs:* bodies cited spec-driven.md §The report mold as preamble prose ("owns the shape step N prints in") and not one of the eight contained the string --sections "§The report mold"; develop.md went as far as explicitly deferring to step 8, and step 8 carried no call at all
maintainer: quenching
---

# Loading is a call inside the step; citing is preamble prose

Every `commands/**/*.md` body in this plugin cites references by `§`-address instead of restating
them — that is the context saving the whole architecture rests on. But a citation and a load are two
different acts, and confusing them is how a body ends up obeying half of the very rule it declares
itself.

## The rule

> A body that needs a reference section at step N **loads** that section at step N, with the
> literal, copy-pasteable invocation:
>
> ```bash
> cq components read <file> --sections "§X"
> ```
>
> A preamble citation — "the rule lives in `file.md` §X" — says **where** the rule lives. It does
> not make the session open the file.

A section cited only in prose is an address, not an action. A session that reads the command body
end to end sees the sentence, knows the rule exists somewhere, and moves on — the same result as an
`import` that never ran.

## The proof

Before the tasks this standard documents, seven of the eight `/quenching:specs:*` bodies cited
`spec-driven.md` §The report mold like this, in the preamble:

> "whose §The report mold owns the shape step 7 prints in"

and not one of the eight contained, at any point of its own body, the call
`cq components read ... --sections "§The report mold"`. `develop.md` went further: it explicitly
deferred to step 8 ("step 8 loads spec-driven.md's §The report mold") — and step 8, when read,
carried no call at all, only the same sentence of prose.

The measured symptom was exactly what a citation alone permits: a report emitted in free form, with
blocks, closing verbs and glyph vocabulary the cited section already fixed — because nothing in the
step forced the session to open it before writing.

The fix was not rewriting the preamble prose — it already told the truth about where the rule lives,
and deleting it would lose the explanation of why. The fix was to insert, inside each of the eight
report steps, the call the two bodies that already reported consistently
(the front's router, since retired, and `/quenching:specs:execute`, before this spec) already
contained: the literal invocation, at the exact point where the loaded block is used.

## Where a preamble citation is still right

A reference cited in the preamble and **never loaded in any step** is not a defect — it is the
common case. Most of what a body cites is background context that steers how the session thinks
about the command, and restating it inside a specific step would have nowhere to land: nothing in
the step consumes that block as an instruction to follow literally.

Loading inside the step is required when, and only when, the step produces something whose **shape**
comes entirely from a named section — a report, a frontmatter block, a commit format. In those cases
the section is the mold the step copies, and copying a mold not seen in this run is copying from
memory.

## Relation to the neighbouring standards

- [report-mold.md](report-mold.md) is the case that revealed this rule: a mold cited by eight
  bodies, where loading inside the step — instead of trusting the preamble citation — is what makes
  the shape actually converge.
- [../automation/skills.md](../automation/skills.md) governs the other side of the same
  scale: why a reference lives outside the preamble in the first place, and the ceiling a `§`-
  address avoids blowing.
- [plugin-layout.md](plugin-layout.md) establishes that `commands/**` is the only registered tree
  and `assets/` holds what is cited by absolute path — this rule is about the **when** inside the
  body, not about where the reference lives.
