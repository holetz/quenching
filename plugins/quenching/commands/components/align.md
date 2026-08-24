---
description: Converge this repo's whole .claude command surface onto one file per entry point, then audit every body and rewrite every description against the writing doctrine. Triggers on "align the skills", "align and update the skills", "migrate my commands", "fix the .claude surface", "collapse the skill wrappers", "audit the command bodies", "review the skill descriptions", "shorten the descriptions", "converge the automation surface". A body is reported with the /quenching:components:command:new that fixes it, never rewritten; a description is rewritten in ONE surface-wide pass on its own confirmation. Not for: minting one command → /quenching:components:command:new; changing a body → that command's own confirmation.
argument-hint: [optional-scope]
allowed-tools: Bash(python3:*), Bash(py:*), Bash(git grep:*), Bash(grep:*), Bash(mkdir:*), Bash(mv:*), Bash(rm:*), Read, Grep, Glob, Write, Edit, Task
---

# /quenching:components:align — force the automation surface onto the taxonomy

**Input**: `$ARGUMENTS` (an optional scope; omit to sweep the whole automation surface).

The sweep counterpart of `/quenching:components:command:new`: where the mint keeps each **new** command
conformant, this one converges everything that **already exists** — including a surface still
built as `skills/<name>/SKILL.md` + a mirrored wrapper, which it **collapses to one file per
entry point** (§6 below) — then **reads every surviving body against the writing doctrine** (§7)
and **reviews every description against it in one surface-wide pass** (§8).

The axis, naming, placement, and registry format live in
[components-command-new/taxonomy.md](${CLAUDE_PLUGIN_ROOT}/assets/references/components-command-new/taxonomy.md);
the writing doctrine judged against is
[components-command-new/doctrine.md](${CLAUDE_PLUGIN_ROOT}/assets/references/components-command-new/doctrine.md);
the capability levers the wider inventory reads against are
[components-command-new/capabilities.md](${CLAUDE_PLUGIN_ROOT}/assets/references/components-command-new/capabilities.md).
Molds live at
`${CLAUDE_PLUGIN_ROOT}/assets/templates/automation/`.

## Doctrine

Read [align/sweep-doctrine.md](${CLAUDE_PLUGIN_ROOT}/assets/references/align/sweep-doctrine.md) as
this skill's doctrine. What follows is specific to `.claude/`:

- **The legacy `openspec-*` surface is not this sweep's.** `.claude/skills/openspec-*/` and
  `.claude/commands/opsx/` are legacy CLI artifacts a prior `openspec init` left behind — a
  native `/.specs/` repo has none. When present they belong to `/quenching:specs:align`, which
  removes them when migrating a legacy `openspec/` workspace
  ([specs-align/conformance.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-align/conformance.md)
  §Finding policy). Inventory them only to **note** them; never classify them onto the axis,
  rename them, or remove them here.
- **The wider `.claude/` is inventoried, never migrated.** `.claude/agents/*.md` and the
  hooks wired in `settings.json` and in command frontmatter are **report-only** surfaces:
  the tool names their findings (`sk-agent-*`, `sk-hook-*`) and each is routed to the mint
  that owns it (`/quenching:components:agent:new`, `/quenching:components:hook:new`).
- **Codex translation drift is reported, never repaired here.** When this checkout carries the
  generated Codex sibling, `cq components translate --check --json` names every divergent file
  with `ct-translation-drift`. The align report includes those findings and routes the repair to
  `cq components translate --write`; this sweep does not overwrite a generated surface while
  aligning the Claude command taxonomy.

## Resolving the tool

Resolve `cq components` per
[align/tool-resolution.md](${CLAUDE_PLUGIN_ROOT}/assets/references/align/tool-resolution.md)
§Resolving the tool §Write the resolved path literally on every invocation; branch on the
**exit code** (0 ok · 1 findings · 2 refusal) and the `--json`, never on prose.

**Every shell grant is scoped**, per `/.knowledge/standards/automation/skills.md`
§`allowed-tools` is always scoped: `python3`/`py` for the tool, `git grep` and `grep` for the
blast-radius sweep (§3), `mkdir`/`mv` for the renames, `rm` for a
confirmed legacy tool copy.

**What the tool decides, and what it does not.** `doctor` and `lint` decide everything mechanical
— a non-empty description on every command, no two resolving to the same `/` path, kebab-case
segments, the caps, trigger position, the `Not for:` boundary, body length, step criteria,
unscoped `Bash`. Neither decides the **axis**: naming the one folder a command acts on is a claim
about what it is *for*, which no parser makes. Classification stays a read.

## Workflow (probe → ONE OK → migrate → audit → re-probe)

### 1. Probe — the checks that decide whether anything else runs
Before any inventory, ask the tool whether there is work at all:
```bash
cq components doctor --json
cq components lint --json
cq components translate --check --json
```
plus one `Glob` for the legacy pairs the tool cannot see (below). Branch as
[sweep-doctrine](${CLAUDE_PLUGIN_ROOT}/assets/references/align/sweep-doctrine.md) §1. Probe before the inventory prescribes:

| Probe result | What happens |
| --- | --- |
| both exit 0 with no findings, no translation drift, and no legacy pair | **STOP.** Report "`.claude/` conformant, N commands, nothing to align" and end. No inventory, no plan, no confirmation. |
| both exit 0 and the only findings are the report-only wider surface (`sk-agent-*`, `sk-hook-*`) | STOP the same way, then list them with the mint that closes each. Nothing here is this sweep's to write. |
| the only findings are description codes (`sk-metadata-cap`, `sk-description-portable`, `sk-trigger-position`, `sk-no-boundary`) | **Skip to §8.** There is nothing to migrate, and an inventory, a plan and a confirmation for zero renames is ceremony — §8 carries its own gate. |
| translation reports `ct-translation-drift` only | Report every divergent path and route to `cq components translate --write`; continue no migration for it. |
| anything else exits 1 or 2, or a legacy pair exists | Continue to step 2. |

An **empty** surface (no commands, no skills) also stops. Note whether an OKF bundle exists
(`/.knowledge/index.md` with `okf_version`) and say so once
— without one the rule and registry stay out of scope, while the migration still applies.

**Done when:** the three payloads and the glob are in hand, and the run has either stopped,
committed to a full sweep, or entered §8 directly.

### 2. Inventory the surface (read-only)
`Glob` for legacy pairs:
`.claude/skills/*/SKILL.md` and directory-scoped `**/.claude/skills/*/SKILL.md`. **Every one of
those is a pair awaiting collapse** — pair each with the wrapper whose body invokes it (the
`quenching:<name>` or bare `<name>` reference), and record a skill with no wrapper, or a
wrapper naming no skill, as an item needing a human decision rather than a mechanical merge.
Set aside every legacy `openspec-*` skill and `opsx/` wrapper — they are `/quenching:specs:align`'s
(Doctrine §the legacy `openspec-*` surface); list them as *out of scope, owned by
`/quenching:specs:align`* and drop them from the working set, including from the tool's findings.

For each remaining item, make the **axis classification** per the
test ([taxonomy](${CLAUDE_PLUGIN_ROOT}/assets/references/components-command-new/taxonomy.md) §The single axis — several unrelated folders
→ unroutable). Read `/.knowledge/standards/automation/skills.md` if present — it governs; note whether
the rule and the registry (`/.knowledge/documentation/reference/automation.md`) exist.

**Where an item classifies with an evident category, also read the nest-vs-replace convention**
already established for that category in this repo (taxonomy.md §Reading the nest-vs-replace
convention): `Glob` `.claude/commands/<categoria>/**` and infer it from what already sits there.
Derive the canonical path the classification produces and diff it against the item's current
path — a mismatch is a relocation candidate, fed into §4's existing renames row like any other,
never a new plan section or a new confirmation of its own.

**A category whose convention is not readable yields no candidate.** Nothing under
`.claude/commands/<categoria>/` yet, or the two shapes already mixed, means there is no
established convention to diverge from — record the item's classification and move on.
**Done when:** the inventory table (item · classification · canonical path if it diverges ·
`sk-*` gap) covers every item in the working set, and no file changed.

### 3. Sweep the blast radius
Run the shared procedure in
[align/sweep-doctrine.md](${CLAUDE_PLUGIN_ROOT}/assets/references/align/sweep-doctrine.md)
§4. The blast-radius sweep — two repo scans for the whole set, never two per rename — over every name slated for
rename or removal: skill names **and** command paths. **A collapse retires a skill name**, so
every site naming it (a conductor invoking it via the Skill tool, a runbook, a registry row) is a
hit the same way a rename is. **This front's delta:** a command path appears in
prose (`/foo:bar` in a README, a runbook, a CI comment) far more often than in code, so a hit
that is only documentation is workspace-internal, while a hit in a script that *invokes* the
command is code-coupled.
**Done when:** each planned rename is marked coupled or free, with its hits.

### 4. Present ONE consolidated plan → gate
One table: **pairs to collapse** (skill + wrapper → the one command file that survives, with
the skill name being retired), renames (old → canonical new, coupled ones marked), commands to
create or rewrite (and wrongly nested generic commands to flatten), rule + registry creations
from the molds when missing (rule born `authority: background`), unroutables kept-and-reported
with reasons, obsolete-suspect flags (no deletion proposed without the human's word), and —
labelled **"reported, not applied"** — the wider-surface findings (`sk-agent-*`, `sk-hook-*`),
each with the mint that closes it.
Wait for the single confirmation; code-coupled items each await their own.
**Done when:** the user has answered; declined → nothing written, run ends.

### 5. Apply
Execute the confirmed plan: **collapse each pair per §6**, rename command paths, create/rewrite
commands from `automation/command.md`, fix frontmatter gaps per the doctrine (description within
the cap, triggers second sentence — bodies untouched), write rule and registry from their molds
when planned, update each code-coupled reference site alongside its individually confirmed
rename.

**Done when:** every confirmed row is applied.

### 6. Collapse each confirmed pair — the merge, key by key
For every `skills/<name>/SKILL.md` paired with a wrapper in §2, the surviving file is the
**wrapper's path**, so nothing a human types today changes. Frontmatter is a merge with one rule
per key, not a judgement call:

| Key | Source |
| --- | --- |
| `description` | the **wrapper's** |
| `argument-hint` | the wrapper's |
| `allowed-tools` | the **skill's** |
| `effort` | the skill's |
| `name` | **dropped** |
| `when_to_use` | **dropped** |
| `user-invocable` | **dropped** |

The body is the **skill's, moved verbatim** — retitle its `# <skill-name> — …` heading to
`# /<command:path> — …` and fold the wrapper's `$ARGUMENTS` sentence in as the input contract.
Keep the body otherwise unchanged.

Then **re-home what sat beside the skill.** A `references/` folder cannot follow the body into
`commands/`, where it would register as a phantom command — move it outside (in a target repo,
`.claude/references/<name>/`) and rewrite every citation to that absolute path. Same for `evals/`.
Delete `skills/<name>/` only once its body is in place and its neighbours are re-homed.

**A pair that is not a clean pair is reported, never guessed:** a skill with no wrapper needs a
path chosen (a human decision), and a wrapper naming no skill has no body to take.
**Done when:** every confirmed pair is one file, `skills/` holds nothing that was migrated, and
every unclean pair is listed with what it needs.

### 7. Audit every body against the doctrine — read-only, always
Read every body at the path it will keep. This stage **writes nothing** and needs no authorization.

Keep these evidence types separate:

- **What the tool decided.** `lint`'s per-body codes carry the mechanically decidable half —
  `sk-body-length`, `sk-step-criterion`, `sk-trigger-position`, `sk-no-boundary`,
  `sk-description-portable`, `sk-metadata-cap`.
- **What only a read can judge.** For each remaining body: the no-op test, sediment, sprawl,
  positive prescription, and whether shared procedure is **cited rather than restated**
  ([doctrine](${CLAUDE_PLUGIN_ROOT}/assets/references/components-command-new/doctrine.md)).

**Collection may be delegated; judgment may not.** On a surface large enough that reading every
body would bury the conversation, dispatch read-only `Task` collectors — one per slice — that
report *what each body contains* (which levers its frontmatter carries, what it cites, where its
numbered steps end) and nothing else. Every verdict above stays with the orchestrator: a
collector reports text, never a doctrine finding, because "this body has no positive prescription"
is a claim about behaviour and the same read that makes it must also weigh the fix.

Report each finding as `command · violated rule · one-line evidence · the /quenching:components:command:new invocation
that opens the edit`, labelled **"reported, not applied"**. Skip every legacy `openspec-*` body —
that surface is `/quenching:specs:align`'s here as everywhere. Never rewrite a body to close a finding.
**Done when:** every surviving body carries a verdict — a finding with its fix invocation, or
clean — and nothing was written.

### 8. Review every description — ONE table, its own OK
Review every description across the whole surface in **one pass**.

Read **frontmatter only**. Judge descriptions against the other descriptions, not bodies. §1's
`doctor` payload counts the surface, and its `lint` payload names the description codes:
`sk-metadata-cap`, `sk-description-portable`, `sk-trigger-position`, `sk-no-boundary`.

**Which class a description is in decides which verdicts apply.** A typed-only command
(`disable-model-invocation: true`) has left the routing surface: `lint` reports neither routing code
against it, nothing routes from its prose, and nothing ever loads it — so there is nothing to buy by
shortening it and no trigger to demand. Its description keeps all three slots at full length for the
human picking it out of the `/` menu, who has no routing to fall back on
(`/.knowledge/standards/automation/skills.md` §The admission criterion). The split is
read from the frontmatter this stage reads anyway — never guessed.

Judge each description against the three slots and the competitor test in
[components-command-new/doctrine.md](${CLAUDE_PLUGIN_ROOT}/assets/references/components-command-new/doctrine.md)
§The three slots. What this stage does with each verdict:

| Verdict | Action |
| --- | --- |
| prose about **how** the command works — step order, tool names, call counts, the reasoning behind a rule | **cut** on a routed description; it is body. On a typed-only one, cut it only where it confuses the human reader — length is not the reason, since the command is charged 0 |
| the leading concept is a `/`-menu label, or absent | **rewrite** the first sentence in the command's own vocabulary |
| no trigger, or a trigger after the second sentence (`sk-trigger-position`) | **add** one verbatim phrase per branch that has none; move them into the second sentence. **Routed only** — on a typed-only command an absent trigger is not a defect, and adding one buys nothing that routes |
| `Not for:` naming a command that fails the competitor test | **cut**, and record the waiver with the competitor set checked |
| a real competitor with no `Not for:` (`sk-no-boundary`) | **add** the one clause that routes: `Not for: <job> → <command>` |
| a quoted trigger that looks like sediment | **report**, never cut — `/quenching:components:command:eval <command>` decides it on a measured miss |
| over a cap (`sk-metadata-cap`, `sk-description-portable`) after all of the above | **report** the residue with its code; a cap is not closed by deleting a trigger |

The competitor test runs **against the surface in hand, never from memory**: use the paths in §1's
`lint` payload and the trigger vocabulary from the descriptions just read.

Present ONE table — command · class · current chars → proposed chars · what changed · the slot that
earned it — with the description-code count before → after from §1's `lint` payload, the
mechanically decided half of what this stage changes. **Gate on its own
OK**, separately from §4's: that plan was confirmed before any description had been read, and an
edit nobody saw is not an edit anybody authorized. Declined → nothing is written here and the run
continues to §9 reporting the review as proposed-and-declined.
**Done when:** every description carries a verdict, each applied edit is in the confirmed table,
every waived boundary names the competitor set that was checked, and no trigger phrase was
deleted.

### 9. Verify, decide, report
Regenerate the zone, then let the tool judge the surface the migration produced:
```bash
cq components registry reindex --json   # the zone, from the post-migration surface and §8's descriptions
cq components doctor --json             # the surface invariant the migration just changed
cq components lint --json               # the gaps the migration was supposed to close — §8's codes
cq components registry reindex --json   # `changed: false` — the zone now matches disk
```
Every renamed reference site greps clean, and no citation still points into a deleted
`skills/` tree. `reindex` runs **after** §8, never before: the zone's `Typical trigger` column is
each description's **first quoted phrase**, so a §8 that adds or moves a trigger moves the zone
with it, and a zone regenerated ahead of the review is stale the moment the review applies.

Then re-run §1's probe and decide by the four outcomes in
[convergence.md](${CLAUDE_PLUGIN_ROOT}/assets/references/align/convergence.md)
§The convergence contract: **progress** → another pass from §2 under the same OK, narrating its
plan; **converged** → report; **residue** → stop and report; **pass cap reached** → stop and report
what remains. A second pass here catches the one thing the first can create — a rename that shifted
the registry or dangled a reference. §7's findings are **not** progress: they are read-only and
carry forward unchanged, so a pass that only produced them has converged. **Neither is §8's edit**,
though it does write: the review is idempotent by construction — a description rewritten to the
three slots proposes nothing on a second reading — so a second pass runs §8 only to confirm it has
nothing left to say, and never to re-open a table the human already answered.

In an OKF repo, confirm the registry is indexed, per
[knowledge-add/homes.md](${CLAUDE_PLUGIN_ROOT}/assets/references/knowledge-add/homes.md). The migration
counts go in the report below, not into the bundle.
Report: passes run; collapsed / renamed / created / flattened / rule+registry created / unroutable /
flagged; every surviving `sk-*` finding and every `ct-translation-drift` result, by code; §7's doctrine findings, listed
apart, each with its `/quenching:components:command:new`; and §8's line — descriptions reviewed, edited,
declined; the description-code count before → after from `lint`; every waived boundary with the
competitor set checked (and its accepted `sk-no-boundary`); and every trigger handed to
`/quenching:components:command:eval`. Say plainly when the front converged in one pass — that is the
expected outcome here, not a shortfall. **Done when:** `doctor` and `lint` exit 0 or each surviving
finding is named with its code, the second
`registry reindex` reports `changed: false`, and the counts, the doctrine findings and §8's line
are reported.

## Invariants

- Never modify anything before the plan's OK; a code-coupled rename never rides the batch. A
  cycle-authorized run replaces only the batch gate with narration — never a code-coupled
  item's own OK.
- Never rename, reclassify, or remove a legacy `openspec-*` skill or an `opsx/` wrapper — that
  surface is `/quenching:specs:align`'s; note it and move on.
- Never alter a body's prose — only its title line, its input contract, its citation paths,
  its placement, and its frontmatter conformance. A collapse MOVES a body; it never edits it, and
  §7 only reads it.
- Never inventory before the probe, and never treat §7's read-only findings as progress that
  justifies another pass.
- Never delete a quoted trigger phrase — not for length, not for looking redundant. A trigger
  retires on a measured miss, which is `/quenching:components:command:eval`'s; here it is reported with that
  invocation. Cutting one to fit a cap trades a measurable routing loss for a character count.
- Never write a `Not for:` clause naming a command that fails the competitor test, and never cut
  one without stating the set that was checked — an invented boundary and a silent waiver are the
  same error in opposite directions.
- Never apply §8's edits under §4's OK: that plan was confirmed before a single description had
  been read.
- Never delete a command without the human stating it is obsolete; never force an
  unroutable item onto the axis. Deleting a `skills/<name>/` folder whose body has just been
  moved into its command file is not a deletion in this sense — nothing is lost — but it
  happens only after the move is in place.
- Never write anything but an entry point under `commands/`: a `references/` or `evals/`
  folder moved there would register every file in it as a phantom command.
- Never leave the GENERATED zone stale, and never write inside its markers by hand — the run
  ends on a `registry reindex` that reports `changed: false`.
- Never hand this command file `context: fork` — both gates are mid-flow.
