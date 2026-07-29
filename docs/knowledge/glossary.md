---
type: knowledge
title: Glossary
description: The repo's single A–Z lookup of terms, acronyms, and domain vocabulary — one entry per term, each linking to its full concept doc when one exists.
resource: docs/**
tags: [glossary, vocabulary, terminology]
timestamp: 2026-07-26
audience: both
authority: current
source: quenching skeleton
maintainer: <the team>
---

# Glossary

The repository's **single source of truth for what a term means here**. One entry per
term, in the same bullet syntax every `index.md` uses: `* [<Term>](<path>.md) — <one-sentence
definition>` when a full concept doc exists, or `* **<Term>** — <one-sentence definition>`
when it doesn't — the glossary is the *index* of vocabulary, not the long-form home.

**Resolving a term.** When a repo-specific word, acronym, or piece of jargon is unclear,
**search this file first** (Ctrl-F, or `grep -i '<term>' docs/knowledge/glossary.md`). A
matching entry gives the local meaning and, when linked, points to the doc that explains
it in full. No entry means the term is not yet defined — capture it (see *How to enrich*).

**This file is the ONE deliberate exception to "one concept per file."** A glossary is
inherently a multi-term aggregate — a flat bullet list, not a concept doc per term. It is
also the one exception to an `index.md`'s "only list what exists" rule: an **unlinked**
entry (a term with no concept doc yet) is a normal, permanent, valid state, not a defect.
Keep the list **alphabetically sorted by Term**, keep each definition to a single
sentence, and **link out** rather than explaining in full here.

## Terms

- [**Advisory finding**](../standards/quality/bundle-verification.md) — a WARN the commands' verify
  gate does **not** treat as blocking, reported so a human can look and never so a run stops;
  `stale-doc` is the only one, against the WARN-but-must-fix set (`dir-no-index`,
  `index-broken-link`, `index-orphan`, `glossary-broken-link`, `resource-unresolved`,
  `resource-self`). The category has to stay small — a check that cannot tell "wrong" from "worth a
  look" belongs here or nowhere, and folding one into must-fix makes that set unusable.
- [**Always-on ceiling**](../standards/automation/context-budget.md) — the per-surface character
  total `skills.py budget` compares the summed descriptions against, commands **and** agent
  definitions alike; set from a measurement and never guessed, and deliberately kept EQUAL to the
  current total so it has no headroom and the next command crosses it the day it is minted.
  `budget` reports and never refuses — crossing it prompts a re-measure, not a block.
- [**Always-on metadata**](../standards/automation/context-budget.md) — the frontmatter
  `description` of every command, resident in every session's context before anything fires and
  therefore the only surface cost paid whether or not a command runs; measured by
  `skills.py budget` from the parsed value, never the YAML source.
- [**Anchorless strategy**](../standards/workflows/plan-git-record.md) — a merge strategy that
  produces **no merge commit** — `fast-forward` and `rebase` — so the **Merge record** has nothing
  to name and carries an explicit none instead of a fabricated pointer. Under both, the per-task
  commits land on the base directly and their subjects resolve there, which is why a merge pointer
  would add nothing rather than being merely unavailable. `specs.py validate` reports the mismatch
  in **both** directions (`sp-bad-merge`): an anchorless strategy carrying a real subject, and a
  merge-producing strategy carrying an explicit none.
- [**Anomaly sidecar**](../standards/quality/parse-honesty.md) — a *second* function reporting what
  a parse could not represent faithfully, placed beside the parser rather than folded into its
  return. `frontmatter_anomalies(text)` re-reads the frontmatter block and names each unfaithful
  read — a stripped comment, an unterminated quote, an indented form the tool does not read, a
  last-winning duplicate key — while `parse_frontmatter` keeps returning a bare dict. The shape is
  the whole point: a `(value, understood)` return would force all nine call sites to decide what an
  un-understood input means, including mid-cycle ones (`status`, `next`, `triage`) that today refuse
  nothing. Every entry is a suspicion the tool **cannot** resolve, never a proven violation, which
  is why callers surface them at warn.
- [**Approved record**](../standards/workflows/plan-lifecycle.md) — the `approved: {date}`
  frontmatter entry recording that a human said go, the one fact the retired `backlog/` → `ready/`
  `git mv` carried that no derivation reproduces; `execute` asks inline and stamps it rather than
  refusing an unapproved spec.
- [**Blocked task marker**](../standards/workflows/task-execution.md) — the `- [!] <id> <title> —
  blocked: <reason>` line implementation writes when attempts stop converging, replacing the
  earlier hidden attempt counter; `specs.py next` skips it and the reason stays legible to whoever
  unblocks it.
- [**Branch record**](../standards/workflows/plan-git-record.md) — the `branch: {base, work}`
  frontmatter entry stamped by `/specs:isolate` at the moment isolation is taken, write-once.
  `work` is derivable while the branch is checked out; **`base` is not** — after the merge, git
  cannot say what the branch was cut from, which is the whole reason the record exists and why it
  is captured while still true. Work done in place stamps nothing, because a record whose `base`
  equals its `work` states no fact. **The record is never the signal**: anything asking whether a
  spec is in flight asks git for a live `plan/<slug>` ref, since a human may cut a branch with no
  record and a record outlives the branch it names.
- [**Bundle density**](../standards/quality/bundle-verification.md) — the figures `/docs:status`
  prints alongside conformance (concept docs per home, empty homes shown as `0`, glossary size,
  which `standards/` subjects hold anything), carrying **no finding code** by design: coding them
  would make permanent noise of a repo that legitimately has no `mlops/`, omitting them would hide
  a bundle passing every check while knowing nothing. A figure informs without accumulating as a
  defect to chase.
- [**Cache trap**](/plugins/quenching/assets/references/skill-new/capabilities.md) — the standing
  cost of an inline `model:`/`effort:` pin in a command's frontmatter: the pin is part of the
  session's prompt-cache key, so changing it makes the next request recompute every input token.
  A sub-agent's pin is cache-safe because it carries its own context; an orchestrator's is not,
  which is why five `effort: low`/`medium` pins were dropped rather than kept for their tier.
- [**Canonical case list**](../standards/code/frontmatter-parsing.md) — the twelve frontmatter rows
  that `skills.py`, `specs.py` and `okf-validate.py` must all decide **identically**, duplicated
  byte-identically as each tool's `CANONICAL_CASES` and run by each tool's own `selftest`. It is the
  **lockstep unit** standing in for the shared module the three cannot have — each installs
  standalone into a target's `.claude/hooks/`, so none may import the others — and it works by
  localising a break: a parser that drifts fails its OWN selftest on a row the other two still pass.
  A tool may read *more* than the list requires and must then not report the form it genuinely read,
  so a form a tool does **not** read can never become a row; that asymmetry is named per-tool
  instead, which is why a block scalar is diagnosed by two of the three and by neither the list nor
  the third.
- [**Commit record**](../standards/workflows/plan-git-record.md) — the `subject: <line>` field on a
  completed task line, written mechanically by `specs.py task --check --subject`, that links the
  checkbox to the commit implementing it by naming that commit's **subject** and resolving with
  `git log --grep --fixed-strings`. Because a subject is known *before* the commit exists, the box
  is ticked into the commit it describes and no bookkeeping commit follows it — the same inversion
  that lets `merge: {strategy, subject}` be stamped on the work branch and the merge be the last
  action of `/specs:conclude`. Nothing is inscribed into the message as a trailer: the recorded
  subject is whatever the target repo's own convention produced. A spec built before this change
  carries `commit: <sha>` and resolves by sha; both forms are read forever and neither is
  backfilled.
- [**Derived stage**](../standards/workflows/plan-lifecycle.md) — a spec's position in its life
  (`captured` → `proposed` → `designed` → `refined` → `ready` → `approved` → `executing`),
  COMPUTED from which headings are filled and which records frontmatter carries rather than
  declared in a field, so it regresses on its own when a section empties instead of going stale;
  resolution is last-match-wins, which is why `executing` sorts last.
- [**Entry point**](../standards/naming/command-surface.md) — one `commands/<path>.md` file, whose
  path IS its identity (`commands/docs/add.md` → `/docs:add`); since Claude Code merged commands
  into skills there is no second file to mirror, so there is nothing an entry point can drift from.
- [**Handler ladder**](../standards/automation/hooks.md) — the ordering a hook's handler is chosen
  from, cheapest first: a deterministic `command` script (zero tokens on no-match), then a `prompt`
  handler (one cheap judgment per firing), then an `agent` handler — which on a per-tool-call event
  is an LLM toll booth on every operation (`sk-hook-llm-frequent`). Climbed only when the rung
  below cannot express the check.
- [**Merge record**](../standards/workflows/plan-git-record.md) — the `merge: {strategy, subject}`
  frontmatter entry stamped by `/specs:conclude`, write-once, **on the work branch before the
  merge** — which is what makes the merge that command's last action and leaves nothing to be
  committed to the base after it. The strategy was a human choice and the subject names the merge
  commit it is about to produce; recording both is what tells a future reader whether the per-task
  subjects still resolve from the base. An **anchorless strategy** carries an explicit none here.
- [**Parse honesty**](../standards/quality/parse-honesty.md) — the obligation that a verifier names
  its own parse failure rather than reporting it as a content gap. The episode that earned it: a
  command `description` truncated at a `#` surfaced as `sk-no-description` — a statement true of the
  string `lint` held and false of the file on disk — so the author either distrusts the checker or
  edits prose that was never wrong. Three consequences bind: the diagnostic ships **with** the lossy
  transform and never after it, it runs **before** the content checks it would otherwise be mistaken
  for, and a tool that cannot prove it implements the rule does not get the rule. Severity is
  **warn**, because a deliberate comment and lost prose are byte-identical — the tool states a
  suspicion it cannot resolve. Delivered by an **anomaly sidecar**.
- [**Phantom command**](../standards/architecture/plugin-layout.md) — a non-entry-point file left
  under `commands/`, which registers as a real `/` entry that does nothing; it does not error, so
  the only thing that catches it is `sk-no-description`, and it is why shared procedure lives under
  `assets/`.
- [**Phase gate**](../standards/workflows/plan-artifacts.md) — the set of sections a spec must have
  filled before a heading counts as required, which is what makes the explicit-none rule
  stage-scoped rather than absolute. Two gates move a file (`new` into `plans/`, `promote` into
  `archive/`) and refuse with exit 2 and the missing list rather than warning; the `ready` gate is
  a derived stage that refuses nothing. All of them live once in `schema.json`, read by both
  `promote` and `validate`.
- [**`[P]` marker**](../standards/workflows/task-execution.md) — the opt-in flag set on a task when
  the tasks are written, declaring it may run concurrently with its group; honoured only when
  `specs.py parallel` proves the group's `files:` sets disjoint, and never inferred while building.
- [**Probe**](../standards/architecture/align-surface.md) — the opening run of a front's own
  verifier (`okf-validate.py`, `specs.py doctor`, `skills.py doctor`) whose exit code decides
  whether an align inventories anything at all, making a no-op align cost a couple of tool calls;
  the same programs run again as the closing verification.
- [**Promote**](../standards/workflows/plan-lifecycle.md) — the gated `git mv` that moves a spec
  from `plans/` to `archive/` without renaming it, stamping `outcome: done | abandoned`. Under v3
  it is the ONE hop a spec ever makes: the `backlog/` → `ready/` promote is retired, and the human
  OK it used to carry is the **Approved record** instead. Promoting as `done` refuses
  while `- [ ]` boxes remain unless forced; `abandoned` is always allowed.
- [**Refinement record**](../standards/workflows/plan-artifacts.md) — the `refined: {mode, date}`
  entry a spec's **frontmatter** gains once it has been interrogated, whose absence raises the
  non-gating `sp-unrefined` warning.
- [**Resource glob set**](../standards/quality/bundle-verification.md) — the format of an OKF
  doc's `resource:`, a plugin convention rather than an OKF rule: a **comma-separated** list of
  repo-root-relative paths and globs using `*`/`**` **only**, matched **segment-wise everywhere**
  including the `:(glob)` pathspec handed to `git log`, since plain `fnmatch` and git's default
  wildmatch both let `*` cross a `/` and would silently widen every shallow scope. Anything else
  (braces, character classes, `?`) is classified `unknown` and never reported as a violation. It
  says what the doc *governs* — which is why it replaced the `file:line` anchor doctrine once
  named, and why it is also the input `stale-doc` needs.
- [**Retired (reserved artifact)**](../standards/architecture/retiring-a-reserved-artifact.md) — a
  reserved filename nothing produces or checks any more, but which **keeps** its slot in the
  validator's `RESERVED` set and its skip in the `PreToolUse` hard block. Deliberately not
  **unreserved**: dropping the reservation too would send every surviving instance down the
  concept-doc path, turning it into a `no-frontmatter`/`missing-type` ERROR in target repos that
  changed nothing. `docs/log.md` is the first artifact retired this way.
- [**Scope ladder**](../standards/automation/hooks.md) — the four rungs a hook may be installed at,
  narrowest first: a command's own frontmatter `hooks:` block (fires only while that command runs),
  a `settings.json` hook with an event + `matcher`, a gated wide event, and an unmatched
  session-wide hook — the top rung, and a finding (`sk-hook-unmatched`) unless the reason nothing
  narrower suffices is stated where it is wired. `skills.py` holds rung 1 and rung 2 to the same
  checks from one implementation.
- [**Verification policy**](../standards/workflows/task-execution.md) — the per-spec declaration
  (`per-task`, `per-section`, `end-of-plan`) written at creation that decides when a task's
  `verify:` command runs, so execution never guesses and never asks mid-task.
- [**Version lockstep**](../standards/ci-cd/versioning-release.md) — the six version strings a
  release must bump together, split into two halves read by two independent consumers: the
  `plugin.json` `version` + `VERSION` pair Claude Code compares to decide an upgrade fires, and the
  `VERSION` constant in each of the three shipped tools, which its installing align compares against
  the copy **already installed in a target repo**. Missing the second half is the silent failure —
  the tool is never upgraded in any repo that already has it, which cannot be observed from this
  repository at all. Distinct from the **Canonical case list**, which is the lockstep unit for the
  three tools' *parser behaviour* rather than their version strings.
- [**Worktree setup**](../standards/workflows/worktree-setup.md) — the single key `worktreeSetup`
  in `specs/config.json`, holding a command `/specs:isolate` runs once inside a newly created
  worktree so a repo with installed dependencies gets a usable tree rather than one that breaks at
  the first `verify:`. `specs.py` reads it and never executes it. Declaring nothing is the normal
  case and never a finding; the two that are — `sp-config-unknown-key` and `sp-config-unparseable`
  — exist only so a mistyped key cannot fail silently. Its consent is the isolation offer itself:
  the command is shown verbatim in the plan block, and choosing Worktree is the OK for it.

## How to enrich

Add a term whenever a repo-specific word, acronym, or piece of jargon surfaces that a
newcomer would not know. Three ways in:

- **Automatically, as a tail of a capture.** The `quenching` knowledge skills
  (`quenching-docs-learn`, `quenching-docs-add`, `quenching-docs-import-memory`) each check, at
  the end of a capture, whether the new concept introduced a term that belongs here, and
  add or update the entry — linking it to the concept doc just written.
- **On demand, one term at a time.** Run `quenching-docs-define` to add or refine a single
  entry (inserted in alphabetical position, MERGE — never clobbering a filled definition).
- **In bulk, across the whole bundle.** Run `quenching-docs-glossary-backfill` to sweep every doc
  already in `docs/` for repo-specific terms that were never fed into the glossary and
  backfill them in one pass.

Keep entries honest: define the term as **this repo** uses it, not the dictionary sense,
and let the linked doc carry the depth.
