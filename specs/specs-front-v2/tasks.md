# Tasks — Specs front v2 — single-file lifecycle specs

Sections are ordered so each leaves the repo coherent: the contract exists before the tool
implements it, the tool works before the migration uses it, the migration is proven before the
skills assume it. That ordering is **authoring discipline**, not a verification schedule.

The plan verifies **`end-of-plan`**: the sections are genuinely coupled — the tool cannot be proven
before the contract exists, the migration before the tool, the skills before the migration — so
every `verify:` runs once, after the final task. A per-section policy would have had section 2's
terminal check (`specs.py validate`) run v2 code against a still-v1 workspace, which either passes
vacuously or blocks forever; deferring it to the end, after 6.3 has migrated the workspace, is what
makes it mean anything.

Each `verify:` must therefore be **self-contained**: a check that depends on transient state
created during its own task cannot be deferred. That is why 3.3 and 6.1 — both of which build and
discard a throwaway workspace — carry their assertions in the task text rather than in a `verify:`
line. All paths are relative to `plugins/claude-quenching/` unless stated otherwise.

## 1. Contract

- [ ] 1.1 Write the v2 spec-driven reference — one-file layout, the three folders, the
      `YYYY-MM-DD-<slug>.md` naming rule in EVERY folder (stamped at capture, never rewritten),
      the THIRTEEN canonical sections with the per-phase gate table and the **phase-scoped**
      explicit-none rule (a heading is required, and required to carry `- none — <reason>`, only
      once its own gate is reached; a present-but-empty heading is malformed), the derived-stage
      table, frontmatter keys (no `created` — the prefix is it), the `[!]` blocked marker, slug
      identity and suffix resolution, the executor contract
      (design.md §Decisions 1, 3, 8–9, 13)
      files: skills/quenching-specs-plan-propose/references/spec-driven.md
- [ ] 1.2 Write the single-file template and the v2 `schema.json` — the thirteen canonical
      headings with placeholder guidance and audience notes; the schema declares phases, their
      **per-phase required-section sets** (the one source `promote` and `validate` both read), the
      derived stages, and the one filename pattern all three folders share. The template stamps
      `## Problem` alone — a captured spec is not a thirteen-heading skeleton
      files: assets/specs/templates/spec.md, assets/specs/schema.json
- [ ] 1.3 Rework the `assets/specs/` seed to the three-folder shape — `backlog/` with its
      generated-zone `index.md`, `ready/`, `archive/`, and the QUENCHING.md lifecycle wording
      files: assets/specs/**
      verify: python assets/hooks/okf-validate.py assets/specs/backlog --listing-root

## 2. specs.py v2

- [ ] 2.1 Rewrite the core: single-file parser over the thirteen-section canonical set
      (frontmatter + sections; a heading outside the set is a stray, a heading present with an
      empty body is malformed and refuses), slug resolution across the three folders by the
      `*-<slug>.md` suffix (two matches refuses, exit 2, never guesses), derived-stage computation
      reading heading presence, `.specs.json` read/write dropped; templates/schema embedded
      fallbacks kept in lockstep
      files: assets/bin/specs.py
      verify: python assets/bin/specs.py --version
- [ ] 2.2 Implement `new` (scaffold `backlog/YYYY-MM-DD-<slug>.md` with `## Problem` as its only
      section, the date stamped once here and never again), `list` (grouped by folder and derived
      stage), `status --spec <slug>` (sections, stage, tasks, and the destination phase's
      outstanding gates), and `section <slug> <heading> [--write]` — `--write` creates the heading
      in canonical position when it does not exist yet
      files: assets/bin/specs.py
- [ ] 2.3 Implement `promote <slug>` — destination inferred (backlog→ready→archive) or forced
      with `--to`; gate check against the destination phase's required-section set from
      `schema.json`, with exit 2 and the missing list (`- none — <reason>` counts as filled, a
      present-but-empty heading does not); moves the file WITHOUT renaming it, and stamps
      `outcome: done|abandoned` on the archive hop only
      files: assets/bin/specs.py
- [ ] 2.4 Implement `task --check/--uncheck/--block <id> --reason`, `next` (skips `[!]`),
      `parallel` (unchanged semantics over `## Tasks`), and `discover <slug> <text>`
      files: assets/bin/specs.py
- [ ] 2.5 Rework `validate` (the canonical thirteen-heading set with strays flagged, the
      phase-scoped explicit-none rule asserted against `schema.json`'s per-phase sets, a
      present-but-empty heading reported as malformed, `sp-impact-uncovered` re-derived over the
      single file's `## Impact` parsed sub-heading, filename conformance — a spec file missing the
      `YYYY-MM-DD-` prefix, or whose frontmatter `slug` disagrees with the filename suffix —
      empty `## Handoff` in ready/ warns, the v2 `sp-*` vocabulary) and
      `doctor` (three folders present, strays,
      v1 leftovers detected → migrate declared as the remedy), plus `backlog reindex` grouping
      by derived stage
      files: assets/bin/specs.py
      verify: python assets/bin/specs.py validate --json

## 3. Migration

- [ ] 3.1 Implement `specs.py migrate` — fold a v1 plan folder (proposal + design + tasks +
      `.specs.json`) into one v2 file in the right folder; convert a v1 backlog task file into
      a captured-stage spec; the `YYYY-MM-DD-` prefix comes from `.specs.json`'s `created` (a
      task file's frontmatter date), falling back to the path's first commit date, so no
      birth date is invented; refuse (exit 2) on an already-v2 target; `specs/archive/**` never
      touched
      files: assets/bin/specs.py
- [ ] 3.2 Rewrite `quenching-specs-align` and its `references/conformance.md` to the v2
      canonical shape — v1 detection routes to `migrate` as a declared remedy; the openspec
      legacy path is retained; the `sp-*` codes are re-derived from the v2 contract
      files: skills/quenching-specs-align/**
- [ ] 3.3 Dogfood the migration against a THROWAWAY COPY of this repo's `specs/` — copy the
      workspace to a temp root, run the align v2 flow against the copy, assert all three active
      plans fold correctly (`docs-verification-layer`, `instrument-and-extend-skill-front` at
      29/46, and `specs-front-v2` itself), that `validate` is clean on the result, and that
      `specs/archive/**` is untouched; then discard the copy. The REAL workspace is migrated last,
      by 6.3 — this plan lives inside the workspace it migrates, so migrating here would move the
      plan out from under its own apply loop with twelve tasks still open. Settle the `ready/` vs
      `active/` name per design.md §Open Decisions. Self-contained by construction: it builds and
      discards its own fixture, so it carries no deferrable `verify:`

## 4. Skills and commands

- [ ] 4.1 Write the surface mapping doc: each of the thirteen v1 skills → its v2 fate (kept,
      merged, renamed, retired), with the resulting command tree — reviewed at this checkbox
      before any skill body is rewritten. Record the PRE-REWRITE BASELINE in the same doc:
      `skills.py budget` (32093 characters always on against a 36503 ceiling — 88% consumed, ~4400
      chars of headroom) and `skills.py lint skills --json` findings tallied by code. The baseline
      is what turns "the surface is expected to shrink" into something 4.4 can assert
      files: specs/specs-front-v2/surface-map.md (repo root)
- [ ] 4.2 Rewrite the definition-side skills per the mapping — capture (backlog-add successor),
      triage (stages + `## Discoveries` sweep), the propose/refine/update successors as
      stage-advancing edits, explore, from-claude
      files: skills/**, commands/specs/**
- [ ] 4.3 Rewrite the execution-side skills per the mapping — the apply successor carrying the
      executor contract (design.md §Decisions 9), status, archive/abandon folded into promote
      flows, the front conductor, and the two cross-front conductors' references to them
      files: skills/**, commands/specs/**
- [ ] 4.4 Re-mirror the command wrappers — the skill↔wrapper bijection holds at the new count;
      taxonomy names stay `quenching-<front>-<object>-<verb>`. This is also the section's
      verification gate: `doctor` proves the bijection, but thirteen rewritten BODIES are the
      section's real risk and `doctor` cannot see them, so `lint` and `budget` run too.
      **Acceptance**: no lint code class present that was absent from 4.1's baseline, `budget`
      under its ceiling, bijection intact. An always-on budget overrun is paid by every session in
      every installed repo, silently — it must be a check, not an expectation
      files: commands/**
      verify: python assets/bin/skills.py doctor --json && python assets/bin/skills.py lint skills --json && python assets/bin/skills.py budget --json

## 5. Assets, manuals, and standards

- [ ] 5.1 Update the three QUENCHING.md operator manuals — the new lifecycle, the command
      surface enumeration, the promote-as-OK model, and the upgrade note: a target repo that
      upgrades to v2 while holding a v1 `specs/` workspace **re-aligns manually** (`/specs:align`),
      because no format coexistence exists and nothing migrates it automatically
      (proposal.md §Out of Scope)
      files: assets/docs/QUENCHING.md, assets/specs/QUENCHING.md, assets/claude/QUENCHING.md
- [ ] 5.2 Update README.md and CLAUDE.md — the front's description, the 2×4 matrix wording,
      the verification snippet
      files: README.md (repo root), CLAUDE.md (repo root)
- [ ] 5.3 Rewrite `docs/standards/workflows/plan-artifacts.md` IN PLACE — same path, new `title:`
      ("Spec lifecycle contract"), the thirteen-section single-file contract, the phase-scoped
      explicit-none rule replacing the absolute one, promote-as-the-human-OK replacing
      `applyReady`, the one template replacing the three, `refined` moving from `.specs.json` to
      frontmatter, plus one short section "Reading a v1 plan in `specs/archive/`" — the archive is
      deliberately not migrated, so its readers still need the v1 shape named. Keep the
      supersede note in the body, per this repo's `naming/command-surface.md` precedent
      (design.md §Decisions 14)
      files: ../../docs/standards/workflows/plan-artifacts.md
- [ ] 5.4 Edit `docs/standards/workflows/task-execution.md` surgically — §"The failure budget:
      five attempts, re-read at two" gives way to the `[!] — blocked: <reason>` marker
      (design.md §Decisions 6), and the `verify:` fallback chain is re-pointed at the single
      file's `## Validation`. Everything else — the clean-tree precondition, the three
      verification policies, commit-per-task, the two-level review split, delegation, the `[P]`
      disjunction rule — survives untouched, and the `authority: current` grade holds
      files: ../../docs/standards/workflows/task-execution.md
- [ ] 5.5 Re-point the enumerations and the glossary — re-point EVERY surviving `quenching-specs-*`
      reference, found by grep rather than by a memorized count, because these files move under the
      plan: at the time of writing `docs/` carries **nine** such references across the four files
      declared in §Impact, and `automation/skills.md` alone has **two** (`quenching-specs-plan-refine
      --mode` as the mode-as-parameter example, and `quenching-specs-plan-apply` as the standing
      scoped-`Bash` exception — the second added while this plan was being written). Specifically:
      `naming/command-surface.md`'s `quenching-specs-*` ↔ `/specs:*` table re-derived from the v2
      surface (the naming rule itself is unchanged), every `automation/skills.md` example re-pointed
      at its v2 successor, and `knowledge/glossary.md`'s "Failure budget" entry retired with
      "Refinement record" rewritten to the frontmatter record; regenerate the derived listings the
      edits touch. A `current` standard left naming a dead skill is exactly the rot this front
      exists to prevent, and nothing else would catch it
      files: ../../docs/standards/naming/command-surface.md, ../../docs/standards/automation/skills.md, ../../docs/knowledge/glossary.md, ../../docs/standards/**/index.md, ../../docs/standards/log.md
      verify: python plugins/claude-quenching/assets/hooks/okf-validate.py docs --json && ! grep -rq "quenching-specs-plan-propose\|quenching-specs-plan-refine\|quenching-specs-plan-apply\|quenching-specs-plan-update\|quenching-specs-plan-archive\|quenching-specs-plan-abandon\|quenching-specs-plan-from-claude\|quenching-specs-backlog-add\|quenching-specs-backlog-triage" docs/

## 6. Release verification

- [ ] 6.1 Full throwaway-workspace lifecycle exercise per proposal.md §Validation — new →
      section --write → promote refusal listing the missing sections OF THE DESTINATION PHASE
      (exit 2) → promote → next/task → `[!]` block → promote to archive; the basename
      byte-identical in all three folders at the end; okf-validate clean on `assets/docs`.
      Assert the phase-scoped rule in both directions: a freshly captured spec derives as
      `captured` (never `designed`), and a heading present with an empty body refuses.
      Self-contained by construction — it builds and discards its own workspace, so it carries no
      deferrable `verify:`. Under `end-of-plan` this exercise is the plan's real proof, and it runs
      before 6.3 touches the live workspace
- [ ] 6.2 Version lockstep bump — `plugin.json`, `VERSION`, `marketplace.json`, and the
      `VERSION` constant in `specs.py`
      files: .claude-plugin/plugin.json, VERSION, ../../.claude-plugin/marketplace.json, assets/bin/specs.py
      verify: python assets/bin/specs.py --version
- [ ] 6.3 Migrate this repo's REAL `specs/` workspace with the align v2 flow proven in 3.3 —
      last, deliberately: this plan lives inside the workspace being migrated, so running it any
      earlier moves the plan out from under its own apply loop and leaves the remaining tasks to a
      v1 apply skill driving a v2 tool over v2 data. By this point the tool is built, the migration
      is proven on a copy, the skills are rewritten, and the lifecycle exercise has passed. Report
      any stray folder for human deletion, never auto-delete
      files: ../../specs/**
      verify: python plugins/claude-quenching/assets/bin/specs.py validate --json
