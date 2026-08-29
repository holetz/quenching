---
type: standard
title: Applicability of a finding's remedy
description: A declared remedy names an action the surface that emitted the finding actually offers — the measured case where the same CLI refused both actions it advised, why an inapplicable remedy teaches readers to ignore the whole findings output and not just that one item, and the refusal of its own that a case with no path still owes
resource: plugins/quenching/assets/bin/quenching/specs/commands/validate.py, plugins/quenching/assets/bin/quenching/specs/commands/doctor.py, plugins/quenching/assets/bin/quenching/components/commands/doctor.py, plugins/quenching/assets/bin/quenching/components/commands/lint.py, plugins/quenching/assets/bin/quenching/components/commands/registry.py, plugins/quenching/assets/bin/quenching/components/hooks.py
tags: [quality, findings, remedy, cli, surface]
timestamp: 2026-08-27
audience: both
authority: current
source: spec remover-secao-stray-de-um-documento (task 2.2) — the `sp-stray-heading` whose declared remedy advised two actions the very CLI that emitted it refused with exit 2, measured on 2026-08-17; the family's second site — the remedy whose conclusion the check itself does not observe — added by sk-unscoped-bash-le-o-corpo (2026-08-27), measured over the `sk-unscoped-bash` that advised declaring the reason in the body while reading only `allowed-tools`
maintainer: quenching
---

# Applicability of a finding's remedy

**A `remedy` names an action the surface that emitted the finding offers.** Not a description of the
desired state, not editorial advice: a path whoever reads the finding can walk with the same tool
that printed it.

The test is one line: *which command closes this?* If the answer does not exist, the remedy is not
written yet.

## The measured case

`cq specs validate` emitted this pair for years:

```
[warn ] plans/x.md: `## O que mudou` is not one of the fourteen canonical headings  (sp-stray-heading)
        remedy: rename it to a canonical heading or fold it into one
```

Both advised actions were impossible **through the CLI that advised them**. `cmd_section` resolved
every requested heading against the fourteen canonical ones and exited 2 on the first that did not
match — *before* looking at `--write` — so the stray section could not even be **named**, let alone
renamed or folded. There was no `--delete`, and `upsert_section` only reached a section the
resolution had already accepted. Closing the warning required editing the document outside the tool;
under an external backend, that means editing the issue by hand.

The cost is not the warning. It is that it was **permanent by construction**: nine documents in
`archive/` carried the finding on 2026-08-17, and not one of them had a way out.

## Why the yardstick is this one, and not "the text is correct"

An inapplicable remedy does not cost only the finding it accompanies. **It teaches readers to ignore
the whole output.** Whoever tries to follow a piece of advice and finds that the tool refuses it
learns to read the `remedy:` block as decoration — and starts skipping the fifteen that were
applicable too. A verifier lives on the trust that what it says is worth doing; one item that is not
worth it spends that trust on behalf of all the others.

It is also why "raise the severity" is never the first answer. While there was no path to a fix,
moving `sp-stray-heading` from `warn` to `error` would have turned an unsolvable warning into an
unsolvable failure. **The severity question is answerable only after the action exists.**

## How to write the remedy

- **Name the verb, with this case's arguments.** `cq specs section <slug> --fold "<stray>"` is a
  remedy; "fold it into a canonical section" is a wish. Where the values are in hand at the point
  of emission — the slug, the heading, the missing key — interpolate them: the reader copies and
  pastes.
- **A remedy that is a manual edit is still a remedy**, as long as the edit is described as an
  action (`fill it, or write \`- none — <reason>\``) and not as a state.
- **The action may refuse, and that does not break the rule — as long as the refusal explains
  itself.** `--fold` refuses a stray with no canonical section above it, with a message of its own
  (`sp-fold-no-anchor`), because picking a host there would be inventing an owner for the text. The
  reader who follows the remedy gets an answer from the tool, which is exactly what the remedy
  promised. What the rule forbids is the action that **does not exist**, not the one that exists and
  decides not to act.
- **When the action does not exist yet, the remedy is not the place to pretend it does.** Either the
  finding gets the command that closes it — which is spec work, not copywriting — or the text says
  honestly that the fix is manual, and why.

## The second site: the remedy the check itself does not observe

The first case is the action that **does not exist**. The second is quieter: the action exists,
whoever reads it can walk it — and the check that advised it does not look at the result.

`sk-unscoped-bash` advised, by construction, *"scope it to the commands the workflow runs, or
state the reason in the body"*, while reading only `allowed-tools`. The first half closes the
finding: a scoped grant stops matching. The second **changes not a byte** — a body that already
declared the reason got exactly the same output as one nobody had read. Whoever followed the advice
has no way of knowing they followed it.

The yardstick is the one from `## Why the yardstick is this one`, applied a step further: a remedy
whose conclusion the check does not observe spends the same trust as an impossible remedy, and
spends it in a worse way, because whoever follows it believes they have finished.

**The fix is not deleting the unobservable half.** The declared reason still holds — what was
missing was making it observable, and that asks for a form the check can see without pretending it
read prose: a literal line, and a boolean on the finding saying whether it is there. `lint` now
looks for `**Why \`Bash\` is unrestricted here.**` outside a fence and carries `priced` in the JSON,
and the two messages became different. The finding is still reported in both cases, because the
grant is the whole shell for the turn either way.

**What the literal form buys, and what it deliberately does not.** It gives the remedy an observable
end; it does not judge the reason. A predicate that decided whether the justification is *good*
would be inventing a verdict about prose that merely matched a pattern — the same dishonesty
[parse-honesty.md](parse-honesty.md) refuses when a parser fails and reports a content gap.

**The question this site adds to the one-line test:** after *which command closes this?* comes
*and does the check see that it was closed?* A remedy whose answer to the second is no is not
written yet — even if the action exists and someone can run it.

## The review trigger

Every new finding is born with that question answered. Every existing finding is re-evaluated when
the command that would close it changes shape: a renamed flag, a withdrawn verb, a new refusal added
ahead of the path the remedy names. It is the same fan-out as
[computed-fact-prose-fanout.md](computed-fact-prose-fanout.md) — the difference is that here the
restated fact is a **capability**, and it ages when the surface changes, not when a value changes.
