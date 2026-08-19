# Visual language

*When and why* to reach for each visual element — the semantic layer. The exact
syntax and the extensions each one needs live in [material-toolkit.md](material-toolkit.md).

## The one rule
**Every visual element carries information, or it's cut.** A diagram that restates
a sentence, an emoji that decorates a heading, a card that holds one link with no
context — all noise. Elegant restraint beats a carnival: the Codex and Databricks
docs feel premium because they use *few* visuals, each doing real work.

## Choosing the form by content type

| The content is… | Use | Not |
| --- | --- | --- |
| A comparison of options | **table** / decision matrix | prose |
| A sequence of steps | **numbered list** or **Mermaid flow** | prose |
| A branching process / architecture | **Mermaid** graph | ASCII, a wall |
| "Pick your path" (2–4 routes) | **card grid** | a bullet list |
| Same task, different platform/profile/scenario | **content tabs** | repeated sections |
| A risk / tip / decision / tradeoff | **admonition** callout | inline sentence |
| Deep detail the skimmer skips | **collapsible `???`** | inline |
| Status / audience / difficulty / time | **badge** | a sentence |
| The first fold of a landing | **hero** | a plain H1 |

## Icons & emoji — signposts, never confetti
- Use Material/Octicons via `pymdownx.emoji` (`:material-rocket:`,
  `:octicons-arrow-right-24:`) for **navigational meaning** — the arrow that means
  "go here", the icon that labels a card's category.
- One icon per card/section max. If two adjacent headings both get an emoji, it's
  decoration — remove them.
- Keep a **consistent vocabulary**: pick one icon for "warning", one for "start",
  one for "reference", and reuse it site-wide so readers learn the signals.

## Cards — "choose your path"
Use a card grid when a reader must pick among **2–4** routes and each needs a
sentence of context. Each card = icon + bold label + one line of *why* + one
arrow-linked destination. More than ~6 cards is a table, not a grid.

## Tabs — one concept, many contexts
Use content tabs when the *same* idea has variants (macOS/Windows, beginner/expert,
Scenario A/B/C). Don't use tabs to hide unrelated content — a reader shouldn't have
to guess which tab holds the thing they need.

## Mermaid — flows, maps, architecture
Reach for Mermaid whenever a relationship is easier *seen* than read: a pipeline, a
state machine, a system diagram, a decision tree. Rules:
- Keep it to ~5–9 nodes; a diagram that needs a legend is two diagrams.
- Label edges with the *action* (`your OK, item by item`), not just arrows.
- It's theme-aware — don't hardcode colors; let Material's palette drive it.
- **Never put a critical fact only in the diagram** — mirror it in text so the
  skimmer and the agent both get it (see [llm-readability.md](llm-readability.md)).

## Badges — status at a glance
Small inline labels for metadata: `Status: stable`, `Audience: implementer`,
`Difficulty: intermediate`, `~10 min read`. Put them under the H1 as an "info bar".
Keep them factual and few — three or four, not a sticker album.

## Hero — the first fold
Use a hero **only on a landing** (site or major section). It must deliver: what
this is, the one-line promise, and one or two CTAs — nothing a reader must scroll
to get. Everything below it earns attention; the hero *is* the attention. Reuse the
existing hero component/CSS if the repo already has one; don't invent a second.

## Tables & matrices
The workhorse of dense docs. Use for comparisons, options, parameter lists, and
decisions. Give every column a purpose; if a column is empty for most rows, it's
prose in disguise. A **decision matrix** (option × "best when" × cost × "avoid
when") is the highest-leverage visual for a tradeoff page.

## Image strategy — propose before you add
External images are the one visual that needs sign-off, because they add weight,
break on CSP-restricted hosts, and rot. **Before adding any image, propose the
strategy and pick the lightest that works:**

| Need | Prefer | Why |
| --- | --- | --- |
| A flow / architecture / state | **Mermaid** | text-native, themeable, diff-able, no asset |
| A concrete UI / real output | **screenshot** (local asset in `docs/assets/`) | shows reality; keep it current |
| A brand/hero visual | **CSS gradient / local SVG** | no external fetch, crisp, tiny |
| An abstract concept | **simple diagram** (Mermaid/SVG) | precise beats decorative |
| Anything from a remote URL | **vendor it locally first** | external hosts break & disappear |

Announce the choice ("I'll draw this as a Mermaid flow / take a local screenshot")
and get a nod before committing binary assets.

## Palette & typography — restraint
Match the repo's existing theme (palette, fonts, light/dark toggle). Don't
introduce a new accent color per page. The goal is a site that reads as *one
system* — consistent, calm, legible — not a design showcase.
