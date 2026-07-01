# 11. Data / domain catalog — `docs/catalog/`

> **Back path:** [../dimensions-template.md](../dimensions-template.md) (dimensions index +
> transversal doctrine) · [../../SKILL.md](../../SKILL.md) (agent roadmap).

- **Purpose:** table/model metadata (generated) + editorial curation (versioned); how skills consume the domain. Canonical home **`docs/catalog/`** (`docs/catalogo_dados/`/`docs/dominio/` are variants). Only applies to repos with explicit data/domain.

- **How "good" looks:** AUTO-GENERATED and curation **separated** (generated never hand-edited — same «X defines Y» rule); curation versioned separately; one doctrine governs domain consumption by skills.

- **Detection:** locate the catalog/domain (if any); check for manual editing in the AUTO-GENERATED block.

- **Smells:** curation written inside the generated block (will be overwritten); catalog outdated vs. the manifest/source; domain without consumption mapping.

- **Remediation:** move curation to the versioned area; regenerate via the correct generator.

- **Payload:** skill-template [../../assets/skills/quenching-docs/](../../assets/skills/quenching-docs/) (covers the domain/consumption doctrine). *Catalog generators are repo-specific — the method does not carry them; it only signals the generated×curation separation.*
