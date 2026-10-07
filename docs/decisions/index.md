# `decisions/` — why a contract is the way it is

The **history and measurements** behind a contract: the dated measurement, the first cut that
failed, the chain of specs that moved a rule. A [standard](../standards/index.md) keeps only the
rule and a link here, so an agent reading the standard (`cq components read --rules-only`) pays for
the rule, not for how it was found. One decision per file, `type: decision`, numbered
`NNNN-<slug>.md` in the order written; a decision is **append-only**: a later one supersedes it
by saying so, never by rewriting it.

**Boundary:** `decisions/` = "why it became this rule". Distinct from
[standards/](../standards/index.md) (the rule itself) and [vision/](../vision/index.md) (direction).
An agreed-but-unproven rule is still a standard with `authority: background`; this home holds the
evidence, not the rule.

## Decisions

* [0001 — Spec backend measurements and history](0001-spec-backend-measurements.md) — the costs and false-for-a-year sentences behind the spec backend interface
* [0002 — Task execution contract history](0002-task-execution-history.md) — the attempt counter, the Handoff cadence and an unresolvable archived subject
* [0003 — Plan git record history](0003-plan-git-record-history.md) — the host-link default-branch rule, the in-place liveness exception and the unproven azure-boards assumption
* [0004 — Frontmatter source lineage](0004-standards-source-lineage.md) — the long `source:` lineage moved out of the standards' frontmatter
* [0005 — Glossary long forms](0005-glossary-long-forms.md) — the parts of glossary entries removed to keep each to one sentence
