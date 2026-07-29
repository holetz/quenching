---
slug: notice-installed-tool-version-drift
title: Nothing notices an installed tool copy falling behind the plugin
verification: per-section
priority: {level: 5, criticality: high, date: 2026-07-28}
branch: {base: main, work: plan/notice-installed-tool-version-drift}
refined: {mode: gate, date: 2026-07-28}
approved: {date: 2026-07-28}
---

# Nothing notices an installed tool copy falling behind the plugin

<!-- ONE spec is ONE file for its whole lifecycle. Phases enrich it; they never split it.

     `specs.py new` stamps the frontmatter and `## Problem` ALONE — a captured spec is four
     lines of body, not a thirteen-heading skeleton. Every other heading below is created on
     first write by `specs.py section <slug> "<Heading>" --write`, which inserts it in the
     canonical position with the guidance comment kept here.

     THE STAGE-SCOPED EXPLICIT-NONE RULE. A heading is required — and required to carry
     `- none — <reason>` when it has nothing in it — only once ITS OWN gate is reached:

       new (capture)        `## Problem`
       ready (derived)      the nine definition sections (`## Problem` .. `## Risks`)
                            AND `## Tasks`
       ready (warn only)    `## Handoff` non-empty
       promote -> archive/  `## Outcome`

     `ready` is a DERIVED STAGE, not a folder: a spec lives in `plans/` for its whole active
     life, and filling those ten sections is what makes it ready. Nothing refuses on that
     gate — it is a floor `execute` reports against, and the human's go-ahead is the
     `approved:` frontmatter record, asked for inline.

     Before its gate, a heading's absence is NOT an omission — it is a not-yet. After its
     gate, three rules decide whether a section counts as filled:

       1. `- none — <reason>` counts as filled. An omission and a null are different facts.
       2. A heading present with an EMPTY body is malformed and refuses. It is neither an
          answer nor a not-yet.
       3. An absent heading before its gate is legal.

     Headings are a PARSED contract — canonical English, exactly as written here. Body prose
     follows the repo's language. A heading outside this set is a stray and validate flags it.

     AUDIENCE. Each section names who reads it. `## Problem`/`## Proposal`/`## Design` are for
     the human — examples and plain language belong there. `## Handoff`/`## Tasks` are for
     agents — terse, with `files:`/`verify:`/`pattern:` metadata. An orchestrator never sends
     the human sections to an executor; that is what lets one file serve both audiences
     without bloating agent context. -->

## Problem

Each front's align **offers** to install or upgrade its tool into a target's `.claude/hooks/` —
`/docs:align` step 6 for `okf-validate.py`, `/specs:align` for `specs.py`, `/skill:align` for
`skills.py`. The offer is the only moment the version is ever compared, so a repo that installed
once and never ran an align again keeps running whatever it got, indefinitely, and nothing says so.

This repo is the standing example. While concluding `instrument-and-extend-skill-front`,
`.claude/hooks/specs.py --version` answered **1.0.0** against a plugin shipping **4.1.0** — three
major versions behind, and behind enough that its `status` subcommand still took `--plan` where the
current one takes `--spec`. The conclude run had to fall back to the plugin's own copy to proceed.
`okf-validate.py` is in the same state. The repository that *authors* these tools has been running
years-old copies of two of them, and no check anywhere noticed.

The cost is not merely staleness: a stale copy answers a different CLI contract, so a command that
resolves the installed copy first (which the documented fallback tells it to do) branches on a
payload shape that no longer exists.

**What makes this a spec.** The fix is not "run the aligns" — that closes today's instance and
restores the same silence tomorrow. Something must *notice*: a drift check that is cheap enough to
run without an align, reporting the installed version against the shipped one for all three tools.

Discovered and confirmed live during `instrument-and-extend-skill-front`'s conclude, 2026-07-28.

## Proposal

- A **`drift` subcommand exists on `skills.py`** and reports all three installed tools in ONE
  payload: `okf-validate.py`, `specs.py`, `skills.py` — their installed version, the version the
  plugin ships, and the verdict. `--json`, exit `0` ok · `1` findings · `2` refusal.
- **Drift is reported in both directions.** An installed copy *behind* the plugin and one *ahead*
  of it are both findings, and each report names **which copy a command will actually execute** —
  so "yours is newer" reads as "your newer copy is not the one running".
- **Wiring is answered, not assumed.** For `okf-validate.py` the report says whether
  `.claude/settings.json` (or `settings.local.json`) actually references it. An installed-but-never-
  invoked hook is a finding, not silence — the state this repo sat in undetected.
- **It runs without an align.** One call in each of the four probe steps (`/align`, `/docs:align`,
  `/specs:align`, `/skill:align`), and a human can run it by hand from the plugin path at any time.
- **Run from an installed copy, it refuses** (exit 2) rather than answering from a stale `VERSION`.
- The three aligns' install steps **consume that payload** instead of each restating an ad-hoc
  `--version` comparison in prose.

## Out of Scope

- **Fixing the drift.** Installing or overwriting a copy stays each front's align, offered and
  confirmed. `drift` reports; it never copies a file. Repair needs the confirmation an align
  already owns, and a checker that silently rewrites `.claude/hooks/` is the thing nobody could
  trust to run in a probe.
- **Wiring a hook into `settings.json`.** `/docs:align` step 5 and `/skill:hook:new` own that.
  `drift` only reports that the wiring is absent.
- **The six-artifact release bump.** [versioning-release.md](docs/standards/ci-cd/versioning-release.md)
  governs when the numbers move; this spec changes only who notices afterwards.
- **An always-on SessionStart hook.** Rejected in `## Alternatives Considered`, and self-defeating:
  the failure mode being detected is a hook nobody wired.
- **Auditing arbitrary scripts under `.claude/hooks/`.** `drift` knows exactly three tools by name.
- **Operator-manual drift** (`docs/QUENCHING.md`, `specs/QUENCHING.md`, `.claude/QUENCHING.md`).
  Their banner carries a version and could be compared the same way, but a manual is prose a human
  may legitimately have edited, so "behind" is not automatically wrong. Deferred, and named here so
  it stops being re-proposed — see `## Open Decisions`.

## Impact

### Standards this spec will write into docs/standards/

- `docs/standards/ci-cd/versioning-release.md` — gains the lockstep's missing half: how a target
  *notices* drift, in both directions, why the check must run from the plugin copy, and why an
  installed-but-unwired hook is a separate finding from a stale one.

### Product code this spec expects to touch

- `plugins/quenching/assets/bin/skills.py` — the `drift` subcommand and its selftest fixture
- `plugins/quenching/commands/align.md` — step 1's probe gains the call
- `plugins/quenching/commands/docs/align.md`, `commands/specs/align.md`, `commands/skill/align.md` —
  each install step consumes the payload instead of restating a `--version` comparison
- `plugins/quenching/assets/bin/functional-checks.sh` — the assertion that the conductor's probe
  actually issues the call, since nothing else tests a `commands/**` change in-session

## Validation

Run from the repo root; `SK` is `plugins/quenching/assets/bin/skills.py`.

- `python3 $SK drift --json` — three tools reported with `installed`, `shipped`, `status` and
  `executes`; exit **0** once this repo's copies are current and `okf-validate.py` is wired.
- Deliberate regression, in a scratch workspace and never in this repo: a stub copy one version
  behind → exit **1** with `sk-tool-behind`; one version ahead → `sk-tool-ahead`; the tool removed →
  `sk-tool-absent`; the `hooks` block emptied → `sk-tool-unwired`. A clean control fixture must fire
  **nothing**.
- `python3 .claude/hooks/skills.py drift` — exit **2**, refusing and naming `--plugin-root`.
- `python3 $SK selftest` — the drift fixture passes alongside the existing ones.
- `python3 $SK --root plugins/quenching doctor --json` — still 25 commands, no findings.
- `python3 plugins/quenching/assets/hooks/okf-validate.py docs` — 0 errors after the standard lands.
- `./assets/bin/functional-checks.sh` from `plugins/quenching/` — exit **0**, every assertion,
  including the new one. This is the ONLY check that a `commands/**` edit actually loads.

## Design

**1. It lives in `skills.py`, not in a fourth script.** `.claude/hooks/**` and
`.claude/settings.json` *are* the `.claude/` front, which `skills.py` already owns — it already
reads both settings files and runs the hook ladder over them. A fourth script would add a seventh
artifact to the six-artifact lockstep, and partial bumps of that set are the cause this spec exists
to notice.

**2. Truth is read at runtime, never hardcoded.** `drift` reads `<plugin-root>/VERSION` and invokes
`--version` on each installed copy. A version constant embedded in `drift` itself would be a fourth
string to keep in lockstep: a check that can drift is not a check.

**3. Plugin-root resolution, and the refusal.** `--plugin-root` when given; otherwise derived from
`__file__` (`assets/bin/skills.py` → the parent holding `VERSION`). An installed copy under
`.claude/hooks/` has no such parent and **exits 2** naming `--plugin-root`. The one outcome worse
than silent drift is a stale copy answering "all current".

**4. Both directions, and the copy that actually runs.** Per tool: `current` · `behind` · `ahead` ·
`absent` · `unreadable`, plus which copy a command will execute. `ahead` is a genuine finding
because resolution is **plugin-first**
([plans-zone.md](plugins/quenching/assets/references/specs-create/plans-zone.md) §Resolving the
tool) while each align deliberately **leaves a newer copy alone** — so an ahead copy is code that
is never executed and never repaired, and both halves of that are correct behaviour saying nothing.

**5. Wiring is asked only where it is meant.** `okf-validate.py` is a hook and must appear in a
`hooks` block. `specs.py` and `skills.py` are CLIs invoked by command bodies, so their absence from
`settings.json` is normal and never a finding. Scoping it this way is what keeps discovery 1's ask
from manufacturing two false findings on every conformant repo.

**6. Codes join the existing `sk-` vocabulary.** `sk-tool-behind` (error — a stale copy answers a
different CLI contract), `sk-tool-ahead` (warn — correct code, never executed), `sk-tool-absent`
(warn), `sk-tool-unwired` (error — installed and inert, `okf-validate.py` only).

**7. The exit contract is unchanged**: `0` ok · `1` findings · `2` refusal, with `--json` the
machine surface. Every caller branches on the code and the payload, never on prose.

**Binding contracts this design must not contradict**:
[versioning-release.md](docs/standards/ci-cd/versioning-release.md) (six strings, one number; the
tools may not import each other, because each installs standalone),
[plans-zone.md](plugins/quenching/assets/references/specs-create/plans-zone.md) §Resolving the tool
(plugin path first; write the resolved path literally on every invocation),
[align-surface.md](docs/standards/architecture/align-surface.md) (one align per front, probe
first), and [plugin-layout.md](docs/standards/architecture/plugin-layout.md) (`commands/**` is the
only registered tree).

## Alternatives Considered

| Approach | Cost | What it buys | Why it lost |
| --- | --- | --- | --- |
| **A. `drift` on `skills.py`** (chosen) | one subcommand, one selftest fixture, four probe edits | one payload, both directions, wiring answered, runnable by hand | — |
| **B. A standalone `assets/bin/drift.py`** | a **seventh** artifact in the version lockstep, a fourth install target | slightly cleaner ownership | it adds one more thing to bump in lockstep, which is the exact failure it was written to notice |
| **C. Prose-only — extend each align's install step** | three prose edits, no code | cheapest to write | the status quo. Three copies of the rule, still model-executed, still only inside an align — and the Problem already says running the aligns closes today's instance and restores tomorrow's silence |
| **D. A `SessionStart` hook that reports drift every session** | always-on cost in every target repo, wiring in every target | nobody has to remember | it cannot fire in the repository whose hooks block is empty — precisely the case being detected — and an unasked-for report every session is the always-on cost the plugin refuses elsewhere |
| **E. Do nothing; run the three aligns periodically** | zero | zero | it is what has been happening. This repo ran 1.0.0 against 4.2.0 for months |

## Open Decisions

- **Should `sk-tool-absent` be a finding at all?** A target that uses the plugin and never installs
  a copy is legitimate — resolution is plugin-first, so it loses nothing. *Decided by* running
  `drift` against this repo and one plugin-only scratch target in task 2.2: if plugin-only proves to
  be the ordinary case, `absent` drops out of the findings list into the report body, and the code
  is removed rather than demoted.
- **Should `drift` also compare the three operator manuals' banner versions?** *Decided by* the
  first target where a stale `QUENCHING.md` actually misleads someone. Until that exists, a manual
  is prose a human may have edited on purpose and "behind" would be noise — recorded in
  `## Out of Scope` so the idea is not silently dropped.

## Risks

- **The checker becomes a fourth thing that drifts.** Mitigated by design decision 2: `drift` reads
  `<plugin-root>/VERSION` and each copy's `--version` at runtime and hardcodes nothing, so there is
  no constant to forget.
- **A stale installed `skills.py` is asked to report drift and answers from its own old `VERSION`.**
  Mitigated by decision 3's exit-2 refusal, and by every caller passing `--plugin-root` explicitly.
- **Wiring detection is a substring match** over the command strings in `settings.json`, so a hook
  invoked through a wrapper script reads as unwired. **ACCEPTED** — the plugin ships exactly one
  wiring form (`settings.snippet.json`), a false "unwired" is loud and costs one dismissal, and a
  false "wired" would hide the precise failure this spec exists to catch.
- **The subcommand ships without a version bump, so installed copies will not have it.** **ACCEPTED
  and load-bearing** — the check must run from the plugin copy anyway (decision 3), so an installed
  copy never needs `drift`. The bump happens on the next release under
  [versioning-release.md](docs/standards/ci-cd/versioning-release.md).
- **Four command bodies change, and nothing in-session proves they still load** — the registry is
  built at session start. Mitigated by task 3.3: `functional-checks.sh` is the only check for a
  `commands/**` change, and it runs in a fresh process.
- **The probe gets more expensive.** One extra `Bash` call in each align's probe, against a
  probe-first contract whose whole claim is that a conformant front costs two or three calls.
  **ACCEPTED** — one call answers a question no other call in the probe answers, and it is a
  subprocess, not an inference.

## Handoff

- Work happens on `plan/notice-installed-tool-version-drift`, in the worktree beside the repo.
- `skills.py` already reads `settings.json` + `settings.local.json` and runs the hook ladder over
  both — reuse that reader; do not add a second one.
- Subcommands register through `register(name, add_args, cmd_fn)`; `--json` is added for every
  subcommand by `build_parser`, so do not add it by hand.
- Findings are built by `finding(code, severity, message, ...)` with a `remedy:` naming the command
  that fixes it. Severity is `error` or `warn` only.
- The three tools may **not** import each other — each installs standalone.
- Every `Bash` invocation writes the resolved interpreter+path literally; never `$VAR` as a command
  (zsh does not word-split, and the failure is silent).

## Tasks

### 1. The check

- [x] 1.1 Add the `drift` subcommand to skills.py: `--plugin-root` argument, derivation from `__file__`, and the exit-2 refusal when neither resolves a directory holding `VERSION`
      files: plugins/quenching/assets/bin/skills.py
      pattern: plugins/quenching/assets/bin/skills.py (the `register("budget", …)` block and `cmd_budget`)
      verify: python3 plugins/quenching/assets/bin/skills.py drift --json; python3 plugins/quenching/assets/hooks/skills.py 2>/dev/null; true
      subject: plan/notice-installed-tool-version-drift: 1.1 Add the drift subcommand with plugin-root resolution and the exit-2 refusal
- [x] 1.2 Compare each of the three tools in both directions — `current`/`behind`/`ahead`/`absent`/`unreadable` — reading `<plugin-root>/VERSION` and each installed copy's `--version` at runtime, and report which copy a command will execute
      files: plugins/quenching/assets/bin/skills.py
      verify: python3 plugins/quenching/assets/bin/skills.py drift --json
      subject: plan/notice-installed-tool-version-drift: 1.2 Compare the three tools in both directions, with the copy that executes
- [x] 1.3 Answer the wiring question for okf-validate.py only, over settings.json and settings.local.json, reusing the existing settings reader
      files: plugins/quenching/assets/bin/skills.py
      verify: python3 plugins/quenching/assets/bin/skills.py drift --json
      subject: plan/notice-installed-tool-version-drift: 1.3 Answer the wiring question for okf-validate.py over both settings files
- [ ] 1.4 Emit the findings under the `sk-` vocabulary — `sk-tool-behind` (error), `sk-tool-ahead` (warn), `sk-tool-absent` (warn), `sk-tool-unwired` (error) — each with a remedy naming the align that fixes it, and hold the 0/1/2 exit contract
      files: plugins/quenching/assets/bin/skills.py
      verify: python3 plugins/quenching/assets/bin/skills.py drift --json; echo "exit $?"

### 2. Proof

- [ ] 2.1 Add the drift selftest fixture — a clean control plus one case per code — so the rule is proved against a fixture and not against whatever this repo happens to hold
      files: plugins/quenching/assets/bin/skills.py
      pattern: plugins/quenching/assets/bin/skills.py (WIDER_FIXTURE / HOOK_FIXTURE)
      verify: python3 plugins/quenching/assets/bin/skills.py selftest
- [ ] 2.2 Run drift against this repo and a plugin-only scratch target, and settle the `sk-tool-absent` Open Decision with what they show
      verify: python3 plugins/quenching/assets/bin/skills.py drift --json

### 3. Wiring into the surface

- [ ] 3.1 Add the drift call to /align step 1's probe, reporting it with the three front probes
      files: plugins/quenching/commands/align.md
- [ ] 3.2 Make the three aligns' install steps consume the drift payload instead of restating a `--version` comparison
      files: plugins/quenching/commands/docs/align.md, plugins/quenching/commands/specs/align.md, plugins/quenching/commands/skill/align.md
- [ ] 3.3 Add a functional-checks.sh assertion that a fresh session's probe actually issues the drift call
      files: plugins/quenching/assets/bin/functional-checks.sh
      verify: cd plugins/quenching && ./assets/bin/functional-checks.sh

### 4. Docs

- [ ] 4.1 Write the drift half of docs/standards/ci-cd/versioning-release.md — both directions, the plugin-copy rule, and wired-versus-installed (authority: current once proved)
      files: docs/standards/ci-cd/versioning-release.md, docs/index.md, docs/standards/index.md, docs/log.md
      verify: python3 plugins/quenching/assets/hooks/okf-validate.py docs

### 5. Close

- [ ] 5.1 Run the whole shipped-skeleton verification block from CLAUDE.md and report each result
      verify: python3 plugins/quenching/assets/bin/skills.py --root plugins/quenching doctor --json

## Discoveries

- Confirmed again 2026-07-28 during an /align run, with a SECOND silent failure mode this Problem does not cover: the installed okf-validate.py and specs.py were 1.0.0 against a plugin at 4.2.0, but .claude/settings.json carried NO hooks block at all — the scripts sat on disk with nothing invoking them, so deleting all three changed no behaviour, which is precisely why nobody noticed. A drift check that only compares --version would have caught 1.0.0-vs-4.2.0 and still missed that the hook was inert. Whatever notices drift should also answer 'is this tool actually wired?' (for okf-validate.py: a hooks block in settings.json referencing it — one cheap JSON read). Note too that /docs:align's install is step 5, 'pass 1 only, offered', so on this repo the offer never fired at all. -> folded: ## Proposal and ## Design decision 5 — wiring is answered, not assumed, and asked only for okf-validate.py, the one tool that is a hook
- Drift is silent in BOTH directions, and the reverse case is invisible to a --version comparison alone: every command resolves the plugin path FIRST and the installed copy only as fallback (plans-zone.md 'Resolving the tool'), while each align refuses to overwrite a NEWER installed copy — so a repo whose .claude/hooks/ copy is ahead of the loaded plugin runs the older plugin code silently, and the align reports nothing because leaving the newer copy alone is its correct behaviour. Whatever notices drift should report the comparison in both directions and name which copy the commands will actually execute. -> folded: ## Design decision 4 — three statuses plus the executing copy, with `ahead` a real finding rather than a nicety
- Design decision 2 said drift would invoke --version on each installed copy; the implementation READS the VERSION constant instead. Running the copy would execute whatever sits in a target's .claude/hooks/ from inside a read-only probe — a much larger claim than reading three lines, and it needs python3 on PATH. A copy too old to declare a constant reads 'unreadable', which carries the same call to action as 'behind', so nothing is lost. Deviation taken deliberately at task 1.2.
- drift compares an installed copy against the SHIPPED TOOL's own VERSION constant, not against the plugin's VERSION file, because the constant is what an install would put on disk. That leaves the lockstep's own failure — a tool whose constant was not bumped with the VERSION file — unchecked by drift. It is one comparison away (plugin VERSION vs each shipped tool's constant) and worth a follow-up spec.
