# Dimension 8 · Hooks

Hooks are **deterministic automation** wired into the session lifecycle — validate, audit,
re-inject, block. They are the home of what *needs* to happen, in contrast to CLAUDE.md,
which is guidance the model can ignore.

> **Canonical home — `.claude/hooks/` + `.claude/settings.json` (adaptive wiring);
> executable logic in `scripts/` · Fixed (purpose tree).** A hook is a thin trigger that
> *calls* a script; the `scripts/` tree (`ci/`, `checks/`, `<gen>/`, `maintenance/`, `dev/`)
> is canonical. See [Fixed vs. adaptive](../architecture.md).

## Why it belongs in the method

The governing principle is one line from Anthropic's containment work:
*deterministic limits are more reliable than probabilistic guardrails*
([How we contain Claude](https://www.anthropic.com/engineering/how-we-contain-claude)).
A rule written in CLAUDE.md is a *hope*; a hook is a *guarantee*. So anything that must
hold — protecting a generated artifact, surviving a `/compact`, recording who changed the
surface — belongs in a hook, not in prose
([Automate actions with hooks](https://code.claude.com/docs/en/hooks-guide),
[Hooks reference](https://code.claude.com/docs/en/hooks)).

Hooks are also what keep the knowledge surface **alive between audits**. Three lifecycle
hooks do the work: one **re-injects** conventions after compaction (which would otherwise
erase them), one **proposes** CLAUDE.md/memory deltas at end of turn while the gap is
fresh, and one **records** every config change. The detail that trips people up is
**output semantics** — `exit 2` blocks and feeds stderr back to the model, while `exit 1`
only warns and lets the dangerous action through — and the rule that a hook only runs if
it is **wired** in `settings.json`. The reusable logic itself lives in `scripts/`, organized
by purpose; the hook is a thin adapter that calls it, never a place to inline a build.

## What "good" looks like

- Declared in `settings.json`, scripts in `.claude/hooks/`, idempotent, with a sensible
  timeout and an explicit criterion.
- Blocking hooks use `exit 2` (or `permissionDecision: "deny"`); `Stop` hooks guard against
  loops with `stop_hook_active`.
- The three lifecycle hooks present; a `PreToolUse` guard protects generated artifacts.
- Executable logic lives in a purpose-organized `scripts/` tree with a README-map in sync.

## How it drifts

- **Orphan hook** (script present, never wired) or **dangling hook** (wired to a missing
  script).
- **Wrong event/matcher** — a blocking check placed in `PostToolUse`, which can't block.
- **`exit 1` in a blocking hook** — thinks it warns; the dangerous command still runs.
- **Snippet overwriting instead of merging** — clobbers a hook the repo already had.
- **Business rule inlined in the hook** instead of a called `scripts/…`.

## How the method closes the gap

It wires orphans (merging, never clobbering), removes danglers, fixes `exit` codes,
installs the lifecycle hooks, and extracts inline logic into `scripts/`. The payload is the
`quenching-config` skill plus six bundled hooks and the `scripts/` scaffold — the full
table is in [Bundled artifacts](../../plugin/artifacts.md); the canonical tree is the shipped
[`scripts-taxonomy.md`](https://github.com/holetz/claude-quenching/blob/main/plugins/claude-quenching/skills/quenching-management/references/scripts-taxonomy.md).

## Sources

- [Automate actions with hooks — Claude Code Docs](https://code.claude.com/docs/en/hooks-guide) — Anthropic · accessed 2026-06-28
- [Hooks reference — Claude Code Docs](https://code.claude.com/docs/en/hooks) — Anthropic · accessed 2026-06-28
- [How we contain Claude across products — Anthropic Engineering](https://www.anthropic.com/engineering/how-we-contain-claude) — Anthropic · accessed 2026-06-28
- [Claude Code Settings — Claude Code Docs](https://code.claude.com/docs/en/settings) — Anthropic · accessed 2026-06-28
