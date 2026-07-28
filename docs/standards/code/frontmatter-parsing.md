---
type: standard
title: Frontmatter parsing
description: The YAML subset the three shipped tools read — the comment rule (a `#` opens a comment only at the start of a value or after whitespace, and never inside a quoted scalar), the canonical case list all three must decide identically, the anomaly set each must be able to name, and the three-copy lockstep obligation that replaces the shared module they cannot have
resource: plugins/quenching/assets/bin/skills.py, plugins/quenching/assets/bin/specs.py, plugins/quenching/assets/hooks/okf-validate.py
tags: [code, parsing, yaml, frontmatter, tools, lockstep]
timestamp: 2026-07-28
audience: both
authority: current
source: fix-skills-py-description-truncation spec — written at task 1.1 before anything implemented it, promoted at task 3.2 once all three tools passed the canonical case list in their own selftests
maintainer: quenching
---

# Frontmatter parsing

Three shipped tools read YAML frontmatter with three hand-written mini-parsers:
`assets/bin/skills.py`, `assets/bin/specs.py` and `assets/hooks/okf-validate.py`. Each installs
**standalone** into a target's `.claude/hooks/`, so none may import the others and there is no
shared module to hold the rule. This standard is what holds it instead.

It governs the **subset of YAML** those parsers claim to read, and — just as importantly — what
they must be able to say when they have read something they could not represent. That second half
is [../quality/parse-honesty.md](../quality/parse-honesty.md)'s rule; this file supplies the
mechanics it applies to.

## Why there are three copies and not one module

Zero-dependency and self-contained is the tools' contract: each is copied into a target repo by
its own align and runs there with nothing beside it. An extracted `frontmatter.py` would have to be
installed as a fourth file, found on `sys.path`, and version-matched against three callers — which
trades a duplication problem for a distribution problem.

Duplication is the existing mold, not a new concession: `specs.py` already embeds `schema.json` and
`templates/spec.md` as constants for exactly this reason, and `specs.py selftest` is what keeps
those honest. The same shape applies here — **the canonical case list below is the lockstep unit**,
and each tool's `selftest` runs it.

## The subset each parser claims to read

Only **top-level** `key: value` pairs of the leading `---` block. Anything else is out of contract
and must be *named* rather than guessed at.

| Form | `skills.py` | `specs.py` | `okf-validate.py` |
| --- | --- | --- | --- |
| `key: scalar` | yes | yes | yes |
| surrounding quotes stripped | yes | yes | yes |
| inline list `[a, b]` | yes | yes | no — scalar |
| block list `- item` | yes | yes | no |
| inline record `{a: b}` | no — scalar | yes | no — scalar |
| block record (indented `k: v`) | no | yes | no |
| block scalar `>` / `\|` | yes | no | no |
| nested `hooks:` block | via `parse_frontmatter_hooks` | n/a | n/a |

A tool reading *less* is not a defect — each reads what its own checks inspect. A tool reading
something **differently** is, and that is what the canonical list pins down.

## The comment rule

> A `#` opens a comment when it is the first character of the value or is preceded by whitespace,
> and never when it falls inside a quoted scalar.

A value is a *quoted scalar* only when its first character is `'` or `"`. A quote appearing
mid-value is an ordinary character, so `at the first '#'` is a plain scalar whose `#` is preceded by
`'` — not by whitespace — and is therefore part of the value.

The rule replaces `val.split("#", 1)[0]`, which honoured none of those three conditions and
truncated every value at its first `#`. That is not a hypothetical: it cut this repository's own
spec titles and would silently cut any command `description` mentioning a heading, a colour, or C#.

**An unterminated quoted scalar strips nothing.** When a value opens `'` or `"` and never closes it,
the parser cannot know where the scalar ends, so it keeps the value verbatim and reports the anomaly
rather than guessing a comment boundary.

## The canonical case list

Every tool must decide **all twelve identically**, and each tool's `selftest` runs them. `value` is
what `parse_frontmatter` returns for `title`; `anomaly` is what `frontmatter_anomalies` reports.

| # | Frontmatter line | `value` | `anomaly` |
| --- | --- | --- | --- |
| 1 | `title: a plain value` | `a plain value` | — |
| 2 | `title: a value # a note` | `a value` | `comment-stripped` |
| 3 | `title: truncates at the first '#'` | `truncates at the first '#'` | — |
| 4 | ``title: the `#` character`` | ``the `#` character`` | — |
| 5 | `title: C#` | `C#` | — |
| 6 | `title: "quoted # inside"` | `quoted # inside` | — |
| 7 | `title: 'single # inside'` | `single # inside` | — |
| 8 | `title: "quoted" # a note` | `quoted` | `comment-stripped` |
| 9 | `title: # a note` | *(empty)* | `comment-stripped` |
| 10 | `title: "unterminated` | `"unterminated` | `unterminated-quote` |
| 11 | `title: first` then `title: second` | `second` | `duplicate-key` |
| 12 | `title:` then an indented prose line | *(empty)* | `indented-continuation` |

Rows 3, 4 and 5 are the ones that make the rule worth stating: each contains a `#` that a naive
split removes and YAML keeps. Row 12 uses a bare wrapped line — no `- `, no `:`, no block-scalar
indicator — because that is the one indented form **none** of the three parsers reads, which is what
makes it common ground.

**The list is a floor, not a ceiling.** A tool may read more than the table requires (`specs.py`
reads block records; `skills.py` reads block scalars), and must then *not* raise
`indented-continuation` for the form it genuinely read. What no tool may do is disagree with a row.

## The anomaly set

`frontmatter_anomalies(text)` is a **sidecar**: it re-reads the block and reports what the parse
could not represent faithfully. `parse_frontmatter` keeps returning a bare dict, so no existing call
site changes.

| Kind | What it means |
| --- | --- |
| `comment-stripped` | a trailing comment was removed from a value — and a stripped comment is byte-identical to lost prose |
| `unterminated-quote` | a value opens a quote that never closes, so its extent is unknowable |
| `indented-continuation` | a key's value is empty and the indented lines beneath it are in no form this tool reads |
| `duplicate-key` | a top-level key appears more than once and the last one silently won — nothing guarantees Claude Code's own parser resolves it the same way |

Each is reported at **warn**, never error: the tool is stating a suspicion it cannot resolve, not a
violation it has proved. Severity and the reasoning behind it belong to
[../quality/parse-honesty.md](../quality/parse-honesty.md).

Why a sidecar rather than a `(fm, understood)` tuple, which would have mirrored the 3-tuple
`okf-validate.py` already returns: nine call sites would change, and each `specs.py` caller —
`status`, `next`, `triage` — would then have to decide what an un-understood frontmatter means
mid-cycle. That is a behaviour change in commands that today never refuse, bought for a signal only
two places actually read.

## The three-copy lockstep obligation

**Edit all three, or none.** A change to the comment rule, to the anomaly set, or to the canonical
list is a change to three files plus this standard.

The list is what makes drift loud and local: a parser that moves fails **its own** `selftest` on a
row the other two still pass, naming the tool that moved. Nothing else forces the three to agree, so
this is not a convenience — it is the entire mechanism.

Adding a case means adding it to the table above **and** to all three `selftest` fixtures in the
same change. A case list one tool does not run proves nothing about that tool.

## What this does not cover

- **A real YAML parser.** Out of contract permanently — zero-dependency is what lets these tools
  install standalone.
- **Teaching the parsers nested keys or flow values.** The diagnostic *names* what a tool cannot
  read; it does not learn to read it.
- **What Claude Code's own loader does.** These tools read the same files, but nothing here is a
  claim about the platform's parser. Where the two could disagree — a duplicate key, most obviously
  — the anomaly says so instead of asserting a resolution.
- **Frontmatter *content*.** Which keys are required, the `type` vocabulary, and the description cap
  belong to [../automation/skills.md](../automation/skills.md),
  [../workflows/plan-artifacts.md](../workflows/plan-artifacts.md) and the OKF spec. This file is
  only about reading the bytes.
