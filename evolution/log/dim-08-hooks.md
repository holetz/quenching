# Dimension 8 — hooks

> Part of the `quenching-management` evolution log. Index, anchor state, and backlog: [../README.md](../README.md). ID convention (R*/Rev*) and routing: [README.md](README.md).
>
> This file collects the rounds (`R*`) and revisions (`Rev*`) that touched **hooks: continuous audit surface and exit semantics**.

## Current state

> Active summary of each boundary in this dimension (what is valid today). Detail and rationale are in the history below.

- **R36 · VALIDATION Stop hook «before completing» that CALLS the script from the `scripts/` taxonomy** *(dim 8 · materialises the thin-hook-calls-script doctrine of R35 — cross-ref [dim-08-scripts.md](dim-08-scripts.md))* —
  the package now **carries** [`assets/hooks/run-validation.py`](../../plugins/claude-quenching/skills/quenching-management/assets/hooks/run-validation.py) — a portable
  Stop hook that, at **the end of the turn**, **invokes a validation script DERIVED from the target** (`validateScript`/`validateCmd`,
  in the `scripts/checks`/`ci` home of the R35 taxonomy) on the **changed files** (`git status --porcelain`,
  filtered by `includeGlobs`) and **returns the result in an actionable way**. It is the **consumer** that proves
  the R35 boundary: the **hook is THIN and CALLS the script** — validation logic **does not live in the hook**,
  it lives in `scripts/`. **Portability by construction** (same as `protectedGlobs` of R25 × `conventionsFile`
  of R20): `validateScript`/`validateCmd` **empty ⇒ hook INERT**; the trio **`ruff check --fix` + `ruff format`
  + `pyright`** is the **documented EXAMPLE** for a Python repo (in the `$comment`/docstring/README of the
  `scripts/checks` slot), **NEVER** embedded as a fixed path/binary (a Go repo wires `go vet`/`gofmt`; a TS
  repo wires `tsc`/`eslint --fix`). **Event + power:** Stop hook (matches the "Development validation
  (mandatory)" section of CLAUDE.md — runs **once at the end of the turn** = batch "fix ALL", and is the
  **official pattern** for "a hook that sees every file change": *«add a Stop hook that scans the working tree
  once per turn… `git status --porcelain`»*); **default PROPOSES** the result via `additionalContext` with
  **exit 0** — `ruff --fix`/`format` mutate **code** (not the knowledge base), consistent with R28 (hook
  OBSERVES/PROPOSES, never mutates the base alone); **configurable blocking mode** `blockOnFail` (OFF by
  default) uses `decision: block`/`reason` (legacy form `exit 2` via `blockMode`) for the «mandatory/never
  skip» semantics — the docs state: for Stop, *«the `reason` is fed back to Claude so it keeps working»*.
  Guard `stop_hook_active` (cap of 8), latency ceiling. Wired in `settings.snippet.json` (2nd hook in the
  `Stop` block, `timeout: 15`) + `runValidation` block in `hooks-config.json`. **Distinct from R19**
  (Stop/PROPOSES-knowledge-delta by reading the transcript) — this one is Stop/CALLS-external-validator on
  the git-diff. Propagated to `dimensions-template.md`, `ARCHITECTURE.md` (5→6 hooks), `installation.md`,
  `assets/README.md`, `assets/scripts/checks/README.md`. No detection rule (8b) changed. (round 36)

- **R26 · Hook WIRING doctrine + orphan/dangling hook smell** *(core/installation × dim 8)* —
  until R25 the package **carried** 5 hook payloads (Stop/SessionStart/ConfigChange/PostToolUse/PreToolUse)
  + 2 legacy ones from CLAUDE.md, but **a hook only RUNS if it is wired** in the target's `settings.json`
  (docs verbatim: *«a script file alone does nothing»*) — the **installation/merge doctrine** for that
  wiring and the detection of a hook that does not fire were missing. R26 closes this gap **without a new
  payload**: (a) in [`installation.md`](../../plugins/claude-quenching/skills/quenching-management/references/installation.md), section «Hook wiring — merge the
  snippet, do not overwrite»: the [`settings.snippet.json`](../../plugins/claude-quenching/skills/quenching-management/assets/hooks/settings.snippet.json) is a
  **FRAGMENT to MERGE**, not `cat >`: arrays by **event/matcher concatenate** (same matcher ⇒ append to
  `hooks[]`), **never clobber** what the target already wired; **scope choice** (`~/.claude/settings.json`
  user × `.claude/settings.json` project **checked-in** × `.claude/settings.local.json` **gitignored**)
  by the precedence **Managed > CLI > Local > Project > User**; the R7 fact that project settings **load
  only from the start directory, do not inherit from parents** (monorepo ⇒ each start-subfolder needs its
  own); make the script **executable** (`chmod +x`) and the path **portable** (`${CLAUDE_PROJECT_DIR}`,
  never absolute); verify the wiring **1:1**. (b) in [`detection-and-smells.md`](../../plugins/claude-quenching/skills/quenching-management/references/detection-and-smells.md)
  block **8b** + dim 8 of the template, the **orphan hook** smell (script in `.claude/hooks/` WITHOUT an
  entry in `settings.json` ⇒ **inert**, never fires — e.g., `protect-generated.py` copied but not wired,
  and the generated artifact remains editable), **dangling hook** (entry in `settings.json` pointing to a
  **non-existent** script) and **wrong event/matcher** (blocking in PostToolUse that does not actually
  block; `compact`-survival wired to `startup`), + the **snippet overwriting instead of merging** smell.
  **Distinct from R7** (exit semantics / 3 lifecycle hooks — *which* hooks and *how they exit*) **and from
  R19-R25** (each authored a hook PAYLOAD — the *scripts*): R26 is the **installation/wiring doctrine**
  that makes the payloads actually **run**. Wiring greps (HOOK-ORPHAN/HOOK-DANGLING) **PENDING measurement
  vs. fixtures** (no Bash). (round 26)

- **R25 · PreToolUse hook that PROTECTS generated artifacts as an installable PAYLOAD (dim 8 × dim 14 — enforcement)**
  *(reconciled from R24 — number taken in parallel by dim-02)* —
  the package now **carries** the **first and only ENFORCEMENT payload** in the surface:
  [`assets/hooks/protect-generated.py`](../../plugins/claude-quenching/skills/quenching-management/assets/hooks/protect-generated.py) — a portable, read-only
  PreToolUse hook, matcher `Write|Edit`. Runs **before** the tool (the exit-codes table marks PreToolUse
  **«Can block? Yes»** / *«Blocks the tool call»*) and, when the Write/Edit destination matches a
  **generated/protected artifact** pattern of the target (`protectedGlobs` — `*.job.yml`/manifests/
  AUTO-GENERATED catalogue/lockfile, **derived from the target in Step 1, NEVER paths from this repo**;
  empty list ⇒ hook inert), **BLOCKS** the edit. It is the **enforcement complement of R23**: the
  PostToolUse `propose-docs-home` PROPOSES *after*; this one BLOCKS *before* — the method's doctrine
  ("keeps generated artifacts intact") and the «X defines Y» rule (the source is the truth, the generated
  is disposable) enforced by code, not by relying on the LLM's judgment. Docs rigour embedded: (a) **modern
  form** `hookSpecificOutput.permissionDecision: "deny"` + `permissionDecisionReason` with **exit 0** —
  *«With `deny`, Claude Code cancels the tool call and feeds `permissionDecisionReason` back to Claude»*;
  wins **even in** `bypassPermissions`/`--dangerously-skip-permissions` (*«PreToolUse hooks fire before any
  permission-mode check»*), enforcement the user cannot bypass by switching mode; **legacy form** `exit 2`+
  stderr via `denyMode: "exit2"`, **never mixed** (*«Claude Code ignores JSON when you exit 2»*); (b)
  input `tool_name`/`tool_input.file_path`; (c) **ACTIONABLE reason** (dim 14/R11) — names the
  **source-of-truth** that generates the artifact and instructs editing it (`sourceHint` per glob), never
  mute code; without it the agent blindly retries editing the generated artifact (loop); (d) **latency
  ceiling** (`deadlineMs` ~100 ms, only `fnmatch` on string, no I/O — PreToolUse fires on every
  Write/Edit); (e) hook is **executable code** (pre-trust vector), so read-only. Wired in
  `settings.snippet.json` (`PreToolUse` block, matcher `Write|Edit`, `timeout: 5`) + `protectGenerated`
  block in `hooks-config.json`. **Distinct from R19/R20/R21** (lifecycle) **and from R23** (PostToolUse,
  «Can block? No», proposes): this is PreToolUse, **before** the tool, **blocks**. Propagated:
  `dimensions-template.md` (dim 8 «good» — PreToolUse «Can block? Yes», deny/permissionDecisionReason,
  derived-from-target + smell "generated artifact editable without deterministic guard" + Payload; dim 14
  «good» "enforcement > probabilistic safeguard" + Payload), `installation.md` (gap→payload line) and
  `assets/README.md` (inventory). No detection rule (8b/14b) changed — the glob matching is a runtime
  trigger of the hook, outside the harness; no Bash in context to run (like R18-R23). (round 25)

- **R23 · PostToolUse hook covering the `docs/` taxonomy as an installable PAYLOAD (crosses dim 2 × dim 8)** —
  the package now **carries** the **first TOOL-EVENT hook** (distinct from the three lifecycle ones of
  R19/R20/R21): [`assets/hooks/propose-docs-home.py`](../../plugins/claude-quenching/skills/quenching-management/assets/hooks/propose-docs-home.py) —
  a portable, read-only PostToolUse hook, matcher `Write|Edit`. When the agent writes/edits a file
  **under `docs/`** (reads `tool_input.file_path`), it checks the **touched file** against the canonical
  taxonomy (dim 2, Rev1-Rev3) and **PROPOSES** (never blocks) the fix — home in a **variant name** to
  migrate (VARIANT), **two homes** coexisting (TWO-HOMES), material **without a home** (NO-HOME), binary
  outside the slot (OUT-OF-SLOT), slot binary **without sidecar** (NO-SIDECAR), doc **without**
  audience/authority **label** (NO-LABEL). It is the continuous audit (R7) applied to the canonical
  taxonomy at runtime, **reusing the same criteria as block 2b** of `detection-and-smells.md` — it does not
  invent a new smell or change a detection rule. Docs rigour embedded: (a) PostToolUse fires *"After a
  tool call succeeds"*, matcher = tool name, input provides `tool_name`/`tool_input.file_path`; (b)
  **PROPOSES via `additionalContext`, never `decision: block`** — PostToolUse is *"Can block? No"* and
  *"cannot undo actions since the tool has already executed"* (the `decision: block` here only *ends the
  turn* with a warning, without undoing the doc edit); (c) **stdout does NOT become context** in this event
  (goes to the debug log) ⇒ the proposal goes via **JSON `additionalContext`**, not raw text (mechanical
  distinction vs. R20/SessionStart); (d) **actionable error** (dim 14/R11) — each proposal says WHICH
  home/slot is missing and the **exact canonical name** to move/migrate to; (e) latency ceiling
  (`deadlineMs`, < ~500 ms — only one path + one `exists` + the file header). **Portability by
  construction:** the docs root is `docsDir` (default `docs`, derivable); the variant→canonical pairs are
  those of 2b. Wired in `settings.snippet.json` (2nd hook in `PostToolUse` block, matcher `Write|Edit`,
  `timeout: 5`) + `proposeDocsHome` block in `hooks-config.json`. **Distinct from R19/R20/R21** (lifecycle
  events — session moment) — this is a **tool event** (moment of a file edit) and materialises **trigger
  (1) "by event" of Step 8**, the last trigger still without a payload. Propagated: `dimensions-template.md`
  (dim 8 «good» — PostToolUse by tool event, «Can block? No», proposes via additionalContext, same 2b
  criteria; + Payload in dim 8 and cross-ref in dim 2), `installation.md` (gap→payload line) and
  `assets/README.md` (inventory). No detection rule (2b/8b) changed — the harness does not run. (round 23)

- **R21 · ConfigChange hook as installable PAYLOAD (audit-trail) — closes the R7 trilogy** — the
  package now **carries** the **third and last** lifecycle hook that R7 described:
  [`assets/hooks/audit-config-change.py`](../../plugins/claude-quenching/skills/quenching-management/assets/hooks/audit-config-change.py) — a portable
  ConfigChange hook. When something edits the surface during the session (a `settings.json`, a skill
  file), it **records an audit trail** (timestamp/source/file/session) in a **log derived from the
  target** — a new skill or a modified settings goes **noticed**. Docs rigour embedded: (a) the **5
  matchers/sources** verbatim (`user_settings`/`project_settings`/`local_settings`/`policy_settings`/
  `skills`), read from the `source` field; (b) **exit 0 always** — ConfigChange *can* block (`exit 2`,
  except `policy_settings`), but an audit trail **OBSERVES, never vetoes**; (c) **stdout does NOT become
  context** in this event (goes to the debug log) — so it writes to a **file**, not stdout (decisive
  distinction vs. R20/SessionStart); (d) latency ceiling (`deadlineMs`) and **only metadata** in the log
  (never the content/diff — config logs may contain secrets), append-only with size-based rotation.
  **Portability by construction:** the destination is `auditLog` (default `.claude/config-audit.log`,
  relative to `CLAUDE_PROJECT_DIR`), never hardcoded. Wired in `settings.snippet.json` (`ConfigChange`
  block, matcher of the 5 sources, `timeout: 5`) + `auditConfigChange` block in `hooks-config.json`.
  **Distinct from R19** (Stop, end of turn, PROPOSES new delta) **and from R20** (SessionStart,
  restart, RE-INJECTS what already exists): this is ConfigChange, at the moment of change, OBSERVES-and-
  RECORDS. With it, the **three** lifecycle hooks from R7 are all payloads — the trilogy is complete.
  Propagated: `dimensions-template.md` (dim 8 «good» — audit-trail observes/exit-0/stdout-not-context/
  metadata-log; and the **Payload** — the package carries all **three** hooks), `installation.md`
  (gap→payload line) and `assets/README.md` (inventory). No detection rule of dim 8 (8b) changed —
  the harness does not run. (round 21)

- **R20 · SessionStart-compact hook as installable PAYLOAD (compact-survival)** — the package
  now **carries** the **second** lifecycle hook that R7 deferred:
  [`assets/hooks/reinject-conventions.py`](../../plugins/claude-quenching/skills/quenching-management/assets/hooks/reinject-conventions.py) — a portable,
  read-only SessionStart hook. On restart (matcher `compact`/`clear`/`resume`; **not** `startup`)
  **re-injects** the stable layer (conventions/FQNs/guardrails/boundaries) that `/compact` would erase —
  the hook stdout **becomes context** (exit 0; plain text, without needing to build JSON).
  **Portability by construction:** reads from a **source derived from the target** — `conventionsFile`
  (default `.claude/conventions.md`) or, if absent, the **head of the root CLAUDE.md**
  (`$CLAUDE_PROJECT_DIR/CLAUDE.md`) — **never** a fixed conventions list from the package; change repo,
  re-injects the conventions of *that* repo. Latency ceiling (`maxBytes`/`deadlineMs` < ~500 ms) and
  silence on absent source/budget overflow. Wired in `settings.snippet.json` (SessionStart block,
  matcher `compact|clear|resume`, `timeout: 5`) + `reinjectConventions` block in `hooks-config.json`.
  **Distinct from R19** (Stop, end of turn, *PROPOSES* new delta via `additionalContext`): this is
  SessionStart, restart, *RE-INJECTS* what already exists. Propagated: `dimensions-template.md` (dim 8
  «good» — "reads from source derived from target, never a fixed list"; and the **Payload** — the package
  carries both complementary hooks), `installation.md` (gap→payload line) and `assets/README.md`
  (inventory). No detection rule of dim 8 (8b) changed — the harness does not run. (round 20)

- **R19 · Evolutionary Stop hook as installable PAYLOAD (automatic freshness)** — the package
  stops only **detecting the absence** of the lifecycle Stop hook and starts **carrying** it:
  [`assets/hooks/propose-knowledge-delta.py`](../../plugins/claude-quenching/skills/quenching-management/assets/hooks/propose-knowledge-delta.py) — the
  **automated** version of what the evolucionista does by hand. At the end of the turn it reads the
  **tail** of the transcript (`transcript_path` field) and, if the conversation exposed a gap (command
  Claude did not know, obsolete pattern, gotcha, env var), **PROPOSES** a CLAUDE.md/memory delta via
  `hookSpecificOutput.additionalContext` (which *continues* the conversation) with **exit 0 always** —
  **never** `decision: block` or `exit 2` (proposing ≠ blocking). Docs rigour embedded: guard
  `stop_hook_active` (exits early; the harness only caps after **8 blocks**), internal latency ceiling
  (`deadlineMs`/`maxTranscriptBytes`, < ~500 ms in the critical path), read-only (writes nothing;
  hook config is executable code = pre-trust vector) and actionable error (the proposal says **what**
  and **where** to record). Wiring in `settings.snippet.json` (2nd hook in the `Stop` event, `timeout: 5`)
  + `proposeKnowledgeDelta` block in `hooks-config.json`. **Materialises what R7 deferred** (R7 wrote the
  doctrine/detection and left "actually installing the three lifecycle hooks… rich payload as a future
  implementation item"); here the installable artifact is born. Propagated: `dimensions-template.md` (dim 8
  «good» — propose via `additionalContext`, never `exit 2`; and the **Payload** — the package **carries**
  the hook), `installation.md` (gap→payload line) and `assets/README.md` (inventory). No detection rule
  of dim 8 (8b in `detection-and-smells.md`) changed — the harness does not run. (round 19)

- **R7 · Hooks — continuous audit surface + exit semantics** — dimension 8 (hooks) stops
  being "command-exists + idempotent + timeout" and gains: the **continuous knowledge audit
  surface** (three lifecycle hooks — `SessionStart` matcher `compact` re-injects
  conventions/FQNs/guardrails after `/compact`; **evolutionary Stop hook** receives the transcript
  and **proposes** CLAUDE.md deltas «while the gap is fresh»; `ConfigChange` gives an audit trail
  of changes to the surface itself); the **exit semantics** (exit 2 blocks + stderr to model · exit
  1 only warns, does not block · exit 0 + JSON for rich decisions · exit 2 and JSON do not combine);
  the **guard `stop_hook_active`** in Stop hooks (cap of 8 blocks) and the ~500 ms ceiling in the
  critical path; the fact that `settings.json` **loads only from the start directory** (does not
  inherit from parents) and hook config is **executable code** (pre-trust vector, do not run
  destructive in SessionStart). Cross-cutting item **8b** in `detection-and-smells.md` (greps that
  only list candidates: presence of the 3 hooks · Stop without guard · `exit 1` in a blocking hook).
  No single owner (hook authoring is `quenching-config`; the **surface presence** and the
  enforcement×guidance boundary stay in the core). (round 7)

## Round and revision history

> Most recent rounds at the top. Revisions (`Rev*`) are nested under the round they refine.

### Round 36 — 2026-06-29 · boundary: VALIDATION Stop hook «before completing» that CALLS the script from the `scripts/` taxonomy (R35)

> **Round B of two coupled rounds.** Round A (R35, [dim-08-scripts.md](dim-08-scripts.md)) established the **home**
> `scripts/` (purpose-based taxonomy + scaffold + the thin-hook-calls-script doctrine). R36 **materialises the
> consumer**: the validation hook that stores the logic in that home and CALLS it. Permanent cross-ref between
> both contexts.

- **Change:** authored the payload [`assets/hooks/run-validation.py`](../../plugins/claude-quenching/skills/quenching-management/assets/hooks/run-validation.py) — **portable
  Stop hook** that, at the end of the turn, runs the "validation process before completing" by **invoking a SCRIPT**
  from the target: (1) collects **changed files** via `git status --porcelain` (the official pattern for "a hook
  that sees every file change"), filtered by `includeGlobs` (e.g., `*.py`); (2) builds the command of the
  **validator DERIVED from the target** — `validateCmd` (raw command, e.g., `["make","check"]`) **or** `runner`
  + `validateScript` (e.g., `python3` + `scripts/checks/validate.py`); **empty ⇒ returns without running
  anything (INERT)**; (3) passes the changed files as args (`passChangedFiles`) for scope/latency; (4)
  **default PROPOSES** the result via `hookSpecificOutput.additionalContext` with **exit 0** (reports that
  formatting/fix ran + tail of errors the validator raised + where), **`blockOnFail` mode** (off by default)
  returns `{"decision":"block","reason":<errors>}` (or `exit 2` via `blockMode`) for "mandatory/never skip".
  Guard `stop_hook_active`, `deadlineMs` (covers `git status` + the validator call), `maxOutputBytes` (output
  tail, does not flood the context). Wired: 2nd hook in the `Stop` block of `settings.snippet.json`
  (`timeout: 15`, `$comment` explaining thin-hook-calls-script / derived-from-target / proposes-vs-blocks) +
  `runValidation` block in `hooks-config.json` (with `$comment` instructing to derive from target and the
  Python example without hardcoding). **At the METHOD level** I documented the SLOT (did not ship a concrete
  `validate_py.py` — that would be Python coupling): `assets/scripts/checks/README.md` gained the section
  «The validation script that the `run-validation.py` hook calls» (validateScript + the ruff/pyright trio as
  an example of FORM). Propagated to `dimensions-template.md` (dim 8: line in the Payload table + `run-validation`
  cited in the «Canonical home of executable logic» block as the thin trigger), `ARCHITECTURE.md` (count 5→6
  hooks + line in the table + "one can block if configured"), `installation.md` (gap→payload), `assets/README.md`
  (inventory).

- **Why:** it was the **Next candidate** recorded by R35 (and designated by the user) — the use case that
  **proves** the R35 boundary («the hook is THIN and CALLS the script; the deterministic logic lives in
  `scripts/`»). It is a **new** boundary in the exclusion index, not a repetition of R19 (also Stop, but
  PROPOSES a CLAUDE.md delta by reading the **transcript**; this one CALLS an **external validator** on the
  **git-diff**) or of R35 (which established the home and the doctrine; this is the **consumer payload**).
  The key choices, anchored in the docs, maintain the self-contained invariant:
  (1) **GENERIC runner, not hardcoded ruff/pyright trio** — `validateScript`/`validateCmd` derived from the
  target, empty = inert (identical to the pattern of `protectedGlobs`/R25 and `conventionsFile`/R20); the
  trio is only the **documented example** for a Python repo; (2) **Stop hook** because it matches the
  "Development validation (mandatory)" section of CLAUDE.md (end of turn, batch "fix ALL", less disruptive
  than per-edit PostToolUse that would run `pyright` repeatedly and fight the agent mid-task) **and** because
  it is the official pattern for scanning the working tree once per turn; (3) **default PROPOSES / exit 0**
  because `ruff --fix`/`format` **mutate CODE files** (not the knowledge base) and the R28 doctrine is hook
  OBSERVES/PROPOSES — enforcement-that-blocks was reserved for GENERATED artifacts (R25); the **blocking
  mode** exists but is **configurable and off**, using the Stop semantics where the `reason` feeds back to
  Claude (not a destructive veto); (4) **scope by changed files** (`git status --porcelain`) to respect the
  latency ceiling.

- **Sources:**
  - [Automate actions with hooks — Claude Code Docs](https://code.claude.com/docs/en/hooks-guide) — _official-anthropic · accessed 2026-06-29, ✅ WebFetch_. **Verbatim:** *«This example uses a separate script file that the hook calls»* (the thin-hook-calls-script doctrine, «Block edits to protected files» side); the «Auto-format code after edits» example — PostToolUse `Edit|Write`, *«so it runs only after file-editing tools… The command extracts the edited file path with jq»* (the canonical pattern for a hook that acts on the edited file, which **I discarded** in favour of Stop, see Rejected); **decisive for the event choice:** *«If your hook must see every file change… add a `Stop` hook that scans the working tree once per turn… list modified and untracked files with `git status --porcelain`»* (justifies Stop + git-status, exactly the design); the exit-code semantics *«Exit 0… For UserPromptSubmit… and SessionStart hooks, anything you write to stdout is added to Claude's context»* / *«Exit 2: the action is blocked»* / *«Don't mix them: Claude Code ignores JSON when you exit 2»*; for Stop, *«the `reason` is fed back to Claude so it keeps working»* (justifies blocking mode via `decision: block`/`reason`); the Stop agent-hook example *«verifies that tests pass before allowing Claude to stop»* (confirms "validate at end of turn" pattern); the loop guard — *«Claude Code overrides a Stop hook after it blocks 8 times in a row… Parse the `stop_hook_active` field… exit early if it's `true`»*; `${CLAUDE_PROJECT_DIR}` to reference scripts and `chmod +x`.
  - Catalogue: [`research/03-hooks.md`](../research/03-hooks.md) — PostToolUse formatting is idempotent by nature; keep hooks < ~500 ms; *«hooks fire for subagent actions»* (validation covers delegated edits).
  - Home cross-ref: R35 in [dim-08-scripts.md](dim-08-scripts.md) (the `scripts/checks`/`ci` taxonomy where the `validateScript` lives).

- **Rejected/superseded:**
  - **PostToolUse `Write|Edit`** (run on every edit, the canonical «Auto-format code after edits» example) — discarded as primary event: running `pyright` **per file on every Write/Edit** is expensive and **fights the agent mid-task** (formats/reverts while it is still editing); Stop gives the batch "fix ALL" at the end, which is what the "mandatory validation" section of CLAUDE.md describes. (Per-edit formatting remains possible: the repo can wire its own `prettier --write` PostToolUse; this payload is the **end-of-turn** one.)
  - **Hardcoded `ruff`/`pyright` trio in the hook** — **would violate the portable invariant** (would couple to Python); the hook reads `validateScript`/`validateCmd` from the target, empty = inert; the trio only in `$comment`/docstring/README as an example.
  - **Shipping a concrete `validate_py.py`** as payload in `assets/scripts/checks/` — same reason (Python coupling); the package documents the **slot**, the concrete script is born during application to the target (Steps 1-7).
  - **Blocking mode ON by default** — discarded: `ruff --fix`/`format` mutate code and the R28 doctrine is OBSERVES/PROPOSES; blocking the end of turn on a lint error would be disruptive and outside the contract (enforcement-that-vetoes is only for generated artifacts, R25). Remains **configurable and off** (`blockOnFail`).
  - **Parsing the validator output error-by-error** — Simplicity First: returns the **tail** of the output (`maxOutputBytes`) with the command name; the agent reads the linter output directly (already actionable).
  - **`jq`/external dependency** — pure Python, no dependency (like the sibling hooks).
  - **Eval note:** this round did **not** alter a detection rule (8b is the auditor; what the hook runs is a runtime trigger on the live git-diff, outside the fixture harness), so the minimal harness does not apply — and **there is no Bash in this context** for a smoke test (only Read/Edit/Write/Web/Grep/Glob), same situation as R18-R26; the logic is simple (git-status + subprocess + emit JSON) and the default path is read-only over the knowledge base.

- **Next candidate.** "Internal plugin/marketplace as a rollout vehicle for payloads" (package hooks/command/skills as a versioned plugin — `hooks/hooks.json` activates the wiring **together** with the plugin, resolving the manual merge that R26 doctrines; the **distribution** axis is the only one still without a payload, now that command + 3 lifecycle hooks + PostToolUse + PreToolUse + Stop-validation are done) **or** "Event-based hook applied to `.claude/` (the config surface), not just `docs/`" (PostToolUse that reruns detection of dims 6/7/8/9 for the touched config scope and **proposes**; distinct from R21/ConfigChange which only records).

### Round 26 — 2026-06-29 · boundary: Hook WIRING doctrine + orphan/dangling hook smell

> Next free number after R25 (current-round marked 25 at start; the parallel dim-02 evolution did not
> take 26). No reconciliation needed.

- **Change:** introduced the **hook installation/wiring doctrine** (which makes the 5 payloads of R19-R25
  actually run) **without a new payload** — only doctrine + smell + refined «good», across 3 shared files:
  (1) **`references/installation.md`** — Step 4 of the procedure rewritten ("**wire** the command… a hook
  only runs if wired") + **new section «Hook wiring — merge the snippet, do not overwrite»** with 5 points:
  [a] `settings.snippet.json` is a **FRAGMENT to MERGE** (arrays by event/matcher **concatenate**; same
  matcher ⇒ append to `hooks[]`; **never clobber**), canonical structure `Event → matcher-group →
  hooks[]`; [b] **scope choice** (project checked-in default × local gitignored override × user
  unversioned) by the precedence **Managed > CLI > Local > Project > User**; [c] R7 — project settings
  **load only from the start directory, do not inherit from parents** (monorepo ⇒ one settings per
  start-subfolder); [d] **`chmod +x`** + portable path **`${CLAUDE_PROJECT_DIR}`** (never absolute); [e]
  verify wiring 1:1. (2) **`references/detection-and-smells.md` block 8b** — new greps **HOOK-ORPHAN**
  (script in `.claude/hooks/` without entry in `settings.json`/`settings.local.json` via `$WIRED`) and
  **HOOK-DANGLING** (entry pointing to a non-existent script) + reading paragraph «Wiring — orphan/
  dangling/wrong event». (3) **`dimensions-template.md` dim 8** — «good» gains the block «Wiring — a
  hook only RUNS if wired» (merge≠overwrite, ${CLAUDE_PROJECT_DIR}, chmod +x, scope precedence); Smells
  gain **orphan hook / dangling / wrong-event-matcher / snippet overwriting instead of merging**;
  Detection points to wiring 1:1; Remediation instructs wiring the orphan (merge without clobber) /
  removing the dangling. Conceptual diff: dimension 8, which until R25 covered *which* hooks to have,
  *how they exit* (exit codes), and *which* ones the package carries (payloads), now covers the missing
  link — **whether the payload is actually wired and firing**. Without this, installing `protect-generated.py`
  is theatre: the script exists and the generated artifact remains editable.
- **Why:** it was the suggested boundary and the **real gap** the user felt — the method now CARRIES 5
  hook payloads (+2 legacy ones), but no round had doctrined **how to wire them** in the target's
  `settings.json` or detected the silent case where a script was copied but not wired (does nothing). It
  is a **new** boundary in the exclusion index: **distinct from R7** (which established exit semantics
  and *described* the 3 lifecycle hooks — the «what» and «how it exits», not the wiring/merge) and
  **distinct from R19-R25** (each authored a hook *payload* — the *script*; none addressed the
  installation/merge doctrine or the orphan/dangling smell). The key choices come from the docs and keep
  the method portable: (1) **merge, never overwrite** (the docs show the nested event→matcher→hooks[]
  structure; the package snippet already warns "Merge with existing blocks; do not overwrite the whole
  file"); (2) **scope by precedence** and the project-does-not-inherit-from-parents fact (R7/docs) —
  critical in monorepo; (3) **`${CLAUDE_PROJECT_DIR}` + chmod +x** (the docs mandate the placeholder
  and `chmod +x`), preserving the portable invariant (nothing hardcoded). Preferred **doctrine + refined
  «good»** over many greps (only 2 wiring greps, both marked PENDING).
- **Sources:** [Claude Code settings — Claude Code Docs](https://code.claude.com/docs/en/settings)
  (accessed 2026-06-29, ✅ verified by WebFetch) — **verbatim** the precedence *"1. Managed (highest)…
  2. Command line arguments… 3. Local… 4. Project… 5. User (lowest)"*, and the git handling: **project
  settings** `.claude/settings.json` *"Checked into source control and shared with team"*, **local**
  `.claude/settings.local.json` *"Gitignored… Claude Code configures git to ignore the file"*, **user**
  `~/.claude/settings.json` *"Not shared, local to user only"*; [Hooks reference — Claude Code Docs](https://code.claude.com/docs/en/hooks)
  (accessed 2026-06-29, ✅ verified by WebFetch) — **verbatim** the JSON structure `hooks: { PreToolUse:
  [ { matcher, hooks:[ {type:"command", command, …} ] } ] }`, the placeholder **`${CLAUDE_PROJECT_DIR}`**
  ("Project root") with the portability note exec-form, **«a script file alone does nothing»** / *"This
  example runs a linting script only when… "* (the script only acts via the entry in `settings.json`), and
  *"Make the script executable: `chmod +x .claude/hooks/…`"*; R7 anchor: [Set up Claude Code in a monorepo
  or large codebase — Claude Code Docs](https://code.claude.com/docs/en/large-codebases) (via R7) —
  *"Project settings in `.claude/settings.json` load only from your starting directory and are not inherited
  from parent directories"*.
- **Rejected/superseded:** discarded **authoring a new payload** (e.g., a `wire-hooks.py` installer that
  does the merge automatically) — the method **never edits `settings.json` without confirmation** (Step 5)
  and an automatic JSON-merge is speculative complexity (Simplicity First); the doctrine + the snippet with
  `$comment` already guide the manual merge, and the eventual auto-merge stays as a "Plugin/marketplace"
  candidate (which wires `hooks/hooks.json` together). Discarded **many new greps** in 8b — preferred
  doctrine + two essential greps (orphan/dangling); the "wrong event/matcher" stays as a **read** (a grep
  that understands event semantics would be fragile). Discarded **moving the snippet** or rewriting
  `settings.snippet.json` — it is already a fragment and already warns to merge; R26 only **doctrines how**
  to merge (does not touch the payload, which belongs to another round). Discarded touching any docs/dim-02
  file (concurrency). **Eval note:** the two new wiring greps (HOOK-ORPHAN/HOOK-DANGLING) are **detection
  rules** (enter 8b/harness), so **PENDING measurement vs. fixtures** — **there is no Bash in this context**
  (only Read/Edit/Write/Web/Grep/Glob); recorded in the spine review queue as R22/R23/R25 did. The risk to
  measure: HOOK-ORPHAN firing falsely on `hooks-config.json`/`settings.snippet.json` (already excluded by
  the `case`/glob `*.py|*.sh`) and `$WIRED` resolving relative paths vs. `${CLAUDE_PROJECT_DIR}/.claude/hooks/...`
  in the `command` (the `sed` extracts `.claude/hooks/<script>`, matching the `for f in .claude/hooks/*`
  — verify against a fixture).
- **Next candidate:** "Internal plugin/marketplace as a rollout vehicle for payloads" (package hooks/
  command/skills as a versioned plugin — `hooks/hooks.json` activates the wiring **together** with the
  plugin, resolving the manual merge that R26 doctrines; the **distribution** axis still without a payload)
  **or** "Event-based hook applied to `.claude/` (the config surface), not just `docs/`" (PostToolUse that
  reruns detection of dims 6/7/8/9 for the touched config scope and **proposes**; distinct from
  R21/ConfigChange which only records).

### Round 25 — 2026-06-29 · boundary: PreToolUse hook that PROTECTS generated artifacts as an installable PAYLOAD (dim 8 × dim 14 — enforcement)

> Reconciled from R24 → R25: the number R24 was taken in parallel by the dim-02 evolution
> (builder of the `standards/` layer); this round took the next free number, per the concurrent
> environment protocol.

- **Change:** authored the **first and only ENFORCEMENT payload** of the surface as a ready hook:
  **`assets/hooks/protect-generated.py`** (portable, read-only PreToolUse hook, matcher `Write|Edit`,
  without paths from this repo). In the `PreToolUse` event, reads `tool_input.file_path`; if the path
  (relative to root, or basename) matches one of the `protectedGlobs` (via `fnmatch`, no I/O), **BLOCKS**
  the edit: modern form `hookSpecificOutput.permissionDecision: "deny"` + `permissionDecisionReason`
  (exit 0); legacy form `exit 2`+stderr selectable via `denyMode`. The reason is **actionable** — names
  the **source-of-truth** that generates the artifact (glob map `sourceHint`; generic fallback citing the
  «X defines Y» rule) and instructs editing the source, not the generated one. `protectedGlobs`/`sourceHint`
  **empty by default** ⇒ hook **inert** (filled by deriving from target in Step 1). Wired in
  `settings.snippet.json` (PreToolUse block, matcher `Write|Edit`, `timeout: 5`, `$comment` explaining
  blocks-before/modern-deny-vs-exit2/derived-from-target) + `protectGenerated` block in `hooks-config.json`
  (`enabled`/`protectedGlobs`/`sourceHint`/`denyMode`/`deadlineMs`, with `$comment` instructing to derive
  from target and illustrating the FORM without paths from this repo). Conceptual diff: the package's hook
  surface, which until R23 only **PROPOSED/OBSERVED** (Stop proposes, SessionStart re-injects,
  ConfigChange records, PostToolUse proposes), gains the first hook that **DETERMINISTICALLY GUARANTEES**
  an invariant — keeping generated artifacts intact — closing the enforcement axis that dims 8/14 only
  **described** (R7 established the blocking semantics; R11 the actionable message; R25 materialises the
  payload that **uses** both to protect the generated artifact).
- **Why:** it was the explicit candidate for this round (the most important hook event for enforcement
  still **without a payload**: the `PreToolUse`) and the missing piece in the workflow+commands+hooks
  sequence — R18 the command, R19/R20/R21 the lifecycle trilogy, R23 the tool-event PostToolUse (PROPOSES),
  **R25 the tool-event PreToolUse (BLOCKS)**. Materialises the **enforcement** axis of dim 14 (which R11
  left in the template as a requirement) crossing dim 8: dimension 14 already said "deterministic limits >
  probabilistic safeguards" and the method's doctrine always forbade editing the generated artifact, but
  nothing **enforced** it by code — only the CLAUDE.md guidance, which the model can ignore. The key
  choices come from the docs and keep the payload correct and portable: (1) **modern deny** (not just
  `exit 2`) because it is the recommended form and the only one that **wins in `bypassPermissions`**
  (real enforcement); (2) **`protectedGlobs` derived from the target**, never paths from this repo,
  preserving the self-contained/portable invariant (empty list = inert); (3) **actionable reason pointing
  to the source-of-truth** (R11) so the agent fixes by editing the source, instead of blindly retrying
  the generated artifact; (4) **only string matching** (no I/O) for the latency ceiling, as PreToolUse
  fires on every Write/Edit. It is a **new** boundary in the exclusion index, not a repetition of R23:
  different event (PreToolUse × PostToolUse), different power (blocks × proposes), different target
  (generated artifact × docs/ taxonomy), different anchor dimension (14 enforcement × 2 docs).
- **Sources:** [Hooks reference — Claude Code Docs (PreToolUse)](https://code.claude.com/docs/en/hooks)
  (accessed 2026-06-29, ✅ verified by WebFetch) — **verbatim** *«Before a tool call executes. Can block
  it»*, the PreToolUse exit-codes table *«Yes»* / *«Blocks the tool call»*, the input
  `tool_name`/`tool_input` (+ common `session_id`/`transcript_path`/`cwd`/`hook_event_name`), the modern
  form `hookSpecificOutput.permissionDecision` with values `"deny"`/`"allow"`/`"ask"`/`"defer"` +
  `permissionDecisionReason`, the legacy form `exit 2`+stderr, and the stdout rule (*"stdout… not shown…
  exceptions are UserPromptSubmit, UserPromptExpansion, and SessionStart"* — PreToolUse is **not** an
  exception); [Automate actions with hooks — Claude Code Docs (guide, «Block edits to protected files»
  section)](https://code.claude.com/docs/en/hooks-guide)
  (accessed 2026-06-29, ✅ verified by WebFetch) — **verbatim** the canonical example *«Prevent Claude
  from modifying sensitive files like `.env`, `package-lock.json`, or anything in `.git/`. Claude receives
  feedback explaining why the edit was blocked, so it can adjust its approach»*, the `protect-files.sh`
  script reading `.tool_input.file_path`, matching against `PROTECTED_PATTERNS` and *«exits with code 2
  to block the edit»*, the `PreToolUse` registration with `matcher: "Edit|Write"`; **verbatim** *«With
  `deny`, Claude Code cancels the tool call and feeds `permissionDecisionReason` back to Claude»*,
  *«Don't mix them: Claude Code ignores JSON when you exit 2»*, and — decisive for "real enforcement" —
  *«PreToolUse hooks fire before any permission-mode check. A hook that returns `permissionDecision:
  "deny"` blocks the tool even in `bypassPermissions` mode or with `--dangerously-skip-permissions`»*;
  dim 14 anchor: [Writing effective tools for AI agents — Anthropic Engineering](https://www.anthropic.com/engineering/writing-tools-for-agents)
  (accessed 2026-06-29, ✅ verified by WebFetch, via R11) — actionable error that communicates the
  specific correction instead of opaque code (the deny reason points to the source-of-truth).
- **Rejected/superseded:** discarded **only the legacy `exit 2`+stderr form** (what the official example
  uses) — it works, but the modern `deny` form is recommended and the only one that **wins in
  `bypassPermissions`**; kept `exit 2` as a selectable fallback (`denyMode: "exit2"`), never both together
  (the docs forbid mixing). Discarded **hardcoding** the generated patterns (the literal
  `PROTECTED_PATTERNS=(".env"…)` from the example) — violates the portable invariant; `protectedGlobs`
  is derived from the target (Step 1), empty list = inert; examples only in `$comment`/docstring, without
  paths from this repo. Discarded **protecting `.env`/secrets** as the scope of this round — it is a
  distinct enforcement payload (security, not "generated × source"); the scope here is the «X defines Y»
  rule (disposable generated artifact). Discarded **using `permissionDecision: "ask"`** (escalate to the
  user) instead of `"deny"` — the doctrine is to *block* editing the generated artifact and redirect to
  the source, not ask for confirmation every time (Simplicity First; a user who wants to adjust changes
  `protectedGlobs`). Discarded **reading/parsing the content** of the target file — only the path matters
  (poka-yoke + latency ceiling); reading the file on every Write/Edit would be cost in the critical path.
  Discarded `jq`/external parser (the example uses `jq`) — pure Python, no dependency. Discarded
  materialising **also** the "Plugin/marketplace rollout" — one surgical evolution per round; stays as
  candidate. **Eval note:** this round did **not** alter a detection rule (8b/14b are the auditor; the
  hook's glob matching is a runtime trigger on the live event, outside the fixture harness), so the minimal
  harness does not apply — and **there is no Bash in this context** for a smoke test (only
  Read/Edit/Write/Web/Grep/Glob), same situation as R18-R23; the logic is simple (string matching) and
  read-only.
- **Next candidate:** "Event-based hook applied to `.claude/` (the config surface), not just `docs/`"
  (the other slice of trigger (1) of Step 8 — PostToolUse that reruns detection of dims 6/7/8/9 for the
  touched config scope and **proposes** the quality fix, distinct from R21/ConfigChange which only records)
  **or** "Internal plugin/marketplace as a rollout vehicle for payloads" (package hooks/command/skills as
  a versioned plugin — `hooks/hooks.json` activates together; the **distribution** axis still without a
  payload, now that command + 3 lifecycle hooks + PostToolUse + PreToolUse are done).

### Round 23 — 2026-06-29 · boundary: PostToolUse hook covering the `docs/` taxonomy as an installable PAYLOAD (crosses dim 2 × dim 8)

- **Change:** authored the **first tool-event hook** of the package as a ready payload:
  **`assets/hooks/propose-docs-home.py`** (portable, read-only PostToolUse hook, matcher `Write|Edit`,
  without paths from this repo). In the `PostToolUse` event, reads `tool_input.file_path`; if the file
  falls **under `docs/`** (derivable root via `docsDir`, default `docs`), applies to the **touched file**
  the **same criteria as block 2b** of `detection-and-smells.md` and builds **actionable proposals**: VARIANT
  (home in a variant name → migrate to canonical, with the variant→canonical pairs from 2b), TWO-HOMES
  (variant AND canonical coexisting → migrate one), NO-HOME (loose .md in the docs/ root or new subfolder
  outside canonical homes), OUT-OF-SLOT (binary outside `presentations/`/`reference/regulations/`),
  NO-SIDECAR (slot binary without `.md` alongside or cited in an index), NO-LABEL (.md without
  `audience`/`authority` in the header). Returns via `hookSpecificOutput.additionalContext` (JSON, exit
  0), `enabled`/`deadlineMs`/`maxFindings` in `proposeDocsHome`. Wired in `settings.snippet.json` (2nd
  hook in the PostToolUse block, matcher `Write|Edit`, `timeout: 5`, `$comment` explaining proposes-not-
  blocks/stdout-as-JSON). Conceptual diff: the package, which **detected** taxonomy gaps on the scan (2b)
  and **anticipated** the coverage hook (Step 8/R17, backlog item), now **carries** it as a runtime
  application of the SAME criteria, by event — closing **trigger (1) "by event" of Step 8**, the last
  trigger without a payload.
- **Why:** it was the "docs/ coverage hook" candidate from the advancement backlog and the **next
  candidate** pointed out by R21 — the step that **completes** the Step 8 trigger coverage: R17 made
  the doctrine (3 triggers: PR/event · release/cadence · on-demand command); R18 the command (trigger 3);
  R19/R20/R21 the lifecycle hook trilogy; **this round (R23) trigger (1) by event** — the hook that fires
  when the repo changes, applied to the `docs/` axis (crosses dim 2 × dim 8). Fits by construction with
  **R22** (which, in parallel, added the 9th canonical home `communications/`): the hook already recognises
  `communications` as a legitimate home and as the canonical destination of variants
  `comunicados`/`avisos`/… — both advances coexist without conflict. It is a **new** boundary in the
  exclusion index, not a repetition of R19/R20/R21: different **event type** (tool event × lifecycle event;
  moment of a file edit × restart/end-of-turn/config-change) and different target (the touched file × the
  session). The key choices come directly from the docs and keep the payload correct: (1) **PROPOSES,
  never blocks**, because PostToolUse is «Can block? No» (the tool has already executed) and blocking a
  doc edit would be the opposite of proposing; (2) **proposal via JSON `additionalContext`**, because
  stdout in this event does not become context; (3) **reuse the 2b criteria**, to avoid creating a
  parallel detection rule that would diverge from the auditor (single-source-of-truth: the hook is the
  runtime application of the 2b smells, not a second set).
- **Sources:** [Hooks reference — Claude Code Docs (PostToolUse)](https://code.claude.com/docs/en/hooks)
  (accessed 2026-06-29, ✅ verified by WebFetch) — **verbatim** the trigger *"After a tool call
  succeeds"*, the matcher by tool name (`"Edit|Write"`), the input fields `tool_name`/`tool_input.file_path`
  (+ common `session_id`/`transcript_path`/`cwd`/`hook_event_name`), the PostToolUse exit-codes table —
  *"Can block? No"* / *"Shows stderr to Claude (tool already ran)"* (justifies **not** blocking), the
  `hookSpecificOutput` fields for PostToolUse (`additionalContext` = *"String added to Claude's context
  at the point where the hook fired"*, `updatedToolOutput`) and the stdout rule *"stdout is written to
  the debug log but not shown… exceptions are UserPromptSubmit, UserPromptExpansion, and SessionStart"*
  (PostToolUse is **not** an exception ⇒ use `additionalContext`); [Automate actions with hooks — Claude
  Code Docs (guide)](https://code.claude.com/docs/en/hooks-guide) (accessed 2026-06-29, ✅ verified by
  WebFetch) — **verbatim** the canonical PostToolUse `matcher: "Edit|Write"` example extracting
  `.tool_input.file_path` (section *"Auto-format code after edits… runs only after file-editing tools…
  extracts the edited file path"*), the limitation *"PostToolUse hooks cannot undo actions since the tool
  has already executed"* (justifies proposing, not undoing), *"Text returned via `additionalContext` is
  injected as a system reminder that Claude reads as plain text"*, and the `decision: block`/`reason`
  semantics by event — for *"PostToolUse… the turn ends and the `reason` appears in the chat as a warning
  line"* (= it is not a veto of the edit; that is why we use exit 0 + `additionalContext`). Reused
  taxonomy spec: [docs-taxonomy.md](../../plugins/claude-quenching/skills/quenching-management/references/docs-taxonomy.md) and block 2b of
  [detection-and-smells.md](../../plugins/claude-quenching/skills/quenching-management/references/detection-and-smells.md) (the VARIANT/TWO-HOMES/NO-HOME/NO-SIDECAR/
  NO-LABEL criteria).
- **Rejected/superseded:** discarded **blocking** the edit (`decision: block`/`exit 2` to "bar a doc
  outside its home") — PostToolUse does not undo the tool (it has already executed) and blocking a doc
  edit is the opposite of proposing; moreover `decision: block` here only ends the turn with a warning.
  Discarded **printing the proposal to stdout** (like R20/SessionStart) — in this event stdout does not
  become context; it goes via `additionalContext`. Discarded **inventing new smells** or a second set of
  greps in the hook — I reused the 2b criteria (single-source-of-truth; a detector diverging from the
  auditor would be drift); hence **no detection rule (2b or 8b) changed**. Discarded **writing/moving**
  the file automatically — the method never renames/deletes without approval (deprecation doctrine); the
  hook only proposes. Discarded **hardcoding** `docs/` or the variant→canonical pairs outside config —
  `docsDir` is derivable and the pairs are those of 2b. Discarded `jq`/external parser (the docs example
  uses `jq`) — pure Python, no dependency. Discarded materialising **also** the "Plugin/marketplace
  rollout" in this round — one surgical evolution per round; stays as candidate. **Eval note:** this round
  did **not** alter a detection rule (2b is the auditor; the hook is the runtime application of the same
  criteria on the live event, outside the fixture harness), so the minimal harness does not apply — and
  **there is no Bash in this context** to run it (only Read/Edit/Write/Web/Grep/Glob), same situation as
  R18-R21; the logic is simple and read-only. (If any 2b grep needs to be refined to match the hook 1:1,
  that is work for `quenching-reviewer` — recorded in the review queue.)
- **Next candidate:** "Internal plugin/marketplace as a rollout vehicle for payloads" (package hooks/
  command/skills as a versioned plugin — `hooks/hooks.json` activates together with the plugin; the only
  **distribution** axis still without a payload, now that all Step 8 triggers — command + 3 lifecycle
  hooks + tool-event PostToolUse — are materialised) **or** "Deterministic generation/synchronisation of
  the normative layer index" (`INDEX.md` as a derivable artifact from files).

### Round 21 — 2026-06-29 · boundary: ConfigChange hook as installable PAYLOAD (audit-trail) — materialises the 3rd and last hook that R7 deferred

- **Change:** authored the **third and last** lifecycle hook of the package as a ready payload:
  **`assets/hooks/audit-config-change.py`** (portable ConfigChange hook, without paths from this repo).
  In the `ConfigChange` event (matcher of the 5 sources), builds **one JSONL line** with metadata —
  `ts` (UTC ISO), `event`, `source`, `file`, `session` — and **appends** it (append-only, with simple
  size-based rotation by `maxLogBytes`) to a **log derived from the target** (`auditLog`, default
  `.claude/config-audit.log` relative to `CLAUDE_PROJECT_DIR`/`cwd`). Filters by `sources`, has
  `deadlineMs`, **exit 0 always**, and **never records the content/diff** of the changed file (only
  metadata — config may contain secrets). Actionable error (dim 14) if it cannot write the log (says what
  and where to adjust). Wired in `settings.snippet.json` (ConfigChange block,
  `matcher: "user_settings|project_settings|local_settings|policy_settings|skills"`, `timeout: 5`,
  `$comment` explaining observes-not-blocks and stdout-to-file) and configured by the `auditConfigChange`
  block in `hooks-config.json`. Conceptual diff: the package, which **detected** the absence of
  ConfigChange (R7) and **anticipated** the audit trail (Step 8/R17), now **carries** it — completing
  the lifecycle hook trilogy (Stop/R19 + SessionStart/R20 + ConfigChange/R21).
- **Why:** it was the **1st candidate** in the advancement backlog and the **next candidate** pointed out
  by R20 — the step that **completes** the workflow+commands+hooks sequence: R17 made the doctrine
  (Step 8, three hook payloads); R18 the command; R19 the Stop (freshness, PROPOSES); R20 the SessionStart
  (compact-survival, RE-INJECTS); R21 the ConfigChange (audit-trail, OBSERVES/RECORDS). **Materialises
  what R7 deferred** explicitly (R7 wrote the doctrine/detection and left "actually installing the three
  hooks… as a future implementation item") — which is why it is a **new** boundary in the exclusion index,
  not a repetition of R7, R19, or R20: different event/moment/effect (ConfigChange × Stop × SessionStart;
  moment-of-change × end-of-turn × restart; observes × proposes × re-injects). The three key choices come
  directly from the docs and are what keep the payload **correct and portable**: (1) **exit 0** because an
  audit trail cannot veto a legitimate change (although ConfigChange *can* block); (2) **write to file,
  not stdout**, because in this event stdout goes to the debug log and **does not become context** (unlike
  SessionStart/R20 — this is what mechanically distinguishes the two); (3) **target-derived destination +
  only metadata**, to avoid coupling to the repo or leaking secrets.
- **Sources:** [Hooks reference — Claude Code Docs (ConfigChange)](https://code.claude.com/docs/en/hooks)
  (accessed 2026-06-29, ✅ verified by WebFetch) — **verbatim** the 5 matchers/sources
  (`user_settings` = `~/.claude/settings.json`; `project_settings` = `.claude/settings.json`;
  `local_settings` = `.claude/settings.local.json`; `policy_settings` = managed policy; `skills` = skill
  files), the *"Exit code 2 behavior per event"* table for ConfigChange — *"Can block? Yes… Blocks the
  configuration change from taking effect (except `policy_settings`)"* (justifies using **exit 0** for
  the audit trail), the stdout handling *"For ConfigChange, stdout is written to the debug log but not
  shown in the transcript (unlike UserPromptSubmit or SessionStart where stdout is added as context)"*
  (justifies writing to **file**, not stdout), and the common fields (`session_id`/`transcript_path`/`cwd`/
  `hook_event_name`) + the matcher field = "configuration source";
  [Automate actions with hooks — Claude Code Docs (guide, «Audit configuration changes» section)](https://code.claude.com/docs/en/hooks-guide)
  (accessed 2026-06-29, ✅ verified by WebFetch) — **verbatim** *"Track when settings or skills files
  change during a session. The `ConfigChange` event fires when an external process or editor modifies a
  configuration file, so you can log changes for compliance or block unauthorized modifications"*, the
  canonical example *"This example appends each change to an audit log"* reading `.source` and `.file_path`
  with `now | todate` and `>> ~/claude-config-audit.log` (direct model for the `source`/`file_path`
  fields, the timestamp, and append-to-log — we only **derive** the destination from the target instead
  of hardcoding, and write structured JSONL), and *"To block a change from taking effect, exit with code
  2 or return `{\"decision\": \"block\"}`"* (which we do **not** use — audit trail observes). Catalogue:
  `research/03-hooks.md` (ConfigChange gives an audit trail of unauthorised changes to the surface during
  the session; the three hooks form the continuous audit cycle: what was loaded, what survived compaction,
  what was modified; audit logs may contain secrets → retention policy; hook config is executable code).
- **Rejected/superseded:** discarded the ConfigChange that **blocks** (`exit 2`/`decision: block` to
  "bar an unauthorised change") — it is *enforcement*, not *audit-trail*; blocking a legitimate
  settings/skill edit mid-session is the opposite of auditing, and would go outside the "trail" scope
  (Simplicity First; stays as a possible distinct future payload). Discarded **printing the trail to
  stdout** (as R20/SessionStart does) — in this event stdout *does not become context* (goes to debug
  log), so the trail must go to a **file**. Discarded **hardcoding** the log path (the literal
  `~/claude-config-audit.log` from the docs example) — violates the portable invariant; derived from
  `auditLog`/`CLAUDE_PROJECT_DIR`. Discarded **recording the content/diff** of the changed file — the
  catalogue warns that config logs may contain secrets; the trail stays as **metadata**. Discarded
  `jq`/external parser (the docs example uses `jq`) — pure Python, no dependency, more portable.
  **Eval note:** this round did **not** alter a detection rule of dim 8 (8b in `detection-and-smells.md`
  is the auditor; building the log line is a **runtime trigger of the hook** on the live event, outside
  the fixture harness), so the minimal harness does not apply. I sketched a **read-only smoke test** for
  the payload (`scratchpad/smoke_test_configchange.py`: project_settings→1 line, filtered source→silence,
  enabled:false→silence, malformed stdin→exit 0, never touches the config file, log with only metadata)
  but **there is no Bash in this context** to run it (only Read/Edit/Write/Web/Grep/Glob) — same situation
  as R18/R19/R20; the logic is simple and the script only appends to a derived log.
- **Next candidate:** "PR hook / `docs/` coverage that reruns detection of the touched scope and PROPOSES"
  (trigger (1) of Step 8; crosses dim 2 × dim 8 — the only Step 8 trigger still without a payload, now
  that the lifecycle hook trilogy and the on-demand command are done) **or** "Internal plugin/marketplace
  as a rollout vehicle for payloads" (package hooks/command/skills as a versioned plugin — `hooks/hooks.json`
  activates together with the plugin).

### Round 20 — 2026-06-29 · boundary: SessionStart-compact hook as installable PAYLOAD (compact-survival) — materialises the 2nd hook that R7 deferred

- **Change:** authored the **second** lifecycle hook of the package as a ready payload:
  **`assets/hooks/reinject-conventions.py`** (portable, read-only SessionStart hook, without paths from
  this repo). In the `SessionStart` event with `source` in `compact`/`clear`/`resume` (early-exit on
  `startup` and unknown sources — on a new session the docs say to use the native CLAUDE.md), **re-injects**
  the stable layer that `/compact` would erase: resolves the **source derived from the target** in order —
  (1) `conventionsFile` (default `.claude/conventions.md`, relative to `CLAUDE_PROJECT_DIR`/`cwd`), (2) if
  absent, the **head** of the root `CLAUDE.md` — and prints to **stdout** (which in SessionStart **becomes
  context**; plain text, without building JSON, as the docs recommend for "a hook that only loads context").
  Embedded: `maxBytes`+`deadlineMs` (latency ceiling), silence on absent source/budget overflow/malformed
  stdin, **exit 0 always**. Wired in `settings.snippet.json` (SessionStart block,
  `matcher: "compact|clear|resume"`, `timeout: 5`, `$comment` explaining compact-survival and "reads from
  derived source, never a fixed list") and configured by the `reinjectConventions` block in
  `hooks-config.json`. Conceptual diff: the package, which **detected** the absence of the
  SessionStart-compact (R7) and **anticipated** compact-survival (Step 8/R17), now **carries** it —
  closing the gap "the method does not actually use hooks" on the SessionStart axis.
- **Why:** it was the **next candidate** pointed out by R19 (and the 1st in the advancement backlog) and
  the natural step in the workflow+commands+hooks sequence: R17 made the **doctrine** of the loop (Step 8)
  anticipating three hook payloads; R19 delivered the **Stop** (automatic freshness, end of turn, PROPOSES);
  this is the **SessionStart** (compact-survival, restart, RE-INJECTS). **Materialises what R7 deferred**
  explicitly ("Discarded **actually installing** the three lifecycle hooks… rich payload as a future
  implementation item") — R7 was the **doctrine/detection** (refined dim 8 + 8b), this round is the
  **installable artifact**; which is why it is a **new** boundary in the exclusion index, not a repetition
  of R7 or R19 (different event/moment/effect: SessionStart×Stop, restart×end, re-injects×proposes).
  Choosing to **derive the source from the target** (not embed conventions) is what keeps the payload
  portable — without it the hook would be coupled to this repo, violating the invariant.
- **Sources:** [Hooks reference — Claude Code Docs (SessionStart)](https://code.claude.com/docs/en/hooks)
  (accessed 2026-06-29, ✅ verified by WebFetch) — **verbatim** the SessionStart matchers (`startup`
  "New session", `resume`, `clear` "/clear", `compact` "Auto or manual compaction"), the input fields
  (`source` "How the session started: startup/resume/clear/compact", + common `session_id`/`transcript_path`/
  `cwd`/`hook_event_name`), the exit-0 output *"Any text your hook script prints to stdout is added as
  context for Claude"*, the portability note *"For static context that does not require a script, use
  CLAUDE.md instead"* and *"Since plain stdout already reaches Claude for this event, a hook that only
  loads context can print to stdout directly without building JSON"*, and the JSON field
  `hookSpecificOutput.additionalContext` (`hookEventName: "SessionStart"`);
  [Automate actions with hooks — Claude Code Docs (guide)](https://code.claude.com/docs/en/hooks-guide)
  (accessed 2026-06-29, ✅ verified by WebFetch) — **verbatim** the section *"Re-inject context after
  compaction… Use a `SessionStart` hook with a `compact` matcher to re-inject critical context after
  every compaction"*, *"Any text your command writes to stdout is added to Claude's context"*, the
  `matcher: "compact"` example, and — decisive for portability — *"You can replace the `echo` with any
  command that produces dynamic output, like `git log --oneline -5`… For injecting context on every
  session start, consider using CLAUDE.md instead"* (justifies deriving the source from the target and
  excluding `startup`). Catalogue: `research/03-hooks.md` (SessionStart matcher `compact` re-injects
  critical context after compaction; hook is executable code; <500 ms in the critical path).
- **Rejected/superseded:** discarded **hardcoding** a conventions list in the payload (the literal
  `echo` from the docs example) — violates the self-contained/portable invariant; the hook reads from a
  source derived from the target, and changes repo without editing the script. Discarded covering the
  **`startup`** matcher — the docs are explicit ("For injecting context on every session start, consider
  using CLAUDE.md instead"); on a new session the native CLAUDE.md already loads, re-injecting would be
  duplication; only the restarts that **lose** context (`compact`/`clear`/`resume`) need the hook.
  Discarded emitting via `additionalContext`+JSON — the docs say that for plain text direct stdout
  suffices ("without building JSON"); Simplicity First. Discarded materialising **also** the `ConfigChange`
  in this round — one surgical evolution per round; stays as candidate. Discarded a Markdown parser for
  the source (extract "only conventions") — the head in bytes suffices (stable layer = top of CLAUDE.md/
  conventions), latency ceiling; a parser would be cost at restart. **Eval note:** this round did **not**
  alter a detection rule of dim 8 (8b in `detection-and-smells.md` is the auditor; the `source` matching/
  source reading is a **runtime trigger of the hook** on the live event, outside the fixture harness), so
  the minimal fixture harness does not apply. I wrote a **read-only smoke test** for the payload
  (`scratchpad/smoke_test.py`: compact→CLAUDE.md, conventionsFile preferred, startup→silence,
  no-source→compact-default, absent-source→silence, malformed-stdin→exit 0) but **there is no Bash
  tool in this context** to execute it (only Read/Edit/Write/Web/Grep/Glob) — same situation as R18/R19;
  the logic is simple and the script is read-only.
- **Next candidate:** "`ConfigChange` as a payload in `assets/hooks/`" (the **third** and last lifecycle
  hook that R7 described and deferred — audit-trail of changes to the surface itself: matchers
  `user_settings`/`project_settings`/`local_settings`/`policy_settings`/`skills`) **or** "PR hook /
  `docs/` coverage that reruns detection of the touched scope and PROPOSES" (trigger (1) of Step 8;
  crosses dim 2 × dim 8).

### Round 19 — 2026-06-29 · boundary: Evolutionary Stop hook as installable PAYLOAD (automatic freshness) — materialises what R7 deferred

- **Change:** authored the first **lifecycle hook** of the package as a ready payload:
  **`assets/hooks/propose-knowledge-delta.py`** (portable Stop hook, read-only, without paths from this
  repo). At the end of the turn it reads only the **tail** of the transcript (`transcript_path`), matches
  cheap "fresh gap" signals by regex (corrected command · obsolete pattern/fossil · gotcha · env var) and,
  finding one, **PROPOSES** a CLAUDE.md/memory delta — with the **suggested home** per signal (CLAUDE.md =
  map+link × memory = agent-learning) — via `hookSpecificOutput.additionalContext`, **exit 0 always**.
  Embedded and documented in docstring/code: guard `stop_hook_active` (early-exit), `deadlineMs`+
  `maxTranscriptBytes` (latency ceiling), `hooks-config.json` (`enabled: false` → silence). Wired in
  `settings.snippet.json` (2nd hook in the `Stop` event, `timeout: 5`, `$comment` explaining
  propose≠block) and configured by the `proposeKnowledgeDelta` block in `hooks-config.json`. Conceptual
  diff: the package, which **detected** the absence of the evolutionary Stop (R7) and **anticipated**
  automatic freshness (Step 8/R17), now **carries** it — closing the gap "the method does not actually
  use hooks", on the Stop hook axis.
- **Why:** it was the **next candidate** pointed out by R18 (and from the advancement backlog) and the
  concrete gap in the round sequence (workflow+commands+hooks): R17 made the **doctrine** of the loop
  (Step 8) anticipating three payloads; R18 delivered the **command** (trigger 3); this is the **automatic
  freshness hook**. **Materialises what R7 deferred** explicitly ("Discarded **actually installing** the
  three lifecycle hooks… the rich payload stays as a future implementation item") — R7 was the
  **doctrine/detection** (refined dim 8 + 8b), this round is the **installable artifact**; which is why
  it is a new boundary in the exclusion index, not a repetition of R7. The form "propose via
  `additionalContext`, never block" is the only one consistent with the semantics: a Stop hook returning
  `decision: block`/`exit 2` *prevents the turn from ending* — the opposite of an optional suggestion.
- **Sources:** [Hooks reference — Claude Code Docs (Stop)](https://code.claude.com/docs/en/hooks)
  (accessed 2026-06-29, ✅ verified by WebFetch) — **verbatim** the Stop hook input fields
  (`transcript_path` "Path to conversation JSON", `stop_hook_active` "Boolean indicating if a Stop hook
  is currently blocking Claude from stopping"), the guard *"You should check the `stop_hook_active` field
  and exit early if true… This prevents redundant blocking"*, the cap *"If a Stop hook blocks 8 times in
  a row… Claude Code will force-stop the session anyway to prevent infinite loops"*, the exit semantics
  (*"Exit 0: …Claude Code parses stdout for JSON output fields"*; *"Exit 2: Blocking error… Stderr is
  fed back to Claude… prevents Claude from stopping"*) and, decisive for "propose without blocking", the
  output field **`additionalContext`** *"String added to Claude's context. Unlike blocking, this continues
  the conversation and Claude can act on the feedback"*; [Set up Claude Code in a monorepo or large
  codebase — Claude Code Docs](https://code.claude.com/docs/en/large-codebases) (accessed 2026-06-29,
  ✅ verified by WebFetch) — **verbatim** *"Add a Stop hook that proposes updates: a `Stop` hook receives
  the path to the session transcript when Claude finishes responding, so a script can review the session
  and propose CLAUDE.md updates while the gap it exposed is fresh"*. Catalogue: `research/03-hooks.md`
  (exit 1×2 semantics; hook is executable code) and `research/04-claude-md-memory.md` (Stop hook that
  proposes updates from the transcript).
- **Rejected/superseded:** discarded the Stop hook that **blocks** (`decision: block`/`exit 2` to "force"
  the recording) — contradicts its own purpose (proposing, not preventing the turn from ending) and would
  still trigger the cap of 8 blocks; the docs reserve `additionalContext` exactly for "continues the
  conversation". Discarded **writing** the delta directly to CLAUDE.md/memory — the method **never writes
  memory** and edits CLAUDE.md only with confirmation (Step 5); the hook is **read-only** and only
  suggests. Discarded a full `.jsonl` parser (line-by-line, by role/tool) — Simplicity First and latency
  ceiling: the **tail as text** + cheap regex is enough; a rich parser would be cost in the critical path
  of every turn. Discarded materialising **also** the `SessionStart compact` and the `ConfigChange` in
  this round — one surgical evolution per round; they stay as candidates (the PR hook and the other two
  lifecycle hooks). Discarded embedding paths/terms from this repo in the signals (portability) — the
  regexes are generic (EN+PT) and the paths derive from `CLAUDE_PROJECT_DIR`. **Eval note:** this round
  did **not** alter a detection rule of dim 8 (8b in `detection-and-smells.md` is the auditor; the new
  regexes are **a runtime trigger of the hook** on the live transcript, outside the fixture harness), so
  the minimal harness does not apply — and there is no Bash in this context to run it (same situation
  as R18).
- **Next candidate:** "`SessionStart compact` + `ConfigChange` as payloads in `assets/hooks/`" (the
  other two lifecycle hooks that R7 described and deferred — re-inject conventions after `/compact` +
  audit trail of the surface itself: matchers `user_settings`/`project_settings`/`local_settings`/
  `policy_settings`/`skills`) **or** "PR hook / `docs/` coverage that reruns detection of the touched
  scope and PROPOSES" (trigger (1) of Step 8; crosses dim 2 × dim 8).

### Round 7 — 2026-06-29 · boundary: Hooks — continuous audit surface + exit semantics

- **Change:** refined **dimension 8 (hooks)** in `dimensions-template.md` and added the
  cross-cutting item **8b** in `detection-and-smells.md`. The "What good looks like" stops
  being "the `command` exists + idempotent + timeout" and gains three new axes: (1) the
  **continuous knowledge audit surface** — the three lifecycle hooks that keep the base
  **alive**: **`SessionStart` matcher `compact`** re-injects conventions/FQNs/guardrails
  after `/compact` would erase them (hook stdout returns to context); **evolutionary Stop
  hook** receives the transcript path at the end of the turn and **proposes CLAUDE.md
  deltas** «while the exposed gap is fresh» (self-evolving surface, only proposes);
  **`ConfigChange`** gives an audit trail of changes to the surface itself during the
  session. (2) the correct **exit semantics** — `exit 2` blocks and sends `stderr` to the
  model, `exit 1` **only warns** (the dangerous action still executes — most common
  error), `exit 0` + JSON for rich decisions (exit 2 and JSON **do not** combine). (3)
  the **guard `stop_hook_active`** in Stop hooks (the harness cuts after 8 blocks —
  without the guard it is a loop), ~500 ms ceiling in the critical path, and the
  scope/trust facts: `settings.json` **loads only from the start directory** (does not
  inherit from parents) and hook config is **executable code** (do not run destructive in
  `SessionStart`). In `detection-and-smells.md`, the **8b** brings greps that **only list
  candidates** (presence of the 3 lifecycle hooks · Stop without `stop_hook_active` ·
  `exit 1` in a blocking hook) + the semantics and surface-absence as a read. Conceptual
  diff: dimension 8 stops being "does the `command` exist?" and gains a **live-surface
  posture** (compact-survival + self-evolution + audit-trail) and an **wrong-exit-code
  detector** — reinforcing the enforcement (hook, deterministic) × guidance (CLAUDE.md,
  probabilistic) boundary that dims 1/12 already cite. Stays at 15 dimensions.
- **Why:** dimension 8 was the **least operational** after those already refined — only
  checked `command`→script-exists and timeout, without the criterion for *which* hooks a
  Claude Code-ready repo needs or the exit semantics (the most documented production error
  is `exit 1` thinking it blocks). It was the **leading candidate** (pointed out as next in
  R5 and R6, "evolutionary Stop hook / continuous audit") and the most anchored in the
  catalogue (`03-hooks.md` with 9 verified sources + `04-claude-md-memory.md`). The repo
  **lives** by this: it already has a 150-line hook in CLAUDE.md (deterministic enforcement),
  but no `SessionStart compact` (loses conventions on `/compact`, critical in a repo in
  active long refactor) or evolutionary `Stop` — real gaps that the method now flags. The
  method itself benefits: the Stop hook is the *automated* version of what the
  `quenching-evolutionist` does by hand.
- **Sources:** [Set up Claude Code in a monorepo or large codebase — Claude Code Docs](https://code.claude.com/docs/en/large-codebases)
  (accessed 2026-06-29, ✅ verified by WebFetch) — states **verbatim** *"Add a Stop hook that
  proposes updates: a `Stop` hook receives the path to the session transcript when Claude
  finishes responding, so a script can review the session and propose CLAUDE.md updates while
  the gap it exposed is fresh"*, the scope rule *"Project settings in `.claude/settings.json`
  load only from your starting directory and are not inherited from parent directories"*, and
  the `SessionStart` hook that injects context into stdout before the first prompt; [Automate
  actions with hooks — Claude Code Docs](https://code.claude.com/docs/en/hooks-guide) (accessed
  2026-06-29, ✅ verified by WebFetch) — **verbatim** *"Use a `SessionStart` hook with a `compact`
  matcher to re-inject critical context after every compaction… Any text your command writes to
  stdout is added to Claude's context"*, the exit semantics (*"Exit 2: the action is blocked.
  Write a reason to stderr, and Claude receives it as feedback"*; *"Any other exit code: the
  action proceeds"*), the guard *"Claude Code overrides a Stop hook after it blocks 8 times in
  a row… Parse the `stop_hook_active` field… and exit early if it's `true`"*, and the matchers
  of `SessionStart` (startup/resume/clear/compact) and `ConfigChange`
  (user/project/local/policy_settings/skills). Catalogue: `research/03-hooks.md` (the 3
  continuous audit hooks: InstructionsLoaded + SessionStart compact + ConfigChange; `exit 1`
  vs `exit 2` as a common error; hook is executable code with shell privileges) and
  `research/04-claude-md-memory.md` (CLAUDE.md=guidance × hook=enforcement; Stop hook that
  proposes updates from the transcript).
- **Rejected/superseded:** discarded **creating a new dimension** "continuous audit / lifecycle"
  — it is a refinement of existing dimension 8; the cross-cutting axis enters as **8b** (like
  6b/7b/1b), keeping 15 dimensions (Simplicity First). Discarded **actually installing** the
  three lifecycle hooks in the target repo right now (writing ready `SessionStart compact`/
  evolutionary `Stop` in `assets/hooks/`) — it is *application* work (method Step 5, with
  confirmation) and payload authoring, not template evolution; the method now **detects the
  absence and proposes**, and the rich payload stays as a future implementation item, outside
  this single round. Discarded citing the phrase *"Skills: model judgment… Hooks: harness
  enforcement — behavior is certain"* as a literal from the official source — the catalogue
  verification note (R6) already recorded that this literal quote does not exist; the template
  uses only the language the docs actually publish and the functional distinction (guidance ×
  enforcement) that dims 1/12 already anchor. Discarded importing the **pre-trust security
  smell** with the attribution to `/security` — the catalogue marks that URL as `mischaracterised`
  (the HackerOne fix does not appear on the page); the template keeps only the generic, verifiable
  fact ("hook config is executable code; do not run destructive in SessionStart"), without citing
  the specific vulnerability.
- **Next candidate:** "Legacy command → skill" (dim 9 — catalogue `05-slash-commands.md`: migrate
  `.claude/commands/*.md` that mirror owner skills to description-based auto-triggering) or "Writing
  tools for agents / token-efficiency of the surface" (dim 6/11 — catalogue
  `08-writing-tools-for-agents.md`).
