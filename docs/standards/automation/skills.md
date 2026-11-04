---
type: standard
title: Command authoring and alignment
description: How the plugin's commands are classified, authored, named, and swept into conformance — one file per entry point, including the admission criterion that decides whether a command's description stays resident in context or goes typed-only, and where a target repository's skill is born and how its Claude bridge is generated and verified
resource: quenching/skills/**, quenching/references/**, quenching/assets/bin/quenching/components/commands/bridge.py, quenching/assets/bin/quenching/components/commands/migrate.py
tags: [automation, commands, taxonomy, authoring]
timestamp: 2026-11-03
audience: both
authority: current
source: collapse-skills-into-commands, 2026-07-26, correct-command-citation-form, 2026-07-31, route-commands-without-always-on-descriptions, 2026-08-02, spec 2118 (target skills in .agents/skills with a generated Claude bridge, 2026-10-28); spec 2160 (install only by deploy); lineage in ADR 0004
maintainer: quenching
---

# Command authoring and alignment

<!-- rules -->

The contract for how a command enters and stays in this plugin's automation surface, distilled
from the skill-authoring + skill-alignment change that first paired a skill with its wrapper.
`/quenching-components command-new` mints or edits one command; `/quenching-components align`
sweeps the whole surface into conformance. The naming these produce is governed by
[command-surface.md](../naming/command-surface.md); the layout rule for what may sit under
`commands/` by [../architecture/plugin-layout.md](../architecture/plugin-layout.md); the
writing-doctrine detail lives once in
`quenching/references/components-command-new/` and is cited, never restated.

**One file per entry point.** Claude Code merged custom commands into skills, so a command file
carries both the description that routes to it and the body that runs. Where this standard once
required a `SKILL.md` mirrored by a thin wrapper, there is now one file whose path is its
identity.

## Single-axis classification

Every command is classified on **exactly one axis: what it acts on** — asked as up to two
questions, in order, each with a single honest answer. The first question is a
subject/category; the second is the older domain-bound-vs-generic test, now read against
that category instead of standing alone.

**1. Category/subject — the first question.** Name the one subject the command belongs to
(`git`, `deploy`, `tests`, ...). A clean, evident answer wins. No evident subject, or
several unrelated ones, means there is no category: fall straight through to the second
question exactly as if this step did not exist — categorization only applies when it fits;
it is never forced.

**2. Domain-bound vs generic — the second question, read against the category.**
- **No category** — unchanged from before this rule: **domain-bound** when the command
  serves one folder subtree / one front, pathed after that folder plus a verb (see
  [command-surface.md](../naming/command-surface.md)); **generic** when it serves the
  surface as a whole, a flat command named verb-object; **neither** (kept as-is and
  reported) when several unrelated targets answer at once.
- **Category, no single real folder tied to the command** — e.g. `git` for a `commit`
  command: a subject, not a repo folder. The command nests flat under the category.
- **Category, and a real folder tied to the command** — the folder either **nests** inside
  the category or is **replaced** by it, per the convention already established for that
  category in *that* target repo (below). Several unrelated folders still fit neither and
  are kept as-is and reported, exactly as the no-category case.

### Reading the nest-vs-replace convention

The convention lives entirely inside the **target repo's own** `.agents/skills/<categoria>-*/`
— never in the plugin, and never in a dedicated registry file of its own:

- Skills already named `<categoria>-<folder>-…-<verb>` (the real folder folded into the one-segment
  name) → the convention already in force is **nest**.
- Skills already named `<categoria>-<verb>` with no real-folder segment → the convention already in
  force is **replace**.
- The category has no files yet in that repo, or the two shapes are already mixed
  (ambiguous) → ask the human once. The physical structure that first answer produces
  *becomes* the record — reused in silence for every later command of that category in that
  repo, with nothing else written down anywhere.

Two repos may read opposite conventions for the same category name without conflict: the
convention is never shared, catalogued, or asked twice for the same category in the same
repo.

**A technique is a parameter of a verb, not a new axis.** Variants of one action — different
elicitation scripts, different depths, different output shapes — become an argument to a single
skill, never sibling skills. The axis is the object plus the verb; the technique rides along. Four
interrogation modes (`interview`, `critic`, `premortem`, `alternatives`) shipped as
`/specs:refine --mode`, not as four `refine-*` commands, because four always-on
descriptions sit in context forever to express one verb four ways. Split only when the *object* or
the *verb* differs — a command that waits for a human-stated edit and one that generates the
questions are opposite directions of initiative and stay apart; two scripts for the same
interrogation do not.

## Authoring (`/quenching-components command-new`)

- **ONE file** per mint — a `commands/<path>.md` carrying frontmatter and body. Nothing else goes
  under `commands/`.
- **Writing doctrine** applied to every body: predictable naming, trigger phrases in the
  description's second sentence, a no-op self-test, no negation-only guidance, a body well under
  the size cap with shared procedure pushed into a bundled reference cited by absolute path.
- **Read the taxonomy rule before minting** (this standard); offer to create it from the template
  when a bundle-carrying repo lacks it.
- **One plan → one OK**: classification, names, files to write, and the OKF tail presented as a
  single plan, applied on one confirmation.
- **The `Not for:` boundary is directional, so a mint edits the neighbours too.** Writing the new
  command's own boundary points *outward*; until the commands it competes with name it back, a
  spoken request still lands on whichever of them already claims the phrasing. Nothing grades this:
  `sk-no-boundary` sees an absent boundary, never an incomplete one, and `doctor` only asserts that
  no two commands resolve to the same path. The mint's plan therefore carries the return edge — the
  competitor set, and the clause each of them gains — as part of the one confirmation.
- **OKF tail** on every mint: regenerate the derived registry's GENERATED zone, offer a glossary
  entry for any coined term, append a log entry, and self-check.

## Alignment (`/quenching-components align`)

- **Read-only inventory** of the existing command surface before any plan — plus a `Glob` for any
  surviving `skills/<name>/SKILL.md`, which the verifier cannot see because it reads `skills/**`
  and nothing else.
- **Collapse a legacy pair** into the one file its wrapper path names: the wrapper's `description`
  and `argument-hint`, the skill's `allowed-tools` and `effort`, the skill's body moved verbatim.
  Anything that sat beside the skill (`references/`, `evals/`) is re-homed outside `commands/`.
- **One consolidated migration plan, one confirmation** — collapses, renames, and the rule +
  registry created from the molds when missing; a rename referenced by product code or scripts gets
  its own individual confirmation.
- **MERGE, never clobber; never delete without a human word.** Only names, placement, and missing
  scaffolding change — existing bodies are preserved. An unclassifiable command is kept and
  reported, never forced.
- **One surface-wide description review, on its own confirmation.** A body is reported with the
  `/quenching-components command-new` that fixes it; a **description** is rewritten here, because its central question —
  does anything else answer to the same request? — is unanswerable one command at a time, and this
  is the only pass holding the whole surface. Prose about *how* a command works is cut, a missing
  concept or trigger is added, an unearned `Not for:` is waived with the competitor set named — and
  a quoted trigger is **never** deleted, which only a measured miss retires
  ([skill-evaluation.md](skill-evaluation.md) §Description tuning). `doctor` and `lint` stand in
  the probe.
- **Post-apply verification**: regenerate the registry zone, confirm the surface invariant, and
  report residue.

## Where a target's skill is born, and its Claude bridge

In a target repository a skill is born at `.agents/skills/<name>/SKILL.md` — `<name>` one segment
([command-surface.md](../naming/command-surface.md) §A target's skill name is one segment), the
frontmatter `name:` equal to it, sibling files in the same folder, references under
`.agents/references/**` and eval cases under `.agents/evals/<name>/`. That folder is the only
editable copy. `/quenching-components command-new` writes there and then runs
`cq components bridge --target <repo> --write`, never writing `.claude/skills/` by hand; a subagent
stays in `.claude/agents/`, because Claude Code 2.1.312 reads no generic home for it.

The bridge is generated, and verified by code:

- `cq components bridge --write` copies each `.agents/skills/<name>/` to `.claude/skills/<name>/`
  byte for byte, with one generated-from marker line after the `SKILL.md` frontmatter, and writes
  `.claude/skills/.generated-files.json` (one sha256 per file, `verifiedClaudeCode`). Claude Code
  does not read `.agents/skills/`, so without the copy the skill does not exist for it.
- `cq components bridge --check` exits 1 on drift — an edited copy, a source with no copy, an orphan
  copy whose source is gone — and 0 when the copy matches. A `.claude/skills/<name>/` the manifest
  does not list is refused (exit 2, `ct-bridge-unowned`), never overwritten.
- `cq components migrate --target <repo>` plans the move from the legacy `.claude/commands/` layout;
  `/quenching-align`, `/quenching-components align` and `/quenching-components status`
  run it with `bridge --check`, and apply a non-empty plan on one confirmation. It trusts no
  manifest: an `.agents/skills/<path>/` or `.agents/references/<rel>` beside a `.claude/` source is
  retired as the old translation only when its content is what `translate` generates from some
  committed version of that source (or that translation plus edits the current source already
  carries), so a hand-made skill of the same name is a conflict and nothing is written. A nested
  skill folder flattens whole, sibling files with it; `openspec-*` and `opsx/` stay put.
- A target is conformant when `migrate` reports `conformant: true` and `bridge --check` exits 0
  ([surface-translation.md](../architecture/surface-translation.md) §Target repositories).

## Invocation and permission are authored decisions

Three frontmatter fields decide who may invoke a skill and what it may reach. They are chosen
deliberately at mint, never left to default:

| `user-invocable` | `disable-model-invocation` | Who can invoke it | Use for |
| --- | --- | --- | --- |
| *(unset)* | *(unset)* | everyone | **the default here** — typable at `/` AND reachable by name, which is what lets a conductor invoke it as a stage and a spoken trigger route to it |
| `false` | *(unset)* | the model only | a command deliberately kept out of the `/` menu. With no wrapper left to stand in front of it, this hides the entry point itself |
| *(unset)* | `true` | the human only | a command whose cost or blast radius means a human must choose it — **never a conductor stage**, which it silently breaks ([measured](#what-disable-model-invocation-closes-and-how-we-know)) |
| `false` | `true` | **nobody** | never — this is `sk-unreachable`, an error |

The default row changed with the collapse. It used to be `user-invocable: false`, because every
skill hid behind a wrapper; there is no wrapper to hide behind now, so **both fields stay unset**
and a command is reachable by both paths.

`user-invocable: false` **hides the menu entry; it does not block programmatic invocation.**
`disable-model-invocation: true` is the only field that does — and it also stops a conductor
reaching the command by name. Confusing the two is how a command meant to be human-gated ends up
firing from a description match, or how a conductor ends up running and doing nothing. The two
also differ in what they cost: `disable-model-invocation: true` removes the description from
always-on context entirely, while `user-invocable: false` saves nothing — the description still
loads.

### What `disable-model-invocation` closes, and how we know

The row above and the paragraph above both assert that the field stops a conductor. That claim
stood **unmeasured for two months**, in a doc at `authority: current`, while the reference doc that
owns this class of fact carried no line about it at all. It has now been measured, and it holds:

> `Skill quenching:zzprobeb cannot be used with Skill tool due to disable-model-invocation`

Two arms with a control, filesystem-verified, Claude Code 2.1.220 — recorded as row 7 of
[claude-code-skill-command-mechanics.md](../../external/tools/claude-code-skill-command-mechanics.md).
The control arm, identical but for the field, was listed and invoked by name successfully.

<!-- rationale -->

Recorded plainly because being right by luck is worth as much as being wrong here: the opposite
assertion would have been equally easy to write, and
[the mechanics doc's own history](../../external/tools/claude-code-skill-command-mechanics.md)
carries a case where three artifacts supplied the contrary of an unmeasured row. Cite the row; do
not restate the mechanic from memory.

### The admission criterion — which class a command belongs to

Residency is an authored decision like the two above, and it has one test:

> A command is **routed** if, and only if, something reaches it **without a human typing its name** —
> a spoken trigger, or another command's body naming it. Everything else is **typed-only**.

Routed commands keep their description resident. Typed-only commands declare
`disable-model-invocation: true` — their description leaves every session's context, so nothing
ever reads it — and **keep it at full length**; nothing is shortened by this decision, only
residency changes.

Two consequences that are not obvious from the test itself:

- **"A human might type this" is not a reason to pick typed-only.** Every command can be typed. The
  question is whether anything *else* reaches it, and for a conductor stage the answer is yes even
  though a human can also type it — which is exactly how `/quenching-components harness-align`, `/quenching-knowledge import-memory` and
  `/quenching-knowledge glossary-backfill` would be misclassified by intuition.
- **The name-reachable half is not a judgment call.** `cq components lint` derives it from the command
  bodies and reports `sk-inert-stage` at error for a typed-only command another body reaches by
  name. Classify against the instrument, not against recollection of who calls what.

The criterion is a floor, not a quota: it says which commands *may* be typed-only, never that any
must be. On a small surface it may admit nobody, and that is a legitimate outcome rather than a
failure to economise.

### One router per vertical, no shortcuts

A vertical with several flows that conductors call (`specs`: create, develop, execute, conclude,
triage, status, orchestrate) carries **one routed skill** — `/quenching-specs <flow> <id>` — and
each flow's body lives once in `skills/quenching-specs/references/<flow>.md`, loaded with
`cq components read`. The pattern applies to **any vertical**, in the same shape:
`skills/quenching-<vertical>/SKILL.md` routes and `skills/quenching-<vertical>/references/<flow>.md`
holds each body (`knowledge`, `components` and `git` follow it). A flow's body is cited
`/quenching-<vertical> <flow>`; a skill with no flows is cited by its own name
(`/quenching-handoff`, `/quenching-align`).

**There are no shortcuts.** The router's description is what takes a request to the flow, so no
typed-only `/quenching-<vertical>-<flow>` skill sits beside it. A flow that a conductor or a human
names reaches the router with the `flow` argument and the id; a flow nobody should reach by
description or by stage (`autopilot`, `push`, `revert`, `cleanup`) runs **only on an explicit
mention**: the human's request names the flow. A request by stage or by description never picks
one of those four. The rule is stated in the router's body and as an invariant.

**Every front with flows has a router, core or not.** `specs`, `git`, `knowledge` and `components`
were first; `design`, `ops`, `proof`, `toolchain`, `delivery`, `security` and `opensource` follow the
same shape, so a request in natural language reaches any front without a typed shortcut. The cost is
residency, not flows: each router adds one description to the list, and the README's cost model
records the total. `components` `align` and `command-new` recognise a vertical with many
model-invocable entries and *propose* the router; they never apply it unasked. A reference that only
one router cites lives inside it (`skills/quenching-<front>/references/<front>-align/`); a reference
that more than one skill cites stays under `references/` (`front-align`).

**The router's grant is the union of its flows' grants.** Each flow declares its own `allowed-tools`
in the frontmatter of its reference, copied unchanged from the command it replaces. The router
grants their union and repeats no scope that a wider one already covers (`Bash(git status:*)` under
`Bash(git:*)`, everything under `Bash`). Where the union holds an unscoped `Bash`, the router body
carries the **Why `Bash` is unrestricted here.** line (§`allowed-tools` is always scoped, below). `cq components lint`
reports `sk-router-grant` at error when a router does not cover a flow's grant, `sk-router-description` at error when its description omits a flow of the table, and
`sk-dangling-citation` checks that `/quenching-<vertical> <flow>` names a flow in the router's table.
A `hooks:` block cannot ride a flow loaded through the router, so a flow that needs one stays its
own skill; the `git` router drops the warn-level hook of `commit`, since it only warned.

**The conductor calls the router.** `spec-runner`, `spec-orchestrator` and the translated surfaces
(Codex, OpenCode) invoke the router with the `flow` argument and the id.

### The description of a router

The description is a **map of intent per flow**, and the rule is that **what routes comes first and
the limit comes last**, so the description keeps working if the host truncates it:

1. **First sentence, in English:** the domain and every flow of the table by name
   (`Run one design flow: align, status, genre-new.`). It survives any truncation, and
   `sk-router-description` (error) reports a flow of the table the description does not name.
2. **Then the map:** one clause per flow, `<flow>: "<pt-BR trigger>", "<English trigger>"`, separated
   by `;`, with at least one trigger of each language per flow. A trigger is a phrase the user says,
   never the flow name repeated. A flow reached only by explicit mention carries `(only when named)`.
   No full stop sits inside a clause, so the sentence splitter of `sk-trigger-position` does not cut
   the map.
3. **Last:** `Not for: <the likeliest neighbour> → /quenching-<x> <flow>.`
4. **At most 1,024 characters** of the parsed value — the Agent Skills limit that Codex and OpenCode
   read. The 1,536 Claude cap is slack, not a target.

The 250-character `sk-description-budget` binds only a skill **without a table of flows**
(`quenching-align`, `quenching-handoff`): on a router it would contradict the map. The language of
the triggers is not a lint check; `test_router_descriptions.py` proves a pt-BR and an English
candidate exist for every flow by a heuristic declared in the test.

`context: fork` runs the command in a separate context. It is **forbidden** on any command that
asks the human anything mid-flow — a plan whose OK the run waits on, or a plain question one of its
steps puts to them. A forked context presents neither, so the run either hangs or answers itself.
The test is the interaction, never the interaction's weight, and that is already what the instrument
checks: a fork beside an `AskUserQuestion` grant is `sk-fork-gate`, an error, whatever the command
does with the grant.

**Dropping a plan gate does not buy a command the fork.** `/quenching-specs develop` writes its
consolidated edit without confirming it and stays forbidden all the same, because every level but
`low` asks at each stage and its approval close still waits on a go. A command earns the lever by asking nothing at
all — one that only reads and reports may fork freely, and that is the lever's home: self-contained,
noisy, summary-out work whose trail would otherwise sit in the main context forever.

### A target extends a vertical with its own router

A target repository that needs more flows in a family adds them to **its own** routed skill and never edits
an agent that came from the plugin (`.claude/agents/quenching-*.md`): the next `cq deploy --write`
would overwrite the edit, and the list would swell again. The unit of extension is the target's router:

- **The router** is `.agents/skills/<family>/SKILL.md`, one kebab segment without the `quenching-`
  prefix, so it never collides with the plugin's `quenching-<vertical>`. Its Claude bridge is
  generated as for any target skill.
- **The flow bodies** live in `.agents/skills/<family>/references/<flow>.md`, loaded with
  `cq components read`; the router lists one line per flow.
- **No former skill stays** as a shortcut. Body and grant move verbatim into the flow reference;
  nothing is deleted without a human word.
- **The grant** is the union of the flows' grants, as for the plugin's router.
- **The plugin's agents** keep calling the plugin's router; the target's main session calls the
  target's router.

**Which families earn a router.** The family is the first kebab segment of a local skill's name, and the
criterion is the plugin's: three or more model-invocable entries. `cq components status` reports it as
`families` (`skills`, `invocable`, `candidate`), a signal and never a finding, so `ok` and `state` do not
change. `components:align` reads it and proposes; the human confirms before anything moves. A target that
names its skills by suffix, or with no convention, gets no candidate and falls back to the manual report.

## The execution profile

Every further capability a command uses — `context: fork` with `agent`/`background`, a
`model`/`effort` pin, `paths`, frontmatter `hooks:` — is an **authored, priced decision**: the
default profile is all levers off, and each departure enters the mint's plan with its stated
buy. The five inline `model:` pins on `/quenching-specs-*` (opus: develop, conclude, triage; sonnet: create, execute) are that decision made on purpose — a pinned model is a price the spec lifecycle pays for judgment or throughput — and are recorded in [ADR 0007](../../decisions/0007-native-claude-code-features.md). An inline pin invalidates the session's prompt cache (a pin inside a fork or an agent is
cache-safe); `paths` binds a domain-bound command's autonomous firing to its folder. Subagents
are governed by [agents.md](agents.md), hooks by [hooks.md](hooks.md); the pricing doctrine
lives once in the plugin
(`quenching/references/components-command-new/capabilities.md`) and is cited, never
restated.

### `allowed-tools` is always scoped

Grant the narrowest set that lets the workflow finish. A tool that takes a scope gets one:
`Bash(python3:*)`, `Bash(py:*)`, `Bash(git status:*)` — never a bare `Bash`, which grants the whole
shell for the turn. `cq components lint` reports a bare grant as `sk-unscoped-bash`.

One exception, and it must be **stated in the body**: a skill that runs the *target repo's own*
toolchain — its build, its tests, its linters, its migrations — cannot enumerate those commands in
advance, because they are the repo's, not the plugin's. Such a command may hold an unscoped `Bash`
provided its body says so and says why. `/quenching-specs execute` is the standing example. The
finding is still reported; what the stated reason buys is a reader who can tell a deliberate grant
from an unexamined one.

**The reason is written as a line of its own, opening with the literal marker** — for `Bash`:

```markdown
**Why `Bash` is unrestricted here.** <the reason>
```

`lint` looks for that line, outside any fence, and carries the answer as `priced` in the JSON. It
is a **boolean, not a grade**: nothing reads the reason, judges it, or measures it. The form is
literal because the alternative is a check that claims to have understood prose it only pattern-
matched — and because a remedy has to be followable from the message alone, which is the defect
this marker closes. Before it, the finding advised *"state the reason in the body"* while reading
only `allowed-tools`: a body that already stated the reason got byte-identical output to one nobody
had looked at.

**The grant is a declaration `cq components lint` checks; whether it also restricts is unmeasured.**
What scoping reliably buys is that lint: a bare grant is reported, and a reader can see at a glance
which tools a command expects to reach. It has never been observed to stop a command from using a
tool it did not declare — [../quality/surface-verification.md](../quality/surface-verification.md)
§What this does not cover records that, and forbids claiming the enforcement anywhere until it is
measured, in either direction. So a command that must guarantee it writes nothing carries that
guarantee in its own numbered steps and its doctrine, never in its `allowed-tools` line.

## The verifier

`cq components` is this front's verifier, the peer of `cq knowledge` for `/docs/` and `cq specs` for
`/.specs/`. Same contract: `--json` on every subcommand, exit **0** ok · **1** findings · **2**
refusal, errors setting the exit code and warnings never doing so.

| Subcommand | Decides |
| --- | --- |
| `lint [path]` | one command against this standard — the description caps, trigger position, the `Not for:` boundary, body length, a `**Done when:**` per numbered step, unscoped `Bash`, invocation coherence, and the profile's decidable slice (`sk-fork-gate`, `sk-profile-value`). On a surface carrying `.claude-plugin/plugin.json` it also grades **citation form** (`sk-bare-citation`); on a target's own surface it reports a **dangling citation** (`sk-dangling-citation`, warn) — a `/front:verb` whose front exists there but whose command does not. A surface root brings `references/**` into scope alongside `skills/**` |
| `doctor` | the surface invariant — a non-empty `description` on every command, no two resolving to the same `/` path, kebab-case segments, and on a target's own surface no dangling citation (`sk-dangling-citation`) — plus the **report-only** wider surface: `agents/*.md` and the hooks wired in `settings*.json` (`sk-agent-no-description`, `sk-hook-unmatched`, `sk-hook-llm-frequent`, `sk-hook-unparseable`), each routed to its mint, never migrated. A file parked under `commands/` which is not an entry point is exactly this shape — `sk-no-description` — the layout rule's evidence |
| `registry reindex` | regenerates the registry's GENERATED zone; it **owns** that format |
| `bridge --target <repo> [--write\|--check]` | a target's `.claude/skills/` copy matches `.agents/skills/` (§Where a target's skill is born) |
| `migrate --target <repo> [--write]` | the move plan from the legacy target layout; an empty plan is `conformant: true` |

**The caps, inherited from the README's cost model.** A `description` is bounded by **1,536
characters** — Claude Code truncates past it, a fact of the host rather than a ceiling of ours,
which is why `sk-metadata-cap` reports the truncation's tail, where the `Not for:` boundary lives
— and by **1,024 characters** (`sk-description-portable`), the Agent Skills standard's hard limit
on a command's portability outside Claude Code. A body stays well under **500 lines**
(`sk-body-length`).

Every threshold this standard names is implemented there, and the tool is the normative
statement: a rule whose only check is a sentence decays, because nothing fails when it is broken.

**What the tool does not decide.** The axis. Naming the one folder a command acts on is a claim
about what it is *for*, and no parser makes it. So are the doctrine's remaining tests — the
no-op test, sediment, sprawl, positive prescription. Those stay a human read, and a report keeps
the two kinds of evidence apart: a code names a threshold crossed, a read names a claim about
behaviour.

## Convergence condition

The surface is aligned when `cq components doctor` and `cq components lint` exit 0 — or every surviving
finding is named in the report by its `sk-*` code — and `cq components registry reindex` reports
`changed: false`.
