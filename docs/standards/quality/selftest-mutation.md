---
type: standard
title: Mutation-checking a selftest
description: A selftest that has never been observed to fail is an untested test — the mutation pass that earns the claim, one mutation per rule the fixture exists to prove, why the pass is run once at authoring rather than wired into CI, and the graduation gate this repo's three shipped selftests have not yet cleared
resource: plugins/quenching/assets/bin/session.py, plugins/quenching/assets/bin/skills.py, plugins/quenching/assets/bin/specs.py, plugins/quenching/assets/hooks/okf-validate.py
tags: [quality, testing, selftest, mutation, verification]
timestamp: 2026-08-02
audience: both
authority: background
source: improve-command-from-session plan — the mutation pass was run against session.py's selftest at task 2.1 and recorded in that spec's `## Discoveries`; a second pass, over the routing rules only, ran against skills.py's selftest during route-commands-without-always-on-descriptions (7 mutations, 2026-08-02) — the rest of that tool's corpus and the whole of specs.py's and okf-validate.py's still have not had it
maintainer: quenching
---

# Mutation-checking a selftest

Every stdlib tool in this repo carries a `selftest` subcommand, and CLAUDE.md's verification block
leans on all four of them. A selftest is the cheapest verification the repo has — and the easiest
to write so that it can never fail.

**A selftest that passed the first time it was run has proved nothing yet.** It has demonstrated
that some code returns some value; it has not demonstrated that the value is *checked*. A fixture
list that is iterated but never compared, an assertion on a field the parser always populates, a
case appended to the corpus but never reached — each passes exactly as loudly as a real check.

## The rule

Before a selftest is claimed as verification, **break the thing it exists to prove and watch it
fail.** One mutation per rule, applied to the code under test, reverted after.

The pass is done **once, at authoring**, by the human or agent writing the selftest. It is not
wired into CI and there is no mutation-testing dependency — this repo has no build step and no test
framework, and adding one to prove four `selftest` subcommands would cost more than the tools do.
What survives the pass is not tooling but a claim in the commit that wrote it.

## What a mutation is worth

A mutation earns its place when it is **a rule the fixture exists to prove**, not an arbitrary edit.
Deleting a whole function proves nothing: everything fails, and a selftest that catches a deleted
function may still miss every subtle case. The useful mutation inverts one decision.

The pass over `session.py`'s selftest (`session.py:selftest`, 15 fixture records) ran four:

| Mutation | Rule it attacks | Result |
| --- | --- | --- |
| stop excluding `isMeta: true` turns | the harness's own echo of a command body is not a human correction | 2 assertions fail |
| read only the bare-string form of a user turn | a human turn arrives as text **blocks** in a list | 1 assertion fails |
| count `Edit`/`Write` against a file as a read | reads and writes are different facts | 2 assertions fail |
| drop the `uuid` dedup | one turn replayed is not two turns | 1 assertion fails |

Each mutation failing **one or two** assertions rather than all fifteen is itself the signal worth
reading: it means the assertions are discriminating between rules instead of all riding on one
happy path. A mutation that fails every assertion, or none, is a fixture that needs work.

The third row is the one that justifies the whole practice. Counting writes as reads is not a
hypothetical: it shipped once, and reported 51 edits as `redundant read x72` — a confident,
plausible, entirely wrong finding, against a run whose honest redundant-read count was **0**. The
selftest that now holds that line was written *after* the bug, which is the ordinary case; the
mutation pass is what confirms the line is actually held rather than merely intended.

## The second pass — `skills.py`, and why it counts as partial

Run 2026-08-02 for `route-commands-without-always-on-descriptions`, against the rules that spec
added: the residency predicate `budget` and `lint` both read from, and the set of commands a
conductor reaches by name, derived from the bodies. Seven mutations, seven observed failures:

| Mutation | Rule it attacks | Result |
| --- | --- | --- |
| `description_is_resident` → always `True` | prose routing does not reach a typed-only command | `/docs:typed-only-bare`: expected `[]`, got `sk-no-boundary`, `sk-trigger-position` |
| `description_is_resident` → always `False` | …and it *does* reach a resident one | `/docs:routed-bare`: expected both codes, got `[]` |
| drop the leading-slash exclusion | `/prefix:name` is a citation aimed at a human, not a hand-off | `/docs:stage-cited` wrongly flagged `sk-inert-stage` |
| drop the Skill-tool arm | the unprefixed slash form near "Skill tool" is also a hand-off | `/docs:stage-handed` not flagged |
| drop the registry arm | the bare registry form is the hand-off | `/docs:stage-inert` not flagged |
| drop the self-reference guard | a command cannot conduct itself | `/docs:typed-only-bare` wrongly flagged |
| ungate `sk-inert-stage` from the caller set | typed-only is legitimate when nobody names it | **crash** — `TypeError: 'NoneType' object is not iterable` |

Six of the seven land the way the section above says a useful mutation lands: one named fixture
case, expected and actual code lists printed side by side. **The seventh does not, and naming that
is worth more than counting it.** It failed by raising, so what caught it was Python, not the
corpus. A crash proves the mutated path is reached; it does not prove the fixture discriminates —
the same mutation in a tool that tolerated the bad value would have survived silently. Read
strictly, this is six mutations that earned the claim and one that only looks like it did.

**And it covers the new rules only.** `skills.py`'s selftest also carries fixtures for the two
description caps, body length, step criteria, tool scoping, the hook codes and the citation form,
and none of those was mutated. Adding a rule with a mutation beside it is the practice working; it
is not the same as having checked the tool.

## Where this sits

This is the authoring-time complement to the two verification gates already written:
[bundle-verification.md](bundle-verification.md) decides *which invariants are owed a deterministic
check at all*, and [surface-verification.md](surface-verification.md) covers what only a fresh
process can prove. This standard governs neither of those — it asks the narrower question of
whether a check that exists is load-bearing.

It shares a premise with [parse-honesty.md](parse-honesty.md): both refuse to let a tool's silence
read as a clean result. There, a parse failure is named rather than reported as a content gap; here,
a selftest that cannot fail is named rather than counted as coverage.

## Graduation gate

`authority: background`, and the gate is explicit. Two passes exist: `session.py`'s whole selftest
(four mutations, 2026-07-29) and `skills.py`'s **newest rules only** (seven, 2026-08-02). What is
still unchecked is the rest of `skills.py`'s corpus and the whole of `specs.py`'s and
`okf-validate.py`'s — selftests CLAUDE.md's verification block treats as the repo's primary gate,
and which **have never been observed to fail.** They may well be sound; nobody has checked.

This becomes `authority: current` when a pass of the shape above has been run against all three
shipped tools and the result recorded — not before. A pass over one tool's newest rules does not
clear it, and booking it as partial rather than as progress is the same honesty the standard asks
of the mutations themselves. Until then this describes a practice the repo has adopted twice and
not generalised, which is what the `background` stamp is for.
