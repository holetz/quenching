# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

This repo is **two things at once**, and the distinction governs almost every decision here:

1. A **Claude Code plugin marketplace** ([`.claude-plugin/marketplace.json`](.claude-plugin/marketplace.json)) hosting a single plugin, **`claude-quenching`**.
2. The **development workspace** for that plugin — its evolution log, maintainer agents, and documentation-site source.

**The only thing ever shipped to a user is [`plugins/claude-quenching/`](plugins/claude-quenching/).** The marketplace `source` points only there. Everything else — [`evolution/`](evolution/), [`.claude/agents/`](.claude/agents/), [`docs/`](docs/) — is **maintainer tooling, versioned but never delivered**. Keep these three siblings *outside* `plugins/claude-quenching/` so they stay un-shipped.

The plugin itself is a **portable, self-contained audit + installer** for the Claude Code "knowledge surface" (CLAUDE.md, docs, skills, sub-agents, hooks, commands, memory, MCP, …) of *any* target repo. It scores a repo across **15 dimensions**, produces a prioritized gap report, and — with item-by-item confirmation — **installs its own bundled artifacts** into the target's `.claude/`/`docs/`.

> Note: the working directory is `harness-gestao` ("gestão" = management), but the project/repo is `claude-quenching` (`israelholetz/claude-quenching`). The codebase is English; some Portuguese strings are **intentional** (detection regexes, folder-variant literals) — do not "translate" them.

## Commands

There is no build/test toolchain for the plugin itself — it is Markdown + a few inert Python hook payloads. The only tooling is for the **docs site** (MkDocs Material, managed by [`uv`](https://docs.astral.sh/uv/), pinned in `pyproject.toml`/`uv.lock`):

```bash
make help            # list all scripts
make docs-serve      # uv sync + serve with live reload at http://127.0.0.1:8000
make docs-build      # strict static build into ./site (fails on broken refs)
make docs-deploy     # publish to GitHub Pages (gh-pages branch)
make docs-update     # upgrade pinned docs deps, then re-sync
```

Every target runs through `uv` (e.g. `uv run mkdocs serve`); no global Python is touched. `docs-build --strict` is the closest thing to a CI gate — run it before changing `docs/`. CI auto-deploys the site on push to `main` touching `docs/`/`mkdocs.yml`/`pyproject.toml`/`uv.lock` ([.github/workflows/docs.yml](.github/workflows/docs.yml)).

### Loading the plugin locally

```bash
claude --plugin-dir ./plugins/claude-quenching   # then /reload-plugins after edits
```

Only `quenching-management` should appear as an active skill — the payloads under `assets/` are **not** auto-discovered (that is intentional; see below).

### "Tests"

There is no unit-test runner. The method is evaluated against **eval fixtures** — small sample repos with one known planted gap each — catalogued in [evolution/research/14-eval-fixtures.md](evolution/research/14-eval-fixtures.md). The harness measures hit-rate, **false-negative rate (the metric that matters most)**, and token cost per dimension. The evolutionist runs it only when a round changes a *measured* detection rule (a grep / smell / "good" criterion); most rounds note "no measured rule changed → harness does not run."

## Architecture

### The plugin (`plugins/claude-quenching/skills/quenching-management/`)

One skill, three layers:

- **[`SKILL.md`](plugins/claude-quenching/skills/quenching-management/SKILL.md)** — the agent's roadmap: the **8-step workflow** (derive shape → inventory → score → prioritized report → install-with-OK → propose human-content items → flag deprecables → install the recurring maintenance loop). Keep it **present-tense and under ~500 lines**; push detail to `references/`.
- **[`references/`](plugins/claude-quenching/skills/quenching-management/references/)** — operational detail consulted per step. The heart is [`dimensions-template.md`](plugins/claude-quenching/skills/quenching-management/references/dimensions-template.md) (the 15 dimensions: purpose · "good" · detection · smells · remediation · payload). Others: `docs-taxonomy.md` and `scripts-taxonomy.md` (single sources for the canonical `docs/`/`scripts/` trees), `detection-and-smells.md` (the adaptive grep cookbook + 4-state scoring), `repo-profiles.md`, `report-format.md`, `installation.md`.
- **[`assets/`](plugins/claude-quenching/skills/quenching-management/assets/)** — the **installable payloads** the method stamps into a target: skill templates (`skills/`), **worker** sub-agents (`agents/` — only `quenching-auditor`/`quenching-writer`), Python hooks (`hooks/`), `docs/`/`scripts/` scaffolds, frontmatter/body `templates/`. The **maintainer agents** (`quenching-evolutionist`/`quenching-reviewer`) are **never** under `assets/` (or anywhere under `plugins/`) — they are dev-only; see "Working on the method itself" below.

### Two non-negotiable invariants

1. **Self-contained & portable.** Everything the method needs to audit *and* install lives inside the skill (in `assets/`). Nothing references an external skill or a hardcoded path from another repo. The method **derives the target's shape first**, and **the target repo's existing convention wins** — artifacts adapt their names/paths to fit. Hooks are written so an empty config makes them **inert** (e.g. empty `protectedGlobs`/`validateScript` ⇒ no-op); concrete logic is the documented *example*, never hardcoded.
2. **The `assets/` payloads are INERT installers, not active components.** They must never become auto-discoverable native skills/hooks of *this* plugin. They are inert files that get copied into a *target* repo, where they become live.

### Operation model: `audit-by-default + install-with-confirmation`

The report always comes first; installation is a separate, explicit, item-by-item step that uses the **package's** artifact (the single evolved source), flagging any pre-existing equivalent in the target as **deprecable** rather than duplicating it — and never removing it without an explicit OK. Three dimensions are **human-content decisions** the method only *proposes*, never writes: **direction/VISION (3)**, **memory (10)**, **boundary doctrine (12)**. The line the method never crosses: it installs *structure/method*, never *content/direction*.

## Working on the method itself — read this before editing

> **GOLDEN RULE: do not hand-edit `SKILL.md` / `references/` / `assets/` outside the evolution flow.** Direct edits break the log that prevents re-attacking a solved problem.

The method is a **living method**, advanced only through two maintainer agents that live **exclusively at this repo's root** [`.claude/agents/`](.claude/agents/). They are **dev-only**: never shipped, never installed into a target, and never duplicated under `plugins/` (the shipped `assets/agents/` holds only the *worker* payloads `quenching-auditor`/`quenching-writer`). Their **canonical, kept-up-to-date reference is [CONTRIBUTING.md](CONTRIBUTING.md)** — the summary below is a convenience pointer; CONTRIBUTING.md wins on any discrepancy:

- **[`quenching-evolutionist`](.claude/agents/quenching-evolutionist.md)** — *advances the frontier.* One new round (`R<N>`) per invocation, on a topic **not yet addressed**, increments `current-round`. Trigger: "evolve the method", "run an evolution round".
- **[`quenching-reviewer`](.claude/agents/quenching-reviewer.md)** — *critiques/refines what already exists.* One revision (`Rev<K>`) per invocation; revisits an existing definition (sharpen a smell, fix a stale source, merge/prune, supersede a round); does **not** increment `current-round` (tracked by `last-revision`). Trigger: "critique/refine the method", "revisit round N".

The **public docs site** ([`docs/`](docs/), the MkDocs source) describes the **plugin for its users** — what to expect when *applying* the method to a target repo. It must **not** re-document the maintainer agents or the evolution flow; that belongs in CONTRIBUTING.md, and the site only carries a thin [Contributing](docs/evolving/index.md) pointer to it.

The evolution layer (the **history**; the shipped skill describes only the **present**):

- **[`evolution/README.md`](evolution/README.md)** — the *spine/index*: the always-read cheap state. Holds `current-round`/`last-revision` anchors, the **exclusion index** (one line per already-addressed boundary — do not re-attack), the context index, the advance backlog, and the review queue.
- **[`evolution/log/`](evolution/log/)** — verbose detail, **one file per dimension/theme** (`dim-01-claude-md.md`, `dim-08-hooks.md`, `core-workflow.md`, …). `R*` and `Rev*` entries; a `Rev` nests under the round it refines and marks it `revised-by:`/`superseded-by:`.
- **[`evolution/research/`](evolution/research/)** — research input. **Every round needs ≥1 citable source (URL + date)** or it does not close.

To make a method change: invoke the relevant agent → it reads the spine, picks the next frontier / revision target, does the research, makes **one surgical change**, and records the round/revision in the right log file + updates the spine anchor. No round may reintroduce coupling to a specific repo or external skill.

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full doctrine and [evolution/log/README.md](evolution/log/README.md) for the `R*` vs `Rev*` conventions and routing table.
