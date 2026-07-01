# 5. Open decisions — `docs/decisions/`

> **Back path:** [../dimensions-template.md](../dimensions-template.md) (dimensions index +
> transversal doctrine) · [../../SKILL.md](../../SKILL.md) (agent roadmap).

- **Purpose:** decision **not yet implemented**, under debate, with weighed alternatives. Canonical home **`docs/decisions/`** — MADR recommends **verbatim** *"Create folder `docs/decisions`"*.

- **How "good" looks:** one `NNNN-slug/` folder per ADR under `decisions/`; **removed + distilled** to `standards/` upon implementation; a "Distilled" ledger preserved; references (`sdd_slug`/`vision_refs`) in the frontmatter. `docs/adr/` is a variant name (migration candidate to `docs/decisions/`).

- **Detection:** read the README/index of `decisions/` + the folders; cross-reference ADRs marked as implemented with the ledger; detect `docs/adr/` as a variant to migrate.

- **Smells:** already-implemented ADR that didn't leave the tree; **current/active** decision stalled as an ADR; unresolvable ADR number; "how" (implementation) inside the ADR; **`docs/adr/`** instead of `docs/decisions/` (variant), or both coexisting (`TWO-HOMES`).

- **Remediation:** distill→`standards/` and remove; update the ledger; migrate `docs/adr/` → `docs/decisions/` (propose, with OK).

- **Payload:** skill-template [../../assets/skills/quenching-docs/](../../assets/skills/quenching-docs/) (covers ADR/decision) + `decisions/` skeleton from canonical scaffold [../../assets/docs/](../../assets/docs/) (second agent) + template [../../assets/templates/docs/decisions/adr.md](../../assets/templates/docs/decisions/adr.md). Specification: [../docs-taxonomy.md](../docs-taxonomy.md).
