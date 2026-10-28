---
type: standard
title: Surface translation — Claude, Codex, OpenCode and Omnigent
description: A target repository keeps its surface in .agents/ and AGENTS.md with a generated Claude bridge; the packaged plugin keeps Claude as source and translates it deterministically to Codex, OpenCode and Omnigent
resource: plugins/quenching/assets/bin/quenching/components/commands/translate.py, plugins/quenching/assets/bin/quenching/components/commands/bridge.py, plugins/quenching/assets/bin/quenching/components/commands/migrate.py, plugins/quenching/assets/translation/codex-adaptation.json, .agents/plugins/marketplace.json, scripts/sync_opencode_plugin.py, plugins/opencode/**, scripts/sync_omnigent_plugin.py, plugins/omnigent/**, docs/project/model-compat.md, plugins/quenching/assets/translation/omnigent-model-compat.json
tags: [architecture, claude-code, codex, opencode, omnigent, translation, surfaces]
timestamp: 2026-10-28
audience: both
authority: current
source: alinhar-plugin-a-agents-md spec, tasks 2.1–2.4 (2026-08-18); spec 2115 (layout per harness, Omnigent operator agent, 2026-10-28); spec 2118 (target surface in .agents/ with a generated Claude bridge, 2026-10-28)
maintainer: quenching
---

# Surface translation — Claude, Codex, OpenCode and Omnigent

<!-- rules -->

Two directions exist, and they never mix. **The packaged plugin** keeps Claude as its source:
this marketplace repository publishes and checks its generated Codex plugin under
`plugins/codex/quenching-codex/`, registered in `.agents/plugins/marketplace.json`, regenerated with
`python3 scripts/sync_codex_plugin.py --write`. **A target repository** keeps its surface in the
generic layer — `.agents/` and `AGENTS.md` — and gets only a generated Claude bridge
(§Target repositories). Translating a target's `.claude/` into `.agents/` is the legacy layout, which
`cq components migrate` converts.

The package's platform, identity, manifest and catalog are declared in `assets/modules.json` under
`distributions`. Publication and the isolated marketplace upgrade check are governed by
[versioning-release.md](../ci-cd/versioning-release.md); translation drift alone does not prove
that an installed consumer can discover or upgrade the package.

## Target repositories

A target repository's single editable source is the generic layer. Each artifact has one home:

| Artifact | Home | Why there |
| --- | --- | --- |
| skill | `.agents/skills/<name>/SKILL.md`, sibling files in the same folder | read by Codex and OpenCode; the name is one segment ([command-surface.md](../naming/command-surface.md)) |
| reference | `.agents/references/**` | cited by the skills beside them |
| eval | `.agents/evals/<name>/` | beside the skill it scores |
| instructions | `AGENTS.md` at the root | read by Codex and OpenCode |
| configuration | `.agents/quenching.json`, `.claude/quenching.json` read as legacy ([plugin-configuration.md](../workflows/plugin-configuration.md)) | one editable file |

The Claude interface carries only what the facts below require: `CLAUDE.md` holding exactly
`@AGENTS.md`; `.claude/skills/<name>/` as a **generated copy** of `.agents/skills/<name>/`; and
`.claude/agents/`, `.claude/hooks/`, `.claude/settings*.json`, which have no generic home Claude Code
reads. `.claude/commands/` and `.claude/references/` do not exist in a conformant target.

### Verified facts

Probed on Claude Code 2.1.312 and OpenCode 1.18.35 (2026-10-28), with real `claude -p` sessions in
throwaway repositories against a positive control, and by reading the installed binaries:

| Question | Answer |
| --- | --- |
| Does Claude Code discover a skill only under `.agents/skills/<n>/SKILL.md`? | **No.** `.agents/skills` appears only in its Cursor importer, which copies into `.claude/skills/` |
| Does it discover a nested `.claude/skills/<a>/<b>/SKILL.md`? | **No**; only the flat sibling skill is listed |
| Does it load `AGENTS.md` alone as project instructions? | **No** (default configuration); with both files only `CLAUDE.md` loads |
| Does it read a subagent under `.agents/agents/`? | **No** |
| Does OpenCode read `.claude/skills` and `.agents/skills`? | **Yes, both**, in that order; a repeated name logs `duplicate skill name` and the `.agents` copy wins, so the listing does not duplicate |

A newer host version may change any row; the bridge manifest records the version it was verified
against (`verifiedClaudeCode`), and a row is re-probed before the layout is relaxed.

### The bridge

`cq components bridge --target <repo> [--write|--check] --json` copies every `.agents/skills/<name>/`
folder to `.claude/skills/<name>/` byte for byte, inserting one marker line right after the
`SKILL.md` frontmatter — `<!-- generated from .agents/skills/<name>/SKILL.md by cq components bridge;
edit the source -->`. The manifest `.claude/skills/.generated-files.json` records one sha256 per
generated file and `verifiedClaudeCode`; freshness is a byte comparison, with no aggregate digest.
`--check` exits 1 on drift (an edited copy, a new source, an orphan). A `.claude/skills/<name>/` the
manifest does not list is the human's: the bridge refuses (exit 2, `ct-bridge-unowned`) rather than
overwrite it. No symbolic link is used ([windows-support.md](../platform/windows-support.md)).

### Migration and conformance

`cq components migrate --target <repo> [--write] --json` plans the move from the legacy layout and
applies it with `git mv`/`git rm`, preserving history: `.claude/commands/<a>/<b>.md` becomes
`.agents/skills/<a>-<b>/SKILL.md` (replacing a generated Codex translation of the same command),
`.claude/references/**` becomes `.agents/references/**`, a hand-written `.claude/skills/<n>/` moves
to `.agents/skills/<n>/`, the old translation manifests are removed, `.claude/quenching.json` moves to
`.agents/quenching.json`, and `CLAUDE.md` content moves to `AGENTS.md`. Moved bodies have `/a:b`
invocations rewritten to `/a-b` and `.claude/references/` citations to `.agents/references/`. A
conflict (two divergent configurations, two harness files with their own content) is reported in
the plan (exit 1), and `--write` refuses it (exit 2, `ct-migrate-conflict`) and writes nothing. A target is **conformant** when `migrate` reports an empty plan
(`conformant: true`) and `bridge --check` exits 0.

`cq components translate` never runs on a target that has the generic surface or the bridge
manifest: it refuses with exit 2, because it would write the legacy translation over the source.

## What translates

This section and the next describe the packaged plugin's direction, and a legacy target that has
not migrated yet. `cq components translate --source <repo> --target <repo>` maps each
`.claude/commands/<path>.md` to `.agents/skills/<path>/SKILL.md`, preserving the command body
while adapting platform vocabulary and retaining only frontmatter Codex can use. It also copies
and adapts `.claude/references/**` to `.agents/references/**`, so translated skills retain valid
local citations, and maps the root `CLAUDE.md` harness to `.agents/AGENTS.md` when it exists.

The translator owns only those generated artifacts. Existing Codex configuration, including
`.agents/plugins/marketplace.json`, stays in place and is excluded from translation-drift checks.

The generated `.agents/.generated-from.json` and `.generated-files.json` record the generated set
and one sha256 per generated file. They deliberately carry no aggregate source digest: it changed
on every unrelated edit and made every parallel PR conflict on one line. Freshness is a byte
comparison, not a stamp. A check compares the deterministic result to that set without changing either
surface.

## What never translates

The configuration is never copied: one editable file exists, so coexistence cannot create two
independently editable configurations.

The translator's adaptation map and implementation ship inside the Claude plugin under `assets/`.
An installed plugin can therefore perform the same translation in a target repository; the
marketplace repository's root `scripts/` directory is not a runtime dependency.

## Direction and authority

This initial implementation proves the Claude-to-Codex generation path and the coexistence rule,
but not yet the reverse reconciliation path. Accordingly this standard is `background` until the
hash-based reverse direction and its tests are delivered. A future proven rule may graduate it to
`current`; it must retain Claude as the authority for configuration and for source forms that
cannot round-trip without loss.

## Codex runtime policy

Runtime adaptation is generated from `assets/translation/codex-adaptation.json` and
`components/commands/translate.py`, never edited in generated skills or an installed cache.
The project's role mapping is `opus` → `gpt-6-astra`, `sonnet` → `gpt-6.1-sol`, and
`haiku` → `gpt-6-luna`; these are project routing choices, not measured model equivalence.
Declared efforts survive. Luna writes product code only on ONE task whose
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
Claude CLI, so the review step belongs to the Claude surface and is absent from the generated
Codex surface; this grants no new `allowed-tools` or `tools:`. Host capabilities determine
spawn, messaging, interruption and completion mechanics; unavailable independent delegation
is reported rather than replaced by self-review. Token usage is reported per model and role
only when the Codex host exposes it, otherwise `not measured`; Claude transcript telemetry
cannot measure a Codex run. The shared configuration file (`.agents/quenching.json`, or the legacy `.claude/quenching.json`) remains the configuration home.

Model adaptation applies to executable Markdown prose and agent frontmatter, while fenced
fixtures and copied Python implementation remain data. Existing general platform/path
translation is separate from the runtime model pass.

The generated surface-load adapter exits 2 (inconclusive) until a Codex capture harness exists;
it never runs the Claude harness. Generated `cq components session cost` likewise refuses
with `se-codex-telemetry-unavailable`. Import-memory may read existing Claude-format memory
files as data, with the original source path explicit; translation invents no Codex memory layout.
Generated runtime prefixes are excluded from reverse body reconciliation and cannot be edited
from the generated side to change source policy.

## OpenCode distribution

`plugins/opencode/quenching-opencode/` is generated by `python3 scripts/sync_opencode_plugin.py --write`
and checked by `--check` in the repository gate; the release regeneration runs it after the
Codex step. It is laid out as an OpenCode configuration directory: `commands/quenching-<front>-<verb>.md`
for each source command, `agents/quenching-<agent>.md` for each source agent registered as an
OpenCode subagent, and `quenching/` carrying the cited references, templates, specs, knowledge,
design, portal, checks (Python only), zensical, evals, opensource, agent protocols and the bundled `cq`. It has no marketplace entry and no
`distributions` row: installing it is copying `commands/` and `agents/` into `~/.opencode/` and
`quenching/` into `~/.opencode/quenching/`. `~/.opencode/` survives a per-session
`XDG_CONFIG_HOME`, which hides `~/.config/opencode/`. The distribution keeps its payload because
bash works outside Omnigent; a machine that serves the Omnigent operator agent does not install it,
since the agent already carries the same commands as skills.

Markdown is translated from the Claude source with the OpenCode vocabulary: module-qualified ids
become `quenching-<front>-<verb>`, agent ids become `quenching-<agent>`, plugin paths become the
installed payload root `~/.opencode/quenching/`, and every bash block that calls `cq`
defines a per-call wrapper honouring `QUENCHING_OPENCODE_ROOT`. The `cq` payload is the Codex
translator's own `scripts/` output carried verbatim, so the bundled tool behaves as it does on
Codex, its `.agents/` surface model and its telemetry refusals included.

The payload root carries `.claude-plugin/plugin.json`, emitted by the generator with `name: quenching`
and the source `VERSION`. The bundled `cq` enables a pillar only when the root that owns its package
has a manifest naming the owning module, `quenching` or `quenching-codex`; without the manifest every
pillar answers `belongs to module ..., which is not enabled` (exit 2) in a clean directory. A test
runs the bundled `cq` in an empty directory so the manifest cannot regress.

No model is pinned: commands and subagents run on the model the OpenCode session configures,
and the source tier and effort survive as prose. Agent permissions are mapped deny-only from the
source `tools:` — no edit tool → `edit: deny`, no `WebFetch` → `webfetch: deny`, no `Agent` →
the task tool off, unrestricted `Bash` → `bash: allow`, no `Bash` → `bash: deny` — with one
decided exception, set per agent: the agent's `bash` map opens with `"*": ask`, then each scoped
`Bash(cq <verbs>:*)` grant → one `"cq <verbs> *": allow` pattern, in source order. OpenCode applies the
last rule that matches (`findLast` in its permission evaluator), so a catch-all written last would
override every allow: the order is the policy (the reviewer gets
`"cq git history *": allow` and nothing else), and a scoped `Bash(...)` with no `cq` → `bash: ask`.
Only the verbs the source grants are allowed, so a read-only agent never runs `cq git push` or
`cq specs record` unasked; OpenCode checks each parsed command node, so a prefix pattern cannot be
chained past with `;`, `&&` or `$(...)`. The pattern `cq *` is written only for a source
`Bash(cq:*)`; every other allow-pattern stays a human decision. A test locks every agent's map
against its source `tools:`. The
generated README shows a session-wide `cq *` allow for `opencode.json`, because a command carries no
permission of its own. Command `allowed-tools` are dropped, as on Codex. The CI
templates `ci-github-pages.yml` and `azure-pipelines-docs.yml` of `assets/zensical/` are not copied
into the payload. Per-command permission sets and hooks are not generated; they widen or reshape
grants and stay a human decision. The generated tree is never edited by hand,
and nothing flows back from it to the source.

## Omnigent distribution

`plugins/omnigent/quenching/` is generated by `python3 scripts/sync_omnigent_plugin.py --write` and checked by
`--check` in the repository gate (the `Claude/Omnigent distribution` line of `scripts/verify_repo.sh`). It is
**one operator agent, with no payload**: the plugin's commands as skills, its agents as sub-agents and the
`quenching` MCP server. The pin is `OMNIGENT_VERSION = "0.19.1"` (server image `omnigent-server:v0.19.1`), whose
bundle schema (`omnigent/server/schemas.py`, `inner/datamodel.py`) the generator validates against.

| Path | What it holds |
| --- | --- |
| `config.yaml` | `name: quenching`, `instructions: instructions.md`, an `executor` of type `omnigent` with `harness: opencode`, `skills: none`, `os_env` of type `caller_process`, `tools.agents` listing the sub-agents and `tools.quenching` of `type: mcp` (stdio, `uvx --from git+…@<VERSION>#subdirectory=plugins/quenching quenching-mcp`, the tag equal to `plugins/quenching/VERSION`, without `v`) |
| `instructions.md` | the operator role and the routing to the skills, the sub-agents and the MCP server |
| `skills/<id>/SKILL.md` | one skill per source command (`quenching-<front>-<verb>`), 61 today |
| `agents/<name>/` | one sub-agent per source agent (`config.yaml` plus `instructions.md`, named without prefix), with its deny-only policy |
| `README.md` | the generated install note |

No model is pinned: the server's policy chooses it, and `omnigent run --harness X --model Y` overrides both
executor fields. The Omnigent schema declares the MCP server inline under `tools.<name>`; there is no
`mcp_servers` key. The prose is the OpenCode translation re-rooted — `~/.omnigent/quenching`,
`QUENCHING_OMNIGENT_ROOT`, the word Omnigent — so one prose pass exists and no second harness vocabulary is
forked. A cited reference becomes `quenching://references/<path>`, served by the MCP server; a citation to a
template, knowledge, design, zensical, eval or check asset stays under `~/.omnigent/quenching` and resolves
only where a local install sits there, since the bundle ships no payload. Every bundle loads with
`omnigent.spec.load`; a test loads it when Omnigent is importable.

The operator runs with the session's tools: the 61 skills carry no per-command policy. A skill keeps its source
`allowed-tools:` in its frontmatter as metadata the audit reads, never as a policy Omnigent applies; `hooks:` and
`model:` frontmatter are dropped. Only the sub-agents carry a policy, derived from their source `tools:` by the
rules below.

### Rule ordering

Omnigent has no positional allow list. Policies run in declaration order within a level, the levels run session,
then agent spec, then server, a DENY from any policy short-circuits, and DENY outranks ASK outranks ALLOW
(`docs/POLICIES.md` and `PolicyResult` in `omnigent/policies/types.py`, tag v0.19.1). OpenCode is the opposite
(the last matching rule wins), so the OpenCode "catch-all first" ordering does not carry over. Durable rule: an
Omnigent policy states only denials; an ALLOW can never reopen a DENY, so the order of two denials is irrelevant
and the allowed `cq` verbs are the exception inside the one shell denial, never a rule of their own.

### Permission mapping (deny-only)

One CEL policy (`omnigent.policies.builtins.cel.cel_policy`, under `guardrails.policies.source_tools`) per
sub-agent returns DENY on a `tool_call` whose `event.data.name` is in the denied set, else ALLOW. The source
agent's `tools:` is the grant set.

| Source head | Absent or not granted: denied names |
| --- | --- |
| `Write`, `Edit`, `NotebookEdit` | `sys_os_write`, `Write`, `write` / `sys_os_edit`, `Edit`, `MultiEdit`, `edit` / `NotebookEdit`; each head independently |
| `Read`, `Grep`, `Glob` | `sys_os_read`, `Read`, `read` / `Grep`, `grep` / `Glob`, `glob` |
| `WebFetch` | `WebFetch`, `webfetch`, `WebSearch`, `websearch`; a granted `WebFetch` has no Omnigent tool |
| bare `Agent` or `Task` | `sys_session_create`, `Task`, `Agent`, `task` when neither is bare; a scoped `Agent(names)` stays denied |
| `Skill` | `Skill` when absent |
| `Bash` | absent: `sys_os_shell`, `Bash`, `Shell`, `bash`; bare: none; scoped only: the shell rule |

Shell rule, for scoped `Bash(cq …:*)` and no bare `Bash`: a shell call is denied unless its `command` argument
matches, in full, one or more segments joined by `&&`, `||` or `;`, each `cq <verbs>` (the source verbs; bare
`Bash(cq:*)` meaning `cq`) followed by arguments free of `;`, `&`, `|`, `<`, `>`, `$`, backtick, backslash and
newline. A missing or non-string `command` is denied. A heredoc, a redirect, a pipe or a command substitution is
therefore denied: Omnigent has no parser a CEL expression can call, and the conservative regex denies what it
cannot split. A non-`cq` scoped grant (`python3`, `py`, `rm`, `git ls-files`, …) is denied, never widened. Tests
run adversarial commands through `celpy`.

### Model compatibility table

`plugins/quenching/assets/translation/omnigent-model-compat.json` holds the measured cells of spike H1 (forge
`spikes/h1/REPORT.md`): per command and model, the approved cases and the assertion pass rate, plus the agent cost
of the 9 cases. The same generator writes [model-compat.md](../../project/model-compat.md), an OKF doc with one
row per generated skill and one column per model, `unmeasured` unless the JSON holds the cell. H1 ran OpenCode
with the quenching-opencode port, not an Omnigent-hosted run, so a cell is evidence about the model on that
harness and not about Omnigent. Filling the rest is a human step; its per-case cost is computed from the JSON by
the generator, so the figures cannot drift from it.

### Eval profile

`scripts/eval_harnesses.json` has an `omnigent` profile: `omnigent run {arm} --harness {agent_harness} --model
{model} --no-session {extra} -p {prompt}`, with arm `with: ["{agent}"]` (the operator agent,
`plugins/omnigent/quenching`) and `without: []` (the bare harness), `prompts.with = "/{skill} {prompt}"` so the
with arm invokes the suite's `skill` in the session, and a `container` block with no permission token.
`run_evals.py` takes `--agent-harness` (default `opencode`) and refuses a skill missing from the bundle. The
wiring is proved by `--dry-run` and a stub; no Omnigent-hosted eval has been run. Whether a non-interactive
`omnigent run -p "/<skill> …"` invokes the skill is unproved: in the live proof below the command opened an interactive
REPL, and the path proved live is the HTTP API's `slash_command` of kind `skill`. The generated tree is never
edited by hand, and nothing flows back from it to the source.

### Live proof on Omnigent 0.19.1 (2026-10-28)

The operator bundle `plugins/omnigent/quenching/` was proved on an isolated `uvx omnigent@0.19.1` server (own
port, `OMNIGENT_DATA_DIR`, `HOME` and no auth), one host daemon, one session on `harness: opencode` and the
DeepSeek V4.1 Flash endpoint through the Databricks gateway. What it showed:

- **Registration.** `omnigent server --agent plugins/omnigent/quenching` pre-registers `quenching` beside the
  built-in agents (`/v1/agents`, 61 skills, one stdio MCP server); `omnigent.spec.load` of 0.19.1 reads the
  bundle with `skills_filter: none` and the 7 sub-agents.
- **Skills.** The 61 skills reach the session through `omnigent_load_skill`; a `slash_command` of kind `skill`
  injects the bundle's `SKILL.md` into the turn.
- **Sub-agent with policy.** The operator delegated to `scout` through `omnigent_sys_session_send`; the scout's
  write was denied by its CEL policy (`omnigent-policy`) and no file was created.
- **`skills: none` does not remove the duplication under OpenCode.** OpenCode's own `skill` tool still listed
  the host skills planted in `~/.claude/skills/` and `~/.agents/skills/`, including a host copy of
  `quenching-security-status` beside the bundle's; only `~/.config/opencode/skills/` was hidden, by the
  per-session `XDG_CONFIG_HOME`. The field stays in the bundle (it binds the Claude SDK harness), and a host
  that serves the operator must not carry quenching skills in those two directories.
- **MCP.** The `uvx --from git+…@6.9.0#subdirectory=plugins/quenching quenching-mcp` server does not start:
  the 6.9.0 tag has no `pyproject.toml` there. It starts only from a release that ships the MCP.
- **Cost.** Estimated at 150–250k tokens for three turns and one sub-agent; measured 53,195 tokens (49,438
  input, 1,274 output, 51,921 of them cache reads), with `total_cost_usd` 0.0 because the gateway endpoint
  carries no price in Omnigent's catalog.
