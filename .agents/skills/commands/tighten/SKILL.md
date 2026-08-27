---
name: quenching-commands-tighten
description: "Cut dead weight from ONE command body under plugins/quenching/commands/ or .agents/skills/ — justification for a directive already given, sediment from a mechanism the surface no longer has, a limit no run could reach, a rule another line or an invariant already carries. Triggers: \"enxugar esse comando\", \"revisar essa skill em busca de redundância\", \"cortar o conteúdo morto do corpo\", \"remover as justificativas desnecessárias\", \"tighten this command body\", \"cut the dead weight from this skill\". Leaves every trigger and every `Done when:` untouched, reports the incoherences the cut exposes instead of fixing them silently, and measures the delta against the working tree it opened."
---

<!-- GENERATED FROM .claude/commands/commands/tighten.md -->


# /commands:tighten — the binding half stays, the dead weight goes, the delta is measured

**Input**: `$ARGUMENTS` — one or more command paths under `plugins/quenching/commands/` or
`.agents/skills/`, or `--all` for the whole surface. `--review` reports the plan and writes
nothing. `--skip <path>` drops a file from a batch, repeatable.

A command body is re-sent on every turn of every run it governs, so a line that changes no
behaviour is billed forever for nothing. This command deletes those lines.

It is the command-body half of a pair. `/references:tighten` owns
`plugins/quenching/assets/references/**`, where rationale is **relocated** under its marker and
never deleted — a reference is read by `§`-address, and its rationale is the one asset a later
session cannot reconstruct. A body has no marker convention and no `§` API, so here the no-op
test **deletes**.

## The model, cited and never restated

| Rule | Owner |
| --- | --- |
| The no-op test; positive prescription; sediment / duplication / sprawl / negation | [doctrine.md](/plugins/quenching/assets/references/components-command-new/doctrine.md) §The no-op test, §Positive prescription, §Named failure modes |
| What a description may carry, and the trigger that is never cut for length | [doctrine.md](/plugins/quenching/assets/references/components-command-new/doctrine.md) §The three slots, and the boundary that must be earned |
| A `Done when:` per numbered step is what `lint` counts | [doctrine.md](/plugins/quenching/assets/references/components-command-new/doctrine.md) §Steps carry checkable completion criteria |
| The caps, the `sk-*` codes, and what no parser decides | [skills.md](/.knowledge/standards/automation/skills.md) §The verifier |
| A computed number restated in prose fans out — grep its literal form | [computed-fact-prose-fanout.md](/.knowledge/standards/quality/computed-fact-prose-fanout.md) |
| Which language the prose is written in | [communication.md](/.knowledge/standards/agents/communication.md) |

Resolve `cq` at `plugins/quenching-codex/scripts/bin/cq`, invoked by that literal quoted path
([align/tool-resolution.md](/plugins/quenching/assets/references/align/tool-resolution.md)
§Resolving the tool); branch on the **exit code** (0 ok · 1 findings · 2 refusal), never on prose.

**`--root` names the directory that HOLDS the command tree** — `.agents/` here (the parent of
`.agents/skills/`), `plugins/quenching/` for the plugin's. Pointed at a repo root it finds no
commands and reports a count of zero, which `registry reindex` then writes through as an empty
zone.

## The five classes of dead weight

| Class | The line is | The tell |
| --- | --- | --- |
| **justification** | a reason for a directive the same passage already gave imperatively | strip the clause after "because", "the reason is", "so that", "which is why" — the directive stands unchanged |
| **sediment** | prose describing a mechanism, file layout or option the surface no longer has | `grep` the tool and the surface for the thing it names; nothing answers |
| **unreachable limit** | a prohibition against something no run of this command could reach | name the step that would have to reach it — there is none |
| **restatement** | a rule another line of the same body, an invariant, or a cited owner already carries | delete the copy that does not sit where the rule operates |
| **ownership meta** | a claim about *which* command or file owns a rule, in place of the rule | the citation stays; the sentence about whose rule it is goes |

A **negation with no stated target** is converted, never cut: rewrite it as the positive
prescription (doctrine.md §Positive prescription). Negation survives only as a hard invariant
with its consequence attached.

**What always stays**, whatever the char count says: the binding half of every rule; a number a
rule actually depends on; every verbatim trigger in the description; every `Done when:` marker;
the directional `Not for:` boundary; and any negation that is a hard invariant.

## Workflow

### 1. Establish the baseline — from the WORKING TREE, never from `HEAD`
```bash
wc -c -l <path>
git status --porcelain <path>
python3 "plugins/quenching-codex/scripts/bin/cq" --root <surface-root> components lint --json
python3 "plugins/quenching-codex/scripts/bin/cq" --root <surface-root> components doctor --json
```
Record the file's char and line count **as it stands on disk now**, and the finding count for the
whole surface. A target already carrying uncommitted work measures from that work: a delta taken
against the last commit reports somebody else's edit as this pass's, and `git status --porcelain`
is what tells the two apart. The report names which baseline it used.

The surface-wide finding count is what step 6 compares against. A surface carrying pre-existing
findings is normal, so "lint exits 0" is evidence only against the number that was already there.
**Done when:** the file's chars and lines, the surface's finding count, and whether the target was
already dirty are written down as numbers.

### 2. Classify every line
Read the body whole once — classification is a judgement over the argument, not a regex. Every
line gets exactly one move: **keep**, one of §The five classes of dead weight, or **convert**.

A **restatement** is decided by two reads, never from memory: `grep` the body for the rule's own
key term, and read the `## Invariants` block whole. The copy that goes is the one that does not
sit where the rule operates — an invariant list is a checklist, and it legitimately repeats what a
step already said.

**A cut that changes what the command DOES is not a cut.** Name the input each candidate line
governs; if removing it leaves an input the body no longer answers, it was binding and it stays.
**Done when:** every line carries exactly one move, and every restatement names the line that
keeps the rule.

### 3. Record the incoherences the cut exposes — never fix them silently
Compacting a body brings its contradictions into contact: a premise the surface has since
falsified, an invariant that contradicts one of this command's own steps, a table row that
disagrees with the step above it. None of these is dead weight, and none is this pass's to decide
alone.

Each becomes a numbered finding: the two lines that disagree, quoted, and the reading that would
resolve them. They ride the same plan and the same OK as the cuts, and they are reported as fixes,
never folded into a cut's line count.
**Done when:** every contradiction found is a numbered finding in the plan, or the pass states it
found none.

### 4. ONE plan, one OK
Present, in this order: the baseline numbers; every **cut** quoted verbatim with its class; every
**convert** with its before and after; the numbered incoherence findings from step 3; and the
predicted after-count. State explicitly that no quoted trigger, no `Done when:` and no `Not for:`
clause is in the cut list — or name the one that is, and why.

Ask once, for the whole plan. `--review` stops here and reports the plan as the deliverable.
**Done when:** the plan is on screen with real before-numbers, and nothing has been written.

### 5. Apply
Write the approved moves and nothing else. Two conditions bind every write:

- **A cut that leaves a ragged wrap is reflowed in the same edit**, to the wrap width the file
  already uses. A half-width line is how a later reader spots an edit and re-opens a settled
  decision.
- **The file's existing language stays.** This pass changes what a body costs, never what it is
  written in.

**Done when:** every approved move is on disk, and no unapproved edit rode along with it.

### 6. Verify against the baseline, then report what was measured
```bash
python3 "plugins/quenching-codex/scripts/bin/cq" --root <surface-root> components lint --json
python3 "plugins/quenching-codex/scripts/bin/cq" --root <surface-root> components doctor --json
python3 "plugins/quenching-codex/scripts/bin/cq" components read <cited file> --sections "<each §>"
python3 -m unittest discover -s tests
bash plugins/quenching/assets/checks/functional-checks.sh
```
Every `§`-address the body still cites must resolve with exit 0 — a cut that took a citation's
context with it leaves an address pointing at nothing, and no linter sees that. The unittest suite
and `functional-checks.sh` run where the target is a plugin command; the harness is the **only**
check that proves the surface still LOADS, because `lint` and `doctor` read frontmatter off disk
and disk is not the session-start registry. Its exit 2 is inconclusive, not green.

Report **before → after** in chars and lines as measured numbers, the per-class breakdown of what
was cut, the step 3 findings and what was decided about each, and every check with its result. A
pass that moved little says so; an estimated delta is not a result.
**Done when:** the surface's finding count is at or below its baseline, every cited `§` resolves,
the functional harness has run or is reported as not run, and the report carries measured
before/after numbers.

## Batch mode (`--all`)

Take the baseline for the whole surface **once, in this session** — one `lint`, one `doctor`, one
`wc` sweep — and hand each file's numbers to the agent that works it, so none re-derives them.
Then delegate **one sub-agent per file**, the unit
[context-discipline.md](/.knowledge/standards/automation/context-discipline.md) §What a delegated
executor costs blesses.

- **First fan-out is plan-only.** Every agent returns steps 2–3 as a plan; nothing writes.
- **One table, one OK, for the whole batch.** Confirm once over all files, then fan out again to
  apply and verify.
- **Never fan out per step, and never let an agent widen to a second file.**
- Run the functional harness **once** for the batch, after the last file lands.

**Done when:** every file has an applied-or-skipped line with its measured delta, the skipped ones
say why, and the harness ran once over the result.

## Invariants to never violate

- **Never cut a quoted trigger from a description.** Only a measured miss retires one —
  `/quenching:components:command:eval`'s. A trigger that looks like sediment is REPORTED with that
  command named.
- **Never cut a `Done when:` marker**, and never leave a numbered step without one — `lint` counts
  that literal string (`sk-step-criterion`).
- **Never cut a `Not for:` clause to save chars.** The boundary is directional: a command whose
  neighbour stops naming it goes back to competing for the same spoken request, and no `sk-*` code
  sees a one-directional surface.
- **Never delete rationale from a file under `plugins/quenching/assets/references/`** — that tree
  is `/references:tighten`'s, and there rationale is relocated under its marker, never deleted.
- **Never fix an incoherence inside a cut.** It is a numbered finding on the plan (step 3),
  answered by the human, and reported as a fix.
- **Never measure the delta against `HEAD`** when the working tree already carried changes; the
  baseline is the file as it stood when the pass opened it.
- **Never report a delta that was not re-measured** by step 6.
- **Never report a linter's exit 0 as proof the command loads.** Only a fresh session proves that.
- **Never tighten a GENERATED body.** A file carrying a `GENERATED FROM <path>` marker is
  overwritten by the next translation, so the cut belongs to the `<path>` it names. Tighten that,
  then regenerate.
- **Never write during `--review`.**
- Never edit a `/.knowledge/` standard, a reference, or a file outside a command body from here —
  report it with the command that owns it (`quenching-knowledge-add`, `/references:tighten`).
