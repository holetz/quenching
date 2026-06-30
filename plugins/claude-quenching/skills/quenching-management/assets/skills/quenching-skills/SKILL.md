---
name: quenching-skills
description: >-
  Creates, edits, and optimizes skills, sub-agents, and commands in a Claude Code
  repo — with focus on the DESCRIPTION as routing code (3rd person, what-it-does
  + when-to-use + user's literal phrases) and the should-trigger × should-not-trigger
  test. Decides the HOME of a flow (skill × sub-agent × command × hook) and
  ensures least-privilege tools in agents. Use when the user asks to "create a
  skill", "create a sub-agent", "improve the skill description", "the skill is not
  triggering", "skill with a huge SKILL.md", "two skills colliding on trigger",
  "convert a command to a skill", "what should be skill/agent/hook", or "agent
  with no declared tools".
when_to_use: >-
  authoring/editing/optimizing skills, sub-agents, and commands; sharpening
  trigger descriptions; deciding the home of a flow; least-privilege tools.
allowed-tools: Read, Grep, Glob, Edit, Write
---

# Authoring skills, sub-agents, and commands

> Skill-template of the `quenching-management` method. Generic and portable:
> adapt the prefix/taxonomy and language to the conventions of the repo where
> it is installed.

## The description is routing code

The `description` (+`when_to_use`) is the **only** text always visible to the
model and what it uses to pick the right skill among 100+ available. Rules:

- **3rd person**, specific: **what-it-does** + **when-to-use** + **literal phrases
  the user would type** (and variants). Never 1st/2nd person ("I can…/You can…").
- **Distinguishes** from neighboring skills in the same domain (exclusion clause
  when there is a shared keyword).
- `name` = folder name; thematic prefix consistent with the repo's taxonomy.

### Verifiable trigger test

For each skill, write 3-5 requests that **should** trigger it and 3-5 *tricky*
ones (same keywords, require another skill) that **should not**. Wrong trigger
on the should-nots = **false-trigger**; silence on the shoulds = **missed-fire**.
Both are a **description** problem, not an instruction one (rule: if it works via
`/name` but does not auto-trigger, the body is correct and the description is the
bug). Fix with literal phrases + exclusion clause — without narrowing too much.

## Deciding the home of a flow (skill × sub-agent × command × hook)

Ask in order:

1. Would the intermediate output **flood** the context with results that won't be
   re-referenced, **or** is the same worker spawned repeatedly? ⇒ **sub-agent**.
2. Does the operator need to **see and direct each step** in the main thread? ⇒
   **skill**.
3. Is it just a manual invocation shortcut? ⇒ **command**.
4. Does the action need to be **deterministically guaranteed** (enforcement)? ⇒
   **hook**.

## Sub-agents — least-privilege

- Complete frontmatter: `name`/`description`/`tools`/`model`.
- **`tools` ALWAYS declared** — omitting it makes the agent **inherit all** parent
  tools (a read-only auditor would gain `Edit`/`Write`/`Bash`/MCP). Allowlist via
  `tools`, denylist via `disallowedTools`.
- Body = role + inputs + numbered steps + **explicit return format**.
- Cheap audit: `tools: Read, Grep, Glob`, `model: haiku`.

## Structural hygiene

- SKILL.md <500 lines; detail goes to `references/`.
- Side-effect (deploy/commit/send) ⇒ `disable-model-invocation: true`.
- Advisory-only ⇒ `user-invocable: false`; scope ⇒ `paths`.
- Skill/agent frontmatter templates live in `assets/templates/claude/` of the
  method.
