---
type: tutorial
title: Getting started
description: Load the quenching study artifact, verify the bundled CLI, probe a repository read-only, and inspect the first alignment.
resource: plugins/quenching/README.md
tags:
  - tutorial
  - install
timestamp: 2026-08-28
audience: human
authority: current
source: plugins/quenching/README.md §The seven fronts, the non-converging axes, and the one align per front; command bodies under plugins/quenching/commands/
maintainer: Israel Holetz
---

# Getting started

*Audience: implementer · ~10 min at 4 steps · The first probe writes nothing; alignment waits for your OK*

By the end of this page you will have quenching loaded in a Claude Code session, the bundled
`cq` CLI answering, and a read-only report of where your repository stands — and you will have
run your first alignment knowing exactly what it was about to change, because it told you first.

!!! note "Prerequisites"
    - **Claude Code** installed and working in a terminal.
    - **Python 3.11 or newer** on the PATH — the `cq` CLI is a self-contained stdlib tool, no `pip install`.
    - A **git repository** to point the plugin at (any repo; a fresh one works fine).

## 1. Install the plugin

For a disposable study target, start Claude Code in the target repository and run the published
plugin path:

```text
/plugin marketplace add holetz/claude-quenching
/plugin install quenching@quenching
```

Run `/reload-plugins` when Claude Code was already open. For local plugin development and testing,
clone the marketplace repository and load the checkout directly instead:

```bash
git clone https://github.com/holetz/claude-quenching
cd your-repository
claude --plugin-dir ../claude-quenching/plugins/quenching
```

The `--plugin-dir` form is a development path; marketplace installation is the normal adoption
and upgrade path.

**Alternative — deploy the surface into the target.** A repository that must operate without a
harness plugin can carry the generic layer itself:

```bash
uvx --from "git+https://github.com/holetz/quenching@<tag>#subdirectory=plugins/quenching" \
  cq deploy --target . --modules core --write
```

This writes `AGENTS.md`, `.agents/skills/`, the vendored runtime under `.agents/quenching/` and
the generated `.claude/skills/` bridge. It never creates `CLAUDE.md`; Claude Code 2.1.277+ reads
`AGENTS.md` directly. Deploy does not install `/docs/` — run the target's `quenching-knowledge-align` skill next. The contract
is [deploy-mode.md](../standards/architecture/deploy-mode.md).

Claude Code appends the plugin's `bin/` to the session PATH, which is what lets every command —
and you — call `cq` bare.

### Stop or undo the installation

To remove the plugin without removing the marketplace:

```text
/plugin uninstall quenching@quenching
/reload-plugins
```

This leaves the target repository's `/docs/`, `.claude/` and `.agents/quenching.json` (or the
legacy `.claude/quenching.json`) intact.
Plugin removal is not a rollback of repository changes: review the target's Git history and
revert the commits that you want to undo. For a bad plugin upgrade, reinstall the previously
published version or use a known checkout with `--plugin-dir` only for development recovery, then
reload the session.

## 2. Verify the tool answers

Inside the session (or any shell with the plugin's `bin/` on the PATH):

```bash
cq --version
```

!!! success "You should see"
    ```text
    <the plugin version you installed>
    ```
    One line, the plugin's version. `cq` is the deterministic rail every command drives —
    uniform `--json` output, exit codes `0` ok · `1` findings · `2` refusal.

## 3. Probe before you change anything

The status commands are intended as read-only views, and their declared tool grants exclude
`Write` and `Edit`:

```text
/quenching-align:knowledge:status
/quenching-design:design:status
/quenching-specs:specs:status
/quenching-ops:ops:status
/quenching-proof:proof:status
/quenching-toolchain:toolchain:status
/quenching-delivery:delivery:status
/quenching-security:security:status
```

These reports cover the seven aligned fronts, provider-owned specs and the read-only security
pillar. Each finding is named with the command that would fix it — that is the plugin's habit
everywhere: **report with the owner, never repair silently**. This is a command-surface guarantee,
not a sandbox: an available shell or Python interpreter remains outside the status contract.

## 4. Run your first alignment

```text
/quenching-align:align
```

This conducts the seven local fronts in dependency order. What happens next depends on what the probe
finds:

- **A clean front stops there.** The probe found nothing, so there is no inventory, no plan and
  no question — a couple of tool calls, done.
- **A drifted front presents ONE plan.** You get one consolidated, read-only inventory of what
  would change, and nothing is written until you give one OK. Declining leaves the repository
  untouched.

After your OK, the alignment installs or repairs the canonical `/docs/` bundle and verifies its
own work with the front's
validator:

```bash
cq knowledge validate docs
```

!!! success "You should see"
    ```text
    0 error(s), N warning(s)
    ```
    Zero errors is the gate; warnings are named, file-level findings you can chase one by one.

## Recap

You installed the plugin from the marketplace, proved the rail answers (`cq --version`), read the available
read-only status reports, and ran one conducted alignment that asked before writing. That
probe → plan → OK → apply → verify loop is the plugin's one interface — every front repeats it.

**Next:** reproduce the bounded workflow in a disposable fixture with
[First workflow study](first-workflow-study.md), then read the full workflow in an existing repository with
[Adopt quenching in a repository](../how-to/adopt-quenching.md), or read
[the operating model](../explanation/operating-model.md#the-operating-model) to see why the local fronts feed each
other.
