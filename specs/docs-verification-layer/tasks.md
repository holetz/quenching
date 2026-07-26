# Tasks — Verification layer for the docs/ front

## 1. Fixtures first

- [x] 1.1 Create a throwaway fixture bundle under the scratchpad with one doc per new code: a
      `resource:` naming a nonexistent path, a `resource` glob containing the doc itself, a
      `glossary.md` linking a deleted doc, and a doc whose `timestamp` predates the last commit
      touching its `resource` globs
      verify: python3 plugins/claude-quenching/assets/hooks/okf-validate.py <fixture> --json
- [x] 1.2 Record the current baseline so regressions are visible: run the validator over
      `assets/docs` and over `assets/specs/backlog --listing-root` and capture both outputs
      verify: python3 plugins/claude-quenching/assets/hooks/okf-validate.py plugins/claude-quenching/assets/docs

## 2. Resource integrity checks

- [x] 2.1 Add a `resource` parser: split on commas, trim, classify each entry as path-shaped,
      glob-shaped (`*`/`**` only), URI-shaped, or unparseable
      files: plugins/claude-quenching/assets/hooks/okf-validate.py
- [x] 2.2 Add `resource-unresolved` (WARN) — a path- or glob-shaped entry matching nothing on disk;
      an entry the parser cannot classify is reported as unknown, never as a violation
      files: plugins/claude-quenching/assets/hooks/okf-validate.py
      verify: python3 plugins/claude-quenching/assets/hooks/okf-validate.py <fixture> --json
- [x] 2.3 Add `resource-self` (WARN) — the doc's own path falls inside its declared resource scope
      files: plugins/claude-quenching/assets/hooks/okf-validate.py
- [x] 2.4 Generalize `TYPES_WITHOUT_RESOURCE` into a bundle-aggregate exemption covering
      `knowledge/glossary.md`, so it keeps `resource: docs/**` without firing `resource-self`
      files: plugins/claude-quenching/assets/hooks/okf-validate.py
      pattern: plugins/claude-quenching/assets/hooks/okf-validate.py

## 3. Glossary links and staleness

- [x] 3.1 Add `glossary-broken-link` (WARN) — apply the existing `index-broken-link` link-resolution
      rule to `knowledge/glossary.md`, reusing the same helper rather than a second implementation
      files: plugins/claude-quenching/assets/hooks/okf-validate.py
- [x] 3.2 Add `stale-doc` (WARN, advisory) — `git log -1 --format=%cI` over the resource globs using
      explicit `:(glob)` pathspec magic, compared against `timestamp`; pin the pathspec behavior
      with a fixture that would fail under naive passing
      files: plugins/claude-quenching/assets/hooks/okf-validate.py
      verify: python3 plugins/claude-quenching/assets/hooks/okf-validate.py <fixture> --json
- [x] 3.3 Gate `stale-doc` to CLI only — never `PostToolUse`, never `Stop` — and skip it silently
      when the tree is not a git checkout
      files: plugins/claude-quenching/assets/hooks/okf-validate.py
- [x] 3.4 Fix the shipped seed's self-pointing `resource` per the 2.4 exemption, and confirm the
      skeleton still validates clean
      files: plugins/claude-quenching/assets/docs/knowledge/glossary.md
      verify: python3 plugins/claude-quenching/assets/hooks/okf-validate.py plugins/claude-quenching/assets/docs
- [x] 3.5 Document the four new codes in the conformance contract — their severity, which are
      must-fix in a skill's verify gate, and that `stale-doc` is advisory and CLI-only
      files: plugins/claude-quenching/skills/quenching-docs-align/references/conformance.md

## 4. The status skill

- [x] 4.1 Write `quenching-docs-status/SKILL.md` — read-only (`allowed-tools` with no `Write`/`Edit`),
      description under the 1,536-char cap with trigger phrases in the second sentence, no
      `context: fork`, owning no contract and citing `conformance.md` and `cycle.md`
      files: plugins/claude-quenching/skills/quenching-docs-status/SKILL.md
      pattern: plugins/claude-quenching/skills/quenching-specs-status/SKILL.md
- [x] 4.2 Add the report's three sections — what `/docs:align` fixes, what `/docs:align-and-update`
      drives, what neither closes — routed by `cycle.md`'s opportunity table, cited not restated
      files: plugins/claude-quenching/skills/quenching-docs-status/SKILL.md
- [x] 4.3 Add the density table (homes scaffolded vs empty, concept docs per home, glossary term
      count) as reported figures carrying no finding code, and verify the skill's finding
      vocabulary matches `conformance.md` exactly
      files: plugins/claude-quenching/skills/quenching-docs-status/SKILL.md
- [x] 4.4 Write the mirrored wrapper `/docs:status`
      files: plugins/claude-quenching/commands/docs/status.md
      pattern: plugins/claude-quenching/commands/specs/status.md
- [x] 4.5 Run `/docs:status` against this repository and confirm it writes nothing and reports the
      five concept docs, the empty homes and the one-entry glossary
      verify: git status --porcelain

## 5. The standard and the deferred work

- [x] 5.1 Write `docs/standards/quality/bundle-verification.md` (`authority: current` once the
      checks land) — what the front machine-checks versus what it leaves to a skill's prose
      self-check, the rule that an invariant restated in more than two skills is owed a
      deterministic check, and the comma-separated `resource` glob-set format
      files: docs/standards/quality/bundle-verification.md
- [x] 5.2 Correct the `file:line` instruction in the four skills that state it, so the doctrine
      describes the glob-set practice it actually produced
      files: plugins/claude-quenching/skills/quenching-docs-add/SKILL.md, plugins/claude-quenching/skills/quenching-docs-add/references/homes.md, plugins/claude-quenching/skills/quenching-docs-align/SKILL.md, plugins/claude-quenching/skills/quenching-docs-learn/SKILL.md
- [x] 5.3 Record the empty-home observation from 4.5 in `design.md` §Open Decisions, and park the
      two deferred items — import provenance and the AGENTS.md harness inversion — via
      `/specs:backlog:add`

## 6. Surface lockstep

- [x] 6.1 Enumerate `/docs:status` in all three operator manuals
      files: plugins/claude-quenching/assets/docs/QUENCHING.md, plugins/claude-quenching/assets/specs/QUENCHING.md, plugins/claude-quenching/assets/claude/QUENCHING.md
- [x] 6.2 Update the skill count and the stale 27 ↔ 27 bijection to the true current count
      files: CLAUDE.md, plugins/claude-quenching/README.md, docs/standards/naming/command-surface.md
- [x] 6.3 Bump the release quartet in lockstep
      files: plugins/claude-quenching/VERSION, plugins/claude-quenching/.claude-plugin/plugin.json, .claude-plugin/marketplace.json, plugins/claude-quenching/assets/bin/specs.py, plugins/claude-quenching/assets/hooks/okf-validate.py

## 7. Verification

- [x] 7.1 Both skeleton validations clean
      verify: python3 plugins/claude-quenching/assets/hooks/okf-validate.py plugins/claude-quenching/assets/docs
- [x] 7.2 Backlog listing root still clean — the new checks must not regress it
      verify: python3 plugins/claude-quenching/assets/hooks/okf-validate.py plugins/claude-quenching/assets/specs/backlog --listing-root
- [x] 7.3 Each new code fires on its fixture and stays silent on the skeleton; no existing code
      changed severity; `--json` stays parseable with a code, severity and path per finding
      verify: python3 plugins/claude-quenching/assets/hooks/okf-validate.py <fixture> --json
- [x] 7.4 Version lockstep and the wrapper bijection both hold
      verify: python3 plugins/claude-quenching/assets/hooks/okf-validate.py --version
