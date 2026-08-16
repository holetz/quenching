---
type: standard
title: Plugin layout — what may live under commands/
description: commands/** is the only tree Claude Code registers, so everything that is not an entry point lives under assets/ and is cited by absolute path
resource: plugins/quenching/commands/**, plugins/quenching/assets/**, plugins/quenching/hooks/hooks.json
tags: [architecture, plugin, commands, layout, claude-code]
timestamp: 2026-08-16
audience: both
authority: current
source: collapse-skills-into-commands spec (2026-07-26) — proved by the migration itself; the self-contained-mold rule from the verify-allowed-tools-enforcement spec (2026-07-28); the boundary-reminder test from the collapse-remaining-language-clause-restatements spec (2026-07-31), whose narrowing case is the one defect it caught; §A mold cites nothing it does not also install re-justified on the mechanical reason (2026-08-03, enxugar-create-e-eliminar-o-rung-hooks spec) — the load-path test generalizes to the pasted-payload bash-block case the old does-a-copy-leave-the-plugin test missed; §hooks/hooks.json and the invocation rule's re-justification added by that spec's branch review, which caught the standard silent about a tree the same branch created and still resting the hooks/ placement on a hooks-config.json adjacency the same branch removed; the invocation rule amended by modularizar-specs-knowledge-components task 9.6 once `cq` became one entry serving both a hook event and every command body, the case the by-invocation rule had not anticipated; §A plugin body cites the target's bundle only where the align installs it — the sibling rule for the opposite direction, added by the marchas-do-orquestrador-vivem-no-plugin spec (2026-08-11) once the gears contract moved out of `/.knowledge/standards/` and the 23-line `## Impact` sweep showed the mold rule had never covered an ordinary command or reference body citing a fixed `/.knowledge/` path; the form-is-not-the-rule paragraph added by that spec's branch review (2026-08-11), which found five relative-form citations left standing in the payload the absolute-form sweep had just declared clean, two of them in files the same sweep had already edited; §A contract a command reads at runtime is a reference, not a standard distilled from that spec's `## Design` §1 at conclude (2026-08-11) — the criterion that overrode the shrunken-standard precedent of skills.md and plan-artifacts.md, which nothing had written down; the declare-the-split rule added by the orquestrar-specs-em-paralelo branch review (2026-08-16), which found the criterion silent about authoring time — that spec's `## Impact` declared a bundle standard and a plugin reference for one contract, and each task wrote its artifact whole, with both validators green
maintainer: quenching
---

# Plugin layout — what may live under `commands/`

The rule the collapse to one file per entry point created, and that nothing previously stated.

## `commands/**` is the only tree Claude Code registers

Every `.md` under `commands/` **is** a command. Not "is treated as one if it looks right" — the
path is the identity, so `commands/knowledge/align/references/conformance.md` would register as a
four-segment `knowledge:align:references:conformance` command and appear in the surface a session
pays for.

Therefore: **anything that is not an entry point lives outside `commands/`.** Shared procedure,
reference files, fixtures, eval cases, notes.

This is not a style preference. Before the collapse the question could not arise — a
`references/` folder sat beside a `SKILL.md`, inside `skills/`, which Claude Code registered by
folder rather than by file. Moving bodies into `commands/` made the adjacency illegal, and
nothing in the repo said so.

### `hooks/hooks.json` is the second tree Claude Code reads by convention

`commands/**` is the only tree that becomes an **entry point**, which is what the heading above is
about — but it is not the only path Claude Code loads from a plugin by name.
`plugins/quenching/hooks/hooks.json` is read at plugin-load time and its `hooks` block is wired for
every repo that has the plugin installed, with `${CLAUDE_PLUGIN_ROOT}` substituted at load. That is
why the OKF checker needs no copy in a target's `.claude/hooks/` and no merge into a target's
`.claude/settings.json`; the contract is
[../automation/hooks.md](../automation/hooks.md) §What this repo's own surface does under it.

**Two consequences for this standard.** A convention-named file at the plugin's top level is
neither an entry point nor an asset, so it sits *outside* both trees rather than being filed under
`assets/` — the `assets/` definition ("everything Claude Code must not surface as an entry point")
would otherwise swallow a file Claude Code is specifically meant to find. And the reason it may sit
there is the same one that governs `commands/`: **the path is the identity**, fixed by the host,
not chosen by us. A third such path added by Claude Code later inherits this paragraph without
amending the `assets/` inventory below.

## Where it goes instead: `assets/`

In this plugin, `assets/`. Its meaning is **deliberately wider** than it once was.

`assets/` used to mean *"the installable payload — copied into target repos, never executed
here"*. References are neither installed nor copied, so they did not fit that sentence. The
definition is now:

> **`assets/` is everything Claude Code must not surface as an entry point.**

The installable payload is a subset of that, not the whole of it.

**This widening was weighed against splitting the folder** (`assets/payload/` +
`assets/internal/`, say) and rejected while writing this standard, which is the point at which
the fudge would have shown. It does not read as one: both halves share the single property that
defines the folder — Claude Code ignores them — and the split would have bought a second
directory level, a second citation prefix, and 351 more path rewrites to distinguish two things
no reader confuses. If a future addition sits under `assets/` for a *third* reason, revisit; a
folder meaning three things is a folder meaning nothing.

### The revisit happened, and the answer was a name rather than a split

That trigger fired (2026-07-29). The inventory had drifted past three reasons without anyone
counting: `bin/` alone held four lifecycles — two tools installed into target repos (the specs
and components tools), one the plugin runs but never installs (the session tool, which says so in its own
docstring), and two bash harnesses that grade *this checkout* and are payload of nothing
(`functional-checks.sh`, `conclude-order-check.sh`). `mkdocs/` was missing from the inventory
line above entirely.

**The split stayed rejected.** Nothing in the drift touched the reasoning against it. What the
folder needed was the fourth reason **named and given its own subtree**, which is exactly what
`evals/` had already done for the third: the two harnesses moved to `checks/`.

The rule that decides where an executable sits, made explicit by the same move: **by how it is
invoked, not by whether it ships.** It placed by invocation only as long as each invocation kind
had its own file: the knowledge checker sat in `hooks/` because it was the one tool a **hook event**
fired rather than a command body, and the specs/components tools sat in `bin/` because commands were
what invoked them. One entry point serving both kinds is the case that rule did not anticipate.

**The rule as amended: `hooks/` holds a handler dedicated to a hook event; an entry that serves
both a command body and a hook lives in `bin/`.** `cq` answers `hooks/hooks.json`'s
`PostToolUse`/`Stop` wiring (`cq knowledge hook`) *and* every pillar's own command bodies (`cq
specs …`, `cq components …`), so it sits in `bin/` — the invocation that is not exclusive to the
hook path wins the placement, and `hooks/` is left to hold what actually is hook-exclusive:
`hooks/hooks.json` itself, which is wiring, not a handler, and does not move.

**The adjacency that used to justify a hook handler sitting beside its config is gone too.** The
original reasoning was that the knowledge checker had to sit beside the `hooks-config.json` it loaded
*from its own directory*, so separating the pair would break config loading in every installed
copy. Both halves are now false: the knowledge pillar reads the **target's**
`.claude/hooks/hooks-config.json` and nothing else — the bundle root it validates is the fixed
`/.knowledge/` convention, which no configuration names ([bundle-root.md](bundle-root.md)) — and there
are no installed copies left to break. `hooks/hooks.json` itself is unaffected: it is wiring read
at plugin-load time, addressed by the heading above, never by this one.

Current subtrees, by the reason each is here:

| Reason | Subtrees |
| --- | --- |
| payload copied whole by an align | `docs/` `specs/` `claude/` `mkdocs/` |
| payload applied per insert (molds) | `templates/` |
| tool the plugin executes | `bin/cq` (its four retired predecessors, unwired, still sit under `bin/` and `hooks/` until removed) |
| artifact of developing this repository | `references/` `evals/` `checks/` |

Four rows is one past what the warning above tolerates, so the warning needs restating rather
than quietly exceeding: what makes a folder mean nothing is a **membership rule that is a list**.
This one's rule is still the single sentence in the blockquote, and the four rows are
consequences of it that a reader can derive. Revisit when a subtree stops being derivable from
that sentence — not when the table gains a row.

### A contract a command reads at runtime is a reference, not a standard

The split between a bundle standard and a plugin reference is **by kind, not by size**. A standard
states what this repo holds itself to — a rule its own work is graded against. A reference carries
what a command reads *while running inside a target*: procedure, not a fact about anyone's repo.

Two standards already sit on that line and delegate across it. [skills.md](../automation/skills.md)
states the command taxonomy rule and leaves the writing doctrine to
`assets/references/components-command-new/`; [plan-artifacts.md](../workflows/plan-artifacts.md)
states what a spec must contain and leaves the per-section authoring to `specs-develop/`. Both keep
a standard because both **have** a rule this repo is graded against, separable from the procedure.

**Where a contract is entirely runtime procedure, there is no standard left to shrink** — it moves
whole into `assets/references/` and the standard is **retired**, under
[retiring-a-standard.md](../workflows/retiring-a-standard.md), never kept as a stub. A stub that
restates the reference is the second copy the delegation existed to prevent, now with the two
halves graded by different validators. `automation/orchestration-gears.md` is the worked case:
every sentence in it was procedure `/quenching:specs:cycle` reads mid-run, so shrinking it
would have left a pointer and nothing else.

Read the precedent by what it **kept**, never by its shape: a shrunken standard is evidence that a
separable rule existed there, not a template for a contract that has none.

**A spec that declares both artifacts must say which half each carries, or both get written whole.**
The criterion above does not apply itself at authoring time. A `## Impact` naming a bundle standard
*and* a plugin reference for one contract reads as two deliverables; one task writes each, and each
writes the contract entire. **Nothing mechanical catches that**: `cq knowledge validate` grades the
standard, `cq components lint` grades the reference, and neither can see the other — which is the
"two halves graded by different validators" above, arriving through the front door rather than as a
stub. The worked case is `orquestrar-specs-em-paralelo`, whose branch review measured six of
`workflows/spec-queue.md`'s eight sections restating `specs-fanout/fanout.md`, while a third task on
the same branch wrote into [align-surface.md](align-surface.md) that the contract lives in the plugin
and never in the bundle. Declare the split in `## Impact` — the rule this repo is graded against on
one side, the runtime procedure on the other — and the branch review stops being the only net.

## References are cited by absolute path, never relatively

Every citation of a bundled reference is:

```
${CLAUDE_PLUGIN_ROOT}/assets/references/<name>/<file>.md
```

`${CLAUDE_PLUGIN_ROOT}` substitutes inside a command body — measured, not assumed
([/.knowledge/external/tools/claude-code-skill-command-mechanics.md](/.knowledge/external/tools/claude-code-skill-command-mechanics.md)
rows 1–2, re-measured 2026-07-26 on Claude Code 2.1.215).

Relative paths are not merely inconvenient here, they are **wrong**: a relative path encodes the
depth of the *citing* file, so `commands/knowledge/documentation/build.md` and `commands/align.md`
would need different strings for the same target. The absolute form is one string everywhere,
which is what makes the citation set mechanically rewritable and mechanically checkable.

### `<name>` is the owning command's path, flattened

`commands/knowledge/add.md` owns `references/knowledge-add/`; `commands/align.md` owns
`references/align/`. The path, with `/` → `-`, and nothing else — which is why
`references/align-all/`, carrying the name of the retired `quenching-align-all` skill, was
renamed: a directory name that lies is forbidden by
[../naming/command-surface.md](../naming/command-surface.md), and it lies about the one thing this
convention encodes.

**Owning is not exclusive.** `references/align/` is cited by seven commands and
`references/components-command-new/` by four. The folder is named for the command that would have to *change*
the procedure, not for every command that reads it — that is what keeps a single name answerable
when a rule has several readers.

**`evals/` encodes the same source differently, and the difference is deliberate.** An eval tree
keeps the slashes — `commands/components/hook/new.md` ↔ `evals/components/hook/new/` — because it
mirrors exactly one command 1:1 and is renamed in the same mechanical step as that command, so the
two paths differ by one prefix and a reviewer finds it without searching
([components-command-eval/evaluation.md](/plugins/quenching/assets/references/components-command-eval/evaluation.md)
§Where the artifacts live). A reference folder is shared, has no 1:1 to preserve, and gains a flat
listing from being flattened. Same input, two encodings, two jobs — do not reconcile them.

### A mold cites nothing it does not also install

The rule above governs citation **inside** the plugin, where `${CLAUDE_PLUGIN_ROOT}` resolves. The
reason is mechanical, not a claim about what a target repo happens to have: Claude Code substitutes
`${CLAUDE_PLUGIN_ROOT}` only while it **loads a file that is part of the plugin itself** — the
variable is never exported to a shell, and never substituted for a copy sitting in a target repo, a
`bash` block pasted into a terminal, or any other reader outside that load path. A cross-reference to
`quality/surface-verification.md` is correct in the plugin's own bundle and dangles wherever that
load path does not hold — **even in a repo that has this very plugin installed**, because
installed-elsewhere is not the same fact as loaded-from-here.

**The test is "is whoever reads this inside the plugin's own file-load path?", not "does a copy
leave the plugin?"** The narrower test missed a case the wider one catches: a payload meant to be
pasted by a human into a raw terminal dangles a `${CLAUDE_PLUGIN_ROOT}` citation inside its `bash`
blocks the moment a human reads that block verbatim — before the file is copied anywhere, and
regardless of whether the plugin is loaded in the session doing the reading. Three trees still
answer the wider test today — `assets/templates/**` (the harness and front-matter molds),
`assets/knowledge/**` (the OKF skeleton, copied by `/quenching:knowledge:align`) and `assets/specs/templates/**`; a
fourth surface added later inherits the rule without amending this list. Naming one folder was how
a `${CLAUDE_PLUGIN_ROOT}` citation reached `assets/docs/` unnoticed: the reasoning covered it, the
wording did not, and nothing else checks. **No validator catches this** — a path that fails to
resolve reads as ordinary prose, so the rule is the only guard.

So **a template states its caveat self-contained**, citing only what the same align installs
alongside it. This is why a mold and the plugin's own copy of the same standard legitimately differ
in wording: `skills.md` may point at the measurement behind a rule, while
`skills-standard.md` states the rule and stops. That difference is the rule being obeyed, not
drift — do not "reconcile" them.

### A plugin body cites the target's bundle only where the align installs it

The rule above governs the direction a mold may not cite: content that will *become* target
content may not cite the plugin, because `${CLAUDE_PLUGIN_ROOT}` never resolves once it is copied
there. The opposite direction — a command or a reference, which stays in the plugin forever,
citing a path in the target's own bundle — needs its own rule, because nothing above states one.

`/.knowledge/standards/<subject>/<file>.md` is a **fixed string**
([bundle-root.md](bundle-root.md)), never a variable, so it reads as a well-formed link in every
repo whether or not the named file actually exists there. Existence is not syntax: a target only
carries that file if `/quenching:knowledge:align` installs it — that is, only if it exists under
`plugins/quenching/assets/knowledge/**` in this very plugin.

**A command body or a reference in `commands/**` or `assets/references/**` links a `/.knowledge/` path
only when that path exists under `plugins/quenching/assets/knowledge/**`.** Where it does not, the body
names the target in backticks, without a markdown link, and states the rule the citation would
have carried directly in its own prose — the citation was never load-bearing there, only
provenance, and the statement survives its removal. `commands/specs/create.md` is the didactic
case, two halves of the same rule in the same file: the line citing
[agents/communication.md](../agents/communication.md), which the align installs, stays linked; the
line that cited `workflows/plugin-configuration.md`, which it does not, loses the link and keeps
only the prose the citation was standing in for.

**The citation's form is not part of the rule.** An absolute `](/.knowledge/standards/…)` and a relative
climb `](../../../../.knowledge/standards/…)` are the same citation of the same target file, and both
dangle identically where the align installs nothing. A sweep that derives the class from the
absolute form alone under-counts it: this section's own branch review found **five** relative-form
citations still standing in the payload the sweep had just declared clean — two of them in files
that sweep had already edited. Derive the class from the target file, never from the link's
spelling.

Same mechanic as the rule above, same warning: **no validator catches this** — a path that fails to
resolve reads as ordinary prose, so the rule is the only guard.

### A boundary reminder is not a restatement

The rule above answers *may this text stand alone?*. The neighbouring question — *is this text a
restatement at all?* — had no owner, and a collapse sweep that lacks it will fold text that was
never a duplicate.

The case that forced it: thirteen places in this plugin say something about the repo's language.
Three are self-contained molds, covered above. Ten restate nothing — they state the
**canonical-structure boundary** ([../naming/command-surface.md](../naming/command-surface.md)):
the slug stays English, the prose around it follows the tag. Their whole value is being in context
at the instant a slug is written, which a citation spends a tool call to destroy.

**The ownership test** — is a reminder legitimate at all? A boundary reminder states the edge of a
rule the citing place **already owns**, seen from the other side. `/quenching:knowledge:add` owns where a doc goes
and what its slug looks like, so "the slug is canonical English, the body may follow the repo's
language" is that command's own rule at its border, not a second copy of somebody else's. A
restatement states a fact the citing place neither owns nor can change.

**The verifiable guardrail** — is it still legitimate *as written*? Three properties, each checked
against the owning doc:

1. **One clause.** A reminder names the border and stops. A paragraph is a copy.
2. **No fact the owner states.** The owner's scope, its exclusions and its declaration form belong
   to the owner. Repeat one and the reminder has become the thing it was allowed not to be.
3. **Never a narrowing.** A reminder may not scope the rule smaller than the owner scopes it.

The third earns the list on its own. `assets/README.md` narrowed the language rule to
`audience: human` docs — one adjective, no citation — and so taught a smaller rule than
[../agents/communication.md](../agents/communication.md) declares, which governs all prose the
agent authors. It survived weeks: the ownership test passes it, and no validator reads prose.
**Apply the guardrail, not the sentence.** "A boundary reminder is not a restatement", read loosely,
absolves every copy there is.

## The layout rule needs no check of its own

A stray file under `commands/` is a file with no `description`, which `cq components doctor`
already reports as **`sk-no-description`** — an error. Adding a second check for the same defect
would give one failure two names.

## How a violation actually presents

Worth writing down, because it is silent. A reference parked under `commands/` does not error at
load. It registers, costs its slot in the always-on listing, and appears in the `/` menu as a
command that does nothing when invoked. Nothing fails; the surface is just quietly wrong. That is
why the rule is stated structurally here rather than left to be noticed.
