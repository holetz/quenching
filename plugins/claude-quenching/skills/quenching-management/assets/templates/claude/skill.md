---
name: <prefix>-<slug>
description: >-
  <3rd person. WHAT-IT-DOES + WHEN-TO-USE + literal phrases the user would type
  (and variants). Distinguish from neighboring skills with an exclusion clause if
  there is a shared keyword. E.g.: "Creates X in Y following Z. Use when the
  user asks to 'do A', 'create B', or describes C — not for D (that belongs to
  skill W).">
when_to_use: >-
  <1-line summary of the trigger — the case in which this skill is the path>
allowed-tools: Read, Grep, Glob, Edit, Write
# Optional:
# disable-model-invocation: true   # side-effect (deploy/commit/send): only via /name
# user-invocable: false            # background/advisory skill
# paths: ["path/**"]               # restricts auto-trigger to scope
---

# <Skill title>

<Body: role + procedure. SKILL.md <500 lines; push detail to references/.
name = folder name. Prefix consistent with the repo taxonomy.>
