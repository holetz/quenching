---
type: tutorial
title: Getting started
description: Deploy quenching into a repository, verify the bundled CLI, probe a repository read-only, and inspect the first alignment.
resource: quenching/README.md
tags:
  - tutorial
  - install
timestamp: 2026-11-03
audience: human
authority: current
source: quenching/README.md §The seven fronts, the non-converging axes, and the one align per front; command bodies under quenching/skills/; spec 2160
maintainer: Israel Holetz
---

# Getting started

*Audience: implementer · ~10 min at 4 steps · The first probe writes nothing; alignment waits for your OK*

By the end of this page you will have quenching deployed into a repository, the bundled
`cq` CLI answering, and a read-only report of where your repository stands — and you will have
run your first alignment knowing exactly what it was about to change, because it told you first.

!!! note "Prerequisites"
    - **Claude Code** installed and working in a terminal.
    - **Python 3.11 or newer** on the PATH — the `cq` CLI is a self-contained stdlib tool, no `pip install`.
    - A **git repository** to deploy into (any repo; a fresh one works fine).

## 1. Deploy quenching into the target

quenching is installed into the repository itself with `cq deploy`; there is no plugin to install.
From a clone of the source repository:

```bash
git clone https://github.com/holetz/quenching
python3 quenching/quenching/assets/bin/cq deploy --target your-repository --write
```

Or, without a clone, from a release tag through `uvx`:

```bash
cd your-repository
uvx --from "git+https://github.com/holetz/quenching@<tag>#subdirectory=quenching" \
  cq deploy --target . --modules core --write
```

`<tag>` is a release tag such as `7.0.0` (list them with
`git ls-remote --tags https://github.com/holetz/quenching`); a literal `<tag>` fails with
`Git operation failed`. To upgrade an installed target, drop `--modules`: the recorded manifest
keeps its modules, while `--modules core` narrows a wider install and deletes the rest.

This writes `AGENTS.md` (only when absent), `.agents/skills/`, the vendored runtime under
`.agents/quenching/` and the generated `.claude/skills/` bridge, for Claude Code, Codex and OpenCode
by default (`--harness` narrows it). It never creates `CLAUDE.md`; Claude Code 2.1.277+ reads
`AGENTS.md` directly. Deploy does not install `/docs/` — that is step 4. The contract is
[deploy-mode.md](../standards/architecture/deploy-mode.md). Start Claude Code in the target once
the files exist; every command is `/quenching-<front>-<verb>`.

### Stop or undo the installation

The deploy manifest `.agents/.quenching-deploy.json` lists every file deploy owns: delete those
and the manifest, or revert the commit that added them. That leaves the target's `/docs/` and
`.agents/quenching.json` intact. Removing the surface is not a rollback of repository changes:
review the target's Git history and revert the commits that you want to undo. For a bad upgrade,
deploy the previous release tag again.

## 2. Verify the tool answers

From the target repository:

```bash
python3 .agents/quenching/bin/cq --version
```

!!! success "You should see"
    ```text
    <the version you deployed>
    ```
    One line, the deployed version. `cq` is the deterministic rail every command drives —
    uniform `--json` output, exit codes `0` ok · `1` findings · `2` refusal.

## 3. Probe before you change anything

The status commands are intended as read-only views, and their declared tool grants exclude
`Write` and `Edit`:

```text
/quenching-knowledge status
/quenching-design status
/quenching-specs status
/quenching-ops status
/quenching-proof status
/quenching-toolchain status
/quenching-delivery status
/quenching-security status
```

These reports cover the seven aligned fronts, provider-owned specs and the read-only security
pillar. Each finding is named with the command that would fix it — that is the plugin's habit
everywhere: **report with the owner, never repair silently**. This is a command-surface guarantee,
not a sandbox: an available shell or Python interpreter remains outside the status contract.

## 4. Run your first alignment

```text
/quenching-align
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
python3 .agents/quenching/bin/cq knowledge validate docs
```

!!! success "You should see"
    ```text
    0 error(s), N warning(s)
    ```
    Zero errors is the gate; warnings are named, file-level findings you can chase one by one.

## Recap

You deployed the surface into the target, proved the rail answers (`cq --version`), read the available
read-only status reports, and ran one conducted alignment that asked before writing. That
probe → plan → OK → apply → verify loop is the plugin's one interface — every front repeats it.

**Next:** reproduce the bounded workflow in a disposable fixture with
[First workflow study](first-workflow-study.md), then read the full workflow in an existing repository with
[Adopt quenching in a repository](../how-to/adopt-quenching.md), or read
[the operating model](../explanation/operating-model.md#the-operating-model) to see why the local fronts feed each
other.
