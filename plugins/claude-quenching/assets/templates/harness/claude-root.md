# CLAUDE.md — <repo-name>

<one line: what this repo is. The harness auto-loads this file on EVERY turn — it earns each line.>

## Operating this repo

Commands, env vars, ports, and etiquette the agent needs on **every** task — keep them verbatim.

```bash
<build / run / test / lint — the fenced, copy-pasteable commands>
```

- <env var / port / local quirk needed every turn>
- <agent etiquette: a permission, a tool rule, a "never do X" — harness-operational only>

## Where knowledge lives

Knowledge is **NOT** in this file — it lives in the OKF bundle at [docs/](docs/index.md).
Point, never paraphrase; each bullet lists a home THAT EXISTS with its boundary one-liner.

**Resolving a term.** Hit an unfamiliar repo word, acronym, or codename? Look it up in the
**glossary first** → [docs/knowledge/glossary.md](docs/knowledge/glossary.md): the A–Z lookup,
one entry per term with a link to its full doc when one exists. `grep -i '<term>' docs/knowledge/glossary.md`.

- [docs/standards/](docs/standards/index.md) — how WE build (current, proven contracts).
- [docs/knowledge/](docs/knowledge/index.md) — generic understanding we hold (concepts, learnings);
  its [glossary.md](docs/knowledge/glossary.md) is the term lookup.
- [docs/reference/](docs/reference/index.md) — facts about what we consume (tools, libs, regulations).
- [docs/<other-home>/](docs/<other-home>/index.md) — <boundary one-liner>.
- [openspec/backlog/](openspec/backlog/index.md) — task inbox (park now, triage later); a
  quenching-managed sibling of `openspec/specs/`, **outside** the `docs/` bundle. Drop this
  bullet if the repo has no `openspec/`.

<!-- HOW TO FIND A TERM: the glossary is the repo's A–Z vocabulary index at
     docs/knowledge/glossary.md — a flat, alphabetically sorted bullet list (the same syntax
     every index.md uses), linked when a concept doc exists. To resolve a word: `grep -i
     '<term>' docs/knowledge/glossary.md` (or Ctrl-F it). A matching entry gives the local
     meaning and, when linked, its full concept doc; no entry means the term is not yet
     defined — add it with the `quenching-define` skill (one term), backfill many at once
     with `quenching-glossary-backfill`, or capture the concept with `quenching-learn` (which
     enters the term as its tail step). -->

To **create / edit / move** knowledge (keeping the listing + `log.md` in sync), use the
`claude-quenching` skills: `quenching-add` to add one, `quenching-define` to add a glossary
term, `quenching-align` to migrate/normalize, `quenching-harness` to keep this file thin.

## Agent etiquette

<Harness-operational rules only — how to behave in this repo, not what the domain is.
Anything that is durable knowledge belongs in a docs/ home above, cited here, never inlined.>

<!-- Root harness pointer, auto-loaded by Claude Code on every turn. Keep it a thin pointer:
     repo-wide operations + the docs/ home map. Knowledge is MOVED into docs/, never copied here.
     Installed/maintained by the claude-quenching plugin; this file is a harness pointer, not an
     OKF concept. -->

<!-- MOLD (claude-quenching · root harness pointer — do NOT copy this note into the produced file):
     Produces the repo-root CLAUDE.md as a THIN, HONEST navigation pointer over the OKF bundle.
     • NO frontmatter, NO `type` — a harness file is EXEMPT from OKF (okf-spec §strict-7); the
       validator skips it. Pointer honesty is verified by the `quenching-harness` skill, not the
       validator: EVERY link here MUST resolve before the run ends.
     • KEEP only what the agent needs on EVERY task (commands, env, etiquette). MOVE durable
       knowledge into its docs/ home (via the quenching-add procedure) and leave a one-line
       pointer that CITES the doc — never a paraphrase (a restated rule is drift, like a lying index).
     • List ONLY homes that exist in this repo — drop the bullets for absent homes; do not invent
       a home. Structure/links are canonical English; prose MAY follow the repo's language.
     • KEEP the "Resolving a term" pointer + the HOW-TO-FIND-A-TERM comment when the repo has a
       `knowledge/glossary.md` — term resolution via the glossary is a habit worth one line every
       turn. Drop both only if the repo has no glossary.
     • Size budget: aim ≤ ~60 lines. If it is longer, more knowledge still needs to move out. -->
