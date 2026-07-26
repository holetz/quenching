---
name: quenching-skill-new
description: >-
  Mints or edits ONE Claude Code skill in a target repo's local automation surface
  (.claude/skills/ + .claude/commands/) — classified on the single taxonomy axis
  (domain-bound × generic), canonically named, mirrored by a thin command wrapper when
  domain-bound, written under the skill-writing doctrine, with the derived OKF artifacts
  regenerated in the tail. Use when the user asks to "create a
  skill", "mint a skill for X", "add a new skill", "organize this skill", "make this
  skill conform", or "wire a command for this skill". Reads the taxonomy rule
  (docs/standards/automation/skills.md; offers to create it from the template on first
  run), presents ONE plan, writes on a single
  OK, then self-checks with skills.py lint + doctor. Without an OKF bundle the mint still
  proceeds (skill + wrapper only), the tail is skipped, and quenching-docs-align is suggested
  once. Not for: migrating the existing skills to the taxonomy → quenching-skill-align; a
  doc into the docs/ bundle → quenching-docs-add.
when_to_use: >-
  minting or editing ONE conformant skill (+ mirrored command wrapper) in a target repo.
allowed-tools: Bash(python3:*), Bash(py:*), Read, Grep, Glob, Write, Edit
user-invocable: false
---

# quenching-skill-new — mint ONE conformant skill, wrapper and registry included

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
  suggest `quenching-docs-align` **once**.
- **One plan, one OK, nothing before.** Classification, names, every file to be written,
  and the OKF tail appear in ONE plan; no file is created or modified before the single
  confirmation. A declined plan writes nothing.
- **MERGE, never clobber.** An edit preserves the skill's body and any hand-written
  content; only the gap being fixed changes. This skill never deletes a skill.
- **The registry zone is regenerated, never composed.** `skills.py registry reindex` owns the
  zone's format; this skill and `quenching-skill-align` are the two that invoke it, and neither
  writes between the markers by hand. Composing a derived table and then diffing it against its
  own source is one reader checking its own arithmetic.

## Resolving the tool

Resolve `skills.py` the way the `specs/` front resolves `specs.py`:
`${CLAUDE_PLUGIN_ROOT}/assets/bin/skills.py` first, then a copy installed into the target's
`.claude/hooks/skills.py`, else the declared **manual** fallback — apply the same checks by hand
and **say in the report that the check was manual**, never silently skip it. Invoke with
`python3`/`py`; branch on the **exit code** (0 ok · 1 findings · 2 refusal) and the `--json`,
never on prose. Findings carry `sk-*` codes: an `error` is fixed, a `warn` is reported with its
code.

## Workflow

### 1. Read the rule
Read `docs/standards/automation/skills.md` and confirm the bundle
(`docs/index.md` carries `okf_version`). Rule present → it governs. Rule absent, bundle
present → add "create the rule from `automation/skills-standard.md`" to the plan. No
bundle → note the tail as skipped and plan the `quenching-docs-align` suggestion.
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
the Skill tool with `$ARGUMENTS` — the wrapper pattern, mold `automation/command.md`); write
the rule if planned. **Done when:** every planned file exists with its planned content.

### 7. OKF tail (bundle present)
Create `docs/documentation/reference/automation.md` from `automation/registry.md` first if it is
absent (it was in the plan) — `registry reindex` refuses a missing doc (`sk-no-registry`) or a
doc with no markers (`sk-no-zone`) rather than placing a table at a guessed anchor in curated
prose. Then regenerate the zone:
```bash
skills.py registry reindex --json
```
Update `documentation/reference/`'s `index.md` and append to `log.md`
(`**Creation**`/`**Update**`: the skill minted/edited) per the procedure in
[../quenching-docs-add/references/homes.md](../quenching-docs-add/references/homes.md). If the
skill coined a new repo-specific term, **offer** ONE `knowledge/glossary.md` entry — the user
decides. **Done when:** `registry reindex` exits 0, the index is honest, and the log is appended.

### 8. Self-check
Ask the tool, do not read for it:
```bash
skills.py lint <skills-dir> --json     # this skill's conformance
skills.py doctor --json                # the bijection it just changed
skills.py registry reindex --json      # `changed: false` — nothing wrote inside the markers after step 7
```
`lint` decides the description caps, trigger position, the `Not for:` boundary, body length, the
per-step criteria, unscoped `Bash`, and invocation coherence; `doctor` decides that the wrapper
resolves to this skill and that nothing else claims it. Fix every `error`; report every `warn`
with its `sk-*` code rather than silently accepting it. What no parser can decide — the no-op
test, sediment, sprawl, positive prescription — is still read by eye against
[references/doctrine.md](references/doctrine.md). Any OKF doc touched passes
[../quenching-docs-align/references/conformance.md](../quenching-docs-align/references/conformance.md).
Report what was written, the invocation (`/…:…:<verb>`), and any residue. **Done when:** `lint`
and `doctor` exit 0, `registry reindex` reports `changed: false`, and every remaining `warn` is
named in the report with its code.

## Invariants

- Never write before the single OK; a declined plan leaves the repo untouched.
- Never delete a skill, and never clobber an existing body — MERGE.
- Never mirror a generic skill under a folder path; never mint a directory-scoped skill
  (accepted variation when found, never generated — taxonomy §mirroring).
- Never hand this SKILL.md `context: fork` — the plan gate is mid-flow.
