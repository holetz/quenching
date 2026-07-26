# Tasks — Ferramenta, escopo e avaliacao no front .claude/

Sections are ordered so each is independently shippable: stopping after any section leaves the
plugin in a coherent, releasable state (design.md §Decisions 10, §Risks "The plan is large").
All paths are relative to `plugins/claude-quenching/` unless stated otherwise.

## 1. Build the front's tool

- [x] 1.1 Create `assets/bin/skills.py` to the `specs.py` mold — stdlib only, argparse subcommands,
      `--json` on every one, exit codes 0 ok / 1 findings / 2 refusal, a `VERSION` constant, and
      the `python3`/`py` interpreter-resolution fallback the `specs/` skills already carry
      files: assets/bin/skills.py
      pattern: assets/bin/specs.py
      verify: python assets/bin/skills.py --version
- [x] 1.2 Implement `skills.py lint [path]` and the `sk-*` finding codes — description +
      `when_to_use` over 1,536 (error) and description over 1,024 (warn), trigger phrases absent
      from the second sentence, missing `Not for:` boundary, body over 500 lines, a numbered step
      with no `**Done when:**` criterion, unscoped `Bash` in `allowed-tools`, and
      `user-invocable`/`disable-model-invocation` incoherence
      files: assets/bin/skills.py
      verify: python assets/bin/skills.py lint skills --json
- [x] 1.3 Implement `skills.py doctor` — the bijection (every skill has a wrapper, every wrapper
      resolves to a skill), non-canonical names against the taxonomy, generic skills mirrored under
      a folder path, and name collisions
      files: assets/bin/skills.py
      verify: python assets/bin/skills.py doctor --json
- [x] 1.4 Implement `skills.py registry reindex` — regenerate the GENERATED zone from
      `.claude/skills/*/SKILL.md` frontmatter in the taxonomy's row format and byte-order,
      preserving curated prose outside the markers; the tool becomes the zone's format owner
      (design.md §Decisions 2)
      files: assets/bin/skills.py
      pattern: assets/bin/specs.py
      verify: python assets/bin/skills.py registry reindex --json
- [x] 1.5 Implement `skills.py budget` — per-skill and total always-on metadata characters
      (`description` + `when_to_use` + wrapper descriptions), sorted by cost, against a declared
      ceiling; findings exit 1 and never refuse (design.md §Decisions 4)
      files: assets/bin/skills.py
      verify: python assets/bin/skills.py budget --json
- [x] 1.6 Dogfood on this plugin's own surface: record the baseline `lint`, `doctor`, and `budget`
      output before any skill is edited, so section 3's reduction is measured against a number and
      not an impression
      verify: python assets/bin/skills.py budget --json
- [x] 1.7 Verify section 1: a throwaway target repo with a non-canonical name, a missing wrapper,
      an over-cap description, and a hand-edited registry zone yields one `sk-*` finding each, and
      `registry reindex` restores the zone byte-for-byte

## 2. Put the three skills on the rails

- [x] 2.1 Rewrite `quenching-skill-new` step 7 (OKF tail) and step 8 (self-check) to call
      `skills.py registry reindex` and `skills.py lint` instead of composing and diffing the
      registry table by hand
      files: skills/quenching-skill-new/SKILL.md
- [x] 2.2 Rewrite `quenching-skill-align` steps 1 and 5 to drive off `skills.py doctor --json` for
      the inventory and `skills.py lint --json` for the per-item conformance gaps, keeping the
      read-only-inventory-first rule intact
      files: skills/quenching-skill-align/SKILL.md
- [x] 2.3 Rewrite `quenching-skill-align-and-update` step 2 so the mechanical half of the doctrine
      audit consumes `lint --json` and the judgment half (no-op test, sediment, sprawl) stays a
      human read — Stage 2 remains read-only (design.md §Decisions 3)
      files: skills/quenching-skill-align-and-update/SKILL.md
- [x] 2.4 Update `skills/quenching-skill-new/references/taxonomy.md` §registry to cite
      `skills.py registry reindex` as the zone's owner instead of restating the row format
      files: skills/quenching-skill-new/references/taxonomy.md
- [x] 2.5 Add the `.claude/` row's verifier to `skills/quenching-align-all/references/sweep-doctrine.md`
      §6 — `skills.py lint` + `doctor`, replacing the prose verifier
      files: skills/quenching-align-all/references/sweep-doctrine.md
- [x] 2.6 Teach `quenching-skill-align` to install `skills.py` into a target's `.claude/hooks/`
      under the same version-comparison rule `quenching-specs-align` uses for `specs.py`
      files: skills/quenching-skill-align/SKILL.md
- [x] 2.7 Verify section 2: every `skills.py` invocation named in the three skills exists in the
      tool's `--help`, and no skill still describes generating the registry table by hand

## 3. Put the surface on a measured diet

- [x] 3.1 Bring the descriptions over the 1,024-character Agent Skills limit under it (17 today,
      reported as `sk-description-portable`) without removing a trigger phrase; where a
      description cannot shrink without losing one, report the skill and leave it to
      `/skill:eval`'s description tuning (design.md §Decisions 9). The 1,536 cap has no violator
      — see 1.6's baseline
      verify: python assets/bin/skills.py lint skills --json
- [x] 3.2 Cut `when_to_use` text that restates the description's `Not for:` boundary across the
      28 shipped skills — frontmatter only, bodies untouched (design.md §Decisions 9)
      verify: python assets/bin/skills.py budget --json
- [x] 3.3 Flatten the 2-level reference chain: `sweep-doctrine.md` §2's deferral to
      `convergence.md` §cycle-authorization becomes a self-contained statement, so no
      `references/` file sends a reader to another `references/` file
      files: skills/quenching-align-all/references/sweep-doctrine.md, skills/quenching-align-and-update-all/references/convergence.md
- [x] 3.4 Add a table of contents to every `references/*.md` over 100 lines (11 of the 21 files
      today), so a partial read still shows the full scope
- [x] 3.5 Verify section 3: `budget` reports a total below the 36,503-character baseline recorded
      in 1.6, and `lint` reports zero `sk-description-portable` findings except the ones 3.1
      reported as unshrinkable without losing a trigger
      verify: python assets/bin/skills.py budget --json

## 4. Write the front's standards

- [x] 4.1 Extend `docs/standards/automation/skills.md` with the invocation/permission decision
      table (`user-invocable` × `disable-model-invocation` × `context: fork`), the
      scoped-`allowed-tools` rule, and `skills.py` named as the front's verifier (stays
      `authority: current`)
- [x] 4.2 Write `docs/standards/automation/context-budget.md` — the two caps, the rule that both
      are counted on the parsed value and never on the YAML source, what `when_to_use` may carry,
      the per-surface ceiling at its measured baseline of 36,503, and `skills.py budget` as its
      measurement (`authority: background` until the ceiling is proved — design.md §Open Decisions)
- [x] 4.3 Update `docs/standards/naming/command-surface.md` — the bijection count at 31 ↔ 31 and
      the wrapper's stated trade-off now that commands and skills are one mechanism, with its
      revisit trigger (`authority: current`)
- [x] 4.4 Fix `quenching-skill-align`'s own frontmatter under 4.1 — scope its `Bash` grant to the
      commands the workflow actually runs
      files: skills/quenching-skill-align/SKILL.md
      verify: python assets/bin/skills.py lint skills --json
- [x] 4.5 Update `skills/quenching-skill-new/references/doctrine.md` and `taxonomy.md` to cite the
      new standards and the `sk-*` codes rather than restating thresholds
      files: skills/quenching-skill-new/references/doctrine.md, skills/quenching-skill-new/references/taxonomy.md
- [x] 4.6 Update `assets/templates/automation/{skill,command,skills-standard,registry}.md` for
      invocation control, scoped `allowed-tools`, `${CLAUDE_SKILL_DIR}`, and the tool-owned zone
- [x] 4.7 Verify section 4: `okf-validate.py docs` exits 0, and every standard written here is
      listed by its home `index.md` and recorded in `docs/log.md`
      verify: python assets/hooks/okf-validate.py ../../docs

## 5. Mint quenching-skill-eval

- [x] 5.1 Write `skills/quenching-skill-eval/SKILL.md` — authors `evals/evals.json`, runs each case
      in an isolated subagent with and without the skill, grades assertions with evidence, and
      aggregates the delta; description under the cap with triggers in the second sentence
      files: skills/quenching-skill-eval/SKILL.md
      verify: python assets/bin/skills.py lint skills --json
- [x] 5.2 Write `skills/quenching-skill-eval/references/evaluation.md` — the `evals.json` /
      `grading.json` / `benchmark.json` shapes adopted verbatim from `skill-creator`, assertion
      quality rules, and the description-tuning loop (should-trigger / should-not-trigger)
      files: skills/quenching-skill-eval/references/evaluation.md
- [x] 5.3 Write the wrapper `commands/skill/eval.md` → `/skill:eval`
      files: commands/skill/eval.md
      pattern: commands/skill/new.md
- [x] 5.4 Write `docs/standards/automation/skill-evaluation.md` — the evaluation contract: artifact
      locations and shapes, isolated with/without runs, evidence-backed grading, the benchmark
      delta, and what a skill must show before its description is tuned
- [x] 5.5 Verify section 5: run the loop once against an existing skill and commit the resulting
      `evals/evals.json`, `grading.json`, and `benchmark.json` as the first worked example

## 6. Extend the front to subagents

- [ ] 6.1 Extend `quenching-skill-align` step 1 to inventory `.claude/agents/`, `settings.json`
      (hook wiring and permissions), and `.claude/workflows/` — **report-only**, no rename and no
      write (design.md §Risks "Extending the inventory widens the sweep's blast radius")
      files: skills/quenching-skill-align/SKILL.md
- [ ] 6.2 Add the corresponding `sk-*` codes to `skills.py doctor` for the reported surfaces
      files: assets/bin/skills.py
      verify: python assets/bin/skills.py doctor --json
- [ ] 6.3 Write `skills/quenching-skill-agent-new/SKILL.md` — mints ONE subagent definition under
      the one-plan-one-OK discipline, with frontmatter fields, tool scoping, and the OKF tail
      files: skills/quenching-skill-agent-new/SKILL.md
      verify: python assets/bin/skills.py lint skills --json
- [ ] 6.4 Write the wrapper `commands/skill/agent/new.md` → `/skill:agent:new`
      files: commands/skill/agent/new.md
      pattern: commands/skill/new.md
- [ ] 6.5 Write `docs/standards/automation/agents.md` — when work is a subagent rather than a
      skill, the frontmatter contract, tool scoping, and how `agents/` is inventoried
- [ ] 6.6 Verify section 6: a fixture repo carrying `.claude/agents/` and a `settings.json` hook
      block produces the expected `sk-*` report and no write outside the confirmed plan

## 7. Mint quenching-skill-package

- [ ] 7.1 Write `skills/quenching-skill-package/SKILL.md` — turns a repo's `.claude/` surface into
      a distributable plugin: `.claude-plugin/plugin.json`, the `skills/` + `commands/` layout, the
      `VERSION` lockstep, and the marketplace entry
      files: skills/quenching-skill-package/SKILL.md
      verify: python assets/bin/skills.py lint skills --json
- [ ] 7.2 Write the wrapper `commands/skill/package.md` → `/skill:package`
      files: commands/skill/package.md
      pattern: commands/skill/new.md
- [ ] 7.3 Verify section 7: packaging a throwaway repo's surface produces a plugin whose manifests
      parse and whose skill count matches its `.claude/skills/`

## 8. Lockstep, manuals, and release

- [ ] 8.1 Bring `assets/claude/QUENCHING.md` to the new command surface (`/skill:eval`,
      `/skill:agent:new`, `/skill:package`) and to `skills.py` as the front's installed tool
      files: assets/claude/QUENCHING.md
- [ ] 8.2 Bring `assets/docs/QUENCHING.md` and `assets/specs/QUENCHING.md` to the new command
      surface — both enumerate it
      files: assets/docs/QUENCHING.md, assets/specs/QUENCHING.md
- [ ] 8.3 Update `plugins/claude-quenching/README.md` — the cost model rows for the three new
      skills and for the eval subagent fan-out
      files: README.md
- [ ] 8.4 Update the root `CLAUDE.md` — the skill count (28 → 31), the three new rows, `skills.py`
      in the tool inventory and in the release lockstep, and the `.claude/` front's verifier
- [ ] 8.5 Bump `VERSION`, `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, and the
      `VERSION` constant in all three scripts (`skills.py`, `specs.py`, `okf-validate.py`)
      verify: python assets/bin/skills.py --version
- [ ] 8.6 Verify the whole plan: `lint` exits 0 over 31 skills, `doctor` reports 31 ↔ 31, `budget`
      is below the 1.6 baseline, `okf-validate.py assets/docs` and
      `assets/specs/backlog --listing-root` both report `0 error(s), 0 warning(s)`, and all four
      version sources agree
