# Installation — gap → payload + deprecation doctrine

> **Way back:** [../SKILL.md](../SKILL.md) (agent roadmap) ·
> human overview & architecture: the project docs site ·
> [README.md](README.md) (`references/` index).

This method **detects, prioritizes and installs**. The artifact that fills each
gap always comes **from inside the package** ([../assets/](../assets/)), never
from an external skill that must pre-exist in the repo — this is the
**self-containment** guarantee.

When a table row matches the gap, **install the payload** (with user
confirmation, item-by-item) and **adapt it** to the derived shape (language,
prefixes, paths).

## Gap → payload to install

| Detected gap | Package payload | Destination in target repo |
| --- | --- | --- |
| CLAUDE.md above ceiling / broken link / stale dependency / broken root↔sub chain / fossil | skill `quenching-map` + hook `validate-claude-md.py` | `.claude/skills/<prefix>-mapa/`, `.claude/hooks/` + `settings.json` |
| Missing, stale or mis-indexed current standard/contract; unwritten house convention; home in variant name (`arquitetura/`) | skill `quenching-docs` + canonical scaffold `docs/standards/` | `.claude/skills/<prefix>-docs/`, `docs/standards/` of target (migrate variant, with OK) |
| **Entire** `standards/` layer empty/incomplete/stale vs. code, OR `INDEX.md` out of sync with disk (build/rebuild the whole layer in parallel) | orchestrator skill `quenching-standards` + sub-agent `quenching-writer` (fan-out one worker per topic; mines repo for de-facto = `current` anchored at `file:line` + researches references; regenerates `INDEX.md` deterministically from disk) | `.claude/skills/<prefix>-standards/` + `.claude/agents/` of target |
| Binary (slide/PDF/diagram/regulation) whose content the agent consults, without an extract for the LLM | skill `quenching-docs` + template `templates/docs/sidecar.md` | `.md` next to the binary in `presentations/` or `reference/regulations/` |
| Missing backlog item, or completed item still in backlog tree | skill `quenching-docs` + scaffold `docs/backlog/` + frontmatter `backlog-item.md` | `docs/backlog/` of target |
| Open decision / ADR (canonical home `decisions/`, variant `adr/`) / domain terminology | skill `quenching-docs` + scaffold `docs/decisions/` + frontmatter `adr.md` | `docs/decisions/` of target (migrate `adr/`, with OK) |
| Outbound/directed communication (incident/change/deploy/downtime/migration/news) without a home; loose announcement or without a scannable header; channel without template | skill `quenching-announcement` + scaffold `docs/communications/` (`templates/` per channel `email`/`chat`/`wiki`/`markdown` + `archive/`) | `.claude/skills/<prefix>-announcement/` + `docs/communications/` of target |
| Skill with weak description (sub-trigger), giant SKILL.md, no prefix, `name`≠folder; or new skill/agent to create | skill `quenching-skills` + frontmatter `skill.md`/`agent.md` | `.claude/skills/`, `.claude/agents/` |
| Sub-agent without return format / too-broad `tools` / no `model`; missing read-only auditor | skill `quenching-skills` + template `agents/quenching-auditor.md` | `.claude/agents/` |
| Missing/broken hook, `settings.json`, permissions, env var | skill `quenching-config` + hook `validate-claude-md.py` | `.claude/hooks/`, `settings.json` |
| Repo executable logic **without canonical home**: business rule embedded inline in hook (should be a called script); scripts scattered in root / flat bag without purpose; README-map lying vs. disk; `scripts/<…>` invoked by hook/command/CI that doesn't exist | **organization scaffold** `scripts/` (README-map + `ci/checks/maintenance/dev/` by purpose, placeholders — **no concrete scripts**); inline rule is **extracted** to `scripts/…` (proposed, with OK); spec [scripts-taxonomy.md](scripts-taxonomy.md) | `scripts/` of target (organize/move with OK; package ships only the STRUCTURE) |
| Missing **automatic freshness** of the recurring cycle (Step 8): nothing records the gap the session exposed "while it's fresh" | **Stop hook** `hooks/propose-knowledge-delta.py` (only PROPOSES via `additionalContext`, never blocks) + `settings.snippet.json` | `.claude/hooks/` + `Stop` block in `settings.json` |
| Missing **compact-survival** (Step 8): `/compact`/`/clear`/`resume` erases conventions/FQNs/guardrails/boundaries and nothing re-injects them | **SessionStart hook** `hooks/reinject-conventions.py` (reads from target-derived source — `conventionsFile` or CLAUDE.md root head, never a fixed list; stdout becomes context, exit 0) + `settings.snippet.json` | `.claude/hooks/` + `SessionStart` block (matcher `compact\|clear\|resume`) in `settings.json` |
| Missing **audit-trail** (Step 8): a new skill / changed `settings.json` in the session goes unnoticed | **ConfigChange hook** `hooks/audit-config-change.py` (records who/when/what in a target log, append-only, metadata only — never content; OBSERVES, exit 0 always, never blocks) + `settings.snippet.json` | `.claude/hooks/` + `ConfigChange` block (5 sources) in `settings.json`; trail in `auditLog` (default `.claude/config-audit.log`) |
| Missing **`docs/` runtime coverage** (Step 8, event trigger; crosses dim 2 × dim 8): the agent writes/edits a doc outside the canonical home and nothing reconciles it "while it's fresh" | **PostToolUse hook** `hooks/propose-docs-home.py` (matcher `Write\|Edit`): under `docs/`, **PROPOSES** the canonical home/slot via `additionalContext` (does not block, exit 0; criteria 2b and mechanics in **dim 8**) + `settings.snippet.json` | `.claude/hooks/` + 2nd hook in the `PostToolUse` block (matcher `Write\|Edit`) in `settings.json`; adjust `docsDir` to the target's docs root |
| Missing **deterministic protection of generated artifact** (dim 14 enforcement × dim 8): the repo marks something as "generated by CI, never hand-edited" (`*.job.yml`/manifests/AUTO-GENERATED catalog/lockfile) but only the CLAUDE.md guidance protects it — the model can edit it and the work disappears in the next generation | **PreToolUse hook** `hooks/protect-generated.py` (matcher `Write\|Edit`): runs BEFORE the tool and **BLOCKS** when the destination matches `protectedGlobs` (`permissionDecision: "deny"` + actionable reason; wins even in `bypassPermissions`; mechanics in **dim 8/14**) + `settings.snippet.json` | `.claude/hooks/` + `PreToolUse` block (matcher `Write\|Edit`) in `settings.json`; **derive `protectedGlobs`/`sourceHint` from target** in Step 1 (empty list = inert; NEVER hardcode paths) |
| Missing **automatic "before concluding" validation** (dim 8 thin-hook-calls-script × `scripts/`): CLAUDE.md says "altered files pass checks before concluding" but nothing guarantees it — agent forgets (type checking is the most forgotten) | **Stop hook** `hooks/run-validation.py`: at end of turn **CALLS the target's validation script** (`validateScript`/`validateCmd`, home `scripts/checks`/`ci`) on altered files (`git status --porcelain`); logic lives in `scripts/`, hook is the thin trigger. Default **PROPOSES** the result (`additionalContext`, exit 0); `blockOnFail:true` makes it mandatory (`decision: block`) + `settings.snippet.json` | `.claude/hooks/` + 2nd hook in `Stop` block in `settings.json`; **derive `validateScript` from target** (empty = inert; NEVER hardcoded ruff/pyright trio — that's only the example for a Python repo). The **concrete script** is born in `scripts/checks` when applying to the target, not in the payload |
| Expected MCP server outside versioned `.mcp.json`, literal secret, allowlist by `serverName` | skill `quenching-config` | `.mcp.json`/`managed-mcp.json` of target |
| Catalog without generated×curated separation, or missing consumption doctrine | skill `quenching-docs` | target's domain layer |
| Missing behavioral guardrail, or copied in prose in CLAUDE.md | skill `quenching-guardrails` (CLAUDE.md cites, does not copy) | `.claude/skills/<prefix>-guardrails/` |
| Missing **manual trigger** of the recurring maintenance cycle (re-audit on demand; repo doesn't have `/<re-audit>` yet) | **command-skill** `commands/quenching-reaudit/` + sub-agent `agents/quenching-auditor.md` | `.claude/skills/<prefix>-reauditar/` (+ `.claude/agents/` of target) |
| Scorecard/report exists but the user **doesn't know where to start / in what order** to install (greenfield, or many gaps with no sequence) — missing the "invest first in X, then Y" roadmap | **read-only** orchestrator skill `skills/quenching-roadmap/` (+ sub-agent `agents/quenching-auditor.md` via `context: fork`) — PRODUCES the SEQUENCED roadmap "invest first in X, then Y" (METHOD/structure investment order by leverage×cost×prerequisite); PROPOSES the order, does not install (Steps 5-7, with OK) | `.claude/skills/<prefix>-roadmap/` (+ `.claude/agents/` of target) |

> **Paths/prefixes are examples.** Adapt `<prefix>` to the taxonomy derived in
> Step 1 (e.g.: the repo uses `docs-`, `arq-`, `skills-`). The payload is the
> **starting point**, not a rigid mold — rename and re-fit to the target's
> conventions.

## Installation procedure (Step 5 of SKILL.md, with confirmation)

1. **Copy** the payload from [../assets/](../assets/) to the target's destination.
2. **Rename** folder/`name` to the derived taxonomy; **translate** to the repo's
   language if needed.
3. **Repoint** the payload's internal paths to where the layer lives in the
   target (e.g.: the skill `quenching-docs` references "the standards layer" — fix
   it to the real path derived in Step 0 of
   [detection-and-smells.md](detection-and-smells.md)).
4. **Wire** the hooks: register the `command` in the target's `settings.json`
   (copying the script is not enough — **a hook only runs if wired**; see "Hook
   wiring" below) and commit the `hooks-config.json`.
5. **Never** overwrite the target's generated artifacts (`*.job.yml`, manifests,
   AUTO-GENERATED catalog or equivalent) — these respect the repo's "X defines Y"
   rule.

## Hook wiring — merge the snippet, don't overwrite

Copying `protect-generated.py` to `.claude/hooks/` **does nothing**: a hook only
fires if there is a **corresponding entry** in the target's `settings.json` (the
docs are explicit — *"This example runs a linting script only when…"* only works
via the block in `settings.json`; the script alone is **inert**). The package
carries the wiring fragment
[../assets/hooks/settings.snippet.json](../assets/hooks/settings.snippet.json);
installing it means **merging**, never `cat >`/overwriting.

**1. It is a FRAGMENT to MERGE.** The snippet brings
`hooks: { <Event>: [ { matcher, hooks: [...] } ] }`.
- Merge **by event and by matcher** into the blocks the target already has.
- **Arrays concatenate**: add the package's matcher-object to the event's array;
  if there's already a group with the **same `matcher`**, append to its `hooks[]`.
- **Never clobber** what the target already has wired (a pre-existing lint
  PostToolUse survives alongside `propose-docs-home`).
- Canonical structure (doc): `Event → [matcher-group] → "matcher" + "hooks":[
  {"type":"command","command":…,"timeout":…} ]`.

**2. Choose the right SCOPE** — doc precedence: **Managed > CLI > Local > Project
> User**.

| Scope | File | Nature | When to use |
| --- | --- | --- | --- |
| **Project** (default) | `.claude/settings.json` | *checked-in*, shared with the team | home of knowledge hooks that **everyone** should have (the 5 payloads) |
| **Local** | `.claude/settings.local.json` | *gitignored*, per-machine | personal override (e.g.: disable a hook locally, `enabled:false` in `hooks-config.json`) |
| **User** | `~/.claude/settings.json` | unversioned, applies to all user repos | only hook the **machine owner** always wants, outside the team scope |

**3. Project settings load only from the STARTING DIRECTORY, not inherited from
parents** (doc verbatim — *"Project settings in `.claude/settings.json` load only
from your starting directory and are not inherited from parent directories"*): in
a **monorepo**, each subfolder from which Claude is started needs its **own**
`.claude/settings.json` wired — wiring only at root is not enough. Wire at the
target's actual startup level.

**4. Make the script executable and the path portable.**
- `command` uses the **`${CLAUDE_PROJECT_DIR}`** placeholder (project root),
  never an absolute machine path.
- `chmod +x .claude/hooks/<script>` (doc: *"Make the script executable:
  `chmod +x …`"*).
- The payloads are Python (`python3 ${CLAUDE_PROJECT_DIR}/.claude/hooks/<script>.py`)
  — the `python3` in `command` dispenses with the `.py` execution bit, but keep
  the shebang.

**5. Check the 1:1 wiring** (avoids the orphan/dangling hook smell — block 8b):
- every script in `.claude/hooks/` has an entry in `settings.json` (otherwise
  it is **orphan**, inert);
- every entry points to an **existing** script (otherwise it is **dangling**);
- in the **right event/matcher** (PreToolUse to block, PostToolUse to propose,
  `compact` in SessionStart, etc.).

## Cross-repo installation of the canonical `docs/` taxonomy — converge-to-canonical

The skill defines a **CANONICAL `docs/` taxonomy** with **fixed names**. The
single source of the tree, variant→canonical mapping and migration doctrine is
[docs-taxonomy.md](docs-taxonomy.md). The scaffold-payload is
[../assets/docs/](../assets/docs/). **The repo converges to the skill**, not the
skill to the repo — *"replace many per-directory files with one set of
conventions everyone installs"* — so everyone transitioning between repos sees
the tree **literally identical**.

The installation procedure is a **converge-to-canonical** in four stages:

1. **Derive the target's shape against the canonical names (Step 0).** The Step 0
   of [detection-and-smells.md](detection-and-smells.md) resolves variables by deriving
   **the canonical name first** (`$ARCH_DIR`=`docs/standards/`,
   `$ADR`=`docs/decisions/`, `$VISION`=`docs/vision/`, `$CATALOG`=`docs/catalog/`,
   …) and signals when the repo has the home under a **variant name**.
2. **Map variant → canonical and PROPOSE migration (the repo converges).** The
   mapping table by function lives in [docs-taxonomy.md](docs-taxonomy.md) —
   don't repeat it. Each variable pointing to a variant name enters as
   **DEPRECABLE** with the proposed canonical destination: the variant name is a
   non-convergence smell (block 2b), not a convention to keep. A repo home with
   **no corresponding canonical** is `NO-HOME` (2b) — home to add to the taxonomy,
   or material in the wrong quadrant; resolve manually.
3. **Install only the absent canonical homes that apply (completeness of what
   fits).** Each **absent** canonical home whose function **applies** to the repo
   is a slot to install from the scaffold [../assets/docs/](../assets/docs/).
   **Do not** install a home that doesn't fit (repo without data doesn't get
   `catalog/`): the taxonomy is completeness **of what fits**, not a blind
   checklist. The homes **layer**, not **replace** — *"they layer rather than
   replace each other"*.
4. **Migrate the variant; never rename/delete without OK.** Where the repo has
   the home under a variant name, **propose migration to the canonical** (move
   content, sync index/labels) and apply the **deprecation doctrine** below to
   the variant (signals, does not remove). Step 5 confirmation and "don't delete
   without OK" **remain**.

> **Deterministic and prescriptive, with safety preserved:** the variant→canonical
> mapping and installation of absent homes are repeatable (same inputs → same
> result, the SAME tree in every repo), but **each migration requires Step 5
> confirmation**. "Deterministic" = don't re-invent the tree for each repo; **not**
> = rename/delete without OK. The migration of a variant is **recommendation**
> (deprecable); removal of the old name is the user's decision.

## Items without payload — the method only proposes (does not install)

Three dimensions have no content payload, because content is a **human decision**.
For them the method delivers the **suggested text/diff** in the corresponding
section of the report and **stops there**:

- **3. Vision (`docs/vision/`)** — proposes the edit/segmentation of the
  direction; user applies. The canonical home is the **`docs/vision/`** folder
  segmented by area (empty shells + comment, part of the `assets/docs/` scaffold);
  a single `VISION.md` is a variant to migrate. Installing is the user's decision.
- **10. Memory** — signals index×files divergence; **never writes memory**.
- **12. Boundary doctrine** — proposes which is the canonical home and what
  becomes just a link in the other artifacts. This is the method's **core**: the
  diagnosis no payload produces. *Applying* the rearrangement uses the templates
  that own the touched artifacts (moving a standard from VISION to standards
  = `quenching-docs` on the writing end).

## Deprecation doctrine — what the repo already had

The model is **pure installer**: the package payload is the **single source** of
that capability (versioned and evolved here). When the target repo **already has**
a skill/agent/hook doing the same work:

1. **Don't duplicate silently.** Install the package payload (the single source)
   and **list the pre-existing one as DEPRECABLE** in the report's "Deprecables"
   section ([report-format.md](report-format.md)).
2. **Justify the deprecation:** what the old artifact did, which payload replaces
   it, and the gain of removing it (a single source instead of two diverging).
3. **Never remove** the old artifact without the user's **explicit OK** —
   deprecation is a recommendation, removal is their decision.
4. **Exception — repo convention wins (skills/agents/hooks):** if the pre-existing
   artifact is better adapted to local conventions than the generic payload, offer
   **keeping the repo's and discarding the payload** as an alternative in the
   report. The goal is a single source, not imposing the package.
   - **Does not apply to `docs/` NAMES:** the `docs/` taxonomy is **canonical/
     prescriptive** (see "Cross-repo installation" above) — there the repo
     **converges to the canonical name** (the variant name is deprecable, with OK),
     it does not keep its own.

## Golden rule

The method is **self-contained**: everything it installs comes from
[../assets/](../assets/). It **does not depend** on any external skill and
**does not reference** skills from another repo. It only **does not install**
when the dimension has no payload (3/10/12) — and even then, only **proposes**.
Never writes memory, never decides the direction alone, never edits generated
artifacts, never removes the old artifact without OK.
