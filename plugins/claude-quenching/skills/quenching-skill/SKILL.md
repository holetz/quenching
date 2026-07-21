---
name: quenching-skill
description: >-
  Mints or edits ONE Claude Code skill in a target repo's local automation surface
  (.claude/skills/ + .claude/commands/) — classified on the single taxonomy axis
  (domain-bound × generic), canonically named, mirrored by a thin command wrapper when
  domain-bound, written under the skill-writing doctrine, with the derived OKF artifacts
  (registry, glossary, log) regenerated in the tail. Use when the user asks to "create a
  skill", "mint a skill for X", "add a new skill", "organize this skill", "make this
  skill conform", or "wire a command for this skill". Reads the taxonomy rule
  (docs/standards/automation/skills.md; offers to create it from the template on first
  run), presents ONE plan (classification, names, files, OKF tail), writes on a single
  OK, then self-checks — registry GENERATED zone diffed against .claude/skills/, wrapper
  resolves, description within the per-skill cap. Without an OKF bundle the mint still
  proceeds (skill + wrapper only), the tail is skipped, and quenching-align is suggested
  once. Not for: migrating the existing skills to the taxonomy → quenching-skill-align; a
  doc into the docs/ bundle → quenching-add.
when_to_use: >-
  minting or editing ONE conformant skill (+ mirrored command wrapper) in a target repo.
  The whole-surface migration sweep is quenching-skill-align.
allowed-tools: Read, Grep, Glob, Write, Edit
user-invocable: false
---

# quenching-skill — mint ONE conformant skill, wrapper and registry included

Creates or edits one skill in the **target repo's own** automation surface so the surface
stays predictable: the name tells where the skill acts, the command tree mirrors the repo
tree, and the bundle's registry lists what exists. The axis, naming, mirroring, and
registry format live in [references/taxonomy.md](references/taxonomy.md); how the
`SKILL.md` itself is written lives in [references/doctrine.md](references/doctrine.md) —
this skill owns both, and `quenching-skill-align` cites them. Molds live at
`${CLAUDE_PLUGIN_ROOT}/assets/templates/automation/`.

## Doctrine

- **The rule governs; the plan proposes.** In a target repo the taxonomy rule is
  `docs/standards/automation/skills.md` — read it before classifying and follow it when
  present (a repo-specific delta there beats the plugin default). Absent + OKF bundle
  present → the plan offers creating it from the mold, born `authority: background`;
  never created without the OK.
- **No bundle, no tail — but the mint proceeds.** `docs/index.md` without `okf_version`
  (or absent) means: write skill + wrapper only, skip registry/glossary/log silently, and
  suggest `quenching-align` **once**.
- **One plan, one OK, nothing before.** Classification, names, every file to be written,
  and the OKF tail appear in ONE plan; no file is created or modified before the single
  confirmation. A declined plan writes nothing.
- **MERGE, never clobber.** An edit preserves the skill's body and any hand-written
  content; only the gap being fixed changes. This skill never deletes a skill.
- **The registry zone has two owners.** Only this skill and `quenching-skill-align` write
  between the registry's GENERATED markers; the tail regenerates the zone from
  `.claude/skills/*/SKILL.md` frontmatter — full format in
  [references/taxonomy.md](references/taxonomy.md) §registry.

## Workflow

### 1. Read the rule
Read `docs/standards/automation/skills.md` and confirm the bundle
(`docs/index.md` carries `okf_version`). Rule present → it governs. Rule absent, bundle
present → add "create the rule from `automation/skills-standard.md`" to the plan. No
bundle → note the tail as skipped and plan the `quenching-align` suggestion.
**Done when:** the governing rule (or its planned creation, or the no-bundle note) is fixed.

### 2. Classify on the axis
Apply the classification test ([references/taxonomy.md](references/taxonomy.md) §axis):
name the one folder the skill acts on — one folder → domain-bound; "the repo" → generic;
several unrelated folders → stop and ask the user which folder it serves (or whether it is
generic) instead of forcing a value. For an **edit**, re-derive the classification and diff
it against the skill's current name. **Done when:** the axis value (and bound folder, if
any) is fixed.

### 3. Derive name, wrapper, and placement
Domain-bound → name = flattened folder path + verb; wrapper at
`.claude/commands/<folder-path>/<verb>.md` → `/<folder>:<subfolder>:<verb>`. Generic →
name = verb-object; flat command or none. `Glob` `.claude/skills/*` and
`.claude/commands/**` for collisions — an existing name is a MERGE target (edit), never
silently overwritten. **Done when:** every path to be written is listed, collision-free or
resolved as an edit.

### 4. Draft under the doctrine
Fill `automation/skill.md` (and `automation/command.md` for the wrapper) per
[references/doctrine.md](references/doctrine.md): description front-loads the leading
concept, one verbatim trigger per branch in the second sentence, `Not for:` boundary;
steps end in checkable **Done when** criteria; every line passes the no-op test;
prescriptions positive; body well under 500 lines; description + `when_to_use` within the
1,536-char cap. For an edit, apply the doctrine to the diff — cure the named failure mode
(sediment, sprawl, negation, …), keep the rest. **Done when:** the draft passes the
doctrine's failure-mode table read top to bottom.

### 5. Present ONE plan → gate on the OK
Show: axis value + bound folder, skill name, every file (skill, wrapper, rule if planned,
registry create-or-regenerate, log), and the tail steps. Wait for the single confirmation.
**Done when:** the user has answered; declined → report "nothing written" and stop.

### 6. Write
Write the `SKILL.md` and the wrapper (wrapper body: one sentence invoking the skill via
the Skill tool with `$ARGUMENTS` — the opsx pattern, mold `automation/command.md`); write
the rule if planned. **Done when:** every planned file exists with its planned content.

### 7. OKF tail (bundle present)
Per [references/taxonomy.md](references/taxonomy.md) §registry: regenerate the registry's
GENERATED zone from all `.claude/skills/*/SKILL.md` frontmatter — creating
`docs/documentation/reference/automation.md` from `automation/registry.md` if absent (it
was in the plan), updating `documentation/reference/`'s `index.md` and appending to
`log.md` (`**Creation**`/`**Update**`: the skill minted/edited) per the procedure in
[../quenching-add/references/homes.md](../quenching-add/references/homes.md). If the
skill coined a new repo-specific term, **offer** ONE `knowledge/glossary.md` entry — the
user decides. **Done when:** zone regenerated, index honest, log appended.

### 8. Self-check
Verify: the GENERATED zone diffs clean against `.claude/skills/*/SKILL.md` (regenerate on
mismatch and report it); the wrapper resolves to the skill it names; the description +
`when_to_use` fit the cap with triggers in the second sentence; the body is under 500
lines; any OKF doc touched passes
[../quenching-align/references/conformance.md](../quenching-align/references/conformance.md).
Report what was written, the invocation (`/…:…:<verb>`), and any residue. **Done when:**
every check passed or its mismatch is reported.

## Invariants

- Never write before the single OK; a declined plan leaves the repo untouched.
- Never delete a skill, and never clobber an existing body — MERGE.
- Never mirror a generic skill under a folder path; never mint a directory-scoped skill
  (accepted variation when found, never generated — taxonomy §mirroring).
- Never hand this SKILL.md `context: fork` — the plan gate is mid-flow.
