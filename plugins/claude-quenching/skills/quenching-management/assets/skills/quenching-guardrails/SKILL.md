---
name: quenching-guardrails
description: >-
  Behavioral guardrails for LLM-assisted coding in a repo — Think-Before-Coding,
  Simplicity First, Surgical Changes, and Goal-Driven Execution. Use when writing,
  reviewing, or refactoring code anywhere in the repo, to avoid overcomplication,
  keep changes surgical, make assumptions explicit early, and execute against a
  verifiable criterion. The root CLAUDE.md must CITE this skill (link), never copy
  the directives as prose.
when_to_use: >-
  behavioral guidelines when coding (simplicity, surgical change, explicit
  assumptions, goal-driven execution).
allowed-tools: Read
---

# Behavioral guardrails — LLM-assisted coding

> Skill-template of the `quenching-management` method. Generic and portable:
> the repo's root CLAUDE.md **cites** this skill by link (dimension 14), instead
> of duplicating the directives as prose (avoids the cross-quadrant smell of
> dim 12).

The four directives:

- **Think Before Coding** — make assumptions and ambiguities explicit **before**
  implementing; if something decisive is uncertain, **ask** instead of guessing.
- **Simplicity First** — the **minimum** that solves the request: no single-
  call-site abstraction, no speculative knob, no impossible-error handling.
- **Surgical Changes** — touch **only** what the task requires; do not refactor
  working code; point out neighboring dead code/bugs instead of silently changing
  them.
- **Goal-Driven Execution** — convert the request into a **verifiable criterion**
  (a test that fails → make it pass) and iterate until it passes.

## Why cite, not copy

A guardrail is **broad and stable** knowledge, but the canonical home is **a skill**
(loaded when going to code), not the always-loaded CLAUDE.md. Copying it as prose
in CLAUDE.md spends a fixed context budget and creates two sources that can diverge.
CLAUDE.md cites: *"Coding guardrails: see skill `quenching-guardrails`."*
