---
type: standard
title: A guard that names what it forbids must parse, not match
description: A checker whose finding text quotes the pattern it prohibits will match itself — the self-accusation this repo measured on its first run, why the fix is parsing the construct rather than excluding the checker, and the narrow case where a substring scan is still honest
resource: plugins/quenching/assets/bin/quenching/specs/**
tags: [quality, verification, selftest, parsing, false-positive]
timestamp: 2026-08-10
audience: both
authority: current
source: anunciar-resolucao-aproximada-em-todos-os-verbos spec (distilled at conclude) — measured on the first run of `announcement_failures()`, which flagged `selftest` for the call quoted in its own remedy string
maintainer: quenching
---

# A guard that names what it forbids must parse, not match

A structural guard scans code for a construct nobody should write. It also has to *say* what it
found, and the most useful thing it can say names that construct. Those two facts collide: **the
guard's own source now contains the pattern it is looking for**, and a substring scan reports the
guard as the violation.

## The failure, as measured

`announcement_failures()` asserts that no CLI verb resolves the human's slug outside the shared
resolver. Its first implementation scanned each verb's source for `read_spec(args.spec)`, and its
finding carried a remedy naming that same call so a reader would know what to fix.

The first run flagged `selftest` — because `cmd_selftest` holds the remedy string. The guard was
correct about the bytes and wrong about the program: prose describing a call is not a call. Every
real verb passed, and the one finding it produced was about itself.

## The rule

> A guard whose own text names the construct it forbids **parses** that construct — `ast`, a real
> tokenizer, the language's own reader — rather than matching it as a substring.

Parsing is not a hardening step taken for elegance. It is what makes the check *mean* what its
finding says: `_resolves_directly` asks for a `Call` node whose function is an attribute
`read_spec` and whose first argument is `args.spec`, so a docstring, a comment and a remedy string
are all invisible to it by construction — not by exclusion.

## Why excluding the checker is the wrong fix

The tempting repair is to skip the guard's own function, or to split the forbidden string so it
never appears whole. Both leave the substring scan in place, and both fail the next time somebody
does the honest thing:

- **Excluding the checker** blinds the guard to the one function most likely to be edited by
  whoever is changing the rule.
- **Splitting the string** (`"read_spec(" + "args.spec)"`) makes the remedy unreadable in source
  and silently breaks the moment a second file quotes the rule — a standard citing it, a test
  fixture, a docstring in the code being governed.

Both are the shape [shared-mold-keys.md](../architecture/shared-mold-keys.md) rejects on a
different field: a rule that survives only while everyone remembers a workaround.

## Where a substring scan is still honest

Nothing here says parsing is always required. A substring scan is fine when the pattern **cannot**
appear in prose about itself — a generated marker, a UUID, a `<!-- BEGIN GENERATED -->` fence — or
when the scanned text is not source code at all. The rule binds exactly where the checker's own
vocabulary and the checked construct are the same characters.

The cheap test: **write the finding first.** If the sentence the guard would print contains the
thing the guard is hunting, it needs a parser.
