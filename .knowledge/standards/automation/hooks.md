---
type: standard
title: Scoped hooks
description: Where a hook may be installed, what each scope and handler costs, and the policy defaults every hook obeys
resource: .claude/settings.json, plugins/quenching/commands/**, plugins/quenching/assets/bin/quenching/components/**
tags: [automation, hooks, performance, budget]
timestamp: 2026-08-10
audience: both
authority: current
source: skill-front capability research (2026-07-27) — hookify/plugin-dev + official docs; the knowledge checker's dirty-gate precedent. Graduated to current on an adopting surface, and the components pillar enforces both rungs from one implementation (8 selftest cases, since ported to the test suite). The adopting surface changed shape (2026-08-03, enxugar-create-e-eliminar-o-rung-hooks spec): the plugin's own hooks/hooks.json wires the checker for every repo, so the three rung-1 frontmatter blocks it replaced were removed; the dead-rung paragraph gained this repo's own measurement (2026-08-06) after its frozen 4.4.5 copy was caught reporting `bundle root is not a directory` against a bundle the shipped 4.13.0 passed clean
maintainer: quenching
---

# Scoped hooks

A hook charges **other people's operations**: it fires on events the command that installed
it does not own, so a session-wide hook taxes every iteration in the repo — including every
one it never helps. This repo therefore installs every hook at the **narrowest scope that
still catches what it exists to catch**, minted by `/quenching:components:hook:new` under one plan → one
OK, inventoried (report-only) by `/quenching:components:align`.

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

**This repo wires no hook of its own today.** It once wired the OKF checker itself, at rungs 2 and
3, via `plugins/quenching/hooks/hooks.json` — a `PostToolUse` hook matched to `Write|Edit` and a
`stopScan: "dirty"`-gated `Stop` sweep, both invoking `cq knowledge hook` — for every repo that had
the plugin installed. The capability was discontinued outright (`descontinuar-hooks-do-plugin`
spec), not merely rescoped: nothing in this repo answers a hook event any more, and
`/quenching:components:hook:new` is how a hook — a future one of this repo's own, or a target's —
gets minted, under the two ladders above.

**The lesson the old wiring left behind, still worth keeping.** A target that once accepted an
older install offer could carry a frozen, dead copy of the checker alongside the live one — this
repo carried exactly that until 2026-08-06, a copy frozen at `4.4.5` against a shipped `4.13.0`,
still resolving its bundle root from a retired `docsDir` config key. The dead copy reported
`bundle root is not a directory` on every sweep, against a bundle the current checker passed
clean: a frozen duplicate does not merely go redundant, because the contract it was frozen against
can move underneath it, and it then reports **failures of its own staleness as findings about your
repo**. `/quenching:knowledge:align` removes that class of debris on sight.

The full pricing doctrine lives once, in
[capabilities.md](/plugins/quenching/assets/references/components-command-new/capabilities.md) §Hooks;
this standard is the repo-side projection of it. An unparseable `settings*.json` is
`sk-hook-unparseable` — every hook wired in it is dead.
