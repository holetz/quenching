---
type: standard
title: Deploy mode — install the surface in a target repository
description: "`cq deploy` materializes the selected quenching modules in a target's generic layer — AGENTS.md, .agents/skills and a vendored runtime — while Claude Code receives only a generated bridge under .claude; install is not alignment and never calls a model."
resource: quenching/assets/bin/quenching/deploy/**, quenching/assets/bin/cq, quenching/assets/modules.json, quenching/pyproject.toml, quenching/assets/bin/quenching/components/commands/bridge.py, quenching/assets/bin/quenching/components/commands/migrate.py, integrations/opencode-vitrine/**
tags: [architecture, deploy, installation, agents, skills, bridge]
timestamp: 2026-11-03
audience: both
authority: current
source: deploy-mode implementation (2026-10-28); surface facts re-measured on Claude Code 2.1.312; drift redefined as content plus the executable bit (spec 2126, 2026-10-30); spec 2160 (install only by deploy); spec 2168 (the launcher is generated); spec 2174 (absorbs surface-translation.md, whose lineage is spec 2115, spec 2118, spec 2160 and spec 2170); retired with surface-translation.md (spec 2174, 2026-11-03)
maintainer: quenching
---

# Deploy mode — install the surface in a target repository

<!-- rules -->

## Two modes, one source

Deploy is the only mode: since [ADR 0017](../../decisions/0017-install-only-by-deploy.md) no
plugin carries the command surface, and `cq deploy` materializes the selected surface from
`quenching` in a target repository. It never edits a target's knowledge or code by itself.

`cq deploy` is a **top-level command**, not a front. `delivery` and `ops` keep their own meaning
for deployment; this verb installs the tool surface. It never invokes a model, never aligns
`/docs/`, never chooses a provider and never runs a target pipeline.

## The target layout

| Path | Kind | Owner |
| --- | --- | --- |
| `AGENTS.md` | instructions | target; seeded only when absent |
| `.agents/quenching.json` | configuration | target; seeded only when absent |
| `.agents/skills/quenching-<command>/SKILL.md` | one-segment skills | generated |
| `.agents/quenching/` | vendored payload: runtime, references, templates, commands, agent protocols | generated, read-only |
| `.agents/.quenching-deploy.json` | manifest: version, modules, profiles, hashes, skills | generated |
| `.claude/skills/<name>/` | Claude bridge, byte copy of every skill | generated |
| `.claude/agents/quenching-<name>.md` | Claude subagents | generated when the `claude` harness is selected |
| `.opencode/agents/quenching-<name>.md` | OpenCode subagents, `mode: subagent` | generated when the `opencode` harness is selected |
| `.mcp.json` | Claude Code project MCP registration | generated when `shared.mcp` is declared and the `claude` harness is selected |
| `.codex/config.toml` | Codex MCP registration | generated when `shared.mcp` is declared and the `codex` harness is selected |
| `opencode.json` | OpenCode MCP registration | generated when `shared.mcp` is declared and the `opencode` harness is selected |
| `CLAUDE.md` | legacy pointer to `AGENTS.md` | never created; removed only by `--prune-legacy` |
| `.claude/commands/`, `.claude/references/` | legacy layout | refused; run `cq components migrate` first |

`AGENTS.md` is read natively by Claude Code 2.1.277+ when no `CLAUDE.md`/`CLAUDE.local.md` exists
in the working directory or above it (§Surface translation below). Claude
does **not** read `.agents/skills/`; the generated `.claude/skills/` bridge is the only reason it
is present. A repository therefore never authors `.claude` for quenching.

## Selection and the manifest

`--modules` selects principal modules, not fronts. `core` means `specs,git,knowledge,components`
(the modules `quenching-specs`, `quenching-git`, `quenching-knowledge` and `quenching-components`; the
alias `align` is `knowledge,components`); `specs` is always included because it
owns the one `cq`. `--profiles` overrides the `shared.profiles.installed` seed; otherwise the
fronts of the selected modules are derived. `specs` is kept in that list as the provider axis.

A target that already carries a manifest reuses its recorded `modules`, `harnesses`, `runtime` and
`profiles` for every flag the caller omits, so `cq deploy --write` upgrades what is installed
instead of reinstall `core`. An explicit flag always wins; the manifest is a default, not an
authority over the plan.

The manifest is the authority for what deploy owns. A generated file must be listed before it may
be overwritten; a file at a generated path that the manifest does not own is a conflict
(`ct-deploy-unowned`, exit 2) and nothing is written. Generated files may be edited by hand only
as drift: `--check` reports it and `--write` regenerates them. Drift is content and the executable
bit — the only part of the mode git carries — so a checkout that creates files group-writable
(`umask 0002`) is clean. A target's own skills, references, `AGENTS.md` and configuration are never
in the manifest's write set.

## Runtime

`--runtime vendor` copies the selected Python packages and the entry point into
`.agents/quenching/assets/bin/` and **generates** the launcher `.agents/quenching/bin/cq` (with its
`bin/cq.cmd` for Windows), a shim that re-executes `../assets/bin/cq`; it is offline and
self-contained. The source ships no `bin/` of its own. `--runtime uvx` omits the
packages and writes `.agents/quenching/bin/cq` as a shim pinned to the release tag, so the target
needs network and `uvx` at call time.

Every deployed command body uses the target-local path `.agents/quenching/bin/cq`; the generated
grant is `Bash(.agents/quenching/bin/cq:*)`.

## MCP registration

A target that wants the quenching MCP server registered declares `shared.mcp` in
`.agents/quenching.json` (`{mount: "specs", command: [...]}`, see
[plugin-configuration.md](../workflows/plugin-configuration.md#the-sharedmcp-block)). Deploy then
writes one whole file per selected harness — `.mcp.json` for `claude`, `.codex/config.toml` for
`codex`, `opencode.json` for `opencode` — with the same argv:
`<command...> .agents/quenching/assets/bin/cq <mount> mcp`.

One whole file per harness, no merge: each file belongs to the target and to the manifest, so a
hand edit is drift, not a second owner, and a file present at that path without a manifest entry is
refused (`ct-deploy-unowned`). Turning the key off removes the files through the normal `delete`
flow, and selecting fewer harnesses writes fewer files. The option requires `--runtime vendor`,
because a `uvx` runtime omits the vendored entry point the generated command calls.
Approving a generated `.mcp.json` server (`enabledMcpjsonServers`) stays a human step in the
harness; deploy never writes it.

## The `.claude/settings.json` merge

With `claude` among the harnesses, deploy installs the hooks of the selected modules into the
target's `.claude/settings.json`, and unlike `.mcp.json` the file stays the user's: it is merged,
never owned, so it is not in the manifest's `files`.

- **Own entries only.** An entry is quenching's when its `command` points under
  `.agents/quenching/assets/hooks/`; that path is the marker, valid even without a manifest.
  Everything else in the file (keys, groups, hooks, order) is left as written. A wanted entry that
  already exists is updated in place; a missing one is appended in a new `{matcher, hooks}` group.
- **`attribution`.** Deploy writes `commit: ""` and `pr: ""` only for keys that are absent. A value
  the user set stays and becomes a warning, not drift. Removal deletes only the keys that are still
  `""` and that the manifest records (`claudeSettings.attribution`) as written by deploy.
- **`--check`.** The merge result differing from the file is `settings` drift (exit 1).
- **Removal.** Selecting fewer modules drops the hooks of the module that left; a harness list
  without `claude` (`codex`, `opencode`, `none`) wants nothing, so only deploy's own entries leave.
  A file reduced to `{}` by that removal is deleted.
- **Refusal.** Invalid JSON, a root that is not an object, or `hooks` / `hooks.<event>` of the
  wrong type is `ct-deploy-settings` (exit 2) and nothing is written. A successful merge rewrites
  the file once with two-space indentation; later runs are idempotent.

## What deploy does not do

- It does not install `/docs/` or call an align; the target runs its own
  `quenching-knowledge` skill (flow `align`) after the surface exists. `AGENTS.md` names that next step when the bundle is absent.
- It does not touch `.claude/settings.local.json` or the user's `~/.claude`, and edits
  `.claude/settings.json` only through the merge above.
- It does not choose the specs backend, license, release provider or any product policy.
- It does not merge a content-bearing `CLAUDE.md`; the target's
  `quenching-components` skill (flow `harness-align`) owns that, and a pointer-only file is removed only on
  `--prune-legacy`.

## Surface translation

The source, `quenching/`, is written in the target dialect: `/quenching-<vertical> <flow>` ids and
`.agents/quenching` citations, with no `${CLAUDE_PLUGIN_ROOT}` and no `:` in an id
([source-layout.md](source-layout.md)). **`cq deploy`** rewrites only the frontmatter, the generated
header, the grants (and the OpenCode permissions) and the `cq.cmd` launcher; a source that still
carries a plugin-root marker or a plugin-surface id is refused. It writes a target repository's
generic layer — `.agents/skills/` (read by Codex and OpenCode), the payload under
`.agents/quenching/`, the Claude bridge under `.claude/skills/` and the subagents under
`.claude/agents/` and `.opencode/agents/` (§The target layout above). No Codex package and no
user-level OpenCode distribution exist since [ADR 0017](../../decisions/0017-install-only-by-deploy.md).
A target's `.claude/commands/` is the legacy layout, which `cq components migrate` converts; the
`cq components translate` that once copied it into `.agents/` is retired, and a copy it wrote beside
its `.claude/` source is, to `migrate`, a second editable copy and a conflict for the human to settle.

`integrations/opencode-vitrine/` is outside every translation: a hand-written OpenCode Desktop GUI
plugin that carries no skill body and no generated byte ([source-layout.md](source-layout.md)).

The standard that held this translation, surface-translation.md, retired with this section (spec 2174,
2026-11-03): the deploy does the translating, so the rules live beside it.

### Target repositories and the generic layer

A target repository's single editable source is the generic layer. Each artifact has one home:

| Artifact | Home | Why there |
| --- | --- | --- |
| skill | `.agents/skills/<name>/SKILL.md`, sibling files in the same folder | read by Codex and OpenCode; the name is one segment ([command-surface.md](../naming/command-surface.md)) |
| reference | `.agents/references/**` | cited by the skills beside them |
| eval | `.agents/evals/<name>/` | beside the skill it scores |
| instructions | `AGENTS.md` at the root; subfolder `AGENTS.md` loads with that folder | read natively by Claude Code 2.1.277+, Codex and OpenCode |
| configuration | `.agents/quenching.json`, `.claude/quenching.json` read as legacy ([plugin-configuration.md](../workflows/plugin-configuration.md)) | one editable file |

There is no root `CLAUDE.md` in a conformant target: Claude Code reads `AGENTS.md` itself when
no `CLAUDE.md`/`CLAUDE.local.md` exists in the working directory or above it. The Claude interface
carries only what the facts below require: `.claude/skills/<name>/` as a **generated copy** of
`.agents/skills/<name>/`; and `.claude/agents/`, `.claude/hooks/`, `.claude/settings*.json`, which
have no generic home Claude Code reads. `.claude/commands/`, `.claude/references/` and
`.claude/CLAUDE.md` do not exist in a conformant target. A pointer-only `CLAUDE.md` (`@AGENTS.md`)
is legacy, kept only for hosts before Claude Code 2.1.277, and `cq components migrate` removes it.

#### Verified facts

Probed on Claude Code 2.1.312 and OpenCode 1.18.35 (2026-10-28), with real `claude -p` sessions in
throwaway repositories against a positive control, and by reading the installed binaries:

| Question | Answer |
| --- | --- |
| Does Claude Code discover a skill only under `.agents/skills/<n>/SKILL.md`? | **No.** `.agents/skills` appears only in its Cursor importer, which copies into `.claude/skills/` |
| Does it discover a nested `.claude/skills/<a>/<b>/SKILL.md`? | **No**; only the flat sibling skill is listed |
| Does it load `AGENTS.md` alone as project instructions? | **Yes**, by default since 2.1.277 (`claude-md-or-agents-md`): with no `CLAUDE.md`/`CLAUDE.local.md` in the working directory or above it, every `AGENTS.md` and `.claude/AGENTS.md` in that path loads. With both files, only `CLAUDE.md` loads unless the setting is `claude-md-and-agents-md`. Nothing under `.agents/` is read as instructions. |
| Does it read a subagent under `.agents/agents/`? | **No** |
| Does OpenCode read `.claude/skills` and `.agents/skills`? | **Yes, both**, in that order; a repeated name logs `duplicate skill name` and the `.agents` copy wins, so the listing does not duplicate |

A newer host version may change any row; the bridge manifest records the version it was verified
against (`verifiedClaudeCode`), and a row is re-probed before the layout is relaxed.

#### The bridge

`cq components bridge --target <repo> [--write|--check] --json` copies every `.agents/skills/<name>/`
folder to `.claude/skills/<name>/` byte for byte, inserting one marker line right after the
`SKILL.md` frontmatter — `<!-- generated from .agents/skills/<name>/SKILL.md by cq components bridge;
edit the source -->`. The manifest `.claude/skills/.generated-files.json` records one sha256 per
generated file and `verifiedClaudeCode`; freshness is a byte comparison, with no aggregate digest.
`--check` exits 1 on drift (an edited copy, a new source, an orphan). A `.claude/skills/<name>/` the
manifest does not list is the human's: the bridge refuses (exit 2, `ct-bridge-unowned`) rather than
overwrite it. No symbolic link is used ([windows-support.md](../platform/windows-support.md)).

#### Migration and conformance

`cq components migrate --target <repo> [--write] --json` plans the move from the legacy layout and
applies it with `git mv`/`git rm`, preserving history: `.claude/commands/<a>/<b>.md` becomes
`.agents/skills/<a>-<b>/SKILL.md` (replacing a generated Codex translation of the same command),
`.claude/references/**` becomes `.agents/references/**`, a hand-written `.claude/skills/<n>/` moves
to `.agents/skills/<n>/`, the old translation manifests are removed, `.claude/quenching.json` moves to
`.agents/quenching.json`, and `CLAUDE.md` content moves to `AGENTS.md`. A pointer-only `CLAUDE.md`
(`@AGENTS.md`) is removed, never recreated: Claude Code 2.1.277+ reads `AGENTS.md` directly. Moved bodies have `/a:b`
invocations rewritten to `/a-b` and `.claude/references/` citations to `.agents/references/`. A
conflict (two divergent configurations, two harness files with their own content) is reported in
the plan (exit 1), and `--write` refuses it (exit 2, `ct-migrate-conflict`) and writes nothing. A target is **conformant** when `migrate` reports an empty plan
(`conformant: true`) and `bridge --check` exits 0.

### Codex runtime policy

Deployed skills carry no model pin: `cq deploy` drops `model` and `effort` from their
frontmatter. The project's role mapping for a Codex run is `opus` → `gpt-6-astra`, `sonnet` → `gpt-6.1-sol`, and
`haiku` → `gpt-6-luna`; these are project routing choices, not measured model equivalence.
Luna writes product code only on ONE task whose
`cq specs estimate --task` reports `oracleProtected` and `smallTierEligible` — an executable
`verify:` whose tests sit outside the task's `files:`, nothing under `/docs/`, projected context
at or under 80k — the same conditions as `haiku` (ADR 0014); a failed `verify:` returns the task
to the session model. Judgment roles and import-memory classifiers/executors never use Luna.
Source Claude model pins remain intact.

A Codex run delegates exclusively through the Codex host's subagent tools, with explicit
models and role protocols. It must never launch Claude CLI or fall back to Claude models.
Claude workflows may still delegate development to Codex, and may also ask Codex for an
independent review of their own work. That review runs only as `codex exec` under the bypass with
`--ignore-user-config` and no native sandbox, a git guard proving the tree unchanged, and runs in parallel with the Claude review, by default when quota is
available. When Codex is unavailable or out of quota the workflow reports the fallback and keeps
the Claude review rather than skipping the step in silence. A Codex run never launches Codex or
Claude CLI, so the review step belongs to the Claude surface; this grants no new `allowed-tools`
or `tools:`. Host capabilities determine
spawn, messaging, interruption and completion mechanics; unavailable independent delegation
is reported rather than replaced by self-review. Token usage is reported per model and role
only when the Codex host exposes it, otherwise `not measured`; Claude transcript telemetry
cannot measure a Codex run. The shared configuration file (`.agents/quenching.json`, or the legacy `.claude/quenching.json`) remains the configuration home.

Import-memory may read existing Claude-format memory files as data, with the original source path
explicit; it invents no Codex memory layout.

### OpenCode agents

With the `opencode` harness selected, `cq deploy` writes each source agent to
`.opencode/agents/quenching-<agent>.md` as `mode: subagent`. No model is pinned: the source tier
and effort survive as prose. Permissions are mapped deny-only from the source `tools:` — no edit
tool → `edit: deny`, no `WebFetch` → `webfetch: deny`, no `Agent`/`Task` → the task tool off,
unrestricted `Bash` → `bash: allow`, no `Bash` → `bash: deny` — with one decided exception: scoped
`Bash(cq <verbs>:*)` grants give a `bash` map that opens with `"*": ask`, then one
`"cq <verbs> *": allow` pattern per grant, in source order. OpenCode applies the last rule that
matches, so a catch-all written last would override every allow: the order is the policy, and a
scoped `Bash(...)` with no `cq` → `bash: ask`. Only the verbs the source grants are allowed, so a
read-only agent never runs `cq git push` or `cq specs record` unasked. Per-agent permission sets
beyond this mapping and hooks are not generated; they widen or reshape grants and stay a human
decision.

## Verify

```bash
cq deploy --target . --modules core --check --json   # 0 clean, 1 drift, 2 refusal
python3 .agents/quenching/bin/cq --version
python3 .agents/quenching/bin/cq components status --json
python3 .agents/quenching/bin/cq components bridge --target . --check --json
```

The target's `components` surface excludes the skills listed in the deploy manifest and reports
them as `generated`; only the target's own skills are audited.
