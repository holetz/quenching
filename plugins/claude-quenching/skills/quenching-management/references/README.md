# `references/` — the operational detail of the method

> **Way back:** agent roadmap → [../SKILL.md](../SKILL.md). The files in this
> folder are **dense agent reference**; the human-facing overview and
> architecture live in the project documentation site.

This folder holds the **detail** that [SKILL.md](../SKILL.md) loads on demand.
`SKILL.md` is the **roadmap** (the 8 audit/install steps); each file here is the
**reference** a step consults. You don't need to read everything: open the file
for the step you're on.

> **One-sentence summary:** the method looks at a repo, measures 15 knowledge
> dimensions against a standard, delivers a prioritized report and installs
> what's missing. The files below are, in this order, **what to measure**, **how
> to measure**, **how to prioritize**, **how to report** and **how to install**.

## The 7 files

| File | What it is | When to open |
| --- | --- | --- |
| [dimensions-template.md](dimensions-template.md) | **The heart.** The **index** of the 15 dimensions + the transversal doctrine (ADAPTABLE preamble, canonical-`docs/`-names exception, 6-field explanation, scoring). Each dimension is one file under [dimensions/](dimensions/README.md), self-contained: purpose · how "good" looks · detection · smells · remediation · payload. Open only the dimension you are scoring. | Steps 2-3 (inventory and score each dimension). Start here to understand the method. |
| [docs-taxonomy.md](docs-taxonomy.md) | The **canonical `docs/` tree** (single source): the homes (`standards/`, `decisions/`, `vision/`, `backlog/`, `guides/`, `reference/`, `catalog/`, `communications/`, `presentations/`), their boundaries and the variant→canonical mapping. | Whenever the task touches `docs/` (dims 2/3/5/11). Dimensions and detection **link** here instead of repeating the tree. |
| [scripts-taxonomy.md](scripts-taxonomy.md) | The **canonical `scripts/` organization** (single source): purpose subfolders (`ci`/`<gen>`/`checks`/`maintenance`/`dev`), README-map, execution convention, and the boundaries `repo scripts/` × `.claude/hooks/*` × skill-internal `scripts/` × `src/`. | Whenever the task touches the executable logic invoked by the surface (dim 8, crosses 1/9). Dim 8 and detection **link** here. |
| [detection-and-smells.md](detection-and-smells.md) | The detection **cookbook**: the rule of 4 states + Step 0 (derive the repo's paths) + read-only bash per dimension. Only commands + how to read the result; *doctrine* lives in the dimensions. | Steps 1-2 (derive the repo's shape and run the greps). |
| [repo-profiles.md](repo-profiles.md) | Catalog of **repo profiles** (signals → emphasis): how to modulate priority for the concrete repo (monorepo, MLOps, greenfield…). Example guide, not an enum. | Step 4 (modulate the report's emphasis by profile). |
| [report-format.md](report-format.md) | The **skeleton of the audit report** (scorecard · prioritized gaps · deprecables · installation plan). | Step 4 (produce the output). |
| [installation.md](installation.md) | The **gap → package payload** map + the installation procedure, hook wiring and deprecation doctrine. | Steps 5-7 (install what's missing, with OK; deprecate what the repo already had). |

## How the files chain

```
SKILL.md (the roadmap, 8 steps)
   │
   1-2  derive shape + run detection ......... detection-and-smells.md
   2-3  measure each dimension against "good" . dimensions-template.md  (↘ docs-taxonomy.md for docs/)
   4    prioritize by repo shape ............. repo-profiles.md
   4    write the report ..................... report-format.md
   5-7  install payload / deprecate .......... installation.md
```

## Conventions of this folder

- **`dimensions-template.md` + [dimensions/](dimensions/README.md) are the home of
  DOCTRINE** (the *why* and decision criteria — the template is the index, each
  dimension its own file); **`detection-and-smells.md` is the home of BASH** (the *how
  to detect*). Detection blocks `1b/2b/6b/7b/8b/9b/14b` point to the corresponding
  dimension file instead of repeating the explanation.
- **`docs-taxonomy.md` is the single source of the `docs/` tree** — other files
  link there, don't copy.
- Everything here is **consulted reference**, not the spec that fires: the
  instructions the agent executes when the skill opens live in
  [SKILL.md](../SKILL.md). **Evolving** the method (not applying it) is a
  maintainer task, documented in the project's `CONTRIBUTING.md`.
