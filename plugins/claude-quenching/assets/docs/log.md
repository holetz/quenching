# Change log — `docs/` bundle

History of the OKF bundle, most recent first. Each entry is grouped under a
`## YYYY-MM-DD` heading and prefixed `**Creation**` / `**Update**` / `**Deprecation**`.
`quenching-align` and `quenching-insert` append here whenever they scaffold, migrate, or insert.

## 2026-07-07

**Update**: [Glossary](/docs/knowledge/glossary.md) reformatted from a
`| Term | Definition | See |` table to a flat, `index.md`-style bullet list
(`* [<Term>](<path>.md) — <definition>`, or `* **<Term>** — <definition>` when unlinked) —
normalizes the glossary onto the same syntax every other listing uses; an unlinked entry
is a valid, permanent state. Also backfillable in bulk by the new `quenching-knowledge-scan`.

**Creation**: [Glossary](/docs/knowledge/glossary.md) fixed seed added to `knowledge/` — the
repo's A–Z term lookup (`| Term | Definition | See |`), enriched by `quenching-glossary` and, as
a tail step, by `quenching-insert` / `quenching-knowledge` / `quenching-memory-to-docs`.

## 2026-07-06

**Creation**: [`knowledge/`](/docs/knowledge/index.md) home added — generic knowledge we hold
(concepts, explanations, learnings; `type: knowledge`), filled by `quenching-knowledge`.

**Creation**: OKF bundle skeleton installed by `claude-quenching` (`quenching-align`) —
homes scaffolded, `index.md` listings established, `okf_version: "0.1"` set at the root.
