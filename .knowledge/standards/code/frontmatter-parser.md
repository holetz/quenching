---
type: standard
title: Frontmatter parsing — the one parser
description: The YAML subset `common/frontmatter.py` reads — the comment rule (a `#` opens a comment only at the start of a value or after whitespace, and never inside a quoted scalar), the canonical case list its tests hold it to, the anomaly sidecar, and why the union it now reads is wider than any of the three parsers it replaced
resource: plugins/quenching/assets/bin/quenching/common/frontmatter.py
tags: [code, parsing, yaml, frontmatter, tools]
timestamp: 2026-08-10
audience: both
authority: current
source: modularizar-specs-knowledge-components spec, task 9.1 — retired with frontmatter-parsing.md (2026-08-10), whose comment rule, canonical case list and anomaly sidecar this file inherits; the three-copy lockstep the retired doc held was itself the premise task 2.1 removed, once nothing installed standalone any more
maintainer: quenching
---

# Frontmatter parsing — the one parser

`common/frontmatter.py` is the **one** parser every pillar reads YAML frontmatter through —
`specs`, `knowledge` and `components` alike. Three hand-written mini-parsers used to hold this
line, one per shipped script, because each ran self-contained out of a target repo's
`.claude/hooks/` and could import nothing else
([align/tool-resolution.md](/plugins/quenching/assets/references/align/tool-resolution.md)
§Resolving the tool). Nothing installs standalone any more — every pillar resolves through
`${CLAUDE_PLUGIN_ROOT}/assets/bin/cq` — so the premise that forced three copies is gone, and this
module is what replaced them.

It governs the **subset of YAML** the parser claims to read, and — just as importantly — what it
must be able to say when it has read something it could not represent faithfully. That second half
is [../quality/parse-honesty.md](../quality/parse-honesty.md)'s rule; this file supplies the
mechanics it applies to.

## Normalizing upward, not picking a winner

The three predecessors never read the same YAML subset, and no two read the same one:

| Form | `specs` read | `skills` read | `okf` read |
| --- | --- | --- | --- |
| `key: scalar`, quotes, comment | yes | yes | yes |
| inline list `[a, b]` | yes | yes | no — kept the literal `"[a, b]"` |
| block list `- item` | yes | yes | no — read as `""` |
| block record (indented `k: v`) | yes | no | no |
| flow map `{a: b}` | yes | no | no — kept the literal `"{a: b}"` |
| block scalar `\|` / `>` | no | yes | no — kept the bare indicator |

Nobody read the union: `specs` read records and flow maps but no block scalars, `skills` the
reverse. `common/frontmatter.py` reads **every** row — so `knowledge` (formerly its own dedicated checker)
gained the four forms it used to flatten, and `components` (formerly its own dedicated tool) gained records
and flow maps.

**What that costs, deliberately.** `frontmatter_anomalies` had three divergent bodies, each a
carve-out for what its own parser could not read: `okf` reported every indented run because it
read none of them, `skills` exempted block lists and `hooks:`, `specs` tested its own parse
result. Only the last criterion survives a parser that reads everything — **an anomaly is a key
the parser could not turn into a value** — so `knowledge` and `components` now report *fewer*
anomalies than they did. Nothing became invisible: they stopped denouncing forms they can now
read.

## The comment rule

> A `#` opens a comment when it is the first character of the value or is preceded by whitespace,
> and never when it falls inside a quoted scalar.

A value is a *quoted scalar* only when its first character is `'` or `"`. A quote appearing
mid-value is an ordinary character, so `at the first '#'` is a plain scalar whose `#` is preceded
by `'` — not by whitespace — and is therefore part of the value.

The rule replaces `val.split("#", 1)[0]`, which honoured none of those three conditions and
truncated every value at its first `#`. That is not a hypothetical: it cut this repository's own
spec titles and would silently cut any command `description` mentioning a heading, a colour, or
C#.

**An unterminated quoted scalar strips nothing.** When a value opens `'` or `"` and never closes
it, the parser cannot know where the scalar ends, so it keeps the value verbatim and reports the
anomaly rather than guessing a comment boundary.

## The canonical case list

`tests/test_frontmatter.py` — `CANONICAL_CASES` — holds the parser to all twelve, unchanged from
the standard this file inherits from. `value` is what `parse_frontmatter` returns for `title`;
`anomaly` is what `frontmatter_anomalies` reports.

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
indicator — because that is the one indented form this parser still does not read on an
unrecognised key, which is what makes it a live case rather than a historical one.

**The list is a floor, not a ceiling.** The parser reads every form the table above enumerates
(inline/block list, block/flow record, block scalar) and more besides — so a key whose value it
genuinely reads must *not* raise `indented-continuation`, checked against the parse result itself
rather than re-derived. What no future edit may do is disagree with a row.

## The anomaly sidecar

`frontmatter_anomalies(text)` is a **sidecar**: it re-reads the block and reports what the parse
could not represent faithfully. `parse_frontmatter` keeps returning a bare dict, so no existing
call site changes.

| Kind | What it means |
| --- | --- |
| `comment-stripped` | a trailing comment was removed from a value — and a stripped comment is byte-identical to lost prose |
| `unterminated-quote` | a value opens a quote that never closes, so its extent is unknowable |
| `indented-continuation` | a key's value is empty and the indented lines beneath it are in no form this parser reads |
| `duplicate-key` | a top-level key appears more than once and the last one silently won — nothing guarantees Claude Code's own parser resolves it the same way |

Each is reported at **warn**, never error: the parser is stating a suspicion it cannot resolve,
not a violation it has proved. Severity and the reasoning behind it belong to
[../quality/parse-honesty.md](../quality/parse-honesty.md).

**`hooks:` is exempt, and the exemption is the dialect's, not a caller's.** `ANOMALY_EXEMPT_KEYS =
{"hooks"}` is a module constant: `components` has its own dedicated reader for that nested block
(`parse_frontmatter_hooks`), so whatever this sidecar would say about it is not evidence either
way. Handing each caller its own exemption set is exactly how the three predecessor copies
diverged in the first place.

`frontmatter_block(text)` is the second, narrower sidecar — `(has_block, well_formed)` — the one
signal only `knowledge` reads: whether a file opens a `---` fence at all, and whether that fence
ever closes. `parse_frontmatter` cannot express "fence opened, never closed" on its own; it
returns an empty dict for that exactly as it does for a file with no frontmatter, and only this
function separates the two.

## Why a sidecar, and two of them

Folding either signal back into `parse_frontmatter`'s own return — a `(fm, has_block, well_formed)`
triple, which is what the retired pre-refactor checker returned — would put a three-way unpack at
every call site in every pillar to carry a signal only one of them reads. Two call sites read
`frontmatter_block`; the rest read a bare dict exactly as before.

## What this does not cover

- **A real YAML parser.** Out of contract permanently — zero-dependency is what lets this module
  run wherever `python3` does, with nothing beside it.
- **Nested structure below the first level.** The diagnostic *names* what the parser could not
  read faithfully; it does not learn to read arbitrary depth.
- **What Claude Code's own loader does.** This module reads the same files, but nothing here is a
  claim about the platform's parser. Where the two could disagree — a duplicate key, most
  obviously — the anomaly says so instead of asserting a resolution.
- **Frontmatter *content*.** Which keys are required, the `type` vocabulary, and the description
  cap belong to [../automation/skills.md](../automation/skills.md),
  [../workflows/plan-artifacts.md](../workflows/plan-artifacts.md) and the OKF spec. This file is
  only about reading the bytes.
