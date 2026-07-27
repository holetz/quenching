<!-- quenching v<VERSION> · operator manual · generated payload.
     Refreshed by /skill:align (or /align). Edit the plugin asset, not this copy —
     a run with a newer plugin overwrites this file. Remove this banner to keep
     your own version: the align will then leave it alone and report it. -->

# Operating this repo's automation surface

`.claude/` is where **this repository's own** Claude Code automation lives — the commands it
wrote for itself, the commands that invoke them, the hooks that enforce its conventions. It is
kept on a single taxonomy by the
[`quenching`](https://github.com/eloysekonell/quenching) plugin, via
`/skill:new` and `/skill:align`.

Its siblings: `../docs/QUENCHING.md` (the knowledge bundle) and
`../specs/QUENCHING.md` (the plan workspace).

---

## 1. What lives here

```
.claude/
  QUENCHING.md          # this manual (payload)
  settings.json         # hook wiring, permissions — commit it
  settings.local.json   # personal overrides — gitignore it
  commands/             # THE surface — one file per entry point; mirrors the repo's folders
    <folder>/<verb>.md  # frontmatter + workflow, in the one file
  references/<name>/    # shared procedure — outside commands/, cited by path
  evals/<path>/         # measured case sets — outside commands/ too
  hooks/
    okf-validate.py     # the OKF conformance checker (see ../docs/QUENCHING.md §5)
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

Without an OKF `docs/` bundle the mint still proceeds — the command file only — the OKF tail is
skipped, and `/docs:align` is suggested once.

### `/skill:align` — migrate the WHOLE surface

Read-only inventory first (path, classification, and conformance gaps per item, including
directory-scoped surfaces), then **one consolidated plan**: renames to canonical paths, commands
to create or rewrite, and the rule + registry created from the molds when missing. Applied on a
single OK — with a **code-coupled rename confirmed on its own**. Then it verifies: zone
regenerated, registry matches `commands/` exactly.

**If this repo still carries the old paired shape** — a `skills/<name>/SKILL.md` plus a thin
wrapper — the plan includes **collapsing each pair into one file**: the wrapper's `description`
and `argument-hint`, the skill's `allowed-tools` and `effort`, the skill's body moved verbatim
into the wrapper's path. Nothing you type today changes. Anything that sat beside the skill
(`references/`, `evals/`) is re-homed outside `commands/` first.

**Bodies are preserved** (MERGE), an unclassifiable command is **kept and reported**, and nothing
is deleted unless you state it is obsolete.

### `/skill:align-and-update` — migrate, then audit every body

This front's conductor, and the exact complement of the align above. Stage 1 is `/skill:align`.
Stage 2 is the one thing that align is **forbidden** to do: a **read-only audit of every skill
body** against the writing doctrine in §5.

A violation is a **finding, not a fix**. Rewriting a body is *authoring*, and authoring needs the
person whose intent the skill encodes — so the report names the file, the rule it breaks, the
one-line evidence, and the exact `/skill:new <name>` that opens the edit. Nothing is rewritten
behind your back.

This front is the plugin's shortest, and the command says so: unlike `docs/` (agent memory,
harness files) and `specs/` (finished plans), it has **no out-of-band store to drain**, so
it converges in **one or two passes**, essentially always. The loop still earns its keep — a
Stage 1 rename shifts the registry and can strand a citation, and re-assessing catches that in
the same run — but the report will tell you plainly when there was nothing left to do rather
than dressing it up.

Every front has this same pair (`/docs:align-and-update`, `/specs:align-and-update`);
`/align-and-update` runs all three.

---

## 4. The two OKF artifacts

The pair maintains two documents inside the `docs/` bundle — the automation surface is knowledge
about this repo, so it is recorded where knowledge lives:

| Artifact | Path | Role |
| --- | --- | --- |
| **The rule** | `docs/standards/automation/skills.md` | `type: standard`. The taxonomy this repo binds itself to. Born `authority: background`; it becomes `current` once the surface actually follows it. |
| **The registry** | `docs/documentation/reference/automation.md` | `type: documentation`. The authoritative listing of the local surface. |

The registry's `<!-- GENERATED:BEGIN -->` … `<!-- GENERATED:END -->` zone holds one table —
`Command | Serves | Typical trigger` — derived **exclusively** from the local
`commands/**/*.md` frontmatter, ordered by the Command column. It lists **this repo's own**
surface, never a plugin's.

**Never hand-edit inside those markers.** Curated prose lives outside them and is never touched
by regeneration. Only `/skill:new` and `/skill:align` write the zone — the same anti-drift rule
that governs `specs/backlog/index.md`.

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

---

## 6. Hooks and settings

`hooks/okf-validate.py` keeps `docs/` conformant after every edit. Full behavior, every config
knob, and the finding codes are in `../docs/QUENCHING.md` §5 and §7.

- `settings.json` — hook wiring and permissions. **Commit it**; it is shared configuration.
- `settings.local.json` — personal overrides. **Gitignore it.**
- `hooks/hooks-config.json` — checker config. **Commit it**; per-developer overrides go in
  `hooks-config.local.json` (gitignored).

Hook config is executable configuration with shell privileges. Review it like infrastructure.

```bash
python3 .claude/hooks/okf-validate.py --version   # must match the plugin's version
```

If it does not match, `/docs:align` offers the upgrade — overwriting only the script and
preserving your `hooks-config.json`.

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

| Front | Manual | Status (read-only) | Align (structure, one pass) | Align-and-update (+ content, looped) |
| --- | --- | --- | --- | --- |
| `docs/` — the OKF knowledge bundle | `../docs/QUENCHING.md` | `/docs:status` | `/docs:align` | `/docs:align-and-update` |
| `specs/` — the spec-driven plan workspace | `../specs/QUENCHING.md` | `/specs:status` | `/specs:align` | `/specs:align-and-update` |
| `.claude/` — this surface | this file | — | `/skill:align` | `/skill:align-and-update` |

`/align` runs the three aligns in dependency order on one confirmation, and `/align-and-update`
runs the three conductors the same way, looped: `docs/` first (the other two
write artifacts into it), then `specs/` (it clears the shadow copies the skill sweep would
otherwise inventory), then `.claude/`. A front this repo does not use simply has no manual — the
paths above are references, not promises.

The normative taxonomy and the full command-writing doctrine live in the plugin's
`assets/references/skill-new/`. This file is the operator's view; those are the specification.
