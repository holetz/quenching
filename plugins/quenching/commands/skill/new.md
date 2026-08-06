---
description: Mint or edit ONE command in this repo's .claude surface — one file per entry point. Triggers on "create a command", "mint a command for X", "add a new entry point to the .claude surface". Not for: a subagent definition → /skill:agent:new; a hook → /skill:hook:new; measuring a command → /skill:eval.
argument-hint: [skill-name-or-description]
allowed-tools: Bash(python3:*), Bash(py:*), Read, Grep, Glob, Write, Edit
---

# /quenching:skill:new — mint ONE conformant command, registry included

**Input**: `$ARGUMENTS` (the command to create or edit — a name or a description of what it should do).

Creates or edits **ONE FILE** in the **target repo's own** automation surface — a
`.claude/commands/<path>.md` carrying both the description that routes to it and the body that
runs. Claude Code merged commands into skills, so there is no `SKILL.md` half and no wrapper to
mirror: the command's path IS its identity, and the surface stays predictable because that path
tells where the command acts. The axis, naming, and registry format live in
[skill-new/taxonomy.md](${CLAUDE_PLUGIN_ROOT}/assets/references/skill-new/taxonomy.md); how the
body itself is written lives in [skill-new/doctrine.md](${CLAUDE_PLUGIN_ROOT}/assets/references/skill-new/doctrine.md);
what a command may strategically use — fork, pins, hooks, the invocation controls — and what
each lever costs lives in
[skill-new/capabilities.md](${CLAUDE_PLUGIN_ROOT}/assets/references/skill-new/capabilities.md) —
this skill owns all three, and `/quenching:skill:align` cites them. Molds live at
`${CLAUDE_PLUGIN_ROOT}/assets/templates/automation/`.

## Doctrine

- **The rule governs; the plan proposes.** In a target repo the taxonomy rule is
  `/.docs/standards/automation/skills.md` — read it before classifying and follow it when
  present (a repo-specific delta there beats the plugin default). Absent + OKF bundle
  present → the plan offers creating it from the mold, born `authority: background`;
  never created without the OK.
- **No bundle, no tail — but the mint proceeds.** `/.docs/index.md` without `okf_version`
  (or absent) means: write the command file only, skip registry/glossary/log silently, and
  suggest `/quenching:docs:align` **once**.
- **One plan, one OK, nothing before.** Classification, names, every file to be written,
  and the OKF tail appear in ONE plan; no file is created or modified before the single
  confirmation. A declined plan writes nothing.
- **MERGE, never clobber.** An edit preserves the skill's body and any hand-written
  content; only the gap being fixed changes. This skill never deletes a skill.
- **The registry zone is regenerated, never composed.** `skills.py registry reindex` owns the
  zone's format; this skill and `/quenching:skill:align` are the two that invoke it, and neither
  writes between the markers by hand. Composing a derived table and then diffing it against its
  own source is one reader checking its own arithmetic.

## Resolving the tool

Resolve `skills.py` per
[align/tool-resolution.md](${CLAUDE_PLUGIN_ROOT}/assets/references/align/tool-resolution.md)
§Resolving the tool §Write the resolved path literally on every invocation; branch on the
**exit code** (0 ok · 1 findings · 2 refusal) and the `--json`, never on prose. Findings carry
`sk-*` codes: an `error` is fixed, a `warn` is reported with its code.

## Workflow

### 1. Read the rule
Read `/.docs/standards/automation/skills.md` and confirm the bundle
(`/.docs/index.md` carries `okf_version`). Rule present → it governs. Rule absent, bundle
present → add "create the rule from `automation/skills-standard.md`" to the plan. No
bundle → note the tail as skipped and plan the `/quenching:docs:align` suggestion.
**Done when:** the governing rule (or its planned creation, or the no-bundle note) is fixed.

### 2. Classify on the axis
Apply the classification test ([skill-new/taxonomy.md](${CLAUDE_PLUGIN_ROOT}/assets/references/skill-new/taxonomy.md) §The single axis):
name the one folder the skill acts on — one folder → domain-bound; "the repo" → generic;
several unrelated folders → stop and ask the user which folder it serves (or whether it is
generic) instead of forcing a value. For an **edit**, re-derive the classification and diff
it against the skill's current name. **Done when:** the axis value (and bound folder, if
any) is fixed.

### 3. Derive the path — which is the name
Domain-bound → `.claude/commands/<folder-path>/<verb>.md` → `/<folder>:<subfolder>:<verb>`.
Generic → a flat `.claude/commands/<verb-object>.md`. There is no second name to derive: the
path is it. `Glob` `.claude/commands/**` for collisions — an existing path is a MERGE target
(edit), never silently overwritten. Nothing but entry points goes under `commands/`: shared
procedure lives outside it and is cited by absolute path, because a file parked there registers
as a phantom command (`sk-no-description`). **Done when:** the path to be written is fixed,
collision-free or resolved as an edit.

### 4. Choose the execution profile
Walk [skill-new/capabilities.md](${CLAUDE_PLUGIN_ROOT}/assets/references/skill-new/capabilities.md):
the default profile is **all levers off**, and each departure needs a stated buy — `context:
fork` (+ `agent`, `background`) only for a self-contained, noisy, summary-out run with **no
mid-flow gate**; an `effort`/`model` pin only for genuinely mechanical work, priced against
the cache it invalidates inline; `paths` to bind a domain-bound command's autonomous firing
to its folder; `disable-model-invocation` only for a human-must-choose command (it also
removes the description from always-on context entirely); frontmatter `hooks:` only for a check
tied to this command's own workflow. For an **edit**, re-derive the profile and flag any
lever whose original buy no longer holds. **Done when:** each non-default lever is listed
with its one-line reason — or the profile is stated as default.

### 5. Draft under the doctrine
Fill `automation/command.md` per
[skill-new/doctrine.md](${CLAUDE_PLUGIN_ROOT}/assets/references/skill-new/doctrine.md): description front-loads the leading
concept, one verbatim trigger per branch in the second sentence, `Not for:` boundary;
steps end in checkable **Done when** criteria; every line passes the no-op test;
prescriptions positive; body well under 500 lines; the description within the 1,536-char cap.
The description is the **only** always-on text there is — its triggers and its boundary are what
route a spoken request here, so a description trimmed to a `/`-menu label routes nothing. For an edit, apply the doctrine to the diff — cure the named failure mode
(sediment, sprawl, negation, …), keep the rest. **Done when:** the draft passes the
doctrine's failure-mode table read top to bottom.

### 6. Present ONE plan → gate on the OK
Show: axis value + bound folder, the command path, **the execution profile** (each
non-default lever with its reason, or "default"), every file (the command, rule if planned,
registry create-or-regenerate, log), and the tail steps. Wait for the single confirmation.
**Done when:** the user has answered; declined → report "nothing written" and stop.

### 7. Write
Write the command file from `automation/command.md` — frontmatter and body in the one file;
write the rule if planned. **Done when:** every planned file exists with its planned content.

### 8. OKF tail (bundle present)
Create `/.docs/documentation/reference/automation.md` from `automation/registry.md` first if it is
absent (it was in the plan) — `registry reindex` refuses a missing doc (`sk-no-registry`) or a
doc with no markers (`sk-no-zone`) rather than placing a table at a guessed anchor in curated
prose. Then regenerate the zone:
```bash
skills.py registry reindex --json
```
Update `documentation/reference/`'s `index.md` per the procedure in
[docs-add/homes.md](${CLAUDE_PLUGIN_ROOT}/assets/references/docs-add/homes.md). If the
command coined a new repo-specific term, **offer** ONE `knowledge/glossary.md` entry — the user
decides. **Done when:** `registry reindex` exits 0 and the index is honest.

### 9. Self-check
Ask the tool, do not read for it:
```bash
skills.py lint <command-file> --json   # this command's conformance
skills.py doctor --json                # the surface invariant it just changed
skills.py registry reindex --json      # `changed: false` — nothing wrote inside the markers after step 8
```
`lint` decides the description caps, trigger position, the `Not for:` boundary, body length, the
per-step criteria, unscoped `Bash`, and invocation coherence; `doctor` decides that every command
carries a description, that no two resolve to the same `/` path, and that every segment is
kebab-case. Fix every `error`; report every `warn`
with its `sk-*` code rather than silently accepting it. What no parser can decide — the no-op
test, sediment, sprawl, positive prescription — is still read by eye against
[skill-new/doctrine.md](${CLAUDE_PLUGIN_ROOT}/assets/references/skill-new/doctrine.md). Any OKF doc touched passes
[docs-align/conformance.md](${CLAUDE_PLUGIN_ROOT}/assets/references/docs-align/conformance.md).
**None of that proves the command LOADS.** `lint` and `doctor` read frontmatter off disk, and disk
is not the registry — which is built at **session start**, so the command just written is not
invocable until a new process. Every mechanical check above can be green while the body is
unreachable, a `${CLAUDE_PLUGIN_ROOT}` placeholder never expands, or a citation points at nothing.

So this step, not a later one, owns the functional proof: **where the repo ships a harness that
spawns a fresh session and asserts on captured tool calls, run it now** — scoped to what this mint
changed, since each check is a billed session. In this plugin that is
`assets/checks/functional-checks.sh` (default subset for a body; `/quenching:skill:eval` for a description).
**Where the repo ships none, say plainly that the command is written but unproven until a fresh
session** — never report a linter's exit 0 as evidence that the surface loaded.

Report what was written, the invocation (`/…:…:<verb>`), the functional result or its absence, and
any residue. **Done when:** `lint` and `doctor` exit 0, `registry reindex` reports `changed: false`,
the surface was either functionally proved or reported unproven, and every remaining `warn` is
named in the report with its code.

## Invariants

- Never write before the single OK; a declined plan leaves the repo untouched.
- Never delete a command, and never clobber an existing body — MERGE.
- Never path a generic command under a folder; never mint a directory-scoped surface
  (accepted variation when found, never generated — taxonomy §placement).
- Never write anything but an entry point under `commands/` — shared procedure, references and
  fixtures live outside it and are cited by absolute path.
- Never hand this command file `context: fork` — the plan gate is mid-flow.
