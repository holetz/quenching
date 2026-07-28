---
slug: fix-skills-py-description-truncation
title: skills.py silently truncates a description at the first '#'
verification: per-section
priority: {level: 4, criticality: high, complexity: 3, date: 2026-07-28}
refined: {mode: gate, date: 2026-07-28}
approved: {date: 2026-07-28}
branch: {base: main, work: plan/fix-skills-py-description-truncation}
reviewed: {date: 2026-07-28}
merge: {strategy: merge-commit, subject: "plan/fix-skills-py-description-truncation: merge (merge-commit)"}
outcome: done
---

# skills.py silently truncates a description at the first '#'

<!-- ONE spec is ONE file for its whole lifecycle. Phases enrich it; they never split it.

     `specs.py new` stamps the frontmatter and `## Problem` ALONE — a captured spec is four
     lines of body, not a thirteen-heading skeleton. Every other heading below is created on
     first write by `specs.py section <slug> "<Heading>" --write`, which inserts it in the
     canonical position with the guidance comment kept here.

     THE STAGE-SCOPED EXPLICIT-NONE RULE. A heading is required — and required to carry
     `- none — <reason>` when it has nothing in it — only once ITS OWN gate is reached:

       new (capture)        `## Problem`
       ready (derived)      the nine definition sections (`## Problem` .. `## Risks`)
                            AND `## Tasks`
       ready (warn only)    `## Handoff` non-empty
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

     AUDIENCE. Each section names who reads it. `## Problem`/`## Proposal`/`## Design` are for
     the human — examples and plain language belong there. `## Handoff`/`## Tasks` are for
     agents — terse, with `files:`/`verify:`/`pattern:` metadata. An orchestrator never sends
     the human sections to an executor; that is what lets one file serve both audiences
     without bloating agent context. -->

## Problem

`skills.py`'s `parse_frontmatter` treats a `#` anywhere in a value as the start of a YAML comment
and drops the rest of the line. A command `description` is a single long line, so a `#` inside it
**silently truncates the description at that point** — for the parser, not for Claude Code, which
reads the real thing.

Found while rewriting `/specs:create`'s description during `specs-flow-consolidation`: writing a
markdown heading inline (backticked, as `## Problem`) cost the whole `Not for:` boundary and half
the trigger phrases. `lint` then reported `sk-no-boundary` — technically true of what it had
parsed, and completely misleading about the cause, which sent the fix at the wrong thing.

Two defects, and the second is the dangerous one:

- The parser is wrong: inside a quoted or plain scalar, `#` only begins a comment when preceded by
  whitespace, and never inside quotes.
- **A truncation is reported as absence.** Every downstream check — the character cap, trigger
  position, the boundary — runs against a silently shortened string, so the finding always names a
  missing part rather than the truncation that removed it. A verifier that misreports its own
  parse failure is worse than one that refuses.

The immediate fix is the comment rule; the durable one is a distinct finding (`sk-description-
truncated`, or a parse-level refusal) so the cause is never again presented as a content gap.

## Proposal

- All three tools apply one YAML comment rule: `#` begins a comment only at the start of a
  value or after whitespace, and never inside a quoted scalar. `skills.py` and `specs.py`
  stop truncating; `okf-validate.py` stops leaking a trailing comment into a value.
- `specs.py status --spec <slug> --json` returns a `title:` containing `#` whole. Today this
  spec's own title reads back cut at `at the first '`.
- A command `description:` may carry a backticked heading, an apostrophe-quoted `'#'`, or a
  quoted `#` without losing its trigger phrases or its `Not for:` boundary.
- Each tool can state when its parse was not faithful, instead of returning a value it
  silently could not represent.
- `lint`, `validate` and the OKF checker each report that as its own finding —
  `sk-frontmatter-unparsed`, `sp-frontmatter-unparsed`, `okf-frontmatter-unparsed` — so a
  parse failure is never again presented as a content gap (`sk-no-description`, a missing
  `title`, a bad `type`).
- No caller of `parse_frontmatter` changes: the nine existing call sites keep reading a dict,
  and no cycle command changes behaviour mid-build.
- One `docs/standards/` doc records the rule and the three-copy lockstep obligation.

## Out of Scope

- A shared frontmatter module, or any cross-tool import — each tool installs standalone into
  a target's `.claude/hooks/`. Lockstep duplication is the existing mold: `specs.py` already
  duplicates its templates as constants for exactly this reason.
- A real YAML parser, or any non-stdlib dependency — zero-dependency is the tools' contract.
- Teaching the mini-YAML to read nested keys or flow values. The diagnostic NAMES what it
  cannot read; it does not learn to read it.
- Rewriting any shipped command description to avoid `#` — all 24 were scanned and none
  contains one. The parser is what is wrong, not the descriptions.
- Bumping the version. All three aligns overwrite an installed copy only when the plugin is
  newer (`commands/skill/align.md:185`, `commands/docs/align.md:204`), so until `VERSION`,
  `plugin.json`, `marketplace.json` and the three script constants move off `4.1.0` together,
  every already-aligned target keeps the truncating copy. Deferred to whatever ships the
  release, not forgotten.

## Impact

### Standards this spec will write into docs/standards/

- `docs/standards/code/frontmatter-parsing.md` — the YAML subset the three tools read, the
  comment rule, the canonical case list, and the three-copy lockstep obligation
- `docs/standards/quality/parse-honesty.md` — a verifier names its own parse failure rather
  than reporting it as a content gap; warn severity, and why

### Standards at `authority: background` this spec may resolve

- `docs/standards/code/frontmatter-parsing.md` — written at `background` in task 1.1 before
  anything implements it, promoted to `current` in task 3.2 once the three tools prove it

### Product code this spec expects to touch

- `plugins/quenching/assets/bin/skills.py` — `parse_frontmatter`, the new sidecar, `selftest`
- `plugins/quenching/assets/bin/specs.py` — the same three
- `plugins/quenching/assets/hooks/okf-validate.py` — `parse_frontmatter`, the new sidecar, and
  a `selftest` subcommand it does not have today

## Validation

Each tool proves its own rule, and the three selftests are the standing guard.

```bash
cd plugins/quenching
python3 assets/bin/skills.py selftest          # exit 0 — the canonical cases named
python3 assets/bin/specs.py selftest           # exit 0 — same cases, same verdicts
python3 assets/hooks/okf-validate.py selftest  # exit 0 — NEW subcommand
```

Each must run the canonical case list from `docs/standards/code/frontmatter-parsing.md` and
report the same verdict per case: every comment-rule row parses whole where the rule says
whole, and each anomaly raises that tool's `*-frontmatter-unparsed` finding at `warn`.

The self-demonstrating check — this spec's own title is an instance of the bug:

```bash
python3 plugins/quenching/assets/bin/specs.py status \
  --spec fix-skills-py-description-truncation --json
# .title MUST read: skills.py silently truncates a description at the first '#'
# today it reads:   skills.py silently truncates a description at the first '
```

The standing regression block from `CLAUDE.md` §Verifying changes must stay clean:

```bash
cd plugins/quenching
python3 assets/hooks/okf-validate.py assets/docs                        # 0 error(s), 0 warning(s)
python3 assets/hooks/okf-validate.py assets/specs/plans --listing-root  # 0 error(s), 0 warning(s)
python3 assets/bin/skills.py --root . doctor --json                     # 24 commands, no findings
python3 assets/bin/skills.py --root . lint --json                       # exit 0
```

No functional check is owed: nothing under `commands/**` changes, so the fresh-process rule in
`docs/standards/quality/surface-verification.md` does not apply here.

## Design

Inside a plain or quoted scalar, `#` opens a comment only when it is the first character of
the value or is preceded by whitespace, and never inside a quoted scalar. The current
`val.split("#", 1)[0]` (skills.py:322, specs.py:507) honours none of those conditions.

**The signal is a sidecar, not a changed signature.** `frontmatter_anomalies(text)` re-reads
the block and returns what the parse could not represent faithfully: a trailing comment
stripped off a prose field, an unterminated quote, an indented continuation read as empty, and
a duplicate top-level key silently last-winning — where nothing guarantees Claude Code's own
parser resolves it the same way. `parse_frontmatter` keeps returning a bare dict.

The alternative was `(fm, understood)`, mirroring the 3-tuple `okf-validate.py` already
returns and the fail-open contract `parse_frontmatter_hooks` already states. It lost on two
counts: nine call sites change, and each `specs.py` caller — `status`, `next`, `triage` —
would then have to decide what an un-understood frontmatter means mid-cycle, which is a
behaviour change in commands that today never refuse. The sidecar puts the signal in the two
places a human actually reads findings from, at zero churn.

**`okf-validate.py` gets the rule and the diagnostic together, never the rule alone.** It
strips no comments today, which makes it the one tool that cannot truncate. Adding the rule
by itself would hand a prose-loss path to the tool with the widest blast radius — a hook
firing on every `docs/**` write in every target repo. The pair is what makes it safe.

**The finding is a warn, not an error.** A stripped trailing comment may be intentional; the
tool reports a suspicion it cannot resolve. This matches the fail-open contract
`parse_frontmatter_hooks` states: warn rather than guess.

Binding contracts this must not contradict: the three tools stay zero-dependency and
self-contained (CLAUDE.md §Repository layout); their `VERSION` constants stay in lockstep
with `plugins/quenching/VERSION` (§Releasing).
## Alternatives Considered

- **Fix `skills.py` only, as `## Problem` scoped it.** Rejected: the identical line at
  `specs.py:507` is corrupting data right now — it truncates this spec's own `title` in every
  `specs.py status --json` call — and whoever fixed it there would re-derive the same rule.
- **Fix the two truncating tools, leave `okf-validate.py`.** Rejected: the three tools would
  keep disagreeing on the same YAML subset, and the standard could not honestly claim to
  describe the toolchain.
- **The comment rule alone, no diagnostic.** Rejected: it closes the reported symptom but not
  the defect `## Problem` calls the dangerous one. An indented multi-line `description` still
  parses as empty and `lint` still reports `sk-no-description` — a parse failure presented as
  a content gap, with no `#` involved at all.
- **Extract one shared frontmatter module.** Rejected; recorded with its reason in
  `## Out of Scope`.

## Open Decisions

- The anomaly set is a floor, not a ceiling. Four are named in `## Design`: a stripped trailing
  comment, an unterminated quote, an indented continuation read as empty, and a duplicate
  top-level key. **Decided during execution** — any further silent misread a selftest fixture
  exposes is named in the canonical list before that task is ticked, or recorded with
  `specs.py discover` if it is out of shape for this spec.

## Risks

- **The three copies drift.** Extraction is ruled out in `## Out of Scope`, so nothing
  structurally forces the parsers to agree. MITIGATED: one canonical case list, named in
  `docs/standards/code/frontmatter-parsing.md` and embedded verbatim in all three selftests, so
  a drifted parser fails its own selftest on a case the other two still pass — loud, and
  localised to the tool that moved. The list itself becomes the lockstep unit, and the standard
  says so plainly.
- **`okf-validate.py` changes behaviour in an always-on hook.** It strips no comments today, so
  on upgrade a `type: standard # tentative` stops failing the vocabulary check and starts
  parsing as `standard`. Correct, but it is a behaviour change in a `PostToolUse`/`Stop` hook in
  every target repo. MITIGATED: the paired diagnostic names every strip it performs, and the
  new selftest covers the case.
- **The new warn fires on legitimate frontmatter comments.** A repo that deliberately comments
  its frontmatter gets a finding on every affected file. ACCEPTED — it is a warn, not an error,
  and it reports a suspicion the tool genuinely cannot resolve: a stripped comment and lost
  prose are byte-identical.
- **The fix never reaches an installed target.** All three aligns overwrite an installed copy
  only when the plugin is newer, and the version bump is out of scope. ACCEPTED — recorded in
  `## Out of Scope` with the propagation cost stated, so it is deferred rather than forgotten.

## Handoff

All seven tasks are built, verified and committed on `plan/fix-skills-py-description-truncation`
(seven commits, `6aaa8bc` through `5edd488`). Nothing is left to build; what remains is
`/specs:conclude` — the branch review, the emergent `docs/`, the merge and the archive-time
distillation.

**The state of the tree.** All three tools share four identically-bodied helpers
(`_frontmatter_body`, `_indented_run`, `_quote_end`, `_split_comment`) plus `frontmatter_anomalies`,
`CANONICAL_CASES` and `canonical_case_failures`. **The case list is byte-identical in all three; edit
all three or none.** Two standards are `authority: current`:
`docs/standards/code/frontmatter-parsing.md` (the mechanics) and
`docs/standards/quality/parse-honesty.md` (the obligation).

**Everything the sweep proved, so a reviewer need not re-run it.** Version lockstep holds at 4.2.0
across `VERSION`, `plugin.json` and all three scripts. `assets/docs` and
`assets/specs/plans --listing-root` are 0/0. `skills.py doctor` reports 25 commands and 0 findings;
`lint` exits 0. All three selftests exit 0 on the same twelve cases. `specs validate` and
`specs doctor` are 0/0; `okf-validate.py docs` is 0 errors with the same two warnings that predate
this branch (`agents.md` `resource-unresolved`, `hooks.md` `stale-doc`). Each tool's output was also
diffed against its `ec0a631` copy on every real tree and came back **byte-identical**, so the
behaviour change is confined to inputs this repository does not contain. No functional check is owed:
`git diff --name-only main...HEAD -- plugins/quenching/commands/` is empty.

**Three things for the reviewer to decide, none of them blocking.** `## Discoveries` holds all three:
the `okf-frontmatter-unparsed` code is the only tool-prefixed code in a file whose other codes carry
no prefix (implemented as the spec declared it); `## Validation` says 24 commands where there are 25;
and `## Out of Scope` reasons about a bump "off 4.1.0" when everything is already at 4.2.0. The
propagation argument in `## Out of Scope` still holds — an installed copy is overwritten only when
the plugin is newer, so **no already-aligned target gets this fix until a release ships**, which
remains deliberately out of scope.
## Tasks

### 1. The rule, agreed before it is proved

- [x] 1.1 Write `docs/standards/code/frontmatter-parsing.md` at `authority: background`: the YAML subset the three tools read, the comment rule, the canonical case list, and the three-copy lockstep obligation
      pattern: docs/standards/quality/surface-verification.md
      verify: python3 plugins/quenching/assets/hooks/okf-validate.py docs
      subject: plan/fix-skills-py-description-truncation: 1.1 the parsing standard

### 2. The three tools

- [x] 2.1 [P] skills.py: correct the comment rule, add `frontmatter_anomalies`, emit `sk-frontmatter-unparsed` from `lint`, and add the canonical cases to `selftest`
      files: plugins/quenching/assets/bin/skills.py
      verify: python3 plugins/quenching/assets/bin/skills.py selftest
      subject: plan/fix-skills-py-description-truncation: 2.1 the rule in skills.py
- [x] 2.2 [P] specs.py: the same rule and sidecar, emit `sp-frontmatter-unparsed` from `validate`, and add the canonical cases to `selftest`
      files: plugins/quenching/assets/bin/specs.py
      verify: python3 plugins/quenching/assets/bin/specs.py selftest
      subject: plan/fix-skills-py-description-truncation: 2.2 the rule in specs.py
- [x] 2.3 [P] okf-validate.py: add the comment rule it has never had, the sidecar, an `okf-frontmatter-unparsed` finding, and a `selftest` subcommand it does not have today
      files: plugins/quenching/assets/hooks/okf-validate.py
      verify: python3 plugins/quenching/assets/hooks/okf-validate.py selftest
      subject: plan/fix-skills-py-description-truncation: 2.3 the rule in okf-validate.py

### 3. The honesty rule, once proved

- [x] 3.1 Write `docs/standards/quality/parse-honesty.md` at `authority: current`: a verifier names its own parse failure rather than reporting a content gap, at warn severity
      pattern: docs/standards/quality/surface-verification.md
      verify: python3 plugins/quenching/assets/hooks/okf-validate.py docs
      subject: plan/fix-skills-py-description-truncation: 3.1 the honesty rule
- [x] 3.2 Promote `docs/standards/code/frontmatter-parsing.md` to `authority: current` — the three selftests are what proved it
      files: docs/standards/code/frontmatter-parsing.md
      subject: plan/fix-skills-py-description-truncation: 3.2 promote the parsing standard

### 4. Verification sweep

- [x] 4.1 Run the `CLAUDE.md` §Verifying changes block and the self-demonstrating title check; every line clean
      verify: python3 plugins/quenching/assets/bin/skills.py --root plugins/quenching doctor --json
      subject: plan/fix-skills-py-description-truncation: 4.1 the verification sweep

## Discoveries

- The spec's ## Validation expects `skills.py doctor` to report 24 commands; the surface has 25 since /specs:isolate landed. Task 4.1 must read 25, and the spec's stated figure is stale rather than a finding. RESOLVED at conclude: left as written. A spec records what was believed when it was written, and 4.1 verified against 25.
- The spec's ## Out of Scope reasons about a version bump 'off 4.1.0', but VERSION and all three scripts are already at 4.2.0. The propagation argument holds; the number is stale. RESOLVED at conclude: left as written, same reason — and the propagation argument is unaffected, so no already-aligned target gets this fix until a release ships.
- okf-validate.py's other finding codes carry no tool prefix (missing-type, resource-unresolved, index-orphan), so the spec-declared okf-frontmatter-unparsed is the only prefixed code in that file. Implemented as declared; whether to rename it to frontmatter-unparsed is a naming call for conclude. RESOLVED at conclude: KEPT as `okf-frontmatter-unparsed`. The `sk-`/`sp-`/`okf-` triad is the cross-tool symmetry this spec exists to create, and it reads as one rule in three tools rather than three unrelated findings. Nothing outside this branch references the codes, so the choice was free either way; local consistency inside one file lost to the symmetry across three.
- The branch review found the standard's own opening rule unmet: `specs.py` and `okf-validate.py` do not read block scalars (the table says so) but returned the bare `|`/`>` indicator as the value and named nothing — `description: |` read as the literal `"|"`. Pre-existing, not a regression, and invisible to the emptiness test because a block scalar is the one unread form that does not come back empty. RESOLVED at conclude: fixed on the branch, detected on the indicator; `skills.py` unchanged because it genuinely reads them.

## Outcome

Shipped. All three tools â€” `skills.py`, `specs.py` and `okf-validate.py` â€” apply one YAML comment
rule (`#` opens a comment only at the start of a value or after whitespace, never inside a quoted
scalar) and each carries a `frontmatter_anomalies` sidecar that names what its parse could not
represent. `lint`, `validate` and the OKF checker report those as `sk-`/`sp-`/`okf-frontmatter-unparsed`
at **warn**, emitted *before* the content checks they used to be mistaken for. `parse_frontmatter`
kept its signature in all three, so none of the nine call sites changed and no cycle command
changed behaviour mid-build.

Two standards carry it: `docs/standards/code/frontmatter-parsing.md` (the YAML subset each tool
reads, the comment rule, the twelve canonical cases and the three-copy lockstep obligation) and
`docs/standards/quality/parse-honesty.md` (a verifier names its own parse failure rather than
reporting it as a content gap). Both are `authority: current` â€” the parsing standard was written at
`background` in task 1.1 before anything implemented it and promoted in task 3.2 once all three
selftests passed the same twelve cases.

**What the branch review added.** The standard's own opening rule â€” a form out of contract must be
*named*, not guessed at â€” was unmet by two of the three tools. `specs.py` and `okf-validate.py` do
not read block scalars, but returned the bare `|`/`>` indicator as the value and reported nothing:
`description: |` read as the literal `"|"`. Pre-existing rather than a regression, and invisible to
the emptiness test because a block scalar is the one unread form that does not come back empty, so
it is now detected on the indicator. `skills.py` is unchanged and stays silent, because it genuinely
reads them. This is deliberately **not** a thirteenth canonical case and cannot become one: the
three legitimately differ here, which is why row 12 uses a bare wrapped line as common ground.

**What was left out, deliberately.** No shared frontmatter module and no cross-tool import â€” each
tool installs standalone into a target's `.claude/hooks/`, so the duplication is the mold, not an
accident. Nothing learned to read a form it does not read; the diagnostic names it instead. And no
version bump: all three aligns overwrite an installed copy only when the plugin is newer, so
**no already-aligned target repo gets this fix until a release ships**. That is deferred to whatever
ships the release, not forgotten.

**What the next reader needs.** `CANONICAL_CASES` is duplicated byte-identically in all three tools
and **is the lockstep unit â€” edit all three or none**; a drifted parser fails its own selftest on a
row the other two still pass. Everything below that list is per-tool by design, because each reads a
different subset: `frontmatter_anomalies` legitimately differs in all three, and each docstring says
why. The three selftests are the standing guard and are now named in `CLAUDE.md` Â§Verifying changes.

Merged with a **merge commit** (`--no-ff`), so every per-task commit stays on `main` and all seven
recorded `subject:` fields resolve from it.
