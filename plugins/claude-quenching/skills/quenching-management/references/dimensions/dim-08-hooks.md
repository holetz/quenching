# 8. Hooks — .claude/settings.json + .claude/hooks/

> **Back path:** [../dimensions-template.md](../dimensions-template.md) (dimensions index +
> transversal doctrine) · [../../SKILL.md](../../SKILL.md) (agent roadmap).

- **Purpose:** **deterministic** automation (validate/audit) in the session lifecycle. Home of what **needs** to happen (enforcement), contrasted with CLAUDE.md (probabilistic guidance the model can ignore) — `«deterministic limits are more reliable than probabilistic guardrails»`.

- **How "good" looks:**

  **Basic hygiene:** declared in `settings.json`; scripts in `.claude/hooks/`; idempotent; sensible `timeout` (below ~500 ms on the critical path); explicit criterion/ceiling; shared committed config, per-dev override in `*.local.json`.

  **Output semantics (most common error):**

  | Output | Effect |
  | --- | --- |
  | **exit 2** | **blocks**; the message in `stderr` is returned to the model as feedback |
  | **exit 1** | **only warns, does NOT block** (the dangerous action still executes) |
  | **exit 0 + JSON** in stdout | rich decisions |
  | exit 2 **+** JSON | **do not combine** — the harness ignores stdout when exit is 2 |

  - **Stop hook:** check the `stop_hook_active` field in the input JSON and exit early if `true` (the harness cuts after **8** consecutive blocks — without this, a loop).

  **Three lifecycle hooks (keep the knowledge surface alive):**

  | Hook | Event/matcher | Does | Output |
  | --- | --- | --- | --- |
  | **compact-survival** | `SessionStart` matcher `compact` (and ideally `clear`/`resume`; **not** `startup` — there the doc says to use native CLAUDE.md) | re-injects conventions/FQNs/guardrails after compaction (stdout becomes context; otherwise `/compact` loses them). **Good = reads from a derived source of the target** (conventions file or head of root CLAUDE.md), **never** a hardcoded list | exit 0 |
  | **evolutionary** | `Stop` (receives `transcript_path` at end of turn) | **proposes deltas** to CLAUDE.md/memory «while the exposed gap is still fresh» (auto-evolution, without force-editing). **Propose ≠ block:** returns via `hookSpecificOutput.additionalContext` (continues the conversation for Claude to report/act), **never** `decision: block` nor `exit 2` (those would force the turn not to finish) | exit 0 |
  | **audit-trail** | `ConfigChange` (matchers `user_settings`/`project_settings`/`local_settings`/`policy_settings`/`skills`) | change trail on the surface itself (new skill / `settings.json` modified doesn't go unnoticed). **OBSERVES, does not block** (though `ConfigChange` *can* block via `exit 2`/`decision: block`, except `policy_settings`). Stdout **does not** become context (goes to debug log) → writes to a **log file derived from the target**, **append-only and metadata-only** (timestamp/source/file/session — **never the content**, which may contain secrets) | exit 0 always |

  **Audit by TOOL EVENT (distinct from the 3 lifecycle ones, which trigger by *moment*):**

  | Hook | Matcher | Does | Can block? | Output |
  | --- | --- | --- | --- | --- |
  | **PostToolUse** | `Write\|Edit` | looks at the **touched file** (`tool_input.file_path`); when it falls under `docs/`, **PROPOSES** the taxonomy fix (dim 2) reusing **the same criteria from block 2b** — VARIANT/TWO-HOMES/NO-HOME/NO-SIDECAR/NO-LABEL (invents no new smell) | **No** — *«PostToolUse hooks cannot undo actions since the tool has already executed»*; «Can block? No» | exit 0; proposal via **JSON `additionalContext`** (stdout does not become context), never `decision: block` (only *ends the turn*, without undoing) |
  | **PreToolUse** | `Write\|Edit` | runs **before** the tool; when the destination matches a GENERATED artifact of the target (`protectedGlobs`, derived from target, never hardcoded paths — empty list ⇒ inert), **BLOCKS** — protect GENERATED YAML/manifests, AUTO-GENERATED catalog, lockfiles (rule «X defines Y» enforced by code). Crosses dim 14 | **Yes** — «Can block? Yes» / *«Blocks the tool call»* | modern form `hookSpecificOutput.permissionDecision: "deny"` + `permissionDecisionReason` with **exit 0** (wins **even** in `bypassPermissions`/`--dangerously-skip-permissions` — *«PreToolUse hooks fire before any permission-mode check»*); legacy `exit 2` + reason in `stderr`. **Do not mix** — *«Claude Code ignores JSON when you exit 2»* |

  - **The PreToolUse reason is ACTIONABLE (dim 14):** it says **WHICH** source-of-truth generates the artifact and tells you to edit the source (*«Claude receives it as feedback so it can adjust»*) — without this the agent blindly retries editing the generated artifact (loop). Latency ceiling: only matches the path string (`fnmatch`), no I/O.

  **Wiring — a hook only RUNS if it's wired:** copying the script to `.claude/hooks/` **is not enough** — *«a script file alone does nothing»*. Only triggers with the **corresponding entry** in `settings.json`, canonical structure `Event → matcher-group (`matcher`) → `hooks`:[ {`type`:`command`,`command`,`timeout`} ]`.
  - Installing the fragment ([../../assets/hooks/settings.snippet.json](../../assets/hooks/settings.snippet.json)) is **MERGING, never overwriting**: arrays per **event/matcher concatenate** (adds the package's group; same matcher ⇒ appends to `hooks[]`), preserving what the target already wired.
  - `command` uses the placeholder **`${CLAUDE_PROJECT_DIR}`** (never the machine's absolute path) and the script is **executable** (`chmod +x`).

  **Scope, precedence & trust:**
  - **Managed > CLI > Local > Project > User**.
  - home of hooks the **team** should have = `.claude/settings.json` (**checked-in**); per-machine override = `.claude/settings.local.json` (**gitignored**).
  - `.claude/settings.json` loads **only from the start directory** (does not inherit from parents — in a monorepo, each start-subfolder needs its own).
  - hook config **is executable code** with shell privileges — version and review as infra, never run destructive logic in `SessionStart`.

  **Canonical home for executable logic — `scripts/` (the hook is THIN and CALLS the script):**
  the reusable deterministic logic the surface invokes does not live **inline** in the
  hook's `command` nor scattered loose — it lives in **`scripts/`**, organized **by
  PURPOSE** (`ci/`/`<gen>`/`checks/`/`maintenance/`/`dev/`), with a README-map and a
  single execution convention. The official doc fixes the form: *«This example uses a
  separate script file that the hook calls»* + *«use… `${CLAUDE_PROJECT_DIR}` to
  reference scripts»*. The **hook is the thin trigger** (stdin-JSON→exit-code adapter);
  the **business rule** (validate/generate/check) is a **called `scripts/…`** — the
  payload [run-validation.py](../../assets/hooks/run-validation.py) (Stop) **is** that
  thin trigger: it invokes the target's `validateScript` (home `scripts/checks`/`ci`) on
  the changed files, without reimplementing the validation. This is
  the same home that (a) the **"common commands" of CLAUDE.md** (dim 1) invoke, (b)
  commands/skills (dim 9) load, (c) CI runs. The complete tree, the boundaries
  (`scripts/` of repo × `.claude/hooks/*` × `scripts/` internal to skill × `src/`), the
  CI scope of each purpose, and the organization doctrine are the **prescriptive canonical
  taxonomy** — single source in [../scripts-taxonomy.md](../scripts-taxonomy.md);
  **do not copy the tree** (Simplicity First) — link.

- **Detection:** read `.claude/settings.json`; `ls .claude/hooks/`; verify the **1:1 wiring** (every script has an entry / every entry points to an existing script, in the right event/matcher — orphan × dangling); check the **presence** of the three lifecycle hooks and the **output semantics** of blocking ones; locate the repo-level `scripts/`, verify **organization by purpose** (subfolders `ci`/`checks`/`maintenance`/`dev`), the **README-map vs. disk**, and that each `command`/command/CI invoking `scripts/<…>` points to an **existing** module (item **8b** in [../detection-and-smells.md](../detection-and-smells.md)).

- **Smells:**
  - hook referencing absent script; validation without ceiling/criterion; hook that edits a generated artifact (violates the «X defines Y» rule); missing timeout.
  - **orphan hook** — script present in `.claude/hooks/` **without** an entry in `settings.json` (inert: never triggers — e.g.: `protect-generated.py` copied but not wired, and the generated artifact remains editable).
  - **dangling hook** — entry in `settings.json` pointing to a **nonexistent** script (the `command` lies, fails on every trigger).
  - **wrong event/matcher** — right script in the wrong event (blocking placed in `PostToolUse`, which doesn't block; `compact`-survival wired to `startup` instead of `compact`).
  - **snippet overwriting instead of merging** — clobbers the array of an event the target already had (loses the pre-existing hook, instead of **concatenating**).
  - **`exit 1` in a blocking hook** (thinks it warns but the dangerous command still executes — should be `exit 2`).
  - **Stop hook without `stop_hook_active`** (loop until the 8-block cap); slow hook on the critical path (>500 ms).
  - **absence of lifecycle hooks** — without `SessionStart compact` the `/compact` deletes conventions/guardrails; without evolutionary `Stop` the surface doesn't self-correct; without `ConfigChange` there is no audit-trail.
  - **editable generated artifact without deterministic guard** — the repo has an artifact "generated by CI, never hand-edited" (`*.job.yml`/manifests/AUTO-GENERATED catalog/lockfile) but **nothing protects it by code** (only the CLAUDE.md guidance, which the model can ignore): missing the **PreToolUse** that BLOCKS Write/Edit on the generated artifact — deterministic enforcement × probabilistic guardrail (crosses dim 14).
  - sensitive/destructive logic in `SessionStart` (pre-trust vector).

  **Smells of the `scripts/` home (the executable logic invoked by the surface — crosses dim 1/9; doctrine in [../scripts-taxonomy.md](../scripts-taxonomy.md)):**
  - **deterministic logic embedded in the hook that should be a script** — the hook's `command` carries the **business rule** inline (multi-line validation/build), or a `.claude/hooks/<x>.py` **reimplements** what a `scripts/checks|ci/<x>` already does, instead of the hook **calling** the script (*«a separate script file that the hook calls»*). The rule should live in `scripts/`; the hook is the thin trigger.
  - **script referenced by hook/command/CI that doesn't exist** — the `command` of a hook (or a command/skill, or CI) invokes `scripts/<…>` that **doesn't exist** (mirrors the HOOK-DANGLING, now on the script target side).
  - **scripts loose at the root / single bag without purpose** — executables at the repo root or all in a flat `scripts/` without a purpose subfolder (`ci`/`checks`/`maintenance`/`dev`) — invisible to audit, no CI-scope boundary (uninsolated `dev/` enters product lint; destructive operational isn't flags-off).
  - **`scripts/README.md` that lies vs. disk** — the map (module → what-it-does → input) cites nonexistent module or omits new module (should be derivable from disk, like `standards/` `INDEX.md`); or **divergent execution convention** (CLAUDE.md says `python -m scripts.X`, README says another form).
  - **repo executable in the wrong home** — repo utility buried in the **internal `scripts/`** of a skill and re-called from outside it (should be promoted to repo-level `scripts/`); or product script dropped in `dev/` (escapes lint).

- **Remediation:** fix path; provide criterion; **wire the orphan hook** (merge the `settings.snippet.json` entry at the right event/matcher, without clobber) or **remove the dangling entry**; swap `exit 1`→`exit 2` in the blocking hook; add the `stop_hook_active` guard; **install** the lifecycle hooks (copy the script **AND** merge the wiring in `settings.json` for the right scope); remove broken hook. The evolutionary Stop hook **proposes**, does not impose. For `scripts/`: **extract** the inline business rule from the hook to a called `scripts/…`; **organize** the loose-at-root/single-bag into purpose subfolders (propose the move, with OK — install the scaffold from [../../assets/scripts/](../../assets/scripts/) where the home is missing); **sync** the README-map with disk; create the module a hook/command/CI invokes but doesn't exist (or fix the invocation).

- **Payload:** skill-template [../../assets/skills/quenching-config/](../../assets/skills/quenching-config/) (settings.json/hooks/permissions/env/MCP) + ready hooks [../../assets/hooks/](../../assets/hooks/) with their `hooks-config.json`. The package **carries** (not just detects absence):

  | Hook payload | Step 8 | What it does (summary) |
  | --- | --- | --- |
  | [validate-claude-md.py](../../assets/hooks/validate-claude-md.py) | — | CLAUDE.md line ceiling |
  | [propose-knowledge-delta.py](../../assets/hooks/propose-knowledge-delta.py) (Stop) | **automatic freshness** | reads the transcript at **end** of turn, **PROPOSES** deltas via `additionalContext`, **exit 0 always**, `stop_hook_active` guard, latency ceiling |
  | [reinject-conventions.py](../../assets/hooks/reinject-conventions.py) (SessionStart) | **compact-survival** | on restart (matcher `compact`/`clear`/`resume`) **re-injects** the stable layer that `/compact` would erase, reading from a **source derived from the target** (`conventionsFile` or head of root CLAUDE.md, **never** a fixed list from the package), stdout-becomes-context, exit 0, latency ceiling; does not cover `startup` (there the doc recommends native CLAUDE.md) |
  | [audit-config-change.py](../../assets/hooks/audit-config-change.py) (ConfigChange) | **audit-trail** | records in a **log derived from the target** (append-only, metadata-only — timestamp/source/file/session, **never the content** which may contain secrets) who/when/what changed (settings/skills), covering the 5 sources (`user_settings`/`project_settings`/`local_settings`/`policy_settings`/`skills`), **exit 0 always** (OBSERVES, never blocks), stdout-does-not-become-context |
  | [propose-docs-home.py](../../assets/hooks/propose-docs-home.py) (PostToolUse) | **`docs/` coverage** | triggered by **tool event**: on `Write`/`Edit` under `docs/`, checks the **touched file** (`tool_input.file_path`) against the taxonomy (dim 2) reusing **the criteria from block 2b** (VARIANT/TWO-HOMES/NO-HOME/NO-SIDECAR/NO-LABEL) and **PROPOSES** the home/slot via `additionalContext`, **exit 0 always** («Can block? No»), actionable error (says WHICH home/slot is missing + exact canonical name), latency ceiling |
  | [protect-generated.py](../../assets/hooks/protect-generated.py) (PreToolUse) | **generated artifact protection** | the only **enforcement** payload (crosses dim 14): runs **before** `Write`/`Edit` and, when the destination matches `protectedGlobs` (**derived from target**, never paths from this repo — empty list ⇒ inert), **BLOCKS** via `permissionDecision: "deny"` + `permissionDecisionReason` (exit 0; legacy `exit 2`+stderr via `denyMode`), **actionable** reason naming the source-of-truth (rule «X defines Y») |
  | [run-validation.py](../../assets/hooks/run-validation.py) (Stop) | **validation before finishing** (THIN hook that CALLS the script — crosses `scripts/`) | at **end of turn**, invokes the **validator derived from the target** (`validateScript`/`validateCmd`, in home `scripts/checks`/`ci` — **empty ⇒ inert**, never a hardcoded trio) on the **changed files** (`git status --porcelain`, filtered by `includeGlobs`). The **rule lives in `scripts/`**, the hook is the thin trigger. Default **PROPOSES** the result via `additionalContext` (**exit 0** — `ruff --fix`/`format` mutate **code**, not the knowledge base ⇒ informs, does not block); `blockOnFail` mode (OFF by default) uses `decision: block`/`reason` for «mandatory/never skip» (*«the `reason` is fed back to Claude so it keeps working»*). `stop_hook_active` guard, latency ceiling. **Documented example for Python repo:** the script runs `ruff check --fix` + `ruff format` + `pyright` (a Go repo would wire `go vet`/`gofmt`) |

  The **three** lifecycle ones are complementary (one **proposes** new delta at end of turn, another **re-injects** what exists on restart, the third **records** the change). PostToolUse and PreToolUse are also complementary: **PostToolUse PROPOSES *after***, **PreToolUse BLOCKS *before***. Wire via [../../assets/hooks/settings.snippet.json](../../assets/hooks/settings.snippet.json).

  For the **`scripts/` home** (the executable logic that hooks call): **organization scaffold** [../../assets/scripts/](../../assets/scripts/) — README-map template + skeleton of purpose subfolders (`ci`/`checks`/`maintenance`/`dev`) with `<...>` placeholders, **no concrete scripts** (the package carries the STRUCTURE, not the executables — those would be coupled to a repo). Canonical spec: [../scripts-taxonomy.md](../scripts-taxonomy.md).
