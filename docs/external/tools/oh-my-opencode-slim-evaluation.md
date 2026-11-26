---
type: external
title: oh-my-opencode-slim evaluation
description: Facts about the oh-my-opencode-slim OpenCode plugin gathered from search extracts, with a verdict per mechanism for quenching — hub-and-spoke orchestrator with specialist agents, keyword-triggered council injection paid once per session, named model presets with single-parent extends, session-id handoff of stored council answers, a codemap.md per directory, subagent allowlists compiled into permissions, and which mechanisms are OpenCode-runtime specific
resource: quenching/agents/**
tags: [opencode, plugin, multi-agent, orchestration, presets, evaluation]
timestamp: 2026-11-26
audience: both
authority: background
source: spec 2147, 2026-11-26, retrieved from search extracts (README, docs, DeepWiki), the repository itself was not read
maintainer: quenching
---

# oh-my-opencode-slim evaluation

Facts about the [oh-my-opencode-slim](https://github.com/alvinunreal/oh-my-opencode-slim) OpenCode
plugin (v3.0.7 at retrieval), read as a reference for quenching. External tool facts, not our
contract. **Provenance:** retrieved 2026-11-26 from search extracts of the README, `docs/council.md`,
`docs/configuration.md`, `GLOSSARY.md`, `src/agents/codemap.md`, DeepWiki (2026-10-24), Hysen Labs
(2026-09-21) and Greptile (undated). The repository was not read directly, so a mechanism may differ
in code; reconfirm the primary source before building on any row.

## What the plugin is

An OpenCode plugin with a hub-and-spoke shape: one orchestrator delegates to specialists (explorer,
oracle, designer, fixer, an optional observer, and a council with councillors), each with its own
model, prompt and permission, configured in `~/.config/opencode/oh-my-opencode-slim.json`. It also
ships background tasks, LSP and AST-search tools, MCPs (Exa, Context7, grep.app) and skills
(deepwork, codemap, verification-planning, reflect).

## Mechanisms and what they mean for quenching

| # | Mechanism | Quenching today | Verdict | Where it went |
| --- | --- | --- | --- | --- |
| 1 | `council-inject`: the council procedure is injected once per session, on the first trigger keyword; a session that never asks pays zero tokens | Section-addressed reference reads through `components_read` | Covered | none |
| 2 | Named model presets with single-parent `extends` and runtime switch (`/preset`) | Model tier and effort fixed in each agent's frontmatter | Applicable | spec 585 |
| 3 | The orchestrator passes only session ids to the synthesizer; the harness attaches the stored answers, so text is never retyped | The orchestrator receives and relays worker summaries | Applicable | spec 586 |
| 4 | A `codemap.md` per directory (responsibility, design, flow) as an orientation map | `/docs/index.md` and the glossary orient; no per-area code map | To evaluate | spec 587 |
| 5 | `agents.orchestrator.subagents` compiled into `subagent allow/deny` permissions | Spawn grant fixed per agent | Applicable, widens a grant | spec 588, the human's decision |
| 6 | Fixer, observer and the synthesizer cannot spawn; nesting depth is limited | `task: false` profile already closes nesting | Covered | none |
| 7 | Council seats see only their prompt; read-only is enforced by permission config, never prompt text | Read-only agents by frontmatter; clean-context reviewer | Covered | none |
| 8 | Multimodal observer, tmux panes, native background jobs, LSP and AST tools | Depend on the OpenCode runtime | Not applicable | none |
| 9 | Custom agents declared in config with model, prompt, description and permission | `components agent-new` generates the subagent | Covered | none |

## Cautions

- Rows 2 and 5 touch configuration and permission surface, which epic 559 reserves for the human
  (epic 560); neither is authorised by this evaluation.
- Web extracts support an alternative or a rationale; none grounds a binding rule alone.
