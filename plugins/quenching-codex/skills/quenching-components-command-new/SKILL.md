---
name: quenching-components-command-new
description: "Mint or edit ONE command in this repo's .claude surface — one file per entry point. Triggers on \"create a command\", \"mint a command for X\", \"add a new entry point to the .claude surface\". Not for: a subagent definition → quenching-components-agent-new; a hook → quenching-components-hook-new; measuring a command → quenching-components-command-eval."
---

<!-- GENERATED FROM plugins/quenching/commands/components/command/new.md -->


# quenching-components-command-new — mint ONE conformant command, registry included

**Input**: `$ARGUMENTS` (the command to create or edit — a name or a description of what it should do).

Creates or edits **ONE FILE** in the **target repo's own** automation surface — a
`.agents/skills/<path>.md` carrying both the description that routes to it and the body that
runs. Codex merged commands into skills, so there is no `SKILL.md` half and no wrapper to
mirror: the command's path IS its identity, and the surface stays predictable because that path
tells where the command acts. The axis, naming, and registry format live in
[components-command-new/taxonomy.md](../../references/components-command-new/taxonomy.md); how the
body itself is written lives in [components-command-new/doctrine.md](../../references/components-command-new/doctrine.md);
what a command may strategically use — fork, pins, hooks, the invocation controls — and what
each lever costs lives in
[components-command-new/capabilities.md](../../references/components-command-new/capabilities.md) —
this skill owns all three, and `quenching-components-align` cites them. Molds live at
`../../templates/automation/`.

## Doctrine

- **The rule governs; the plan proposes.** In a target repo the taxonomy rule is
  `/.knowledge/standards/automation/skills.md` — read it before classifying and follow it when
  present (a repo-specific delta there beats the plugin default). Absent + OKF bundle
  present → the plan offers creating it from the mold, born `authority: background`;
  never created without the OK.
- **No bundle, no tail — but the mint proceeds.** `/.knowledge/index.md` without `okf_version`
  (or absent) means: write the command file only, skip registry/glossary/log silently, and
  suggest `quenching-knowledge-align` **once**.
- **One plan, one OK, nothing before.** Classification, names, every file to be written,
  and the OKF tail appear in ONE plan; no file is created or modified before the single
  confirmation. A declined plan writes nothing.
- **MERGE, never clobber.** An edit preserves the skill's body and any hand-written
  content; only the gap being fixed changes. This skill never deletes a skill.
- **The registry zone is regenerated, never composed.** `cq components registry reindex` owns the
  zone's format; this skill and `quenching-components-align` are the two that invoke it, and neither
  writes between the markers by hand. Composing a derived table and then diffing it against its
  own source is one reader checking its own arithmetic.

## Resolving the tool

Resolve `cq components` per
[align/tool-resolution.md](../../references/align/tool-resolution.md)
§Resolving the tool §Write the resolved path literally on every invocation; branch on the
**exit code** (0 ok · 1 findings · 2 refusal) and the `--json`, never on prose. Findings carry
`sk-*` codes: an `error` is fixed, a `warn` is reported with its code.

## Workflow

### 1. Read the rule
Read `/.knowledge/standards/automation/skills.md` and confirm the bundle
(`/.knowledge/index.md` carries `okf_version`). Rule present → it governs. Rule absent, bundle
present → add "create the rule from `automation/skills-standard.md`" to the plan. No
bundle → note the tail as skipped and plan the `quenching-knowledge-align` suggestion.
**Done when:** the governing rule (or its planned creation, or the no-bundle note) is fixed.

### 2. Classify — category first, then the axis
Apply the classification test ([components-command-new/taxonomy.md](../../references/components-command-new/taxonomy.md) §The single axis) in order:

- **Category/subject.** `Glob` `.agents/skills/*/` for the top-level names already in use in
  this repo target, and ask which one this command belongs to (`git`, `deploy`, `tests`, ...) —
  offering the existing names, and free text for a new one. No clean, evident subject → there is
  no category; the rest of this step runs exactly as before this rule.
- **The axis.** Name the one folder the command acts on — one folder → domain-bound; "the repo"
  → generic; several unrelated folders → stop and ask the user which folder it serves (or
  whether it is generic) instead of forcing a value.
- **Nest vs replace, only with both a category and a bound folder.** Read the convention already
  established for this category in this repo (taxonomy.md §Reading the nest-vs-replace
  convention): `Glob` `.agents/skills/<categoria>/**` and infer **nest** (a real-folder subpath
  already present) or **replace** (files already sitting flat) from what is already there.
  Nothing there yet, or the two shapes are mixed → ask the human once — the first command minted
  under that answer becomes the convention for every later command of the same category in this
  repo, with nothing else recorded.

For an **edit**, re-derive category, axis and (if both apply) the nest-vs-replace read, and diff
them against the command's current path. **Done when:** the category (or its absence), the axis
value and bound folder (if any), and the nest-vs-replace read (if it applies) are fixed.

### 3. Derive the path — which is the name
No category: domain-bound → `.agents/skills/<folder-path>/<verb>.md` →
`/<folder>:<subfolder>:<verb>`; generic → a flat `.agents/skills/<verb-object>.md`. Category, no
bound folder, or the convention reads **replace** → `.agents/skills/<categoria>/<verb>.md` →
`/<categoria>:<verb>`. Category, bound folder, convention reads **nest** →
`.agents/skills/<categoria>/<folder-path>/<verb>.md` → `/<categoria>:<subfolder>:<verb>`. There
is no second name to derive: the path is it. `Glob` `.agents/skills/**` for collisions — an
existing path is a MERGE target (edit), never silently overwritten. Nothing but entry points goes
under `commands/`: shared procedure lives outside it and is cited by absolute path, because a file
parked there registers as a phantom command (`sk-no-description`). **Done when:** the path to be
written is fixed, collision-free or resolved as an edit.

### 4. Choose the execution profile
Walk [components-command-new/capabilities.md](../../references/components-command-new/capabilities.md):
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
[components-command-new/doctrine.md](../../references/components-command-new/doctrine.md): description front-loads the leading
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
Create `/.knowledge/documentation/reference/automation.md` from `automation/registry.md` first if it is
absent (it was in the plan) — `registry reindex` refuses a missing doc (`sk-no-registry`) or a
doc with no markers (`sk-no-zone`) rather than placing a table at a guessed anchor in curated
prose. Then regenerate the zone:
```bash
python3 "$(find "${CODEX_HOME:-$HOME/.codex}" "$HOME/.codex" -type f -path '*/quenching-codex*/scripts/cq' -print -quit 2>/dev/null)" components registry reindex --json
```
Update `documentation/reference/`'s `index.md` per the procedure in
[knowledge-add/homes.md](../../references/knowledge-add/homes.md). If the
command coined a new repo-specific term, **offer** ONE `glossary.md` entry — the user
decides. **Done when:** `registry reindex` exits 0 and the index is honest.

### 9. Self-check
Ask the tool, do not read for it:
```bash
python3 "$(find "${CODEX_HOME:-$HOME/.codex}" "$HOME/.codex" -type f -path '*/quenching-codex*/scripts/cq' -print -quit 2>/dev/null)" components lint <command-file> --json   # this command's conformance
python3 "$(find "${CODEX_HOME:-$HOME/.codex}" "$HOME/.codex" -type f -path '*/quenching-codex*/scripts/cq' -print -quit 2>/dev/null)" components doctor --json                # the surface invariant it just changed
python3 "$(find "${CODEX_HOME:-$HOME/.codex}" "$HOME/.codex" -type f -path '*/quenching-codex*/scripts/cq' -print -quit 2>/dev/null)" components registry reindex --json      # `changed: false` — nothing wrote inside the markers after step 8
```
`lint` decides the description caps, trigger position, the `Not for:` boundary, body length, the
per-step criteria, unscoped `Bash`, and invocation coherence; `doctor` decides that every command
carries a description, that no two resolve to the same `/` path, and that every segment is
kebab-case. Fix every `error`; report every `warn`
with its `sk-*` code rather than silently accepting it. What no parser can decide — the no-op
test, sediment, sprawl, positive prescription — is still read by eye against
[components-command-new/doctrine.md](../../references/components-command-new/doctrine.md). Any OKF doc touched passes
[knowledge-align/conformance.md](../../references/knowledge-align/conformance.md).
**None of that proves the command LOADS.** `lint` and `doctor` read frontmatter off disk, and disk
is not the registry — which is built at **session start**, so the command just written is not
invocable until a new process. Every mechanical check above can be green while the body is
unreachable, a `../..` placeholder never expands, or a citation points at nothing.

So this step, not a later one, owns the functional proof: **where the repo ships a harness that
spawns a fresh session and asserts on captured tool calls, run it now** — scoped to what this mint
changed, since each check is a billed session. In this plugin that is
`assets/checks/functional-checks.sh` (default subset for a body; `quenching-components-command-eval` for a description).
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
