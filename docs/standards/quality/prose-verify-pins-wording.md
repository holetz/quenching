---
type: standard
title: A `verify:` that greps prose pins the wording it asserts
description: A check written as a grep over prose does not prove the prose — it pins it to the phrase the check named, and the resulting failure is ambiguous between "the text is wrong" and "the check named a phrase nobody agreed to"; how to write the assertion, how to read the failure, the third reading that is never permitted, and the negative face where the check forbids a string the spec itself requires elsewhere
resource: plugins/quenching/commands/**, plugins/quenching/assets/references/**
tags: [quality, verification, prose, specs, verify]
timestamp: 2026-08-27
audience: both
authority: current
source: spec observacoes-do-triage-sem-portador-de-acao (distilled at conclude) — measured on task 3.1, whose `verify:` required "qualquer coluna que nomeie um comando" in lowercase and failed because the bullet actually written opened with "Qualquer"; §The negative face added by spec 1003 (2026-08-27), which measured the inverse three times on the same branch — a `verify:` forbidding the string `mkdocs` in three files where the `## Proposal` itself required it to appear
maintainer: quenching
---

# A `verify:` that greps prose pins the wording it asserts

## The rule

> A `verify:` that greps prose **does not prove the prose — it pins it to the phrase the check
> named.** Write the assertion over a phrase the wording has already settled, or accept that the
> check is choosing the words before the writer does.

A check over code asserts a **behaviour**: it passes with any implementation that behaves that way.
A check over prose asserts a **sequence of characters**, and prose has infinitely many sequences
that say the same thing. On the `verify:` line the two look alike, and they are not the same thing.

## How to read the failure

A failure here is **ambiguous by construction**, and the two honest readings call for opposite
actions:

| What is wrong | How you recognise it | What to do |
| --- | --- | --- |
| the text | the required phrase is the one the author actually meant, and the text does not contain it | change the text |
| the check | the required phrase was never agreed — a sentence-initial capital, a synonym, a different order | it is a definition defect: `/quenching:specs:develop` fixes the `verify:` |

The **third reading is never permitted**: rewriting the check to match whatever the text happens to
say. It is the prohibition `/quenching:specs:execute` already carries — never edit the assertion so
it stops failing — applied to the case where the assertion is a string.

## How to write the assertion

- **Name a phrase the wording has already settled**, never one it has yet to choose. The moment to
  write that `verify:` is after the text exists; before that it is a guess about words.
- **Prefer the middle of the sentence to its edge.** A fragment that can open a bullet will be
  capitalised by whoever writes it, and that capital is exactly the difference that takes down a
  `grep` without `-i`.
- **Assert the term, not the sentence.** The smaller the required fragment, the less wording the
  check pins — and the term is precisely the part that should not vary.
- **Prove the check knows how to fail** before writing the text that makes it pass: running it
  against the tree before the fix and requiring a non-zero exit is what separates a check from an
  ornament.

## The negative face: the check that forbids a string

The inverse form — `! grep -q "<palavra>" <arquivo>` — looks safer, because it chooses no words: it
only forbids one. **It pins more, not less.** A prohibition holds over the whole file, so it reaches
every legitimate use of the word the spec itself requires elsewhere, and the author finds that out
only when the check shuts the door in front of the right text.

Three measurements on the same branch (spec 1003), all with the string `mkdocs`:

| Where | The legitimate use the check forbade |
| --- | --- |
| a command's body | the spec required, in a `## Proposal` bullet, that the command recognise the legacy configuration — which can only be written by naming it |
| the plugin's README | the version changelog records what 0.9.0 actually delivered; rewriting that would falsify the record |
| the translated mirror | it is a literal translation of the source, so it inherits both the legacy handling and the changelog |

The failure mode is the same in all three: **the check's target is the file, and the rule's target
was the mechanism.** What had to disappear was not the word — it was the command nobody can run any
more, the flag that does not exist, the plugin that does not run. Written this way, the check goes
back to asserting behaviour:

```bash
# forbid the dead mechanism, not the word
! grep -qE "mkdocs build|--site-dir|awesome-pages" <arquivo>
# and, when the file has a historical half, sweep only the living half
! awk '/^- \*\*[0-9]+\.[0-9]+\.[0-9]+:/{exit} {print}' README.md | grep -qi mkdocs
```

**Two rules fall out of this.** A prohibition over a file that contains history has to delimit the
live part, because history is not corrected — it is rewritten, and rewriting it is lying. And a
prohibition over a **generated** artifact is never the right check: what you assert of it is that it
is up to date with its source, not what the translator happened to produce.

The third reading stays forbidden here: none of this authorises loosening the prohibition so the
text that happens to exist can pass. What authorises the swap is the prohibition **contradicting a
written requirement of the spec itself** — and the swap is then declared, with the reason recorded
where the reviewer will find it.

## Relation to neighbouring standards

- [self-matching-guards.md](self-matching-guards.md) — the case where the checker itself matches the
  text it forbids. Here it is the inverse: the check does **not** match a text that is right.
- [prose-sweeps.md](prose-sweeps.md) — a mechanical substitution corrupts precisely the sentences
  that *talk about* the substituted form. All three say the same thing from different angles: prose
  is not a stable mechanical target.
