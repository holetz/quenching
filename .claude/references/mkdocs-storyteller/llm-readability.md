# LLM-readable docs

Great docs now have a second audience: the agents that read, copy, reconstruct and
cite them. A page can delight a human and still be useless to an LLM — or vice
versa. This is the doctrine for serving both from the same page.

## Why it matters
An agent lands on a page via search or a link, needs to lift an exact fact,
command, or contract, and act on it — without misreading a metaphor or missing a
detail hidden in an image. Docs that are *reconstructable* by an agent are also,
not by coincidence, clearer for humans: precise, structured, self-consistent.

## The rules

### Headings that are stable and descriptive
- A heading names the thing it covers in the reader's words — `Wiring the hooks`,
  not `Details` or `More`. An agent selects a section by its heading.
- **Don't rename headings casually** once published — the anchor is a contract.
  A renamed heading is a broken deep link for every agent that cited it.

### Predictable anchors
- Keep `toc.permalink: true` so every heading is addressable (`page/#wiring-the-hooks`).
- Prefer short, obvious heading text so the generated slug is guessable.
- Reference pages: one stable heading per entry, so `#option-name` always resolves.

### `TL;DR for agents` blocks
Where a page carries a reusable contract, add a compact, high-signal block:
```markdown
!!! abstract "TL;DR for agents"
    - **Does:** audits a repo's knowledge surface, installs fixes with confirmation.
    - **Contract:** `repo path → scored report → item-by-item install`.
    - **Invariants:** never removes without OK; three dimensions are proposed-only.
    - **Run:** `claude --plugin-dir ./plugins/claude-quenching`
```
Put facts, not adjectives. This is the block an agent copies first.

### Copyable, real examples
- Every command/config is real and copy-pasteable (`content.code.copy` on).
- No `foo`/`bar` where a real name exists. A fake example teaches a fake fact.
- Show the **expected output** so an agent can verify it reproduced the result.

### Explicit contracts
State inputs, outputs, preconditions and invariants **in text** — a table or list,
not implied by prose. If a step "usually" needs X, say exactly when.

### A glossary for core terms
Define each central/ambiguous term once, in one place, and link to it. Agents (and
newcomers) resolve `harness`, `dimension`, `payload` against a single definition
instead of inferring drifting meanings across pages.

### A concept map / index
Give the site one page that lists the core concepts and where each is defined — a
mental map an agent can load to navigate precisely. The "choose the right file"
routing table ([information-architecture.md](information-architecture.md)) is the
human-facing half of the same idea.

### Consistent relative links
Internal links are always relative (`../reference/api.md`) — portable, and they
survive `--strict`. Consistent link style lets an agent resolve the graph.

### Never hide critical facts only in images
An LLM may not read a diagram, and screen readers can't either. Any fact that
matters must exist **in text** too — the diagram/screenshot is a reinforcement, not
the sole source. Mirror Mermaid node content in a sentence or table nearby.

### No undefined metaphors
Metaphors are great *after* the literal definition ("the harness — everything
around the model"), never instead of it. An agent can't dereference a metaphor it
was never given the key to.

## Quick agent-readability checklist
- [ ] Headings are descriptive and won't be renamed.
- [ ] Anchors resolve and are guessable (`toc.permalink`).
- [ ] Reusable contracts have a `TL;DR for agents` block.
- [ ] Every example is real, copyable, with expected output.
- [ ] Inputs/outputs/invariants stated in text.
- [ ] Core terms defined once (glossary) and linked.
- [ ] A concept map / routing table exists.
- [ ] No fact lives only in an image or a metaphor.
- [ ] All internal links relative.
