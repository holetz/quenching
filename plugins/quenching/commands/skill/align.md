---
description: Migrate this repo's whole .claude command surface AND audit every body against the writing doctrine — collapse pairs, one file per entry point. Triggers on "align the skills", "align and update the skills", "migrate my commands", "fix the .claude surface", "collapse the skill wrappers", "audit the command bodies", "converge the automation surface". Probes with skills.py doctor and lint before reading anything, so a conformant surface costs two calls and stops. Otherwise: inventory, ONE plan, one OK, apply the migration, collapse each pair to one file, then read every body against the doctrine — reported with the /skill:new that fixes it, never rewritten, because authoring needs the human whose intent the command encodes. Not for: minting or editing ONE command → /skill:new; an agent or a hook → /skill:agent:new, /skill:hook:new; measuring whether a command teaches anything → /skill:eval; the docs/ or specs/ front → /docs:align, /specs:align.
argument-hint: [optional-scope]
allowed-tools: Bash(python3:*), Bash(py:*), Bash(git grep:*), Bash(grep:*), Bash(mkdir:*), Bash(mv:*), Bash(cp:*), Read, Grep, Glob, Write, Edit, Task
---

# /skill:align — force the automation surface onto the taxonomy

**Input**: `$ARGUMENTS` (an optional scope; omit to sweep the whole automation surface).

The sweep counterpart of `/skill:new`: where the mint keeps each **new** command
conformant, this one converges everything that **already exists** — including a surface still
built as `skills/<name>/SKILL.md` + a mirrored wrapper, which it **collapses to one file per
entry point** (§6 below) — and then **reads every surviving body against the writing doctrine**
(§7), which is the one thing the migration itself is forbidden to touch.

Structure and content are one command because the audit only becomes possible once the migration
has run: a body still sitting in `skills/<name>/SKILL.md` is not yet at the path that will be
judged. The axis, naming, placement, and registry format live in
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
[align-all/sweep-doctrine.md](${CLAUDE_PLUGIN_ROOT}/assets/references/align-all/sweep-doctrine.md).
Read it as this skill's doctrine. What follows is only what is **specific to `.claude/`**:

- **The legacy `openspec-*` surface is not this sweep's.** `.claude/skills/openspec-*/` and
  `.claude/commands/opsx/` are legacy CLI artifacts a prior `openspec init` left behind — a
  native `specs/` repo has none. When present they belong to `/specs:align`, which
  removes them when migrating a legacy `openspec/` workspace
  ([specs-align/conformance.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-align/conformance.md)
  §Shadow copies). Inventory them only to **note** them; never classify them onto the axis,
  rename them, or remove them here.
- **A body is audited, never rewritten.** The shared MERGE rule says bodies are preserved; on this
  front that is the whole point — the migration changes only names, placement, and
  description/frontmatter conformance. §7 then **reads** each body and reports what it finds with
  the `/skill:new` invocation that opens the edit. Rewriting one is **authoring**, and authoring
  needs the human whose intent the command encodes — the same anti-fabrication boundary every
  align holds ([sweep-doctrine](${CLAUDE_PLUGIN_ROOT}/assets/references/align-all/sweep-doctrine.md)
  §Align conformance; report the cycle).
- **This front is honestly short, and says so.** `docs/` and `specs/` each have an out-of-band
  store to drain; this one has none, and the migration is idempotent — so the loop reaches a
  fixpoint in **1–2 passes**, essentially always. It is not ceremony: a rename in the migration
  shifts the registry and can dangle a reference, and re-probing catches that in the same run. But
  a run that converged in one pass with nothing to do reports exactly that, never padded.
- **The wider `.claude/` is inventoried, never migrated.** `.claude/agents/*.md` and the
  hooks wired in `settings.json` and in command frontmatter are **report-only** surfaces:
  the tool names their findings (`sk-agent-*`, `sk-hook-*`) and each is routed to the mint
  that owns it (`/skill:agent:new`, `/skill:hook:new`) — no rename, no move, no write, so
  the confirmed plan's write set stays exactly the command surface's.
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

**Invoke it by its literal resolved path**, never through a shell variable holding the interpreter
plus the path — that idiom word-splits on bash and silently fails on zsh, so it passes where it is
written and breaks in the target repo. The rule, the measured evidence and the one correct
abbreviation are
[specs-create/plans-zone.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-create/plans-zone.md)
§Write the resolved path literally on every invocation.

**This sweep also installs it** (§5), so the repo keeps its verifier after the run ends —
one align per front, each installing its own front's tool.

**Every shell grant is scoped**, per
[`docs/standards/automation/skills.md`](../../../../docs/standards/automation/skills.md)
§`allowed-tools` is always scoped: `python3`/`py` for the tool, `git grep` and `grep` for the
blast-radius sweep (§3), `mkdir`/`mv`/`cp` for the renames and the two installs. This skill
touches no repo toolchain, so it has no claim to an unscoped `Bash`.

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
skills.py lint --json     # per-command conformance, one sk-* code per gap
```
plus one `Glob` for the legacy pairs the tool cannot see (below). Branch as
[sweep-doctrine](${CLAUDE_PLUGIN_ROOT}/assets/references/align-all/sweep-doctrine.md) §Probe before
the inventory prescribes:

| Probe result | What happens |
| --- | --- |
| both exit 0 with no findings, and no legacy pair | **STOP.** Report "`.claude/` conformant, N commands, nothing to align" and end. No inventory, no plan, no confirmation. |
| both exit 0 and the only findings are the report-only wider surface (`sk-agent-*`, `sk-hook-*`) | STOP the same way, then list them with the mint that closes each. Nothing here is this sweep's to write. |
| either exits 1 or 2, or a legacy pair exists | Continue to step 2. |

An **empty** surface (no commands, no skills) also stops: scaffolding a taxonomy for zero commands
is ceremony. Note whether an OKF bundle exists (`docs/index.md` with `okf_version`) and say so once
— without one the rule and registry stay out of scope, while the migration still applies.

The registry zone is deliberately **not** probed: `registry reindex` has no dry run, and it is one
cheap idempotent call that step 8 makes anyway as this front's verifier. A `changed: true` there on
an otherwise-clean run means the zone was stale and has just been repaired — which is a fact to
report, not a reason to pay for an inventory.
**Done when:** both payloads and the glob are in hand, and the run has either stopped or committed
to a full sweep.

### 2. Inventory the surface (read-only)
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
the rule and the registry (`docs/documentation/reference/automation.md`) exist.
**Done when:** the inventory table (item · classification · `sk-*` gap) covers every item in the
working set, and no file changed.

### 3. Sweep the blast radius
Run the shared procedure in
[align-all/sweep-doctrine.md](${CLAUDE_PLUGIN_ROOT}/assets/references/align-all/sweep-doctrine.md)
§The blast-radius sweep — two repo scans for the whole set, never two per rename — over every name slated for
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
from the molds when missing (rule born `authority: background`), **the tool**
`.claude/hooks/skills.py`
(install / upgrade / leave — §5), the operator manual
`.claude/QUENCHING.md` (install / refresh / leave), unroutables kept-and-reported
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

Report each finding as `command · violated rule · one-line evidence · the /skill:new invocation
that opens the edit`, labelled **"reported, not applied"**. Skip every legacy `openspec-*` body —
that surface is `/specs:align`'s here as everywhere. Never rewrite a body to close a finding.
**Done when:** every surviving body carries a verdict — a finding with its fix invocation, or
clean — and nothing was written.

### 8. Verify, decide, report
Regenerate the zone, then let the tool judge the surface the migration produced:
```bash
skills.py registry reindex --json   # the zone, from the post-migration surface
skills.py doctor --json             # the surface invariant the migration just changed
skills.py lint --json               # the gaps the migration was supposed to close
skills.py registry reindex --json   # `changed: false` — the zone now matches disk
```
Every renamed reference site greps clean, and no citation still points into a deleted
`skills/` tree.

Then re-run §1's probe and decide by the four outcomes in
[convergence.md](${CLAUDE_PLUGIN_ROOT}/assets/references/align-all/convergence.md)
§The convergence contract: **progress** → another pass from §2 under the same OK, narrating its
plan; **converged** → report; **residue** → stop and report; **pass cap reached** → stop and report
what remains. A second pass here catches the one thing the first can create — a rename that shifted
the registry or dangled a reference. §7's findings are **not** progress: they are read-only and
carry forward unchanged, so a pass that only produced them has converged.

In an OKF repo, append ONE consolidated `log.md` entry (the migration, with counts) and confirm the
registry is indexed, per
[docs-add/homes.md](${CLAUDE_PLUGIN_ROOT}/assets/references/docs-add/homes.md).
Report: passes run; collapsed / renamed / created / flattened / rule+registry created / unroutable /
flagged; every `sk-*` finding that survived the run, by code; and §7's doctrine findings, listed
apart, each with its `/skill:new`. Say plainly when the front converged in one pass — that is the
expected outcome here, not a shortfall. **Done when:** `doctor` and `lint` exit 0 or each surviving
finding is named with its code, the second `registry reindex` reports `changed: false`, and the
counts and the doctrine findings are reported.

## Invariants

- Never modify anything before the plan's OK; a code-coupled rename never rides the batch. A
  cycle-authorized run replaces only the batch gate with narration — never a code-coupled
  item's own OK.
- Never rename, reclassify, or remove a legacy `openspec-*` skill or an `opsx/` wrapper — that
  surface is `/specs:align`'s; note it and move on.
- Never alter a body's prose — only its title line, its input contract, its citation paths,
  its placement, and its frontmatter conformance. A collapse MOVES a body; it never edits it, and
  §7 only reads it.
- Never inventory before the probe, and never treat §7's read-only findings as progress that
  justifies another pass.
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
