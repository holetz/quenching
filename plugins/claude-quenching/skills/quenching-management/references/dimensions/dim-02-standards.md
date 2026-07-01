# 2. Standards — the current/active standards layer (`docs/standards/`)

> **Back path:** [../dimensions-template.md](../dimensions-template.md) (dimensions index +
> transversal doctrine) · [../../SKILL.md](../../SKILL.md) (agent roadmap).

> The complete `docs/` tree (all homes + subfolders, purpose, Diátaxis,
> `audience`/`authority`, boundaries) is the **prescriptive canonical taxonomy** — single
> source in [../docs-taxonomy.md](../docs-taxonomy.md). This dimension gives the short directive +
> the smells; **do not copy the tree** (Simplicity First) — link.

- **Purpose:** the **current/active** standard/contract (how it should be and why), versioned — the shared source of truth. Canonical home **`docs/standards/`** (subfolders by subject: `architecture/`, `code/`, `naming/`, `data-modeling/`, `ci-cd/`, `workflows/`, `mlops/`, `quality/`, `platform/`). It is **one home** of the taxonomy, not the whole `docs/`.

- **How "good" looks:**
  - subfolders by subject; **`INDEX.md`** in sync (lists exactly the docs that exist); minimal frontmatter (`title`/`updated`/`status: current`/`audience`/`authority`); **one standard per file**; names in **English kebab-case**.
  - **Home = subject** (subject-first); **content inside the home = Diátaxis** (reference/explanation here).
  - **Canonical convergence:** the skill defines the taxonomy; the repo **converges to it** — every repo in the **SAME tree of identical names**, so someone moving between repos sees the tree **literally identical** (instead of re-mapping "by function"). Variant name (`docs/arquitetura/`, `docs/adr/`) is a **non-convergence smell** → migration candidate, not a convention to preserve.
  - **Variant migration (deterministic, safe):** map variant→canonical, **flag as DEPRECATABLE** and **PROPOSE** — **never rename/delete without OK** (Step 5 confirmation + deprecation doctrine).
  - **Label + binary by sidecar:** `audience: both`/`agent` · `authority: current`/`background`; the LLM reads the `.md` extract, never the `.pdf`/`.pptx` — part of the taxonomy (see [../docs-taxonomy.md](../docs-taxonomy.md)).
  - **Complete for agent = passes the reconstruction test** (Augment Code "rebuild test"): a new agent reconstructs the behavior **solely from the doc**, without asking the human. For this, the standard carries the **requirement** (*what* applies) **AND** the **decision** (*why* + alternatives; a requirements-only doc regenerates different behavior every time).
  - **Current/active is de-facto proven, anchored in `file:line`** — external best practice the repo does NOT follow is a **PROPOSAL/GAP** (`authority: background`), never stated as current/active.
  - **`INDEX.md` is a DERIVED artifact** — regenerated from disk between `<!-- BEGIN/END GENERATED -->` markers (rule «X defines Y»), not hand-written; structural drift becomes impossible by construction.

- **Detection:** derive against the **canonical names** first (Step 0); cross-reference the `INDEX.md` list with actual files; `grep` for pointers to old paths; detect variant names (`arquitetura/`/`adr/`/`VISION.md`); check for missing canonical homes; check audience+provenance label per doc/folder; check `.md` sidecar next to each binary and that no sidecar has `authority: current` — item **2b** in [../detection-and-smells.md](../detection-and-smells.md).

- **Smells:**
  - **index lies** (cites nonexistent doc / missing new doc); **index hand-edited diverging from disk** (should be regenerated between `<!-- BEGIN/END GENERATED -->`); standard without short directive in CLAUDE.md; direction or open-decision mixed in here; doc without frontmatter.
  - **non-converged variant name** — `docs/arquitetura/`, `docs/adr/`, single `VISION.md`, `docs/patterns/` as a silo = migration candidate (not "repo convention that wins").
  - **`docs/` without canonical segmentation** — loose technical markdown at the root of `docs/`, without named homes (the agent sweeps everything).
  - **TWO-HOMES** — `docs/arquitetura/` AND `docs/standards/` coexisting, or `adr/` AND `decisions/`: single-home violation (dim 12), one migrates to the other.
  - **human material leaking into the technical layer** — slides/diagrams/PDFs in `standards/` or at the root, without the `presentations/`/`reference/` home.
  - **doc without declared audience/authority**; **human/external material marked as current/active** (slide/PDF/standard without `authority: background` cited as a contract).
  - **binary without sidecar/extract** (the agent would ingest the binary, ~7x tokens, low signal); **sidecar without provenance or marked as current/active**.
  - **repo section without canonical home** (`NO-HOME`) — technical folder that doesn't match any home (home to be added, or material in the wrong quadrant).
  - **directed communication outside its home** — incident/change/deploy notice loose at the root, in `guides/`/`standards/`, without the `communications/` home; **channel without template** (`communications/templates/<channel>.md` absent, form becomes ad-hoc); **communication without a scannable header** (without scope/status/impact/audience/validity/action/last-updated); **communication marked as current/active** (should be `authority: background`; what became a rule **distills to `standards/`**).
  - **standard stated as `current/active` WITHOUT `file:line` anchor** — external best practice promoted to contract without proof the repo follows it (capability/outcome hallucination risk).
  - **`standards/` layer with only an empty skeleton** — homes exist but were never populated from the repo.

- **Remediation:** sync `INDEX.md`/pointers; move direction→`vision/` or decision→`decisions/`; **install the canonical taxonomy** (procedure in [../installation.md](../installation.md)): map each section to the **canonical** home by function, **propose the variant migration** (deprecatable, with OK), install only the absent homes **that apply**, move each material to the right home (technical→`standards/`/subject; human→`presentations/`; external→`reference/`); **label** each doc/folder with audience+provenance; **create the sidecar/extract** next to each consulted binary — or, for reference-only material, **a folder index**, without extracting for the sake of it.

- **Payload:** (the canonical tree is specified in [../docs-taxonomy.md](../docs-taxonomy.md))

  - **authoring/editing ONE doc** → skill-template [../../assets/skills/quenching-docs/](../../assets/skills/quenching-docs/) (docs-as-code: authoring + index sync) + **canonical taxonomy skeleton** [../../assets/docs/](../../assets/docs/) (second agent scaffold) + **audience+provenance frontmatter** [../../assets/templates/docs/docs-front.md](../../assets/templates/docs/docs-front.md) + **sidecar/extract** [../../assets/templates/docs/sidecar.md](../../assets/templates/docs/sidecar.md).
  - **building/updating the ENTIRE `standards/` layer** (≠ authoring ONE doc) → **orchestrating skill** [../../assets/skills/quenching-standards/](../../assets/skills/quenching-standards/) + **parallel worker** [../../assets/agents/quenching-writer.md](../../assets/agents/quenching-writer.md): fan-out of one `quenching-writer` per subject in parallel (each one mines the de-facto = `current/active` anchored in `file:line` + external research, gap = **PROPOSAL**, never current/active) and **deterministically regenerates `INDEX.md` from disk** (between markers). Composes with `quenching-docs`, does not duplicate.
  - **directed communication** (`communications/` home) → **skeleton** [../../assets/docs/communications/](../../assets/docs/communications/) (`README` + `templates/` per channel `email`/`chat`/`wiki`/`markdown` + `archive/`) + **generic skill** [../../assets/skills/quenching-announcement/](../../assets/skills/quenching-announcement/) that reads the requested channel template and fills it in (not one per subject).
  - **runtime enforcement** (crosses dim 8) → **PostToolUse hook** [../../assets/hooks/propose-docs-home.py](../../assets/hooks/propose-docs-home.py): when touching a file under `docs/`, **proposes** the absent canonical home/slot reusing the criteria from block 2b.
