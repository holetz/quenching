---
type: standard
title: Always-on context budget
description: What a command surface costs before anything fires — the two description caps, what the description may carry, the per-surface ceiling, and the disable-model-invocation exit that lets a typed-only command cost nothing at all
resource: plugins/quenching/commands/**, plugins/quenching/assets/bin/skills.py
tags: [automation, commands, context, budget, performance]
timestamp: 2026-07-29
audience: both
authority: background
source: instrument-and-extend-skill-front plan + collapse-skills-into-commands — measured on this plugin's own surface (28 commands 2026-07-26; 24 commands plus the agent surface 2026-07-27); the zero-cost exit distilled from improve-command-from-session, whose 26th command took it and left the total unchanged at 12,726
maintainer: quenching
---

# Always-on context budget

A command's body loads only when the command fires. Its **`description` never stops loading**: the
description of every command is in context on every session before a single command is selected.
That is the budget this standard governs. The mechanical rules live in [skills.md](skills.md)
§The verifier and are implemented by `skills.py`; this file owns the numbers and what may occupy
them.

Born `authority: background`: the ceiling below is **one surface's measurement**, not a proven
threshold. It graduates to `current` once `skills.py budget` has run on this plugin plus at least
two adopting repos. The collapse supplied one much larger measurement on one surface, which is not
that condition — a bigger number from the same repo is still one repo.

## Count the parsed value, never the YAML source

Every character count here is taken on the **parsed** frontmatter value. A description written as
a folded block scalar —

```yaml
description: >-
  First line of the description, wrapped
  across several indented lines.
```

— costs its *folded string*. The block indentation and the newlines are syntax the YAML parser
removes before Claude Code ever sees the field.

This is not pedantry. Counting the source lines instead inflates a description by roughly two
characters per line, which was enough to invent two cap violations on this plugin's own surface
that the model never paid for: the two skills reported at 1,568 and 1,559 measured 1,497 and 1,444
parsed, against a 1,536 cap. `skills.py` counts parsed, and any measurement offered against this
standard must say which it used.

## The two caps, per command

| Cap | Applies to | Code | Severity |
| --- | --- | --- | --- |
| **1,536** | `description` | `sk-metadata-cap` | error — Claude Code truncates past it |
| **1,024** | `description` | `sk-description-portable` | warning — the Agent Skills standard's hard limit |

Both apply to the same field now. `when_to_use` was a Claude-Code-only extension carried by the
skill half of a pair; with one file per entry point there is one description and nothing to add to
it.

**1,536** is what Claude Code will hold. What truncation eats is the **tail**, which is exactly
where the `Not for:` routing boundary lives — so a description that overflows loses the part that
tells the reader when *not* to fire it.

**1,024** is the Agent Skills standard, and a description over it is not portable to any other
host. This is a warning rather than an error because portability is a goal a repo may legitimately
decline — but it should decline it on purpose.

## What the description may carry

Three things, in this order, and nothing else:

1. the leading concept: what the command does and to what, in its own vocabulary;
2. the trigger phrases, quoted verbatim, one per distinct way a user asks — in the **second
   sentence**, so truncation cannot reach them (`sk-trigger-position`);
3. the boundary: `Not for: <adjacent job> → <owning command>` (`sk-no-boundary`).

**What belongs in none of them** — how the command works. The step order, the tool calls, the
checks it runs: a reader who needs those has already fired the command and loaded the body. A
description's job is to let a reader predict **when it fires and what will exist when it
finishes**, not how. Cutting exactly this prose from 17 over-limit descriptions on the
pre-collapse surface recovered 2,605 characters without touching a single trigger phrase.

## The per-surface ceiling

`skills.py budget` sums the whole surface and compares it against a ceiling:

```bash
skills.py budget --json              # against the default ceiling
skills.py budget --ceiling 40000     # against a surface's own
```

The current default is **12,726 characters** — this plugin's measured total across its 25 always-on
commands and 0 agent definitions, on 2026-07-28. It is a number a run produced, not one somebody
picked, and it is **revised only from a measurement**. The surface has since grown to 26 commands
and the figure has not moved, because the 26th is typed-only and counts 0 (§*The one command that
costs nothing* below).

**This ceiling has no headroom, and that is deliberate.** It equals the surface's current total, so
the next **always-on** command crosses it on the day it is minted. Under §*A new command is not free* below,
that is the signal working: `budget` **reports, it never refuses**, so crossing it prompts a human
to re-measure and re-set rather than blocking anything. The pre-diet default (36,503) was a
baseline the surface then sat 5,798 characters under, which meant it could never fire and
therefore told nobody anything.

### The ratchet fired exactly as predicted, and that is the evidence it works

This section previously read *"the 25th command crosses it on the day it is minted"* against a
ceiling of 11,565 over 24 commands. `/specs:isolate` was the 25th, and it did — the total went to
12,726, `budget` exited 1 naming the cost, and a human re-measured and re-set. The prediction and
the outcome are recorded together because a zero-headroom ceiling is easy to mistake for a
misconfiguration when it fires; it is the design working, and the design has now been observed
working once.

What the firing also showed is the cost of the shape: the re-set is a `skills.py` edit that **no
task declares**, sitting in lockstep with the figure this standard and the README both transcribe.
A ratchet with no headroom converts every new **always-on** command into a three-file bookkeeping
change. That is a real price for a signal that cannot go quiet, and it is the trade this standard is
choosing — stated so the next person to find it annoying knows it was chosen rather than overlooked.

The qualifier is load-bearing and was added after the fact: a typed-only command pays nothing and
fires nothing, so the ratchet has a second exit — see
[§The one command that costs nothing](#the-one-command-that-costs-nothing--disable-model-invocation-true).
The 26th command took it, and the re-set this paragraph predicts was never needed.

### Why the ceiling went 2,083 → 11,565

Not growth to be alarmed by — **the two numbers measure different surfaces.** The 2,083 was taken
on 2026-07-26, immediately after the collapse deleted the half of each pair that carried the quoted
trigger phrases and the `Not for:` boundary, leaving descriptions that were bare `/`-menu labels.
§*What the collapse measured* below says exactly that, and calls the restoration affordable. It has
since been restored on the commands that route by description, plus two trigger additions that
[skill-evaluation.md](skill-evaluation.md)'s measured hit rates argued for. The surface is not
carrying more prose about *how* commands work; it is carrying the routing information this standard
calls mandatory.

The re-measure deliberately **waited for the surface to stop moving**. A ceiling set while a fold
was still removing commands can never fire honestly, because every measurement during the shrink
describes a surface that no longer exists by the time the number lands.

`budget` over the ceiling exits 1 and lists the commands sorted by cost; exit 2 is unreachable from
it. A surface may legitimately be large, and the decision to cut is a human's.

### The total includes the agent surface

`budget` charges **every `agents/*.md` description** to the same total, and reports the split. This
repo's own surface defines no agents, so its second line reads zero:

```json
"breakdown": { "commands": 12726, "agents": 0 }
```

A repo that defines three agents averaging a 300-character description carries `"agents": 900` on
that line, and its total — the number the ceiling is compared against — is 900 higher.

An agent definition's description is always-on context by exactly the same mechanism as a
command's — it is carried so the model can decide whether to delegate, and it is paid whether or
not any delegation ever happens. Counting commands and exempting agents understated a surface by
however many agents it had defined, and it did so **invisibly**: the exempted cost never appeared
in any row, so a repo could add ten agents and watch its budget report stay flat.

The same discipline therefore applies to an agent's description as to a command's: it states what
the agent does **and when to invoke it**, and nothing about how it works. `/skill:agent:new` prices
that cost in its plan; `doctor` and `budget` read the agent surface through one shared enumeration,
so the two can never disagree about what it contains.

### The one command that costs nothing — `disable-model-invocation: true`

A command whose frontmatter carries `disable-model-invocation: true` counts **0** against the total
(`skills.py:1432`, applied at `skills.py:1439`). This is not an exemption the budget grants as a
favour: Claude Code drops such a command's description from the routing surface entirely, because
the model is never offered the chance to route to it. The description is still read — by a human,
in the file, and by `/skill:*` — but it is not resident in any session's context, so there is
nothing to charge.

That makes the ceiling's zero-headroom ratchet **a question rather than a verdict**. When the next
command would cross the ceiling, there are two exits, not one:

| Exit | When it applies | Cost |
| --- | --- | --- |
| **re-measure the ceiling** | the command must be auto-routable — Claude should reach it from a description alone | the bookkeeping change: `DEFAULT_CEILING`, the figure transcribed here, and `README.md` |
| **`disable-model-invocation: true`** | a human should choose it — it reads private data, is irreversible, or only makes sense when deliberately invoked | **0**, and the ceiling never fires |

The second exit is only honest when typed-only is the *right* design, never as a way to dodge the
measurement. `/skill:retro` is the case that established it and shows the test: a retro reads the
human's own session transcripts, so a human chooses it — the same reasoning that would have made it
typed-only at zero cost. It was minted as the 26th command against a ceiling equal to the total,
and the surface stayed at **12,726 characters** with the new command reporting `0`.

Stating this matters because the ratchet's phrasing invites the wrong inference. "The next command
crosses the ceiling the day it is minted" is true only of the next **always-on** command; read as a
universal it turns every new command into a mandatory three-file edit, and a spec that planned for
that bookkeeping found it was never needed.

Two things follow from the ceiling being per-surface rather than per-command:

- **A new command is not free.** Minting one adds its description to every session in the repo,
  forever. That is the honest cost to weigh against what the command saves.
- **Trimming is bounded by discovery.** Where a description cannot shrink without dropping a
  trigger phrase, it is **reported, not trimmed** — which triggers earn their place is decided on
  measured should-trigger / should-not-trigger hit rates, not by whoever is editing that day.

## What the collapse measured

Collapsing 28 skill+wrapper pairs into 28 command files took the surface from **30,705** characters
to **2,083** — a **93% cut**, ~7,676 to ~521 approximate tokens, off every session in every repo
that installs the plugin.

The saving is the *deletion of one of two descriptions*, not the compression of either. That
distinction matters for what it cost: the deleted skill description is where the quoted trigger
phrases and the `Not for:` boundary lived, so every command now reports `sk-trigger-position` and
`sk-no-boundary` against a description written as a `/`-menu label. Both are warnings, so the
budget looks clean while the routing information the two sections above call mandatory is absent.

**Spoken routing was measured afterwards and survived** — three natural phrases each reached their
command by description alone in a fresh process (see
[../naming/command-surface.md](../naming/command-surface.md) §Why there is no longer a wrapper).
So the number above is not hiding a broken surface. It is still true that **this number cannot
tell you whether a surface routes** — cheapness and routability are independent, and only a
should-trigger / should-not-trigger measurement decides the second. Read the two together.

The collapse also left **real headroom**: at 2,083 against a former 30,705, restoring explicit
triggers and boundaries to the surviving descriptions is affordable in a way it never was before.
That is a decision for measured hit rates, not for the next person who happens to be editing.

## Rough conversion

`budget` reports `approxTokens` as characters ÷ 4. It is a rule of thumb for the report, not a
tokenizer count, and no decision should turn on the last digit. The useful signal is the direction
and the order of magnitude.
