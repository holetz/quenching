# Storytelling patterns

How to make a `.md` tree read like the Claude docs — a document you finish
because it kept pulling you forward, not one you abandon on page two.

## The voice (borrowed from the Claude docs)
- **Intent first.** Open with what the reader is trying to *do*, not with a
  definition. "Turn a pile of `.md` into docs people want to read" beats
  "MkDocs is a static-site generator."
- **Second person, present tense.** "You point it at a folder" — direct, active,
  never passive or academic.
- **Short sentences carry load.** One idea per sentence. If you need a comma to
  bolt on a second clause, it's probably a second sentence.
- **Confidence without hype.** State the thing plainly. No "revolutionary",
  no "simply just" — respect the reader's time and intelligence.
- **Show, then tell.** A concrete example before the abstraction. Readers
  generalize from a case faster than they specialize from a rule.

## The page arc
Every good page has the same skeleton:
1. **Hook** — one sentence: what this is / why you're here.
2. **The shortest path** — the 20% that serves 80% of readers, immediately.
3. **Depth on demand** — the rest, in a scannable order, with the heaviest
   material in tabs or collapsible blocks so it never blocks the skimmer.
4. **Where next** — a pointer (or a card grid) to the logical next page.

## The site arc
- **One spine.** Landing → problem → solution → how → reference. Each page
  answers the question the previous one raised. Use `prev`/`next` (front matter
  or theme footer) so the whole site is one continuous read.
- **Split by audience, not by file.** A "5-minute tour" and a "full reference"
  of the same feature are two pages, because a newcomer and an implementer
  scan differently. Don't average them into one lukewarm page.
- **One idea per page.** Two H1-sized ideas → two pages. A page that needs a
  table of contents three levels deep is usually two or three pages hiding in a
  trench coat.

## Progressive disclosure (the core move)
The reader should never scroll past what they don't need yet.
- Lead with the intent and the happy path.
- Collapse edge cases, deep-dives, and "why it's built this way" into
  `??? note` (collapsed) admonitions or content tabs.
- Link to a dedicated deep page instead of inlining 40 lines of caveats.
- Mirror the plugin's own doctrine: a thin, always-read top; heavy detail one
  click away.

## Turning a raw `.md` into a page — a checklist
- [ ] Does the first sentence say what this is and why the reader is here?
- [ ] Is the happy path reachable without scrolling past prerequisites?
- [ ] Are comparisons in **tables**, steps in **numbered lists**, options in a
      **card grid** — not buried in prose?
- [ ] Does every rule state its **why**?
- [ ] Are examples **real** (real commands, real names) and copy-pasteable?
- [ ] Is anything longer than a screen a candidate to **split or collapse**?
- [ ] Does the page end pointing **somewhere**?
- [ ] Do all internal links resolve **relative** (survives `--strict`)?

## Anti-patterns
- **The wall.** Ten paragraphs with no heading, list, or callout. Break it up.
- **The dump.** A README pasted verbatim as a page. Rewrite for a reader who
  landed here from search, not from the repo root.
- **The lukewarm merge.** One page trying to serve beginner and expert at once.
- **Toy examples.** `foo`, `bar`, `doSomething()` — replace with the real thing.
- **Orphan pages.** Reachable by URL but absent from `nav`. `--strict` catches
  these; so should you.
