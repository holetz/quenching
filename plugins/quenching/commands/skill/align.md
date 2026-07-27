---
description: Migrate this repo's whole .claude command surface — collapse pairs, one file per entry point
argument-hint: [optional-scope]
allowed-tools: Bash(python3:*), Bash(py:*), Bash(git grep:*), Bash(grep:*), Bash(mkdir:*), Bash(mv:*), Bash(cp:*), Read, Grep, Glob, Write, Edit
---

# /skill:align — force the automation surface onto the taxonomy

**Input**: `$ARGUMENTS` (an optional scope; omit to sweep the whole automation surface).

The sweep counterpart of `/skill:new`: where the mint keeps each **new** command
conformant, this one converges everything that **already exists** — including a surface still
built as `skills/<name>/SKILL.md` + a mirrored wrapper, which it **collapses to one file per
entry point** (§5 below). The axis, naming, placement, and registry format live in
[skill-new/taxonomy.md](${CLAUDE_PLUGIN_ROOT}/assets/references/skill-new/taxonomy.md);
the writing doctrine judged against is
[skill-new/doctrine.md](${CLAUDE_PLUGIN_ROOT}/assets/references/skill-new/doctrine.md) —
both owned by the sibling and cited here, never restated. Molds live at
`${CLAUDE_PLUGIN_ROOT}/assets/templates/automation/`.

## Doctrine

The sweep contract every align shares — read-only inventory first, one plan → one OK with
code-coupled items gating individually, the cycle-authorized narration exception, the two-scan
blast-radius procedure, MERGE-never-clobber, never-delete-on-a-guess, and
align-conformance-report-the-cycle — lives once in
[align-all/sweep-doctrine.md](${CLAUDE_PLUGIN_ROOT}/assets/references/align-all/sweep-doctrine.md).
Read it as this skill's doctrine. What follows is only what is **specific to `.claude/`**:

- **The legacy `openspec-*` surface is not this sweep's.** `.claude/skills/openspec-*/` and
  `.claude/commands/opsx/` are legacy CLI artifacts a prior `openspec init` left behind — a
  native `specs/` repo has none. When present they belong to `/specs:align`, which
  removes them when migrating a legacy `openspec/` workspace
  ([specs-align/conformance.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-align/conformance.md)
  §Shadow copies). Inventory them only to **note** them; never classify them onto the axis,
  rename them, or remove them here.
- **A skill body is never rewritten here.** The shared MERGE rule says bodies are preserved;
  on this front that is the whole point — only names, placement, and description/frontmatter
  conformance change. Auditing a body against the writing doctrine is
  `/skill:align-and-update`'s second stage, not this sweep's.
- **The registry ends the run honest.** `skills.py registry reindex` regenerates the GENERATED
  zone from the post-migration surface, and a second run reporting `changed: false` is what
  proves it matches disk; residue is reported, never silently dropped.

## Resolving the tool

Resolve `skills.py` the way the `specs/` front resolves `specs.py`:
`${CLAUDE_PLUGIN_ROOT}/assets/bin/skills.py` first, then a copy installed into the target's
`.claude/hooks/skills.py`, else the declared **manual** fallback — apply the same checks by hand
and **say in the report that the check was manual**, never silently skip it. Invoke with
`python3`/`py`; branch on the **exit code** (0 ok · 1 findings · 2 refusal) and the `--json`,
never on prose.

**This sweep also installs it** (Step 4), so the repo keeps its verifier after the run ends —
one align per front, each installing its own front's tool.

**Every shell grant is scoped**, per
[`docs/standards/automation/skills.md`](../../../../docs/standards/automation/skills.md)
§`allowed-tools` is always scoped: `python3`/`py` for the tool, `git grep` and `grep` for the
blast-radius sweep (Step 2), `mkdir`/`mv`/`cp` for the renames and the two installs. This skill
touches no repo toolchain, so it has no claim to an unscoped `Bash`.

**What the tool decides, and what it does not.** `doctor` and `lint` decide everything mechanical
— a non-empty description on every command, no two resolving to the same `/` path, kebab-case
segments, the caps, trigger position, the `Not for:` boundary, body length, step criteria,
unscoped `Bash`. Neither decides the **axis**: naming the one folder a command acts on is a claim
about what it is *for*, which no parser makes. Classification stays a read.

**Neither does the tool see a legacy pair.** `skills.py` reads `commands/**` and nothing else, so
a leftover `skills/<name>/SKILL.md` is invisible to it — the collapse in §5 is found by `Glob`
and reported by this sweep, never by a `sk-*` code.

## Workflow

### 1. Inventory the surface (read-only)
Ask the tool for the mechanical half — it reads nothing this skill would not, and it reports
what a reader would otherwise have to hold in their head:
```bash
skills.py doctor --json   # descriptions, duplicate / paths, non-canonical segments
skills.py lint --json     # per-command conformance, one sk-* code per gap
```
`Glob` for what the tool cannot see, because it reads only `commands/**`:
`.claude/skills/*/SKILL.md` and directory-scoped `**/.claude/skills/*/SKILL.md`. **Every one of
those is a pair awaiting collapse** — pair each with the wrapper whose body invokes it (the
`quenching:<name>` or bare `<name>` reference), and record a skill with no wrapper, or a
wrapper naming no skill, as an item needing a human decision rather than a mechanical merge.
Set aside every legacy `openspec-*` skill and `opsx/` wrapper — they are `/specs:align`'s
(Doctrine §the legacy `openspec-*` surface); list them as *out of scope, owned by
`/specs:align`* and drop them from the working set, including from the tool's findings.

Then add the half the tool cannot: for each remaining item, the **axis classification** per the
test ([taxonomy](${CLAUDE_PLUGIN_ROOT}/assets/references/skill-new/taxonomy.md) §axis — several unrelated folders
→ unroutable). Read `docs/standards/automation/skills.md` if present — it governs; note whether
the rule and the registry (`docs/documentation/reference/automation.md`) exist, and whether
`docs/index.md` carries `okf_version` (no bundle → rule/registry stay out of scope, migration
still applies).
**Done when:** `doctor` and `lint` have run, the inventory table (item · classification · `sk-*`
gaps) is complete, and no file changed.

### 2. Sweep the blast radius
Run the shared procedure in
[align-all/sweep-doctrine.md](${CLAUDE_PLUGIN_ROOT}/assets/references/align-all/sweep-doctrine.md)
§3 — two repo scans for the whole rename set, never two per rename — over every name slated for
rename or removal: skill names **and** command paths. **A collapse retires a skill name**, so
every site naming it (a conductor invoking it via the Skill tool, a runbook, a registry row) is a
hit the same way a rename is. **This front's delta:** a command path appears in
prose (`/foo:bar` in a README, a runbook, a CI comment) far more often than in code, so a hit
that is only documentation is workspace-internal, while a hit in a script that *invokes* the
command is code-coupled.
**Done when:** each planned rename is marked coupled or free, with its hits.

### 3. Present ONE consolidated plan → gate
One table: **pairs to collapse** (skill + wrapper → the one command file that survives, with
the skill name being retired), renames (old → canonical new, coupled ones marked), commands to
create or rewrite (and wrongly nested generic commands to flatten), rule + registry creations
from the molds when missing (rule born `authority: background`), **the tool**
`.claude/hooks/skills.py`
(install / upgrade / leave — Step 4), the operator manual
`.claude/QUENCHING.md` (install / refresh / leave), unroutables kept-and-reported
with reasons, obsolete-suspect flags (no deletion proposed without the human's word).
Wait for the single confirmation; code-coupled items each await their own.
**Done when:** the user has answered; declined → nothing written, run ends.

### 4. Apply
Execute the confirmed plan: **collapse each pair per §5**, rename command paths, create/rewrite
commands from `automation/command.md`, fix frontmatter gaps per the doctrine (description within
the cap, triggers second sentence — bodies untouched), write rule and registry from their molds
when planned, update each code-coupled reference site alongside its individually confirmed
rename.

**Install the front's tool**, so the repo keeps its verifier after this run ends: copy
**exactly** `${CLAUDE_PLUGIN_ROOT}/assets/bin/skills.py` into the target's `.claude/hooks/`
(never the directory recursively). If a copy is **already installed**, compare its version
(`python3 .claude/hooks/skills.py --version`) with the plugin's `VERSION` file and overwrite
**only** when the plugin is newer — the same rule `/specs:align` applies to `specs.py`
and `/docs:align` to `okf-validate.py`. A newer installed copy is left alone and
reported: it means the target is ahead of this plugin, which is a fact to state, not a
regression to force.

Then install the operator manual from
`${CLAUDE_PLUGIN_ROOT}/assets/claude/QUENCHING.md` to `.claude/QUENCHING.md` under the
four-branch manual-install rule in
[/docs:align](${CLAUDE_PLUGIN_ROOT}/commands/docs/align.md) §4 (cited, never restated).
**Done when:** every confirmed row is applied, and `.claude/hooks/skills.py` is present at a
version at least the plugin's (or its being newer is reported).

### 5. Collapse each confirmed pair — the merge, key by key
For every `skills/<name>/SKILL.md` paired with a wrapper in §1, the surviving file is the
**wrapper's path**, so nothing a human types today changes. Frontmatter is a merge with one rule
per key, not a judgement call:

| Key | Source | Why |
| --- | --- | --- |
| `description` | the **wrapper's** | already reviewed for the `/` menu; deleting the skill's is the whole saving |
| `argument-hint` | the wrapper's | wrappers carry it; skills never did |
| `allowed-tools` | the **skill's** | the scoped grant the body needs; wrappers declare none |
| `effort` | the skill's | carried through unchanged |
| `name` | **dropped** | the command path IS the name now |
| `when_to_use` | **dropped** | restates the description's first clause |
| `user-invocable` | **dropped** | it exists to hide a skill behind a wrapper; there is no wrapper left |

The body is the **skill's, moved verbatim** — retitle its `# <skill-name> — …` heading to
`# /<command:path> — …` and fold the wrapper's `$ARGUMENTS` sentence in as the input contract.
No other edit: judging what a body *says* is `/skill:align-and-update`'s, and mixing it in makes
the migration diff unreviewable.

Then **re-home what sat beside the skill.** A `references/` folder cannot follow the body into
`commands/`, where it would register as a phantom command — move it outside (in a target repo,
`.claude/references/<name>/`) and rewrite every citation to that absolute path. Same for `evals/`.
Delete `skills/<name>/` only once its body is in place and its neighbours are re-homed.

**A pair that is not a clean pair is reported, never guessed:** a skill with no wrapper needs a
path chosen (a human decision), and a wrapper naming no skill has no body to take.
**Done when:** every confirmed pair is one file, `skills/` holds nothing that was migrated, and
every unclean pair is listed with what it needs.

### 6. Verify and report
Regenerate the zone, then let the tool judge the surface the migration produced:
```bash
skills.py registry reindex --json   # the zone, from the post-migration surface
skills.py doctor --json             # the surface invariant the migration just changed
skills.py lint --json               # the gaps the migration was supposed to close
skills.py registry reindex --json   # `changed: false` — the zone now matches disk
```
Every renamed reference site greps clean, and no citation still points into a deleted
`skills/` tree. In an OKF repo, append ONE consolidated `log.md` entry (the migration, with
counts) and confirm the registry is indexed, per
[docs-add/homes.md](${CLAUDE_PLUGIN_ROOT}/assets/references/docs-add/homes.md).
Report: collapsed / renamed / created / flattened / rule+registry created / unroutable /
flagged, and every `sk-*` finding that survived the run, by code. **Done when:** `doctor` and
`lint` exit 0 or each surviving finding is named with its code, the second `registry reindex`
reports `changed: false`, and the counts are reported.

## Invariants

- Never modify anything before the plan's OK; a code-coupled rename never rides the batch. A
  cycle-authorized run replaces only the batch gate with narration — never a code-coupled
  item's own OK.
- Never rename, reclassify, or remove a legacy `openspec-*` skill or an `opsx/` wrapper — that
  surface is `/specs:align`'s; note it and move on.
- Never alter a body's prose — only its title line, its input contract, its citation paths,
  its placement, and its frontmatter conformance. A collapse MOVES a body; it never edits it.
- Never delete a command without the human stating it is obsolete; never force an
  unroutable item onto the axis. Deleting a `skills/<name>/` folder whose body has just been
  moved into its command file is not a deletion in this sense — nothing is lost — but it
  happens only after the move is in place.
- Never write anything but an entry point under `commands/`: a `references/` or `evals/`
  folder moved there would register every file in it as a phantom command.
- Never leave the GENERATED zone stale, and never write inside its markers by hand — the run
  ends on a `registry reindex` that reports `changed: false`.
- Never overwrite a `.claude/QUENCHING.md` whose `quenching` banner a human removed —
  keep it and report it.
- Never hand this command file `context: fork` — both gates are mid-flow.
