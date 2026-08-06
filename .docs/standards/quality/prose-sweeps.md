---
type: standard
title: Mechanical sweeps over prose
description: A find-and-replace over prose corrupts exactly the sentences that talk ABOUT the form being replaced — how to recognise those sites, why the check written to guard the sweep cannot see them, and the mitigation that survives both
resource: plugins/quenching/commands/**, plugins/quenching/assets/references/**
tags: [quality, sweeps, prose, refactoring]
timestamp: 2026-07-31
audience: both
authority: current
source: correct-command-citation-form (2026-07-31) — two sites corrupted out of 519 rewritten, caught in the branch review
maintainer: quenching
---

# Mechanical sweeps over prose

A sweep that rewrites one textual form into another across a tree of prose is the cheapest way to
move hundreds of sites, and this repo runs them: command bodies and shared references are the
source code, so a naming change is a prose change. The failure mode below is **structural**, not a
matter of care — it follows from what a regex can and cannot know.

## The mention/use distinction is invisible to a regex

A sweep replaces every *use* of a form. It also replaces every *mention* of it — the sentences
whose whole subject is the form being swept. Those sentences do not merely lose accuracy: they
become self-contradictory, because they now assert something about a form they no longer contain.

Measured on 2026-07-31: sweeping 519 bare command citations into their plugin-prefixed form
corrupted **two** sites out of 519, and both were the sentences that *defined the rule the sweep
was implementing*:

> a bare `/quenching:docs:align` is what a human types, not what the Skill tool resolves

The sentence names the bare form and then shows a prefixed one. Every other site was correct.

**Two out of 519 is the point, not a reassurance.** The corrupted sites cluster where the rule is
explained, which is the highest-leverage prose in the tree — the paragraphs future authors copy.
A sweep is most likely to damage exactly the text that teaches what the sweep was for.

## The check that guards the sweep cannot catch this

A sweep of this kind is owed a deterministic check, per
[bundle-verification.md](bundle-verification.md) §*An invariant restated in more than two skills*.
That check greps for the old form — so **after** the sweep it reports the corrupted sites as
clean, because they now carry the new form. It is measuring the thing that is right about them.

Nothing mechanical closes this. The distinction between using a form and talking about it is
semantic, and belongs to the branch review
([surface-verification.md](surface-verification.md) draws the same line for the command surface):
**the sweep is verified by a checker, its mention-sites by a reader.**

## Write the mention as a placeholder, not as an instance

The mitigation that survives is to stop the mention from being an instance at all. A sentence
explaining a form should carry the form's *shape*, not a real value:

| Instead of | Write |
| --- | --- |
| the bare `/docs:harness` resolves only where… | the bare form `/<front>:<verb>` resolves only where… |
| a bare `/docs:align` is what a human types | the registry name for the tool, `/<plugin>:<front>:<verb>` for a human |

Three things follow at once, and the third is why this is a rule rather than a preference:

1. The sentence stays true when the concrete values change.
2. It reads more clearly — a shape states the general case that an example only implies.
3. **The placeholder does not match the sweep's own pattern**, so the site is immune to the next
   sweep and invisible to the check. `<front>` is not a path segment; no regex written for real
   citations will find it.

## Sweeping a tree, in practice

- **Drive the sweep off the checker's own pattern and vocabulary**, never a hand-written `sed`. The
  sweep and the check that guards it disagreeing is a second defect on top of the first.
- **Respect the parse, not a pattern.** Where a sweep must skip a region — frontmatter, a fenced
  block — split it off with the same parser the tool uses. A regex extended to "avoid the
  frontmatter" is one that must be kept in step with a format it does not own.
- **Read the diff for mention-sites before committing**, and grep the tree for prose *about* the
  form (`grep -n 'bare' …`) rather than for the form itself. That grep is what found both sites
  here; the checker found neither.
