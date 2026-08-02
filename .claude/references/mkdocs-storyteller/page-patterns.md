# Page patterns

Ready skeletons per page type. Each names its **intent**, its **primary
audience**, and the **shape** to reach for. Copy the skeleton, then fill it with
real, sourced content — never ship the placeholder text.

> Syntax for every element below (admonitions, cards, tabs, Mermaid, badges) is
> in [material-toolkit.md](material-toolkit.md); *when* to use each is in
> [visual-language.md](visual-language.md).

## Landing page
**Intent:** promise + orient. **Audience:** skimmer. **Shape:** hero → one-line
value → "choose your path" cards → problem/solution → quick start CTA.

```markdown
<div class="hero">…name · one-sentence promise · two buttons…</div>

<div class="grid cards" markdown>
- :material-rocket: **Just run it** — first win in 2 commands. [Get started →](install.md)
- :material-lightbulb: **Understand why** — the problem in depth. [Concepts →](concepts/index.md)
- :material-book: **Reference** — the exact detail. [Reference →](reference/index.md)
</div>

## The problem   ## The solution   ## Quick start
```

## Quick start
**Intent:** first success fast. **Audience:** implementer. **Shape:** prerequisites
→ copy-paste steps → "you should see…" → next step. Keep it under one screen; push
explanation to the concept page.

```markdown
!!! note "Prerequisites"  …one list…
1. `command one`   2. `command two`
!!! success "You should see…"  …the observable outcome…
Next: [The full workflow](workflow.md)
```

## Tutorial (learning-oriented)
**Intent:** teach by doing an end-to-end example. **Audience:** implementer/learner.
**Shape:** goal → numbered stages, each with code + expected result → recap. One
runnable thread; no branching. State the goal and the finished artifact up front.

## Concept / explanation
**Intent:** build the mental model. **Audience:** human + agent. **Shape:** the
idea in one line → why it exists → a diagram → the boundary/tradeoff → link to the
reference. Prefer one diagram over three paragraphs. End with a `TL;DR for agents`.

## Reference
**Intent:** exact, lookup-optimized detail. **Audience:** implementer + agent.
**Shape:** stable headings per item, a parameters/options **table**, one example
per item. No narrative — optimize for `Ctrl-F` and predictable anchors. Every item
heading is a stable anchor an agent can deep-link.

## Architecture
**Intent:** how the parts fit as a system. **Audience:** human + agent. **Shape:**
one-line system summary → a **Mermaid** diagram → a table mapping each node to its
own page → the fixed/adaptive or key boundaries. Describe *relationships*, don't
restate each part (link to its page).

## Workflow / process
**Intent:** the real path end to end. **Audience:** implementer. **Shape:** the
governing principle as a callout → a **Mermaid** flow or numbered steps → scenario
**tabs** (or a card grid) for variants → what each step produces.

## Decision / tradeoff
**Intent:** help choose. **Audience:** human + implementer. **Shape:** the question
→ a **decision matrix** → a recommendation with its *why* → when to reconsider.

```markdown
| Option | Best when | Cost | Avoid when |
| --- | --- | --- | --- |
| A | … | … | … |
| B | … | … | … |
!!! tip "Recommendation"  Default to **A** unless … — because …
```

## Troubleshooting
**Intent:** unblock fast. **Audience:** implementer. **Shape:** a **symptom → cause
→ fix** table first (scannable), then `???` collapsibles for the long cases. Lead
with the symptom (what the reader sees), not the internal cause.

## Catalog / index
**Intent:** enumerate a set (APIs, artifacts, entities). **Audience:** implementer
+ agent. **Shape:** a table with one row per entry (name · purpose · link · status
badge), generated deterministically where possible; each entry links to its own
reference page.

## Changelog / evolution
**Intent:** what changed and why. **Audience:** human + agent. **Shape:** reverse
chronological; each entry = date · one-line summary · impact · link. Stable
headings per version so an agent can diff. Never rewrite history entries.

## "For humans / for agents" dual page
**Intent:** serve both explicitly. **Shape:** the human narrative up top, then a
fenced, machine-oriented section:

```markdown
## For agents
!!! abstract "TL;DR for agents"
    - Contract: `input → output`
    - Invariants: …
    - Copy-paste: ```…```
    - Canonical anchors: #install, #run, #config
```

See [llm-readability.md](llm-readability.md) for the full agent contract.
