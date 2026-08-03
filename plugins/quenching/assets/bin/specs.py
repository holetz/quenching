#!/usr/bin/env python3
"""specs.py — self-contained deterministic trail for the `specs/` front.

Payload of the `quenching` plugin, sibling of `assets/hooks/okf-validate.py`
and built in the same mold: stdlib-only, ZERO dependencies (its own minimal
frontmatter parser — no PyYAML), one script installed alone into a target repo.

ONE SPEC IS ONE FILE
--------------------
A spec is a single markdown file for its whole lifecycle. Phases enrich it; they
never split it. The file lives in ONE folder until it is closed, and is never renamed:

    specs/
      plans/                     # ACTIVE — captured -> proposed -> designed -> refined
        2026-07-25-<slug>.md     #          -> ready -> approved -> executing
      archive/                   # done or abandoned, told apart by `outcome:` frontmatter
        2026-06-30-<slug>.md

THE FOLDER IS THE PHASE, and it is the single truth — there is no `phase:` field,
because two declared sources of one fact diverge and a folder cannot lie. The one
remaining transition is a `git mv` performed by `promote`, so `git log` still narrates
the close-out.

v3 FOLDED `backlog/` AND `ready/` INTO `plans/`. That split bought exactly one fact no
derivation reproduces — a human said go — and that fact is now `approved:` in
frontmatter. Everything else it implied is DERIVED: `ready` is a stage over the same ten
sections that used to be the `ready/` entry gate. Both legacy folders are still READ (so
a v2 workspace keeps working and `migrate` can fold it), never written; `canonical_phase`
maps them onto `plans` so every derivation sees one phase.

IDENTITY IS THE SLUG, not the path. Every command names the bare slug; this tool
resolves it to the one file whose name ends in `-<slug>.md`, wherever it sits. Two
matches is a REFUSAL (exit 2), never a guess.

THE DATE PREFIX is stamped once, at capture, and never rewritten — so the basename is
stable for the whole lifecycle, `git log --follow` reads as one history, and a plain
`ls` of any folder is chronological. A file listing IS the status view, and no file
listing reads frontmatter.

FOURTEEN CANONICAL SECTIONS, and the explicit-none rule is PHASE-SCOPED
-----------------------------------------------------------------------
`## Overview`, `## Problem`, `## Proposal`, `## Out of Scope`, `## Impact`,
`## Validation`, `## Design`, `## Alternatives Considered`, `## Open Decisions`,
`## Risks`, `## Handoff`, `## Tasks`, `## Discoveries`, `## Outcome`.

Headings are a PARSED contract — canonical English, exactly as written. A heading
outside the set is a stray. Each canonical heading is in one of three states:

  absent               its phase was never reached — legal before its own gate
  present, empty       MALFORMED: neither an answer nor a not-yet; refuses
  present, filled      OK (`- none — <reason>` counts as filled)

A heading is required — and required to carry an explicit none — only once ITS OWN
phase gate is reached. That scoping is what keeps a captured spec four lines long
instead of a fourteen-heading skeleton, and it is what keeps the derived stage honest:
applied absolutely, a fresh spec carrying fourteen `- none` sections would derive as
`designed` and pass every gate without anyone having thought anything.

DERIVED STAGES, never declared. Computed from heading presence and frontmatter, so
they regress automatically when a section empties. Declared state is forgotten on edit.

There is NO `.specs.json`, no attempt counter, and no delta format. A blocked task is
a visible `- [!] <id> <title> — blocked: <reason>` marker in `## Tasks`.

OUTPUT CONTRACT (uniform across every subcommand)
-------------------------------------------------
`--json` on every subcommand, and STRICT exit codes so the skill branches on data:
  0  ok
  1  findings (validate/doctor found something; a spec/task was not found)
  2  refusal  (an ambiguous slug; a gate not met; archiving `done` with open tasks)

WORKSPACE RESOLUTION
  --root PATH, else $SPECS_ROOT, else the nearest `specs/` directory walking up from
  cwd (or cwd itself if it is named `specs`). `new` creates `./specs` when none exists.

ASSETS
  Schema and template load from `<script>/../specs/` when present (so editing the
  shipped `assets/specs/schema.json` / `assets/specs/templates/spec.md` changes
  behavior in the plugin), and fall back to the constants embedded below — so an
  installed copy under `.claude/hooks/` with no adjacent assets still works.
  EDIT BOTH OR NEITHER.
"""
from __future__ import annotations

import argparse
import datetime
import difflib
import json
import os
import pathlib
import re
import sys
import unicodedata

VERSION = "4.9.1"  # kept in lockstep with the plugin VERSION file, plugin.json, and okf-validate.py

HERE = os.path.dirname(os.path.abspath(__file__))
ASSET_DIR = os.path.normpath(os.path.join(HERE, "..", "specs"))

PHASES = ("plans", "archive")

# v2 folders. READ so an unmigrated workspace keeps working and `migrate` can fold it;
# NEVER written — `new` and `promote` only ever target a folder in PHASES. Reading them
# is not politeness: `list` globs the phase folders, so a workspace this tool refused to
# see would read as EMPTY rather than as out of date, and a skill would conclude there is
# no work when there is.
LEGACY_PHASES = ("backlog", "ready")
PHASE_ALIASES = {"backlog": "plans", "ready": "plans"}
# scan order — a spec's canonical folder before the legacy ones it may still sit in
PHASE_DIRS = ("plans", "backlog", "ready", "archive")


def canonical_phase(folder: str) -> str:
    """The schema phase a folder maps to. `plans` for both v2 definition folders, so
    stage rules, gates and `next` branch on ONE phase and never on where the file
    happens to sit mid-migration."""
    return PHASE_ALIASES.get(folder, folder)


# THE BASENAME IS THE SLUG, and nothing else. It used to carry a `YYYY-MM-DD-` prefix, so the
# identity key and the capture date lived in one string — which meant a store with no filenames
# had to invent one to hold a date, and the `github` marker did exactly that. The date is a
# frontmatter field now (`date:`), in EVERY backend, because no external store carries an honest
# copy of it: an issue's `created_at` is when the issue was made, and a migration makes them all
# on the same day. The citable identity is the bare slug, which is already the only thing a human
# ever typed and the only thing `--spec` ever took.
#
# THE LOOKAHEAD IS LOAD-BEARING. `[a-z0-9]` matches digits, so without it the old
# `2026-07-25-<slug>.md` matches this pattern *whole* and the date is swallowed INTO the
# identity key — measured against this repository's 72 specs, every one of them came back
# slugged `2026-07-25-decide-agents-md-harness-default` with an empty date, and nothing
# reported a thing. Refusing the dated shape turns that silent corruption into the
# `sp-bad-filename` finding it always was. A slug may still begin with digits (`2026-roadmap`);
# only the full date prefix is rejected.
SPEC_FILE_RE = re.compile(r"^(?!\d{4}-\d{2}-\d{2}-)([a-z0-9]+(?:-[a-z0-9]+)*)\.md$")
# The pre-date-in-frontmatter basename, read ONLY by the migration folds — which exist precisely
# to recognise a layout this tool no longer writes. Nothing else may match on it: a file still
# named this way is a `sp-bad-filename` finding, not a second supported form.
LEGACY_DATED_FILE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})-([a-z0-9]+(?:-[a-z0-9]+)*)\.md$")
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

# `- [ ]` / `- [x]` / `- [!]` — the third is a BLOCKED task, visible and human-legible,
# which is what replaced v1's hidden five-attempt counter in `.specs.json`.
CHECKBOX_RE = re.compile(r"^(\s*)-\s\[( |x|X|!)\]\s+(.*)$")
CHECKBOX_LOOSE_RE = re.compile(r"^\s*-\s*\[.*?\]")   # looks like a checkbox (malformed detection)
TASK_ID_RE = re.compile(r"^(\d+(?:\.\d+)*)\b")
TASK_META_KEYS = ("files", "pattern", "verify", "constraint", "subject", "commit")
TASK_META_RE = re.compile(rf"^\s+({'|'.join(TASK_META_KEYS)})\s*:\s*(.+?)\s*$",
                          re.IGNORECASE)
# `constraint:` is INERT by design: the grammar admits it and `next` hands it through, but no
# command reads it. Its only consumer would be an executor sub-agent briefing itself, and the
# decision to dispatch one belongs to another spec — so the field lands first and the decision
# stays untouched. A field nobody reads costs one alternation and moves no turn.
#
# The anchor is written into a one-line grammar and read back, so the only hard requirement
# is that it holds text and stays on its line. `commit:` is both the legacy form of the same
# field — still READ from specs written before the anchor became the subject — AND, since
# `task --commit`, a form written again on purpose: a real git sha, upserted by the CLI once
# the commit that implements the task already exists. `subject:` stays the default `--check`
# writes; `commit:` is opt-in via the new flag. See `task --commit`'s help and `## Design`
# ("Decisão: o anchor task→commit é o sha") for why both anchors coexist for now.
SUBJECT_RE = re.compile(r"^[^\r\n]+$")
# A git object id, short or full — hex only. Loose on purpose (git accepts abbreviations down
# to a repo-dependent minimum well below 7), but tight enough to catch an obvious mistake like
# passing a commit MESSAGE where a sha was meant.
COMMIT_SHA_RE = re.compile(r"^[0-9a-fA-F]{7,40}$")
DEFAULT_META_INDENT = "      "
PARALLEL_RE = re.compile(r"^\[P\](?:\s|$)")
BLOCKED_REASON_RE = re.compile(r"—\s*blocked\s*:\s*(.+?)\s*$", re.IGNORECASE)

VERIFICATION_POLICIES = ("per-task", "per-section", "end-of-plan")
DEFAULT_VERIFICATION = "per-section"
OUTCOMES = ("done", "abandoned")
# The four strategies `/specs:conclude` offers. Two of them create no merge commit, so the
# record has no subject to name and carries an explicit none instead — a fact about the
# strategy, not a gap in the record.
MERGE_STRATEGIES = ("merge-commit", "squash", "rebase", "fast-forward")
MERGE_ANCHORLESS_STRATEGIES = ("rebase", "fast-forward")
RECORD_NONE_RE = re.compile(r"^none\b", re.IGNORECASE)

PLACEHOLDER_RE = re.compile(r"<[^>\n]+>")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
FENCE_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})")
BULLET_RE = re.compile(r"^\s*[-*+]\s")
SUBHEADING_RE = re.compile(r"^\s*(?:#{1,6}\s+|\*\*\S)")
STANDARD_PATH_RE = re.compile(r"docs/standards/[A-Za-z0-9._-]+(?:/[A-Za-z0-9._-]+)*\.md")

# --------------------------------------------------------------------------- #
# embedded assets (fallbacks when the sibling asset files are absent)
# Keep in lockstep with assets/specs/schema.json and assets/specs/templates/spec.md.
# --------------------------------------------------------------------------- #
DEFAULT_SCHEMA: dict = {
    "schema": "spec-lifecycle",
    "version": "3.0.0",
    "filename": {
        "pattern": r"^([a-z0-9]+(?:-[a-z0-9]+)*)\.md$",
        "groups": ["slug"],
        "example": "session-tokens.md",
    },
    "frontmatter": {
        "required": ["slug", "title", "date"],
        "optional": ["verification", "priority", "refined", "approved", "branch", "reviewed",
                     "merge", "outcome"],
        "verification": list(VERIFICATION_POLICIES),
        "outcome": list(OUTCOMES),
        "records": {
            "priority": {"fields": ["level", "criticality", "complexity", "date"],
                         "writtenBy": "triage", "writeOnce": False},
            "refined": {"fields": ["mode", "date"],
                        "writtenBy": "develop", "writeOnce": False},
            "approved": {"fields": ["date"],
                         "writtenBy": "develop, or execute inline", "writeOnce": True},
            "branch": {"fields": ["base", "work"],
                       "writtenBy": "execute", "writeOnce": True},
            "reviewed": {"fields": ["date"],
                         "writtenBy": "conclude", "writeOnce": False},
            "merge": {"fields": ["strategy", "subject"],
                      "strategies": list(MERGE_STRATEGIES),
                      "anchorless": list(MERGE_ANCHORLESS_STRATEGIES),
                      "writtenBy": "conclude", "writeOnce": True},
            "outcome": {"valuesFrom": "frontmatter.outcome",
                        "writtenBy": "conclude", "writeOnce": True},
        },
    },
    "sections": [
        {"heading": "Overview", "order": 1, "group": "orientation", "moment": "decision"},
        {"heading": "Problem", "order": 2, "group": "definition", "moment": "decision"},
        {"heading": "Proposal", "order": 3, "group": "definition", "moment": "build"},
        {"heading": "Out of Scope", "order": 4, "group": "definition", "moment": "build"},
        {"heading": "Impact", "order": 5, "group": "definition", "moment": "build", "parsed": True},
        {"heading": "Validation", "order": 6, "group": "definition", "moment": "close"},
        {"heading": "Design", "order": 7, "group": "definition", "moment": "build"},
        {"heading": "Alternatives Considered", "order": 8, "group": "definition", "moment": "decision"},
        {"heading": "Open Decisions", "order": 9, "group": "definition", "moment": "decision"},
        {"heading": "Risks", "order": 10, "group": "definition", "moment": "decision"},
        {"heading": "Handoff", "order": 11, "group": "execution", "moment": "build"},
        {"heading": "Tasks", "order": 12, "group": "execution", "moment": "build"},
        {"heading": "Discoveries", "order": 13, "group": "execution"},
        {"heading": "Outcome", "order": 14, "group": "archive", "moment": "close"},
    ],
    "impact": {
        "parsedSubheading": "Standards this spec will write into docs/standards/",
        "acceptedAliases": ["Standards this plan will write into docs/standards/"],
        "pathPrefix": "docs/standards/",
    },
    "phases": [
        {"id": "plans", "folder": "plans", "role": "active",
         "entryGate": ["Problem"], "warnWhenEmpty": []},
        {"id": "archive", "folder": "archive", "role": "closed",
         "entryGate": ["Outcome"], "warnWhenEmpty": []},
    ],
    "promote": {
        "sequence": ["plans", "archive"],
        "explicitNone": "- none — <reason>",
        "filledRule": "An explicit none counts as FILLED. A heading present with an empty body "
                      "is malformed and refuses. An absent heading before its own gate is legal.",
        "openTasks": {"done": "refuse", "abandoned": "allow", "forceFlag": "--force"},
    },
    "stages": {
        "resolution": "last-match-wins",
        "derived": [
            {"id": "captured", "phase": "plans", "when": {"filled": ["Problem"]}},
            {"id": "proposed", "phase": "plans", "when": {"filled": ["Proposal"]}},
            {"id": "designed", "phase": "plans", "when": {"filled": ["Design"]}},
            {"id": "refined", "phase": "plans", "when": {"frontmatter": "refined"}},
            {"id": "ready", "phase": "plans", "gate": True,
             "when": {"filled": ["Problem", "Proposal", "Out of Scope", "Impact",
                                 "Validation", "Design", "Alternatives Considered",
                                 "Open Decisions", "Risks", "Tasks"]},
             "warnWhenEmpty": ["Overview", "Handoff"]},
            {"id": "approved", "phase": "plans", "when": {"frontmatter": "approved"}},
            {"id": "executing", "phase": "plans",
             "when": {"anyOf": [{"taskState": ["x", "!"]}, {"filled": ["Handoff"]}]}},
        ],
    },
}

# The FULL template, embedded VERBATIM so an installed copy with no adjacent assets can
# still stamp a capture AND pull any heading's guidance for `section --write`. It is a
# byte-for-byte copy of assets/specs/templates/spec.md — `specs.py selftest` proves it, and
# EDIT BOTH OR NEITHER.
TEMPLATE_SPEC = """---
slug: <SLUG>
title: <TITLE>
date: <DATE>
verification: <VERIFICATION>
---

# <TITLE>

<!-- ONE spec is ONE file for its whole lifecycle. Phases enrich it; they never split it.

     `specs.py new` stamps the frontmatter and `## Problem` ALONE — a captured spec is four
     lines of body, not a fourteen-heading skeleton. Every other heading below is created on
     first write by `specs.py section <slug> "<Heading>" --write`, which inserts it in the
     canonical position with the guidance comment kept here.

     THE STAGE-SCOPED EXPLICIT-NONE RULE. A heading is required — and required to carry
     `- none — <reason>` when it has nothing in it — only once ITS OWN gate is reached:

       new (capture)        `## Problem`
       ready (derived)      the nine definition sections (`## Problem` .. `## Risks`)
                            AND `## Tasks`
       ready (warn only)    `## Overview` non-empty, `## Handoff` non-empty
       promote -> archive/  `## Outcome`

     `ready` is a DERIVED STAGE, not a folder: a spec lives in `plans/` for its whole active
     life, and filling those ten sections is what makes it ready. Nothing refuses on that
     gate — it is a floor `execute` reports against, and the human's go-ahead is the
     `approved:` frontmatter record, asked for inline.

     Before its gate, a heading's absence is NOT an omission — it is a not-yet. After its
     gate, three rules decide whether a section counts as filled:

       1. `- none — <reason>` counts as filled. An omission and a null are different facts.
       2. A heading present with an EMPTY body is malformed and refuses. It is neither an
          answer nor a not-yet.
       3. An absent heading before its gate is legal.

     Headings are a PARSED contract — canonical English, exactly as written here. Body prose
     follows the repo's language. A heading outside this set is a stray and validate flags it.
     *(`standards/agents/communication.md` owns that language rule for a repo whose bundle has
     one. This template states it self-contained rather than citing it: `/specs:align` is native
     and installs here into repos that never adopted the bundle, where that path resolves to
     nothing.)*

     MOMENT. Each section belongs to one of three moments on the spec's timeline: `decision`
     (the human, deciding whether to build), `build` (the executor, in step 4 of
     `/specs:execute`), `close` (`/specs:conclude`, at archive time). `## Discoveries` belongs
     to none of them — captured indiscriminately while building, resolved later by
     `/specs:develop`'s triage sweep on its own schedule. An orchestrator sends an executor
     exactly the `build` set; that is what lets one file serve every moment without bloating
     agent context. -->

## Overview

<!-- MOMENT: decision. Warned on when empty once the ready gate is met.

     Connective tissue for a reader who is not holding the whole spec in their head: how the
     other sections relate to one another, not a compressed restatement of each. Plain
     language, assuming no prior context — avoid the jargon the spec itself introduces.

     Written LAST, after every other section has settled, because it can only be correct once
     they have — even though it lives here, first, because that is where a reader starts. -->

## Problem

<!-- MOMENT: decision. Gate: new (capture).

     The problem or opportunity this spec answers, and why now. This is the only section a
     freshly captured spec carries — write it even if it is two sentences. -->

## Proposal

<!-- MOMENT: build. Gate: ready (derived).

     The change at a high level, in bullet points. What will be true afterwards that is not
     true now. -->

## Out of Scope

<!-- MOMENT: build. Gate: ready (derived).

     What this spec deliberately does NOT do, and why it was ruled out.

     Empty is written `- none — <reason>`. "We drew the boundary and nothing fell outside it"
     and "nobody ever drew the boundary" are different answers, and an absent section cannot
     tell them apart. -->

## Impact

<!-- MOMENT: build + PARSED. Gate: ready (derived).

     Declared scope for human review. The `### Standards this spec will write into
     docs/standards/` sub-heading below is PARSED by `specs.py validate`: every
     `docs/standards/**.md` path bulleted under it must be named by a `## Tasks` item, or
     validate emits `sp-impact-uncovered` (warn). Keep that heading text verbatim — it is the
     anchor.

     Example of a parsed bullet:
       - `docs/standards/naming/command-surface.md` — the bijection rule for wrappers

     The sibling sub-headings are prose for the reader and are deliberately NOT parsed: they
     name paths the spec never promised to write. A spec with no such sub-heading declares
     nothing and is never flagged — the check is opt-in by writing the heading. -->

### Standards this spec will write into docs/standards/

- `<docs/standards/subject/concept.md>` — <the rule it states>

### Standards at `authority: background` this spec may resolve

- <path, or `none`>

### Product code this spec expects to touch

- `<path>` — <why>

## Validation

<!-- MOMENT: close (plus the agent's `verify:` fallback, resolved lazily). Gate: ready (derived).

     How anyone confirms this spec actually worked: the commands to run and the output they
     must produce, the fixtures to check, the invariants that must still hold afterwards.

     This section is LOAD-BEARING: a `## Tasks` item with no `verify:` line falls back to it.

     Empty is written `- none — <reason>`, which is a claim that the spec is unverifiable by
     construction. Make it on purpose or fill it in. -->

## Design

<!-- MOMENT: build. Gate: ready (derived).

     The choices made and their rationale, plus the background and binding contracts this
     design must not contradict. For each decision: what was chosen, why, and what was
     weighed against it.

     Empty is written `- none — <reason>` (e.g. "mechanical change, no design surface"). -->

## Alternatives Considered

<!-- MOMENT: decision. Gate: ready (derived).

     Whole-shape alternatives rejected at the spec level, each with the reason it lost.
     Per-decision alternatives can stay inside `## Design`; this section is for the ones that
     would have changed the spec's shape.

     Empty is written `- none — <reason>` (e.g. "only one viable approach"). -->

## Open Decisions

<!-- MOMENT: decision. Gate: ready (derived).

     What is deliberately still undecided, and how each will be decided — the evidence or the
     moment that settles it, not "TBD".

     Empty is written `- none — <reason>`. -->

## Risks

<!-- MOMENT: decision. Gate: ready (derived).

     What could go wrong, and the mitigation for each. A risk taken knowingly is written
     `ACCEPTED — <why>`; a silent failure mode is the shape to hunt for.

     Empty is written `- none — <reason>`. -->

## Handoff

<!-- MOMENT: build. Warned on when empty once the ready gate is met.

     The context an executor needs and cannot derive: the state of play, the conventions in
     force, what was already tried. Small by construction — it is sent with EVERY task.

     Refresh is bound to EVENTS, not judgment: the orchestrator rewrites this after each
     committed task. Staleness is this section's failure mode. -->

## Tasks

<!-- MOMENT: build. Gate: ready (derived).

     Checkboxes `- [ ] <id> <text>` grouped under `### N. <Section>` headings.
     `specs.py task --spec <slug> --check <id>` flips one mechanically — NEVER hand-edit the
     `[ ]` / `[x]` character. `--subject <line>` records the commit that implements it.

     A checkbox MAY carry indented metadata lines directly beneath it:

       - [ ] 3.2 Add rate limiting to the auth middleware
             files: src/middleware/auth.ts, src/config/limits.ts (new)
             pattern: src/middleware/cors.ts
             verify: pnpm test middleware/
             subject: plan/<slug>: 3.2 Add rate limiting to the auth middleware

     files:    the paths this task may touch. Declaring them is what PERMITS the task to be
               handed to an executor sub-agent, and what makes a `[P]` marker checkable.
     pattern:  an existing file to imitate — the cheapest context an executor can be given.
     verify:   the command that proves the task done. WHEN it runs is the `verification`
               frontmatter policy, not this section's business. With no `verify:` line the
               task falls back to `## Validation`.
     subject:  written by `task --check --subject`, never by hand — the SUBJECT of the commit
               that implements this task, resolved by `git log --grep --fixed-strings`. It is
               known BEFORE the commit, so the box is ticked INTO the task's own commit
               instead of a bookkeeping commit that follows it. A spec built before this
               change carries `commit: <sha>`; both forms are read, neither is backfilled.

     `[P]` right after the id marks a task parallel-eligible:

       - [ ] 3.3 [P] Add the rate-limit config loader

     Set HERE, at definition time, and NEVER inferred while building. Honoured only when the
     marked tasks' `files:` sets are provably disjoint and none writes into `docs/` —
     `specs.py parallel` checks the disjunction mechanically rather than judging it in prose.
     Serial execution is the default and needs no marker.

     A BLOCKED task is a visible marker, not a hidden counter:

       - [!] 2.3 Implement the gate check — blocked: the vendor SDK has no hook for it

     Written by the orchestrator when it decides to stop retrying; `next` skips it. There is
     no attempt budget — an honest written reason serves better than a counter nobody sees. -->

### 1. <Section>

- [ ] 1.1 <first task>
- [ ] 1.2 <next task>

## Discoveries

<!-- MOMENT: none — triage, resolved by `/specs:develop`'s discoveries bank whenever it runs,
     not tied to one of the three. No gate — appended during execution.

     One line per discovery, appended by `specs.py discover <slug> "<text>"` while building.
     Captured INDISCRIMINATELY: whether one is worth acting on is triage's judgment, not the
     executor's.

     The triage sweep resolves each entry IN PLACE, so provenance is never lost:

       - the rate limiter double-counts retries → promoted: fix-retry-accounting
       - the config loader is slow on cold start → dismissed: acceptable, runs once -->

## Outcome

<!-- MOMENT: close. Gate: promote -> archive/.

     What actually happened, written at archive time: what shipped, what was left out, what
     the next reader needs to know. `outcome: done | abandoned` is stamped into the
     frontmatter by `specs.py promote --to archive`; this section is the prose behind it.

     For an abandoned spec, the reason it will not be built is the whole content. -->
"""


# --------------------------------------------------------------------------- #
# minimal frontmatter parser (deliberately duplicated from okf-validate.py so
# each script stays self-contained — ~40 lines, no shared module)
# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #
# The YAML comment rule — one rule, three copies
#
# `docs/standards/code/frontmatter-parsing.md` owns the rule, the canonical case
# list and the lockstep obligation. `skills.py` and `okf-validate.py` carry the same
# functions; each installs standalone into a target's `.claude/hooks/`, so none may
# import the others. EDIT ALL THREE, OR NONE — `CANONICAL_CASES` below is what makes
# a drifted parser fail its OWN selftest on a row the other two still pass.
# --------------------------------------------------------------------------- #
def _frontmatter_body(text: str) -> list[str] | None:
    """The lines between the leading `---` fences; `None` when there is no closed
    block."""
    if not text.startswith("---"):
        return None
    lines = text.splitlines()
    if lines[0].strip() != "---":
        return None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return lines[1:i]
    return None


def _indented_run(body: list[str], start: int) -> tuple[list[str], int]:
    """The blank-or-indented lines beginning at `start` with trailing blanks dropped,
    and the index of the first line that is neither — i.e. everything belonging to
    the value above, and where the next top-level key begins."""
    run: list[str] = []
    j = start
    while j < len(body) and (not body[j].strip() or body[j][:1] in (" ", "\t")):
        run.append(body[j])
        j += 1
    while run and not run[-1].strip():
        run.pop()
    return run, j


def _quote_end(val: str) -> int | None:
    """Index just past the closing quote of a quoted scalar; `0` when the value is
    not quoted, `None` when the quote never closes.

    A quote opens a scalar only in the first position — mid-value it is an ordinary
    character, which is why `at the first '#'` is a plain scalar and its `#` is not
    inside quotes."""
    if not val or val[0] not in ("'", '"'):
        return 0
    quote, i = val[0], 1
    while i < len(val):
        if quote == '"' and val[i] == "\\":
            i += 2
            continue
        if val[i] == quote:
            if quote == "'" and val[i + 1:i + 2] == "'":   # YAML doubles a literal '
                i += 2
                continue
            return i + 1
        i += 1
    return None


def _split_comment(val: str) -> tuple[str, str]:
    """Split a scalar into (value, comment).

    A `#` opens a comment only when it is the first character of the value or is
    preceded by whitespace, and never inside a quoted scalar. The `val.split("#")[0]`
    this replaced honoured none of the three, so it cut every value at its first `#`
    — including this workspace's own spec titles, in every `status --json` call.

    An unterminated quote strips nothing: the scalar's extent is unknowable, so the
    value is kept verbatim and `frontmatter_anomalies` reports it rather than the
    parser guessing a boundary."""
    start = _quote_end(val)
    if start is None:
        return val, ""
    for i in range(start, len(val)):
        if val[i] == "#" and (i == 0 or val[i - 1] in " \t"):
            return val[:i].rstrip(), val[i:]
    return val, ""


def parse_frontmatter(text: str) -> dict:
    """Top-level `key: value` pairs of a leading `---` block. List values are
    returned as Python lists for inline `[a, b]` and block `- item` forms; scalars
    as strings with surrounding quotes stripped. Empty dict when there is no block."""
    body = _frontmatter_body(text)
    if body is None:
        return {}
    fm: dict = {}
    j = 0
    while j < len(body):
        raw = body[j]
        if not raw.strip() or raw.lstrip().startswith("#") or raw[:1] in (" ", "\t"):
            j += 1
            continue
        if ":" not in raw:
            j += 1
            continue
        key, _, val = raw.partition(":")
        key = key.strip()
        val = _split_comment(val.strip())[0]
        if val == "":
            items = []
            k = j + 1
            while k < len(body) and body[k][:1] in (" ", "\t") and body[k].lstrip().startswith("- "):
                items.append(body[k].lstrip()[2:].strip().strip("'\""))
                k += 1
            if items:
                fm[key] = items
                j = k
                continue
            # A block mapping. Flow (`{a: b, c: d}`) splits on commas, so a record value
            # that contains one — or is long enough to wrap — can only be written this way.
            # Indent decides, exactly as YAML does it: a line deeper than the record's keys
            # continues the value above it rather than starting a new key, which is what
            # lets an explicit-none reason run past one line.
            rec, last, base_indent = {}, None, None
            k = j + 1
            while k < len(body) and body[k][:1] in (" ", "\t") and body[k].strip():
                indent = len(body[k]) - len(body[k].lstrip())
                cur = body[k].strip()
                if base_indent is None:
                    base_indent = indent
                if indent > base_indent and last is not None:
                    rec[last] = f"{rec[last]} {cur}".strip()
                elif indent == base_indent and ":" in cur:
                    k2, _, v2 = cur.partition(":")
                    last = k2.strip()
                    rec[last] = v2.strip().strip("'\"")
                else:
                    break
                k += 1
            if rec:
                fm[key] = rec
                j = k
                continue
            fm[key] = ""
            j += 1
            continue
        if val.startswith("[") and val.endswith("]"):
            inner = val[1:-1].strip()
            fm[key] = [x.strip().strip("'\"") for x in inner.split(",") if x.strip()] if inner else []
        elif val.startswith("{") and val.endswith("}"):
            inner = val[1:-1].strip()
            rec: dict = {}
            for part in inner.split(","):
                if ":" in part:
                    k2, _, v2 = part.partition(":")
                    rec[k2.strip()] = v2.strip().strip("'\"")
            fm[key] = rec
        else:
            if len(val) >= 2 and val[0] == val[-1] and val[0] in ("'", '"'):
                val = val[1:-1]
            fm[key] = val
        j += 1
    return fm


# The block-scalar indicator. `skills.py` compiles the same pattern to READ these;
# this parser does not read them, so it uses the pattern to NAME them instead.
BLOCK_SCALAR_RE = re.compile(r"^([|>])(?:[+-]?)(?:\d*)\s*$")


def frontmatter_anomalies(text: str) -> list[dict]:
    """What the frontmatter parse could not represent faithfully.

    A SIDECAR: `parse_frontmatter` keeps returning a bare dict, so none of its call
    sites change — `status`, `next` and `triage` never have to decide mid-cycle what
    an un-understood frontmatter means, which would be a behaviour change in commands
    that today refuse nothing.

    Every entry is a suspicion the tool cannot resolve, never a proven violation: a
    stripped comment and lost prose are byte-identical, and nothing here guarantees
    Claude Code's own loader resolves a duplicate key the way this one does. Callers
    surface them at WARN — see `docs/standards/quality/parse-honesty.md`."""
    body = _frontmatter_body(text)
    if body is None:
        return []
    fm = parse_frontmatter(text)
    out: list[dict] = []
    seen: set[str] = set()
    j = 0
    while j < len(body):
        raw = body[j]
        if (not raw.strip() or raw.lstrip().startswith("#")
                or raw[:1] in (" ", "\t") or ":" not in raw):
            j += 1
            continue
        key, _, val = raw.partition(":")
        key, val = key.strip(), val.strip()
        run, k = _indented_run(body, j + 1)

        if key in seen:
            out.append(_anomaly(key, "duplicate-key",
                                f"`{key}` is set more than once and the last one silently wins; "
                                "nothing guarantees another parser resolves it the same way"))
        seen.add(key)

        value, comment = _split_comment(val)
        if comment:
            out.append(_anomaly(key, "comment-stripped",
                                f"`{comment}` was read as a comment and removed from `{key}` — "
                                "a stripped comment and lost prose are byte-identical"))
        elif _quote_end(val) is None:
            out.append(_anomaly(key, "unterminated-quote",
                                f"`{key}` opens a quote that never closes, so the scalar's "
                                "extent is unknowable; nothing was stripped"))
        # A block scalar is an indented form this parser does not read, and the one it
        # fails at WITHOUT reading empty: `parse_frontmatter` keeps the bare `|`/`>`
        # indicator as the value, which is a guess rather than a read, so the truthiness
        # test below would never see it. `skills.py` DOES read block scalars and stays
        # silent — the per-tool carve-out the standard allows (§The canonical case list,
        # "a tool may read more than the table requires"), not a disagreement on a row.
        if BLOCK_SCALAR_RE.match(value) and run:
            out.append(_anomaly(key, "indented-continuation",
                                f"`{key}` opens a block scalar this parser does not read — the "
                                f"`{value}` indicator was kept as the value and the lines beneath "
                                "it were dropped"))
        # The parse result is the test, not a re-derivation of it: a block list or a
        # block record comes back truthy because this parser genuinely reads both, so
        # only a form it read as nothing is reported.
        elif value == "" and run and not fm.get(key):
            out.append(_anomaly(key, "indented-continuation",
                                f"`{key}` has no inline value and the lines beneath it are in "
                                "no form this parser reads — it was read as empty"))
        j = k
    return out


def _anomaly(key: str, kind: str, detail: str) -> dict:
    return {"key": key, "kind": kind, "detail": detail}


# The canonical case list from `docs/standards/code/frontmatter-parsing.md`. It is
# duplicated VERBATIM in skills.py and okf-validate.py and is the lockstep unit for
# all three: adding a row means adding it in three places, and a parser that drifts
# fails here on a row the other two still pass.
#   (label, frontmatter body, expected `title`, expected anomaly kinds)
CANONICAL_CASES = [
    ("plain",                 "title: a plain value",              "a plain value",              ()),
    ("comment-after-space",   "title: a value # a note",           "a value",                    ("comment-stripped",)),
    ("hash-after-quote-char", "title: truncates at the first '#'", "truncates at the first '#'", ()),
    ("hash-in-backticks",     "title: the `#` character",          "the `#` character",          ()),
    ("hash-no-space",         "title: C#",                         "C#",                         ()),
    ("double-quoted-hash",    'title: "quoted # inside"',          "quoted # inside",            ()),
    ("single-quoted-hash",    "title: 'single # inside'",          "single # inside",            ()),
    ("quoted-then-comment",   'title: "quoted" # a note',          "quoted",                     ("comment-stripped",)),
    ("comment-only",          "title: # a note",                   "",                           ("comment-stripped",)),
    ("unterminated-quote",    'title: "unterminated',              '"unterminated',              ("unterminated-quote",)),
    ("duplicate-key",         "title: first\ntitle: second",       "second",                     ("duplicate-key",)),
    ("indented-continuation", "title:\n  a wrapped prose line",    "",                           ("indented-continuation",)),
]


def canonical_case_failures() -> list[str]:
    """Run `CANONICAL_CASES` against this tool's own parser and sidecar."""
    out = []
    for label, fm, want_value, want_kinds in CANONICAL_CASES:
        text = f"---\n{fm}\n---\n\nbody\n"
        got_value = parse_frontmatter(text).get("title", "<missing>")
        got_kinds = tuple(sorted(a["kind"] for a in frontmatter_anomalies(text)))
        if got_value != want_value:
            out.append(f"{label}: title expected {want_value!r}, got {got_value!r}")
        if got_kinds != tuple(sorted(want_kinds)):
            out.append(f"{label}: anomalies expected {sorted(want_kinds)}, got {list(got_kinds)}")
    return out


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def slugify(name: str) -> str:
    """A kebab identity key, in the language the repo actually writes in.

    UNICODE IS NORMALISED AND STRIPPED FIRST, and that is the whole of it. Without it the
    `[^a-z0-9]+` below treats every accented letter as a SEPARATOR, so `criação` reduced to
    `cria-o` and `avaliar-o-fluxo-de-criacao-de-specs` came out
    `avaliar-o-fluxo-de-cria-o-de-specs` — an identity key that is neither readable nor
    guessable, in a repository whose declared harness language is pt-BR. NFD splits a letter
    from its combining marks and the marks are then dropped, so `ç` becomes `c` and `ã`
    becomes `a`: exactly the transliteration a human types when the accent is unavailable.

    A character that does not decompose (`ß`, `ø`) still falls to the separator rule. That is
    a real limit and it is left alone rather than papered over with a lookup table nobody
    maintains — the languages this front is used in are covered, and a slug that loses a
    letter is visible the moment it is printed."""
    folded = unicodedata.normalize("NFD", name.strip().lower())
    folded = "".join(c for c in folded if not unicodedata.combining(c))
    s = re.sub(r"[^a-z0-9]+", "-", folded).strip("-")
    return re.sub(r"-{2,}", "-", s)


# What `slugify` must answer, asserted by `selftest`. The accented rows are the point: they
# are what the identity key of every spec captured in pt-BR runs through.
SLUG_CASES = (
    ("Avaliar o fluxo de criação de specs", "avaliar-o-fluxo-de-criacao-de-specs"),
    ("Ação e Manutenção", "acao-e-manutencao"),
    ("Sessão — tokens", "sessao-tokens"),
    ("session tokens", "session-tokens"),
    ("  Trim  --  Me  ", "trim-me"),
    ("JÁ-EM-CAIXA-ALTA", "ja-em-caixa-alta"),
)


def slug_case_failures() -> list[str]:
    return [f"slugify({given!r}) = {slugify(given)!r}, expected {want!r}"
            for given, want in SLUG_CASES if slugify(given) != want]


def titleize(slug: str) -> str:
    return " ".join(w.capitalize() for w in slug.replace("_", "-").split("-") if w)


def today() -> str:
    return datetime.date.today().isoformat()


def read_text(path: str) -> str | None:
    try:
        return pathlib.Path(path).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None


def write_text(path: str, text: str) -> None:
    """Replace a file's whole content ATOMICALLY — a reader never sees half a spec.

    Write-then-rename rather than `Path.write_text`, which truncates first: a reader landing in
    the window between the truncate and the write gets an empty or torn document. That window
    is why this is here rather than left alone — `SpecsLock` serialises WRITERS ONLY, and the
    argument for letting readers run unlocked is exactly that a write is never observable
    half-done. `os.replace` is atomic on POSIX and on Windows.

    The temp file is created in the SAME directory, so the rename never crosses a filesystem,
    and carries the pid, so two writers cannot collide on the temp name even where no lock
    covers them (a workspace still in the code tree has no worktree and takes no lock)."""
    p = pathlib.Path(path)
    tmp = p.with_name(f".{p.name}.tmp-{os.getpid()}")
    try:
        tmp.write_text(text, encoding="utf-8")
        os.replace(tmp, p)
    finally:
        try:
            tmp.unlink()      # a no-op after a successful replace; cleanup after a failure
        except OSError:
            pass


def load_schema() -> dict:
    p = os.path.join(ASSET_DIR, "schema.json")
    txt = read_text(p)
    if txt:
        try:
            obj = json.loads(txt)
            if isinstance(obj, dict) and obj.get("sections"):
                return obj
        except json.JSONDecodeError:
            pass
    return DEFAULT_SCHEMA


def load_template() -> str:
    """The FULL fourteen-section authoring reference — frontmatter, the contract preamble,
    and every heading with its guidance comment.

    Two consumers read it and they need different slices: `new` stamps only the capture
    form (below), while `section --write` pulls one heading's guidance when creating it.
    Keeping one source for both is what stops the guidance drifting from the contract."""
    txt = read_text(os.path.join(ASSET_DIR, "templates", "spec.md"))
    return txt if txt is not None else TEMPLATE_SPEC


def capture_form(template_text: str | None = None, schema: dict | None = None) -> str:
    """What `new` stamps: the frontmatter and the contract preamble, then the heading blocks
    the `plans` entry gate names — `## Problem` with its guidance, and nothing else.

    Sliced by GATE MEMBERSHIP, never by position. The obvious implementation — everything up
    to the SECOND `## ` heading — was right only while `## Problem` happened to be the first
    heading in the template, and it broke the moment `## Overview` was added ahead of it:
    capture then stamped an empty `## Overview` and dropped `## Problem`, so every spec `new`
    created was born failing its own gate. What makes a heading part of capture is the gate,
    not where it sits in the file, so read the gate.

    A captured spec is four lines of body, not a fourteen-heading skeleton. That is not
    cosmetic: the explicit-none rule makes `- none — <reason>` count as filled, so a spec
    born with fourteen headings would derive as `designed` and pass every promote gate
    without anyone having thought anything."""
    text = template_text if template_text is not None else load_template()
    gate = phase_spec("plans", schema).get("entryGate", [])
    if not gate:
        return text
    lines = text.splitlines(keepends=True)
    preamble = None
    for i, line in enumerate(lines):
        m = HEADING_RE.match(line)
        if m and len(m.group(1)) == 2:
            preamble = "".join(lines[:i]).rstrip()
            break
    if preamble is None:
        return text
    blocks = [section_guidance(h, text).rstrip() for h in gate]
    return preamble + "\n\n" + "\n\n".join(blocks) + "\n"


def section_guidance(heading: str, template_text: str | None = None) -> str:
    """One heading's block from the template — the heading line plus its guidance comment,
    used by `section --write` when it creates a heading that does not exist yet."""
    text = template_text if template_text is not None else load_template()
    lines = text.splitlines()
    want = heading.strip().lower()
    start = None
    for i, line in enumerate(lines):
        m = HEADING_RE.match(line)
        if m and len(m.group(1)) == 2:
            if start is not None:
                return "\n".join(lines[start:i]).rstrip() + "\n"
            if m.group(2).strip().lower() == want:
                start = i
    if start is not None:
        return "\n".join(lines[start:]).rstrip() + "\n"
    return f"## {heading}\n"


def canonical_headings(schema: dict | None = None) -> list[str]:
    s = schema or load_schema()
    return [x["heading"] for x in sorted(s["sections"], key=lambda d: d.get("order", 0))]


def headings_for_moment(moment: str, schema: dict | None = None) -> list[str]:
    """The canonical headings declared `moment: <moment>`, in canonical order.

    `## Discoveries` declares no `moment` — resolved on its own schedule by
    `/specs:develop`'s triage sweep, not one of `decision` / `build` / `close` — so it never
    matches here, by construction rather than by exclusion list."""
    s = schema or load_schema()
    return [x["heading"] for x in sorted(s["sections"], key=lambda d: d.get("order", 0))
            if x.get("moment") == moment]


def phase_spec(phase: str, schema: dict | None = None) -> dict:
    s = schema or load_schema()
    for p in s.get("phases", []):
        if p.get("id") == phase:
            return p
    return {"id": phase, "folder": phase, "entryGate": [], "warnWhenEmpty": []}


def strip_comments(text: str) -> str:
    return re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)


def mask_comments(text: str) -> str:
    """Blank out HTML-comment spans, preserving every newline and column so line numbers
    and offsets still line up with the original.

    The template documents the task format with example checkboxes inside its comment
    guidance. Without this, those examples parse as real tasks and a freshly captured spec
    reports phantom progress — and `task --check` needs the surviving `lineno` to point at
    the true line, which stripping (rather than masking) would break."""
    return re.sub(r"<!--.*?-->",
                  lambda m: re.sub(r"[^\n]", " ", m.group(0)),
                  text, flags=re.DOTALL)


def body_after_frontmatter(text: str) -> str:
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) == 3:
            return parts[2]
    return text


def has_real_content(text: str) -> bool:
    """True when a block carries authored prose beyond the shipped template (headings,
    HTML comments, and `<placeholder>` lines don't count).

    `- none — <reason>` DOES count: an explicit null is an answer, and the whole
    explicit-none rule depends on this returning True for it."""
    body = strip_comments(text)
    for line in body.splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        residue = PLACEHOLDER_RE.sub("", s)
        residue = re.sub(r"^[-*+]\s*(\[.?\])?\s*", "", residue)  # drop list/checkbox markers
        residue = re.sub(r"^\d+(?:\.\d+)*\s*", "", residue)      # drop a leading task id
        if re.search(r"[A-Za-z0-9]", residue):
            return True
    return False


# --------------------------------------------------------------------------- #
# workspace resolution and spec discovery
# --------------------------------------------------------------------------- #
def find_specs_root(root_arg: str | None) -> str:
    if root_arg:
        return os.path.abspath(root_arg)
    env = os.environ.get("SPECS_ROOT")
    if env:
        return os.path.abspath(env)
    cur = os.path.abspath(os.getcwd())
    if os.path.basename(cur) == "specs":
        return cur
    d = cur
    while True:
        cand = os.path.join(d, "specs")
        if os.path.isdir(cand):
            return cand
        parent = os.path.dirname(d)
        if parent == d:
            break
        d = parent
    return os.path.join(cur, "specs")   # default (created by `new`)


CONFIG_FILE = os.path.join(".claude", "quenching.json")
LEGACY_CONFIG_FILE = "config.json"
CONFIG_KEYS = ("backend", "specsBranch", "worktreeSetup", "azureStates")
BACKENDS = ("files", "github", "azure-boards")
DEFAULT_BACKEND = "files"
DEFAULT_SPECS_BRANCH = "specs"
# `azureStates` has NO default, and that is the decision rather than an omission. GitHub's
# open/closed is universal, so `github` needs no such key; an Azure Boards state is defined
# by the project's PROCESS — Basic says To Do/Doing/Done, Agile says New/Active/Resolved/
# Closed, Scrum says New/…/Done/Removed, and a customised process says whatever it likes.
# Guessing would not fail loudly: it would read every archived spec as active in half the
# projects it ran against.

# The backends that ship without ever having run against a real target. `## Out of Scope`
# accepts that for `azure-boards`, and the selftest's completeness and refusal checks are
# what it has instead. Named HERE rather than inside the backend so that retiring the
# caveat is one edit: a real Azure DevOps project exercises it, this tuple loses a name,
# and the doctor finding and the write-time line go quiet together.
UNPROVED_BACKENDS = ("azure-boards",)

_UNPROVED_ANNOUNCED: set[str] = set()


def announce_unproved(name: str) -> None:
    """One line on stderr, once per process, before an unproved backend's first WRITE.

    THE DECISION IS "WARN, BUT NOT ON EVERY OPERATION". A line per operation is honest and
    becomes a per-call tax on the agent reading this CLI, paid forever for a fact that never
    changes between calls. Silence is not defensible either, because the unproved paths do
    not all fail the same way: a wrong `AZ_SPEC_TYPE` fails LOUDLY — `az` answers with an
    API error and the transport turns it into an exit-2 refusal — but a relation whose child
    ids do not extract fails QUIETLY, returning a spec with no tasks, and a write that fails
    halfway leaves work items behind on somebody's real board. So the line lands on the
    writes, where an unproved path can cost something that does not announce itself, and
    reads — the overwhelming majority of a build loop's calls — stay silent. The permanent,
    zero-noise half of the same answer is `sp-backend-unproved` in `doctor`.

    stderr and never stdout: every caller branches on the `--json` payload, and a warning
    printed into it would break the parse it is trying to inform."""
    if name not in UNPROVED_BACKENDS or name in _UNPROVED_ANNOUNCED:
        return
    _UNPROVED_ANNOUNCED.add(name)
    print(f"warning: backend '{name}' ships without an end-to-end run against a real "
          f"target — its writes have never seen a live response, so this one may fail, or "
          f"half-succeed and leave items behind. `specs.py selftest` proves its five "
          f"primitives and its refusals; nothing proves this call.", file=sys.stderr)


def find_repo_root(specs_root: str) -> str:
    """The target repo's root — where `.claude/` lives.

    Git's own top level first, because it is the answer that survives being invoked from a
    subdirectory. Falling back to the specs workspace's parent, which is the repo root by
    construction: `specs/` sits beside `.claude/`, never below it."""
    top = _git(specs_root, "rev-parse", "--show-toplevel").strip()
    return top or os.path.dirname(os.path.abspath(specs_root))


def load_config(root: str) -> dict:
    """`.claude/quenching.json` — the plugin's declared parameters, read as data and never
    as a refusal.

    THE FILE MOVED, AND THE MOVE IS THE POINT. It used to be `specs/config.json`, at the
    root of the specs workspace, holding one key. Two things broke that home: a repo whose
    backend is external may have no `specs/` folder at all, so a config that lives inside
    the workspace cannot say where the workspace is; and the config stopped being the specs
    front's alone. `.claude/` is the one directory every front already shares.

    A leftover `specs/config.json` comes back as `legacyPath` rather than being read. Merging
    the two silently would leave a repo with a config that half-works and no way to tell which
    file won; `doctor` names it instead.

    Absent file, absent key, malformed JSON: all yield the defaults, because a repo that
    declares nothing is the normal case and must cost nothing. Every way the file can be
    *wrong* — an unrecognised key, an unrecognised backend, unparseable JSON — comes back as
    a field rather than as a finding, so `doctor` decides what each is worth and every other
    caller is spared the question.

    Whether `worktreeSetup` actually resolves is deliberately NOT answered here: it is judged
    relative to the freshly created worktree, whose path this tool never learns.
    `/specs:isolate` runs it there and reports the exit code."""
    repo = find_repo_root(root)
    path = os.path.join(repo, CONFIG_FILE)
    legacy = os.path.join(root, LEGACY_CONFIG_FILE)
    out = {"path": path, "present": os.path.isfile(path), "unparseable": None,
           "unknownKeys": [], "backend": DEFAULT_BACKEND, "unknownBackend": None,
           "specsBranch": DEFAULT_SPECS_BRANCH, "worktreeSetup": None,
           "azureStates": None,
           "legacyPath": legacy if os.path.isfile(legacy) else None}
    if not out["present"]:
        return out
    try:
        obj = json.loads(read_text(path) or "")
    except json.JSONDecodeError as e:
        out["unparseable"] = str(e)
        return out
    if not isinstance(obj, dict):
        out["unparseable"] = f"top level is {type(obj).__name__}, not an object"
        return out
    out["unknownKeys"] = sorted(k for k in obj if k not in CONFIG_KEYS)

    backend = obj.get("backend")
    if isinstance(backend, str) and backend.strip():
        if backend.strip() in BACKENDS:
            out["backend"] = backend.strip()
        else:
            # The declared value is kept, not discarded: `doctor` must be able to quote back
            # what was typed. The effective backend stays the default, so a typo degrades to
            # the local one rather than to no backend at all.
            out["unknownBackend"] = backend.strip()

    branch = obj.get("specsBranch")
    if isinstance(branch, str) and branch.strip():
        out["specsBranch"] = branch.strip()

    val = obj.get("worktreeSetup")
    if isinstance(val, str) and val.strip():
        out["worktreeSetup"] = val.strip()

    # Both phases or neither. A half-declared mapping is worse than none: it would archive a
    # spec into a state the project has and then fail to recognise it on the way back.
    states = obj.get("azureStates")
    if isinstance(states, dict):
        named = {p: str(states.get(p, "")).strip() for p in PHASES}
        if all(named.values()):
            out["azureStates"] = named
    return out


def spec_files(root: str, phase: str | None = None) -> list[dict]:
    """Every conformant spec file across the phase folders, oldest first within each.

    Each row carries BOTH `folder` (where the file actually is, so every message names a
    real path) and `phase` (what it means, so a v2 file in `backlog/` derives exactly like
    a v3 file in `plans/`). Passing `phase` filters on the canonical phase, so
    `phase="plans"` sweeps up the legacy folders too.

    A file whose name does not match `<slug>.md` is NOT returned — it is a finding for
    `validate`/`doctor` to report, not something to silently half-support.

    The rows are in BASENAME order, which is slug order. It used to be date order, for free,
    because the date led the basename; ordering by date now would mean opening every file to
    read its frontmatter, and the one caller that ranks by date — `_next_front` — already
    reads each document and sorts on `info["date"]` itself."""
    out: list[dict] = []
    for folder in PHASE_DIRS:
        ph = canonical_phase(folder)
        if phase and ph != phase:
            continue
        d = os.path.join(root, folder)
        if not os.path.isdir(d):
            continue
        for name in sorted(os.listdir(d)):
            m = SPEC_FILE_RE.match(name)
            if not m:
                continue
            out.append({
                "phase": ph,
                "folder": folder,
                "legacy": folder in LEGACY_PHASES,
                "file": name,
                "path": os.path.join(d, name),
                "slug": m.group(1),
            })
    return out


def resolve_slug(root: str, slug: str) -> tuple[dict | None, list[dict]]:
    """The one spec file whose basename ends in `-<slug>.md`, wherever it sits.

    Returns (spec, matches). TWO MATCHES IS A REFUSAL, never a guess: the caller exits 2
    and names both paths. This is what makes N folder moves survivable — every
    cross-reference names the bare slug and never a path."""
    matches = [s for s in spec_files(root) if s["slug"] == slug]
    return (matches[0] if len(matches) == 1 else None), matches


# --------------------------------------------------------------------------- #
# the single-file parser
# --------------------------------------------------------------------------- #
def parse_sections(text: str) -> dict[str, dict]:
    """Every level-2 section of a spec file, keyed by its heading text.

    Sub-headings (`###`+) belong to their parent section — `## Impact` carries its parsed
    `### Standards …` sub-heading, and splitting on them would orphan it.

    Each entry carries `lines` (the body), `lineno` (0-based, of the heading itself), and
    `filled` — the three-state distinction the whole contract rests on: a heading that is
    present but empty is MALFORMED, which is neither an answer nor a not-yet.

    **A fenced block is never read as a heading.** `## Tasks` routinely carries a shell block,
    and a `## ` comment inside one used to open a phantom section — which `validate` then
    reported as a stray heading, and which silently truncated the real section at that line."""
    out: dict[str, dict] = {}
    current: str | None = None
    buf: list[str] = []
    start = 0
    lines = text.splitlines()
    fence: str | None = None

    def flush() -> None:
        if current is not None and current not in out:
            body = "\n".join(buf)
            out[current] = {"lines": list(buf), "lineno": start,
                            "filled": has_real_content(body), "body": body}

    for lineno, line in enumerate(lines):
        fm = FENCE_RE.match(line)
        if fm:
            mark = fm.group(1)
            if fence is None:
                fence = mark[0] * len(mark)
            elif mark[0] == fence[0] and len(mark) >= len(fence):
                fence = None
            if current is not None:
                buf.append(line)
            continue
        if fence is not None:
            if current is not None:
                buf.append(line)
            continue
        m = HEADING_RE.match(line)
        if m and len(m.group(1)) == 2:
            flush()
            current = m.group(2).strip()
            buf = []
            start = lineno
            continue
        if current is not None:
            buf.append(line)
    flush()
    return out


def section_state(sections: dict, heading: str) -> str:
    """`absent` · `empty` (present but malformed) · `filled`."""
    if heading not in sections:
        return "absent"
    return "filled" if sections[heading]["filled"] else "empty"


def stray_headings(sections: dict, schema: dict | None = None) -> list[str]:
    canon = set(canonical_headings(schema))
    return [h for h in sections if h not in canon]


def derive_stage(spec: dict, sections: dict, fm: dict, tasks: list[dict],
                 schema: dict | None = None) -> str:
    """The sub-stage, COMPUTED from section completeness and frontmatter — never declared.

    Declared state is forgotten on edit and goes stale; derived state regresses on its own
    when a section empties. Rules are evaluated in schema order and the LAST match wins."""
    s = schema or load_schema()
    stage = spec["phase"]
    for rule in s.get("stages", {}).get("derived", []):
        if rule.get("phase") != spec["phase"]:
            continue
        if _stage_match(rule.get("when", {}), sections, fm, tasks):
            stage = rule["id"]
    return stage


def _stage_match(when: dict, sections: dict, fm: dict, tasks: list[dict]) -> bool:
    if "anyOf" in when:
        return any(_stage_match(w, sections, fm, tasks) for w in when["anyOf"])
    if "filled" in when:
        return all(section_state(sections, h) == "filled" for h in when["filled"])
    if "frontmatter" in when:
        return bool(fm.get(when["frontmatter"]))
    if "taskState" in when:
        want = set(when["taskState"])
        return any(t["state"] in want for t in tasks)
    return False


def parse_tasks(text: str) -> list[dict]:
    """Every checkbox under `## Tasks`, in order: index, explicit id, state, text, line
    number, the `[P]` marker, the optional indented metadata (`files`/`pattern`/`verify`),
    and — for a blocked task — the reason written right in the line.

    `state` is `" "` (open), `"x"` (done) or `"!"` (blocked). The blocked marker is
    deliberately IN THE FILE rather than in sidecar state: it is what a human reads when
    they come to unblock it, and v1's hidden attempt counter was read by nobody."""
    sections = parse_sections(mask_comments(text))
    if "Tasks" not in sections:
        return []
    base = sections["Tasks"]["lineno"] + 1
    lines = sections["Tasks"]["lines"]
    out = []
    idx = 0
    section = 0
    for i, line in enumerate(lines):
        hm = HEADING_RE.match(line)
        if hm and len(hm.group(1)) == 3:
            section += 1          # a `### N.` heading starts a new task section
            continue
        m = CHECKBOX_RE.match(line)
        if not m:
            continue
        idx += 1
        state = m.group(2).lower()
        body = m.group(3).strip()
        idm = TASK_ID_RE.match(body)
        rest = body[idm.end():].lstrip() if idm else body
        parallel = bool(PARALLEL_RE.match(rest))
        blocked = BLOCKED_REASON_RE.search(body)
        files: list[str] = []
        pattern = verify = subject = commit = None
        subject_off = commit_off = last_meta_off = None
        meta_indent = None
        block_end = i + 1
        for off, cont in enumerate(lines[i + 1:], start=i + 1):
            # the task's block ends at a blank line, a non-indented line, or another
            # checkbox; anything else indented is scanned, so a wrapped prose line between
            # the checkbox and its `verify:` does not hide it.
            if not cont.strip() or cont[:1] not in (" ", "\t") or CHECKBOX_RE.match(cont):
                break
            block_end = off + 1
            mm = TASK_META_RE.match(cont)
            if not mm:
                continue
            key, val = mm.group(1).lower(), mm.group(2).strip()
            if meta_indent is None:
                meta_indent = cont[:len(cont) - len(cont.lstrip())]
            last_meta_off = off
            if key == "files":
                files = [p.strip() for p in val.split(",") if p.strip()]
            elif key == "pattern":
                pattern = val
            elif key == "subject":
                subject, subject_off = val, off
            elif key == "commit":
                commit, commit_off = val, off
            elif key == "verify":
                verify = val
            # `constraint:` is admitted by the grammar and read by nothing — the inert field.
            # This arm is why the dispatch is exhaustive rather than an `else: verify = val`:
            # under the open form, a `constraint:` line following `verify:` overwrote it, and
            # the loop would have run that prose as the task's shell command.
        out.append({
            "index": idx,
            "id": idm.group(1) if idm else None,
            "state": state,
            "checked": state == "x",
            "blocked": state == "!",
            "reason": blocked.group(1) if blocked else None,
            "text": body,
            "lineno": base + i,
            "section": section,
            "parallel": parallel,
            "files": files,
            "pattern": pattern,
            "verify": verify,
            "subject": subject,
            "commit": commit,
            # ONE PAST the task's own last line — checkbox plus every indented metadata
            # line under it, exactly the span `block_end` already tracked to find the
            # metadata. Exists so a caller can slice `lines[lineno:blockEndLineno]` and get
            # the task's literal source text, verbatim, with nothing re-rendered. The
            # `github` backend is the first reader: a task's raw block IS what a sub-issue
            # stores, so `checked`/`blocked` round-trip by re-parsing the same text through
            # THIS function again on read, rather than the backend inventing its own
            # encoding of state.
            "blockEndLineno": base + block_end,
            # where the anchor line is, and where one would go — so `task` upserts it
            # mechanically instead of the caller doing string surgery on the file. Both
            # forms are tracked because both are read AND, as of `task --commit`, both can be
            # written: `subject:` by `--check --subject`, `commit:` by `--check --commit` once
            # the real sha exists. A spec written before either form applied to it carries
            # only whichever one it has, and `--uncheck` must still be able to drop it.
            "subjectLineno": (base + subject_off) if subject_off is not None else None,
            "commitLineno": (base + commit_off) if commit_off is not None else None,
            # After the last metadata line when there is one; otherwise after the WHOLE
            # block, not under the checkbox's first physical line. A task with no `files:`
            # or `verify:` whose text wraps was being cut in half by its own `subject:`.
            "metaInsertAt": base + ((last_meta_off + 1) if last_meta_off is not None
                                    else block_end),
            "metaIndent": meta_indent or DEFAULT_META_INDENT,
        })
    return out


def task_progress(tasks: list[dict]) -> tuple[int, int, int]:
    """(checked, blocked, total)."""
    return (sum(1 for t in tasks if t["checked"]),
            sum(1 for t in tasks if t["blocked"]),
            len(tasks))


def parse_impact_standards(text: str, schema: dict | None = None) -> list[str]:
    """The `docs/standards/**.md` paths a spec DECLARES it will write, read from the one
    fixed sub-heading of `## Impact`.

    Only that sub-heading is parsed, and deliberately so. Its siblings name paths the spec
    does NOT promise to write — a background standard it *may* resolve, the product code it
    touches — and parsing those would flag a spec for not writing a doc it never claimed. A
    spec with no such sub-heading declares nothing and is never flagged: the check is
    opt-in by writing the heading."""
    s = schema or load_schema()
    imp = s.get("impact", {})
    anchors = [imp.get("parsedSubheading", "")] + list(imp.get("acceptedAliases", []))
    anchor_re = re.compile(
        r"^\s*(?:#{3,6}\s+|\*\*)\s*(?:" +
        "|".join(re.escape(a.rstrip("/ ")) for a in anchors if a) + r")",
        re.IGNORECASE)
    sections = parse_sections(strip_comments(text))
    if "Impact" not in sections:
        return []
    out: list[str] = []
    seen: set[str] = set()
    collecting = False
    for line in sections["Impact"]["lines"]:
        if anchor_re.match(line):
            collecting = True
            continue
        if SUBHEADING_RE.match(line):     # any other sub-heading closes the parsed zone
            collecting = False
            continue
        if not collecting or not BULLET_RE.match(line):
            continue
        # An unfilled `<placeholder>` declares nothing — the same rule has_real_content
        # uses. Without it the shipped template's own example bullet would make every
        # freshly captured spec report sp-impact-uncovered against a path nobody wrote.
        for m in STANDARD_PATH_RE.finditer(PLACEHOLDER_RE.sub("", line)):
            if m.group(0) not in seen:
                seen.add(m.group(0))
                out.append(m.group(0))
    return out


# How close a slug or title has to be before it resolves at all. Tuned to accept a typo and a
# copied fragment while refusing a merely adjacent spec: `0.62` matched
# `decide-plan-quick-skill` against `decide-sp-unrefined-severity` on this repository's own
# listing, which is not a near miss, it is a different spec.
FUZZY_MATCH_THRESHOLD = 0.75


def _norm(text: str) -> str:
    """Case, accents and runs of whitespace folded away — the form both sides of a title
    comparison are reduced to, so `Criação` and `criacao ` are the same string."""
    folded = unicodedata.normalize("NFD", " ".join((text or "").split()).lower())
    return "".join(c for c in folded if not unicodedata.combining(c))


def resolve_one(specs: list[dict], slug: str,
                titles: dict | None = None) -> tuple[dict | None, dict]:
    """Pick one spec descriptor out of a listing, by slug and then by title.

    Pure over the listing, so every backend resolves the same way and gets the same refusals
    — an ambiguous slug is exit 2 whether the duplicates are two files or two issues. THE
    TOLERANCE LIVES HERE AND NOWHERE ELSE, for that same reason.

    Four rungs, tried in order and stopping at the first that answers:

      1. the exact slug          the only path that costs anything today
      2. the exact title         normalised for case, accents and whitespace
      3. the closest slug OR title above the threshold, if exactly ONE clears it
      4. nothing                 `sp-unknown-slug`, exit 1

    TWO MATCHES IS STILL A REFUSAL at every rung — never a guess, and the refusal names the
    candidates so the human picks. A rung-3 answer is announced: the descriptor comes back
    carrying `resolvedBy: "approximate"` and what it matched, because a command that silently
    acted on a spec the human did not name is worse than one that asked.

    `titles` is `{slug: title}`, or a callable returning one. It is consulted ONLY after the
    exact slug misses, so the common path never pays to build it — which is what lets the
    `files` backend hand over a callable that opens every document."""
    matches = [s for s in specs if s["slug"] == slug]
    if len(matches) > 1:
        return None, _ambiguous(slug, matches, "slug")
    if matches:
        return matches[0], {}

    index = (titles() if callable(titles) else titles) or {}
    want = _norm(slug)

    exact = [s for s in specs if _norm(index.get(s["slug"], "")) == want]
    if len(exact) > 1:
        return None, _ambiguous(slug, exact, "title")
    if exact:
        return dict(exact[0], resolvedBy="title",
                    resolvedFrom=index.get(exact[0]["slug"], "")), {}

    scored = []
    for s in specs:
        ratio = max(
            difflib.SequenceMatcher(None, want, _norm(s["slug"])).ratio(),
            difflib.SequenceMatcher(None, want, _norm(index.get(s["slug"], ""))).ratio()
            if index.get(s["slug"]) else 0.0)
        if ratio >= FUZZY_MATCH_THRESHOLD:
            scored.append((ratio, s))
    if len(scored) > 1:
        best = max(r for r, _ in scored)
        tied = [s for r, s in scored if r == best]
        # A single clear winner among several that merely cleared the bar still resolves;
        # what refuses is a genuine tie, where picking either one would be a coin flip.
        if len(tied) > 1:
            return None, _ambiguous(slug, tied, "approximate")
        return dict(tied[0], resolvedBy="approximate",
                    resolvedFrom=index.get(tied[0]["slug"], "") or tied[0]["slug"]), {}
    if scored:
        s = scored[0][1]
        return dict(s, resolvedBy="approximate",
                    resolvedFrom=index.get(s["slug"], "") or s["slug"]), {}

    return None, {"code": "sp-unknown-slug", "exit": 1, "slug": slug,
                  "message": f"no spec with slug '{slug}'"}


def _ambiguous(slug: str, matches: list[dict], rung: str) -> dict:
    """The one refusal every rung of `resolve_one` shares — exit 2, with the candidates
    named. `rung` says WHICH comparison tied, because "two specs share a slug" and "your
    fragment is close to two titles" are fixed by different things."""
    where = [f"{m['phase']}/{m['file']}" for m in matches]
    return {
        "code": "sp-ambiguous-slug", "exit": 2, "slug": slug, "matchedOn": rung,
        "matches": where,
        "message": f"'{slug}' matches {len(matches)} specs by {rung} — {', '.join(where)}",
    }


def derive_info(spec: dict, text: str) -> dict:
    """Everything derivable from one spec's document, in one pass.

    THE SINGLE DERIVATION. Every backend hands its canonical document here and gets the same
    `info` back — frontmatter, sections, tasks, stage and policy. No backend derives any of
    it, which is why "every backend behaves identically" is a property of the code rather
    than a claim to be re-tested per target."""
    fm = parse_frontmatter(text)
    sections = parse_sections(body_after_frontmatter(text))
    tasks = parse_tasks(text)
    info = dict(spec)
    info.update({
        "text": text,
        "frontmatter": fm,
        "sections": sections,
        "tasks": tasks,
        "stage": derive_stage(spec, sections, fm, tasks),
        "verification": _policy(fm),
        # THE DATE COMES FROM THE DOCUMENT, not from the descriptor. It used to be the
        # basename's prefix, which every backend without filenames then had to fake. Reading
        # it here — in the one shared derivation — is what makes it the same fact in `files`,
        # in `github` and in a dict, and it is why no descriptor carries a `date` key at all.
        "date": str(fm.get("date", "")).strip(),
    })
    return info


def load_spec(root: str, slug: str) -> tuple[dict | None, dict]:
    """Resolve a slug against the files workspace and derive its document.

    Returns (info, err). `err` carries a ready-to-emit refusal when the slug is unknown or
    ambiguous, so every command handles both the same way."""
    specs = spec_files(root)
    spec, err = resolve_one(specs, slug, lambda: {
        s["slug"]: str(parse_frontmatter(read_text(s["path"]) or "").get("title", ""))
        for s in specs})
    if err:
        return None, err
    return derive_info(spec, read_text(spec["path"]) or ""), {}


# --------------------------------------------------------------------------- #
# the spec backend
# --------------------------------------------------------------------------- #
class SpecBackend:
    """Where a repo's specs actually live. One implementation per target; every command
    above talks to this and never to a path.

    THE INTERFACE IS THE DOCUMENT, NOT THE VERBS. `status`, `show`, `section`, `task`,
    `discover`, `promote` and `validate` are shared code layered on the five primitives
    below — they are not methods each backend reimplements. That is what makes "every
    backend behaves identically" provable by construction rather than by hoping three
    parsers agree: the canonical markdown document is the contract, the derivation of
    stages, gates, records and tasks happens once, and a backend's only job is to produce
    that document and to store it again.

    A backend is therefore free to serialise natively — `## Tasks` as sub-issues, sections
    as fields — provided it reassembles the canonical document on read. The hybrid
    serialisation lives inside each external implementation, exactly where it belongs, and
    it can never drift the JSON the CLI prints.

    Granular reading is unaffected by this split, because the cost it addresses is the
    agent's context and not I/O: `section` hands back the headings asked for whether or not
    the backend had to fetch the whole document to find them."""

    name = "abstract"

    def list_specs(self, phase: str | None = None) -> list[dict]:
        """Every spec descriptor, oldest first within each phase."""
        raise NotImplementedError

    def read_spec(self, slug: str) -> tuple[dict | None, dict]:
        """`(info, err)` — the canonical document plus everything derived from it, or a
        ready-to-emit refusal. Never raises for an unknown or ambiguous slug."""
        raise NotImplementedError

    def write_spec(self, info: dict, text: str) -> None:
        """Replace one spec's whole document with `text`."""
        raise NotImplementedError

    def create_spec(self, phase: str, filename: str, text: str) -> str:
        """Store a new spec and return the locator a report can show a human."""
        raise NotImplementedError

    def move_spec(self, info: dict, dest_phase: str) -> str:
        """The one lifecycle hop — `plans/` to `archive/` — returning the new locator."""
        raise NotImplementedError


class FilesBackend(SpecBackend):
    """Specs as markdown files under the specs workspace. The reference implementation:
    when the interface and this backend disagree, this backend is right, because it is the
    one whose behaviour every other backend is asserted against."""

    name = "files"

    def __init__(self, root: str) -> None:
        self.root = root

    def list_specs(self, phase: str | None = None) -> list[dict]:
        return spec_files(self.root, phase)

    def read_spec(self, slug: str) -> tuple[dict | None, dict]:
        return load_spec(self.root, slug)

    def write_spec(self, info: dict, text: str) -> None:
        write_text(info["path"], text)

    def create_spec(self, phase: str, filename: str, text: str) -> str:
        dest_dir = os.path.join(self.root, phase)
        os.makedirs(dest_dir, exist_ok=True)
        path = os.path.join(dest_dir, filename)
        write_text(path, text)
        return path

    def move_spec(self, info: dict, dest_phase: str) -> str:
        dest_dir = os.path.join(self.root, dest_phase)
        os.makedirs(dest_dir, exist_ok=True)
        dest = os.path.join(dest_dir, info["file"])
        os.rename(info["path"], dest)
        return dest


class MemoryBackend(SpecBackend):
    """Specs in a dict. No disk, no network, no repository to stage.

    This exists to be the OTHER side of the selftest's equality: the canonical case list runs
    against `files` and against this, and the two must agree. A backend that shares nothing
    with the filesystem but the interface is the only honest way to prove the interface is
    what the CLI depends on — if a command reaches around it to a path, this backend is where
    that shows up, immediately and without a fixture.

    It is deliberately NOT a cache and never reachable from the config: nothing a human can
    declare selects it, because a store that forgets on exit must never be somewhere real
    work can land."""

    name = "memory"

    def __init__(self) -> None:
        # slug -> (phase, filename, document). The filename is stored rather than rebuilt
        # from the slug so that this backend can hand back exactly what it was given, the
        # way a filesystem does. It no longer carries the capture date: that moved into the
        # document's `date:`, which every backend reads through the one derivation — the
        # divergence the equality check caught here was a backend RECOMPUTING the date, and
        # the fix was to stop having a second place able to compute it at all.
        self.docs: dict[str, tuple[str, str, str]] = {}

    def _descriptor(self, slug: str) -> dict:
        # The SAME key set `spec_files` returns, and nothing more. An extra key here would
        # be a field some command could come to depend on and that the files backend would
        # then not have.
        phase, filename, _ = self.docs[slug]
        m = SPEC_FILE_RE.match(filename)
        return {"phase": phase, "folder": phase, "legacy": False, "file": filename,
                "path": f"memory://{phase}/{filename}",
                "slug": m.group(1) if m else slug}

    def list_specs(self, phase: str | None = None) -> list[dict]:
        rows = [self._descriptor(s) for s in self.docs
                if phase is None or self.docs[s][0] == phase]
        return sorted(rows, key=lambda r: (PHASES.index(r["phase"]), r["file"]))

    def read_spec(self, slug: str) -> tuple[dict | None, dict]:
        spec, err = resolve_one(self.list_specs(), slug, lambda: {
            k: str(parse_frontmatter(d[2]).get("title", "")) for k, d in self.docs.items()})
        if err:
            return None, err
        return derive_info(spec, self.docs[spec["slug"]][2]), {}

    def write_spec(self, info: dict, text: str) -> None:
        phase, filename, _ = self.docs[info["slug"]]
        self.docs[info["slug"]] = (phase, filename, text)

    def create_spec(self, phase: str, filename: str, text: str) -> str:
        m = SPEC_FILE_RE.match(filename)
        slug = m.group(1) if m else filename
        self.docs[slug] = (phase, filename, text)
        return f"memory://{phase}/{filename}"

    def move_spec(self, info: dict, dest_phase: str) -> str:
        _, filename, text = self.docs[info["slug"]]
        self.docs[info["slug"]] = (dest_phase, filename, text)
        return f"memory://{dest_phase}/{filename}"


BACKEND_CASES = (
    ("list an empty store", lambda b: _listing(b)),
    ("create, then list", lambda b: _case_create(b)),
    ("read what was created", lambda b: _observable(b.read_spec("alpha")[0])),
    ("read an unknown slug", lambda b: b.read_spec("nope")[1]),
    ("validate what was created", lambda b: _case_validate(b)),
    ("the capture date survives the store", lambda b: _case_date(b)),
    ("write a section, then re-read", lambda b: _case_write(b)),
    ("tick a task", lambda b: _case_task(b)),
    ("stamp a record, then re-read", lambda b: _case_record(b)),
    # AFTER the three cases that author the document, never on the fresh capture form. See
    # `_case_front`: on a capture form the case passes with the reader broken.
    ("rank the front", lambda b: _case_front(b)),
    ("move to archive", lambda b: _case_move(b)),
    ("list after the move", lambda b: _listing(b)),
)


def _listing(b: "SpecBackend") -> list[dict]:
    """A listing minus `path` — the one field the locator is allowed to differ on."""
    return [{k: v for k, v in s.items() if k != "path"} for s in b.list_specs()]


def _case_doc(slug: str = "alpha") -> str:
    # A FIXED date, never `today()`: it is the fact the case asserts travels intact through
    # each store, and one computed at call time would compare equal to itself no matter what
    # either backend did with it.
    return (capture_form().replace("<SLUG>", slug).replace("<TITLE>", "Alpha")
            .replace("<DATE>", "2026-01-01").replace("<VERIFICATION>", "per-task"))


def _observable(info: dict | None) -> dict:
    """One spec's info minus the two fields a backend is SUPPOSED to disagree on.

    `path` is the locator — a filesystem path here, a URL there — and `text` is echoed back
    verbatim from what was written, so neither can distinguish a correct backend from a
    broken one. Everything else must match exactly, including the derived stage."""
    if info is None:
        return {}
    return {k: v for k, v in info.items() if k not in ("path", "text")}


def _case_create(b: "SpecBackend") -> list[dict]:
    b.create_spec("plans", "alpha.md", _case_doc())
    return _listing(b)


def _case_date(b: "SpecBackend") -> str:
    """The capture date, read back out of whatever the store did with the document.

    It used to ride in the basename, so `_listing` alone proved it survived. Now it is a
    frontmatter field, and the only thing that proves a backend did not drop, rewrite or
    recompute it is asking for it after a round trip."""
    info, _ = b.read_spec("alpha")
    return (info or {}).get("date", "")


def _case_validate(b: "SpecBackend") -> list[dict]:
    """Every finding for the one spec in the store — the READER, not just the store.

    The cases above prove a backend can hand back the document it was given. This proves the
    shared code ASKS it for one: a `validate_spec` that reaches around the interface to
    `read_text(s["path"])` gets nothing from a `memory://` locator and reports a well-formed
    document as missing every required key, while `files` reports the real findings. The two
    disagree, and the case fails. Nothing asserted that before, which is how `validate`
    shipped fabricating a finding per required key per spec against GitHub."""
    return validate_spec(b, b.list_specs()[0])


def _case_front(b: "SpecBackend") -> dict:
    """One ranked candidate — the same trap on the other disk reader.

    `_candidate` off the path ranks a `memory://` spec as an empty one with no tasks and no
    priority, which is exactly what `/specs:continue` was handed against GitHub. `heads` and
    `current` are pinned empty so the case asserts the READ and never the repository it
    happens to run in.

    IT MUST RUN ON AN AUTHORED DOCUMENT, which is why it is ordered last rather than beside
    the other read case. Measured on the fresh capture form this case PASSED with the reader
    fully broken: every field it compares collapses to the same value from an empty document
    — `titleize("alpha")` gives back the same `Alpha` the frontmatter carries, and the task
    counts, the progress and the stage are all already the empty ones. A fixture that cannot
    tell the two apart is a case that asserts nothing, and the only reason this one is known
    to discriminate is that reverting the reader was tried against it."""
    return _candidate(b, b.list_specs("plans")[0], load_schema(), set(), None)


def _case_write(b: "SpecBackend") -> dict:
    info, _ = b.read_spec("alpha")
    block, _ = upsert_section(info, "Problem", "## Problem\n\nUm problema.\n")
    b.write_spec(info, block)
    return _observable(b.read_spec("alpha")[0])


def _case_task(b: "SpecBackend") -> dict:
    info, _ = b.read_spec("alpha")
    block, _ = upsert_section(info, "Tasks", "## Tasks\n\n- [x] 1.1 feito\n")
    b.write_spec(info, block)
    info, _ = b.read_spec("alpha")
    return {"progress": task_progress(info["tasks"]), "stage": info["stage"]}


def _case_record(b: "SpecBackend") -> dict:
    info, _ = b.read_spec("alpha")
    b.write_spec(info, set_frontmatter_record(
        info["text"], "priority", {"level": "1", "criticality": "high"}))
    info, _ = b.read_spec("alpha")
    return spec_records(info["frontmatter"])


def _case_move(b: "SpecBackend") -> dict:
    info, _ = b.read_spec("alpha")
    b.move_spec(info, "archive")
    return _observable(b.read_spec("alpha")[0])


def resolution_failures() -> list[str]:
    """The four rungs of `resolve_one`, over a fixed listing. No backend, no store.

    It is asserted here rather than through a backend precisely because the tolerance is pure
    over the listing: if it were reachable only through one store, "every backend refuses the
    same way" would again be a claim rather than a property."""
    listing = [
        {"phase": "plans", "folder": "plans", "legacy": False,
         "file": "avaliar-o-fluxo-de-criacao-de-specs.md", "path": "x",
         "slug": "avaliar-o-fluxo-de-criacao-de-specs"},
        {"phase": "plans", "folder": "plans", "legacy": False,
         "file": "fechar-vazamentos-do-backend-files.md", "path": "y",
         "slug": "fechar-vazamentos-do-backend-files"},
    ]
    titles = {"avaliar-o-fluxo-de-criacao-de-specs":
              "Avaliar o fluxo de criação de specs, sobretudo no backend github",
              "fechar-vazamentos-do-backend-files":
              "Fechar os vazamentos do backend files"}
    out: list[str] = []

    def rung(label: str, given: str, want_slug: str | None, want_by: str | None,
             want_exit: int | None = None, specs: list[dict] | None = None) -> None:
        spec, err = resolve_one(specs if specs is not None else listing, given, titles)
        if want_exit is not None:
            if err.get("exit") != want_exit or err.get("code") != "sp-ambiguous-slug":
                out.append(f"{label}: expected an exit-{want_exit} sp-ambiguous-slug for "
                           f"{given!r}, got {err or spec}")
            return
        if err or spec is None:
            out.append(f"{label}: {given!r} did not resolve — {err}")
            return
        if spec["slug"] != want_slug:
            out.append(f"{label}: {given!r} resolved to {spec['slug']!r}, not {want_slug!r}")
        if spec.get("resolvedBy") != want_by:
            out.append(f"{label}: {given!r} announced resolvedBy="
                       f"{spec.get('resolvedBy')!r}, expected {want_by!r}")

    # 1. the exact slug — and it announces NOTHING, because nothing was inferred.
    rung("exact slug", "avaliar-o-fluxo-de-criacao-de-specs",
         "avaliar-o-fluxo-de-criacao-de-specs", None)
    # 2. the exact title, accents and case folded — a fragment copied out of the issue.
    rung("exact title", "AVALIAR O FLUXO DE CRIACAO DE SPECS, SOBRETUDO NO BACKEND GITHUB",
         "avaliar-o-fluxo-de-criacao-de-specs", "title")
    # 3. a slug with a typo — resolves, and SAYS it approximated.
    rung("approximate", "avaliar-o-fluxo-de-criacao-de-spec",
         "avaliar-o-fluxo-de-criacao-de-specs", "approximate")
    # 4. two specs sharing a slug — still exit 2, still naming both.
    dup = listing + [dict(listing[0], file="outro.md", phase="archive", folder="archive")]
    rung("ambiguous", "avaliar-o-fluxo-de-criacao-de-specs", None, None,
         want_exit=2, specs=dup)

    # And the rung that must NOT fire: something genuinely absent stays exit 1, never the
    # nearest spec on the front. This is what the threshold is for.
    spec, err = resolve_one(listing, "algo-completamente-diferente", titles)
    if err.get("code") != "sp-unknown-slug" or err.get("exit") != 1:
        out.append(f"an absent slug resolved to {spec and spec['slug']!r} instead of "
                   f"refusing with sp-unknown-slug")
    return out


def backend_equivalence_failures() -> list[str]:
    """Run the canonical case list against `files` and against `memory`, and name every
    case where they disagree.

    THIS IS THE PROOF OF THE CENTRAL CLAIM. "Every backend behaves identically" is the
    sentence the whole configurable-backend design rests on, and a sentence nobody checks is
    a wish. Two backends sharing nothing but the interface — one on real files in a temp
    directory, one in a dict — must produce byte-identical results for every case but the
    locator.

    Self-contained: `tempfile` is stdlib and the documents come from the embedded template,
    so this runs on an installed copy with no assets beside it."""
    import tempfile
    failures: list[str] = []
    with tempfile.TemporaryDirectory() as tmp:
        root = os.path.join(tmp, "specs")
        os.makedirs(os.path.join(root, "plans"))
        os.makedirs(os.path.join(root, "archive"))
        files: SpecBackend = FilesBackend(root)
        memory: SpecBackend = MemoryBackend()
        for label, case in BACKEND_CASES:
            try:
                got_f, got_m = case(files), case(memory)
            except Exception as e:                      # noqa: BLE001 — reported, not raised
                failures.append(f"{label}: raised {type(e).__name__}: {e}")
                continue
            if json.dumps(got_f, sort_keys=True, default=str) != \
                    json.dumps(got_m, sort_keys=True, default=str):
                failures.append(f"{label}: files={got_f!r} memory={got_m!r}")
    return failures


_BACKEND_CACHE: dict[str, SpecBackend] = {}


def open_backend(root: str) -> tuple[SpecBackend | None, dict]:
    """The backend this workspace declares, or a ready-to-emit refusal.

    Memoised per root because resolving it reads the config from disk, and a single command
    asks for it more than once. The cache holds no mutable state — a backend is its root and
    nothing else — so this is a lookup table, not a session.

    THIS IS WHERE "ON DEMAND" IS MADE TRUE for the `files` backend's specs worktree, and the
    reason it is here rather than in `FilesBackend.__init__`. Every command that reads or
    writes a spec passes through here and nothing else does — `doctor`, `config` and `selftest`
    never open a backend — so the worktree is created by the first command that actually needs
    the specs and never as a side effect of a diagnostic. A constructor could not make that
    distinction: `FilesBackend(root)` is also how the equivalence cases instantiate it over a
    bare temp directory with no repository, which must keep costing nothing and touching
    nothing.

    A backend named in the config but not yet implemented refuses with exit 2 rather than
    falling back to `files`. Silently writing specs to the local filesystem for a repo that
    asked for GitHub is the one failure that loses work instead of reporting it."""
    if root in _BACKEND_CACHE:
        return _BACKEND_CACHE[root], {}
    cfg = load_config(root)
    name = cfg["backend"]
    if name == "files":
        target, err = resolve_files_root(root, cfg)
        if err:
            # A worktree that could not be created — unignored, occupied, or refused by git.
            # Nothing falls back to the declared root: the specs are on the specs branch, and
            # writing them beside the code is the state this backend exists to end.
            return None, err
        backend: SpecBackend = FilesBackend(target)
    elif name == "github":
        gh, err = open_github_backend(root)
        if err:
            # `gh` missing, nobody logged in, or no repository to point at. Each is an
            # exit-2 refusal for the same reason the worktree failures above are: nothing
            # falls back to `files` when the repo asked for GitHub.
            return None, err
        backend = gh                                        # type: ignore[assignment]
    elif name == "azure-boards":
        az, err = open_azure_backend(root)
        if err:
            # No `az`, no extension, nobody logged in, no configured project, or no declared
            # phase-to-state mapping. Each is an exit-2 refusal, and nothing falls back to
            # `files` when the repo asked for Azure Boards.
            return None, err
        backend = az                                        # type: ignore[assignment]
    else:
        return None, {
            "code": "sp-backend-unavailable", "exit": 2, "backend": name,
            "message": f"backend '{name}' is declared in {CONFIG_FILE} but this copy of "
                       f"specs.py does not implement it yet — no spec was read or written",
        }
    _BACKEND_CACHE[root] = backend
    return backend, {}


# --------------------------------------------------------------------------- #
# the github backend — transport over the `gh` CLI
# --------------------------------------------------------------------------- #
# `gh`'s own exit code for "no host is authenticated", distinct from the 1 it uses for an
# API that answered with an error. Telling the two apart is the whole point of shelling out
# to `gh` instead of speaking HTTP: one is fixed by `gh auth login`, the other is not.
GH_NOT_AUTHENTICATED = 4
# OURS, never one of gh's: the binary is not on PATH, so no process ever started.
GH_MISSING = 127


class BackendRefusal(Exception):
    """An external backend's call that failed, carried to the CLI boundary as a
    ready-to-emit refusal. Shared by `github` and `azure-boards`.

    THREE OF THE FIVE PRIMITIVES RETURN A LOCATOR AND NOT `(value, err)` — `write_spec`,
    `create_spec` and `move_spec` were shaped around a backend that cannot fail halfway.
    A network target can, and the contract is "never a traceback", so the failure travels
    as an exception carrying the refusal already built and is converted exactly once, in
    `main`. Widening the interface instead would make every backend and every command pay,
    in every signature, for a failure mode only the external backends have."""

    def __init__(self, err: dict) -> None:
        super().__init__(err.get("message", "the backend failed"))
        self.err = err


def _gh_run(cwd: str, *argv: str, stdin: str | None = None) -> tuple[int, str, str]:
    """Exit code, stdout AND stderr of one `gh` command.

    A SIBLING of `_git_run`, deliberately not a reuse of it. The two binaries fail
    differently and the difference IS the contract here: `gh` answers "nobody is logged in"
    with its own exit 4 and a body-less stderr, and "GitHub said no" with exit 1 plus an
    `HTTP <code>` line, while the JSON explaining why goes to STDOUT. A runner that
    flattened those to "nonzero" could not tell a human to run `gh auth login` rather than
    to check the repository name.

    A missing binary comes back as `GH_MISSING` rather than as an exception, so the one
    failure a user is most likely to hit is an ordinary return value on the path every
    caller already handles — never a traceback out of a `subprocess` call.

    A cwd that does not exist is an error and NOT a fallback to `"."`, for the same reason
    `_git_run` refuses it: `gh repo view` reads the git remote of wherever it runs, so the
    fallback would resolve some other repository and then write specs into it.

    60s and not git's 30: this is a round trip to api.github.com, not a local object
    lookup, and a paginated listing of a busy repository legitimately takes seconds."""
    import subprocess
    if not os.path.isdir(cwd):
        return 1, "", f"not a directory: {cwd}"
    try:
        out = subprocess.run(["gh", *argv], capture_output=True, text=True, timeout=60,
                             cwd=cwd, input=stdin)
        return out.returncode, out.stdout, out.stderr
    except FileNotFoundError as e:
        return GH_MISSING, "", str(e)
    except (OSError, ValueError, subprocess.SubprocessError) as e:   # noqa: BLE001
        return 1, "", str(e)


def _gh_said(stdout: str, stderr: str) -> str:
    """The one line worth quoting back from a failed `gh` call.

    `gh api` SPLITS A FAILURE ACROSS BOTH STREAMS: stderr carries its own one-liner
    (`gh: Not Found (HTTP 404)`) and stdout carries GitHub's JSON body, whose `message` is
    the half that says why — "API rate limit exceeded for user ID 1" against a bare
    "HTTP 403". Quoting only stderr loses the reason; quoting only stdout loses the status
    code, and loses everything for the failures that never reach the API at all."""
    head = next((ln.strip() for ln in (stderr or "").splitlines() if ln.strip()), "")
    # gh prefixes its own one-liners with `gh: `, and every refusal built from this already
    # says "gh said" — kept, the message reads "gh said: gh: Not Found".
    head = head[4:].strip() if head.startswith("gh: ") else head
    detail = ""
    try:
        obj = json.loads(stdout or "")
        if isinstance(obj, dict) and isinstance(obj.get("message"), str):
            detail = obj["message"].strip()
    except (json.JSONDecodeError, TypeError, ValueError):
        detail = ""
    if detail and detail.lower() not in head.lower():
        return f"{head} — {detail}" if head else detail
    return head or "gh failed without saying why"


def gh_refusal(action: str, code: int, stdout: str, stderr: str) -> dict:
    """Every way a `gh` call can fail, as an exit-2 refusal a human can act on.

    THREE OUTCOMES, THREE DIFFERENT REMEDIES, and separating them is the reason this
    backend is a subprocess and not an HTTP client: the binary is missing (install it),
    the binary is there but nobody is logged in (`gh auth login`), or GitHub itself said
    no (read what it said). Collapsing them into "github failed" would leave the first two
    looking like an outage and send a human hunting a network problem that is not there.

    Authentication is recognised by TWO signals, not one. `gh api` exits 4 when no host is
    configured at all, but a configured host holding a revoked or wrong token gets as far
    as the API and comes back as an ordinary exit 1 with `HTTP 401` — the same shape as a
    404, and the wrong remedy for it.

    Always exit 2, always a refusal and never a finding: nothing was read and nothing was
    written, which is a different statement from "the specs have a problem"."""
    if code == GH_MISSING:
        return {
            "code": "sp-gh-missing", "exit": 2, "action": action,
            "message": "backend 'github' needs the `gh` CLI and it is not on PATH — install "
                       "GitHub CLI (https://cli.github.com), then run `gh auth login`; no "
                       "spec was read or written",
        }
    said = _gh_said(stdout, stderr)
    if code == GH_NOT_AUTHENTICATED or "HTTP 401" in (stderr or "") \
            or "gh auth login" in (stderr or ""):
        return {
            "code": "sp-gh-unauthenticated", "exit": 2, "action": action, "gh": said,
            "message": f"`gh` is installed but not authenticated for this repository — run "
                       f"`gh auth login`; gh said: {said}",
        }
    return {
        "code": "sp-gh-api-error", "exit": 2, "action": action, "gh": said, "ghExit": code,
        "message": f"github refused {action} — gh said: {said}",
    }


GH_REMOTE_RE = re.compile(r"github\.com[:/]+([^/\s]+)/([^/\s]+?)(?:\.git)?/?$")


def resolve_github_repo(cwd: str) -> tuple[str, dict]:
    """`owner/name` for the repository this checkout points at, or a refusal.

    ASK `gh` FIRST, because it answers the question the API will actually be called with:
    it resolves the remote gh itself would use, honours the `gh repo set-default` a human
    set for a fork, and surfaces the auth failure at RESOLUTION time rather than three
    calls later in the middle of a write.

    The git remote is the fallback and not the primary for exactly that reason — it is a
    string, not an answer: on a fork, `origin` names the fork rather than the repository
    the issues live in. It is kept because a checkout whose gh-to-git integration fails
    (no git on PATH, a checkout gh cannot attribute) still has a legible answer, and
    refusing there would be refusing over a detail of how gh finds the remote.

    Never guesses a repository it cannot name. A wrong answer here does not fail — it
    silently reads and writes somebody else's issues."""
    code, out, err = _gh_run(cwd, "repo", "view", "--json", "nameWithOwner",
                             "--jq", ".nameWithOwner")
    if code == 0 and out.strip():
        return out.strip(), {}
    # The two failures the remote cannot repair — no binary, nobody logged in — refuse here
    # with their own remedy instead of degrading into "could not resolve the repository".
    if code in (GH_MISSING, GH_NOT_AUTHENTICATED) or "gh auth login" in (err or ""):
        return "", gh_refusal("resolving the repository", code, out, err)
    url = _git(cwd, "remote", "get-url", "origin").strip()
    m = GH_REMOTE_RE.search(url) if url else None
    if m:
        return f"{m.group(1)}/{m.group(2)}", {}
    return "", {
        "code": "sp-gh-repo-unresolved", "exit": 2, "remote": url or None,
        "gh": _gh_said(out, err),
        "message": f"backend 'github' could not tell which repository holds the specs — "
                   f"`gh repo view` failed ({_gh_said(out, err)}) and origin "
                   f"({url or 'absent'}) is not a github.com remote; add one, or pick the "
                   f"repository with `gh repo set-default`",
    }


# HYBRID SERIALISATION — the WHOLE canonical document is one issue body, and a document too
# large for one body spills into continuation comments on that same issue.
#
# IT USED TO PUT `## Tasks` IN SUB-ISSUES, one per task, and that mapping is retired. It was
# chosen because `## Tasks` is the one section with a native tracker counterpart carrying its
# own state and identity, which is true and turned out not to be the question. The question is
# whether anything READS the native state, and nothing ever did: `parse_tasks` takes a task's
# checked/blocked from the raw block on both ends, never from the sub-issue, so the issue's own
# open/closed was a projection written and never consulted — the same status `hybrid_title`
# records for the issue title, but costing one to three API calls per task per write instead of
# nothing. Measured on this repository on 2026-08-03: 68 spec issues against 689 task
# sub-issues, a listing of 8 pages and 4.4 MB taking 8.4s that EVERY specs command pays, and a
# `write_spec` on a ten-task spec spending twelve round trips where one would do.
#
# What the collapse buys, beyond the calls: the round-trip obligation `spec-backend.md` puts on
# an external backend stops being a property to check and becomes the thing that is stored. No
# anchors, no positional keys, no two-part retirement of a removed task's marker — the three
# mechanisms that produced this backend's only two measured defects (every `### N.` group
# heading dropped; a checked task's sub-issue born open). `- [ ]` in an issue body is a native
# GitHub task list anyway: it renders as a checkbox with a progress count, and ticking it in the
# web UI edits the document, which closing a sub-issue never did.
#
# THE MARKER ON THE BODY CARRIES THE FILENAME, which is now the bare `<slug>.md`. It used to
# carry `YYYY-MM-DD-<slug>.md`, and that prefix was the ONLY reason this marker held a date: the
# files backend read a spec's capture date out of its basename, so a store with no filenames had
# to keep a synthetic one to stay equal to it. The date is a frontmatter field now, read by the
# one shared derivation in every backend, and the marker is back to doing its one job.
#
# That job is what makes a spec issue distinguishable from an ordinary one, and it is why the
# marker did not simply disappear with the date: a repo's issue tracker belongs to its humans,
# and a backend that treated every open issue as a spec would list the bug reports and then
# write over them. An HTML comment is the one place in a markdown body that survives a round
# trip through the issue editor while staying invisible to a human reading the issue, and the
# same reasoning applies one level down to a continuation comment's own marker, below.
HYBRID_MARKER_RE = re.compile(r"\A<!--\s*quenching-spec:\s*(\S+)(?:\s+parts=(\d+))?"
                              r"\s*-->[ \t]*\r?\n")


def hybrid_wrap(filename: str, text: str, parts: int = 1) -> str:
    """The marker line a spec issue is recognised by, and the document under it.

    `parts=` is written ONLY when there is more than one. The single-part form — every document
    but the two largest this repository holds — is therefore byte-identical to the marker as it
    was before continuations existed, and one regex reads both."""
    count = f" parts={parts}" if parts > 1 else ""
    return f"<!-- quenching-spec: {filename}{count} -->\n{text}"


def hybrid_unwrap(body: str) -> tuple[str, str, int]:
    """`(filename, chunk, parts)` for a spec issue, or `("", "", 0)` for anything else.

    Line endings are normalised on the way in. GitHub stores and returns issue bodies with
    CRLF, so a document written as LF comes back different from what was stored — every section
    parse, every diff and the round-trip equality would all read that as content having changed.

    `parts` is what tells a reader whether the chunk it just got IS the document or only its
    head, and it is read from the body already in hand. A one-part spec — the normal case —
    never pays a call to discover there is nothing more to fetch."""
    body = (body or "").replace("\r\n", "\n")
    m = HYBRID_MARKER_RE.match(body)
    if not m:
        return "", "", 0
    return m.group(1), body[m.end():], int(m.group(2) or 1)


HYBRID_PART_MARKER_RE = re.compile(r"\A<!--\s*quenching-spec-part:\s*(\d+)/(\d+)"
                                   r"(?:\s+eol=(\d))?\s*-->[ \t]*\r?\n")


def hybrid_wrap_part(index: int, total: int, chunk: str, eol: bool) -> str:
    """One continuation chunk, marked with its own position.

    `eol` describes THE CUT THAT PRECEDES THIS CHUNK, not the one after it — that is why the
    flag can live on the continuation comment and the body marker needs no second field. The
    rebuild reads it as "the part before me ended at a line boundary", which is what lets it
    restore a newline the store may have trimmed off the end of a body without ever inventing
    one at a cut that landed mid-line."""
    return f"<!-- quenching-spec-part: {index}/{total} eol={1 if eol else 0} -->\n{chunk}"


def hybrid_unwrap_part(body: str) -> tuple[int, str, bool]:
    """`(index, chunk, eol)` for a continuation comment, or `(0, "", False)` for a comment a
    human wrote. Ordinary discussion on a spec issue must stay possible."""
    body = (body or "").replace("\r\n", "\n")
    m = HYBRID_PART_MARKER_RE.match(body)
    if not m:
        return 0, "", False
    return int(m.group(1)), body[m.end():], m.group(3) == "1"


def hybrid_split(text: str, limit: int | None) -> list[tuple[str, bool]]:
    """The document as `(chunk, preceding-cut-was-at-a-line-boundary)` pairs, each within
    `limit`. The first pair's flag is always False: nothing precedes it.

    ONE PART IS THE NORMAL CASE and the only one most repositories will ever take: `limit` is
    None for a store with no published body ceiling, and a document under the ceiling comes back
    as a single pair whatever the store. Measured on this repository's 69 specs on 2026-08-03,
    two exceed GitHub's 65,536 — one of them an ACTIVE plan, not an archived one — so the
    alternative to spilling is refusing to store a spec somebody is building.

    Cuts are made at line boundaries, falling back to a mid-line cut only for the pathological
    single line longer than a whole body. That fallback exists so the loop cannot fail to make
    progress; nothing in this repository takes it."""
    if limit is None or len(text) <= limit:
        return [(text, False)]
    chunks: list[tuple[str, bool]] = []
    rest = text
    pending_eol = False
    while len(rest) > limit:
        # `limit` and not `limit + 1`: the slice below keeps the newline it cuts on, so a
        # boundary found AT `limit` would produce a chunk one character over the very ceiling
        # this loop exists to respect.
        cut = rest.rfind("\n", 0, limit)
        if cut <= 0:
            chunks.append((rest[:limit], pending_eol))
            rest, pending_eol = rest[limit:], False
            continue
        chunks.append((rest[:cut + 1], pending_eol))
        rest, pending_eol = rest[cut + 1:], True
    chunks.append((rest, pending_eol))
    return chunks


def hybrid_join(chunks: list[tuple[str, bool]]) -> str:
    """The document back from its parts.

    A chunk whose flag says the cut before it was a line boundary nudges its PREDECESSOR to end
    in a newline. `hybrid_split` slices verbatim and every such predecessor already ends that
    way; the nudge is there because an issue tracker is free to trim trailing whitespace off a
    body it stores, and a chunk that came back one newline short would weld itself to the line
    after it. A cut made MID-line is never nudged, because the newline would be this function's
    invention rather than the document's."""
    out: list[str] = []
    for chunk, eol in chunks:
        if out and eol and not out[-1].endswith("\n"):
            out[-1] += "\n"
        out.append(chunk)
    return "".join(out)


# The two ceilings a tracker imposes on the fields this serialisation writes. Named here,
# beside the helpers both external backends share, rather than inside `GitHubBackend`: the
# hybrid helpers stopped being GitHub's the moment `azure-boards` started using them.
#
# TITLE: 255, the SMALLER of GitHub's 256-character issue title and Azure Boards'
# 255-character `System.Title`. One number for one shared helper — the alternative is a cap
# per backend threaded through code that is deliberately backend-agnostic, to buy one
# character. Neither figure appears in the REST reference either vendor publishes; GitHub's
# is the widely documented UI limit and Azure's is from its field documentation, unproven
# here like the rest of that backend.
#
# BODY: GitHub's 65,536-character issue body. Azure Boards' `System.Description` has no
# comparable published limit, so this ceiling is enforced only where it is known to exist.
HYBRID_TITLE_MAX = 255
GH_BODY_MAX = 65_536

# What one CHUNK of a document may hold, as opposed to what GitHub will accept. The margin
# covers the marker line a chunk is wrapped in and leaves room for a longer one later; a
# chunk sized to the ceiling itself would put the wrapped body one marker over it, which is
# the off-by-a-header every "just use the limit" split makes once.
GH_PART_MAX = GH_BODY_MAX - 1_024


def hybrid_short_title(text: str) -> str:
    """A title that fits, cut on a word boundary and marked with an ellipsis.

    CUTTING LOSES NOTHING, and that is what makes it the right answer rather than a
    compromise. `hybrid_title` already records that an issue's title is a PROJECTION of the
    document — rewritten from the frontmatter on every write, undone by the next write if a
    human edits it in the web UI — and the same holds one level down: `parse_tasks` reads a
    sub-issue's BODY, never its title, so the block stays whole no matter what the title says.

    The alternative was to send it raw and let the tracker answer. Measured on this
    repository on 2026-08-02: 15 tasks across 12 specs carry a checkbox line longer than the
    cap, the longest at 946 characters — so "send it and see" is not a hypothetical branch,
    it is what a migration would have hit twelve times."""
    text = " ".join((text or "").split())
    if len(text) <= HYBRID_TITLE_MAX:
        return text
    cut = text[:HYBRID_TITLE_MAX - 1]
    space = cut.rfind(" ")
    if space > HYBRID_TITLE_MAX // 2:
        cut = cut[:space]
    return cut.rstrip() + "…"


class GitHubBackend(SpecBackend):
    """Specs as GitHub issues, reached through `gh api` in a subprocess.

    ONE ISSUE IS ONE SPEC, and the phase is the issue's own state: open is `plans`, closed
    is `archive`. That mapping is not a shortcut — it is the same fact told once. A label
    would be a second declaration of a phase the tracker already knows, and the two would
    diverge the first time somebody closed an issue from the web UI.

    ONE ISSUE BODY IS THE WHOLE DOCUMENT. There are no sub-issues: the retirement and what
    measured it are recorded at HYBRID SERIALISATION above. A document past GitHub's body
    ceiling spills into continuation comments on its own issue, which is the only reason this
    class ever makes a second call for one spec.

    It derives NOTHING. `resolve_one` picks the spec, `derive_info` produces the stages,
    gates, records and tasks, exactly as they are produced for a file on disk; `parse_tasks`
    is the ONLY thing that ever decides a task is checked or blocked. This class turns issues
    into the canonical document and back and does no more than that.

    THE SEVEN FRONTMATTER RECORDS STAY IN THE BODY, none of them a label. Multi-field
    records (`priority`, `branch`, `merge`, `refined`) have no honest single-string label
    form — encoding `{level, criticality, complexity, date}` into a label name would invent
    a second format only a new parser could read back, which is the backend deriving its
    own encoding exactly where the interface forbids it. Keeping them in the body costs
    the records being invisible in the issue list without opening the issue — accepted,
    because `parse_frontmatter` already reads them for free and a label would not remove
    that read, only add a second, driftable copy beside it.

    The listing is fetched once per process and cached, which is a local cache and NOT a
    store: it is not authoritative, nothing outside this object reads it, and every write
    drops it. It exists because the CLI asks for the listing more than once per command,
    and each ask is a network round trip. Since the listing already carries every body,
    `read_spec` costs NOTHING beyond it for a one-part spec — which is every spec but the
    largest two this repository holds."""

    name = "github"

    def __init__(self, repo: str, cwd: str) -> None:
        self.repo = repo
        self.cwd = cwd
        # descriptor, issue number, first chunk, how many parts the marker declares
        self._rows: list[tuple[dict, int, str, int, str]] | None = None
        self._legacy: list[tuple[int, str, str, int, str]] = []

    # -- transport ---------------------------------------------------------- #
    def _api(self, action: str, *argv: str, stdin: str | None = None):
        """One `gh api` call, parsed. Raises `BackendRefusal` for every way it can fail."""
        code, out, err = _gh_run(self.cwd, "api", *argv, stdin=stdin)
        if code != 0:
            raise BackendRefusal(gh_refusal(action, code, out, err))
        try:
            return json.loads(out or "null")
        except json.JSONDecodeError as e:
            # Not an API error — gh exited 0 and handed back something unparseable. Named
            # separately so it can never be read as "GitHub said no".
            raise BackendRefusal({
                "code": "sp-gh-bad-response", "exit": 2, "action": action,
                "message": f"`gh api` exited 0 while {action} but its output is not JSON: {e}",
            }) from e

    def _write_api(self, action: str, method: str, path: str, payload: dict):
        """A mutating call, with the payload on STDIN rather than in argv.

        `--input -` and not `-f body=…`: a spec document is kilobytes of markdown with
        newlines, quotes and backticks in it, and every one of those is a way for argv
        quoting to corrupt what lands in the issue.

        THE BODY CEILING IS CHECKED HERE, at the one point every write passes through,
        rather than at each caller — a check per caller is the shape that leaves one out.
        Refusing beats letting GitHub answer 422: in the middle of a migration of dozens of
        specs a 422 is a validation error with no spec's name on it, while this names the
        measured size and the ceiling and emits no call at all.

        IT IS A BACKSTOP AND NO LONGER THE POLICY. Every document write goes through
        `hybrid_split`, which cuts to `GH_PART_MAX` before a payload is ever built, so this
        refusal cannot fire for a spec's own text. It stays because it guards the one point
        every write passes through, and a future caller that builds a body some other way
        must still be unable to hand GitHub something it will answer 422 to."""
        body = payload.get("body")
        if isinstance(body, str) and len(body) > GH_BODY_MAX:
            raise BackendRefusal({
                "code": "sp-gh-body-too-large", "exit": 2, "action": action,
                "size": len(body), "max": GH_BODY_MAX,
                "message": f"the document is {len(body)} characters and a GitHub issue body "
                           f"holds {GH_BODY_MAX} — shorten a section while {action}; nothing "
                           f"was written",
            })
        return self._api(action, "-X", method, path, "--input", "-",
                         stdin=json.dumps(payload))

    # -- the listing, fetched once ------------------------------------------- #
    def _load(self) -> list[tuple[dict, int, str, int]]:
        if self._rows is not None:
            return self._rows
        # `--slurp` because `--paginate` alone concatenates one JSON array per page, which
        # is not a JSON document. state=all: `archive` is the closed half of the tracker,
        # so a default (open-only) listing would report every archived spec as missing.
        pages = self._api("listing the repository's issues", "--paginate", "--slurp",
                          f"repos/{self.repo}/issues?state=all&per_page=100")
        rows: list[tuple[dict, int, str, int, str]] = []
        legacy: list[tuple[int, str, str, int, str]] = []
        for page in (pages or []):
            for issue in (page or []):
                if not isinstance(issue, dict) or "pull_request" in issue:
                    # GitHub models a pull request AS an issue, so `/issues` answers with
                    # both. A PR can never be a spec, and one that happened to carry the
                    # marker would otherwise be listed and then written over.
                    continue
                filename, head, parts = hybrid_unwrap(issue.get("body") or "")
                m = SPEC_FILE_RE.match(filename)
                if not m:
                    # A marker in the pre-fold `YYYY-MM-DD-<slug>.md` form is a SPEC, and it
                    # is kept apart rather than skipped. Skipping is what an ordinary issue
                    # gets, and treating an un-migrated spec that way makes the whole front
                    # vanish silently — `migrate` reads this bucket and nothing else does.
                    if LEGACY_DATED_FILE_RE.match(filename):
                        legacy.append((int(issue.get("number") or 0), filename,
                                       head, parts, str(issue.get("title") or "")))
                    continue
                phase = "archive" if issue.get("state") == "closed" else "plans"
                rows.append(({
                    # The SAME key set `spec_files` returns and nothing more — an extra key
                    # here is a field some command comes to depend on and that the files
                    # backend does not have. `legacy` is False by construction: the v2
                    # folder split never existed here.
                    "phase": phase, "folder": phase, "legacy": False, "file": filename,
                    "path": issue.get("html_url")
                            or f"https://github.com/{self.repo}/issues/{issue.get('number')}",
                    "slug": m.group(1),
                    # For a one-part spec — every spec but the largest — `head` IS the whole
                    # document and this listing has already paid for it. Only a spilled one
                    # costs `read_spec` a second call, and only for the slug it was given.
                }, int(issue.get("number") or 0), head, parts,
                    str(issue.get("title") or "")))
        self._rows = rows
        self._legacy = legacy
        return rows

    def legacy_rows(self) -> list[tuple[int, str, str, int, str]]:
        """`(number, dated filename, head, parts, issue title)` for every spec still stored
        under the pre-fold basename. `migrate` is the only caller; the read path never sees
        these, because a half-migrated front that half-works is worse than one that says so."""
        self._load()
        return list(self._legacy)

    def _invalidate(self) -> None:
        self._rows = None
        self._legacy = []

    def _issue_number(self, slug: str) -> int:
        return self._issue_parts(slug)[0]

    def _issue_parts(self, slug: str) -> tuple[int, int]:
        """`(issue number, how many parts are stored)` — both from the listing already in hand,
        so knowing whether there are stale continuation comments to clean up costs no call."""
        for descriptor, number, _, parts, _title in self._load():
            if descriptor["slug"] == slug:
                return number, parts
        raise BackendRefusal({
            "code": "sp-gh-issue-gone", "exit": 2, "slug": slug,
            "message": f"spec '{slug}' was in the listing and is not there any more — the "
                       f"issue was deleted or transferred while this command ran; nothing "
                       f"was written",
        })

    # -- the five primitives -------------------------------------------------- #
    def list_specs(self, phase: str | None = None) -> list[dict]:
        rows = [dict(d) for d, _, _, _, _ in self._load()
                if phase is None or d["phase"] == phase]
        return sorted(rows, key=lambda r: (PHASES.index(r["phase"]), r["file"]))

    def read_spec(self, slug: str) -> tuple[dict | None, dict]:
        rows = self._load()
        spec, err = resolve_one(self.list_specs(), slug,
                                {d["slug"]: t for d, _, _, _, t in rows})
        if err:
            return None, err
        # `spec["slug"]`, never the slug that was ASKED for: a title or approximate match
        # resolved to a different one, and looking the document up by the request would
        # raise right after the resolution succeeded.
        number, head, parts, native = next((n, d, p, t)
                                           for descriptor, n, d, p, t in rows
                                           if descriptor["slug"] == spec["slug"])
        full_text = head if parts <= 1 else self._joined(number, head, parts)
        # The title comes back from the issue's own, which is where the write put it. A
        # document that still carries its own `title:` is returned untouched.
        return derive_info(spec, hybrid_title_join(full_text, native)), {}

    def write_spec(self, info: dict, text: str) -> None:
        number, had_parts = self._issue_parts(info["slug"])
        self._store(number, info["slug"], info["file"], text, had_parts)
        self._invalidate()

    def _store(self, number: int, slug: str, filename: str, text: str,
               had_parts: int) -> None:
        """The whole write, given an issue number already in hand.

        Split out for `migrate`, which knows every number from its own scan and must not go
        back to the listing between writes: `_invalidate` after each one would make the next
        lookup refetch all eight pages, turning a 73-spec fold into 73 full listings. It is
        the SAME serialisation either way — a migration with a writer of its own would be a
        second implementation that runs exactly once, on the day it matters most."""
        stored, title = hybrid_project(slug, text)
        chunks = hybrid_split(stored, GH_PART_MAX)
        self._write_api(f"updating issue #{number}", "PATCH",
                        f"repos/{self.repo}/issues/{number}",
                        {"title": title,
                         "body": hybrid_wrap(filename, chunks[0][0], len(chunks))})
        self._sync_parts(number, chunks, had_parts)

    def create_spec(self, phase: str, filename: str, text: str) -> str:
        m = SPEC_FILE_RE.match(filename)
        stored, title = hybrid_project(m.group(1) if m else filename, text)
        chunks = hybrid_split(stored, GH_PART_MAX)
        issue = self._write_api("creating an issue", "POST", f"repos/{self.repo}/issues",
                                {"title": title,
                                 "body": hybrid_wrap(filename, chunks[0][0], len(chunks))})
        number = int((issue or {}).get("number") or 0)
        url = (issue or {}).get("html_url") or f"https://github.com/{self.repo}/issues/{number}"
        self._sync_parts(number, chunks)
        if phase == "archive":
            # Created open and then closed, because "closed" is not a state an issue can be
            # born in. Two calls for a case `new` never takes — only a migration does.
            self._set_state(number, "closed")
        self._invalidate()
        return url

    def move_spec(self, info: dict, dest_phase: str) -> str:
        number = self._issue_number(info["slug"])
        issue = self._set_state(number, "closed" if dest_phase == "archive" else "open")
        self._invalidate()
        return (issue or {}).get("html_url") \
            or f"https://github.com/{self.repo}/issues/{number}"

    def _set_state(self, number: int, state: str):
        return self._write_api(f"setting issue #{number} to {state}", "PATCH",
                               f"repos/{self.repo}/issues/{number}", {"state": state})

    # -- the continuation comments a spilled document uses --------------------- #
    def _comments(self, number: int) -> list[dict]:
        return self._api(f"listing comments on #{number}",
                         "--paginate", "--slurp",
                         f"repos/{self.repo}/issues/{number}/comments?per_page=100") or []

    def _part_comments(self, number: int) -> list[tuple[int, dict]]:
        """`(index, comment)` for this issue's continuation comments, in part order.

        Ordinary discussion on a spec issue stays possible and is skipped here, the same way
        `_load` skips an issue without the spec marker: a store that assumed every comment was
        its own would eat a human's note the first time somebody left one."""
        found: list[tuple[int, dict]] = []
        for page in self._comments(number):
            for comment in (page if isinstance(page, list) else [page]):
                index, _, _ = hybrid_unwrap_part((comment or {}).get("body") or "")
                if index:
                    found.append((index, comment))
        found.sort(key=lambda row: row[0])
        return found

    def _joined(self, number: int, head: str, parts: int) -> str:
        """The whole document for a spilled spec — one extra call, made only when the marker
        on the body says there is more.

        A part the marker promised and the comments do not hold is a REFUSAL, not a shorter
        document: silently returning the head would hand every downstream command a spec whose
        `## Tasks` simply stops, and the next write would then persist that truncation as the
        new truth."""
        chunks = [(head, False)]      # nothing precedes the head, so its flag is unused
        for _, comment in self._part_comments(number):
            _, chunk, eol = hybrid_unwrap_part(comment.get("body") or "")
            chunks.append((chunk, eol))
        if len(chunks) != parts:
            raise BackendRefusal({
                "code": "sp-gh-parts-missing", "exit": 2, "issue": number,
                "found": len(chunks), "declared": parts,
                "message": f"issue #{number} declares {parts} document parts and "
                           f"{len(chunks)} are present — a continuation comment was deleted; "
                           f"nothing was read and nothing was written",
            })
        return hybrid_join(chunks)

    def _sync_parts(self, number: int, chunks: list[tuple[str, bool]],
                    had_parts: int = 1) -> None:
        """Make the issue's continuation comments match `chunks[1:]` exactly.

        COSTS NOTHING FOR A ONE-PART SPEC THAT WAS ALREADY ONE PART, which is every write this
        repository will make but two: `chunks` is in hand and `had_parts` comes from the listing
        already fetched, so the common case returns before any call is made.

        `had_parts` is why the early return is safe. A document that USED to spill and no longer
        does still has stale comments to delete, and a check that only looked at the new part
        count would leave them there to be joined back on the next read — a truncation that
        would then be persisted as the truth by the write after it.

        A comment the document no longer needs is DELETED, not retired: unlike an issue, a
        comment really can be deleted with an ordinary token, so there is no leftover to skip
        on the next read and no second meaning for a marker to carry."""
        want = chunks[1:]
        if not want and had_parts <= 1:
            return
        existing = self._part_comments(number)
        for position, (chunk, eol) in enumerate(want, start=2):
            body = hybrid_wrap_part(position, len(chunks), chunk, eol)
            if position - 2 < len(existing):
                cid = existing[position - 2][1]["id"]
                self._write_api(f"updating continuation comment {cid} on #{number}", "PATCH",
                                f"repos/{self.repo}/issues/comments/{cid}", {"body": body})
            else:
                self._write_api(f"adding a continuation comment to #{number}", "POST",
                                f"repos/{self.repo}/issues/{number}/comments", {"body": body})
        for _, comment in existing[len(want):]:
            self._api(f"deleting a stale continuation comment on #{number}",
                      "-X", "DELETE", f"repos/{self.repo}/issues/comments/{comment['id']}")


def hybrid_title(slug: str, text: str) -> str:
    """What a human sees in the issue list, for a document stored WHOLE.

    This is the fallback half of `hybrid_project`, and the sentence that used to be written
    here — the title is a projection, rewritten on every write, so a web edit is undone by
    the next one — is now true only of this path. Where the projection applies, the native
    title is the STORAGE: editing it in the web UI renames the spec, exactly as ticking a
    `- [ ]` in the body edits the document. That is the deliberate consequence of making
    something read the mapping back, and it is why `hybrid_title_split` refuses a title the
    tracker would cut."""
    return hybrid_short_title(str(parse_frontmatter(text).get("title") or titleize(slug)))


def hybrid_title_split(text: str) -> tuple[str, str] | None:
    """`(the document without its title, the title)` — or None when it must be stored whole.

    THE ONE NATIVE MAPPING THAT PAYS FOR ITSELF. `spec-backend.md` allows an external backend
    to use its host's constructs where a mapping exists, and holds it to one test: something
    must READ the native value back. The issue title failed that test for its whole life — it
    was rewritten from the frontmatter on every write and never once consulted — which made it
    a projection, and a projection is duplicated truth. Reading it back is what turns it into
    storage, and it costs nothing: the title was already being written on every write.

    Returning None is the safety, and it is checked rather than assumed. The document is only
    projected when it is in the shape `new` stamps — `title:` immediately after `slug:`, and
    the `# <TITLE>` heading alone between the frontmatter and the first section — because the
    reassembly has to put both back at an exact offset and the store keeps no note of where
    they were. A title the tracker would cut is also refused: cutting used to lose nothing
    precisely because nothing read it, and the moment something does, a cut title is a
    renamed spec."""
    title = str(parse_frontmatter(text).get("title", "")).strip()
    if not title or hybrid_short_title(title) != title:
        return None
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        return None
    close = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
    if close is None:
        return None
    if [ln.split(":", 1)[0].strip() for ln in lines[1:close]][:2] != ["slug", "title"]:
        return None
    # THE RAW LINE, not the parsed value. A quoted title — `title: "…"` — parses to the same
    # string with the quotes gone, so a rebuild from the value alone silently drops them:
    # measured on this repository, 4 of 73 specs quote their title and each came back two
    # characters short. The projection stores a VALUE and can only reproduce a line it would
    # have written itself, so anything else is stored whole.
    if lines[2] != f"title: {title}\n":
        return None
    if lines[close + 1:close + 4] != ["\n", f"# {title}\n", "\n"]:
        return None
    return "".join(lines[:2] + lines[3:close + 2] + lines[close + 4:]), title


def hybrid_project(slug: str, text: str) -> tuple[str, str]:
    """`(what goes in the body, what goes in the title)`, for every external backend.

    ONE place, for two reasons. Within a backend, a create that projected and an update that
    did not would leave the title reading as the spec's while the body carried a second,
    competing one. Across backends, `github` and `azure-boards` storing the title differently
    is exactly the drift `spec-backend.md` forbids — the canonical document is the contract,
    and two external stores disagreeing about what it holds is that contract broken twice."""
    proj = hybrid_title_split(text)
    return proj if proj else (text, hybrid_title(slug, text))


def hybrid_title_join(stored: str, title: str) -> str:
    """Put `title:` and the `# <TITLE>` heading back, at the offsets `hybrid_title_split` cut
    them from. The inverse, and asserted as one by the round-trip case.

    A stored document that still HAS a `title:` was never projected — an older issue, or one
    whose shape `split` refused — and comes back untouched. That is the whole signal: `title`
    is a required frontmatter key, so its absence can only mean the store is holding it."""
    if str(parse_frontmatter(stored).get("title", "")).strip():
        return stored
    lines = stored.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        return stored
    close = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
    if close is None:
        return stored
    return "".join(lines[:2] + [f"title: {title}\n"] + lines[2:close + 2]
                   + [f"# {title}\n", "\n"] + lines[close + 2:])


def open_github_backend(root: str) -> tuple[SpecBackend | None, dict]:
    """The `github` backend for this workspace, or the refusal that says why not.

    Resolution happens HERE and not in `GitHubBackend.__init__`, so the cost — one `gh`
    round trip — is paid by the first command that actually needs a spec, on the same
    "on demand" rule `open_backend` applies to the files worktree. It is also what makes
    the missing-binary and not-logged-in refusals arrive at the START of a command instead
    of halfway through a write."""
    cwd = find_repo_root(root)
    repo, err = resolve_github_repo(cwd)
    if err:
        return None, err
    return GitHubBackend(repo, cwd), {}


GH_REFUSAL_CASES = (
    # (label, gh exit, stdout, stderr, expected code) — the literal streams `gh` 2.97
    # produces, captured by running it. Every one is exit 2: a refusal, never a finding.
    ("no binary on PATH", GH_MISSING, "", "", "sp-gh-missing"),
    ("no host authenticated", GH_NOT_AUTHENTICATED, "",
     "To get started with GitHub CLI, please run:  gh auth login\n",
     "sp-gh-unauthenticated"),
    ("a revoked token", 1, '{"message":"Bad credentials","status":"401"}',
     "gh: Bad credentials (HTTP 401)\n", "sp-gh-unauthenticated"),
    ("a repository that is not there", 1, '{"message":"Not Found","status":"404"}',
     "gh: Not Found (HTTP 404)\n", "sp-gh-api-error"),
    ("rate limited", 1,
     '{"message":"API rate limit exceeded for user ID 1.","status":"403"}',
     "gh: API rate limit exceeded (HTTP 403)\n", "sp-gh-api-error"),
)


def gh_refusal_failures() -> list[str]:
    """The transport's classifier, asserted against gh's real output.

    THE ONE THING THIS BACKEND PROMISES BEFORE IT PROMISES ANYTHING ELSE is that no failure
    reaches a human as a traceback and that each one arrives with the remedy that fixes it.
    That promise lives entirely in `gh_refusal`, it is decided by string matching on another
    program's stderr, and a `gh` release that reworded one line would break it silently —
    so the cases hold the literal streams rather than a paraphrase of them.

    Self-contained: no network, no `gh`, no repository. It runs on an installed copy, which
    is exactly where a classifier quietly reduced to "github failed" would go unnoticed."""
    failures: list[str] = []
    for label, code, out, err, want in GH_REFUSAL_CASES:
        got = gh_refusal("reading a spec", code, out, err)
        if got.get("code") != want:
            failures.append(f"{label}: classified as {got.get('code')!r}, not {want!r}")
        if got.get("exit") != 2:
            failures.append(f"{label}: exits {got.get('exit')!r}, and a refusal is exit 2")
        if not str(got.get("message") or "").strip():
            failures.append(f"{label}: refused with an empty message")
    # The remedy each refusal has to carry, checked as text because that is what a human
    # reads. A missing binary that did not name `gh auth login` would leave the reader
    # installing the CLI and stopping there.
    for code, needle in ((GH_MISSING, "gh auth login"),
                         (GH_NOT_AUTHENTICATED, "gh auth login")):
        msg = gh_refusal("reading a spec", code, "", "")["message"]
        if needle not in msg:
            failures.append(f"exit {code}: the refusal does not name `{needle}` — {msg}")
    # The round trip the shell serialisation rests on, including the CRLF GitHub actually
    # stores bodies with.
    doc = "---\ntitle: Alpha\n---\n\n## Problem\n\nUm problema.\n"
    for label, body in (("as written", hybrid_wrap("alpha.md", doc)),
                        ("as GitHub returns it",
                         hybrid_wrap("alpha.md", doc).replace("\n", "\r\n"))):
        name, back, parts = hybrid_unwrap(body)
        if (name, back, parts) != ("alpha.md", doc, 1):
            failures.append(f"marker round trip {label}: got {(name, back, parts)!r}")
    # A marker written WITHOUT `parts=` must read as one part, because that is the form every
    # spec but a spilled one is stored in and the form every issue already in a repository
    # carries. A reader that answered 0 here would treat the whole corpus as truncated.
    if hybrid_unwrap("<!-- quenching-spec: x.md -->\n" + doc)[2] != 1:
        failures.append("a marker with no `parts=` did not read as a single-part document")
    if hybrid_unwrap("An ordinary bug report.\n") != ("", "", 0):
        failures.append("an issue with no marker was read as a spec")
    return failures


# The fields `parse_tasks` derives, minus the ones a rebuild reproduces only because the
# document does: `lineno`/`blockEndLineno`/`metaInsertAt`/`metaIndent`/`subjectLineno`/
# `commitLineno` are POSITIONS. They are covered by the byte-for-byte equality below —
# a document that comes back identical necessarily reparses to the same line numbers — so
# this tuple stays what it is: the semantic comparison for the field-by-field message that
# names WHICH task drifted when the stricter check has already said the document did.
HYBRID_TASK_SEMANTIC_KEYS = ("id", "state", "checked", "blocked", "reason", "text", "parallel",
                         "files", "pattern", "verify", "subject", "commit")


def gh_body_ceiling_failures() -> list[str]:
    """A body over the ceiling refuses BEFORE any call is made — proved with a transport that
    records every call it is asked to make and fails the check if it was asked at all.

    No network and no `gh`: the point is not that GitHub says no, it is that this backend
    never gives it the chance."""
    failures: list[str] = []
    backend = GitHubBackend("owner/repo", os.getcwd())
    calls: list[str] = []
    backend._api = lambda action, *argv, stdin=None: calls.append(action)   # type: ignore
    try:
        backend._write_api("creating an issue", "POST", "repos/owner/repo/issues",
                           {"title": "x", "body": "a" * (GH_BODY_MAX + 1)})
    except BackendRefusal as e:
        if e.err.get("code") != "sp-gh-body-too-large":
            failures.append(f"an oversized body refused with {e.err.get('code')!r}, "
                            f"not sp-gh-body-too-large")
        if e.err.get("exit") != 2:
            failures.append("an oversized body refused with an exit other than 2")
    else:
        failures.append("an oversized body was sent to GitHub instead of refusing")
    if calls:
        failures.append(f"the refusal still made {len(calls)} call(s) — it must emit none")
    try:
        backend._write_api("creating an issue", "POST", "repos/owner/repo/issues",
                           {"title": "x", "body": "a" * GH_BODY_MAX})
    except BackendRefusal:
        failures.append("a body exactly at the ceiling was refused — the ceiling is inclusive")
    if len(calls) != 1:
        failures.append("a body within the ceiling did not reach the transport")
    return failures


def hybrid_serialization_failures() -> list[str]:
    """The one obligation `spec-backend.md` puts on an external backend: it reassembles the
    canonical document on read, BYTE FOR BYTE.

    It used to be a hard claim, because `## Tasks` was stored apart from the rest and the
    document had to be rebuilt from an anchored pile of blocks. With the whole document in one
    body the claim is nearly free — which is most of why the mapping was retired — and what is
    left to prove is the part that is still real:

    - a document under the ceiling is ONE part, stored and returned unchanged;
    - a document over it splits, and the parts JOIN BACK to exactly what went in;
    - both survive the CRLF a tracker really stores bodies with, applied per part, because that
      is how the parts come back — separately, each normalised on its own;
    - `parse_tasks` reads the same tasks out the other end, since that shared derivation is the
      only thing that ever decides a task is checked or blocked.

    The fixture stays grouped under `### N.` headings with a line of prose inside `## Tasks`. It
    was written for the loss that motivated it — the shell used to empty that section, and 47 of
    this repository's 66 specs came back a structure short with no error anywhere — and it stays
    because a split is still free to cut through a group heading.

    Self-contained: no network, no `gh`."""
    doc = ("---\ntitle: Alpha\nverification: per-task\n---\n\n"
          "## Problem\n\nAlgo.\n\n"
          "## Tasks\n\n"
          "### 1. Primeiro grupo\n\n"
          "Uma linha de prosa dentro de `## Tasks`, que tambem tem de voltar.\n\n"
          "- [ ] 1.1 primeira\n      files: a.py, b.py\n      verify: pytest\n"
          "- [x] 1.2 segunda\n\n"
          "### 2. Segundo grupo\n\n"
          "- [!] 2.1 terceira — blocked: esperando review\n\n"
          "- [ ] [P] quarta sem id\n\n"
          "## Outcome\n\n")
    failures: list[str] = []
    tasks = parse_tasks(doc)

    def store(chunks: list[tuple[str, bool]]) -> str:
        """What comes back after a store-and-reload, with each part CRLF'd on its own."""
        wrapped = [hybrid_wrap("alpha.md", chunks[0][0], len(chunks))] + [
            hybrid_wrap_part(i, len(chunks), c, eol)
            for i, (c, eol) in enumerate(chunks[1:], start=2)]
        stored = [w.replace("\n", "\r\n") for w in wrapped]
        _, head, parts = hybrid_unwrap(stored[0])
        if parts != len(chunks):
            failures.append(f"the marker declared {parts} parts for a {len(chunks)}-part "
                            f"document — a reader would stop early or ask for one too many")
        back = [(head, False)]
        for body in stored[1:]:
            index, chunk, eol = hybrid_unwrap_part(body)
            if not index:
                failures.append("a continuation comment did not read back as one")
            back.append((chunk, eol))
        return hybrid_join(back)

    # ONE PART — the case every spec in this repository but two takes.
    whole = hybrid_split(doc, GH_PART_MAX)
    if len(whole) != 1:
        failures.append(f"a {len(doc)}-character document split into {len(whole)} parts under "
                        f"a {GH_PART_MAX} ceiling")
    if store(whole) != doc:
        failures.append("a one-part document did not come back byte for byte — the one "
                        "obligation spec-backend.md puts on an external backend")

    # MANY PARTS, forced with a ceiling small enough that this fixture spills. A real spill is
    # a 70 KB document and would make the check unreadable; what a split has to survive is the
    # same either way, and a small ceiling exercises MORE boundaries per character, including
    # cuts that land inside a group and inside a task's own metadata block.
    spilled = hybrid_split(doc, 90)
    if len(spilled) < 3:
        failures.append(f"a 90-character ceiling produced {len(spilled)} parts — the "
                        f"multi-part path is not being exercised")
    if any(len(c) > 90 for c, _ in spilled):
        failures.append("a chunk came back over the ceiling it was split to")
    if store(spilled) != doc:
        failures.append("a spilled document did not join back byte for byte")

    # The pathological single line longer than a whole part. It must not hang and it must not
    # lose a byte; nothing in this repository takes this branch, and a split that could not
    # make progress would take it as an infinite loop rather than as an error.
    long_line = "x" * 250 + "\n"
    cut = hybrid_split(long_line, 90)
    if hybrid_join(cut) != long_line:
        failures.append("a line longer than one part did not survive the split")

    # A part joined back must reparse to the same tasks — the shared derivation is the only
    # thing that reads state, so this is what "identical" means to every caller downstream.
    tasks2 = parse_tasks(store(spilled))
    if len(tasks2) != len(tasks):
        failures.append(f"a rebuilt document parsed {len(tasks2)} tasks from {len(tasks)}")
    else:
        for before, after in zip(tasks, tasks2):
            b = {k: before[k] for k in HYBRID_TASK_SEMANTIC_KEYS}
            a = {k: after[k] for k in HYBRID_TASK_SEMANTIC_KEYS}
            if b != a:
                failures.append(f"task '{b['id'] or before['index']}' drifted: "
                                f"before={b!r} after={a!r}")

    # A comment a human left on a spec issue is not a document part. The reverse of the marker
    # rule one level up: a repo's issues belong to its humans, and a backend that read every
    # comment as its own storage would splice a note into the middle of the spec.
    if hybrid_unwrap_part("Concordo, mas a task 2.1 depende da 1.2.\n")[0]:
        failures.append("an ordinary comment was read as a continuation part")

    # THE TITLE IS CUT, THE DOCUMENT IS NOT. The tracker caps a title; the body is the only
    # half `parse_tasks` ever reads. This repository's own longest task line is 946 characters,
    # so the cut is exercised on a length it really carries.
    long_text = "9.9 " + " ".join(f"palavra{i:03d}" for i in range(120))
    short = hybrid_short_title(long_text)
    if len(short) > HYBRID_TITLE_MAX:
        failures.append(f"hybrid_short_title returned {len(short)} characters, over the "
                        f"{HYBRID_TITLE_MAX} a tracker accepts")
    if not short.endswith("…") or not long_text.startswith(short[:-1].rstrip()):
        failures.append("a cut title is not a prefix of the line it came from, marked as cut")
    if hybrid_short_title("9.9 curta") != "9.9 curta":
        failures.append("hybrid_short_title touched a title that already fitted")

    # THE TITLE PROJECTION, on the shape `new` actually stamps. What the store holds must
    # carry neither `title:` nor the `# <TITLE>` heading, and putting the native title back
    # must return the document byte for byte — the same obligation the body is held to, on the
    # one field that is no longer inside it.
    # THE FIXTURE IS THE SHAPE OF A REAL DOCUMENT, not a minimal one. Three properties, each
    # from a way this repository's own specs really look: an accented title, because the
    # harness language is pt-BR and an accent is where a title projection loses bytes if it
    # ever re-encodes; `### N.` groups with prose inside `## Tasks`, because 49 of 68 specs
    # carry groups and that is precisely the structure the retired sub-issue mapping dropped;
    # and task metadata lines, because they are what a split is most likely to cut through.
    canonical = (
        "---\nslug: alpha\ntitle: Avaliar o fluxo de criação de specs\ndate: 2026-01-01\n"
        "verification: per-section\n---\n\n"
        "# Avaliar o fluxo de criação de specs\n\n"
        "## Problem\n\nO documento não volta como entrou.\n\n"
        "## Tasks\n\n"
        "### 1. Primeiro grupo\n\n"
        "Uma linha de prosa dentro de `## Tasks`, que também tem de voltar.\n\n"
        "- [ ] 1.1 primeira\n      files: a.py, b.py\n      verify: pytest\n"
        "- [x] 1.2 segunda\n\n"
        "### 2. Segundo grupo\n\n"
        "- [!] 2.1 terceira — blocked: esperando revisão\n\n"
        "## Outcome\n\n")
    # And the same document over GitHub's 65,536 ceiling. This is the case the projection
    # makes newly interesting: the frontmatter and the `# <TITLE>` heading it removes both
    # live in the HEAD chunk, which is exactly the chunk a spill cuts. Two of this
    # repository's specs are over the ceiling as whole documents, one of them an active plan.
    big = canonical.replace(
        "## Outcome\n\n",
        "### 3. Grupo grande\n\n"
        + "".join(f"- [ ] 3.{i} tarefa com acentuação — número {i}\n"
                  for i in range(1, 2600))
        + "\n## Outcome\n\n")
    if len(big) <= GH_BODY_MAX:
        failures.append(f"the over-ceiling fixture is only {len(big)} characters — it does "
                        f"not reach the {GH_BODY_MAX} it exists to cross")
    proj = hybrid_title_split(canonical)
    if proj is None:
        failures.append("the capture form's own shape was refused by the title projection — "
                        "every spec `new` creates would be stored with a duplicated title")
    else:
        stored, native = proj
        if "title:" in stored or f"# {native}" in stored:
            failures.append("the projected document still carries the title it handed to the "
                            "store — the duplication the projection exists to remove")
        if native != str(parse_frontmatter(canonical).get("title", "")).strip():
            failures.append(f"the title handed to the store was {native!r}, not the "
                            f"document's own")
        if hybrid_title_join(stored, native) != canonical:
            failures.append("the title projection is not reversible — "
                            f"{hybrid_title_join(stored, native)!r} != {canonical!r}")

    # A document the projection REFUSES is stored whole, and a read must not then graft a
    # second title onto it. `doc` above is exactly that shape: no `slug:`, no heading.
    if hybrid_title_split(doc) is not None:
        failures.append("a document outside the capture shape was projected anyway — the "
                        "reassembly has no note of where its title was")
    if hybrid_title_join(doc, "whatever the tracker says") != doc:
        failures.append("a document that still carries its own `title:` was rewritten on read")

    # THE SAME ROUND TRIP, AGAINST BOTH EXTERNAL BACKENDS — each with the ceiling it really
    # passes to `hybrid_split`: `github` splits at GH_PART_MAX, `azure-boards` hands None and
    # gets one chunk. Two stores that serialise a title differently is the drift the canonical
    # document exists to prevent, and it is cheap to refute here: the projection, the wrap, the
    # split and the reassembly are the whole write path, and none of it needs a network.
    for backend_name, ceiling in (("github", GH_PART_MAX), ("azure-boards", None)):
        for label, source in (("one part", canonical), ("over the ceiling", big)):
            stored, native = hybrid_project("alpha", source)
            if native != str(parse_frontmatter(source).get("title", "")).strip():
                failures.append(f"{backend_name}/{label}: stored the title as {native!r}")
            if "title:" in stored.split("\n---\n", 1)[0]:
                failures.append(f"{backend_name}/{label}: the body handed to the store still "
                                f"carries `title:`")
            rebuilt = hybrid_title_join(store(hybrid_split(stored, ceiling)), native)
            if rebuilt != source:
                failures.append(f"{backend_name}/{label}: the document did not come back byte "
                                f"for byte through the title projection")

    # A QUOTED title is refused, and this one was found by the corpus rather than by reasoning.
    # `title: "…"` parses to the same string with the quotes gone, so a rebuild from the value
    # writes an unquoted line and the document comes back two characters short — 4 of this
    # repository's 73 specs quote their title, and all four failed the byte-for-byte round trip
    # before the raw line was checked instead of the parsed value.
    quoted = canonical.replace("title: Avaliar o fluxo de criação de specs\n",
                               'title: "Avaliar o fluxo de criação de specs"\n', 1)
    if hybrid_title_split(quoted) is not None:
        failures.append("a quoted `title:` was projected — the reassembly writes the value "
                        "back unquoted, so the document loses the two quote characters")

    # The marker fold, which is the only thing that moves a capture date out of a basename.
    folded = legacy_marker_fold("2026-07-25-alpha.md", canonical)
    if folded is None or folded[0] != "alpha.md":
        failures.append(f"the marker fold answered {folded!r} for a dated basename")
    elif str(parse_frontmatter(folded[1]).get("date", "")) != "2026-01-01":
        failures.append("the marker fold overwrote a `date:` the document already declared — "
                        "the basename's copy is never allowed to win")
    undated = canonical.replace("date: 2026-01-01\n", "", 1)
    folded = legacy_marker_fold("2026-07-25-alpha.md", undated)
    if folded is None or str(parse_frontmatter(folded[1]).get("date", "")) != "2026-07-25":
        failures.append("the marker fold did not carry the basename's date into `date:` — "
                        "the prefix is the only copy, so dropping it without moving it loses "
                        "the capture date outright")
    elif legacy_marker_fold("alpha.md", undated) is not None:
        failures.append("the marker fold fired on a basename that is already folded")

    # A title the tracker would cut is refused, because a cut title is now a renamed spec.
    long_title = ("---\nslug: alpha\ntitle: " + "t" * (HYBRID_TITLE_MAX + 1) +
                  "\ndate: 2026-01-01\n---\n\n# " + "t" * (HYBRID_TITLE_MAX + 1) +
                  "\n\n## Problem\n\nAlgo.\n")
    if hybrid_title_split(long_title) is not None:
        failures.append("a title over the tracker's ceiling was projected — storing it cuts "
                        "it, and reading it back would rename the spec")
    return failures


# --------------------------------------------------------------------------- #
# the azure-boards backend — transport over the `az` CLI
# --------------------------------------------------------------------------- #
# OURS, never one of az's: the binary is not on PATH, so no process ever started. Same
# number and same meaning as `GH_MISSING`, kept separate so neither constant becomes the
# other's by accident.
AZ_MISSING = 127

# `az` does NOT have gh's exit 4 — it answers almost everything with exit 1 and says why in
# stderr, so the split into remedies is made on what it SAID rather than on the code. Each
# tuple is (fragment lowercased, refusal code, remedy), tried in order; the first match
# wins, so the more specific fragments come first.
AZ_STDERR_SIGNALS = (
    ("az extension add", "sp-az-extension-missing",
     "run `az extension add --name azure-devops`"),
    ("is not in the 'az' command group", "sp-az-extension-missing",
     "run `az extension add --name azure-devops`"),
    ("az devops login", "sp-az-unauthenticated", "run `az devops login`"),
    ("az login", "sp-az-unauthenticated", "run `az login`"),
    ("before you can run azure devops commands", "sp-az-unauthenticated",
     "run `az devops login`"),
    ("tf400813", "sp-az-unauthenticated",
     "the identity is authenticated but not authorised for this project"),
    # Captured from az 2.88 by running `az boards query` with no defaults set. It reaches
    # this table only when the defaults vanish BETWEEN `resolve_azure_project` and the call
    # — otherwise resolution refuses first, with `sp-az-no-project`, which is why both
    # carry the same code and the same remedy.
    ("must be specified", "sp-az-no-project",
     "run `az devops configure --defaults organization=https://dev.azure.com/<org> "
     "project=<project>`"),
)


def _az_run(cwd: str, *argv: str, stdin: str | None = None) -> tuple[int, str, str]:
    """Exit code, stdout AND stderr of one `az` command.

    A SIBLING of `_gh_run` for the same reason that one is a sibling of `_git_run`: the two
    CLIs fail differently, and here the difference is that `az` has no dedicated
    "unauthenticated" exit code — it says so in stderr and exits 1, the same as an API
    error. Flattening them would tell a human to check the project name when the real fix is
    `az devops login`.

    `--only-show-errors` suppresses az's upgrade notices and preview warnings, which
    otherwise land in stderr and would be quoted back as the reason a call failed.

    A missing binary comes back as `AZ_MISSING` rather than as an exception, so the failure
    a user is most likely to hit stays an ordinary return value.

    60s and not git's 30, matching `_gh_run`: this is a round trip to dev.azure.com."""
    import subprocess
    if not os.path.isdir(cwd):
        return 1, "", f"not a directory: {cwd}"
    try:
        out = subprocess.run(["az", *argv, "--only-show-errors"], capture_output=True,
                             text=True, timeout=60, cwd=cwd, input=stdin)
        return out.returncode, out.stdout, out.stderr
    except FileNotFoundError as e:
        return AZ_MISSING, "", str(e)
    except (OSError, ValueError, subprocess.SubprocessError) as e:   # noqa: BLE001
        return 1, "", str(e)


def _az_said(stdout: str, stderr: str) -> str:
    """The one line worth quoting back from a failed `az` call.

    Unlike `gh`, `az` puts the whole story in stderr and prefixes it with `ERROR: `. Stdout
    is read as a fallback only, for the calls that fail with a JSON body and an empty
    stderr."""
    for line in (stderr or "").splitlines():
        line = line.strip()
        if not line:
            continue
        return line[6:].strip() if line.upper().startswith("ERROR:") else line
    head = next((ln.strip() for ln in (stdout or "").splitlines() if ln.strip()), "")
    return head or "az failed without saying why"


def az_refusal(action: str, code: int, stdout: str, stderr: str) -> dict:
    """Every way an `az` call can fail, as an exit-2 refusal a human can act on.

    FOUR OUTCOMES, FOUR REMEDIES — one more than the `gh` transport has, because `az boards`
    lives in an extension that is not installed by default. A human whose `az` is installed
    and logged in still gets "not recognised" until they add it, and telling them to log in
    again would be the wrong remedy delivered confidently.

    Always exit 2, always a refusal and never a finding: nothing was read and nothing was
    written."""
    if code == AZ_MISSING:
        return {
            "code": "sp-az-missing", "exit": 2, "action": action,
            "message": "backend 'azure-boards' needs the Azure CLI and it is not on PATH — "
                       "install `az` (https://aka.ms/azure-cli), then run "
                       "`az extension add --name azure-devops` and `az devops login`; no "
                       "spec was read or written",
        }
    said = _az_said(stdout, stderr)
    haystack = f"{stderr or ''}\n{stdout or ''}".lower()
    for fragment, refusal_code, remedy in AZ_STDERR_SIGNALS:
        if fragment in haystack:
            return {
                "code": refusal_code, "exit": 2, "action": action, "az": said,
                "message": f"azure-boards refused {action} — {remedy}; az said: {said}",
            }
    return {
        "code": "sp-az-api-error", "exit": 2, "action": action, "az": said, "azExit": code,
        "message": f"azure devops refused {action} — az said: {said}",
    }


def resolve_azure_project(cwd: str) -> tuple[tuple[str, str], dict]:
    """`(organization, project)` for this checkout, or a refusal.

    ASK `az` FOR ITS OWN DEFAULTS, the same reasoning `resolve_github_repo` applies to `gh`:
    the answer that matters is the one the CLI will actually use, and a human who ran
    `az devops configure --defaults organization=… project=…` has already stated it in the
    place `az` reads. Deriving it from a git remote instead would be a guess dressed as an
    answer — an Azure DevOps remote URL carries an organization and a REPOSITORY, and the
    repository is not the project.

    Never guesses. Missing defaults are a refusal naming the exact command that sets them,
    because a wrong answer here does not fail — it reads and writes somebody else's board."""
    code, out, err = _az_run(cwd, "devops", "configure", "--list")
    if code != 0:
        return ("", ""), az_refusal("resolving the organization and project", code, out, err)
    defaults = {}
    for line in (out or "").splitlines():
        key, sep, value = line.partition("=")
        if sep:
            defaults[key.strip().lower()] = value.strip()
    org, project = defaults.get("organization", ""), defaults.get("project", "")
    if not org or not project:
        missing = " and ".join(n for n, v in (("organization", org), ("project", project))
                               if not v)
        return ("", ""), {
            "code": "sp-az-no-project", "exit": 2, "missing": missing,
            "message": f"backend 'azure-boards' has no default {missing} — run "
                       f"`az devops configure --defaults organization=https://dev.azure.com/"
                       f"<org> project=<project>`; no spec was read or written",
        }
    return (org, project), {}


AZ_REFUSAL_CASES = (
    # (label, az exit, stdout, stderr, expected code). `az` reports almost everything as
    # exit 1 and explains in stderr, so these are the literal stderr shapes its 2.6x
    # releases produce — a reworded release breaks the check rather than the refusal.
    ("no binary on PATH", AZ_MISSING, "", "", "sp-az-missing"),
    ("the azure-devops extension is not installed", 2, "",
     "ERROR: 'boards' is not in the 'az' command group. Run `az extension add --name "
     "azure-devops`.\n", "sp-az-extension-missing"),
    ("nobody logged in", 1, "",
     "ERROR: Before you can run Azure DevOps commands, you need to run the login command "
     "(az login if using AAD/MSA identity...).\n", "sp-az-unauthenticated"),
    ("an identity without access", 1, "",
     "ERROR: TF400813: The user 'x' is not authorized to access this resource.\n",
     "sp-az-unauthenticated"),
    ("a work item that is not there", 1, "",
     "ERROR: TF401232: Work item 4242 does not exist, or you do not have permissions to "
     "read it.\n", "sp-az-api-error"),
    # Captured VERBATIM from az 2.88 on 2026-08-01, by running `az boards query` in a
    # checkout with no defaults configured. It is the failure a first-time user actually
    # hits, and it is not an API error: nothing was asked of Azure DevOps at all.
    ("no organization configured", 1, "",
     "ERROR: --organization must be specified. The value should be the URI of your Azure "
     "DevOps organization, for example: https://dev.azure.com/MyOrganization/. You can set "
     "a default value by running: az devops configure --defaults "
     "organization=https://dev.azure.com/MyOrganization/.\n", "sp-az-no-project"),
)


SPEC_PRIMITIVES = ("list_specs", "read_spec", "write_spec", "create_spec", "move_spec")


def backend_completeness_failures() -> list[str]:
    """Every declared backend implements all five primitives — none left inherited.

    THIS IS WHAT `azure-boards` HAS INSTEAD OF END-TO-END PROOF. `## Out of Scope` accepts
    shipping it without a real Azure DevOps project to exercise, and `backend_equivalence_
    failures` cannot cover it: that check runs the canonical cases against two backends, and
    running them here would mean a network. What CAN be checked without a network is the
    failure a half-written backend actually takes — a primitive left inheriting the base
    class's `NotImplementedError`, which reaches a human as a traceback rather than as a
    refusal, breaking the one promise every external backend makes.

    Self-contained: reads the classes, calls nothing."""
    failures: list[str] = []
    for cls in (FilesBackend, MemoryBackend, GitHubBackend, AzureBoardsBackend):
        for primitive in SPEC_PRIMITIVES:
            if getattr(cls, primitive, None) is getattr(SpecBackend, primitive):
                failures.append(f"{cls.__name__} inherits `{primitive}` — it would raise "
                                f"NotImplementedError as a traceback")
        if getattr(cls, "name", "abstract") == "abstract":
            failures.append(f"{cls.__name__} never named itself — `name` is what a refusal "
                            f"and every report call it")
    return failures


def az_refusal_failures() -> list[str]:
    """Every `az` failure must arrive as its own exit-2 refusal, carrying the remedy that
    fixes THAT failure — never a traceback, and never the wrong remedy stated confidently.

    Self-contained: no network and no `az`. Asserted against the literal streams the CLI
    produces, because the split into remedies is made on what it said."""
    failures: list[str] = []
    for label, code, out, err, want in AZ_REFUSAL_CASES:
        got = az_refusal("reading a spec", code, out, err)
        if got.get("code") != want:
            failures.append(f"{label}: got {got.get('code')!r}, expected {want!r}")
        if got.get("exit") != 2:
            failures.append(f"{label}: exited {got.get('exit')!r}, every refusal is 2")
        if not str(got.get("message", "")).strip():
            failures.append(f"{label}: refused with an empty message")
    return failures


def unproved_backend_failures() -> list[str]:
    """The unproved-backend warning says its piece once, on stderr, and only for a backend
    that is actually declared unproved.

    Three ways this decision could ship broken, and all three are silent. A name misspelled
    in `UNPROVED_BACKENDS` matches no backend, so the warning never fires and the caveat is
    dead code that reads as coverage. A warning that repeats is the per-operation noise the
    decision rejected, arriving anyway. A warning on stdout breaks the `--json` parse of
    every caller, which is a worse failure than the one it was warning about.

    Self-contained: no network, no `az`, and the process-level flag is restored so the check
    cannot change what a later command prints."""
    import contextlib
    import io
    failures: list[str] = []
    for name in UNPROVED_BACKENDS:
        if name not in BACKENDS:
            failures.append(f"`{name}` is declared unproved and is not a backend — the "
                            f"warning it names can never fire")
    held = set(_UNPROVED_ANNOUNCED)
    _UNPROVED_ANNOUNCED.clear()
    try:
        for name, want in [(b, b in UNPROVED_BACKENDS) for b in BACKENDS]:
            err, out = io.StringIO(), io.StringIO()
            with contextlib.redirect_stderr(err), contextlib.redirect_stdout(out):
                announce_unproved(name)
                announce_unproved(name)
            said = err.getvalue().strip()
            if bool(said) != want:
                failures.append(f"{name}: warned={bool(said)!r}, expected {want!r}")
            if said.count("warning:") > 1:
                failures.append(f"{name}: warned twice in one process — the decision is one "
                                f"line per process, not one per operation")
            if out.getvalue():
                failures.append(f"{name}: wrote to stdout, which is the `--json` payload")
    finally:
        _UNPROVED_ANNOUNCED.clear()
        _UNPROVED_ANNOUNCED.update(held)
    return failures


class AzureBoardsBackend(SpecBackend):
    """Specs as Azure Boards work items, reached through `az boards` in a subprocess.

    ONE WORK ITEM IS ONE SPEC and ONE TASK IS ONE CHILD WORK ITEM — the same hybrid shape
    the `github` backend uses, through the same `hybrid_*` helpers, which is the point of
    those helpers having stopped being `gh_*`. Everything the two backends agree on is
    literally shared code rather than two implementations that must be kept in step.

    IT DERIVES NOTHING, exactly as `GitHubBackend` derives nothing: `derive_info` produces
    the stages, gates and records, and `parse_tasks` is the only thing that ever decides a
    task is checked or blocked.

    THE PHASE IS A DECLARED STATE, and this is the one place the two external backends
    genuinely differ. GitHub's open/closed is universal, so the mapping could be written in
    code. An Azure Boards state belongs to the project's process — Basic, Agile, Scrum and
    CMMI each name their states differently, and a customised process names them however it
    likes — so the mapping is read from `azureStates` in `.claude/quenching.json` and is
    NEVER guessed. Absent, the backend refuses (exit 2) naming the key: a guess would not
    fail loudly, it would silently report every archived spec as active.

    A state this tool did not write is read as `plans` — a work item moved to `Active` or
    `Resolved` by a human on the board is still in flight, and only the declared archive
    state means closed. That is the same one-way reading `github` gets from `state=closed`.

    The listing is fetched once per process and cached — a local cache and NOT a store:
    not authoritative, read by nothing outside this object, dropped on every write."""

    name = "azure-boards"

    def __init__(self, org: str, project: str, states: dict, cwd: str) -> None:
        self.org = org
        self.project = project
        self.states = states
        self.cwd = cwd
        self._rows: list[tuple[dict, int, str]] | None = None   # descriptor, id, shell doc

    # -- transport ---------------------------------------------------------- #
    def _az(self, action: str, *argv: str):
        """One `az boards` call, parsed. Raises `BackendRefusal` for every way it can fail.

        `--org` and `--project` on every call rather than relying on the configured
        defaults: resolution already read them once, and passing them explicitly means a
        human changing their `az` defaults mid-session cannot silently redirect a write to
        another project."""
        code, out, err = _az_run(self.cwd, "boards", *argv,
                                 "--org", self.org, "--output", "json")
        if code != 0:
            raise BackendRefusal(az_refusal(action, code, out, err))
        try:
            return json.loads(out or "null")
        except json.JSONDecodeError as e:
            raise BackendRefusal({
                "code": "sp-az-bad-response", "exit": 2, "action": action,
                "message": f"`az boards` exited 0 while {action} but its output is not "
                           f"JSON: {e}",
            }) from e

    def _field(self, item: dict, name: str) -> str:
        return str((item.get("fields") or {}).get(name, "") or "")

    def _phase_of(self, item: dict) -> str:
        return "archive" if self._field(item, "System.State") == self.states["archive"] \
            else "plans"

    # -- the listing, fetched once ------------------------------------------- #
    def _load(self) -> list[tuple[dict, int, str]]:
        if self._rows is not None:
            return self._rows
        # WIQL rather than a saved query: the filter is this tool's, not the project's, and
        # a saved query is one more thing a human has to create before the backend works.
        found = self._az("querying the project's work items", "query", "--project",
                         self.project, "--wiql",
                         "SELECT [System.Id] FROM WorkItems WHERE "
                         "[System.TeamProject] = @project") or []
        ids = [int(r.get("id") or (r.get("fields") or {}).get("System.Id") or 0)
               for r in found]
        rows: list[tuple[dict, int, str, str]] = []
        for item in self._show_many([i for i in ids if i]):
            filename, doc, _ = hybrid_unwrap(self._field(item, "System.Description"))
            m = SPEC_FILE_RE.match(filename)
            if not m:
                # An ordinary work item a human created. The marker is what tells a spec
                # apart from the project's real backlog, which this backend must never
                # list and must never write over.
                continue
            phase = self._phase_of(item)
            rows.append(({
                # The SAME key set `spec_files` returns and nothing more.
                "phase": phase, "folder": phase, "legacy": False, "file": filename,
                "path": f"{self.org.rstrip('/')}/{self.project}/_workitems/edit/"
                        f"{item.get('id')}",
                "slug": m.group(1),
            }, int(item.get("id") or 0), doc,
                self._field(item, "System.Title")))
        self._rows = rows
        return rows

    def _show_many(self, ids: list[int]) -> list[dict]:
        """Each work item's fields. One call per id — `az boards work-item show` takes a
        single id, and there is no batch form in the CLI. The cost is declared rather than
        hidden: it is why the listing is cached for the whole process."""
        return [self._az(f"reading work item {i}", "work-item", "show", "--id", str(i))
                for i in ids]

    def _invalidate(self) -> None:
        self._rows = None

    def _item_id(self, slug: str) -> int:
        for descriptor, item_id, _, _title in self._load():
            if descriptor["slug"] == slug:
                return item_id
        raise BackendRefusal({
            "code": "sp-az-item-gone", "exit": 2, "slug": slug,
            "message": f"spec '{slug}' was in the listing and is not there any more — the "
                       f"work item was deleted or moved while this command ran; nothing "
                       f"was written",
        })

    # -- the five primitives -------------------------------------------------- #
    def list_specs(self, phase: str | None = None) -> list[dict]:
        rows = [dict(d) for d, _, _, _ in self._load()
                if phase is None or d["phase"] == phase]
        return sorted(rows, key=lambda r: (PHASES.index(r["phase"]), r["file"]))

    def read_spec(self, slug: str) -> tuple[dict | None, dict]:
        rows = self._load()
        spec, err = resolve_one(self.list_specs(), slug,
                                {d["slug"]: t for d, _, _, t in rows})
        if err:
            return None, err
        _, full_text, native = next((i, d, t) for descriptor, i, d, t in rows
                                    if descriptor["slug"] == spec["slug"])
        return derive_info(spec, hybrid_title_join(full_text, native)), {}

    def write_spec(self, info: dict, text: str) -> None:
        announce_unproved(self.name)
        item_id = self._item_id(info["slug"])
        # `System.Description` has no published ceiling, so `hybrid_split` is handed None
        # and answers with the one chunk that is the whole document. The call is made anyway,
        # rather than skipped, so this backend goes through the SAME serialisation as the
        # proved one instead of a shorter path of its own that nothing checks.
        stored, title = hybrid_project(info["slug"], text)
        chunks = hybrid_split(stored, None)
        self._update(item_id, title=title,
                     description=hybrid_wrap(info["file"], chunks[0][0]))
        self._invalidate()

    def create_spec(self, phase: str, filename: str, text: str) -> str:
        announce_unproved(self.name)
        m = SPEC_FILE_RE.match(filename)
        stored, title = hybrid_project(m.group(1) if m else filename, text)
        item = self._az("creating a work item", "work-item", "create", "--project",
                        self.project, "--type", AZ_SPEC_TYPE,
                        "--title", title,
                        "--description", hybrid_wrap(filename,
                                                     hybrid_split(stored, None)[0][0]),
                        "--state", self.states[phase])
        item_id = int((item or {}).get("id") or 0)
        self._invalidate()
        return f"{self.org.rstrip('/')}/{self.project}/_workitems/edit/{item_id}"

    def move_spec(self, info: dict, dest_phase: str) -> str:
        announce_unproved(self.name)
        item_id = self._item_id(info["slug"])
        self._update(item_id, state=self.states[dest_phase])
        self._invalidate()
        return f"{self.org.rstrip('/')}/{self.project}/_workitems/edit/{item_id}"

    def _update(self, item_id: int, **fields: str):
        argv: list[str] = ["work-item", "update", "--id", str(item_id)]
        for key, value in fields.items():
            argv += [f"--{key}", value]
        return self._az(f"updating work item {item_id}", *argv)


# The work item type this backend creates. `Issue` exists in the Basic and Agile processes;
# Scrum and CMMI name their equivalent differently, which is the same process-dependence
# `azureStates` exists for. Left a constant rather than a fifth config key until a real Azure
# DevOps project says otherwise — `## Out of Scope` accepts that this backend ships without
# end-to-end proof, and inventing configuration for an unproven guess is worse than one named
# place to change.
#
# There is no second type any more: a spec was one work item plus one CHILD PER TASK until the
# `## Tasks`-as-children mapping was retired for the reasons at HYBRID SERIALISATION, and one
# work item now carries the whole document.
AZ_SPEC_TYPE = "Issue"


def open_azure_backend(root: str) -> tuple[SpecBackend | None, dict]:
    """The `azure-boards` backend for this workspace, or the refusal that says why not.

    Resolution happens HERE and not in the constructor, on the same "on demand" rule
    `open_backend` applies to the files worktree and the github backend: the round trip is
    paid by the first command that needs a spec, and the missing-binary, not-logged-in and
    nothing-declared refusals arrive at the START of a command rather than halfway through
    a write."""
    cwd = find_repo_root(root)
    cfg = load_config(root)
    states = cfg["azureStates"]
    if not states:
        return None, {
            "code": "sp-az-no-states", "exit": 2, "config": cfg["path"],
            "message": "backend 'azure-boards' needs the phase-to-state mapping declared in "
                       f"{CONFIG_FILE} — add "
                       '`"azureStates": {"plans": "<your active state>", "archive": '
                       '"<your closed state>"}`; an Azure Boards state is defined by the '
                       "project's process, so this tool never guesses it. No spec was read "
                       "or written",
        }
    (org, project), err = resolve_azure_project(cwd)
    if err:
        return None, err
    return AzureBoardsBackend(org, project, states, cwd), {}


def record_keys(schema: dict | None = None) -> list[str]:
    """The optional frontmatter records, in the schema's declared order.

    Read from the schema rather than listed here, so adding a record is a schema edit and
    never also a code edit — and so `status` cannot surface a different set than `validate`
    and the templates describe."""
    fmspec = (schema or load_schema()).get("frontmatter", {})
    return [k for k in fmspec.get("records", {}) if k != "note"] \
        or list(fmspec.get("optional", []))


def spec_records(fm: dict, schema: dict | None = None) -> dict:
    """Every declared record this spec actually carries, `None` where it does not.

    Reading the frontmatter top to bottom narrates the spec's history in order, so the
    order here is the schema's, not the file's."""
    return {k: (fm.get(k) or None) for k in record_keys(schema)}


def _policy(fm: dict) -> str:
    v = str(fm.get("verification", "")).strip().lower()
    return v if v in VERIFICATION_POLICIES else DEFAULT_VERIFICATION


def _gate_over(sections: dict, name: str, entry: list, warn_when_empty: list) -> dict:
    """Which of `entry` is absent or present-but-empty. `- none — <reason>` counts as
    filled and never appears here."""
    missing, malformed = [], []
    for h in entry:
        st = section_state(sections, h)
        if st == "absent":
            missing.append(h)
        elif st == "empty":
            malformed.append(h)
    warn = [h for h in warn_when_empty if section_state(sections, h) != "filled"]
    return {"phase": name, "missing": missing, "malformed": malformed,
            "warn": warn, "ok": not missing and not malformed}


def gate_report(info: dict, phase: str, schema: dict | None = None) -> dict:
    """What stands between this spec and `phase` — the entry gate of a real folder."""
    ph = phase_spec(phase, schema)
    return _gate_over(info["sections"], phase,
                      ph.get("entryGate", []), ph.get("warnWhenEmpty", []))


def ready_gate(schema: dict | None = None) -> dict:
    """The ready set, read from the ONE stage rule marked `gate: true`.

    v2 held these ten sections in the `ready/` phase's `entryGate`; v3 has no `ready/`
    folder, so the same set lives on the derived stage instead. It is read from the schema
    rather than restated here for the same reason it is not restated in schema.json: two
    declared sources of one fact diverge."""
    s = schema or load_schema()
    for r in s.get("stages", {}).get("derived", []):
        if r.get("gate"):
            return {"sections": list(r.get("when", {}).get("filled", [])),
                    "warnWhenEmpty": list(r.get("warnWhenEmpty", []))}
    return {"sections": [], "warnWhenEmpty": []}


def ready_report(info: dict, schema: dict | None = None) -> dict:
    """The ready gate applied to one spec. A FLOOR, not a verdict: nothing refuses on it
    any more — `execute` reports it and asks for the `approved` stamp inline."""
    g = ready_gate(schema)
    return _gate_over(info["sections"], "ready", g["sections"], g["warnWhenEmpty"])


# --------------------------------------------------------------------------- #
# output
# --------------------------------------------------------------------------- #
def display_locator(locator: str, root: str) -> str:
    """A backend's locator as a report should print it.

    `path` is the ONE field the backends are allowed to differ on — a filesystem path for
    `files`, an issue URL for `github` — and only one of the two is a path. Making a URL
    relative to the workspace produces a string that is neither, and that no reader can
    follow: `../../../https:/github.com/o/r/issues/2`. A remote locator is already the
    address a human would open, so it is printed exactly as the backend gave it."""
    if "://" in locator:
        return locator
    return os.path.relpath(locator, os.path.dirname(root)).replace(os.sep, "/")


def emit(as_json: bool, obj: dict, human: str) -> None:
    if as_json:
        print(json.dumps(obj, indent=2, ensure_ascii=False))
    else:
        print(human)


def emit_err(as_json: bool, err: dict) -> int:
    emit(as_json, {"ok": False, **{k: v for k, v in err.items() if k != "exit"}},
         f"error: {err['message']}")
    return err.get("exit", 1)


# --------------------------------------------------------------------------- #
# commands
# --------------------------------------------------------------------------- #
def cmd_new(args, root: str) -> int:
    """Scaffold `plans/<slug>.md` carrying `## Problem` and nothing else.

    THE DATE IS STAMPED HERE AND NEVER AGAIN, now into the frontmatter's `date:` rather than
    into the basename. `promote` moves the file without renaming it, so the basename — the
    bare slug — is the spec's identity for its whole lifecycle, and the date is a fact the
    document carries instead of a fact its name encodes."""
    slug = slugify(args.name)
    if not SLUG_RE.match(slug):
        emit(args.json, {"ok": False, "code": "sp-bad-slug", "slug": args.name,
                         "message": f"'{args.name}' does not reduce to a kebab-case slug"},
             f"error: '{args.name}' does not reduce to a kebab-case slug")
        return 2
    backend, err = open_backend(root)
    if err:
        return emit_err(args.json, err)
    # Asked of the backend, not of the filesystem: a slug already taken in GitHub must
    # refuse here exactly as one already taken on disk does.
    matches = [s for s in backend.list_specs() if s["slug"] == slug]
    if matches:
        m = matches[0]
        emit(args.json, {"ok": False, "code": "sp-slug-exists", "slug": slug,
                         "existing": f"{m['folder']}/{m['file']}",
                         "message": f"slug '{slug}' already exists at {m['folder']}/{m['file']}"},
             f"refused: slug '{slug}' already exists at {m['folder']}/{m['file']}")
        return 2
    policy = args.verification or DEFAULT_VERIFICATION
    title = args.title or titleize(slug)
    name = f"{slug}.md"
    body = (capture_form()
            .replace("<SLUG>", slug)
            .replace("<TITLE>", title)
            .replace("<DATE>", today())
            .replace("<VERIFICATION>", policy))
    path = backend.create_spec("plans", name, body)
    emit(args.json,
         {"ok": True, "slug": slug, "title": title, "verification": policy,
          "phase": "plans", "folder": "plans", "file": name, "stage": "captured",
          "path": display_locator(path, root)},
         f"created plans/{name}  (slug: {slug} · verification: {policy})\n"
         f"next: write ## Problem, then `specs.py section {slug} Proposal --write`")
    return 0


def cmd_list(args, root: str) -> int:
    backend, err = open_backend(root)
    if err:
        return emit_err(args.json, err)
    specs = backend.list_specs()
    rows = []
    for s in specs:
        # ASKED OF THE BACKEND, never of the path. This was the last command reading
        # `read_text(s["path"])` directly, which worked only because the files backend's
        # locator happens to be a filesystem path — against GitHub it is an issue URL, and
        # `list` would have reported every spec as empty rather than failing.
        info, rerr = backend.read_spec(s["slug"])
        if rerr or info is None:
            # The only refusal reachable here is an ambiguous slug — the slug came from the
            # listing, so it cannot be unknown — and `list` is exactly the command a human
            # runs to SEE that duplicate. The row survives, derived from an empty document
            # so every field still comes from the one shared derivation, and `unreadable`
            # says so rather than letting the spec look empty. `validate` names it
            # sp-duplicate-slug.
            info, unreadable = derive_info(s, ""), (rerr or {}).get("code")
        else:
            unreadable = None
        checked, blocked, total = task_progress(info["tasks"])
        rows.append({
            "slug": s["slug"], "phase": s["phase"], "folder": s["folder"],
            "legacy": s["legacy"], "file": s["file"], "date": info["date"],
            "title": info["frontmatter"].get("title", titleize(s["slug"])),
            "stage": info["stage"],
            "outcome": info["frontmatter"].get("outcome") or None,
            # The seven records, on every row. Without them a caller that wants the front's
            # rankings — `triage` reading `priority`, `status` narrating a spec's history —
            # has to open each file itself, which is a path read and so only works while the
            # backend happens to be `files`.
            "records": spec_records(info["frontmatter"]),
            "unreadable": unreadable,
            "tasks": {"checked": checked, "blocked": blocked, "total": total},
        })
    if args.json:
        print(json.dumps({"ok": True, "root": root, "count": len(rows), "specs": rows},
                         indent=2, ensure_ascii=False))
        return 0
    if not rows:
        print(f"no specs under {root}")
        return 0
    print(f"specs — {root} ({len(rows)})")
    for folder in PHASE_DIRS:
        group = [r for r in rows if r["folder"] == folder]
        if not group:
            continue
        legacy = " (v2 — `specs.py migrate` folds it into plans/)" \
            if folder in LEGACY_PHASES else ""
        print(f"\n  {folder}/{legacy}")
        for r in group:
            prog = (f"  {r['tasks']['checked']}/{r['tasks']['total']}"
                    if r["tasks"]["total"] else "")
            blk = f" · {r['tasks']['blocked']} blocked" if r["tasks"]["blocked"] else ""
            oc = f" · {r['outcome']}" if r["outcome"] else ""
            un = f" · {r['unreadable']} (nothing derived)" if r["unreadable"] else ""
            print(f"    {r['date']}  {r['slug']:<28} [{r['stage']}]{prog}{blk}{oc}{un}")
    return 0


def _next_phase(phase: str, schema: dict | None = None) -> str | None:
    seq = (schema or load_schema()).get("promote", {}).get("sequence", list(PHASES))
    return seq[seq.index(phase) + 1] if phase in seq and seq.index(phase) + 1 < len(seq) else None


def cmd_status(args, root: str) -> int:
    backend, err = open_backend(root)
    if err:
        return emit_err(args.json, err)
    info, err = backend.read_spec(args.spec)
    if err:
        return emit_err(args.json, err)
    checked, blocked, total = task_progress(info["tasks"])
    dest = _next_phase(info["phase"])
    gates = gate_report(info, dest) if dest else None
    ready = ready_report(info) if info["phase"] == "plans" else None
    sections = [{"heading": h, "state": section_state(info["sections"], h)}
                for h in canonical_headings()]
    records = spec_records(info["frontmatter"])
    obj = {
        "ok": True, "slug": info["slug"], "title": info["frontmatter"].get("title", ""),
        "phase": info["phase"], "folder": info["folder"], "legacy": info["legacy"],
        "stage": info["stage"], "file": info["file"],
        "date": info["date"], "verification": info["verification"],
        # How the slug was reached, when it was not reached exactly. `null` on the ordinary
        # path. A caller that acts on a spec the human did not name has to be able to see
        # that it happened — the resolution is tolerant, and tolerance without a receipt is
        # just a wrong answer delivered confidently.
        "resolvedBy": info.get("resolvedBy"), "resolvedFrom": info.get("resolvedFrom"),
        # every human-judgment record in one place and in schema order, so `conclude` and
        # `continue` read state instead of re-parsing the file
        "records": records,
        "ready": ready,
        "sections": sections,
        "strays": stray_headings(info["sections"]),
        "tasks": {"checked": checked, "blocked": blocked, "total": total,
                  "blockedTasks": [{"id": t["id"], "text": t["text"], "reason": t["reason"]}
                                   for t in info["tasks"] if t["blocked"]],
                  "subjects": [{"id": t["id"], "subject": t["subject"]}
                               for t in info["tasks"] if t["subject"]],
                  "commits": [{"id": t["id"], "commit": t["commit"]}
                              for t in info["tasks"] if t["commit"]]},
        "promote": gates,
    }
    if args.json:
        print(json.dumps(obj, indent=2, ensure_ascii=False))
        return 0
    print(f"{info['slug']} — {obj['title']}")
    print(f"  {info['folder']}/{info['file']}  [{info['stage']}]  "
          f"verification: {info['verification']}")
    if total:
        print(f"  tasks: {checked}/{total} complete" +
              (f" · {blocked} blocked" if blocked else ""))
    for s in sections:
        mark = {"filled": "✓", "empty": "!", "absent": "·"}[s["state"]]
        print(f"    {mark} ## {s['heading']}")
    if obj["strays"]:
        print(f"  strays: {', '.join(obj['strays'])}")
    if ready:
        if not ready["ok"]:
            print(f"  ready gate: missing {', '.join(ready['missing'] + ready['malformed'])}")
        elif not records.get("approved"):
            print("  ready gate: met — not approved (execute stamps `approved:` inline)")
        else:
            print(f"  ready gate: met · approved {records['approved']}")
    held = [(k, v) for k, v in records.items() if v]
    if held:
        print("  records:")
        for k, v in held:
            if isinstance(v, dict):
                v = ", ".join(f"{kk}: {vv}" for kk, vv in v.items())
            print(f"    {k + ':':<10} {v}")
    if obj["tasks"]["subjects"]:
        print(f"  subjects: {len(obj['tasks']['subjects'])} task(s) carry one")
    if obj["tasks"]["commits"]:
        print(f"  commits: {len(obj['tasks']['commits'])} task(s) carry an older sha")
    if gates:
        if gates["ok"]:
            print(f"  promote → {dest}/: ready")
        else:
            if gates["missing"]:
                print(f"  promote → {dest}/: missing {', '.join(gates['missing'])}")
            if gates["malformed"]:
                print(f"  promote → {dest}/: empty (malformed) {', '.join(gates['malformed'])}")
    return 0


def _canonical_index(heading: str, schema: dict | None = None) -> int:
    canon = canonical_headings(schema)
    return canon.index(heading) if heading in canon else len(canon)


def resolve_heading_name(name: str, candidates: list[str]) -> str | None:
    """One requested name onto the candidate that answers it, or None.

    **`§X` and `## X` are the same request, and a UNIQUE prefix resolves** — the two forms
    `SECTION_CASES` pins, which `skills.py` carries verbatim. The command bodies already cite
    sections as `§Handoff`, so a reader that refused over the marker would be unusable from the
    very prose it serves. An ambiguous prefix resolves to nothing: a guess between two headings is
    worse than the refusal that names them.

    It takes the candidate list as an argument for one reason — so the canonical cases exercise
    THIS function over the fixture's headings, rather than a second copy of the rule written
    inside the selftest. A rule proved against a private re-implementation is not proved."""
    want = " ".join(name.strip().lstrip("#§").strip().split()).lower()
    if not want:
        return None
    for c in candidates:
        if c.lower() == want:
            return c
    hits = [c for c in candidates if c.lower().startswith(want)]
    return hits[0] if len(hits) == 1 else None


def _match_heading(heading: str) -> str | None:
    """Case-insensitive lookup onto the canonical spelling. Headings are a parsed contract,
    so the FILE always carries canonical English — but a human typing `specs.py section x
    validation` should not get a stray section for their trouble."""
    return resolve_heading_name(heading, canonical_headings())


def upsert_section(info: dict, heading: str, block: str) -> tuple[str, str]:
    """Replace a section's block, or create it in CANONICAL POSITION when absent.

    Position is derived from the schema's declared order, not from where the writer
    happened to be: a spec whose `## Tasks` was written before its `## Proposal` still
    reads in contract order, so a human and the parser see the same document."""
    text = info["text"]
    lines = text.splitlines(keepends=True)
    # sections were parsed from the body, so their line numbers need the frontmatter back
    fm_offset = len(lines) - len(body_after_frontmatter(text).splitlines(keepends=True))
    if heading in info["sections"]:
        sec = info["sections"][heading]
        start = sec["lineno"] + fm_offset
        end = start + 1 + len(sec["lines"])
        return "".join(lines[:start]) + block + "".join(lines[end:]), "replaced"
    idx = _canonical_index(heading)
    following = [sec["lineno"] + fm_offset for h, sec in info["sections"].items()
                 if _canonical_index(h) > idx]
    if following:
        at = min(following)
        return "".join(lines[:at]) + block + "\n" + "".join(lines[at:]), "created"
    return text.rstrip() + "\n\n" + block, "created"


SECTION_FIXTURE = '''---
type: standard
title: the section reader's fixture
---

# Top

Preamble under a level-1 heading.

## Alpha

Alpha body.

### Alpha sub

Sub body that belongs to Alpha.

## Beta

Beta opens with a fenced block whose lines look like headings:

```bash
## not a heading
### also not a heading
```

Beta continues after the fence.

## Gamma

~~~
## fenced by tildes
~~~

Gamma ends the file.
'''

# The canonical case list for the SECTION rule, duplicated verbatim in `skills.py`.
# EDIT BOTH, OR NEITHER — exactly as `CANONICAL_CASES` is duplicated across all three
# tools for the frontmatter rule. Neither script may import the other: each installs
# standalone into a target's `.claude/hooks/`, so the list travelling with each copy is
# what makes the rule provable where it actually runs.
#
# It covers only what BOTH tools answer the same way: level-2 sections. A spec's
# fourteen headings are all `##`, so that is the whole of `specs.py`'s contract, while
# `skills.py` also resolves `#` and `###` over free markdown and proves those separately.
# The names here are deliberately NOT canonical spec headings: what this list pins is the
# sectioning rule, not `_match_heading`'s vocabulary, which is `specs.py`'s alone.
SECTION_CASES = {
    "index": ["Alpha", "Beta", "Gamma"],
    "cases": [
        {"why": "sub-headings travel with their parent, and the section stops at the "
                "next heading of the same level",
         "ask": ["Alpha"],
         "contains": ["Alpha body.", "### Alpha sub", "Sub body that belongs to Alpha."],
         "excludes": ["Beta continues"]},
        {"why": "a fenced block containing `## ` never splits the section",
         "ask": ["Beta"],
         "contains": ["## not a heading", "Beta continues after the fence."],
         "excludes": ["Gamma ends"]},
        {"why": "tilde fences count too, and the last section runs to end of file",
         "ask": ["Gamma"],
         "contains": ["## fenced by tildes", "Gamma ends the file."],
         "excludes": []},
        {"why": "the citation form the bodies already use resolves: `§X` and `## X` "
                "are the same request, and N sections come back in the order asked",
         "ask": ["§Gamma", "## Alpha"],
         "contains": ["Gamma ends the file.", "Alpha body."],
         "excludes": [],
         "order": ["Gamma", "Alpha"]},
        {"why": "neither frontmatter nor the preamble above the first section ever "
                "leaks into a section that does not own it",
         "ask": ["Alpha", "Beta", "Gamma"],
         "contains": [],
         "excludes": ["type: standard", "Preamble under a level-1 heading."]},
        {"why": "a unique prefix resolves, so a citation need not reproduce a long "
                "heading's punctuation",
         "ask": ["Gam"],
         "contains": ["Gamma ends the file."],
         "excludes": []},
        {"why": "a section that does not exist is a refusal that names it, never an "
                "empty answer",
         "ask": ["Delta"],
         "missing": ["Delta"]},
    ],
}


def _section_case_rows(text: str) -> list[dict]:
    """This tool's arm of the canonical list: `parse_sections` itself, addressed by name.

    It goes through `parse_sections` and not through `cmd_section`, because the canonical
    list pins the SECTIONING rule — where a section starts and stops — while `cmd_section`
    additionally refuses a heading outside the fourteen. Running the list through the
    canonical filter would prove the filter and leave the rule untested."""
    return [{"heading": h, "level": 2, "body": v["body"]}
            for h, v in parse_sections(text).items()]


def section_case_failures() -> list[str]:
    """Run `SECTION_CASES` against this tool's own sectioning rule."""
    out: list[str] = []
    rows = _section_case_rows(SECTION_FIXTURE)
    heads = [r["heading"] for r in rows]
    if heads != SECTION_CASES["index"]:
        out.append(f"heading index is {heads}, expected {SECTION_CASES['index']} — a "
                   f"fenced line was read as a heading, or a heading was missed")
    # `resolve_heading_name` is the SAME function `_match_heading` runs in production, handed the
    # fixture's headings instead of the canonical fourteen. That is what makes the `\u00a7X` and
    # unique-prefix cases evidence about this tool rather than about the selftest.
    index = {r["heading"]: r for r in rows}
    for case in SECTION_CASES["cases"]:
        got, missing = [], []
        for name in case["ask"]:
            hit = resolve_heading_name(name, list(index))
            (got.append(index[hit]) if hit else missing.append(name))
        want_missing = case.get("missing", [])
        if missing != want_missing:
            out.append(f"{case['ask']}: missing is {missing}, expected {want_missing} "
                       f"— {case['why']}")
            continue
        if want_missing:
            continue
        body = "\n".join(f"## {r['heading']}\n{r['body']}" for r in got)
        for needle in case["contains"]:
            if needle not in body:
                out.append(f"{case['ask']}: missing {needle!r} — {case['why']}")
        for needle in case["excludes"]:
            if needle in body:
                out.append(f"{case['ask']}: leaked {needle!r} — {case['why']}")
        if "order" in case and [r["heading"] for r in got] != case["order"]:
            out.append(f"{case['ask']}: order is {[r['heading'] for r in got]}, expected "
                       f"{case['order']} — {case['why']}")
    return out


def cmd_section(args, root: str) -> int:
    """Deterministic partial read/write of N sections — what makes lean agent context real.

    An executor is handed a task line and `## Handoff`, never the whole spec; this is the
    command that slices it without an LLM re-reading and rewriting the file.

    **The read form is plural, and that is half the saving, not a convenience.** Every turn
    re-sends the whole conversation, so a cost has two factors — tokens AND the turns that
    follow it. Six headings fetched over six turns can lose to the one `Read` this command
    replaced. Comma-separated, one call, back in the order asked.

    `--write` stays singular: it takes stdin, and there is no unambiguous way to split one
    stream across several sections.

    The document comes from the BACKEND, never from a path: this is the reader every other
    front calls, so a backend that could not serve it would leave the whole surface tied to
    `files`."""
    backend, err = open_backend(root)
    if err:
        return emit_err(args.json, err)
    info, err = backend.read_spec(args.spec)
    if err:
        return emit_err(args.json, err)
    if args.moment:
        wanted = headings_for_moment(args.moment)
        if not wanted:
            emit(args.json,
                 {"ok": False, "code": "sp-unknown-moment", "moment": args.moment,
                  "message": f"no canonical section declares moment '{args.moment}'"},
                 f"error: no canonical section declares moment '{args.moment}'")
            return 2
    else:
        wanted = [h for h in (p.strip() for p in (args.heading or "").split(",")) if h]
        if not wanted:
            emit(args.json,
                 {"ok": False, "code": "sp-no-heading",
                  "message": "give a heading, or --moment, to read"},
                 "error: give a heading, or --moment, to read")
            return 2
    headings, stray = [], []
    for name in wanted:
        h = _match_heading(name)
        (headings.append(h) if h else stray.append(name))
    if stray:
        emit(args.json,
             {"ok": False, "code": "sp-stray-heading", "heading": stray[0],
              "stray": stray, "canonical": canonical_headings(),
              "message": f"not one of the fourteen canonical headings: {', '.join(stray)}"},
             f"error: not a canonical heading: {', '.join(stray)}")
        return 2
    if args.write and len(headings) != 1:
        emit(args.json,
             {"ok": False, "code": "sp-write-plural", "stray": headings,
              "message": "--write takes exactly one heading — stdin is one stream"},
             "error: --write takes exactly one heading")
        return 2
    if not args.write:
        rows = [{"heading": h, "state": section_state(info["sections"], h),
                 "body": info["sections"].get(h, {}).get("body", "")} for h in headings]
        absent = [r["heading"] for r in rows if r["state"] == "absent"]
        if args.json:
            one = rows[0] if len(rows) == 1 else {}
            print(json.dumps({"ok": not absent, "slug": info["slug"],
                              **one, "sections": rows, "absent": absent},
                             indent=2, ensure_ascii=False))
        else:
            for r in rows:
                if r["state"] == "absent":
                    print(f"(## {r['heading']} is absent)")
                elif len(rows) == 1:
                    print(r["body"].strip())
                else:
                    print(f"## {r['heading']}\n\n{r['body'].strip()}\n")
        return 0 if not absent else 1
    heading = headings[0]

    content = sys.stdin.read() if not sys.stdin.isatty() else ""
    block = (f"## {heading}\n\n{content.strip()}\n"
             if content.strip() else section_guidance(heading))
    new_text, action = upsert_section(info, heading, block)
    backend.write_spec(info, new_text)
    emit(args.json,
         {"ok": True, "slug": info["slug"], "heading": heading, "action": action,
          "path": display_locator(info["path"], root)},
         f"{action} ## {heading} in {info['phase']}/{info['file']}")
    return 0


def set_frontmatter_key(text: str, key: str, value: str,
                        after: str | None = None) -> str:
    """Set one top-level frontmatter key, preserving every other line as authored.

    Rewriting the block wholesale would reformat a human's `refined: {mode, date}` and
    reorder their keys — a promote is a move, and the outcome stamp is the ONLY content it
    is allowed to write.

    `after` places a key that does not exist yet directly below a named one, instead of at
    the end of the block. It exists for `date`, which the marker fold inserts into documents
    written before the field did: appended, it would land under `verification` and every
    migrated spec would read in a different order from every freshly captured one, for no
    reason a reader could see. An absent `after` key falls back to the end."""
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        return f"---\n{key}: {value}\n---\n\n" + text
    close = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
    if close is None:
        return text
    for i in range(1, close):
        if lines[i].split(":", 1)[0].strip() == key:
            lines[i] = f"{key}: {value}\n"
            return "".join(lines)
    at = close
    if after:
        for i in range(1, close):
            if lines[i].split(":", 1)[0].strip() == after:
                at = i + 1
                break
    lines.insert(at, f"{key}: {value}\n")
    return "".join(lines)


def legacy_marker_fold(filename: str, text: str) -> tuple[str, str] | None:
    """`("<slug>.md", the document carrying its own `date:`)` for a spec still stored under
    the dated basename — or None when there is nothing to fold.

    THE PREFIX IS THE ONLY COPY OF THE DATE. A document written before `date:` existed keeps
    its capture date nowhere but that basename, so the fold has to move it into the
    frontmatter in the SAME step that drops it. Dropping first loses the fact; adding first
    and dropping later leaves two copies free to disagree in between. One function, both
    halves, so no caller can perform half of it.

    A document that already declares `date:` keeps its own — only the name was stale. The
    basename's copy is never allowed to win, because a human may have corrected the field and
    nobody ever renames an issue's marker to correct a date."""
    m = LEGACY_DATED_FILE_RE.match(filename)
    if not m:
        return None
    date, slug = m.group(1), m.group(2)
    if str(parse_frontmatter(text).get("date", "")).strip():
        return f"{slug}.md", text
    return f"{slug}.md", set_frontmatter_key(text, "date", date, after="title")


def _render_record(key: str, rec: dict) -> list[str]:
    """A record as frontmatter lines — flow where flow survives a round trip, block where
    it would not. A value carrying a comma cannot go in `{a: b, c: d}`, which
    `parse_frontmatter` splits on commas; a long one wraps in an editor and stops parsing
    as one line. Both are the block form's whole reason to exist."""
    parts = [f"{k}: {v}" for k, v in rec.items()]
    line = f"{key}: {{{', '.join(parts)}}}"
    if len(line) <= 96 and not any("," in str(v) for v in rec.values()):
        return [line + "\n"]
    return [f"{key}:\n"] + [f"  {p}\n" for p in parts]


def set_frontmatter_record(text: str, key: str, rec: dict) -> str:
    """Replace ONE record, its continuation lines included, preserving every other line.

    `set_frontmatter_key` cannot do this: a record already written in block form occupies
    lines the single-line replacement would leave orphaned below the new value, where they
    would parse as a second record's fields."""
    new_lines = _render_record(key, rec)
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        return "---\n" + "".join(new_lines) + "---\n\n" + text
    close = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
    if close is None:
        return text
    for i in range(1, close):
        if lines[i][:1] in (" ", "\t") or ":" not in lines[i]:
            continue
        if lines[i].split(":", 1)[0].strip() != key:
            continue
        end = i + 1
        while end < close and lines[end][:1] in (" ", "\t") and lines[end].strip():
            end += 1
        return "".join(lines[:i] + new_lines + lines[end:])
    return "".join(lines[:close] + new_lines + lines[close:])


def cmd_verification(args, root: str) -> int:
    """Read ONE spec's verification policy, or set it — through the backend, after capture.

    THE ONLY WRITER USED TO BE `new --verification`, and that is the one moment nobody has an
    opinion: the policy answers how long THIS repo's suite takes and whether a section is the
    smallest safe unit, which is what `/quenching:specs:develop`'s gate bank exists to ask.
    With no writer after capture that bank could only land its answer by editing the
    frontmatter by hand — which needs a file, and an external backend has none. So under
    `github` the policy was decidable exactly once, before anyone knew the answer, and
    unchangeable afterwards.

    It is NOT a `record`: the seven records are `{field: value}` judgments with their own
    write-once rules, and this is a declared scalar with a closed value set. Folding it into
    `record` would have meant inventing a one-field record and a `value=` field name for it."""
    backend, err = open_backend(root)
    if err:
        return emit_err(args.json, err)
    info, err = backend.read_spec(args.spec)
    if err:
        return emit_err(args.json, err)
    declared = str(info["frontmatter"].get("verification", "")).strip().lower()

    if not args.policy:
        emit(args.json,
             {"ok": True, "slug": info["slug"], "verification": info["verification"],
              "declared": declared or None, "default": DEFAULT_VERIFICATION},
             f"{info['slug']} — verification: {info['verification']}"
             + ("" if declared else "  (the default — nothing declared)"))
        return 0

    policy = args.policy.strip().lower()
    if policy not in VERIFICATION_POLICIES:
        emit(args.json,
             {"ok": False, "code": "sp-bad-verification", "slug": info["slug"],
              "given": args.policy, "policies": list(VERIFICATION_POLICIES),
              "message": f"'{args.policy}' is not one of "
                         f"{', '.join(VERIFICATION_POLICIES)}"},
             f"error: '{args.policy}' is not one of {', '.join(VERIFICATION_POLICIES)}")
        return 2
    backend.write_spec(info, set_frontmatter_key(info["text"], "verification", policy))
    emit(args.json,
         {"ok": True, "slug": info["slug"], "verification": policy,
          "previous": declared or None},
         f"{info['slug']} — verification: {policy}"
         + (f"  (was {declared})" if declared and declared != policy else ""))
    return 0


def cmd_record(args, root: str) -> int:
    """Read or merge ONE frontmatter record, through the backend.

    The seven records were the last thing the command surface wrote by editing the file at
    its path — `triage` stamping `priority`, `isolate` stamping `branch`, `conclude`
    stamping `merge`. That is a path write, so it worked only while the backend happened to
    be `files`; against GitHub there is no file to edit.

    Which records exist, which fields each declares and which are write-once all come from
    the schema, so adding a record stays a schema edit. A record declaring no `fields:` is
    not writable here at all — that is `outcome`, whose one writer is `promote --outcome`,
    and it falls out of the declaration rather than being named in the code."""
    schema = load_schema()
    declared = schema.get("frontmatter", {}).get("records", {})
    if args.name not in record_keys(schema):
        emit(args.json,
             {"ok": False, "code": "sp-unknown-record", "record": args.name,
              "declared": record_keys(schema),
              "message": f"'{args.name}' is not a declared record — the declared ones are "
                         f"{', '.join(record_keys(schema))}"},
             f"error: '{args.name}' is not a declared record")
        return 2
    rspec = declared.get(args.name, {})
    fields = list(rspec.get("fields", []))

    backend, err = open_backend(root)
    if err:
        return emit_err(args.json, err)
    info, err = backend.read_spec(args.spec)
    if err:
        return emit_err(args.json, err)
    current = info["frontmatter"].get(args.name) or None

    if not args.set:
        if args.json:
            print(json.dumps({"ok": current is not None, "slug": info["slug"],
                              "record": args.name, "value": current},
                             indent=2, ensure_ascii=False))
        else:
            print(f"{args.name}: {current}" if current is not None
                  else f"({args.name}: is unset)")
        return 0 if current is not None else 1

    if not fields:
        emit(args.json,
             {"ok": False, "code": "sp-record-not-writable", "record": args.name,
              "writtenBy": rspec.get("writtenBy", ""),
              "message": f"`{args.name}:` declares no fields — its one writer is "
                         f"{rspec.get('writtenBy', 'another command')}"},
             f"refused: `{args.name}:` is not written through this command")
        return 2
    if rspec.get("writeOnce") and current:
        emit(args.json,
             {"ok": False, "code": "sp-record-write-once", "record": args.name,
              "current": current,
              "message": f"`{args.name}:` is write-once and already reads {current} — a "
                         f"record that disagrees with reality is a finding to report, "
                         f"never a value to overwrite"},
             f"refused: `{args.name}:` is already set to {current}")
        return 2

    merged = dict(current) if isinstance(current, dict) else {}
    for pair in args.set:
        k, sep, v = pair.partition("=")
        k, v = k.strip(), v.strip()
        if not sep or k not in fields:
            emit(args.json,
                 {"ok": False, "code": "sp-unknown-record-field", "record": args.name,
                  "given": pair, "fields": fields,
                  "message": f"expected `field=value` with field one of "
                             f"{', '.join(fields)} — got '{pair}'"},
                 f"error: expected `field=value` for `{args.name}:` — got '{pair}'")
            return 2
        merged[k] = v
    # The schema's field order, so a record reads the same however it was assembled and a
    # re-stamp never reshuffles what a human wrote.
    ordered = {k: merged[k] for k in fields if k in merged}
    backend.write_spec(info, set_frontmatter_record(info["text"], args.name, ordered))
    emit(args.json,
         {"ok": True, "slug": info["slug"], "record": args.name, "value": ordered},
         f"{info['slug']} — {args.name}: "
         f"{{{', '.join(f'{k}: {v}' for k, v in ordered.items())}}}")
    return 0


def record_round_trip_failures() -> list[str]:
    """Every record this tool writes must read back as what was written.

    A record is written once and read by every later command, so a serialisation that
    round-trips for the short values and silently truncates a long or comma-carrying one
    fails months later, on the spec that finally had a subject with a comma in it — and it
    fails as a record that reads *plausibly*, missing only its tail."""
    failures: list[str] = []
    base = "---\nslug: alpha\ntitle: Alpha\nverification: per-task\n---\n\n## Problem\n\nx\n"
    cases = {
        "short": {"level": "1", "criticality": "high"},
        "comma": {"strategy": "merge-commit", "subject": "plan/a: merge, then tidy"},
        "long": {"strategy": "merge-commit",
                 "subject": "plan/a-rather-long-slug-name-here: merge (merge-commit) " +
                            "carrying every task"},
    }
    for label, rec in cases.items():
        text = set_frontmatter_record(base, "priority", rec)
        got = parse_frontmatter(text).get("priority")
        if got != rec:
            failures.append(f"{label}: wrote {rec!r}, read back {got!r}")
        for k, v in (("slug", "alpha"), ("title", "Alpha"), ("verification", "per-task")):
            if parse_frontmatter(text).get(k) != v:
                failures.append(f"{label}: writing a record lost `{k}: {v}`")

    # Block -> flow, the shape that orphans lines: the block form's fields sit on their own
    # lines, and replacing only the `key:` line would leave them below the new value, where
    # they parse as fields of whatever record comes next.
    blocked = set_frontmatter_record(base, "merge", cases["comma"])
    reflowed = set_frontmatter_record(blocked, "merge", {"strategy": "rebase"})
    if parse_frontmatter(reflowed).get("merge") != {"strategy": "rebase"}:
        failures.append("re-stamping a block record left its old fields behind: "
                        f"{parse_frontmatter(reflowed).get('merge')!r}")
    return failures


def cmd_promote(args, root: str) -> int:
    """The one remaining transition: `plans/` -> `archive/`, closing a spec out.

    v3 has a single hop. The `backlog/` -> `ready/` promote is gone with the folders — it
    recorded that a human said go, and that is now `approved:` in frontmatter, which no
    file move is needed to express. What is left refuses (exit 2) with the missing list
    rather than warning, because a gate that warns is not a gate.

    The file is MOVED, never renamed: the date prefix was stamped at capture and the
    basename is the spec's identity for its whole lifecycle. Git detects the rename by
    content, so `git log --follow` reads as one history without this tool shelling out."""
    backend, err = open_backend(root)
    if err:
        return emit_err(args.json, err)
    info, err = backend.read_spec(args.spec)
    if err:
        return emit_err(args.json, err)
    dest = args.to or _next_phase(info["phase"])
    if not dest:
        emit(args.json,
             {"ok": False, "code": "sp-terminal-phase", "slug": info["slug"],
              "phase": info["phase"],
              "message": f"'{info['slug']}' is already in {info['phase']}/ — nowhere to promote"},
             f"refused: '{info['slug']}' is already in {info['phase']}/")
        return 2
    if dest not in PHASES:
        emit(args.json, {"ok": False, "code": "sp-unknown-phase", "phase": dest,
                         "message": f"'{dest}' is not a phase folder"},
             f"error: '{dest}' is not a phase folder")
        return 2
    if dest == info["phase"]:
        emit(args.json,
             {"ok": False, "code": "sp-same-phase", "slug": info["slug"], "phase": dest,
              "message": f"'{info['slug']}' is already in phase {dest}"},
             f"refused: '{info['slug']}' is already in phase {dest}")
        return 2

    gates = gate_report(info, dest)
    if not gates["ok"]:
        obj = {"ok": False, "code": "sp-gate-unmet", "slug": info["slug"],
               "from": info["phase"], "to": dest,
               "missing": gates["missing"], "malformed": gates["malformed"],
               "message": f"cannot promote '{info['slug']}' to {dest}/ — "
                          f"{len(gates['missing'])} missing, {len(gates['malformed'])} empty"}
        human = [f"refused: cannot promote '{info['slug']}' to {dest}/"]
        if gates["missing"]:
            human += [f"  missing:   ## {h}" for h in gates["missing"]]
        if gates["malformed"]:
            human += [f"  empty:     ## {h}  (write `- none — <reason>` or fill it)"
                      for h in gates["malformed"]]
        emit(args.json, obj, "\n".join(human))
        return 2

    outcome = None
    if dest == "archive":
        outcome = args.outcome or "done"
        if outcome not in OUTCOMES:
            emit(args.json, {"ok": False, "code": "sp-bad-outcome", "outcome": outcome,
                             "message": f"--outcome must be one of {', '.join(OUTCOMES)}"},
                 f"error: --outcome must be one of {', '.join(OUTCOMES)}")
            return 2
        # An abandoned spec is EXPECTED to have open tasks — refusing there would make
        # every abandonment a forced promote. Only `done` has to be true.
        open_tasks = [t for t in info["tasks"] if not t["checked"]]
        if outcome == "done" and open_tasks and not args.force:
            emit(args.json,
                 {"ok": False, "code": "sp-open-tasks", "slug": info["slug"],
                  "open": len(open_tasks), "total": len(info["tasks"]),
                  "openTasks": [{"id": t["id"], "text": t["text"], "state": t["state"]}
                                for t in open_tasks],
                  "message": f"{len(open_tasks)} of {len(info['tasks'])} tasks still open — "
                             f"pass --force, or --outcome abandoned"},
                 f"refused: {len(open_tasks)} of {len(info['tasks'])} tasks still open in "
                 f"'{info['slug']}'\n" +
                 "\n".join(f"  [{t['state']}] {t['text'][:70]}" for t in open_tasks[:8]) +
                 "\n  pass --force to archive anyway, or --outcome abandoned")
            return 2

    dest_path = os.path.join(root, dest, info["file"])
    rel = f"{dest}/{info['file']}"
    if args.dry_run:
        emit(args.json,
             {"ok": True, "dryRun": True, "slug": info["slug"], "from": info["folder"],
              "to": dest, "outcome": outcome, "dest": rel,
              "warn": gates["warn"]},
             f"dry-run: would move {info['folder']}/{info['file']} → {rel}" +
             (f"  (outcome: {outcome})" if outcome else ""))
        return 0
    if os.path.exists(dest_path):
        emit(args.json, {"ok": False, "code": "sp-dest-exists", "dest": rel,
                         "message": f"{rel} already exists"},
             f"error: {rel} already exists")
        return 1
    # The outcome is stamped BEFORE the hop, so the document that moves already carries it —
    # a backend whose move is not atomic must never be able to land an archived spec with no
    # outcome on it.
    if outcome:
        backend.write_spec(info, set_frontmatter_key(info["text"], "outcome", outcome))
    backend.move_spec(info, dest)
    emit(args.json,
         {"ok": True, "slug": info["slug"], "from": info["folder"], "to": dest,
          "outcome": outcome, "dest": rel, "warn": gates["warn"]},
         f"promoted '{info['slug']}': {info['folder']}/ → {rel}" +
         (f"  (outcome: {outcome})" if outcome else "") +
         ("".join(f"\n  warning: ## {h} is empty" for h in gates["warn"])))
    return 0


def _find_task(tasks: list[dict], ident: str) -> dict | None:
    for t in tasks:
        if t["id"] == ident or str(t["index"]) == ident:
            return t
    return None


def cmd_task(args, root: str) -> int:
    """Flip a checkbox MECHANICALLY — never by string surgery on the caller's side.

    `--block` writes the reason into the line itself. That visibility is the whole point:
    v1 kept an attempt counter in `.specs.json` that nobody read, and a task went quiet
    after five failures with no trace of why.

    `--check` may carry `--subject`, `--commit`, both, or neither. `--commit <sha>` is
    called AFTER the commit implementing the task already exists — the CLI records the sha
    it is given, it never resolves or invents one — and is additive: `--subject` keeps
    working exactly as before for any caller that has not moved to the sha anchor. Whichever
    write actually lands the anchor (`backend.write_spec`, below) is where a failure — a
    `gh api` call included — is reported, never swallowed."""
    backend, err = open_backend(root)
    if err:
        return emit_err(args.json, err)
    info, err = backend.read_spec(args.spec)
    if err:
        return emit_err(args.json, err)
    ident = args.check or args.uncheck or args.block
    if not ident:
        emit(args.json, {"ok": False, "code": "sp-no-action",
                         "message": "pass --check, --uncheck or --block"},
             "error: pass --check, --uncheck or --block")
        return 1
    # The subject names WHICH COMMIT IMPLEMENTS THIS TASK, so it is meaningful only on the
    # transition that says the task is done. On --uncheck any recorded anchor is dropped
    # rather than left behind pointing at work the checkbox no longer claims.
    if args.subject and not args.check:
        emit(args.json, {"ok": False, "code": "sp-subject-without-check",
                         "message": "--subject records the commit that implements a task, "
                                    "so it goes with --check"},
             "error: --subject goes with --check")
        return 1
    if args.subject is not None and not SUBJECT_RE.match(args.subject.strip()):
        emit(args.json, {"ok": False, "code": "sp-bad-subject", "subject": args.subject,
                         "message": "a commit subject must be one non-empty line"},
             "error: a commit subject must be one non-empty line")
        return 1
    # --commit is the sha form of the SAME anchor, meant to be called AFTER the commit that
    # implements the task already exists — the CLI never invents or looks up a sha, it only
    # records the one the caller already has. Same rule as --subject: meaningful only on the
    # transition that says the task is done, so it goes with --check too. It is additive,
    # not a replacement: a caller may still pass --subject alone, exactly as before.
    if args.commit and not args.check:
        emit(args.json, {"ok": False, "code": "sp-commit-without-check",
                         "message": "--commit records the sha of the commit that implements "
                                    "a task, so it goes with --check"},
             "error: --commit goes with --check")
        return 1
    if args.commit is not None and not COMMIT_SHA_RE.match(args.commit.strip()):
        emit(args.json, {"ok": False, "code": "sp-bad-commit-sha", "commit": args.commit,
                         "message": "--commit takes a git sha (hex, 7-40 characters), not "
                                    "free text"},
             "error: --commit takes a git sha (hex, 7-40 characters), not free text")
        return 1
    if args.block and not args.reason:
        emit(args.json, {"ok": False, "code": "sp-no-reason",
                         "message": "--block requires --reason"},
             "error: --block requires --reason (a blocked task without a reason is the "
             "hidden state this replaced)")
        return 1
    t = _find_task(info["tasks"], ident)
    if not t:
        emit(args.json, {"ok": False, "code": "sp-unknown-task", "task": ident,
                         "message": f"no task '{ident}' in {info['slug']}"},
             f"error: no task '{ident}' in {info['slug']}")
        return 1

    lines = info["text"].splitlines(keepends=True)
    line = lines[t["lineno"]]
    m = CHECKBOX_RE.match(line.rstrip("\n"))
    if not m:
        emit(args.json, {"ok": False, "code": "sp-line-drift", "task": ident,
                         "lineno": t["lineno"],
                         "message": "the parsed line is not a checkbox — the file changed"},
             "error: the parsed line is not a checkbox — re-read the spec")
        return 1
    mark = {"check": "x", "uncheck": " ", "block": "!"}[
        "check" if args.check else "uncheck" if args.uncheck else "block"]
    body = m.group(3).rstrip()
    body = BLOCKED_REASON_RE.sub("", body).rstrip()      # drop any stale blocked suffix
    if args.block:
        body = f"{body} — blocked: {args.reason.strip()}"
    lines[t["lineno"]] = f"{m.group(1)}- [{mark}] {body}\n"

    # Upsert the `subject:`/`commit:` metadata lines — replace one that is already there,
    # otherwise append it after the task's last metadata line (or right under the
    # checkbox). The two anchors are independent: passing one never disturbs an existing
    # line for the other, and both may be written in the same call while a spec transitions
    # from the subject anchor to the sha one. New lines are inserted together in ONE slice
    # so inserting one never shifts the position computed for the other.
    subject = None
    commit = None
    new_entries: list[str] = []
    if args.subject:
        subject = args.subject.strip()
        entry = f"{t['metaIndent']}subject: {subject}\n"
        if t["subjectLineno"] is not None:
            lines[t["subjectLineno"]] = entry
        else:
            new_entries.append(entry)
    if args.commit:
        commit = args.commit.strip()
        entry = f"{t['metaIndent']}commit: {commit}\n"
        if t["commitLineno"] is not None:
            lines[t["commitLineno"]] = entry
        else:
            new_entries.append(entry)
    if new_entries:
        lines[t["metaInsertAt"]:t["metaInsertAt"]] = new_entries
    if not args.subject and not args.commit and args.uncheck:
        # Drop whichever anchor the line carries — `subject:`, `commit:` written by
        # `--commit`, or the legacy `commit:` on a spec written before either form applied
        # to it. Highest offset first, so deleting one cannot shift the index of the other.
        for off in sorted((o for o in (t["subjectLineno"], t["commitLineno"])
                           if o is not None), reverse=True):
            del lines[off]
    # THE FAILURE-REPORTING CONTRACT: this call is the one that can fail out from under a
    # tick that already looks applied to `lines`. `FilesBackend` either writes the file or
    # raises. `GitHubBackend` pushes the same edited task block into the task's own
    # `GitHubBackend` pushes the same edited document into the issue body (`write_spec`) and
    # raises `BackendRefusal` — never swallowed
    # — the instant `gh api` fails, e.g. on a network error. `main()` is the one place that
    # exception becomes an exit code and an `ok: false` JSON body; nothing here catches it
    # and nothing here prints a success message before this line returns.
    backend.write_spec(info, "".join(lines))

    verb = "checked" if args.check else "unchecked" if args.uncheck else "blocked"
    anchor_lines = ((f"\n  subject: {subject}" if subject else "") +
                    (f"\n  commit: {commit}" if commit else ""))
    emit(args.json,
         {"ok": True, "slug": info["slug"], "task": ident, "action": verb,
          "state": mark, "text": body, "subject": subject, "commit": commit,
          "reason": args.reason if args.block else None},
         f"task {ident} {verb}: {body}" + anchor_lines)
    return 0


# --------------------------------------------------------------------------- #
# granular reading
# --------------------------------------------------------------------------- #
# The reader's view of a task. `metaInsertAt`, `metaIndent`, `subjectLineno` and
# `commitLineno` are deliberately NOT here: they are the offsets `task` upserts by, and
# handing them to a reader is an invitation to do the string surgery `task` exists to
# prevent. `lineno` stays, because locating a task in the file is reading, not writing.
SHOWN_TASK_KEYS = ("index", "id", "state", "checked", "blocked", "reason", "text",
                   "section", "parallel", "files", "pattern", "verify", "subject",
                   "commit", "lineno")


def _task_view(t: dict) -> dict:
    return {k: t[k] for k in SHOWN_TASK_KEYS}


def _show_index(info: dict) -> dict:
    """The MAP of one spec — which sections exist, how big each is, which task ids there are.

    Bounded by the fourteen headings and the task count no matter how long the document is,
    which is what makes it affordable as the default. It also makes the NEXT call exact: a
    caller that knows the heading spellings and the task ids never has to read the document
    to find out what it may ask for."""
    return {
        "sections": [{"heading": h,
                      "state": section_state(info["sections"], h),
                      "lines": len(info["sections"].get(h, {}).get("lines", []))}
                     for h in canonical_headings()],
        "strays": stray_headings(info["sections"]),
        "tasks": [{"id": t["id"], "index": t["index"], "state": t["state"], "text": t["text"]}
                  for t in info["tasks"]],
    }


def _show_human(obj: dict, info: dict) -> str:
    head = (f"{obj['slug']} — {obj['title']}\n"
            f"  {info['folder']}/{info['file']}  [{obj['stage']}]")
    if obj["view"] == "full":
        return info["text"].rstrip("\n")
    marks = {"filled": "✓", "empty": "!", "absent": "·"}
    out = [head]
    if obj["view"] == "index":
        out.append(f"  sections ({sum(1 for s in obj['sections'] if s['state'] != 'absent')}"
                   f"/{len(obj['sections'])} present)")
        for s in obj["sections"]:
            size = f"  {s['lines']} line(s)" if s["state"] != "absent" else ""
            out.append(f"    {marks[s['state']]} ## {s['heading']}{size}")
        if obj["strays"]:
            out.append(f"  strays: {', '.join(obj['strays'])}")
        if obj["tasks"]:
            out.append(f"  tasks ({len(obj['tasks'])})")
            for t in obj["tasks"]:
                out.append(f"    [{t['state']}] {t['text']}")
        out.append(f"  read sections: specs.py section {obj['slug']} \"<Heading>,<Heading>\"\n"
                   f"  read one task: specs.py show --spec {obj['slug']} --task <id>"
                   f"   (--full for the whole document)")
        return "\n".join(out)
    for t in obj["tasks"]:
        out.append(f"\n- [{t['state']}] {t['text']}")
        for key in ("files", "pattern", "verify", "subject", "commit"):
            val = t[key]
            if val:
                val = ", ".join(val) if isinstance(val, list) else val
                out.append(f"      {key}: {val}")
    return "\n".join(out)


def cmd_show(args, root: str) -> int:
    """Read ONE task, or the map of what is there — the whole document only when it is asked
    for by name.

    THE COST THIS ADDRESSES IS THE AGENT'S CONTEXT, NOT I/O. A backend may well have fetched
    the entire document to answer `--task 3.1`, and that is fine — reading a file twice is
    free. What is not free is an executor handed fourteen sections in order to edit one: it
    carries the other thirteen through every remaining turn of its conversation and pays for
    them again on each. So the DEFAULT IS THE INDEX AND NEVER THE DOCUMENT, and `--full`
    exists precisely so that the whole document has to be typed on purpose.

    **Section bodies are `section`'s, not this command's.** That reader is already plural and
    already resolves a `--moment` to its section set, so a second way to ask for a heading
    would be a second spelling of a measured answer — and the two would drift. What is left
    here is what `section` cannot say: WHICH headings and task ids exist (the index), one
    task's line and metadata, and the whole document under a name nobody types by accident.

    An unknown task id is a finding (exit 1), the same as an unknown slug."""
    backend, err = open_backend(root)
    if err:
        return emit_err(args.json, err)
    info, err = backend.read_spec(args.spec)
    if err:
        return emit_err(args.json, err)

    wanted_tasks = list(args.task or [])
    if args.full and wanted_tasks:
        # Two different cost profiles in one request. Silently letting one win would hand
        # back the whole document to a caller that asked for a slice, which is the exact
        # failure this command exists to make impossible.
        emit(args.json,
             {"ok": False, "code": "sp-conflicting-selection",
              "message": "--full asks for the whole document and --task for a slice of it "
                         "— pass one or the other"},
             "error: --full does not combine with --task")
        return 2

    tasks: list[dict] = []
    for ident in wanted_tasks:
        t = _find_task(info["tasks"], ident)
        if not t:
            emit(args.json, {"ok": False, "code": "sp-unknown-task", "task": ident,
                             "message": f"no task '{ident}' in {info['slug']}"},
                 f"error: no task '{ident}' in {info['slug']}")
            return 1
        tasks.append(_task_view(t))

    view = "full" if args.full else ("slice" if tasks else "index")
    obj = {"ok": True, "slug": info["slug"],
           "title": info["frontmatter"].get("title", ""),
           "stage": info["stage"], "phase": info["phase"], "folder": info["folder"],
           "file": info["file"], "view": view}
    if view == "full":
        obj["document"] = info["text"]
        obj["lines"] = len(info["text"].splitlines())
    elif view == "slice":
        obj["tasks"] = tasks
    else:
        obj.update(_show_index(info))
    emit(args.json, obj, _show_human(obj, info))
    return 0


CRITICALITY_RANK = {"critical": 0, "high": 1, "medium": 2, "normal": 2, "low": 3}


def _priority_rank(rec) -> tuple[float, str]:
    """A spec's human-assigned urgency as one comparable number, plus how it was read.

    `level` is the field triage writes and the one that ranks; `criticality` is a coarse
    fallback so a partially-filled record still ranks instead of silently sorting last.
    No record at all sorts after every record — never before."""
    if not isinstance(rec, dict):
        return (float("inf"), "")
    lvl = str(rec.get("level", "")).strip()
    if lvl:
        try:
            return (float(lvl), f"priority level {lvl}")
        except ValueError:
            pass
    crit = str(rec.get("criticality", "")).strip().lower()
    if crit in CRITICALITY_RANK:
        return (float(CRITICALITY_RANK[crit]), f"criticality {crit}")
    return (float("inf"), "")


def _days_since(date: str) -> int:
    try:
        d = datetime.date.fromisoformat(date)
    except ValueError:
        return 0
    return max(0, (datetime.date.fromisoformat(today()) - d).days)


def _git(cwd: str, *argv: str) -> str:
    """Stdout of one git command, or "" for every way it can fail — no git on PATH, not a
    repo, a nonzero exit. Every caller treats absence as "this repo has no git facts",
    which is a real state and never an error."""
    import subprocess
    try:
        out = subprocess.run(["git", *argv], capture_output=True, text=True, timeout=10,
                             cwd=cwd if os.path.isdir(cwd) else ".")
        return out.stdout if out.returncode == 0 else ""
    except (OSError, ValueError, subprocess.SubprocessError):
        return ""


SPECS_WORKTREE_DIR = ".claude/worktrees"


def worktree_dir_ignored(cwd: str, rel: str = SPECS_WORKTREE_DIR) -> bool:
    """Whether git ignores the path the `files` backend puts its specs worktree at.

    `git check-ignore` prints the path when it is ignored and nothing when it is not, so the
    existing `_git` — which swallows the exit code — answers this without a second helper. A
    path that does not exist yet answers the same way, which is exactly what the guard needs:
    the question is asked BEFORE `git worktree add`, never after.

    Resolved against the repo top level, not against `cwd`: this tool's `cwd` is the specs
    workspace, and `.claude/worktrees/` relative to `<repo>/specs/` is a different path that
    would answer the wrong question. No git and no repo answer `False` — a tree git cannot
    speak for is one where nothing can promise the worktree stays out of `git status`."""
    top = _git(cwd, "rev-parse", "--show-toplevel").strip()
    if not top:
        return False
    return bool(_git(top, "check-ignore", os.path.join(top, rel, "")).strip())


def worktree_guard(ignored: bool, rel: str = SPECS_WORKTREE_DIR) -> dict:
    """The refusal that stops the `files` backend sabotaging itself, or `{}` to proceed.

    Pure policy over the one fact `worktree_dir_ignored` establishes, kept separate from it so
    the decision is assertable without a repository to stage.

    Exit 2 rather than a warning, and rather than writing the line itself: `.gitignore` belongs
    to the target repo, and a tool that edits it uninvited to unblock its own feature is making
    the human's decision for them. Naming the one line to add is the whole remedy."""
    if ignored:
        return {}
    return {
        "code": "sp-worktree-unignored", "exit": 2, "path": rel,
        "message": f"git does not ignore '{rel}/' — add it to .gitignore before the files "
                   f"backend creates its specs worktree there; an untracked worktree breaks "
                   f"the clean-tree gate /specs:execute requires before its first task",
    }


# --------------------------------------------------------------------------- #
# the persistent specs worktree — where the `files` backend puts the specs branch
# --------------------------------------------------------------------------- #
def _git_run(cwd: str, *argv: str, stdin: str | None = None) -> tuple[int, str, str]:
    """Exit code, stdout AND stderr of one git command — the two halves `_git` throws away.

    A SIBLING of `_git`, never a change to it: every existing caller reads `""` as "this repo
    has no git facts", which is a real state and never an error. Creating a worktree needs the
    opposite reading — the difference between "the branch is not there" and "git could not
    answer" is what decides whether a branch gets created — and it needs git's own message to
    quote back in a refusal.

    A cwd that does not exist is `127` and no subprocess, where `_git` falls back to `"."`.
    That fallback is harmless when the answer is only ever read as a fact; here it would run
    `git worktree add` in whatever directory the process happens to sit in."""
    import subprocess
    if not os.path.isdir(cwd):
        return 127, "", f"not a directory: {cwd}"
    try:
        out = subprocess.run(["git", *argv], capture_output=True, text=True, timeout=30,
                             cwd=cwd, input=stdin)
        return out.returncode, out.stdout, out.stderr
    except (OSError, ValueError, subprocess.SubprocessError) as e:   # noqa: BLE001
        return 127, "", str(e)


def _repo_main_worktree(start: str) -> str:
    """The MAIN checkout of the repository `start` belongs to, or `""` when git cannot say.

    The main checkout and NOT `--show-toplevel`, because the specs worktree is ONE per
    repository and is reused: asked from inside a plan worktree, `--show-toplevel` answers with
    that plan worktree, so the backend would try to grow a second specs worktree per branch
    under development — each one wanting the same branch, which git refuses outright. Every
    linked worktree agrees on `--git-common-dir`, so it is the one answer that makes "created
    on demand and reused" true from anywhere in the repo.

    `start` may not exist yet (the default specs root is `<cwd>/specs` whether or not it is
    there), so the question is asked from the nearest ancestor that does."""
    d = os.path.abspath(start)
    while not os.path.isdir(d):
        parent = os.path.dirname(d)
        if parent == d:
            return ""
        d = parent
    common = _git(d, "rev-parse", "--path-format=absolute", "--git-common-dir").strip()
    # `--path-format` landed in git 2.31; on an older one the flag itself fails, and the main
    # checkout is still the right answer for every repo that has no linked worktree.
    top = os.path.dirname(common) if common else _git(d, "rev-parse", "--show-toplevel").strip()
    return top if top and os.path.isdir(top) else ""


def specs_worktree_path(top: str, branch: str) -> str:
    """Where the specs branch is checked out — one fixed, derivable path per branch.

    Derived rather than recorded: a path this tool can recompute from the branch name needs no
    state file, and a second process finds the SAME worktree instead of creating a rival one.
    `/` becomes `-` so a namespaced branch (`quenching/specs`) stays one directory deep and can
    never nest inside another worktree's path."""
    return os.path.join(top, SPECS_WORKTREE_DIR, branch.replace("/", "-").strip("-") or "specs")


def _create_empty_branch(top: str, branch: str) -> tuple[int, str]:
    """Point `branch` at a commit whose tree is EMPTY, for a git too old for `--orphan`.

    `git worktree add --orphan` (git 2.42) leaves the branch unborn, which is emptier still and
    is what this prefers. Below that version the same intent costs three plumbing calls and
    lands one root commit holding nothing — the specs branch still shares no history and no
    file with the code branches, which is the property the whole design rests on.

    `mktree` over empty input is the empty tree without depending on `/dev/null` or on a
    hardcoded hash, which differs between a sha1 and a sha256 repository."""
    code, tree, err = _git_run(top, "mktree", stdin="")
    if code != 0:
        return code, err
    code, commit, err = _git_run(top, "commit-tree", tree.strip(),
                                 "-m", f"quenching: initialise the {branch} branch", stdin="")
    if code != 0:
        return code, err
    code, _, err = _git_run(top, "branch", branch, commit.strip())
    return code, err


def specs_worktree(top: str, branch: str) -> tuple[str, dict]:
    """The checkout of the specs branch the `files` backend reads and writes — reused when it
    is already there, created on demand when it is not. Returns `(path, err)`.

    PERSISTENT, not per-command: the branch is checked out once and left in place, so the cost
    of the whole design is one `git worktree add` in a repository's life and one `os.path.isdir`
    per command afterwards. A worktree created and removed around every call would pay a
    checkout per `status`.

    THE GUARD RUNS BEFORE ANYTHING IS CREATED, and only on the creation path. An unignored
    worktree is untracked content in the working tree, which breaks the clean-tree gate
    `/specs:execute` demands before its first task — the backend would sabotage the command
    that drives it. That damage is done by the `git worktree add`, so that is what the guard
    stands in front of; the reuse path creates nothing and pays no subprocess for it.

    The branch is created EMPTY when it does not exist. Not branched off the current HEAD: a
    specs branch sharing history with the code is the very thing the backend exists to undo,
    and one that starts with the whole repository in it would put every code file one merge
    away from the specs."""
    path = specs_worktree_path(top, branch)
    if os.path.isdir(path):
        # The reuse test is `--show-toplevel`, NOT `--is-inside-work-tree`: this path sits
        # inside the repository by construction, so "are you in a work tree" answers `true` for
        # any ordinary directory left there and the backend would happily write specs into a
        # folder that belongs to the code branch. Only a real linked worktree answers with its
        # OWN path as the top level.
        if os.path.realpath(_git(path, "rev-parse", "--show-toplevel").strip() or os.sep) \
                == os.path.realpath(path):
            return path, {}
        return path, {
            "code": "sp-worktree-unusable", "exit": 2, "path": path, "branch": branch,
            "message": f"'{path}' exists but git does not know it as a worktree — the files "
                       f"backend will not write specs into a directory it cannot attribute to "
                       f"the '{branch}' branch; move it aside or `git worktree repair`",
        }

    refusal = worktree_guard(worktree_dir_ignored(top))
    if refusal:
        return path, refusal

    os.makedirs(os.path.dirname(path), exist_ok=True)
    exists, _, _ = _git_run(top, "show-ref", "--verify", "--quiet", f"refs/heads/{branch}")
    if exists == 0:
        code, _, err = _git_run(top, "worktree", "add", path, branch)
    else:
        code, _, err = _git_run(top, "worktree", "add", "--orphan", "-b", branch, path)
        if code != 0 and not os.path.isdir(path):
            # Either `--orphan` is not understood (git < 2.42) or the add failed outright. The
            # `isdir` test is what tells the two apart without parsing git's prose: a refused
            # flag creates nothing, so retrying the long way is safe; anything that got as far
            # as making the directory is reported instead of being retried on top of itself.
            code, err = _create_empty_branch(top, branch)
            if code == 0:
                code, _, err = _git_run(top, "worktree", "add", path, branch)
    if code != 0 or not os.path.isdir(path):
        return path, {
            "code": "sp-worktree-failed", "exit": 2, "path": path, "branch": branch,
            "git": err.strip(),
            "message": f"could not check out the specs branch '{branch}' at '{path}' — git "
                       f"said: {err.strip() or 'nothing'}",
        }
    return path, {}


def _inside_worktree_dir(path: str, rel: str = SPECS_WORKTREE_DIR) -> bool:
    """Whether `path` already sits under a worktree directory, so nothing nests another one
    inside it. Compared segment by segment rather than as a substring — a repository legitimately
    named `.claude/worktrees-archive` is not a worktree."""
    parts = os.path.abspath(path).split(os.sep)
    want = rel.split("/")
    return any(parts[i:i + len(want)] == want for i in range(len(parts)))


def _holds_phase_folder(root: str) -> bool:
    return any(os.path.isdir(os.path.join(root, p)) for p in PHASE_DIRS)


def resolve_files_root(root: str, cfg: dict) -> tuple[str, dict]:
    """Which directory the `files` backend actually operates on: the workspace as declared, or
    the persistent worktree of the specs branch. Returns `(root, err)`.

    Three shapes answer WITHOUT git, and they answer first — which is what keeps the resolution
    free for everything that is not a migrated repository, and what lets the backend be
    exercised over a bare temp directory with no repository at all:

      already inside a worktree   nothing nests a worktree in a worktree; the specs branch is
                                  already the tree underfoot.
      the workspace is populated  a `specs/` holding phase folders in the code tree is the
                                  PRE-MIGRATION store and stays authoritative until a human
                                  moves it. Switching silently would make every repository that
                                  upgrades this tool look like it had lost every spec it has —
                                  the loudest regression this change could ship, and the one
                                  this repository would have taken on the very next `list`.
                                  Moving those files is deliberate work (`## Out of Scope`),
                                  so the presence of the old store is the honest signal that it
                                  has not happened yet.
      no repository               there is no branch to check out, so there is nowhere else the
                                  specs could be.

    Otherwise the specs live on the specs branch, and the worktree is created on demand. The
    workspace keeps its own basename inside it, so `SPECS_ROOT=<x>/design` resolves to
    `<worktree>/design` and the layout is the same on both sides of the migration.

    Memoised per declared root: the answer costs subprocesses, and it is asked twice per
    writing command — once by `writer_lock`, once by `open_backend`. The cache is what makes
    the lock and the backend point at the SAME worktree by construction rather than by two
    resolutions agreeing."""
    if root in _FILES_ROOT_CACHE:
        return _FILES_ROOT_CACHE[root]
    out = _resolve_files_root(root, cfg)
    _FILES_ROOT_CACHE[root] = out
    return out


_FILES_ROOT_CACHE: dict[str, tuple[str, dict]] = {}


def _resolve_files_root(root: str, cfg: dict) -> tuple[str, dict]:
    if _inside_worktree_dir(root) or _holds_phase_folder(root):
        return root, {}
    top = _repo_main_worktree(root)
    if not top:
        return root, {}
    path, err = specs_worktree(top, cfg.get("specsBranch") or DEFAULT_SPECS_BRANCH)
    if err:
        return root, err
    return os.path.join(path, os.path.basename(os.path.normpath(root)) or "specs"), {}


def files_specs_worktree(root: str, cfg: dict) -> tuple[str | None, dict]:
    """The specs worktree the `files` backend resolved to, or `None` when it did not use one.

    `None` is not a failure — it is the pre-migration workspace still sitting in the code tree,
    which is a legal and currently common state. Anything that guards the worktree has to be
    able to tell the two apart without triggering a second resolution."""
    target, err = resolve_files_root(root, cfg)
    if err:
        return None, err
    if os.path.abspath(target) == os.path.abspath(root):
        return None, {}
    return os.path.dirname(os.path.abspath(target)), {}


def files_root_failures() -> list[str]:
    """The shapes `resolve_files_root` must answer without reaching for git, checked rather
    than asserted in prose.

    Every one of them is a case where creating a worktree would be WRONG, and the cost of
    getting it wrong is not a bad answer but a branch and a checkout appearing in someone's
    repository. Self-contained — a temp directory and pure path arithmetic, so this runs on an
    installed copy with no repository staged."""
    import tempfile
    cfg = {"specsBranch": DEFAULT_SPECS_BRANCH}
    out: list[str] = []
    with tempfile.TemporaryDirectory() as tmp:
        populated = os.path.join(tmp, "specs")
        os.makedirs(os.path.join(populated, "plans"))
        got, err = resolve_files_root(populated, cfg)
        if got != populated or err:
            out.append(f"a populated workspace resolved to {got!r} (err={err.get('code')!r}), "
                       f"not to itself — the pre-migration store must stay authoritative")

        nested = os.path.join(tmp, SPECS_WORKTREE_DIR, "specs", "specs")
        os.makedirs(nested)
        got, err = resolve_files_root(nested, cfg)
        if got != nested or err:
            out.append(f"a workspace already inside {SPECS_WORKTREE_DIR}/ resolved to {got!r} "
                       f"(err={err.get('code')!r}) — nothing nests a worktree in a worktree")

    want = os.path.join("/repo", SPECS_WORKTREE_DIR, "quenching-specs")
    got_path = specs_worktree_path("/repo", "quenching/specs")
    if got_path != want:
        out.append(f"a namespaced branch resolved to {got_path!r}, not {want!r} — a `/` in the "
                   f"branch name must not deepen the worktree path")
    return out


# --------------------------------------------------------------------------- #
# the specs worktree lock — one writer at a time, per worktree
# --------------------------------------------------------------------------- #
LOCK_SUFFIX = ".lock"
LOCK_WAIT_SECONDS = 10.0
LOCK_POLL_SECONDS = 0.05


def specs_lock_path(worktree: str) -> str:
    """`<…>/.claude/worktrees/<name>.lock` — BESIDE the worktree, never inside it.

    Inside, the lock would be untracked content in the one tree whose whole job is to hold a
    clean, committable set of specs, and every `git status` run there would report the tool's
    own bookkeeping. Beside, it is already covered by the `.claude/worktrees/` ignore rule that
    `worktree_guard` refuses to run without — so the lock costs no new ignore line, and cannot
    dirty the code tree either."""
    return os.path.normpath(worktree) + LOCK_SUFFIX


def _lock_holder(path: str) -> dict:
    """Who the lock file says is holding it. An unreadable or unparseable lock comes back as an
    empty record rather than as an error: the file existing is the lock, and its contents are
    only ever used to describe the holder to a human or to prove it is gone."""
    try:
        obj = json.loads(read_text(path) or "")
        return obj if isinstance(obj, dict) else {}
    except json.JSONDecodeError:
        return {}


def _holder_is_gone(info: dict) -> bool:
    """True ONLY when this process can prove the recorded holder no longer exists.

    AGE IS NEVER THE REASON. "The lock is old, so I will take it" is the tempting rule and the
    wrong one: a `promote` on a slow filesystem and a crashed process look identical through a
    timestamp, and the fast case for guessing wrong is two writers in the same document. Age
    appears in the refusal message as information for the human and never as a decision.

    Proof, and the three things that make it unavailable:

      another host      a pid is meaningless off the machine that issued it, and a specs
                        worktree on a network share can legitimately be held from elsewhere.
      not POSIX         `os.kill(pid, 0)` is a liveness probe on POSIX and NOT on Windows,
                        where `os.kill` terminates the target whatever signal it is handed.
                        A probe that kills the process it asks about is not a probe.
      pid alive, or not ours  `ProcessLookupError` is the only answer that proves absence.
                        `PermissionError` means it is running under another user, which is
                        alive. Pid reuse can only make a dead holder look ALIVE, which errs
                        toward refusing — the safe direction."""
    import socket
    if os.name != "posix":
        return False
    if str(info.get("host") or "") != socket.gethostname():
        return False
    try:
        pid = int(info.get("pid") or 0)
    except (TypeError, ValueError):
        return False
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return True
    except (OSError, OverflowError):
        return False
    return False


class SpecsLock:
    """Serialises the `specs.py` invocations that WRITE into one specs worktree.

    THE SCOPE IS THE WHOLE COMMAND, not the write syscall. Every writing command is a
    read-modify-write — `task --check` reads the document, flips one character, writes the
    whole file back — so a lock held only around the write would still let two processes read
    the same document and each store its own edit over the other's. Nothing would look corrupt
    and one tick would simply be gone, which is the worse failure: it leaves no trace.

    ONE LOCK PER WORKTREE, because the worktree is the resource. Two agents ticking tasks on
    DIFFERENT specs do contend under this, and that is right rather than unfortunate: they
    share one checkout of one branch, and the next thing that touches it commits everything in
    it. Contention costs milliseconds — the work under the lock is one parse and one rename.

    `O_CREAT | O_EXCL` is the primitive, not `fcntl` and not `msvcrt.locking`: exclusive create
    is one syscall with the same meaning on POSIX and on Windows, and this tool ships to both
    (`_force_utf8_output` is here for the same reason). The cost is a file left behind when a
    process dies, which is what `_holder_is_gone` answers; the gain is a lock with no platform
    branch inside it.

    READERS TAKE NO LOCK. `list`, `status`, `show`, `next`, `validate` and `doctor` are the
    commands a skill calls most, several of them per turn, and putting them in a queue behind a
    writer would make the lock the front's throughput limit. What makes that safe is not luck:
    `write_text` replaces a document by rename, so a reader sees the old text or the new one and
    never a half-written file."""

    def __init__(self, path: str, label: str = "") -> None:
        self.path = path
        self.label = label
        self.held = False

    def acquire(self, wait: float = LOCK_WAIT_SECONDS) -> dict:
        """`{}` once held, or a ready-to-emit refusal naming the holder. Never raises, never
        waits forever: a bounded wait absorbs the normal case, where the process ahead is
        finishing a rename, and anything beyond it is reported to whoever can act on it."""
        import socket
        import time
        deadline = time.monotonic() + max(0.0, wait)
        record = json.dumps({"pid": os.getpid(), "host": socket.gethostname(),
                             "command": self.label, "since": _now_iso(),
                             "tool": f"specs.py {VERSION}"}, ensure_ascii=False)
        while True:
            try:
                os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
                fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
            except FileExistsError:
                pass
            except OSError as e:
                return {"code": "sp-lock-unwritable", "exit": 2, "path": self.path,
                        "message": f"could not create the specs worktree lock at "
                                   f"'{self.path}': {e}"}
            else:
                with os.fdopen(fd, "w", encoding="utf-8") as fh:
                    fh.write(record)
                self.held = True
                return {}

            holder = _lock_holder(self.path)
            if _holder_is_gone(holder):
                try:
                    os.remove(self.path)      # PROVEN dead — not merely old
                except OSError:
                    pass                      # someone else got there first, or we may not
            else:
                time.sleep(LOCK_POLL_SECONDS)
            if time.monotonic() >= deadline:
                return self._refusal(holder, wait)

    def _refusal(self, holder: dict, waited: float) -> dict:
        who = (f"pid {holder.get('pid')} on {holder.get('host')}"
               if holder.get("pid") else "an unidentified process")
        what = f" running `{holder['command']}`" if holder.get("command") else ""
        since = f" since {holder['since']}" if holder.get("since") else ""
        return {
            "code": "sp-specs-locked", "exit": 2, "path": self.path, "holder": holder,
            "waited": round(waited, 2),
            "message": f"the specs worktree is locked by {who}{what}{since} — waited "
                       f"{waited:g}s and gave up; nothing was written. If that process is gone, "
                       f"delete '{self.path}'",
        }

    def release(self) -> None:
        """Drop the lock. Idempotent and silent about a file already gone — a release that
        raised would turn a successful write into a nonzero exit in the `finally` that runs
        after it."""
        if not self.held:
            return
        self.held = False
        try:
            os.remove(self.path)
        except OSError:
            pass

    def __enter__(self) -> "SpecsLock":
        return self

    def __exit__(self, *exc) -> None:
        self.release()


def _now_iso() -> str:
    return datetime.datetime.now().replace(microsecond=0).isoformat()


# Every subcommand that can MODIFY a spec. `list`/`status`/`show`/`next`/`parallel`/`validate`/
# `config`/`doctor`/`selftest` are absent because they only read.
WRITING_COMMANDS = ("new", "task", "discover", "section", "promote", "verification")


def command_writes(args) -> bool:
    """Whether THIS invocation will modify a spec — the scope the lock is taken for.

    Per invocation and not per subcommand: `section` without `--write` and `promote --dry-run`
    read and report, and queueing them behind a writer would put the lock in front of the two
    reads a skill makes most.

    `migrate` is deliberately absent. It rewrites the DECLARED workspace's own folder layout —
    the pre-migration `specs/` in the code tree — and never touches the specs worktree, so the
    worktree's lock would guard nothing it writes."""
    cmd = getattr(args, "cmd", "")
    if cmd in ("new", "task", "discover"):
        return True
    if cmd == "section":
        return bool(getattr(args, "write", False))
    if cmd == "record":
        return bool(getattr(args, "set", None))
    if cmd == "verification":
        return bool(getattr(args, "policy", None))
    if cmd == "promote":
        return not bool(getattr(args, "dry_run", False))
    return False


def writer_lock(args, root: str) -> tuple[SpecsLock | None, dict]:
    """The lock this invocation must hold before it runs, or `(None, {})` when it needs none.

    Three ways to need none, each a fact about where the specs are rather than a policy:

      the command only reads    see `command_writes`.
      an external backend       GitHub and Azure Boards serialise on their own server; a local
                                file could not make a remote write atomic and would only add a
                                second thing to get stuck.
      no specs worktree         a pre-migration workspace in the code tree has nowhere to put a
                                lock that git ignores, and an untracked file there is exactly
                                the breakage `worktree_guard` exists to prevent. It is left
                                unserialised knowingly — that workspace is the state this
                                backend exists to end, and adding a second untracked artifact
                                to it would buy safety for a layout on its way out at the price
                                of the clean-tree gate `/specs:execute` runs under."""
    if not command_writes(args):
        return None, {}
    cfg = load_config(root)
    if cfg["backend"] != DEFAULT_BACKEND:
        return None, {}
    worktree, err = files_specs_worktree(root, cfg)
    if err:
        return None, err
    if worktree is None:
        return None, {}
    lock = SpecsLock(specs_lock_path(worktree), label=_invocation_label(args))
    return lock, lock.acquire()


def _invocation_label(args) -> str:
    """A short, honest name for what is holding the lock — the subcommand and the spec it is
    writing. Read by a human staring at a refusal, so it names the spec rather than echoing the
    whole argv, which would carry `--json` and other noise into the message."""
    spec = getattr(args, "spec", None) or getattr(args, "title", None) or ""
    return f"{getattr(args, 'cmd', '?')} {spec}".strip()


def lock_failures() -> list[str]:
    """The lock's invariants, checked rather than asserted in prose.

    The direction that is asserted here is the DANGEROUS one: a lock that is taken while
    someone holds it, or a holder judged gone on evidence that does not prove it, silently
    loses a human's edit. Both are decidable with no repository and no second process.

    The opposite direction — a genuinely dead holder being reclaimed — is exercised in a
    disposable repository and NOT here, because asserting it needs a pid that is provably dead,
    and the only cheap way to get one is a process that just exited, whose pid the operating
    system may reuse. A selftest that fails once a month teaches people to ignore it."""
    import socket
    import tempfile
    out: list[str] = []
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "specs.lock")
        first = SpecsLock(path, label="task alpha")
        if first.acquire(wait=0.0):
            out.append("a free lock refused to be acquired")
        if not os.path.isfile(path):
            out.append("acquiring left no lock file, so nothing marks the worktree as held")

        second = SpecsLock(path, label="promote alpha")
        err = second.acquire(wait=0.0)
        if err.get("code") != "sp-specs-locked" or err.get("exit") != 2:
            out.append(f"a held lock was acquired again (got {err.get('code')!r}) — two "
                       f"writers in one worktree is the whole failure this prevents")
        if str(err.get("holder", {}).get("pid")) != str(os.getpid()):
            out.append(f"the refusal names holder {err.get('holder')!r}, not the process that "
                       f"actually holds it")

        first.release()
        if os.path.exists(path):
            out.append("releasing left the lock file behind, which wedges the next writer")
        if second.acquire(wait=0.0):
            out.append("a released lock could not be re-acquired")
        second.release()

    live = {"pid": os.getpid(), "host": socket.gethostname()}
    if _holder_is_gone(live):
        out.append("this very process was judged gone — the liveness proof is inverted")
    if not _holder_is_gone({"pid": 1, "host": "a-host-that-is-not-this-one"}):
        pass          # correct: another host is unknowable, never reclaimed
    else:
        out.append("a holder on another host was judged gone — a pid does not travel")
    if _holder_is_gone({"host": socket.gethostname()}) or \
            _holder_is_gone({"pid": 0, "host": socket.gethostname()}):
        out.append("a holder with no usable pid was judged gone — absence of evidence is not "
                   "proof of death")

    reads = argparse.Namespace(cmd="section", write=False, spec="x")
    writes = argparse.Namespace(cmd="section", write=True, spec="x")
    if command_writes(reads) or not command_writes(writes):
        out.append("`section` is classified wrong — the lock follows the invocation, not the "
                   "subcommand")
    for cmd in ("list", "status", "show", "next", "parallel", "validate", "config",
                "doctor", "selftest"):
        if command_writes(argparse.Namespace(cmd=cmd)):
            out.append(f"`{cmd}` takes the writer lock, but it only reads")
    return out


def _git_refs(root: str) -> tuple[set[str], str | None]:
    """Every local branch, and the one checked out. Two calls for the WHOLE front, never
    one per spec — ranking twenty specs must not cost forty subprocesses.

    No git, or no repo → an empty set and no current branch, which ranks exactly as today."""
    heads = {l.strip() for l in
             _git(root, "for-each-ref", "--format=%(refname:short)",
                  "refs/heads").splitlines() if l.strip()}
    current = _git(root, "rev-parse", "--abbrev-ref", "HEAD").strip() or None
    return heads, (current if current and current != "HEAD" else None)


def _work_ref(fm: dict, slug: str) -> str:
    """The branch this spec's work would live on.

    The `branch:` record when one was stamped, else the default `plan/<slug>` — because a
    human may have cut the branch by hand, with no record at all. The record alone is NEVER
    the signal: what counts is whether the ref is alive."""
    rec = fm.get("branch")
    work = str(rec.get("work", "")).strip() if isinstance(rec, dict) else ""
    return work or f"plan/{slug}"


def _candidate(backend: SpecBackend, s: dict, schema: dict, heads: set[str],
               current: str | None) -> dict:
    # ASKED OF THE BACKEND, never of the path. Against GitHub the locator is an issue URL, so
    # every candidate derived from an EMPTY document — the whole front ranked as `captured`
    # with no title, no tasks and nothing executing, and `/specs:continue` handed out its
    # single next action from exactly that.
    info, rerr = backend.read_spec(s["slug"])
    unreadable = (rerr or {}).get("code")
    if info is None:
        # Ambiguous slug — the slug came from the listing, so it cannot be unknown, and
        # `validate` names it `sp-duplicate-slug`. The candidate SURVIVES, derived from an
        # empty document exactly as `list` keeps its row: dropping it would hide a spec from
        # the ranking, and `unreadable` says why it ranks as an empty one.
        info = derive_info(s, "")
    fm, sections, tasks = info["frontmatter"], info["sections"], info["tasks"]
    checked, blocked, total = task_progress(tasks)
    stage = derive_stage(s, sections, fm, tasks, schema)
    ready = ready_report({"sections": sections}, schema)
    prank, pwhy = _priority_rank(fm.get("priority"))
    progress = (checked / total) if total else 0.0
    executing = stage == "executing"
    work = _work_ref(fm, s["slug"])
    live = work in heads
    # A record whose ref is gone stops counting: the branch was merged or deleted, so the
    # spec is no more "in flight" than one that never had a branch at all.
    on_it = live and work == current
    branch_rank = 0 if on_it else (2 if live else 1)
    return {
        "slug": s["slug"], "folder": s["folder"], "file": s["file"], "date": info["date"],
        "title": fm.get("title", titleize(s["slug"])), "stage": stage,
        "tasks": {"checked": checked, "blocked": blocked, "total": total},
        "progress": round(progress, 3),
        "readyGateMet": ready["ok"],
        "approved": fm.get("approved") or None,
        "priority": fm.get("priority") or None,
        "ageDays": _days_since(info["date"]),
        "unreadable": unreadable,
        "branch": {"work": work, "live": live, "current": on_it},
        "_key": (branch_rank, 0 if executing else 1, -progress, prank,
                 info["date"], s["slug"]),
        "_why": pwhy,
        "_executing": executing,
    }


def _rank_reason(c: dict) -> str:
    """Why this candidate sits where it does — the ONE dominant factor, not a formula."""
    t = c["tasks"]
    if c["branch"]["current"]:
        return f"you are on this branch ({c['branch']['work']})"
    if c["branch"]["live"]:
        return f"in flight on `{c['branch']['work']}` — check it out to continue"
    if c["_executing"]:
        r = f"executing — {t['checked']}/{t['total']} tasks done"
        if t["blocked"]:
            r += f", {t['blocked']} blocked"
        return r
    if c["_why"]:
        return f"{c['_why']} — {c['stage']}"
    if c["readyGateMet"]:
        return f"ready to build, untouched for {c['ageDays']}d"
    return f"{c['stage']}, {c['ageDays']}d old"


def _next_front(args, root: str) -> int:
    """The ranked candidate list — THE only place ranking logic lives.

    Four factors, lexicographic and in this order:
      1. executing first     finish what is already started before opening something new
      2. closest to done     among those, the one nearest the end
      3. priority            the human's ranking, when triage has written one
      4. age                 oldest first, so nothing rots quietly

    Factor 2 is harmless for everything else: a spec with no ticked task scores 0, so the
    whole non-executing set ties there and falls through to priority — which is exactly the
    intent, without a special case.

    A LIVE `plan/<slug>` ref outranks all four, in both directions: the branch you are
    standing on goes to the top, and one alive but not checked out is demoted below the
    untouched specs — offering it would send a second run at work already under way
    somewhere else. The signal is the ref, never the `branch:` record: a human may cut a
    branch with no record, and a record outlives the branch it names."""
    schema = load_schema()
    heads, current = _git_refs(root)
    backend, err = open_backend(root)
    if err:
        return emit_err(args.json, err)
    cands = [_candidate(backend, s, schema, heads, current)
             for s in backend.list_specs("plans")]
    cands.sort(key=lambda c: c["_key"])
    ranked = []
    for c in cands:
        c = dict(c)
        c["reason"] = _rank_reason(c)
        for k in ("_key", "_why", "_executing"):
            c.pop(k)
        ranked.append(c)

    # When nothing carries a priority record and nothing is in flight, the order is age
    # alone — which is an ordering, not a judgment. Say so rather than implying a ranking
    # that was never made.
    prioritized = [c for c in ranked if c["priority"]]
    # A live branch IS in flight, whether or not any task has been ticked yet — and it has
    # already reordered the list, so claiming the order is age alone would be false.
    in_flight = [c for c in ranked if c["stage"] == "executing" or c["branch"]["live"]]
    needs_triage = bool(ranked) and not prioritized and not in_flight and len(ranked) > 1

    obj = {"ok": True, "root": root, "count": len(ranked),
           "top": ranked[0]["slug"] if ranked else None,
           "needsTriage": needs_triage,
           "candidates": ranked}
    if args.json:
        print(json.dumps(obj, indent=2, ensure_ascii=False))
        return 0
    if not ranked:
        print(f"no active specs under {root} — nothing to continue")
        return 0
    print(f"specs front — {len(ranked)} active, ranked")
    for i, c in enumerate(ranked, 1):
        print(f"  {i}. {c['slug']:<32} {c['reason']}")
    if needs_triage:
        print("\n  nothing is in flight and nothing carries a priority record — this order "
              "is age alone.\n  `specs.py`-driven triage would give it something to stand on.")
    return 0


def cmd_next(args, root: str) -> int:
    """THE single next action, so a skill never infers state from prose.

    In `plans/` the ladder is one chain, because the folder no longer splits it: fill the
    ready gate, then work the tasks, then close out. A `[!]` task is SKIPPED — it already
    has an honest reason recorded and re-offering it forever is what the attempt budget
    was clumsily trying to prevent.

    Reaching the ready gate does NOT stop the ladder to demand approval. Refusing here
    would rebuild the `promote` this fold removed; `execute` asks for the stamp inline,
    and `approved` rides along in the payload so it can.

    With `--front` the question is the other one — WHICH spec — and that is answered by
    `_next_front`."""
    if args.front:
        return _next_front(args, root)
    if not args.spec:
        emit(args.json, {"ok": False, "code": "sp-no-target",
                         "message": "pass --spec <slug> for one spec's next action, "
                                    "or --front for the ranked candidate list"},
             "error: pass --spec <slug>, or --front")
        return 1
    backend, err = open_backend(root)
    if err:
        return emit_err(args.json, err)
    info, err = backend.read_spec(args.spec)
    if err:
        return emit_err(args.json, err)
    base = {"slug": info["slug"], "phase": info["phase"], "folder": info["folder"],
            "stage": info["stage"], "verification": info["verification"],
            "approved": info["frontmatter"].get("approved") or None,
            "blocked": [{"id": t["id"], "text": t["text"], "reason": t["reason"]}
                        for t in info["tasks"] if t["blocked"]]}

    if info["phase"] == "plans":
        ready = ready_report(info)
        if not ready["ok"]:
            want = (ready["missing"] + ready["malformed"])[0]
            remaining = len(ready["missing"]) + len(ready["malformed"]) - 1
            obj = {"ok": True, "action": "write_section", "heading": want, **base,
                   "missing": ready["missing"], "malformed": ready["malformed"],
                   "message": f"write ## {want}"
                              + (f" (then {remaining} more)" if remaining else "")
                              + " to reach the ready gate"}
            emit(args.json, obj, obj["message"])
            return 0
        openable = [t for t in info["tasks"] if not t["checked"] and not t["blocked"]]
        if openable:
            t = openable[0]
            obj = {"ok": True, "action": "implement_task", "task": t["id"], "text": t["text"],
                   "verify": t["verify"], "files": t["files"], "pattern": t["pattern"],
                   "parallel": t["parallel"], **base,
                   "message": f"implement task {t['id']}: {t['text']}"}
            emit(args.json, obj, obj["message"])
            return 0
        if base["blocked"]:
            obj = {"ok": True, "action": "blocked", **base,
                   "message": f"every remaining task is blocked ({len(base['blocked'])})"}
            emit(args.json, obj, obj["message"] + "".join(
                f"\n  [!] {b['text']}" for b in base["blocked"]))
            return 0
        obj = {"ok": True, "action": "promote", "to": "archive", **base,
               "message": f"all tasks complete — write ## Outcome, then "
                          f"`specs.py promote {info['slug']} --to archive`"}
        emit(args.json, obj, obj["message"])
        return 0

    obj = {"ok": True, "action": "done", **base,
           "message": f"'{info['slug']}' is archived ("
                      f"{info['frontmatter'].get('outcome', 'done')})"}
    emit(args.json, obj, obj["message"])
    return 0


def _norm_file(p: str) -> str:
    p = p.strip().replace("\\", "/")
    p = re.sub(r"\s*\(new\)\s*$", "", p)      # `src/a.py (new)` is still src/a.py
    return p.strip("./")


def _overlaps(a: str, b: str) -> bool:
    a, b = _norm_file(a), _norm_file(b)
    return a == b or a.startswith(b.rstrip("/") + "/") or b.startswith(a.rstrip("/") + "/")


def parallel_groups(tasks: list[dict]) -> list[list[dict]]:
    """Consecutive `[P]` tasks within one `### N.` section form a group."""
    groups, cur, sec = [], [], None
    for t in tasks:
        if t["parallel"] and (sec is None or t["section"] == sec):
            cur.append(t)
            sec = t["section"]
            continue
        if len(cur) > 1:
            groups.append(cur)
        cur, sec = ([t], t["section"]) if t["parallel"] else ([], None)
    if len(cur) > 1:
        groups.append(cur)
    return groups


def cmd_parallel(args, root: str) -> int:
    """Prove a `[P]` group's `files:` sets are disjoint — MECHANICALLY, never judged in
    prose. A group with an undeclared `files:` is ineligible: nothing can be proven about
    a task that never said what it touches."""
    backend, err = open_backend(root)
    if err:
        return emit_err(args.json, err)
    info, err = backend.read_spec(args.spec)
    if err:
        return emit_err(args.json, err)
    findings = []
    for gi, group in enumerate(parallel_groups(info["tasks"]), 1):
        undeclared = [t["id"] for t in group if not t["files"]]
        clashes = []
        for i, a in enumerate(group):
            for b in group[i + 1:]:
                for fa in a["files"]:
                    for fb in b["files"]:
                        if _overlaps(fa, fb):
                            clashes.append({"a": a["id"], "b": b["id"],
                                            "file": _norm_file(fa)})
        eligible = not undeclared and not clashes
        findings.append({"group": gi, "tasks": [t["id"] for t in group],
                         "eligible": eligible, "undeclared": undeclared,
                         "clashes": clashes})
    ok = all(f["eligible"] for f in findings)
    if args.json:
        print(json.dumps({"ok": ok, "slug": info["slug"], "groups": findings},
                         indent=2, ensure_ascii=False))
    else:
        if not findings:
            print(f"{info['slug']}: no [P] groups — serial execution")
        for f in findings:
            print(f"group {f['group']}: {', '.join(x or '?' for x in f['tasks'])} — "
                  f"{'eligible' if f['eligible'] else 'NOT eligible'}")
            for c in f["clashes"]:
                print(f"    {c['a']} and {c['b']} both touch {c['file']}")
            if f["undeclared"]:
                print(f"    no files: declared by {', '.join(f['undeclared'])}")
    return 0 if ok else 1


def cmd_discover(args, root: str) -> int:
    """Append one line to `## Discoveries`, creating the section when absent.

    Captured INDISCRIMINATELY during execution — whether a discovery is worth acting on is
    triage's judgment, not the executor's, and the cost of asking mid-build is a human
    interrupted for something that may not matter."""
    backend, err = open_backend(root)
    if err:
        return emit_err(args.json, err)
    info, err = backend.read_spec(args.spec)
    if err:
        return emit_err(args.json, err)
    entry = f"- {args.text.strip()}"
    sec = info["sections"].get("Discoveries")
    if sec and sec["filled"]:
        block = f"## Discoveries\n{sec['body'].rstrip()}\n{entry}\n"
    else:
        block = f"## Discoveries\n\n{entry}\n"
    new_text, _ = upsert_section(info, "Discoveries", block)
    backend.write_spec(info, new_text)
    emit(args.json,
         {"ok": True, "slug": info["slug"], "entry": args.text.strip()},
         f"recorded in ## Discoveries: {args.text.strip()}")
    return 0


# --------------------------------------------------------------------------- #
# migrate (one-way, v1 -> v2)
# --------------------------------------------------------------------------- #
# Where each v1 artifact's sections land. `## Context` and `## Decisions` merge into the
# single `## Design`; everything else is a rename. The v1 heading is matched
# case-insensitively and its body is carried VERBATIM — a migration must not rewrite prose
# it does not understand.
V1_MAP = {
    "proposal.md": [("Why", "Problem"), ("What Changes", "Proposal"),
                    ("Out of Scope", "Out of Scope"), ("Validation", "Validation"),
                    ("Impact", "Impact")],
    "design.md": [("Context", "Design"), ("Decisions", "Design"),
                  ("Alternatives Considered", "Alternatives Considered"),
                  ("Open Decisions", "Open Decisions"), ("Risks", "Risks")],
}
MIGRATE_NONE = "- none — not recorded in the v1 plan"


def _git_first_commit_date(path: str) -> str | None:
    """The path's first commit date — used only when `.specs.json` has no `created`.

    A birth date is never INVENTED: this walks git history for the real one, and the caller
    falls back to the file's mtime rather than to today."""
    out = _git(os.path.dirname(os.path.abspath(path)),
               "log", "--diff-filter=A", "--follow", "--format=%ad", "--date=short",
               "--", path)
    lines = [l.strip() for l in out.splitlines() if l.strip()]
    return lines[-1] if lines else None


def _birth_date(meta: dict, path: str) -> str:
    created = str(meta.get("created", "") or "")
    if re.match(r"^\d{4}-\d{2}-\d{2}", created):
        return created[:10]
    git = _git_first_commit_date(path)
    if git:
        return git
    try:
        return datetime.date.fromtimestamp(os.path.getmtime(path)).isoformat()
    except OSError:
        return today()


def _v1_sections(plan_dir: str) -> dict[str, list[str]]:
    """Collect v1 bodies keyed by their V2 heading, in canonical order."""
    collected: dict[str, list[str]] = {}
    for fname, pairs in V1_MAP.items():
        text = read_text(os.path.join(plan_dir, fname))
        if text is None:
            continue
        secs = parse_sections(body_after_frontmatter(text))
        lower = {k.lower(): v for k, v in secs.items()}
        for v1h, v2h in pairs:
            sec = lower.get(v1h.lower())
            if sec and sec["filled"]:
                body = sec["body"].strip()
                # `## Context` and `## Decisions` both land in `## Design`
                collected.setdefault(v2h, []).append(
                    f"### {v1h}\n\n{body}" if v2h == "Design" else body)
    tasks_text = read_text(os.path.join(plan_dir, "tasks.md"))
    if tasks_text is not None:
        body = body_after_frontmatter(tasks_text)
        body = re.sub(r"(?m)^#\s+.*$", "", body, count=1)     # drop the `# Tasks — X` title
        # v1 grouped tasks under `## N.`; v2 nests them under the `## Tasks` section
        body = re.sub(r"(?m)^## ", "### ", body)
        if has_real_content(body):
            collected["Tasks"] = [body.strip()]
    return collected


def _migrate_plan(root: str, name: str, dry: bool) -> dict:
    plan_dir = os.path.join(root, name)
    meta_txt = read_text(os.path.join(plan_dir, ".specs.json")) or "{}"
    try:
        meta = json.loads(meta_txt)
    except json.JSONDecodeError:
        meta = {}
    # A v1 folder was normally a bare name, but some carried a `YYYY-MM-DD-` prefix. Left
    # in, that prefix ends up INSIDE the slug and the date is then prepended again, so the
    # fold emits `2026-01-05-2026-01-05-thing.md` with a date buried in its identity key.
    m = re.match(r"^(\d{4}-\d{2}-\d{2})-(.+)$", name)
    slug = slugify(m.group(2) if m else name)
    date = m.group(1) if m else _birth_date(meta, os.path.join(plan_dir, ".specs.json"))
    collected = _v1_sections(plan_dir)
    # v1 sorted a plan by whether it had tasks; v3 has one folder, so what that sorting
    # decided is now a derived stage. The gate a v1 plan must still satisfy is the ready
    # set when it carried tasks (it was buildable) and plans/'s own entry gate otherwise.
    dest_phase = "plans"
    gate = (ready_gate()["sections"] if collected.get("Tasks")
            else phase_spec(dest_phase).get("entryGate", []))

    fm = [f"slug: {slug}", f"title: {meta.get('title') or titleize(slug)}",
          f"date: {date}", f"verification: {_policy(meta)}"]
    if isinstance(meta.get("refined"), dict) and meta["refined"].get("mode"):
        r = meta["refined"]
        fm.append(f"refined: {{mode: {r.get('mode')}, date: {r.get('date', date)}}}")

    parts = ["---", *fm, "---", "", f"# {meta.get('title') or titleize(slug)}", ""]
    for h in canonical_headings():
        if h in collected:
            parts += [f"## {h}", "", "\n\n".join(collected[h]), ""]
        elif h in gate:
            # the destination's gate must be satisfiable, and an explicit none that SAYS
            # the v1 plan never recorded it is a fact — not an invented answer
            parts += [f"## {h}", "", MIGRATE_NONE, ""]
    body = "\n".join(parts).rstrip() + "\n"

    strays = sorted(f for f in os.listdir(plan_dir)
                    if f not in (".specs.json", "proposal.md", "design.md", "tasks.md")
                    and os.path.isfile(os.path.join(plan_dir, f)))
    dest = os.path.join(root, dest_phase, f"{slug}.md")
    rec = {"from": f"{name}/", "slug": slug, "to": f"{dest_phase}/{slug}.md",
           "date": date, "dateSource": "created" if meta.get("created") else "git/mtime",
           "sections": sorted(collected), "strays": strays}
    if dry:
        return rec
    os.makedirs(os.path.join(root, dest_phase), exist_ok=True)
    write_text(dest, body)
    for f in (".specs.json", "proposal.md", "design.md", "tasks.md"):
        p = os.path.join(plan_dir, f)
        if os.path.isfile(p):
            os.remove(p)
    if not strays:
        try:
            os.rmdir(plan_dir)
        except OSError:
            rec["kept"] = True
    else:
        rec["kept"] = True          # never delete a folder still holding a human's file
    return rec


def _migrate_task(root: str, path: str, dry: bool) -> dict:
    text = read_text(path) or ""
    fm = parse_frontmatter(text)
    slug = slugify(os.path.splitext(os.path.basename(path))[0])
    stamp = str(fm.get("timestamp", ""))
    date = stamp[:10] if re.match(r"^\d{4}-\d{2}-\d{2}", stamp) else _birth_date({}, path)
    body = strip_comments(body_after_frontmatter(text)).strip()
    body = re.sub(r"(?m)^#\s+.*$", "", body, count=1).strip()
    problem = fm.get("description") or body or titleize(slug)
    extra = [f"{k}: {fm[k]}" for k in ("priority", "tags", "complexity") if fm.get(k)]
    if extra:
        problem += f"\n\n_(v1 backlog task — {' · '.join(extra)})_"
    if body and fm.get("description") and body not in problem:
        problem += f"\n\n{body}"
    out = ["---", f"slug: {slug}", f"title: {fm.get('title') or titleize(slug)}",
           f"date: {date}", f"verification: {DEFAULT_VERIFICATION}", "---", "",
           f"# {fm.get('title') or titleize(slug)}", "", "## Problem", "", problem, ""]
    dest = os.path.join(root, "plans", f"{slug}.md")
    rec = {"from": f"backlog/{os.path.basename(path)}", "slug": slug,
           "to": f"plans/{slug}.md", "date": date, "kind": "task"}
    if dry:
        return rec
    os.makedirs(os.path.join(root, "plans"), exist_ok=True)
    write_text(dest, "\n".join(out).rstrip() + "\n")
    os.remove(path)
    return rec


def _v2_leftovers(root: str) -> list[dict]:
    """Every spec file still sitting in a v2 folder, in scan order.

    It used to be a pure FILE MOVE — v2 and v3 spec files were the same format and only the
    folder had changed, so the file was never opened, never reformatted and never renamed.
    That stopped being true when the capture date left the basename: a v2 file is named
    `YYYY-MM-DD-<slug>.md` and carries no `date:`, which is a format difference and not a
    location one. So BOTH names are collected here, and `_migrate_v2_file` moves the already
    conformant one untouched and rewrites the dated one."""
    out = []
    for folder in LEGACY_PHASES:
        d = os.path.join(root, folder)
        if not os.path.isdir(d):
            continue
        for name in sorted(os.listdir(d)):
            if not os.path.isfile(os.path.join(d, name)):
                continue
            if SPEC_FILE_RE.match(name) or LEGACY_DATED_FILE_RE.match(name):
                out.append({"folder": folder, "file": name,
                            "path": os.path.join(d, name)})
    return out


def _migrate_v2_file(root: str, item: dict, dry: bool) -> dict:
    """Move one v2 spec file into `plans/`, renaming it only if it still carries a date.

    A file already named `<slug>.md` is moved and NOT opened — the lossless case the v2 fold
    was written for, and the one that still works on a file this tool could not parse. A
    `YYYY-MM-DD-<slug>.md` one is the format change: the date is the only copy of a fact the
    basename is about to stop holding, so it is written into the frontmatter as `date:`
    BEFORE the rename, and never dropped on the floor."""
    dest_dir = os.path.join(root, "plans")
    legacy = LEGACY_DATED_FILE_RE.match(item["file"])
    slug = legacy.group(2) if legacy else SPEC_FILE_RE.match(item["file"]).group(1)
    name = f"{slug}.md" if legacy else item["file"]
    rec = {"from": f"{item['folder']}/{item['file']}", "slug": slug,
           "to": f"plans/{name}", "kind": "v2-file"}
    if legacy:
        rec["date"] = legacy.group(1)
    if dry:
        return rec
    os.makedirs(dest_dir, exist_ok=True)
    if legacy:
        text = read_text(item["path"]) or ""
        # Only when it has none of its own: a v2 file that somebody already gave a `date:`
        # has a human's answer in it, and the basename is the derived copy, not the source.
        if not str(parse_frontmatter(text).get("date", "")).strip():
            write_text(item["path"], set_frontmatter_key(text, "date", legacy.group(1)))
    os.rename(item["path"], os.path.join(dest_dir, name))
    return rec


def _migrate_markers(backend, dry: bool) -> list[dict]:
    """Fold every spec an external backend still stores under a dated basename.

    ONE WRITE PER SPEC, and the document that goes out has already been proved: the fold is
    `legacy_marker_fold` — the same pure function `selftest` exercises — and the write is
    `write_spec`, the same path every other command uses. Nothing here has a serialisation of
    its own, because a migration with its own writer is a second implementation that only
    ever runs once, on the day it matters most.

    `--dry-run` performs the WHOLE fold offline and compares byte for byte, so the answer to
    "will this lose anything" is measured against the real corpus rather than argued."""
    out: list[dict] = []
    for number, filename, head, parts, _title in backend.legacy_rows():
        text = head if parts <= 1 else backend._joined(number, head, parts)
        folded = legacy_marker_fold(filename, text)
        if folded is None:
            continue
        name, new_text = folded
        slug = SPEC_FILE_RE.match(name).group(1)
        # What the store WILL hold, and what a read WILL rebuild from it — run here, before
        # anything is sent, so a document that would not survive is reported and skipped
        # rather than written and lost.
        body, native = hybrid_project(slug, new_text)
        chunks = hybrid_split(body, GH_PART_MAX)
        rebuilt = hybrid_title_join(hybrid_join(
            [(chunks[0][0].replace("\r\n", "\n"), False)]
            + [(c.replace("\r\n", "\n"), eol) for c, eol in chunks[1:]]), native)
        rec = {"issue": number, "from": filename, "to": name, "slug": slug,
               "date": str(parse_frontmatter(new_text).get("date", "")),
               "parts": len(chunks), "projectedTitle": hybrid_title_split(new_text) is not None,
               "roundTrip": rebuilt == new_text}
        if not rec["roundTrip"]:
            rec["skipped"] = "the document would not come back byte for byte"
            out.append(rec)
            continue
        if not dry:
            # The number came from this scan, so no lookup and no re-listing between writes.
            backend._store(number, slug, name, new_text, parts)
        out.append(rec)
    return out


def cmd_migrate(args, root: str) -> int:
    """One-way, to the CURRENT layout. `specs/archive/**` is NEVER touched — it is
    historical and read-only, and churning it would break every link into it for no gain.

    Two folds, either of which may apply:
      v1 -> v3   a three-file plan folder (or a v1 backlog task) becomes one spec file
      v2 -> v3   `backlog/` and `ready/` move into `plans/`, basenames unchanged

    The v2 fold moves files and nothing else: same format, same name, only the folder
    changed. Refuses (exit 2) when neither fold applies, so a second run cannot quietly
    re-migrate an already-converted workspace."""
    plans = _v1_leftovers(root)
    tasks = []
    bdir = os.path.join(root, "backlog")
    if os.path.isdir(bdir):
        for name in sorted(os.listdir(bdir)):
            p = os.path.join(bdir, name)
            # A conformant spec file in `backlog/` — under EITHER name — is the v2 fold's,
            # not the v1 task fold's. Matching only the current name would hand every dated
            # v2 file to the task fold, which rewrites it into a `## Problem` stub.
            if (name == "index.md" or not os.path.isfile(p)
                    or SPEC_FILE_RE.match(name) or LEGACY_DATED_FILE_RE.match(name)):
                continue
            if str(parse_frontmatter(read_text(p) or "").get("type", "")) == "task":
                tasks.append(p)
    v2 = _v2_leftovers(root)

    # The external fold: specs an issue tracker still holds under the dated basename. It is
    # asked of the backend, not of the filesystem, and it is the only fold that can apply to a
    # repo with no `specs/` folder at all.
    markers: list[dict] = []
    backend, berr = open_backend(root)
    if not berr and backend is not None and hasattr(backend, "legacy_rows"):
        markers = _migrate_markers(backend, args.dry_run)
        if markers:
            broken = [r for r in markers if not r["roundTrip"]]
            emit(args.json,
                 {"ok": not broken, "root": root, "dryRun": bool(args.dry_run),
                  "kind": "markers", "count": len(markers),
                  "projected": sum(1 for r in markers if r["projectedTitle"]),
                  "spilled": sum(1 for r in markers if r["parts"] > 1),
                  "skipped": broken, "specs": markers},
                 f"{'would fold' if args.dry_run else 'folded'} {len(markers)} spec(s) out of "
                 f"the dated basename" + (f" — {len(broken)} SKIPPED, see --json" if broken
                                          else ", all byte-for-byte"))
            return 1 if broken else 0

    if not plans and not tasks and not v2:
        emit(args.json, {"ok": False, "code": "sp-nothing-to-migrate", "root": root,
                         "message": "no v1 plan folders, no v1 backlog tasks, no specs in "
                                    "backlog/ or ready/ and no dated markers — this workspace "
                                    "is already current"},
             "refused: nothing to migrate — this workspace is already current")
        return 2

    # A name collision is the one way this could destroy work, so it is checked for the
    # WHOLE set before a single file moves — a partial migration is worse than none.
    dest_dir = os.path.join(root, "plans")
    clashes = []
    seen: dict[str, str] = {}
    for it in v2:
        if os.path.exists(os.path.join(dest_dir, it["file"])):
            clashes.append(f"{it['folder']}/{it['file']} — plans/{it['file']} already exists")
        if it["file"] in seen:
            clashes.append(f"{it['folder']}/{it['file']} — same basename as "
                           f"{seen[it['file']]}/{it['file']}")
        seen[it["file"]] = it["folder"]
    if clashes:
        emit(args.json, {"ok": False, "code": "sp-migrate-collision", "root": root,
                         "collisions": clashes,
                         "message": f"{len(clashes)} destination collision(s) — nothing moved"},
             f"refused: {len(clashes)} destination collision(s) — nothing moved\n" +
             "\n".join(f"  {c}" for c in clashes))
        return 2

    migrated = [_migrate_plan(root, n, args.dry_run) for n in plans]
    migrated += [_migrate_task(root, p, args.dry_run) for p in tasks]
    migrated += [_migrate_v2_file(root, it, args.dry_run) for it in v2]

    # An emptied v2 folder is removed; one still holding anything (a customized index.md,
    # a human's stray note) is KEPT and named, never deleted on a guess.
    kept_dirs = []
    if not args.dry_run:
        for folder in LEGACY_PHASES:
            d = os.path.join(root, folder)
            if not os.path.isdir(d):
                continue
            try:
                os.rmdir(d)
            except OSError:
                kept_dirs.append(f"{folder}/ ({', '.join(sorted(os.listdir(d))[:4])})")

    obj = {"ok": True, "dryRun": bool(args.dry_run), "root": root,
           "migrated": migrated,
           "archiveUntouched": True,
           "keptFolders": kept_dirs,
           "kept": [m["from"] for m in migrated if m.get("kept")]}
    if args.json:
        print(json.dumps(obj, indent=2, ensure_ascii=False))
    else:
        verb = "would migrate" if args.dry_run else "migrated"
        print(f"{verb} {len(migrated)} item(s) — specs/archive/** untouched")
        for m in migrated:
            src = m.get("dateSource")
            print(f"  {m['from']:<40} → {m['to']}" +
                  (f"   (date from {src})" if src else ""))
            if m.get("strays"):
                print(f"      kept, still holds: {', '.join(m['strays'])}")
        for k in kept_dirs:
            print(f"  kept (not empty): {k}")
    return 0


# --------------------------------------------------------------------------- #
# validate / doctor
# --------------------------------------------------------------------------- #
def _finding(code: str, severity: str, message: str, **extra) -> dict:
    return {"code": code, "severity": severity, "message": message, **extra}


def validate_spec(backend: SpecBackend, s: dict) -> list[dict]:
    """Every finding for ONE spec file, in the v2 `sp-*` vocabulary.

    The phase-scoped rule is asserted against the schema's per-phase sets — the SAME sets
    `promote` gates on, so the two can never drift into disagreeing about what a phase
    requires.

    ASKED OF THE BACKEND, never of the path — and the derivation is the shared one, so this
    validates the same `frontmatter`/`sections`/`tasks` every other command reads. Against
    GitHub the locator is an issue URL, so `read_text` returned nothing and EVERY spec was
    reported missing every required key: 210 fabricated findings on this repository, from
    documents that were entirely well-formed."""
    where = f"{s['folder']}/{s['file']}"
    info, rerr = backend.read_spec(s["slug"])
    if rerr or info is None:
        # The only refusal reachable here is an ambiguous slug — it came from the listing, so
        # it cannot be unknown — and `cmd_validate` already names it `sp-duplicate-slug`.
        # Deriving from an empty document instead, as `list` does to keep its row, would
        # report a well-formed spec as missing everything: the same fabrication this function
        # exists to stop, just narrowed to the duplicates.
        return []
    text, fm = info["text"], info["frontmatter"]
    sections, tasks = info["sections"], info["tasks"]
    out: list[dict] = []

    # BEFORE the required-key checks, so a parse failure is never presented as a
    # content gap — a value this parser could not represent used to surface as a
    # missing `title`, naming the absence rather than the misread that caused it.
    for a in frontmatter_anomalies(text):
        out.append(_finding("sp-frontmatter-unparsed", "warn",
                            f"{where}: `{a['key']}`: {a['detail']}", spec=s["slug"], path=where,
                            kind=a["kind"], key=a["key"],
                            remedy="quote the value, or write the comment on its own line — "
                                   "see docs/standards/code/frontmatter-parsing.md"))

    schema = load_schema()
    for key in schema.get("frontmatter", {}).get("required", []):
        if not str(fm.get(key, "")).strip():
            out.append(_finding("sp-missing-frontmatter", "error",
                                f"{where}: frontmatter has no `{key}`", spec=s["slug"],
                                path=where, remedy=f"add `{key}:` to the frontmatter"))
    if fm.get("slug") and fm["slug"] != s["slug"]:
        out.append(_finding("sp-slug-mismatch", "error",
                            f"{where}: frontmatter slug `{fm['slug']}` disagrees with the "
                            f"filename suffix `{s['slug']}`", spec=s["slug"], path=where,
                            remedy="make the frontmatter slug match the filename"))
    pol = str(fm.get("verification", "")).strip().lower()
    if pol and pol not in VERIFICATION_POLICIES:
        out.append(_finding("sp-bad-verification", "error",
                            f"{where}: verification `{pol}` is not one of "
                            f"{', '.join(VERIFICATION_POLICIES)}", spec=s["slug"], path=where,
                            remedy=f"set verification to one of {', '.join(VERIFICATION_POLICIES)}"))

    for h in stray_headings(sections, schema):
        out.append(_finding("sp-stray-heading", "warn",
                            f"{where}: `## {h}` is not one of the fourteen canonical headings",
                            spec=s["slug"], path=where, heading=h,
                            remedy="rename it to a canonical heading or fold it into one"))

    # The phase-scoped rule governs whether a heading must be PRESENT — so `missing` is
    # checked only against the gate of the phase this spec is IN.
    gates = gate_report({"sections": sections}, s["phase"], schema)
    for h in gates["missing"]:
        out.append(_finding("sp-gate-unmet", "warn",
                            f"{where}: `## {h}` is required in {s['phase']}/ and is absent",
                            spec=s["slug"], path=where, heading=h,
                            remedy=f"specs.py section {s['slug']} \"{h}\" --write"))
    # Malformed is NOT phase-scoped. Once a heading exists it must say something, in any
    # phase: it is neither an answer nor a not-yet, and leaving it for the promote to catch
    # means a spec looks fine right up until the gate refuses it.
    for h in canonical_headings(schema):
        if section_state(sections, h) == "empty":
            out.append(_finding("sp-empty-section", "error",
                                f"{where}: `## {h}` is present but empty — neither an answer "
                                f"nor a not-yet", spec=s["slug"], path=where, heading=h,
                                remedy="fill it, or write `- none — <reason>`"))
    # `Handoff` used to be warned on by the ready/ FOLDER. With one folder the same
    # question is asked of the derived ready gate: a spec nobody could build yet is not
    # missing an executor's context, and a spec that is buildable is.
    ready = ready_report({"sections": sections}, schema) if s["phase"] == "plans" else None
    if ready and ready["ok"]:
        for h in ready["warn"]:
            if h == "Overview":
                out.append(_finding("sp-overview-missing", "warn",
                                    f"{where}: `## Overview` is empty in a spec that meets "
                                    f"the ready gate — a reader gets no orientation",
                                    spec=s["slug"], path=where, heading=h,
                                    remedy=f"specs.py section {s['slug']} \"Overview\" --write, "
                                           "written last once the other sections settle"))
            else:
                out.append(_finding("sp-handoff-empty", "warn",
                                    f"{where}: `## {h}` is empty in a spec that meets the ready "
                                    f"gate — an executor gets no context", spec=s["slug"],
                                    path=where, heading=h,
                                    remedy="rewrite it after each committed task"))

    declared = parse_impact_standards(text, schema)
    if declared:
        named = "\n".join(t["text"] for t in tasks)
        for p in declared:
            if p not in named:
                out.append(_finding("sp-impact-uncovered", "warn",
                                    f"{where}: `{p}` is declared under ## Impact but no task "
                                    f"names it", spec=s["slug"], path=where, standard=p,
                                    remedy="add a task that writes it, or drop the declaration"))

    # Judged against the READY gate: a spec is "unrefined" once it could be built, not the
    # moment it is captured. Warning on every fresh capture would train the reader to
    # ignore the code.
    if ready and ready["ok"] and not fm.get("refined"):
        out.append(_finding("sp-unrefined", "warn",
                            f"{where}: ready to build, but nobody has interrogated it",
                            spec=s["slug"], path=where,
                            remedy="run a refinement pass, or build as-is (never gated)"))
    if s["phase"] == "archive" and not fm.get("outcome"):
        out.append(_finding("sp-no-outcome", "warn",
                            f"{where}: archived with no `outcome:` — done and abandoned "
                            f"read alike", spec=s["slug"], path=where,
                            remedy="stamp `outcome: done` or `outcome: abandoned`"))
    merge_finding = merge_record_finding(fm, where, s["slug"])
    if merge_finding:
        out.append(merge_finding)
    return out


def merge_record_finding(fm: dict, where: str, slug: str) -> dict | None:
    """Whether a `merge:` record still says which commit carries the merge.

    TWO forms are legal and both are read forever: the current `{strategy, subject}`, and
    `{strategy, commit}` on a spec archived before the anchor became the subject. The older
    one is never rewritten — a recorded sha describes a commit that exists, and editing an
    archived spec to "fix" it would be a lie about when the record was made."""
    rec = fm.get("merge")
    if not rec:
        return None
    remedy = ("stamp `merge: {strategy: <one of " + ", ".join(MERGE_STRATEGIES) +
              ">, subject: <the merge commit's subject>}`")
    if not isinstance(rec, dict):
        return _finding("sp-bad-merge", "warn",
                        f"{where}: `merge:` is not a {{strategy, subject}} record",
                        spec=slug, path=where, remedy=remedy)
    strategy = str(rec.get("strategy", "")).strip().lower()
    subject = str(rec.get("subject", "")).strip()
    if strategy not in MERGE_STRATEGIES:
        return _finding("sp-bad-merge", "warn",
                        f"{where}: merge strategy `{strategy or '(unset)'}` is not one of "
                        f"{', '.join(MERGE_STRATEGIES)}", spec=slug, path=where,
                        remedy=remedy)
    if not subject:
        if str(rec.get("commit", "")).strip():
            return None          # the older form, read and left exactly as it was written
        return _finding("sp-bad-merge", "warn",
                        f"{where}: `merge:` names a strategy but nothing to resolve the "
                        f"merge by", spec=slug, path=where, remedy=remedy)
    anchorless = strategy in MERGE_ANCHORLESS_STRATEGIES
    explicit_none = bool(RECORD_NONE_RE.match(subject))
    if anchorless and not explicit_none:
        return _finding("sp-bad-merge", "warn",
                        f"{where}: `{strategy}` creates no merge commit, so `subject:` has "
                        f"nothing to point at", spec=slug, path=where,
                        remedy="write `subject: none — <why>`")
    if not anchorless and explicit_none:
        return _finding("sp-bad-merge", "warn",
                        f"{where}: `{strategy}` creates a merge commit, so `subject:` must "
                        f"name it rather than be an explicit none", spec=slug, path=where,
                        remedy=remedy)
    return None


def cmd_validate(args, root: str) -> int:
    backend, err = open_backend(root)
    if err:
        return emit_err(args.json, err)
    specs = backend.list_specs()
    findings: list[dict] = []

    seen: dict[str, list[str]] = {}
    for s in specs:
        seen.setdefault(s["slug"], []).append(f"{s['phase']}/{s['file']}")
    for slug, paths in seen.items():
        if len(paths) > 1:
            findings.append(_finding("sp-duplicate-slug", "error",
                                     f"slug `{slug}` resolves to {len(paths)} files: "
                                     f"{', '.join(paths)}", spec=slug,
                                     remedy="rename one — a slug is an identity, and two "
                                            "matches makes every command refuse"))

    for ph in PHASES:
        d = os.path.join(root, ph)
        if not os.path.isdir(d):
            continue
        for name in sorted(os.listdir(d)):
            if name == "index.md" or name.startswith("."):
                continue
            if os.path.isdir(os.path.join(d, name)):
                # archive/ is DELIBERATELY not migrated — it is historical and read-only, so
                # its v1 `YYYY-MM-DD-<name>/` plan folders are expected, not strays. Flagging
                # them would push a reader to migrate the one tree the design protects.
                if ph == "archive":
                    continue
                findings.append(_finding("sp-stray-dir", "warn",
                                         f"{ph}/{name}/ is a directory — v2 specs are files",
                                         path=f"{ph}/{name}",
                                         remedy="a v1 plan folder? run `specs.py migrate`"))
            elif not SPEC_FILE_RE.match(name):
                dated = LEGACY_DATED_FILE_RE.match(name)
                findings.append(_finding("sp-bad-filename", "error",
                                         f"{ph}/{name} is not `<slug>.md`",
                                         path=f"{ph}/{name}",
                                         remedy="run `specs.py migrate` — the date belongs in "
                                                "`date:` now, not in the basename"
                                         if dated else
                                         "rename it to the one filename pattern all "
                                         "three folders share"))

    target = [s for s in specs if s["slug"] == args.spec] if args.spec else specs
    if args.spec and not target:
        emit(args.json, {"ok": False, "code": "sp-unknown-slug", "slug": args.spec,
                         "message": f"no spec with slug '{args.spec}'"},
             f"error: no spec with slug '{args.spec}'")
        return 1
    for s in target:
        findings.extend(validate_spec(backend, s))

    errors = [f for f in findings if f["severity"] == "error"]
    if args.json:
        print(json.dumps({"ok": not errors, "root": root, "specs": len(specs),
                          "findings": findings}, indent=2, ensure_ascii=False))
    else:
        print(f"specs validate — {root} ({len(errors)} error(s), "
              f"{len(findings) - len(errors)} warning(s))")
        for f in findings:
            print(f"  [{f['severity']:<5}] {f['message']}  ({f['code']})")
            if f.get("remedy"):
                print(f"          remedy: {f['remedy']}")
        if not findings:
            print("  OK — every spec conforms.")
    return 1 if findings else 0


def _v1_leftovers(root: str) -> list[str]:
    """A v1 plan folder is a directory at the specs root holding proposal/tasks/.specs.json.

    Detecting it matters more than it looks: v2 `list` globs the three phase folders, so an
    unmigrated v1 workspace reads as EMPTY rather than as wrong-format, and a skill would
    conclude there is no work when there is."""
    out = []
    if not os.path.isdir(root):
        return out
    for name in sorted(os.listdir(root)):
        d = os.path.join(root, name)
        if not os.path.isdir(d) or name in PHASE_DIRS or name.startswith("."):
            continue
        if any(os.path.isfile(os.path.join(d, f))
               for f in (".specs.json", "proposal.md", "tasks.md")):
            out.append(name)
    return out


def _behavioral(node):
    """A schema with the prose stripped. `note`/`why` exist for a human reading
    schema.json; the embedded fallback has never carried them, and they are not what the
    tool branches on."""
    if isinstance(node, dict):
        return {k: _behavioral(v) for k, v in node.items() if k not in ("note", "why")}
    if isinstance(node, list):
        return [_behavioral(v) for v in node]
    return node


def cmd_selftest(args, root: str) -> int:
    """Prove the two duplicated constants have not drifted from their asset files.

    `schema.json` and `templates/spec.md` are each duplicated inside this script, because an
    installed copy under a target's `.claude/hooks/` has no adjacent assets and must still
    behave identically. Duplication is the deliberate cost of being one self-contained file
    — and a duplicate nobody checks is just a bug with a delay on it. This is the check.

    It can only run where the assets are adjacent (the plugin itself); an installed copy has
    nothing to compare against and says so rather than passing vacuously.

    The canonical frontmatter cases are NOT part of that caveat — they are self-contained and
    must run everywhere, which is why they are checked before the early return: an installed
    copy is exactly where a drifted parser would otherwise go unnoticed. The capture-form
    assertion runs there for the same reason, and covers what a byte-for-byte comparison
    structurally cannot: whether `new` still stamps the headings its own gate requires."""
    findings: list[dict] = []
    for failure in canonical_case_failures():
        findings.append(_finding("sp-frontmatter-case", "error",
                                 f"canonical frontmatter case — {failure}",
                                 remedy="this parser disagrees with the case list in "
                                        "docs/standards/code/frontmatter-parsing.md; the three "
                                        "tools move together or not at all"))

    # The section rule, against the SAME canonical list `skills.py` proves. Self-contained,
    # so it runs on an installed copy too — which is exactly where a `## ` inside a shell
    # block in somebody's `## Tasks` would otherwise open a phantom section unnoticed.
    # The identity key, on the accented input this repository actually captures. Self-contained,
    # so it runs on an installed copy — which is where a slug quietly losing a letter would
    # otherwise surface only as a spec nobody can resolve by name.
    # The four rungs of slug resolution, plus the one that must not fire.
    for failure in resolution_failures():
        findings.append(_finding("sp-resolution-case", "error",
                                 f"slug resolution — {failure}",
                                 remedy="resolve_one tries exact slug, exact title, then one "
                                        "close match above the threshold; a tie is exit 2 and "
                                        "an approximation announces itself"))

    for failure in slug_case_failures():
        findings.append(_finding("sp-slug-case", "error", f"canonical slug case — {failure}",
                                 remedy="slugify normalises to NFD and drops combining marks "
                                        "before reducing to kebab; an accent is a letter, "
                                        "never a separator"))

    for failure in section_case_failures():
        findings.append(_finding("sp-section-case", "error",
                                 f"canonical section case — {failure}",
                                 remedy="this reader disagrees with SECTION_CASES, which "
                                        "`skills.py` carries verbatim; the two tools move "
                                        "together or not at all"))

    # What `new` actually stamps, asserted against the gate rather than eyeballed. Runs on
    # TEMPLATE_SPEC, so it is self-contained and fires on an installed copy too — and it is
    # checked BEFORE the early return for the same reason the frontmatter cases are.
    #
    # This is the assertion the byte-for-byte drift check below cannot make. Adding
    # `## Overview` ahead of `## Problem` kept both template copies identical, so drift
    # passed — while capture, which sliced to the second `## ` heading, silently started
    # stamping an empty `## Overview` and dropping `## Problem`. Position is not what makes a
    # heading part of capture; gate membership is, and that is what this checks.
    stamped = capture_form(TEMPLATE_SPEC, DEFAULT_SCHEMA)
    gate = phase_spec("plans", DEFAULT_SCHEMA).get("entryGate", [])
    present = {h for h in canonical_headings(DEFAULT_SCHEMA)
               if re.search(rf"^## {re.escape(h)}\s*$", stamped, re.M)}
    for h in [x for x in gate if x not in present]:
        findings.append(_finding("sp-capture-gate-missing", "error",
                                 f"the capture form omits `## {h}`, which the plans entry "
                                 f"gate requires — every spec `new` creates would be born "
                                 f"failing its own gate", heading=h,
                                 remedy="capture_form() slices by entryGate membership; a "
                                        "heading in the gate must appear in what `new` stamps"))
    for h in sorted(present - set(gate)):
        findings.append(_finding("sp-capture-extra-heading", "error",
                                 f"the capture form stamps `## {h}`, which is not in the "
                                 f"plans entry gate — stamped empty, it is malformed "
                                 f"(sp-empty-section) from the moment the spec exists",
                                 heading=h,
                                 remedy="capture_form() must stamp the entry-gate headings "
                                        "and nothing else"))

    # The retirement of `plans/index.md`: the artifact is gone, so the subcommand that
    # rebuilt its GENERATED zone must not come back. Asserted against BOTH surfaces a
    # caller can reach — argparse decides what the CLI accepts, DISPATCH decides what
    # actually runs — because re-adding either alone is the shape a partial revert takes.
    # Self-contained, and checked before the early return: an installed copy is where a
    # resurrected subcommand would otherwise go unnoticed for months.
    _, _sub = build_parser()
    for surface, present in (("the argparse surface", "plans" in _sub.choices),
                             ("DISPATCH", "plans" in DISPATCH)):
        if present:
            findings.append(_finding("sp-plans-subcommand-back", "error",
                                     f"`plans` is back in {surface} — the listing it "
                                     f"reindexed was retired, so nothing is left to rebuild",
                                     remedy="`plans/index.md` is a retired artifact: no "
                                            "command produces it and none may reindex it"))

    # The guard that keeps the `files` backend from breaking the clean-tree gate it runs
    # under. Asserted on the pure half, so it needs no repository staged and runs on an
    # installed copy too — which is where a guard quietly downgraded to a warning, or to
    # `{}` on both branches, would otherwise never be noticed.
    for ignored, want in ((True, False), (False, True)):
        got = worktree_guard(ignored)
        if bool(got) is not want:
            findings.append(_finding("sp-worktree-guard-broken", "error",
                                     f"worktree_guard(ignored={ignored}) "
                                     f"{'refused' if got else 'allowed'} — an unignored specs "
                                     f"worktree must refuse, and an ignored one must proceed",
                                     remedy="the guard is the only thing standing between the "
                                            "files backend and the clean-tree gate it needs"))
    refusal = worktree_guard(False)
    if refusal.get("exit") != 2:
        findings.append(_finding("sp-worktree-guard-broken", "error",
                                 f"the unignored-worktree refusal exits "
                                 f"{refusal.get('exit')!r}, not 2 — a missing `.gitignore` line "
                                 f"is a refusal the human must fix, not a finding to report",
                                 remedy="exit 2 is this tool's refusal code; 1 is findings"))

    # The three shapes that must NEVER reach for a specs worktree. Getting one of them wrong
    # does not produce a bad answer — it produces a branch and a checkout in a repository that
    # asked for neither, or a workspace full of specs reported as empty.
    for failure in files_root_failures():
        findings.append(_finding("sp-files-root-drift", "error",
                                 f"the files root resolved wrong — {failure}",
                                 remedy="resolve_files_root answers the git-free shapes first: "
                                        "already inside a worktree, a populated pre-migration "
                                        "workspace, no repository at all"))

    # The lock, asserted in the direction that loses work: taken while held, or a holder judged
    # gone on evidence that does not prove it. Both decide silently, and both end in an edit
    # nobody can find afterwards.
    for failure in lock_failures():
        findings.append(_finding("sp-lock-broken", "error",
                                 f"the specs worktree lock is unsound — {failure}",
                                 remedy="one writer per worktree, held for the whole command; "
                                        "a lock is only ever reclaimed on proof the holder is "
                                        "gone, never on its age"))

    # The claim the configurable-backend design rests on, checked rather than asserted in
    # prose. Runs before the early return: an installed copy is exactly where a backend that
    # quietly started deriving its own stages would go unnoticed.
    for failure in backend_equivalence_failures():
        findings.append(_finding("sp-backend-divergence", "error",
                                 f"backends disagree — {failure}",
                                 remedy="every backend supplies the canonical document and "
                                        "derives nothing; a difference outside `path` and "
                                        "`text` means one of them is deriving its own"))

    # The records, which no other check covers: they are frontmatter rather than a section,
    # so the canonical case list never sees them, and they are written once and read forever.
    for failure in record_round_trip_failures():
        findings.append(_finding("sp-record-round-trip-broken", "error",
                                 f"a record does not read back as written — {failure}",
                                 remedy="flow (`{a: b}`) only where it survives the round "
                                        "trip; a comma-carrying or long value goes in the "
                                        "block form, and a re-stamp replaces the old "
                                        "field lines rather than orphaning them"))

    # The `github` transport's promise that no failure reaches a human as a traceback, and
    # that each one arrives with the remedy that fixes it. Asserted against gh's literal
    # stderr, so a reworded release breaks the check rather than the refusal. Needs no
    # network and no `gh`, and runs before the early return for the same reason the rest do.
    for failure in gh_refusal_failures():
        findings.append(_finding("sp-gh-refusal-broken", "error",
                                 f"the gh transport misreports a failure — {failure}",
                                 remedy="a missing binary, an unauthenticated one and an API "
                                        "error are three refusals with three remedies; all "
                                        "exit 2 and none is a traceback"))

    # What `azure-boards` has instead of an end-to-end run, and the reason it runs before
    # the early return: a primitive left inherited reaches a human as a traceback, which is
    # the one thing every external backend promises never to do.
    for failure in backend_completeness_failures():
        findings.append(_finding("sp-backend-incomplete", "error",
                                 f"a backend is half-implemented — {failure}",
                                 remedy="all five primitives on every declared backend; a "
                                        "failure travels as a BackendRefusal carrying its "
                                        "own remedy, never as an exception"))

    # The `azure-boards` transport's half of the same promise, and the reason it is its own
    # check: `az` has no dedicated exit code for "not logged in", so every refusal here is
    # split on what stderr SAID. A reworded release must break this check rather than start
    # telling a human to log in when the real fix is installing the extension.
    for failure in az_refusal_failures():
        findings.append(_finding("sp-az-refusal-broken", "error",
                                 f"the az transport misreports a failure — {failure}",
                                 remedy="a missing binary, a missing azure-devops "
                                        "extension, an unauthenticated identity and an API "
                                        "error are four refusals with four remedies; all "
                                        "exit 2 and none is a traceback"))

    # The other thing `azure-boards` ships with instead of proof: the warning that says so.
    # It runs here, beside the two checks above, because all three answer the same question
    # — what an unproved backend owes the human who selects it — and because a warning that
    # silently stopped firing would leave that debt unpaid with nothing to show for it.
    for failure in unproved_backend_failures():
        findings.append(_finding("sp-unproved-warning-broken", "error",
                                 f"the unproved-backend warning misfires — {failure}",
                                 remedy="one line per process on stderr, only for a backend "
                                        "named in UNPROVED_BACKENDS, never on stdout; the "
                                        "permanent half is doctor's sp-backend-unproved"))

    # The hybrid serialisation's own claim: the canonical document comes back byte for byte,
    # whether it fitted in one issue body or spilled into continuation comments, and it
    # reparses to the same tasks through the one shared derivation.
    for failure in hybrid_serialization_failures():
        findings.append(_finding("sp-gh-doc-serialization-broken", "error",
                                 f"the github document serialisation loses content — {failure}",
                                 remedy="the whole document is stored and returned verbatim; a "
                                        "document over the ceiling splits on line boundaries "
                                        "and joins back with nothing added and nothing dropped"))

    # A document too large for an issue body refuses without making the call, so a migration
    # fails on a named spec instead of on GitHub's anonymous 422.
    for failure in gh_body_ceiling_failures():
        findings.append(_finding("sp-gh-body-ceiling-broken", "error",
                                 f"the issue body ceiling does not hold — {failure}",
                                 remedy="`_write_api` is the one point every write passes "
                                        "through; the check belongs there and must emit no "
                                        "call when it refuses"))

    # The config defaults, asserted where nothing is declared. A repo that declares nothing
    # is the overwhelmingly common case, so a loader that started returning `None` for the
    # backend would break every such repo while every configured one kept working — the
    # failure shape that goes unnoticed longest. Read against a path that cannot exist, so
    # it stays self-contained and never depends on this checkout's own config.
    blank = load_config(os.path.join(os.sep, "nonexistent-specs-root", "specs"))
    for key, want in (("backend", DEFAULT_BACKEND), ("specsBranch", DEFAULT_SPECS_BRANCH),
                      ("worktreeSetup", None), ("present", False)):
        if blank[key] != want:
            findings.append(_finding("sp-config-default-drift", "error",
                                     f"with nothing declared, config `{key}` is "
                                     f"{blank[key]!r} and not {want!r}",
                                     key=key,
                                     remedy="an absent .claude/quenching.json must yield the "
                                            "documented defaults, never a null backend"))

    # The task metadata grammar, asserted key by key rather than eyeballed. Self-contained, so
    # it runs on an installed copy too. Both halves matter: every documented key parses, AND an
    # undocumented one does not — a grammar that admits everything admits the prose under a task.
    for key in TASK_META_KEYS:
        m = TASK_META_RE.match(f"{DEFAULT_META_INDENT}{key}: value")
        if not m or m.group(1).lower() != key:
            findings.append(_finding("sp-task-meta-key", "error",
                                     f"`{key}:` is a documented task metadata key that "
                                     f"TASK_META_RE no longer parses",
                                     remedy="TASK_META_KEYS and the grammar documented in "
                                            "assets/references/specs-develop/artifacts.md "
                                            "§Execution metadata move together"))
    for bad, why in ((f"{DEFAULT_META_INDENT}notakey: value", "an undocumented key"),
                     ("files: value", "an unindented line")):
        if TASK_META_RE.match(bad):
            findings.append(_finding("sp-task-meta-key", "error",
                                     f"TASK_META_RE accepts {why} — the grammar is closed on "
                                     f"both the key list and the indent",
                                     remedy="metadata is indented under its checkbox and drawn "
                                            "from TASK_META_KEYS; anything else is prose"))

    # Admitting a key into the grammar is only half the job — the dispatch has to place it.
    # `constraint:` is inert, so the arm that reads it is *no arm at all*, and the failure this
    # asserts is what an `else: verify = val` fallthrough did: a `constraint:` line after
    # `verify:` silently became the task's verify command, and the loop would have run that
    # prose as shell. Ordering matters to the fixture — constraint must follow verify.
    probe = parse_tasks("## Tasks\n\n### 1. X\n\n"
                        "- [ ] 1.1 t\n"
                        "      verify: THE-REAL-CHECK\n"
                        "      constraint: prose that is not a command\n")
    if not probe or probe[0].get("verify") != "THE-REAL-CHECK":
        findings.append(_finding("sp-task-meta-dispatch", "error",
                                 "a `constraint:` line overwrote the task's `verify:` — an "
                                 "inert key reached the verify arm, so the loop would run "
                                 "prose as the task's shell command",
                                 remedy="the metadata dispatch is exhaustive: every key in "
                                        "TASK_META_KEYS gets its own arm or is deliberately "
                                        "unread — never a trailing `else` that catches it"))

    # `--moment build` is the set `/quenching:specs:execute` step 4 sends an executor — asserted
    # against the literal list rather than eyeballed, so an edit to DEFAULT_SCHEMA that drops or
    # reorders a `moment: build` section is caught here instead of at the first run that pays
    # for it. Self-contained: DEFAULT_SCHEMA, not the loaded schema, so it covers an installed
    # copy with no adjacent assets too.
    want_build = ["Proposal", "Out of Scope", "Impact", "Design", "Handoff", "Tasks"]
    got_build = headings_for_moment("build", DEFAULT_SCHEMA)
    if got_build != want_build:
        findings.append(_finding("sp-moment-build", "error",
                                 f"headings_for_moment('build') is {got_build}, expected "
                                 f"{want_build} — `/quenching:specs:execute` step 4 would read "
                                 f"the wrong section set",
                                 remedy="DEFAULT_SCHEMA's `moment: build` sections must match "
                                        "docs/standards/workflows/plan-artifacts.md §Fourteen "
                                        "canonical sections"))

    # A `## Impact` bullet may carry a `§`address beside its path (the executor's optional
    # narrowing in `/quenching:specs:execute` step 4). `parse_impact_standards` must tolerate
    # it — one bullet addressed, one bare — without a line of code changing. Proved against a
    # fixture, never the real command surface: editing that to pass would prove it by
    # coincidence, not by contract.
    impact_probe = parse_impact_standards(
        "## Impact\n\n### Standards this spec will write into docs/standards/\n\n"
        "- `docs/standards/automation/context-budget.md` §The two caps §The per-surface "
        "ceiling — revisado.\n"
        "- `docs/standards/workflows/plan-artifacts.md` — revisado, sem endereço: o executor "
        "lê inteiro.\n", DEFAULT_SCHEMA)
    want_impact = ["docs/standards/automation/context-budget.md",
                   "docs/standards/workflows/plan-artifacts.md"]
    if impact_probe != want_impact:
        findings.append(_finding("sp-impact-address-tolerance", "error",
                                 f"parse_impact_standards() on a §addressed bullet returned "
                                 f"{impact_probe}, expected {want_impact} — a `§`address beside "
                                 f"the path must not break the declaration it sits on",
                                 remedy="parse_impact_standards must keep matching only the "
                                        "docs/standards/**.md path and ignore the rest of the "
                                        "line, addressed or not"))

    tpl_path = os.path.join(ASSET_DIR, "templates", "spec.md")
    sch_path = os.path.join(ASSET_DIR, "schema.json")
    disk_tpl = read_text(tpl_path)
    disk_sch = read_text(sch_path)

    if disk_tpl is None and disk_sch is None:
        emit(args.json,
             {"ok": not findings, "skipped": True, "assetDir": ASSET_DIR, "findings": findings,
              "cases": len(CANONICAL_CASES),
              "message": f"{len(CANONICAL_CASES)} canonical frontmatter case(s) run; "
                         "no adjacent assets to compare (installed copy)"},
             f"selftest: {len(CANONICAL_CASES)} canonical frontmatter case(s) run; "
             "no adjacent assets to compare (installed copy)")
        return 1 if findings else 0

    if disk_tpl is None:
        findings.append(_finding("sp-selftest-no-template", "error",
                                 f"no template at {tpl_path}", path=tpl_path,
                                 remedy="restore assets/specs/templates/spec.md"))
    elif disk_tpl != TEMPLATE_SPEC:
        d = list(difflib.unified_diff(TEMPLATE_SPEC.splitlines(),
                                      disk_tpl.splitlines(),
                                      "specs.py:TEMPLATE_SPEC", "templates/spec.md",
                                      lineterm="", n=1))
        findings.append(_finding("sp-template-drift", "error",
                                 f"TEMPLATE_SPEC and templates/spec.md differ "
                                 f"({len(d)} diff line(s))", path=tpl_path,
                                 diff=d[:40],
                                 remedy="edit both or neither — copy the file into the "
                                        "TEMPLATE_SPEC constant verbatim"))

    if disk_sch is None:
        findings.append(_finding("sp-selftest-no-schema", "error",
                                 f"no schema at {sch_path}", path=sch_path,
                                 remedy="restore assets/specs/schema.json"))
    else:
        try:
            parsed = json.loads(disk_sch)
        except json.JSONDecodeError as e:
            parsed = None
            findings.append(_finding("sp-schema-unparseable", "error",
                                     f"{sch_path} is not valid JSON: {e}", path=sch_path,
                                     remedy="fix the JSON"))
        if parsed is not None:
            a, b = _behavioral(parsed), _behavioral(DEFAULT_SCHEMA)
            for key in sorted(set(a) | set(b)):
                if a.get(key) != b.get(key):
                    findings.append(_finding(
                        "sp-schema-drift", "error",
                        f"schema.json and DEFAULT_SCHEMA disagree on `{key}`",
                        path=sch_path, key=key,
                        remedy="edit both or neither — DEFAULT_SCHEMA is what an installed "
                               "copy runs on"))

    errors = [f for f in findings if f["severity"] == "error"]
    if args.json:
        print(json.dumps({"ok": not errors, "assetDir": ASSET_DIR,
                          "cases": len(CANONICAL_CASES) + len(SECTION_CASES["cases"]) + 1,
                          "findings": findings},
                         indent=2, ensure_ascii=False))
        return 1 if errors else 0
    print(f"specs selftest — {ASSET_DIR} ({len(CANONICAL_CASES)} frontmatter + "
          f"{len(SECTION_CASES['cases']) + 1} section canonical case(s), "
          f"{len(errors)} error(s))")
    for f in findings:
        print(f"  [{f['severity']:<5}] {f['message']}  ({f['code']})")
        print(f"          remedy: {f['remedy']}")
        for line in f.get("diff", [])[:12]:
            print(f"            {line}")
    if not findings:
        print(f"  OK — the canonical frontmatter and section cases pass, the capture form "
              f"stamps exactly the entry-gate headings, the task metadata grammar is closed "
              f"on both the key list and the indent, `--moment build` resolves the six "
              f"sections an executor is sent, a §addressed Impact bullet still declares its "
              f"path, the {len(BACKEND_CASES)} backend cases agree between `files` and "
              f"`memory`, the config defaults hold with nothing declared, the files root "
              f"reaches for no specs worktree where there must not be one, the worktree lock "
              f"admits one writer and reclaims nothing it cannot prove dead, the "
              f"{len(GH_REFUSAL_CASES)} gh and {len(AZ_REFUSAL_CASES)} az transport failures "
              f"each refuse with their own remedy, the unproved-backend warning says its "
              f"piece once per process on stderr and only for "
              f"{', '.join(UNPROVED_BACKENDS)}, every record reads back as it was "
              f"written, a grouped document survives store-and-reload byte for byte whether "
              f"it fits one issue body or spills into continuation comments, an oversized body "
              f"refuses without making the call, and the embedded "
              f"schema and template match their asset files.")
    return 1 if errors else 0


def cmd_config(args, root: str) -> int:
    """The workspace's declared parameters, as data. Exit 0 even with nothing declared —
    a missing config is the normal case, and `doctor` is where a malformed one is judged."""
    cfg = load_config(root)
    lines = [f"quenching config — {cfg['path']}",
             f"  backend: {cfg['backend']}"
             + (" (default)" if not cfg["present"] else ""),
             f"  specsBranch: {cfg['specsBranch']}",
             "  worktreeSetup: " + (cfg["worktreeSetup"] or "(none declared)"),
             "  azureStates: " + (", ".join(f"{p}={s}" for p, s in cfg["azureStates"].items())
                                  if cfg["azureStates"] else "(none declared)")]
    if cfg["legacyPath"]:
        lines.append(f"  legacy config still on disk, unread: {cfg['legacyPath']}")
    emit(args.json, {"ok": True, "root": root, **cfg}, "\n".join(lines))
    return 0


def cmd_doctor(args, root: str) -> int:
    findings: list[dict] = []
    if not os.path.isdir(root):
        findings.append(_finding("sp-no-workspace", "error", f"no specs/ workspace at {root}",
                                 remedy="scaffold specs/ (copy the plugin's assets/specs skeleton)"))
        return _emit_doctor(args, root, findings)

    for ph in PHASES:
        if not os.path.isdir(os.path.join(root, ph)):
            findings.append(_finding("sp-missing-phase", "warn", f"no {ph}/ folder",
                                     path=ph, remedy=f"mkdir {ph}/ (the folder IS the phase)"))
    # A v2 folder that still holds specs is the one shape `list` reads correctly but
    # reports as out of date — surfaced here so it is fixed by a migrate, not by hand.
    for folder in LEGACY_PHASES:
        held = [s for s in spec_files(root) if s["folder"] == folder]
        if held:
            findings.append(_finding("sp-v2-layout", "error",
                                     f"`{folder}/` still holds {len(held)} spec(s) — v3 "
                                     f"folded backlog/ and ready/ into plans/",
                                     path=folder, count=len(held),
                                     remedy="specs.py migrate  (moves them into plans/ "
                                            "unrenamed; specs/archive/** is never touched)"))

    # The real failure mode of a machine-read config is `worktree_setup` written where
    # `worktreeSetup` was expected, followed by silence — the file is valid JSON, the key
    # is simply never looked at, and the setup that was declared never runs. Both findings
    # exist so that silence cannot happen; neither is an error, because a workspace with a
    # malformed config is still a workspace and every other command still works.
    cfg = load_config(root)
    if cfg["unparseable"]:
        findings.append(_finding("sp-config-unparseable", "warn",
                                 f"{CONFIG_FILE} is not valid JSON: {cfg['unparseable']}",
                                 path=CONFIG_FILE,
                                 remedy=f"fix the JSON, or remove {CONFIG_FILE} — an absent "
                                        f"config declares nothing and is not a finding"))
    for key in cfg["unknownKeys"]:
        findings.append(_finding("sp-config-unknown-key", "warn",
                                 f"{CONFIG_FILE} declares `{key}`, which nothing reads",
                                 path=CONFIG_FILE, key=key,
                                 remedy=f"the recognised key(s): {', '.join(CONFIG_KEYS)}"))
    if cfg["unknownBackend"]:
        findings.append(_finding("sp-config-unknown-backend", "warn",
                                 f"{CONFIG_FILE} declares backend `{cfg['unknownBackend']}`, "
                                 f"which is not one this tool implements — `{cfg['backend']}` "
                                 f"is in effect instead",
                                 path=CONFIG_FILE, backend=cfg["unknownBackend"],
                                 remedy=f"the implemented backend(s): {', '.join(BACKENDS)}"))
    # The permanent half of the "warn or stay silent" answer, and the reason it is a finding
    # and not a line on every call: a backend that was never run against a real target is a
    # fact about the CONFIGURATION, unchanged between operations, so it belongs where a
    # human goes to ask what is wrong with this workspace rather than in the output of every
    # command. The write-time line in `announce_unproved` is the other half. A warning on
    # every operation would be noise nobody reads twice; silence would let the untested
    # guesses (AZ_SPEC_TYPE, the state mapping) surface only when they are
    # already wrong in a real project. `doctor` is the middle the Open Decision asked for.
    if cfg["backend"] in UNPROVED_BACKENDS:
        findings.append(_finding("sp-backend-unproved", "warn",
                                 f"{CONFIG_FILE} declares backend `{cfg['backend']}`, which "
                                 f"ships without ever having been run against a real target "
                                 f"— its writes are unproved",
                                 path=CONFIG_FILE, backend=cfg["backend"],
                                 remedy="verify AZ_SPEC_TYPE matches this "
                                        "project's process template before relying on it, "
                                        "or declare a proven backend: "
                                        f"{', '.join(b for b in BACKENDS if b not in UNPROVED_BACKENDS)}"))
    # The config moved to `.claude/`, and a repo that upgrades without moving its file is the
    # one shape where every command keeps working while nothing it declared is read — the
    # silence the two findings above exist to prevent, reappearing one directory over. Named
    # here rather than merged in load_config: two configs with no stated winner is worse than
    # one that is plainly stranded.
    if cfg["legacyPath"]:
        findings.append(_finding("sp-config-legacy-location", "warn",
                                 f"`specs/{LEGACY_CONFIG_FILE}` is still on disk and is no "
                                 f"longer read — the plugin's config is {CONFIG_FILE}",
                                 path=f"specs/{LEGACY_CONFIG_FILE}",
                                 remedy=f"move its keys into {CONFIG_FILE} and delete it; "
                                        f"whatever it declares is doing nothing today"))

    leftovers = _v1_leftovers(root)
    for name in leftovers:
        findings.append(_finding("sp-v1-leftover", "error",
                                 f"`{name}/` is a v1 three-file plan folder",
                                 path=name,
                                 remedy=f"specs.py migrate  (folds {name}/ into one v2 file; "
                                        f"specs/archive/** is never touched)"))
    for entry in sorted(os.listdir(root)):
        full = os.path.join(root, entry)
        # `config.json` stays exempt even though nothing reads it any more: it has its own
        # finding above, which says where it went. Reporting it as a stray would offer
        # "move it into a phase folder", which is the one thing that must not happen to it.
        if os.path.isfile(full) \
                and entry not in ("QUENCHING.md", "schema.json", LEGACY_CONFIG_FILE) \
                and not entry.startswith("."):
            findings.append(_finding("sp-stray-file", "warn",
                                     f"stray file at the specs root: {entry}", path=entry,
                                     remedy="move it into a phase folder or remove it"))
    return _emit_doctor(args, root, findings)


def _emit_doctor(args, root: str, findings: list[dict]) -> int:
    errors = [f for f in findings if f["severity"] == "error"]
    if args.json:
        print(json.dumps({"ok": not errors, "root": root, "findings": findings},
                         indent=2, ensure_ascii=False))
    else:
        print(f"specs doctor — {root} ({len(errors)} error(s), "
              f"{len(findings) - len(errors)} warning(s))")
        for f in findings:
            print(f"  [{f['severity']:<5}] {f['message']}  ({f['code']})")
            print(f"          remedy: {f['remedy']}")
        if not findings:
            print("  OK — workspace conforms.")
    return 1 if errors else 0


def cmd_export(args, root: str) -> int:
    """Dump the canonical markdown of one spec, or every spec, to disk — write-only.

    THE MITIGATION `## Risks` NAMES FOR LOSING AN EXTERNAL BACKEND, AND NOTHING MORE. Nothing
    in this tool reads the dump back and nothing keeps it in sync with the backend, so it is
    never a second store — a stale copy on disk cannot silently outrank the backend the way a
    cache could. `info["text"]` is the same canonical document every other command derives
    from and shows under `show --full`; this command only adds the write to disk."""
    backend, err = open_backend(root)
    if err:
        return emit_err(args.json, err)
    slugs = [s["slug"] for s in backend.list_specs()] if args.all else [args.spec]
    written = []
    for slug in slugs:
        info, rerr = backend.read_spec(slug)
        if rerr:
            return emit_err(args.json, rerr)
        dest = os.path.join(args.out, info["folder"], info["file"])
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, "w", encoding="utf-8") as f:
            f.write(info["text"])
        written.append(dest)
    obj = {"ok": True, "out": args.out, "count": len(written), "files": written}
    human = f"exported {len(written)} spec(s) to {args.out}/\n" + \
            "\n".join(f"  {w}" for w in written)
    emit(args.json, obj, human)
    return 0


# --------------------------------------------------------------------------- #
# dispatch
# --------------------------------------------------------------------------- #
def build_parser() -> tuple[argparse.ArgumentParser, argparse._SubParsersAction]:
    p = argparse.ArgumentParser(prog="specs.py",
                                description="deterministic trail for the specs/ front")
    p.add_argument("--root", help="the specs/ workspace directory (default: nearest specs/ upward)")
    p.add_argument("--version", action="store_true", help="print the version and exit")
    sub = p.add_subparsers(dest="cmd")

    def add_json(sp):
        sp.add_argument("--json", action="store_true", help="machine-readable output")
        return sp

    sp = add_json(sub.add_parser("new", help="capture a spec into plans/"))
    sp.add_argument("name")
    sp.add_argument("--title")
    sp.add_argument("--verification", choices=list(VERIFICATION_POLICIES),
                    help=f"when the suite runs (default: {DEFAULT_VERIFICATION})")

    add_json(sub.add_parser("list", help="every spec, by folder and derived stage"))

    sp = add_json(sub.add_parser("status", help="one spec's sections, stage, tasks, gates"))
    sp.add_argument("--spec", required=True)

    sp = add_json(sub.add_parser("show", help="granular read: ONE task, the map by default, "
                                              "the document only with --full (section "
                                              "bodies are `section`'s)"))
    sp.add_argument("--spec", required=True)
    sp.add_argument("--task", action="append", metavar="ID",
                    help="one task's line and metadata, by id or index; repeatable")
    sp.add_argument("--full", action="store_true",
                    help="the WHOLE document — never the default, because every caller "
                         "that did not need it pays for it in context on every later turn")

    sp = add_json(sub.add_parser("section", help="read N sections, or write ONE"))
    sp.add_argument("spec")
    sp.add_argument("heading", nargs="?",
                    help="one canonical heading, or several comma-separated; returned in "
                         "the order asked. Omit when --moment resolves the list instead")
    sp.add_argument("--moment", choices=["decision", "build", "close"],
                    help="read every canonical section declared this moment, in canonical "
                         "order, instead of an enumerated heading list")
    sp.add_argument("--write", action="store_true",
                    help="replace the section from stdin, creating it in canonical position")

    sp = add_json(sub.add_parser("verification",
                                 help="read or set ONE spec's verification policy"))
    sp.add_argument("spec")
    # No `choices=`: argparse would refuse a bad value with a usage message on stderr and
    # exit 2 with no JSON, and every caller of this tool is told to branch on the exit code
    # AND the `--json` payload. The check lives in the command, where the refusal carries
    # `sp-bad-verification` and the declared set like every other refusal here.
    sp.add_argument("policy", nargs="?",
                    help="omit to read; one of " + ", ".join(VERIFICATION_POLICIES))

    sp = add_json(sub.add_parser("record", help="read or merge ONE frontmatter record"))
    sp.add_argument("spec")
    sp.add_argument("name", help="one of the declared records")
    sp.add_argument("--set", action="append", metavar="FIELD=VALUE",
                    help="merge one field; repeatable. Fields not named survive, so a "
                         "re-stamp never drops what an earlier pass wrote")

    sp = add_json(sub.add_parser("promote", help="the gated close-out: plans/ → archive/"))
    sp.add_argument("spec")
    sp.add_argument("--to", choices=list(PHASES), help="force the destination phase")
    sp.add_argument("--outcome", choices=list(OUTCOMES),
                    help="archive hop only (default: done)")
    sp.add_argument("--force", action="store_true",
                    help="archive as done despite open tasks")
    sp.add_argument("--dry-run", action="store_true", dest="dry_run")

    sp = add_json(sub.add_parser("task", help="flip or block a checkbox"))
    sp.add_argument("--spec", required=True)
    sp.add_argument("--check")
    sp.add_argument("--uncheck")
    sp.add_argument("--block", help="mark TASK blocked (requires --reason)")
    sp.add_argument("--reason", help="why the task is blocked — written into the line")
    sp.add_argument("--subject", help="the subject of the commit that implements the task, "
                                      "recorded as a `subject:` metadata line "
                                      "(goes with --check)")
    sp.add_argument("--commit", help="the sha of the commit that implements the task, "
                                     "recorded as a `commit:` metadata line — call it AFTER "
                                     "the commit exists (goes with --check; additive to "
                                     "--subject, not a replacement for it)")

    sp = add_json(sub.add_parser("next", help="THE single next action, or --front for the "
                                              "ranked candidate list"))
    sp.add_argument("--spec", help="one spec's next action")
    sp.add_argument("--front", action="store_true",
                    help="rank every active spec: executing, closest to done, priority, age")

    sp = add_json(sub.add_parser("parallel", help="prove a [P] group's files: are disjoint"))
    sp.add_argument("--spec", required=True)

    sp = add_json(sub.add_parser("discover", help="append a line to ## Discoveries"))
    sp.add_argument("spec")
    sp.add_argument("text")

    sp = add_json(sub.add_parser("validate", help="the canonical set, the gates, the sp-* codes"))
    sp.add_argument("--spec", help="one slug (default: every spec)")

    add_json(sub.add_parser("config", help="the workspace's declared parameters, as data"))

    add_json(sub.add_parser("doctor", help="workspace shape; remedies declared"))

    add_json(sub.add_parser("selftest", help="prove the embedded schema and template "
                                             "have not drifted from their asset files"))

    sp = add_json(sub.add_parser("migrate", help="one-way fold to the current layout "
                                                 "(v1 → v3, and backlog/ + ready/ → plans/)"))
    sp.add_argument("--dry-run", action="store_true", dest="dry_run")

    sp = add_json(sub.add_parser("export", help="dump the canonical markdown to disk — "
                                                "write-only, nothing reads it back"))
    grp = sp.add_mutually_exclusive_group(required=True)
    grp.add_argument("--spec", help="one slug")
    grp.add_argument("--all", action="store_true", help="every spec")
    sp.add_argument("--out", default="specs-export",
                    help="destination directory (default: ./specs-export)")

    return p, sub


DISPATCH: dict = {
    "new": cmd_new,
    "list": cmd_list,
    "status": cmd_status,
    "show": cmd_show,
    "section": cmd_section,
    "verification": cmd_verification,
    "record": cmd_record,
    "promote": cmd_promote,
    "task": cmd_task,
    "next": cmd_next,
    "parallel": cmd_parallel,
    "discover": cmd_discover,
    "validate": cmd_validate,
    "config": cmd_config,
    "doctor": cmd_doctor,
    "selftest": cmd_selftest,
    "migrate": cmd_migrate,
    "export": cmd_export,
}


def _force_utf8_output() -> None:
    """Spec files are prose — em-dashes, arrows, accented words — and a Windows console
    defaults to cp1252, where printing one raises UnicodeEncodeError AFTER the write
    already landed. That turns a successful `task --check` into a traceback and a nonzero
    exit, which the exit-code contract (0 ok / 1 findings / 2 refusal) reads as a finding.
    Encode output as UTF-8 and never let a glyph decide the exit code."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, OSError, ValueError):
            pass


def main(argv: list[str]) -> int:
    _force_utf8_output()
    if "--version" in argv:
        print(f"specs {VERSION}")
        return 0
    parser, _ = build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, "cmd", None):
        parser.print_help()
        return 1
    if not hasattr(args, "json"):
        args.json = False
    root = find_specs_root(args.root)
    # The lock is taken HERE and not inside the backend, because the unit it protects is the
    # whole command: every writing subcommand reads a document, edits it and writes it back,
    # and a lock that only spanned the write would let two of them read the same text and each
    # store its own edit over the other's. `finally` and not `atexit`: the lock must be gone by
    # the time the process reports its exit code, so whatever runs next sees a free worktree.
    lock, err = writer_lock(args, root)
    if err:
        return emit_err(args.json, err)
    try:
        return DISPATCH[args.cmd](args, root)
    except BackendRefusal as e:
        # THE ONE PLACE A TRANSPORT FAILURE BECOMES AN EXIT CODE. An external backend can
        # fail in the middle of a primitive that has no error channel, and the contract is
        # a legible refusal and never a traceback — so the failure is raised where it
        # happens, carrying the message already built, and converted exactly once here.
        return emit_err(args.json, e.err)
    finally:
        if lock is not None:
            lock.release()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
