# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

This repo is **two things at once**, and the distinction governs almost every decision here:

1. A **Claude Code plugin marketplace** ([`.claude-plugin/marketplace.json`](.claude-plugin/marketplace.json)) hosting a single plugin, **`claude-quenching`**.
2. The **development workspace** for that plugin — its maintainer skill and documentation-site source.

**The only thing ever shipped to a user is [`plugins/claude-quenching/`](plugins/claude-quenching/).** The marketplace `source` points only there. Everything else — [`.claude/skills/`](.claude/skills/), [`mkdocs/`](mkdocs/) — is **maintainer tooling, versioned but never delivered**. Keep these siblings *outside* `plugins/claude-quenching/` so they stay un-shipped.

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

Every target runs through `uv` (e.g. `uv run mkdocs serve`); no global Python is touched. `docs-build --strict` is the closest thing to a CI gate — run it before changing `mkdocs/`. CI auto-deploys the site on push to `main` touching `mkdocs/`/`mkdocs.yml`/`pyproject.toml`/`uv.lock` ([.github/workflows/docs.yml](.github/workflows/docs.yml)).

### Loading the plugin locally

```bash
claude --plugin-dir ./plugins/claude-quenching   # then /reload-plugins after edits
```

Only `quenching-management` should appear as an active skill — the payloads under `assets/` are **not** auto-discovered (that is intentional; see below).

### "Tests"

There is no unit-test runner. The method is evaluated against **eval fixtures** — small sample repos with one known planted gap each. The harness measures hit-rate, **false-negative rate (the metric that matters most)**, and token cost per dimension. Run it only when a change alters a *measured* detection rule (a grep / smell / "good" criterion); a change that touches no measured rule needs no harness run. See [CONTRIBUTING.md](CONTRIBUTING.md) for the eval doctrine.

## Architecture

### The plugin (`plugins/claude-quenching/skills/quenching-management/`)

One skill, three layers:

- **[`SKILL.md`](plugins/claude-quenching/skills/quenching-management/SKILL.md)** — the agent's roadmap: the **8-step workflow** (derive shape → inventory → score → prioritized report → install-with-OK → propose human-content items → flag deprecables → install the recurring maintenance loop). Keep it **present-tense and under ~500 lines**; push detail to `references/`.
- **[`references/`](plugins/claude-quenching/skills/quenching-management/references/)** — operational detail consulted per step. The heart is [`dimensions-template.md`](plugins/claude-quenching/skills/quenching-management/references/dimensions-template.md) (the 15 dimensions: purpose · "good" · detection · smells · remediation · payload). Others: `docs-taxonomy.md` and `scripts-taxonomy.md` (single sources for the canonical `docs/`/`scripts/` trees), `detection-and-smells.md` (the adaptive grep cookbook + 4-state scoring), `repo-profiles.md`, `report-format.md`, `installation.md`.
- **[`assets/`](plugins/claude-quenching/skills/quenching-management/assets/)** — the **installable payloads** the method stamps into a target: skill templates (`skills/`), **worker** sub-agents (`agents/` — `quenching-auditor`/`quenching-writer`/`quenching-direction`), Python hooks (`hooks/`), `docs/`/`scripts/` scaffolds, frontmatter/body `templates/`. The **maintainer skill** (`quenching-maintainer`) lives at `.claude/skills/` and is **never** under `assets/` (or anywhere under `plugins/`) — it is dev-only; see "Working on the method itself" below.

### Two non-negotiable invariants

1. **Self-contained & portable.** Everything the method needs to audit *and* install lives inside the skill (in `assets/`). Nothing references an external skill or a hardcoded path from another repo. The method **derives the target's shape first**, and **the target repo's existing convention wins** — artifacts adapt their names/paths to fit. Hooks are written so an empty config makes them **inert** (e.g. empty `protectedGlobs`/`validateScript` ⇒ no-op); concrete logic is the documented *example*, never hardcoded.
2. **The `assets/` payloads are INERT installers, not active components.** They must never become auto-discoverable native skills/hooks of *this* plugin. They are inert files that get copied into a *target* repo, where they become live.

### Operation model: `audit-by-default + install-with-confirmation`

The report always comes first; installation is a separate, explicit, item-by-item step that uses the **package's** artifact (the single evolved source), flagging any pre-existing equivalent in the target as **deprecable** rather than duplicating it — and never removing it without an explicit OK. Beyond structure, the method **generates knowledge** in three regimes by dimension type (single source: `references/module-contract.md` part 3): for **derived-content** dims (standards/2, conventions/13) it **mines the code and writes the standard itself** — every `current` rule anchored at `file:line`, unproven → `authority: background`; for **human-direction** dims — **vision (3)**, **memory (10)**, **boundary doctrine (12)** — it **drafts** the content from observable signals and writes it **labeled `authority: background` + a "pending human ratification" banner**, promoted only by a human gate; **structural** dims (map/1, catalog/11) are install/migrate/regenerate only. The line the method never crosses is **not** "never content" — it is **never assert DIRECTION as ratified truth**: derived description it writes; direction it only drafts for the human to ratify.

## Working on the method itself — read this before editing

The method is a **living method**, maintained through **one dev-only skill** that lives **exclusively at this repo's root** [`.claude/skills/quenching-maintainer/`](.claude/skills/quenching-maintainer/). It is never shipped, never installed into a target, and never duplicated under `plugins/` (the shipped `assets/agents/` holds only the *worker* payloads `quenching-auditor`/`quenching-writer`/`quenching-direction`). It runs **inline**, so the maintainer reviews the surgical change directly.

- **[`quenching-maintainer`](.claude/skills/quenching-maintainer/SKILL.md)** accepts **mixed directions in one invocation** and makes the change directly in `SKILL.md` / `references/` / `assets/`: revise a section (sharpen a smell, prune bloat, fix a stale source, merge duplicates), evolve a concept (grounded in current Claude/Claude Code practice), change the main `SKILL.md` workflow, or analyze a repository/session (audit the method's own source for drift, or mine a real application session under `~/.claude/projects/` for field evidence and apply the fixes). Triggers: "evolve/refine/critique the method", "revise section X", "change the main skill", "run a retrospective on session Y", "harvest field feedback".

**There is no evolution log.** History lives in **git** — the commit message records anything about a change worth remembering beyond its diff. Do **not** reintroduce `R*`/`Rev*` round/revision numbering, a spine/index, an exclusion index, a review queue, or an advance backlog: that apparatus was removed on purpose. The active spec (`SKILL.md`/`references/`/`assets/`) is **present-tense only**. **Canonical reference: [CONTRIBUTING.md](CONTRIBUTING.md)** — it wins on any discrepancy.

The **public docs site** ([`mkdocs/`](mkdocs/), the MkDocs source) describes the **plugin for its users** — what to expect when *applying* the method to a target repo. It must **not** re-document the maintainer skill; that belongs in CONTRIBUTING.md, and the site only carries a thin pointer to [CONTRIBUTING.md](CONTRIBUTING.md).

To make a method change: invoke `quenching-maintainer` with the direction(s) → it locates the relevant surface, reads only what's relevant, makes the surgical change(s), self-checks the invariants, and reports. No change may reintroduce coupling to a specific repo or external skill. See [CONTRIBUTING.md](CONTRIBUTING.md) for the full doctrine.
