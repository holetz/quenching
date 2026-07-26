---
description: <one line — what invoking this command does>
argument-hint: [<the input the skill accepts — e.g. subject, target file, options>]
---

Use the Skill tool to invoke `<skill-name>`, passing `$ARGUMENTS` as the skill's input.

<!-- MOLD (claude-quenching · automation command wrapper) → becomes
     `.claude/commands/<folder-path>/<verb>.md` for a domain-bound skill (invocable as
     `/<folder>:<subfolder>:<verb>` — native `:` separator, one per path segment) or
     `.claude/commands/<name>.md` flat for a generic skill that wants one. The wrapper
     pattern, literally: frontmatter `description` + `argument-hint`, ONE sentence of body
     invoking the skill via the Skill tool with `$ARGUMENTS`. The wrapper stays thin — the
     skill body, its doctrine, and its triggers live in `.claude/skills/<skill-name>/`
     only; a wrapper that restates them drifts.

     Keep the `description` SHORT. Claude Code produces `/x` from a command or a skill alike,
     so the only thing this wrapper still buys is the `:`-namespaced `/` tree — and its
     description is always in context, on every session, alongside the skill's own. One line
     that names the action is the whole budget it has earned; `skills.py budget` reports the
     wrapper half of the surface's total separately for exactly this reason. -->

