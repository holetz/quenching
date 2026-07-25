# Change log — `docs/` bundle

History of the OKF bundle, most recent first. Each entry is grouped under a
`## YYYY-MM-DD` heading and prefixed `**Creation**` / `**Update**` / `**Deprecation**`.
`quenching-docs-align` and `quenching-docs-add` append here whenever they scaffold, migrate, or insert.

## 2026-07-24

**Creation**: [Skill authoring and alignment](/docs/standards/automation/skills.md) distilled from
the archived `add-quenching-skill-pair` plan (`specs/archive/2026-07-24-add-quenching-skill-pair/`)
— the single-axis classification, authoring, and alignment contract for the skill surface.

**Creation**: [Command surface naming](/docs/standards/naming/command-surface.md) — the plugin's
skill + command-wrapper naming standard, superseding the retired `openspec/specs/command-naming`
spec (the `opsx:`/`openspec-*` rules no longer hold now that the spec-driven front is native).

**Update**: spec-driven workspace migrated `openspec/` → `specs/` (flat plans, no `config.yaml`,
no delta store); the OKF `docs/` bundle installed at the repo root and the `okf-validate.py` +
`specs.py` tools installed into `.claude/hooks/`.

## 2026-07-07

**Update**: [Glossary](/docs/knowledge/glossary.md) reformatted from a
`| Term | Definition | See |` table to a flat, `index.md`-style bullet list
(`* [<Term>](<path>.md) — <definition>`, or `* **<Term>** — <definition>` when unlinked) —
normalizes the glossary onto the same syntax every other listing uses; an unlinked entry
is a valid, permanent state. Also backfillable in bulk by the new `quenching-docs-glossary-backfill`.

**Creation**: [Glossary](/docs/knowledge/glossary.md) fixed seed added to `knowledge/` — the
repo's A–Z term lookup (`| Term | Definition | See |`), enriched by `quenching-docs-define` and, as
a tail step, by `quenching-docs-add` / `quenching-docs-learn` / `quenching-docs-import-memory`.

## 2026-07-06

**Creation**: [`knowledge/`](/docs/knowledge/index.md) home added — generic knowledge we hold
(concepts, explanations, learnings; `type: knowledge`), filled by `quenching-docs-learn`.

**Creation**: OKF bundle skeleton installed by `claude-quenching` (`quenching-docs-align`) —
homes scaffolded, `index.md` listings established, `okf_version: "0.1"` set at the root.
