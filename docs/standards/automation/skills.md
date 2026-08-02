---
type: standard
title: Command authoring and alignment
description: How the plugin's commands are classified, authored, named, and swept into conformance — one file per entry point, including the admission criterion that decides whether a command's description stays resident in context or goes typed-only
resource: plugins/quenching/commands/**, plugins/quenching/assets/references/**
tags: [automation, commands, taxonomy, authoring]
timestamp: 2026-08-02
audience: both
authority: current
source: add-quenching-skill-pair change (skill-authoring + skill-alignment deltas) + collapse-skills-into-commands (2026-07-26) + correct-command-citation-form (2026-07-31) + route-commands-without-always-on-descriptions (2026-08-02), which measured the disable-model-invocation claim this doc had asserted unmeasured and added the routed/typed-only admission criterion + the surface-wide description review added to /skill:align (2026-08-02)
maintainer: quenching
---

# Command authoring and alignment

The contract for how a command enters and stays in this plugin's automation surface, distilled
from the `add-quenching-skill-pair` change. `/skill:new` mints or edits one command; `/skill:align`
sweeps the whole surface into conformance. The naming these produce is governed by
[command-surface.md](../naming/command-surface.md); the layout rule for what may sit under
`commands/` by [../architecture/plugin-layout.md](../architecture/plugin-layout.md); the
writing-doctrine detail lives once in
`plugins/quenching/assets/references/skill-new/` and is cited, never restated.

**One file per entry point.** Claude Code merged custom commands into skills, so a command file
carries both the description that routes to it and the body that runs. Where this standard once
required a `SKILL.md` mirrored by a thin wrapper, there is now one file whose path is its
identity.

## Single-axis classification

Every command is classified on **exactly one axis**, and its path derives from it:

- **Domain-bound** — serves one folder subtree / one front. Pathed after that folder plus a verb
  (see [command-surface.md](../naming/command-surface.md)).
- **Generic** — serves the surface as a whole. A flat command named verb-object.

The classification test is naming the one folder/front the command acts on: exactly one answer
means domain-bound; "the whole surface" means generic; several unrelated targets means the command
is kept as-is and reported, never forced onto the axis.

**A technique is a parameter of a verb, not a new axis.** Variants of one action — different
elicitation scripts, different depths, different output shapes — become an argument to a single
skill, never sibling skills. The axis is the object plus the verb; the technique rides along. Four
interrogation modes (`interview`, `critic`, `premortem`, `alternatives`) shipped as
`/specs:refine --mode`, not as four `refine-*` commands, because four always-on
descriptions sit in context forever to express one verb four ways. Split only when the *object* or
the *verb* differs — a command that waits for a human-stated edit and one that generates the
questions are opposite directions of initiative and stay apart; two scripts for the same
interrogation do not.

## Authoring (`/skill:new`)

- **ONE file** per mint — a `commands/<path>.md` carrying frontmatter and body. Nothing else goes
  under `commands/`.
- **Writing doctrine** applied to every body: predictable naming, trigger phrases in the
  description's second sentence, a no-op self-test, no negation-only guidance, a body well under
  the size cap with shared procedure pushed into a bundled reference cited by absolute path.
- **Read the taxonomy rule before minting** (this standard); offer to create it from the template
  when a bundle-carrying repo lacks it.
- **One plan → one OK**: classification, names, files to write, and the OKF tail presented as a
  single plan, applied on one confirmation.
- **OKF tail** on every mint: regenerate the derived registry's GENERATED zone, offer a glossary
  entry for any coined term, append a log entry, and self-check.

## Alignment (`/skill:align`)

- **Read-only inventory** of the existing command surface before any plan — plus a `Glob` for any
  surviving `skills/<name>/SKILL.md`, which the verifier cannot see because it reads `commands/**`
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
  `/skill:new` that fixes it; a **description** is rewritten here, because its central question —
  does anything else answer to the same request? — is unanswerable one command at a time, and this
  is the only pass holding the whole surface. Prose about *how* a command works is cut, a missing
  concept or trigger is added, an unearned `Not for:` is waived with the competitor set named — and
  a quoted trigger is **never** deleted, which only a measured miss retires
  ([skill-evaluation.md](skill-evaluation.md) §Description tuning). `budget` joins `doctor` and
  `lint` in the probe, because it is the only one of the three that can see a description grown
  expensive while structurally clean.
- **Post-apply verification**: regenerate the registry zone, confirm the surface invariant, and
  report residue.

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
always-on context entirely (`budget` counts the command at 0), while `user-invocable: false`
saves nothing — the description still loads.

### What `disable-model-invocation` closes, and how we know

The row above and the paragraph above both assert that the field stops a conductor. That claim
stood **unmeasured for two months**, in a doc at `authority: current`, while the reference doc that
owns this class of fact carried no line about it at all. It has now been measured, and it holds:

> `Skill quenching:zzprobeb cannot be used with Skill tool due to disable-model-invocation`

Two arms with a control, filesystem-verified, Claude Code 2.1.220 — recorded as row 7 of
[claude-code-skill-command-mechanics.md](/docs/reference/tools/claude-code-skill-command-mechanics.md).
The control arm, identical but for the field, was listed and invoked by name successfully.

Recorded plainly because being right by luck is worth as much as being wrong here: the opposite
assertion would have been equally easy to write, and
[the mechanics doc's own history](/docs/reference/tools/claude-code-skill-command-mechanics.md)
carries a case where three artifacts supplied the contrary of an unmeasured row. Cite the row; do
not restate the mechanic from memory.

### The admission criterion — which class a command belongs to

Residency is an authored decision like the two above, and it has one test:

> A command is **routed** if, and only if, something reaches it **without a human typing its name** —
> a spoken trigger, or another command's body naming it. Everything else is **typed-only**.

Routed commands keep their description resident and are charged against the surface ceiling.
Typed-only commands declare `disable-model-invocation: true`, cost 0, and **keep their description
at full length** — see [context-budget.md](context-budget.md) §*The tier for a description that is
not in context*. Nothing is shortened by this decision; only residency changes.

Two consequences that are not obvious from the test itself:

- **"A human might type this" is not a reason to pick typed-only.** Every command can be typed. The
  question is whether anything *else* reaches it, and for a conductor stage the answer is yes even
  though a human can also type it — which is exactly how `/docs:harness`, `/docs:import-memory` and
  `/docs:glossary-backfill` would be misclassified by intuition.
- **The name-reachable half is not a judgment call.** `skills.py lint` derives it from the command
  bodies and reports `sk-inert-stage` at error for a typed-only command another body reaches by
  name. Classify against the instrument, not against recollection of who calls what.

The criterion is a floor, not a quota: it says which commands *may* be typed-only, never that any
must be. On a small surface it may admit nobody, and that is a legitimate outcome rather than a
failure to economise.

`context: fork` runs the command in a separate context. It is **forbidden** on any command that
gates on a mid-flow confirmation — a forked context cannot present the plan whose OK the run
depends on; a fork beside an `AskUserQuestion` grant is `sk-fork-gate`, an error. A command that
only reads and reports may fork freely, and that is the lever's home: self-contained, noisy,
summary-out work whose trail would otherwise sit in the main context forever.

## The execution profile

Every further capability a command uses — `context: fork` with `agent`/`background`, a
`model`/`effort` pin, `paths`, frontmatter `hooks:` — is an **authored, priced decision**: the
default profile is all levers off, and each departure enters the mint's plan with its stated
buy. An inline pin invalidates the session's prompt cache (a pin inside a fork or an agent is
cache-safe); `paths` binds a domain-bound command's autonomous firing to its folder. Subagents
are governed by [agents.md](agents.md), hooks by [hooks.md](hooks.md); the pricing doctrine
lives once in the plugin
(`plugins/quenching/assets/references/skill-new/capabilities.md`) and is cited, never
restated.

### `allowed-tools` is always scoped

Grant the narrowest set that lets the workflow finish. A tool that takes a scope gets one:
`Bash(python3:*)`, `Bash(py:*)`, `Bash(git status:*)` — never a bare `Bash`, which grants the whole
shell for the turn. `skills.py lint` reports a bare grant as `sk-unscoped-bash`.

One exception, and it must be **stated in the body**: a skill that runs the *target repo's own*
toolchain — its build, its tests, its linters, its migrations — cannot enumerate those commands in
advance, because they are the repo's, not the plugin's. Such a command may hold an unscoped `Bash`
provided its body says so and says why. `/specs:apply` is the standing example. The
finding is still reported; what the stated reason buys is a reader who can tell a deliberate grant
from an unexamined one.

**The grant is a declaration `skills.py lint` checks; whether it also restricts is unmeasured.**
What scoping reliably buys is that lint: a bare grant is reported, and a reader can see at a glance
which tools a command expects to reach. It has never been observed to stop a command from using a
tool it did not declare — [../quality/surface-verification.md](../quality/surface-verification.md)
§What this does not cover records that, and forbids claiming the enforcement anywhere until it is
measured, in either direction. So a command that must guarantee it writes nothing carries that
guarantee in its own numbered steps and its doctrine, never in its `allowed-tools` line.

## The verifier

`skills.py` is this front's verifier, the peer of `okf-validate.py` for `docs/` and `specs.py` for
`specs/`. Same contract: `--json` on every subcommand, exit **0** ok · **1** findings · **2**
refusal, errors setting the exit code and warnings never doing so.

| Subcommand | Decides |
| --- | --- |
| `lint [path]` | one command against this standard — the description caps, trigger position, the `Not for:` boundary, body length, a `**Done when:**` per numbered step, unscoped `Bash`, invocation coherence, and the profile's decidable slice (`sk-fork-gate`, `sk-profile-value`). On a surface carrying `.claude-plugin/plugin.json` it also grades **citation form** (`sk-bare-citation`), and a surface root brings `assets/references/**` into scope alongside `commands/**` |
| `doctor` | the surface invariant — a non-empty `description` on every command, no two resolving to the same `/` path, kebab-case segments — plus the **report-only** wider surface: `agents/*.md` and the hooks wired in `settings*.json` (`sk-agent-no-description`, `sk-hook-unmatched`, `sk-hook-llm-frequent`, `sk-hook-unparseable`), each routed to its mint, never migrated |
| `selftest` | that a file parked under `commands/` which is not an entry point fires `sk-no-description` — the layout rule's evidence |
| `registry reindex` | regenerates the registry's GENERATED zone; it **owns** that format |
| `budget` | what the surface costs before anything fires — see [context-budget.md](context-budget.md) |

Every threshold this standard names is implemented there, and the tool is the normative
statement: a rule whose only check is a sentence decays, because nothing fails when it is broken.

**What the tool does not decide.** The axis. Naming the one folder a command acts on is a claim
about what it is *for*, and no parser makes it. So are the doctrine's remaining tests — the
no-op test, sediment, sprawl, positive prescription. Those stay a human read, and a report keeps
the two kinds of evidence apart: a code names a threshold crossed, a read names a claim about
behaviour.

## Convergence condition

The surface is aligned when `skills.py doctor` and `skills.py lint` exit 0 — or every surviving
finding is named in the report by its `sk-*` code — and `skills.py registry reindex` reports
`changed: false`.
