---
description: Converge this repo's whole .claude command surface onto one file per entry point, then audit every body and rewrite every description against the writing doctrine. Triggers on "align the skills", "align and update the skills", "migrate my commands", "fix the .claude surface", "collapse the skill wrappers", "audit the command bodies", "review the skill descriptions", "shorten the descriptions", "converge the automation surface". A body is reported with the /quenching:components:command:new that fixes it, never rewritten; a description is rewritten in ONE surface-wide pass on its own confirmation. Not for: minting or editing ONE command → /quenching:components:command:new; an agent or a hook → /quenching:components:agent:new, /skill:hook:new; measuring what a command teaches, or retiring a trigger on measured evidence → /quenching:components:command:eval; the `knowledge` or `specs` front → /quenching:knowledge:align, /specs:align.
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

Structure and content are one command because both audits only become possible once the migration
has run: a body still sitting in `skills/<name>/SKILL.md` is not yet at the path that will be
judged, and a collapsed pair's surviving description is the wrapper's, which §6 decides. The axis,
naming, placement, and registry format live in
[skill-new/taxonomy.md](${CLAUDE_PLUGIN_ROOT}/assets/references/skill-new/taxonomy.md);
the writing doctrine judged against is
[skill-new/doctrine.md](${CLAUDE_PLUGIN_ROOT}/assets/references/skill-new/doctrine.md);
the capability levers the wider inventory reads against are
[skill-new/capabilities.md](${CLAUDE_PLUGIN_ROOT}/assets/references/skill-new/capabilities.md) —
all owned by the sibling and cited here, never restated. Molds live at
`${CLAUDE_PLUGIN_ROOT}/assets/templates/automation/`.

## Doctrine

The sweep contract every align shares — probe before the inventory, convergence over
accommodation, one plan → one OK with
code-coupled items gating individually, the cycle-authorized narration exception, the two-scan
blast-radius procedure, MERGE-never-clobber, never-delete-on-a-guess, and
align-conformance-report-the-cycle — lives once in
[align/sweep-doctrine.md](${CLAUDE_PLUGIN_ROOT}/assets/references/align/sweep-doctrine.md).
Read it as this skill's doctrine. What follows is only what is **specific to `.claude/`**:

- **The legacy `openspec-*` surface is not this sweep's.** `.claude/skills/openspec-*/` and
  `.claude/commands/opsx/` are legacy CLI artifacts a prior `openspec init` left behind — a
  native `/.specs/` repo has none. When present they belong to `/quenching:specs:align`, which
  removes them when migrating a legacy `openspec/` workspace
  ([specs-align/conformance.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-align/conformance.md)
  §Findings the sweep FIXES). Inventory them only to **note** them; never classify them onto the axis,
  rename them, or remove them here.
- **A body is audited, never rewritten.** The shared MERGE rule says bodies are preserved; on this
  front that is the whole point — the migration changes only names, placement, and
  description/frontmatter conformance. §7 then **reads** each body and reports what it finds with
  the `/quenching:components:command:new` invocation that opens the edit. Rewriting one is **authoring**, and authoring
  needs the human whose intent the command encodes — the same anti-fabrication boundary every
  align holds ([sweep-doctrine](${CLAUDE_PLUGIN_ROOT}/assets/references/align/sweep-doctrine.md)
  §6. Align conformance; report the cycle).
- **A description is the one text this sweep rewrites, and §8 is where.** The asymmetry is not an
  exception to the rule above; it is what the rule is for. A body is intent — long, authored, and
  only its author knows what it meant. A description is **routing**, it is short enough to review
  whole, and its central question — does anything else on this surface answer to the same
  request? — is unanswerable one command at a time. This sweep is the only place holding all of
  them at once, so it is the only place that can waive a boundary honestly. Reviewing them one per
  `/quenching:components:command:new` run would cost N sessions to reach a verdict none of them can reach.
  The edit still gates on its own OK, and a **trigger phrase is never deleted here** — that is
  `/quenching:components:command:eval`'s, on a measured miss.
- **This front is honestly short, and says so.** `/.docs/` and `/.specs/` each have an out-of-band
  store to drain; this one has none, and the migration is idempotent — so the loop reaches a
  fixpoint in **1–2 passes**, essentially always. It is not ceremony: a rename in the migration
  shifts the registry and can dangle a reference, and re-probing catches that in the same run. But
  a run that converged in one pass with nothing to do reports exactly that, never padded.
- **The wider `.claude/` is inventoried, never migrated.** `.claude/agents/*.md` and the
  hooks wired in `settings.json` and in command frontmatter are **report-only** surfaces:
  the tool names their findings (`sk-agent-*`, `sk-hook-*`) and each is routed to the mint
  that owns it (`/quenching:components:agent:new`, `/quenching:skill:hook:new`) — no rename, no move, no write, so
  the confirmed plan's write set stays exactly the command surface's.
- **The registry ends the run honest.** `skills.py registry reindex` regenerates the GENERATED
  zone from the post-migration surface, and a second run reporting `changed: false` is what
  proves it matches disk; residue is reported, never silently dropped.

## Resolving the tool

Resolve `skills.py` per
[align/tool-resolution.md](${CLAUDE_PLUGIN_ROOT}/assets/references/align/tool-resolution.md)
§Resolving the tool §Write the resolved path literally on every invocation; branch on the
**exit code** (0 ok · 1 findings · 2 refusal) and the `--json`, never on prose.

**This sweep also offers to remove a legacy copy** (§5) — never install or refresh one, since the
tool always resolves via the plugin path.

**Every shell grant is scoped**, per
[`/.docs/standards/automation/skills.md`](../../../../.docs/standards/automation/skills.md)
§`allowed-tools` is always scoped: `python3`/`py` for the tool, `git grep` and `grep` for the
blast-radius sweep (§3), `mkdir`/`mv` for the renames, `rm` for a
confirmed legacy tool copy. This skill touches no repo toolchain, so it has no claim to an
unscoped `Bash`.

**What the tool decides, and what it does not.** `doctor` and `lint` decide everything mechanical
— a non-empty description on every command, no two resolving to the same `/` path, kebab-case
segments, the caps, trigger position, the `Not for:` boundary, body length, step criteria,
unscoped `Bash`. Neither decides the **axis**: naming the one folder a command acts on is a claim
about what it is *for*, which no parser makes. Classification stays a read.

**Neither does the tool see a legacy pair.** `skills.py` reads `commands/**` and nothing else, so
a leftover `skills/<name>/SKILL.md` is invisible to it — the collapse in §6 is found by `Glob`
and reported by this sweep, never by a `sk-*` code.

## Workflow (probe → ONE OK → migrate → audit → re-probe)

### 1. Probe — the two calls that decide whether anything else runs
Before any inventory, ask the tool whether there is work at all:
```bash
skills.py doctor --json   # descriptions, duplicate / paths, non-canonical segments — plus
                          # the report-only wider surface: agents/ and wired hooks (sk-agent-*, sk-hook-*)
skills.py lint --json     # per-command conformance, one sk-* code per gap — including the
                          # description codes §8 reports before → after (sk-metadata-cap,
                          # sk-description-portable, sk-trigger-position, sk-no-boundary)
```
plus one `Glob` for the legacy pairs the tool cannot see (below). Branch as
[sweep-doctrine](${CLAUDE_PLUGIN_ROOT}/assets/references/align/sweep-doctrine.md) §1. Probe before the inventory prescribes:

| Probe result | What happens |
| --- | --- |
| both exit 0 with no findings, and no legacy pair | **STOP.** Report "`.claude/` conformant, N commands, nothing to align" and end. No inventory, no plan, no confirmation. |
| both exit 0 and the only findings are the report-only wider surface (`sk-agent-*`, `sk-hook-*`) | STOP the same way, then list them with the mint that closes each. Nothing here is this sweep's to write. |
| the only findings are description codes (`sk-metadata-cap`, `sk-description-portable`, `sk-trigger-position`, `sk-no-boundary`) | **Skip to §8.** There is nothing to migrate, and an inventory, a plan and a confirmation for zero renames is ceremony — §8 carries its own gate. |
| anything else exits 1 or 2, or a legacy pair exists | Continue to step 2. |

**`lint` carries §8's before-image.** Descriptions can be structurally perfect — every trigger in
place, every boundary present — while the surface pays for prose about *how* each command works, and
`doctor` exits 0 on that surface forever. What `lint` names is the description codes —
`sk-metadata-cap`, `sk-description-portable`, `sk-trigger-position`, `sk-no-boundary` — the half of
§8's review a parser can decide, for one call; the prose no parser names, §8 cuts by the read.

An **empty** surface (no commands, no skills) also stops: scaffolding a taxonomy for zero commands
is ceremony. Note whether an OKF bundle exists (`/.docs/index.md` with `okf_version`) and say so once
— without one the rule and registry stay out of scope, while the migration still applies.

The registry zone is deliberately **not** probed: `registry reindex` has no dry run, and it is one
cheap idempotent call that step 8 makes anyway as this front's verifier. A `changed: true` there on
an otherwise-clean run means the zone was stale and has just been repaired — which is a fact to
report, not a reason to pay for an inventory.
**Done when:** the three payloads and the glob are in hand, and the run has either stopped,
committed to a full sweep, or entered §8 directly.

### 2. Inventory the surface (read-only)
`Glob` for what the tool cannot see, because it reads only `commands/**`:
`.claude/skills/*/SKILL.md` and directory-scoped `**/.claude/skills/*/SKILL.md`. **Every one of
those is a pair awaiting collapse** — pair each with the wrapper whose body invokes it (the
`quenching:<name>` or bare `<name>` reference), and record a skill with no wrapper, or a
wrapper naming no skill, as an item needing a human decision rather than a mechanical merge.
Set aside every legacy `openspec-*` skill and `opsx/` wrapper — they are `/quenching:specs:align`'s
(Doctrine §the legacy `openspec-*` surface); list them as *out of scope, owned by
`/quenching:specs:align`* and drop them from the working set, including from the tool's findings.

Then add the half the tool cannot: for each remaining item, the **axis classification** per the
test ([taxonomy](${CLAUDE_PLUGIN_ROOT}/assets/references/skill-new/taxonomy.md) §The single axis — several unrelated folders
→ unroutable). Read `/.docs/standards/automation/skills.md` if present — it governs; note whether
the rule and the registry (`/.docs/documentation/reference/automation.md`) exist, and whether
the rule and the registry (`/.docs/documentation/reference/automation.md`) exist.
**Done when:** the inventory table (item · classification · `sk-*` gap) covers every item in the
working set, and no file changed.

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
from the molds when missing (rule born `authority: background`), a **legacy copy of the tool**
`.claude/hooks/skills.py`
(removal offered — §5, never installed or refreshed), unroutables kept-and-reported
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

**Offer to remove a legacy copy of the front's tool.** `skills.py` always resolves via the plugin
path now, so a copy under the target's `.claude/hooks/` does nothing but drift — never install or
refresh one. **Ask the tool rather than comparing by hand** — one call covers all three fronts'
copies:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/assets/bin/skills.py" drift --json
```

Run it from the **plugin path**: an installed copy would answer from the same stale `VERSION` it
is being asked about, and refuses (exit 2) instead. Act on this front's row (`skills.py`): a
legacy copy present → offer **removal**; absent → nothing to do. The same one call is what
`/quenching:specs:align` reads for `specs.py` and `/quenching:docs:align` for `okf-validate.py`, so a run of any one of
them can report the other two fronts' drift without a second probe.

**Done when:** every confirmed row is applied, and no stale `.claude/hooks/skills.py` copy
remains (or its being ahead of the plugin is reported and left alone).

### 6. Collapse each confirmed pair — the merge, key by key
For every `skills/<name>/SKILL.md` paired with a wrapper in §2, the surviving file is the
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
No other edit: judging what a body *says* is §7's, and mixing it into the migration makes the
diff unreviewable.

Then **re-home what sat beside the skill.** A `references/` folder cannot follow the body into
`commands/`, where it would register as a phantom command — move it outside (in a target repo,
`.claude/references/<name>/`) and rewrite every citation to that absolute path. Same for `evals/`.
Delete `skills/<name>/` only once its body is in place and its neighbours are re-homed.

**A pair that is not a clean pair is reported, never guessed:** a skill with no wrapper needs a
path chosen (a human decision), and a wrapper naming no skill has no body to take.
**Done when:** every confirmed pair is one file, `skills/` holds nothing that was migrated, and
every unclean pair is listed with what it needs.

### 7. Audit every body against the doctrine — read-only, always
Now that every body sits at the path it will keep, read it. This stage **writes nothing** and needs
no authorization; it is the one thing the migration is forbidden to do, and folding it in here is
what makes the fold worth having.

Two kinds of evidence, kept apart in the report because they are not the same claim:

- **What the tool decided.** `lint`'s per-body codes carry the mechanically decidable half —
  `sk-body-length`, `sk-step-criterion`, `sk-trigger-position`, `sk-no-boundary`,
  `sk-description-portable`, `sk-metadata-cap`. A code names a **threshold crossed**.
- **What only a read can judge.** For each remaining body: the no-op test, sediment, sprawl,
  positive prescription, and whether shared procedure is **cited rather than restated**
  ([doctrine](${CLAUDE_PLUGIN_ROOT}/assets/references/skill-new/doctrine.md)). A read names a
  **claim about behaviour**, and no parser makes one.

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
The description is the only text a command has that never stops loading: it is paid on every
session in the repo whether or not the command ever fires, and it is the only text that decides
whether a spoken request reaches it at all. Review the whole surface in **one pass**, here.

Read **frontmatter only** — never a body, whether or not §7 ran. A description is judged against the
other descriptions, and no body changes that verdict. The read is self-limiting and its size is
known *before* it starts: §1's `doctor` payload counts the surface, and its `lint` payload names
the description codes it carries — `sk-metadata-cap`, `sk-description-portable`,
`sk-trigger-position`, `sk-no-boundary` — the mechanically decided half of this stage. Say the count
and the code total when opening the stage, so the human authorizes a cost rather than an open-ended
sweep.

**Which class a description is in decides which verdicts apply.** A typed-only command
(`disable-model-invocation: true`) has left the routing surface: `lint` reports neither routing code
against it, nothing routes from its prose, and nothing ever loads it — so there is nothing to buy by
shortening it and no trigger to demand. Its description keeps all three slots at full length for the
human picking it out of the `/` menu, who has no routing to fall back on
([skills.md](../../../../.docs/standards/automation/skills.md) §The admission criterion). The split is
read from the frontmatter this stage reads anyway — never guessed.

Judge each description against the three slots and the competitor test in
[skill-new/doctrine.md](${CLAUDE_PLUGIN_ROOT}/assets/references/skill-new/doctrine.md)
§The three slots — owned there, never restated here. What this stage does with each verdict:

| Verdict | Action |
| --- | --- |
| prose about **how** the command works — step order, tool names, call counts, the reasoning behind a rule | **cut** on a routed description; it is body. On a typed-only one, cut it only where it confuses the human reader — length is not the reason, since the command is charged 0 |
| the leading concept is a `/`-menu label, or absent | **rewrite** the first sentence in the command's own vocabulary |
| no trigger, or a trigger after the second sentence (`sk-trigger-position`) | **add** one verbatim phrase per branch that has none; move them into the second sentence. **Routed only** — on a typed-only command an absent trigger is not a defect, and adding one buys nothing that routes |
| `Not for:` naming a command that fails the competitor test | **cut**, and record the waiver with the competitor set checked |
| a real competitor with no `Not for:` (`sk-no-boundary`) | **add** the one clause that routes: `Not for: <job> → <command>` |
| a quoted trigger that looks like sediment | **report**, never cut — `/quenching:components:command:eval <command>` decides it on a measured miss |
| over a cap (`sk-metadata-cap`, `sk-description-portable`) after all of the above | **report** the residue with its code; a cap is not closed by deleting a trigger |

The competitor test runs **against the surface in hand, never from memory**: the `/<namespace>:`
commands share, from the paths in §1's `lint` payload, and the trigger vocabulary that overlaps,
from the descriptions this stage just read. It needs nothing §2 collected, which is what lets §1
enter this stage directly on a surface with nothing to migrate.

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
skills.py registry reindex --json   # the zone, from the post-migration surface and §8's descriptions
skills.py doctor --json             # the surface invariant the migration just changed
skills.py lint --json               # the gaps the migration was supposed to close — §8's codes
skills.py registry reindex --json   # `changed: false` — the zone now matches disk
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
[docs-add/homes.md](${CLAUDE_PLUGIN_ROOT}/assets/references/docs-add/homes.md). The migration
counts go in the report below, not into the bundle.
Report: passes run; collapsed / renamed / created / flattened / rule+registry created / unroutable /
flagged; every `sk-*` finding that survived the run, by code; §7's doctrine findings, listed
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
