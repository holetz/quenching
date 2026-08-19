# Storytelling craft & voice

The page-level writing layer: how to make a single page read like the Codex docs
— finished because it kept pulling the reader forward, not abandoned on screen
two. (Site-level structure is [information-architecture.md](information-architecture.md);
ready skeletons are [page-patterns.md](page-patterns.md).)

## The voice
- **Intent first.** Open with what the reader is trying to *do*, not a definition.
  "Turn a pile of `.md` into docs people want to read" beats "MkDocs is a static
  site generator."
- **Second person, present tense, active.** "You point it at a folder."
- **One idea per sentence.** If a comma bolts on a second clause, it's probably a
  second sentence.
- **Confidence without hype.** No "revolutionary", no "simply just". Respect the
  reader's time and intelligence.
- **Show, then tell.** A concrete example before the abstraction — readers
  generalize from a case faster than they specialize from a rule.
- **Dense, not padded.** Every sentence earns its place. Beautiful ≠ wordy.

## The page arc
Every strong page has the same skeleton:
1. **Hook** — one sentence: what this is / why you're here.
2. **The fast path** — the 20% that serves 80% of readers, immediately.
3. **Depth on demand** — the rest, scannable, heaviest material behind tabs or
   collapsible `???` blocks so it never blocks the skimmer.
4. **Next step** — a pointer (or card grid) to the logical next page.

## Writing the hook
The first two lines decide whether the page gets read. A good hook states the
*payoff* or the *stakes*:

- ✅ "A hook only runs if it's wired — copying the script does nothing."
- ✅ "Point it at a repo; get a scored gap report; install the fixes with your OK."
- ❌ "This document describes the hooks subsystem." (topic, not payoff)

## Progressive disclosure (the core move)
The reader must never scroll past what they don't need yet.
- Lead with intent and the happy path.
- Collapse edge cases, deep-dives and "why it's built this way" into `??? note`
  (collapsed) blocks or content tabs.
- Link to a dedicated deep page instead of inlining 40 lines of caveats.
- Mirror the thin-top / heavy-detail-one-click-away pattern the best docs use.

## Make prose scannable
Prose is the *last* resort for structured information. Before writing a paragraph,
ask if it's really:
- a **comparison** → table;
- a **sequence** → numbered list or Mermaid flow;
- a **set of options** → card grid;
- a **rule with a reason** → `!!! tip` / `!!! warning` callout;
- a **decision** → a small matrix (see [page-patterns.md](page-patterns.md)).

Keep real paragraphs to 2–4 sentences. Every rule states its **why** — the reason
is the part that sticks.

## Turning a raw `.md` into a page — checklist
- [ ] First sentence says what this is and why the reader is here.
- [ ] The fast path is reachable without scrolling past prerequisites.
- [ ] Comparisons are tables; steps are numbered; options are cards.
- [ ] Every rule states its **why**.
- [ ] Examples are **real** (real commands/names) and copy-pasteable.
- [ ] Anything longer than a screen is split or collapsed.
- [ ] Risks/tips/tradeoffs are callouts, not buried in prose.
- [ ] The page ends pointing **somewhere**.
- [ ] Internal links are **relative** (survive `--strict`).

## Anti-patterns
- **The wall** — many paragraphs, no heading/list/callout. Break it up.
- **The dump** — a README pasted verbatim. Rewrite for someone who arrived from
  search, not from the repo root.
- **The lukewarm merge** — one page serving beginner and expert at once.
- **Toy examples** — `foo`, `bar`, `doSomething()`. Use the real thing.
- **Orphan pages** — reachable by URL, absent from `nav`.
- **Decoration** — a diagram/emoji/card that carries no information.
- **Marketing air** — adjectives with no fact behind them. Delete or ground them.
