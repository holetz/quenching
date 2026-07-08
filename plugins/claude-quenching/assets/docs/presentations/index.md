# `presentations/` — human deliverables (binary)

Our **visual deliverables** — slides, source diagrams, reports. Binaries that belong in
`docs/` but **not** in the standards layer.

**The LLM never opens the binary** — it reads the **sidecar `.md`** alongside it (summary +
key points + `binary:` pointing to the source). The sidecar carries `type: sidecar`,
`audience: agent`, `authority: background`; the binary is `audience: human`.

**Boundary:** `presentations/` = "our **visual** deliverables" — distinct from
[reference/](/docs/reference/index.md) (external factual reference). Content that became
current/active **distills into [standards/](/docs/standards/index.md)**.

## Subfolders

* [slides/](slides/index.md) — decks (.pptx), onboarding exports
* [diagrams/](diagrams/index.md) — diagrams (prefer diagrams-as-code)
* [reports/](reports/index.md) — stakeholder reports / PDFs

Mold: `sidecar.md` (applied by `quenching-insert`).
