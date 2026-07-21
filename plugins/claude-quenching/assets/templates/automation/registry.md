---
type: documentation
title: Automation registry
description: The repo's local Claude Code automation surface — every skill and its command, derived from .claude/skills/
resource: .claude/skills/
tags: [automation, skills, commands]
timestamp: <ISO 8601 — e.g. 2026-07-20>
audience: both
authority: current
source: <who established the surface — e.g. quenching-skill-align first run>
maintainer: <owner>
---

# Automation registry

<Curated prose — one short paragraph: how this repo's automation surface is organized
(the single axis: domain-bound skills named after their folder, generic skills named
verb-object), a link to the rule at [/docs/standards/automation/skills.md](/docs/standards/automation/skills.md),
and, when relevant, a pointer to installed plugins whose commands extend the surface
(they stay out of the table below).>

The table between the markers is **DERIVED** — regenerated exclusively by its owning
skills (`quenching-skill`, `quenching-skill-align`) from the local
`.claude/skills/*/SKILL.md` frontmatter. Edit outside the markers only.

<!-- GENERATED:BEGIN -->
| Command | Skill | Serves | Typical trigger |
| --- | --- | --- | --- |
| /<folder>:<subfolder>:<verb> | <flattened-path>-<verb> | <folder>/<subfolder>/ | "<first quoted trigger>" |
| — | <verb-object> | generic | "<first quoted trigger>" |
<!-- GENERATED:END -->

<!-- MOLD (claude-quenching · automation registry) → becomes
     `docs/documentation/reference/automation.md` in a target repo's OKF bundle. Zone
     rules (owner: the plugin's `quenching-skill/references/taxonomy.md`): rows ordered by
     the Command column, wrapperless rows (`—`) last ordered by Skill; the zone lists ONLY
     the repo's own surface — plugin-contributed commands (/opsx:*, marketplace plugins)
     may be pointed at from the curated prose, never listed in the zone; the two owning
     skills are the zone's only editors, and their self-checks diff the zone against
     `.claude/skills/` and regenerate on mismatch. STAMP = MERGE, never clobber. -->
