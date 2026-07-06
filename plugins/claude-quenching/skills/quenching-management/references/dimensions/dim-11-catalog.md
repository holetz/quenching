# 11. Data / domain catalog — `docs/catalog/`

> **Back path:** [../dimensions-template.md](../dimensions-template.md) (dimensions index +
> transversal doctrine) · [../../SKILL.md](../../SKILL.md) (agent roadmap).

- **Purpose:** table/model metadata (generated) + editorial curation (versioned); how skills consume the domain. Canonical home **`docs/catalog/`** (`docs/catalogo_dados/`/`docs/dominio/` are variants). Only applies to repos with explicit data/domain.

- **How "good" looks:**
  - AUTO-GENERATED and curation **separated** (generated never hand-edited — same «X defines Y» rule); curation versioned separately; one doctrine governs domain consumption by skills.
  - **The catalog is a conformant OKF bundle** (Open Knowledge Format v0.1) — **additively**, on top of the method's own labels: one concept per `.md`, identity = file path; every page's frontmatter carries a non-empty **`type`** (`system`/`schema`/`table`) and a **`resource`** (URI/FQN of the underlying asset); the consolidated `<schema>.md` plays the role of the OKF `index.md`; an optional **`log.md`** at the bundle root (date-grouped chronological history, newest-first) is the home for catalog change history. Conformance never dilutes the taxonomy/curation and carries **no tooling/SDK dependency** — any OKF consumer (viewer, `kcmd`/MCP, non-Claude agent) can read the bundle as-is.
  - **Regeneration preserves unknown frontmatter keys** — the generator only owns the keys it stamps; curated or third-party fields survive every regeneration.

- **Detection:** locate the catalog/domain (if any); check for manual editing in the AUTO-GENERATED block; check every catalog page has a non-empty `type:` in frontmatter (block 11 in [../detection-and-smells.md](../detection-and-smells.md)).

- **Smells:** curation written inside the generated block (will be overwritten); catalog outdated vs. the manifest/source; domain without consumption mapping; **page without `type` in frontmatter** (bundle non-conformant — invisible to OKF consumers); **`type` overloaded with the engine flavor** (`postgres`/`databricks-uc` in `type` — concept-type collision; the engine lives in `engine:`); **regeneration that strips curated/unknown frontmatter keys**.

- **Remediation:** move curation to the versioned area; regenerate via the correct generator; stamp `type`/`resource` from the catalog templates (additive — never rename/drop existing keys).

- **Payload:** skill-template [../../assets/skills/quenching-docs/](../../assets/skills/quenching-docs/) (covers the domain/consumption doctrine) + catalog templates [../../assets/templates/docs/catalog/](../../assets/templates/docs/catalog/) (`system.md`/`schema.md`/`table.md`, OKF-conformant frontmatter). *Catalog generators are repo-specific — the method does not carry them; it only signals the generated×curation separation.*
