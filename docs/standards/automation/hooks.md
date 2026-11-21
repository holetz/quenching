---
type: standard
title: Scoped hooks
description: Where a hook may be installed, what each scope and handler costs, and the policy defaults every hook obeys
resource: .claude/settings.json, quenching/skills/**, quenching/assets/bin/quenching/components/**
tags: [automation, hooks, performance, budget]
timestamp: 2026-11-20
audience: both
authority: current
source: 2026-07-27, 2026-08-03, enxugar-create-e-eliminar-o-rung-hooks, 2026-08-06; lineage in ADR 0004
maintainer: quenching
---

# Scoped hooks

<!-- rules -->

A hook charges **other people's operations**: it fires on events the command that installed
it does not own, so a session-wide hook taxes every iteration in the repo — including every
one it never helps. This repo therefore installs every hook at the **narrowest scope that
still catches what it exists to catch**, minted by `/quenching-components hook-new` under one plan → one
OK, inventoried (report-only) by `/quenching-components align`.

## The scope ladder — narrowest first

1. **Skill-scoped** — `hooks:` in the owning command's frontmatter; fires only while that
   command runs. The default home for a check tied to one workflow.
2. **Operation-scoped** — a `settings.json` hook with an event + `matcher` (+ `if` gate);
   fires only on matched tool calls.
3. **Gated wide event** — a `Stop`/`UserPromptSubmit` hook made cheap by construction:
   dirty-gated by a marker file (an untouched turn costs one stat) or `once: true`. No live
   example in this repo today — the plugin's own dirty-gated `Stop` hook, once the standing
   example, was retired along with the capability it checked (§What this repo's own surface
   does under it).
4. **Unmatched session-wide** — a finding (`sk-hook-unmatched`) unless the reason nothing
   narrower suffices is stated where the hook is wired.

## The handler ladder — cheapest first

1. **`command`** — deterministic script; prints `{}` on no-match, so a non-firing turn costs
   process time and **zero tokens**.
2. **`prompt`** — one cheap-model judgment per firing.
3. **`agent`** — a full-model inference per firing; on a per-tool-call event this is
   `sk-hook-llm-frequent` and demands a stated reason.

Climb only when the rung below cannot express the check; a fast `command` rung deciding the
deterministic 95% may share a matcher with a `prompt` rung for the judgment tail.

## Policy defaults

- **Warn by default; block by consent** — a blocking hook is chosen by the human at mint,
  per rule.
- **Intrusive rules are born disabled**, their body saying when to enable them.
- **Fail open on infrastructure, fail closed on scope** — a crashed script never blocks the
  session; an unclassifiable event matches nothing.
- **Every hook carries a `timeout`** sized to its event's frequency.
- **`Stop` hooks honor `stop_hook_active`** — the re-fire loop guard.
- **Hooks are independent** — matching hooks run in parallel and never see each other's
  output; two hooks that need an order are one hook.
- **Every hook states its cost claim** at mint: event × frequency × handler cost × fast-path
  cost on no-match.
- **A handler whose script may not be installed guards its own absence.** `python3 <missing-file>`
  exits **2**, and on `PostToolUse` exit 2 feeds stderr back as an error — so a hook pointing at
  an optionally-installed checker turns every matched tool call into a reported failure in exactly
  the repos that never installed it. Lead with the guard, and keep the checker's own exit code:
  `test -f "<path>" || exit 0; python3 "<path>"`. A missing handler must be a **no-op**, never a
  finding about the handler.

## What this repo's own surface does under it

**The source declares its hooks in `modules.json`; deploy installs them.** A module lists its hooks
in `owned.hooks` (`name`, `event`, `matcher`, `timeout`; the body is the Python file
`assets/hooks/<name>.py`), and `cq deploy` merges them into the target's `.claude/settings.json`.
The owner of a hook is the module that declares it.

**Two harnesses read that file, so the command is one polyglot line.** Claude Code runs a hook
command through bash (Git Bash on Windows); the GitHub Copilot harness — the VS Code Agents window
and the Copilot CLI — reads the same `.claude/settings.json` and, on Windows, runs the command
through PowerShell or cmd, where a bash line fails and a failed `preToolUse` command **denies the
tool call**. The deployed command is therefore `<python prefix> -I -c "<code>"`, where `<code>` holds
no `$`, no backtick, no `%`, no `!` and no inner double quote, so bash, PowerShell and cmd all hand it
to Python unchanged. The code takes the root from `CLAUDE_PROJECT_DIR` (both harnesses export it;
Copilot also exports `COPILOT_PROJECT_DIR`), else the working directory, prints `{}` when the body
is not installed — the absence guard, now inside Python — and otherwise runs the body as
`__main__`. The prefix is the repository's `shared.mcp.command` when declared (the one that already
starts the MCP server), else `python3`; a Windows target declares it, since `python3` is often only
the Store alias there. The marker path `.agents/quenching/assets/hooks/<name>.py` stays a literal
substring of the command, which is how the merge finds its own entry — an older `<name>.sh` entry is
recognised too and rewritten in place.

**A body reads both input shapes.** Claude Code, and Copilot's `PreToolUse` alias, send
`tool_input.command`; Copilot's native `preToolUse` sends `toolArgs`, an object or JSON text. The
output stays `hookSpecificOutput.permissionDecision`, which both accept. The matcher names both
shell tools (`Bash|PowerShell|bash|powershell`), so a Windows session's PowerShell calls are guarded
too.

**A separate `.github/hooks/` file is not shipped.** It is Copilot's own format, but Copilot also
reads `.claude/settings.json`, so a second file would run every hook twice there.

**`deny-claude-coauthor`.** `quenching-specs` declares one rung-2 `PreToolUse` hook matched to
the shell tools, running `assets/hooks/deny-claude-coauthor.py` (5-second timeout, absence-guarded). It denies a
message-writing command (`git commit`/`merge`/`tag`/`notes`, `gh pr`, `cq git`) that carries Claude's
co-authorship trailer or `Generated with Claude Code` line — a block chosen by the owner on
2026-10-18. Rung 1 does not suffice: a skill-scoped hook misses every commit made outside
`/quenching-git commit`. Cost claim: every shell call × one Python start and one regex over the raw
input, zero tokens on no-match; the JSON is parsed only when that regex names a co-author. It denies rather than
rewrites, because `updatedInput` applies only paired with `allow`, which would auto-approve the
whole command. Opt-out: `QUENCHING_ALLOW_CLAUDE_COAUTHOR=1`.

**`warn-git-add-all`.** `quenching-git` declares a rung-2 `PreToolUse` hook on the shell tools that warns
(never blocks) on two things: `git add -A`, `--all` and `.`, citing `/quenching-git commit`; and a
command that skips the git hooks — `--no-verify`, `git commit -n`, `git -c core.hooksPath=` — since
the leak and identity gates only exist while those hooks run. Both rules share one body, so a shell
call pays one Python start for them, not one each; the file keeps its first rule's name because the
settings merge finds its entry by it. Cost claim: every shell call × one Python start and two
regexes over the raw input, zero tokens on no-match; a regex hit is confirmed on the tokenized
command, so a quoted commit message or an `echo` that only mentions a flag stays silent. It reads the command text only — a hook path
set by `git config` beforehand, a variable or an alias goes unseen — so it is a reminder, not a
boundary. A skill-scoped rung 1 does not exist for it: the skill bridge is a byte copy and carries
no frontmatter hook.

**Before it, this repo wired no hook of its own.** It once wired the OKF checker itself, at rungs 2 and
3, via a `hooks.json` shipped under this plugin's own `hooks/` — a `PostToolUse` hook matched to `Write|Edit` and a
`stopScan: "dirty"`-gated `Stop` sweep, both invoking `cq knowledge hook` — for every repo that had
the plugin installed. The capability was discontinued outright (`descontinuar-hooks-do-plugin`
spec), not merely rescoped: nothing in this repo answers a hook event any more, and
`/quenching-components hook-new` is how a hook — a future one of this repo's own, or a target's —
gets minted, under the two ladders above.

**The three bundle-writing commands hold no rung, and rely on their own Self-check.**
`/quenching-knowledge add`, `/quenching-knowledge learn` and `/quenching-knowledge define` each
carried a rung-1 frontmatter block running `cq knowledge validate` on its own `Write`/`Edit`. All
three were removed on 2026-08-03 (`enxugar-create-e-eliminar-o-rung-hooks` spec) as redundant with
the wiring above — which was then discontinued along with it. **Nothing replaced them**: each
command's own *Self-check against the conformance core* step, run against
`quenching/references/knowledge-align/conformance.md`, is the whole of the
conformance check at the moment of the write, and it is a step the body executes rather than an
event anything answers. Restoring the rung would be a **mint, not a revert** — through
`/quenching-components hook-new`, under the two ladders above and behind the missing-handler guard
this standard requires, since `cq` may not be installed in the target being written into. Stated
here because the claim is otherwise re-derived from the removal's own rationale, which the
discontinuation invalidated: the plugin manual asserted the three blocks as live for two releases
after they were gone.

**The lesson the old wiring left behind, still worth keeping.** A target that once accepted an
older install offer could carry a frozen, dead copy of the checker alongside the live one — this
repo carried exactly that until 2026-08-06, a copy frozen at `4.4.5` against a shipped `4.13.0`,
still resolving its bundle root from a retired `docsDir` config key. The dead copy reported
`bundle root is not a directory` on every sweep, against a bundle the current checker passed
clean: a frozen duplicate does not merely go redundant, because the contract it was frozen against
can move underneath it, and it then reports **failures of its own staleness as findings about your
repo**. `/quenching-knowledge align` removes that class of debris on sight.

The full pricing doctrine lives once, in
`quenching/references/components-command-new/capabilities.md` §Hooks;
this standard is the repo-side projection of it. An unparseable `settings*.json` is
`sk-hook-unparseable` — every hook wired in it is dead.
