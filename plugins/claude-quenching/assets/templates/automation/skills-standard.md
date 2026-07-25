---
type: standard
title: Skill taxonomy and naming
description: How this repo's Claude Code skills are classified, named, and mirrored as commands
resource: <the surface this rule governs — .claude/skills/ and .claude/commands/>
tags: [automation, skills, naming]
timestamp: <ISO 8601 — e.g. 2026-07-20>
audience: both
authority: background   # born background (agreed-but-unproven); graduates to current once the surface follows it in practice
source: <who agreed the rule — e.g. quenching-skill-new first run, team decision>
maintainer: <owner>
---

# Skill taxonomy and naming

Every skill in `.claude/skills/` is classified on **one axis**:

- **Domain-bound** — serves ONE folder subtree of this repo. Named as the flattened
  folder path plus a verb (`communications/teams/` + create →
  `communications-teams-create`), and mirrored by a thin command wrapper at
  `.claude/commands/<folder-path>/<verb>.md`, invocable as `/<folder>:<subfolder>:<verb>`.
- **Generic** — serves the repo as a whole. Named verb-object (`release-notes`), never
  mirrored under a folder path: a flat command or none.

The classification test: name the one folder the skill acts on — exactly one answer means
domain-bound to that folder; "the repo" means generic; several unrelated folders means the
skill is kept as-is and reported, never forced onto the axis.

Directory-scoped skills (`<folder>/.claude/skills/`) are an **accepted variation** for
expressing domain-binding; new skills are minted with the mirrored-wrapper mechanism above.

The surface is listed in the registry at
[/docs/documentation/reference/automation.md](/docs/documentation/reference/automation.md):
its GENERATED zone is derived from `.claude/skills/*/SKILL.md` frontmatter, and its only
editors are the owning skills (`quenching-skill-new`, `quenching-skill-align`) — hand edits
inside the markers are repaired on their next run.

<!-- MOLD (claude-quenching · skills standard) → becomes
     `docs/standards/automation/skills.md` in a target repo's OKF bundle, offered by
     `quenching-skill-new`/`quenching-skill-align` on first run (never created without an OK).
     The body above IS the canonical rule — fill the frontmatter placeholders and keep the
     body; add repo-specific deltas (extra verbs, reserved names) below the standard text
     rather than rewriting it. Born `authority: background` per the house doctrine for
     agreed-but-unproven rules; graduate to `current` once the surface demonstrably
     follows it. STAMP = MERGE, never clobber. The full doctrine lives in the plugin
     (`quenching-skill-new/references/taxonomy.md`); this standard is the target-repo
     projection of it. -->
