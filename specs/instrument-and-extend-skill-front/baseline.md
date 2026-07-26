# Baseline — the .claude/ front before any skill is edited

Recorded by task 1.6 with `skills.py` at the commit that finished section 1, so section 3's
reduction is measured against a number rather than an impression. Every count is taken on the
PARSED frontmatter value, never on the YAML source lines.

## budget — always-on metadata

| Metric | Characters |
| --- | --- |
| Skill `description` + `when_to_use` | 34431 |
| Command wrapper `description` | 2072 |
| **Total always on** | **36503** (~9126 tokens) |

Ceiling: 36503 · exit 0 · 28 skills.

### Per skill, most expensive first

| Skill | Command | desc | when_to_use | wrapper | total |
| --- | --- | ---: | ---: | ---: | ---: |
| quenching-specs-align | /specs:align | 1272 | 234 | 82 | 1588 |
| quenching-specs-plan-refine | /specs:plan:refine | 1291 | 206 | 82 | 1579 |
| quenching-docs-align-and-update | /docs:align-and-update | 1266 | 216 | 79 | 1561 |
| quenching-docs-documentation-build | /docs:documentation:build | 1300 | 194 | 65 | 1559 |
| quenching-align-all | /align | 1270 | 193 | 78 | 1541 |
| quenching-skill-align | /skill:align | 1312 | 140 | 78 | 1530 |
| quenching-skill-align-and-update | /skill:align-and-update | 1170 | 254 | 81 | 1505 |
| quenching-specs-plan-apply | /specs:plan:apply | 1265 | 179 | 27 | 1471 |
| quenching-specs-align-and-update | /specs:align-and-update | 1122 | 253 | 70 | 1445 |
| quenching-docs-import | /docs:import | 1047 | 252 | 79 | 1378 |
| quenching-skill-new | /skill:new | 1147 | 146 | 82 | 1375 |
| quenching-specs-plan-abandon | /specs:plan:abandon | 1055 | 221 | 86 | 1362 |
| quenching-specs-plan-from-claude | /specs:plan:from-claude | 1023 | 244 | 90 | 1357 |
| quenching-specs-backlog-add | /specs:backlog:add | 1050 | 230 | 76 | 1356 |
| quenching-specs-backlog-triage | /specs:backlog:triage | 1096 | 181 | 72 | 1349 |
| quenching-align-and-update-all | /align-and-update | 1045 | 182 | 82 | 1309 |
| quenching-specs-plan-archive | /specs:plan:archive | 1034 | 202 | 62 | 1298 |
| quenching-specs-status | /specs:status | 1017 | 206 | 71 | 1294 |
| quenching-docs-align | /docs:align | 1069 | 145 | 78 | 1292 |
| quenching-specs-plan-propose | /specs:plan:propose | 933 | 223 | 69 | 1225 |
| quenching-specs-explore | /specs:explore | 884 | 190 | 72 | 1146 |
| quenching-docs-harness | /docs:harness | 866 | 188 | 69 | 1123 |
| quenching-docs-glossary-backfill | /docs:glossary-backfill | 785 | 207 | 75 | 1067 |
| quenching-specs-plan-update | /specs:plan:update | 810 | 169 | 77 | 1056 |
| quenching-docs-import-memory | /docs:import-memory | 785 | 170 | 73 | 1028 |
| quenching-docs-learn | /docs:learn | 702 | 205 | 72 | 979 |
| quenching-docs-define | /docs:define | 649 | 169 | 69 | 887 |
| quenching-docs-add | /docs:add | 631 | 136 | 76 | 843 |

## lint — per-skill conformance

Exit 0 · 28 skills · 46 findings, 0 of them errors.

| Code | Severity | Count |
| --- | --- | ---: |
| `sk-description-portable` | warn | 17 |
| `sk-step-criterion` | warn | 16 |
| `sk-unscoped-bash` | warn | 13 |

No skill exceeds the 1,536-character `sk-metadata-cap`. The largest always-on metadata is
1506 characters (`quenching-specs-align`) — see §Correction below.

## doctor — surface shape

Exit 0 · bijection 28 ↔ 28, 28 paired, holds: True.

- `sk-path-mismatch` (warn) — /align does not mirror `quenching-align-all` — a wrapper's path is its skill's flattened name
- `sk-path-mismatch` (warn) — /align-and-update does not mirror `quenching-align-and-update-all` — a wrapper's path is its skill's flattened name

## Correction to the proposal's measurements

The proposal reports 34,579 characters of skill metadata, 36,651 in total, and two skills over
the 1,536 cap (`quenching-specs-plan-refine` at 1,568 and `quenching-specs-plan-apply` at
1,559). Measured on parsed values those numbers are 34,431, 36,503, and **no skill over the
cap** — the two named skills measure 1,497 and 1,444.

The gap is the counting method. A description written as a folded `>-` block costs its folded
string; the block indentation and newlines are syntax the YAML parser removes before Claude
Code sees the field. Counted as source lines, `quenching-specs-plan-refine` is 1,565 and
`quenching-specs-align` is 1,574 — which is where the two reported violations come from, and
why the surface has three of them under that method rather than two.

The wrapper half is unaffected: 2,072 characters, matching the proposal exactly.

**What this changes:** task 3.1 has no cap violation to fix, and the ceiling in
`docs/standards/automation/context-budget.md` (task 4.2) is 36,503, not 36,651.
