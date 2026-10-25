---
type: standard
title: Surface translation — Claude, Codex and OpenCode
description: A repository may carry Claude and Codex surfaces together; Claude owns configuration and deterministic translation keeps their command, reference, and harness artifacts aligned
resource: plugins/quenching/assets/bin/quenching/components/commands/translate.py, plugins/quenching/assets/translation/codex-adaptation.json, .agents/plugins/marketplace.json, scripts/sync_opencode_plugin.py, plugins/quenching-opencode/**, scripts/sync_omnigent_plugin.py, plugins/quenching-omnigent/**, plugins/quenching/assets/translation/omnigent-model-compat.json
tags: [architecture, claude-code, codex, opencode, omnigent, translation, surfaces]
timestamp: 2026-10-25
audience: both
authority: current
source: alinhar-plugin-a-agents-md spec, tasks 2.1–2.4 (2026-08-18)
maintainer: quenching
---

# Surface translation — Claude, Codex and OpenCode

<!-- rules -->

This marketplace repository publishes and checks its generated Codex plugin under
`plugins/quenching-codex/`, registered in `.agents/plugins/marketplace.json`. Regenerate it with
`python3 scripts/sync_codex_plugin.py --write`; the translator also remains a capability
for target repositories. A repository may expose `.claude/` and `.agents/` at the same time. They are paired surfaces,
not alternatives: Claude remains the authoritative source for configuration and the translator
generates the Codex representation deterministically.

The package's platform, identity, manifest and catalog are declared in `assets/modules.json` under
`distributions`. Publication and the isolated marketplace upgrade check are governed by
[versioning-release.md](../ci-cd/versioning-release.md); translation drift alone does not prove
that an installed consumer can discover or upgrade the package.

## What translates

`cq components translate --source <repo> --target <repo>` maps each
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

`.claude/quenching.json` is the single configuration home. The Codex surface does not receive a
second copy, so coexistence cannot create two independently editable configurations.

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
cannot measure a Codex run. Shared `.claude/quenching.json` remains the configuration home.

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

`plugins/quenching-opencode/` is generated by `python3 scripts/sync_opencode_plugin.py --write`
and checked by `--check` in the repository gate; the release regeneration runs it after the
Codex step. It is laid out as an OpenCode configuration directory: `commands/quenching-<front>-<verb>.md`
for each source command, `agents/quenching-<agent>.md` for each source agent registered as an
OpenCode subagent, and `quenching/` carrying the cited references, templates, specs, knowledge,
design, portal, checks (Python only), zensical, evals, opensource, agent protocols and the bundled `cq`. It has no marketplace entry and no
`distributions` row: installing it is copying it into the OpenCode configuration directory.

Markdown is translated from the Claude source with the OpenCode vocabulary: module-qualified ids
become `quenching-<front>-<verb>`, agent ids become `quenching-<agent>`, plugin paths become the
installed payload root `~/.config/opencode/quenching/`, and every bash block that calls `cq`
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

`plugins/quenching-omnigent/` is generated by `python3 scripts/sync_omnigent_plugin.py --write` and checked
by `--check` in the repository gate (the `Claude/Omnigent distribution` line of `scripts/verify_repo.sh`). It is
laid out as Omnigent agent bundles: `agents/<id>/config.yaml` plus `instructions.md` for each source command
(`quenching-<front>-<verb>`) and each source agent (`quenching-<agent>`), the same payload as the OpenCode
distribution under `quenching/` (bundled `cq` included), `PERMISSIONS.md`, `MODEL-COMPAT.md`, `README.md` and the
manifest. The pin is `OMNIGENT_VERSION = "0.19.1"` (server image `omnigent-server:v0.19.1`). The prose is the
OpenCode translation re-rooted — `~/.omnigent/quenching`, `QUENCHING_OMNIGENT_ROOT`, the word Omnigent — so one
prose pass exists and no second harness vocabulary is forked. Every bundle loads with `omnigent.spec.load`; a
test loads all of them when Omnigent is importable.

A `config.yaml` carries `spec_version: 1`, an `executor` of type `omnigent` with `harness: opencode` (the loader
requires one; `omnigent run --harness X --model Y` overrides both and no model is pinned), `os_env` of type
`caller_process` only when the source grants Read, Write, Edit or Bash, `spawn: true` only when the source grants
a bare `Agent` or `Task`, and `guardrails.policies.source_tools`. `hooks:` and `model:` frontmatter are dropped
and listed in `PERMISSIONS.md`.

### Rule ordering

Omnigent has no positional allow list. Policies run in declaration order within a level, the levels run session,
then agent spec, then server, a DENY from any policy short-circuits, and DENY outranks ASK outranks ALLOW
(`docs/POLICIES.md` and `PolicyResult` in `omnigent/policies/types.py`, tag v0.19.1). OpenCode is the opposite
(the last matching rule wins), so the OpenCode "catch-all first" ordering does not carry over. Durable rule: an
Omnigent bundle states only denials; an ALLOW can never reopen a DENY, so the order of two denials is irrelevant
and the allowed `cq` verbs are the exception inside the one shell denial, never a rule of their own.

### Permission mapping (deny-only)

One CEL policy (`omnigent.policies.builtins.cel.cel_policy`) per bundle returns DENY on a `tool_call` whose
`event.data.name` is in the denied set, else ALLOW. The source `allowed-tools:` (commands) and `tools:` (agents)
are both read as the grant set, which makes a command bundle stricter than the Claude command (a pre-approval
there), never wider.

| Source head | Absent or not granted: denied names |
| --- | --- |
| `Write`, `Edit`, `NotebookEdit` | `sys_os_write`, `Write`, `write` / `sys_os_edit`, `Edit`, `MultiEdit`, `edit` / `NotebookEdit`; each head independently |
| `Read`, `Grep`, `Glob` | `sys_os_read`, `Read`, `read` / `Grep`, `grep` / `Glob`, `glob` |
| `WebFetch` | `WebFetch`, `webfetch`, `WebSearch`, `websearch`; a granted `WebFetch` has no Omnigent tool and is listed |
| bare `Agent` or `Task` | `sys_session_create`, `Task`, `Agent`, `task` when neither is bare; a scoped `Agent(names)` stays denied and listed |
| `Skill` | `Skill` when absent |
| `Bash` | absent: `sys_os_shell`, `Bash`, `Shell`, `bash`; bare: none; scoped only: the shell rule |

Shell rule, for scoped `Bash(cq …:*)` and no bare `Bash`: a shell call is denied unless its `command` argument
matches, in full, one or more segments joined by `&&`, `||` or `;`, each `cq <verbs>` (the source verbs; bare
`Bash(cq:*)` meaning `cq`) followed by arguments free of `;`, `&`, `|`, `<`, `>`, `$`, backtick, backslash and
newline. A missing or non-string `command` is denied. A heredoc, a redirect, a pipe or a command substitution is
therefore denied: Omnigent has no parser a CEL expression can call, and the conservative regex denies what it
cannot split. A non-`cq` scoped grant (`python3`, `py`, `rm`, `git ls-files`, …) is denied, listed per bundle in
`PERMISSIONS.md` as "not expressed", never widened. Tests run adversarial commands through `celpy`.

### Model compatibility table

`plugins/quenching/assets/translation/omnigent-model-compat.json` holds the measured cells of spike H1 (forge
`spikes/h1/REPORT.md`): per command and model, the approved cases and the assertion pass rate, plus the agent cost
of the 9 cases. `MODEL-COMPAT.md` renders one row per generated command and one column per model, `unmeasured`
unless the JSON holds the cell. H1 ran OpenCode with the quenching-opencode port, not an Omnigent-hosted run, so a
cell is evidence about the model on that harness and not about Omnigent. Filling the rest is a human step; its
per-case cost is computed from the JSON by the generator, so the figures cannot drift from it.

### Eval profile

`scripts/eval_harnesses.json` has an `omnigent` profile: `omnigent run {arm} --harness {agent_harness} --model
{model} --no-session {extra} -p {prompt}`, with arm `with: ["{agent}"]` (the generated bundle of the suite's
`skill`) and `without: []` (the bare harness), and a `container` block with no permission token. `run_evals.py`
takes `--agent-harness` (default `opencode`); `arm_values` builds the values of both the dry run and `run_arm`
and refuses a missing bundle. The wiring is proved by `--dry-run` and a stub; no Omnigent-hosted eval has been
run. The generated tree is never edited by hand, and nothing flows back from it to the source.
