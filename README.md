# quenching

A **Claude Code plugin** that forces any repository's `docs/` into a single
canonical **[Open Knowledge Format (OKF v0.1)](https://github.com/GoogleCloudPlatform/knowledge-catalog)**
bundle — and keeps it that way. Every repository that adopts it ends up with the
**same rich, greppable knowledge tree** in the same places, so anyone moving
between repos sees one structure.

This repository is a **plugin marketplace**. The plugin itself lives in
[`plugins/quenching/`](plugins/quenching/).

## What it does

Eight skills, plus one enforcement hook:

| Skill | Role |
| --- | --- |
| **`quenching-docs-align`** | Installs the canonical OKF bundle (incl. the fixed `knowledge/glossary.md` seed), **force-aligns** an existing `docs/` to it (migrates variant names, relocates misfiled docs, stamps required frontmatter, reserves `index.md` as a listing, establishes `log.md`, writes `okf_version` at the root), then validates. Invasive: presents a full plan, executes on **one** confirmation (code-coupled renames confirm on their own). |
| **`quenching-docs-add`** | Adds a **new** piece of knowledge (a standard, catalog table, announcement, …) into the correct home with a complete OKF stamp, updates the folder's `index.md`, appends to `log.md`, enriches the glossary on a new term, and validates. |
| **`quenching-docs-learn`** | Captures one piece of **generic knowledge** the human states (a concept, glossary term, explanation, learning) into the `knowledge/` home with a `type: knowledge` stamp, an updated `index.md`, a `log.md` entry, and a glossary entry for any new term. |
| **`quenching-docs-glossary-backfill`** | Sweeps the **entire** `docs/` bundle for repo-specific terms that already exist in the docs but were never fed into the glossary, fanning out sub-agents per home and backfilling them in one consolidated pass. |
| **`quenching-docs-define`** | Adds or refines **one** entry in the fixed glossary `knowledge/glossary.md` — the repo's A–Z term lookup — placing the entry alphabetically, deriving the link to the concept doc, MERGE never clobber. The on-demand counterpart of the glossary tail step the other knowledge skills run. |
| **`quenching-docs-import-memory`** | Drains the project's Claude Code memory (`~/.claude/projects/<cwd>/memory/`) into the bundle — promoting each memory into its home — then **clears each memory** once its doc lands and passes the conformance check. |
| **`quenching-docs-harness`** | Refactors the repo's `CLAUDE.md`/`AGENTS.md` into **thin, honest pointers** over the bundle: keeps the operational (commands, env, etiquette), **moves** inlined knowledge into its `docs/` home, points at the glossary for term resolution, and self-verifies every pointer resolves (the validator exempts harness files). |
| **`quenching-docs-align-and-update`** | The **conductor**. Runs the sweep/structural skills as a dependency pipeline (`align` → `memory-to-docs` → `harness` → `knowledge-scan`) **pass after pass** — **one** OK at cycle start authorizes the whole run (code-coupled items still gate individually) — until a full pass changes nothing and the validator is clean, **exhausting** a repo's OKF improvement opportunities. Conducts, never reimplements: every change is the sub-skill's; per-item content gaps are surfaced, never fabricated. Bounded by a pass cap so it converges or reports residue, never spins. |

The **`okf-validate.py`** hook (self-contained, no dependencies) keeps future edits
conformant: it validates touched `docs/**` files against the OKF core on
`Write`/`Edit` and at `Stop`, and can optionally block a non-conformant write.

## Install

Local (no marketplace publish needed):

```bash
claude --plugin-dir ./plugins/quenching
```

Then, inside a target repository:

```
/quenching:quenching-docs-align            # install + force the knowledge base into OKF shape
/quenching:quenching-docs-add           # add a new standard / table / announcement
/quenching:quenching-docs-learn        # capture a piece of generic knowledge
/quenching:quenching-docs-glossary-backfill   # backfill the glossary from the whole bundle
/quenching:quenching-docs-define         # add / refine one glossary term
/quenching:quenching-docs-import-memory   # drain project memory into the bundle
/quenching:quenching-docs-harness          # refactor CLAUDE.md/AGENTS.md into thin pointers
/quenching:quenching-docs-align-and-update            # loop the sweep skills to OKF convergence
```

Or add this marketplace and enable the plugin the usual way (see the
[plugin README](plugins/quenching/README.md)).

> **Succession note.** This plugin reuses the marketplace/plugin **name**
> `quenching` as the lean, OKF-centric successor of the 15-dimension
> audit plugin. **Do not enable both at once** (name collision) — this one
> replaces it.

## Cost model

Skill metadata fits Claude Code's 1,536-char per-skill listing cap (trigger phrases in the
second sentence, truncation-safe); skill bodies load only on invocation and shared procedure
lives once in its owning reference file; heavy sweeps fan out to cheaper sub-agents (haiku /
sonnet at low effort) while every classification and destructive gate stays on the session
model; and the enforcement hook's `Stop` sweep is dirty-gated — a turn that touches no
`docs/**` file costs one stat. Full policy:
[plugin README → Cost model](plugins/quenching/README.md#cost-model).

## License

[MIT](LICENSE) © Israel Holetz.
