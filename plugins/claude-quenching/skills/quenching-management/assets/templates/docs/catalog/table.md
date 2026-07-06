---
title: <system>.<catalog>.<schema>.<table>
type: table             # concept type (OKF) — non-empty on every catalog page
resource: <URI/FQN of the underlying asset — e.g. uc://<catalog>.<schema>.<table>>
audience: both
authority: current
source: <metadata origin — UC, origin dictionary, curation>
maintainer: <owning team>
updated: <YYYY-MM-DD>
---

<!-- AUTO-GENERATED — do not edit (remove this line if the page is fully curated) -->

# `<table>`

`<system>.<catalog>.<schema>.<table>` · **grain:** `<one line>` · **key:**
`<pk>`

System access: [`../../README.md`](../../README.md) · schema index:
[`../<schema>.md`](../<schema>.md).

## Columns

| Column | Type | Description |
|---|---|---|
| `<col>` | `<type>` | `<description — leave blank if the origin does not expose it; fill in via curation>` |

## Build

- **Script(s) that materialize it:** `<repo/folder/file>` — `<what it does>`.
- **Main transformation:** `<summary — upstream source → this table>`.

## Related

- **Upstream:** `<source tables/scripts>`.
- **Downstream:** `<who consumes this table>`.

<!-- /AUTO-GENERATED -->

## Curated observation

`<grain, unit, gotchas, usage — survives regeneration; the only section outside the
AUTO-GENERATED block in a generated page>`.
