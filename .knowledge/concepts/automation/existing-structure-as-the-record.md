---
type: concept
title: The structure already produced is the record — a parallel catalogue can disagree with it
description: When a convention has to be remembered across invocations, reading it back from the artefacts it already produced costs nothing to maintain and cannot drift; a dedicated registry is a second source of truth that can disagree with the tree it describes
resource: plugins/quenching/assets/references/components-command-new/taxonomy.md, .knowledge/standards/automation/skills.md
tags: [automation, convention, registry, drift, naming]
timestamp: 2026-08-15
audience: both
authority: current
source: alocar-comandos-skills-por-categoria spec (2026-08-15) — distilled at conclude from its `## Design` and the central-catalogue alternative rejected in `## Alternatives Considered`
maintainer: quenching
---

A command that has to remember a decision across invocations — *which* convention this repo settled
on — reaches naturally for somewhere to write it down. That instinct produces a registry file, and
the registry is the expensive answer.

**The artefacts the convention already produced are themselves the record.** Whether a category
nests a real folder inside it or replaces it is answered by looking at what already sits under
`.claude/commands/<category>/`: a real-folder subpath present means *nest*, files sitting flat mean
*replace*. Nothing is written down, so nothing has to be kept in sync, migrated, or validated —
and the answer is derived from the very thing a future reader will be looking at anyway.

## Why the parallel catalogue is worse than no catalogue

A registry introduces a **second** statement of one fact, and two statements can disagree. The
moment they do, the file says one thing and the tree says another, and neither is obviously wrong:
a human moving a directory by hand, a rename that skipped the registry, a merge that resolved one
side only. Now something has to check that they agree, and the check is a cost the derived reading
never had.

This is the same argument
[command-surface.md](../../standards/naming/command-surface.md) §The path IS the identity makes
about names — *"Nothing derives a name that could disagree with the path, so nothing checks that
they agree"* — applied one level up, from a name to a convention. A path cannot drift from itself;
neither can a convention read out of the paths.

## What it costs, and when it does not apply

The derived reading is **silent about the first time**. An empty category, or one where both
shapes already appear, answers nothing — so the mechanism needs an honest fallback: ask the human
once, and let the structure that answer produces become the record from then on. A design that
cannot say "I don't know yet" would have to guess, and guessing is how the wrong convention gets
enshrined for every later command.

It also **does not travel**. Two repos may settle opposite conventions for the same category name,
because each repo's answer lives in its own tree. That is a genuine loss of cross-repo consistency,
accepted deliberately: a shared catalogue would impose a vocabulary of subjects no target repo asked
for, and the cost of maintaining it exceeded the consistency it bought.

Read those two together as the applicability test. Deriving beats cataloguing when the convention
**leaves a visible trace** in what it produces and the scope is one repo. A convention that produces
no trace, or one that must hold identically across repositories, has nothing to read back and needs
a record of its own.
