<!-- quenching v<VERSION> · operator manual · generated payload.
     Refreshed by /skill:align (or /align). Edit the plugin asset, not this copy —
     a run with a newer plugin overwrites this file. Remove this banner to keep
     your own version: the align will then leave it alone and report it. -->

# Operating this repo's automation surface

`.claude/` is where **this repository's own** Claude Code automation lives — the commands it
wrote for itself, the commands that invoke them, the hooks that enforce its conventions. It is
kept on a single taxonomy by the
[`quenching`](https://github.com/eloysekonell/quenching) plugin, via the `/skill:*` commands —
`/skill:new`, `/skill:agent:new`, `/skill:hook:new`, `/skill:eval`, `/skill:retro`, and the
sweep `/skill:align`.

Its siblings: `../.docs/QUENCHING.md` (the knowledge bundle) and
`../.specs/QUENCHING.md` (the plan workspace).

---

## 1. What lives here

```
.claude/
  QUENCHING.md          # this manual (payload)
  settings.json         # hook wiring, permissions — commit it
  settings.local.json   # personal overrides — gitignore it
  commands/             # THE surface — one file per entry point; mirrors the repo's folders
    <folder>/<verb>.md  # frontmatter + workflow, in the one file
  agents/<name>.md      # subagent definitions — minted by /skill:agent:new
  references/<name>/    # shared procedure — outside commands/, cited by path
  evals/<path>/         # measured case sets — outside commands/ too
  hooks/
    okf-validate.py     # the OKF conformance checker (see ../.docs/QUENCHING.md §5)
    hooks-config.json   # its config — commit it
```

**What does *not* live here:** anything that comes from an installed plugin. `quenching`'s
own skills and its `/docs:*`, `/specs:*`, `/skill:*`, `/align` commands are provided by the
plugin — copying them into `.claude/` creates two registrations of the same triggers. The same
goes for the `openspec-*` skills and `opsx/` commands the OpenSpec CLI generates: `/specs:align`
removes them.

---

## 2. The single axis

Every skill in this repo is classified on **exactly one axis**, and everything else — its name,
whether it gets a command, where that command sits — follows from the answer.

**The test:** *name the one folder this skill acts on.*

| Answer | Class | Name pattern | Example |
| --- | --- | --- | --- |
| Exactly one folder | **domain-bound** | flattened folder path + verb | `pipelines/ingest/` + validate → `pipelines-ingest-validate` |
| "the repo" | **generic** | verb-object (no path prefix) | `release-notes`, `generate-changelog` |
| Several unrelated folders | **neither** | — | kept untouched and **reported as unroutable** |

A forced classification is worse than none. The name alone then tells you where a skill acts: a
reader scanning `commands/` reconstructs the repo map from the domain-bound paths, and anything
without a path prefix is repo-wide by declaration.

### Placement — the path IS the identity

**One file per entry point.** Claude Code merged custom commands into skills, so a command file
carries both the description that routes to it and the body that runs. There is no `SKILL.md`
half and no wrapper to keep in step: the path is the whole identity.

- **A domain-bound command lives at** `commands/<folder-path>/<verb>.md`, invocable as
  `/<folder>:<subfolder>:<verb>` — one `:` per path segment.
- **A generic command is a flat** `commands/<verb-object>.md`.
- `/` + tab then walks the command tree in folder order, so the automation surface is navigable
  the same way the repo is.

**`commands/` is the only tree Claude Code registers**, so nothing else may live in it. A
`references/` folder placed there would register every file in it as a phantom command like
`/docs:align:references:conformance` — which does not error, it just quietly appears in your `/`
menu and does nothing. Shared procedure, references and eval cases live beside `commands/`, not
inside it, and are cited by path.

**Accepted variation:** a directory-scoped surface at `<folder>/.claude/commands/` also binds a
command to a folder and is conformant. `/skill:align` classifies those in place; `/skill:new`
always writes into the repo-root `.claude/`, so the surface stays auditable in one place.

---

## 3. The commands

### `/skill:new` — mint or edit ONE command

Reads the taxonomy rule (offering to create it from the mold on first run), classifies on the
axis, derives the command path — which is the name — drafts the file under the writing doctrine,
and presents **ONE plan**: classification, path, files, and the OKF tail. On a single OK it
writes, then self-checks: the registry's generated zone matches `commands/` on disk and the
description fits the listing cap.

Without an OKF `/.docs/` bundle the mint still proceeds — the command file only — the OKF tail is
skipped, and `/docs:align` is suggested once.

### `/skill:align` — migrate the WHOLE surface, then audit every body

**Probe-first**: it opens with `skills.py doctor` + `lint`, so a conformant surface costs two
tool calls and stops there, saying so. Otherwise: a read-only inventory (path, classification,
and conformance gaps per item, including directory-scoped surfaces), then **one consolidated
plan**: renames to canonical paths, commands to create or rewrite, and the rule + registry
created from the molds when missing. Applied on a single OK — with a **code-coupled rename
confirmed on its own**. Then it verifies: zone regenerated, registry matches `commands/` exactly.

**If this repo still carries the old paired shape** — a `skills/<name>/SKILL.md` plus a thin
wrapper — the plan includes **collapsing each pair into one file**: the wrapper's `description`
and `argument-hint`, the skill's `allowed-tools` and `effort`, the skill's body moved verbatim
into the wrapper's path. Nothing you type today changes. Anything that sat beside the skill
(`references/`, `evals/`) is re-homed outside `commands/` first.

The migration's last stage is the one thing the sweep itself is **forbidden** to fix: a
**read-only audit of every command body** against the writing doctrine in §5. A violation is a
**finding, not a fix** — rewriting a body is *authoring*, and authoring needs the person whose
intent the command encodes — so the report names the file, the rule it breaks, the one-line
evidence, and the exact `/skill:new <name>` that opens the edit. Nothing is rewritten behind
your back.

**Bodies are preserved** (MERGE), an unclassifiable command is **kept and reported**, and nothing
is deleted unless you state it is obsolete.

### `/skill:agent:new` — mint or edit ONE subagent definition

The delegation counterpart of `/skill:new`, for `.claude/agents/`. Applies the delegation test
(does this work return a summary rather than a trail?), scopes the agent's tools to the
narrowest set that still does the job, prices the definition's always-on cost, and lands the OKF
tail on one OK. *Not for:* a command (`/skill:new`) or a hook (`/skill:hook:new`).

### `/skill:hook:new` — wire ONE scoped hook

Walks the scope ladder to the narrowest event + matcher and the cheapest handler that still
catch what it must, states the hook's cost claim, and applies on one OK — **warn by default;
block only on your word**. *Not for:* the OKF conformance hook — the plugin wires it automatically,
and `/docs:align` only offers to remove a legacy copy.

### `/skill:eval` — measure whether a command teaches anything

Runs one command's cases twice — with the command loaded and without — in isolated sub-agents,
grades every assertion against **quoted evidence**, and reports the delta over pass rate, tokens
and duration. A command whose delta is zero is reported as teaching nothing, never quietly
passed. Description tuning runs on measured should-trigger / should-not-trigger rates, never on
taste.

### `/skill:retro` — what one session proves about the command that drove it

Typed-only: a human names the session (or takes the current one) and, optionally, the command
in it to analyse. Reads the transcript through the bundled `session.py` — never by recalling the
run — and reports counted findings in four classes: performance, redundancy, bugs, and
unresolved problems the human had to fix by hand, each carrying its count and the quoted turn
behind it. A command reached as a conducted stage whose conductor never regained attribution is
spoken as an upper bound, never as an exact count. Reports only; nothing is applied — each
finding ends with the `/skill:new` invocation that would close it.

---

## 4. The OKF artifacts

The commands maintain these documents inside the `/.docs/` bundle — the automation surface is
knowledge about this repo, so it is recorded where knowledge lives. Each standard is born
`authority: background` and becomes `current` once the surface actually follows it:

| Artifact | Path | Role |
| --- | --- | --- |
| **The rule** | `/.docs/standards/automation/skills.md` | `type: standard`. The taxonomy this repo binds itself to. |
| **The agent rule** | `/.docs/standards/automation/agents.md` | `type: standard`. Installed by `/skill:agent:new`: when work becomes a subagent, the definition contract, the verifier shape. |
| **The hook rule** | `/.docs/standards/automation/hooks.md` | `type: standard`. Installed by `/skill:hook:new`: the scope ladder, the handler ladder, the policy defaults. |
| **The registry** | `/.docs/documentation/reference/automation.md` | `type: documentation`. The authoritative listing of the local surface. |

The registry's `<!-- GENERATED:BEGIN -->` … `<!-- GENERATED:END -->` zone holds one table —
`Command | Serves | Typical trigger` — derived **exclusively** from the local
`commands/**/*.md` frontmatter, ordered by the Command column. It lists **this repo's own**
surface, never a plugin's.

**Never hand-edit inside those markers.** Curated prose lives outside them and is never touched
by regeneration. Only `/skill:new` and `/skill:align` write the zone. This zone earns its keep
because nothing else derives the registry; `/.specs/plans/` went the other way — its listing
duplicated what `specs.py list` already read from disk, so the artifact was retired rather than
guarded.

---

## 5. Writing a skill that behaves

The full doctrine lives in the plugin; these are the parts you feel every day.

- **Predictability is the root virtue.** The same request should produce the same run. Prefer a
  named step with a checkable completion criterion over a paragraph of intent.
- **Trigger phrases go in the description's second sentence.** The listing is truncated at a
  fixed length shared with every other installed plugin — anything past it is invisible to
  routing.
- **Load lazily.** Frontmatter is always in context; the body loads on invocation; `references/`
  load only when a step reaches for them. Keep bodies short and push shared procedure into a
  reference file that other skills **cite** rather than restate.
- **Say what to do, not what to avoid.** A positive prescription is executable; a prohibition
  leaves the next step undefined.
- **Apply the no-op test.** If a step could be skipped without changing the outcome, delete it.
- **State each boundary explicitly** — "not for X → other-skill" — so routing lands on the right
  one instead of the first plausible match.
- **Every capability is bought, never collected.** A new command starts with **all levers off**:
  no `context: fork`, no `model`/`effort` pin, no `hooks`, `allowed-tools` scoped to what its
  steps run, and default invocation. Each departure enters the mint's plan with what it buys,
  because each has a standing cost — an inline `model`/`effort` pin is part of the session's
  prompt-cache key and makes the next request recompute every input token, and `context: fork`
  cannot present a plan or ask a question, so a fork beside an `AskUserQuestion` grant is an
  error (`sk-fork-gate`). A lever whose buy nobody can state is bloat wearing a feature's name.

---

## 6. Hooks and settings

A hook charges **other people's operations** — it fires on events the command that installed it
does not own — so `/skill:hook:new` installs every hook at the **narrowest scope that still
catches what it exists to catch**, and climbs only with evidence:

1. **A command's own frontmatter `hooks:` block** — fires only while that command runs, and costs
   nothing to any other operation. The default home for a check tied to one workflow.
2. **A `settings.json` hook with an event + `matcher`** — fires only on the matched tool calls.
3. **A gated wide event** — a `Stop`/`UserPromptSubmit` hook made cheap by construction, like
   `okf-validate.py`'s dirty gate below.
4. **An unmatched session-wide hook** — the top of the ladder, and a finding
   (`sk-hook-unmatched`) unless the reason nothing narrower suffices is stated where it is wired.

Handlers ladder the same way — a deterministic `command` script costs zero tokens on no-match, a
`prompt` handler costs one cheap judgment per firing, and an `agent` handler on a per-tool-call
event is an LLM toll booth on every operation (`sk-hook-llm-frequent`). Warn by default; block
only on your word.

The plugin's own `okf-validate.py` keeps `/.docs/` conformant after every edit — wired automatically
via the plugin's `hooks/hooks.json`, never installed into this repo. Full behavior, every config
knob, and the finding codes are in `../.docs/QUENCHING.md` §5 and §7.

- `settings.json` — this repo's own hook wiring and permissions, if any. **Commit it**; it is
  shared configuration.
- `settings.local.json` — personal overrides. **Gitignore it.**
- `hooks/hooks-config.json` — optional, hand-maintained checker config (nothing installs one).
  **Commit it** if you keep one; per-developer overrides go in `hooks-config.local.json`
  (gitignored). The bundle root is the fixed `/.docs/` convention — nothing in config names it.

Hook config is executable configuration with shell privileges. Review it like infrastructure.

Run `/docs:status` any time to check the checker's own version against the plugin's. A legacy
`.claude/hooks/okf-validate.py` copy is never executed — resolution is plugin-first with no
fallback — so `/docs:align` offers to remove one rather than upgrade it.

---

## 7. Troubleshooting

| Symptom | What is going on |
| --- | --- |
| Two skills answer the same request | A local copy shadows a plugin skill. Remove the local one — `/specs:align` clears CLI-generated `openspec-*` duplicates; `/skill:align` reports the rest. |
| A skill never triggers | Its trigger phrases fell past the description cap, or another skill's description claims the same ground. `/skill:new` on that skill rewrites the description under the doctrine. |
| A command path does not resolve | The file is missing or was renamed. `/skill:align` reconciles the tree and verifies every path. |
| A `/` entry does nothing when invoked | Something that is not an entry point is sitting under `commands/` — a reference or a fixture. Move it out; `skills.py doctor` reports it as `sk-no-description`. |
| The registry disagrees with `commands/` | Its generated zone is stale — `/skill:new` and `/skill:align` both rebuild it from disk. |
| A command fits no folder | That is a valid outcome. It is kept and reported as unroutable — do not force a path onto it. |

---

## 8. The other fronts

| Front | Manual | Status (read-only) | Align |
| --- | --- | --- | --- |
| `/.docs/` — the OKF knowledge bundle | `../.docs/QUENCHING.md` | `/docs:status` | `/docs:align` |
| `/.specs/` — the spec-driven plan workspace | `../.specs/QUENCHING.md` | `/specs:status` | `/specs:align` |
| `.claude/` — this surface | this file | — | `/skill:align` |

**One align per front**, each probe-first, each carrying its front's content stages when the
probe finds work. `/align` conducts the three in dependency order on one confirmation: `/.docs/`
first (the other two write artifacts into it), then `/.specs/` (it clears the shadow copies the
skill sweep would otherwise inventory), then `.claude/`. A front this repo does not use simply
has no manual — the paths above are references, not promises.

The normative taxonomy and the full command-writing doctrine live in the plugin's
`assets/references/skill-new/`. This file is the operator's view; those are the specification.
