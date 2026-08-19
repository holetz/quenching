# Source ledger — traceability

Documentation earns trust by being *true*. Every **strong claim** — a number, a
statistic, a quote, a capability, a limit, a "best practice" — must trace to a
source. This is the rule that separates a technical document from marketing.

## The five allowed origins
A strong claim is valid only if it rests on one of these:

1. **Source file** — a `.md`/spec/README in the repo.
2. **Code** — a file:line in the codebase that proves it.
3. **Official docs provided** — a doc the user pointed to.
4. **A link the user gave** — an explicit reference.
5. **Marked inference** — your reasoning, *labeled as such* ("inferred:", "likely").

Anything else is an invention. **Never fabricate statistics, numbers, quotes,
benchmarks, or citations.**

## The ledger format
When a page carries important claims, produce a ledger:
```markdown
### Source ledger — <page>
| Claim | Source | Used in | Confidence |
| --- | --- | --- | --- |
| "85% of devs use AI coding agents" | Google, *New SDLC* (2026), p7 | landing stat band | high |
| "hooks fire only when wired" | `assets/hooks/README.md` | artifacts page | high |
| "most repos drift within a quarter" | inferred from source | intro | low — marked |
```
`Confidence`: **high** (direct source) · **medium** (derived) · **low** (inference —
must be marked in the prose too).

## Handling a missing source: `source gap`
When a claim has no origin, do **not** write it as fact. Instead:
- write **`source gap: <the claim + what's missing>`** in the ledger;
- either cut the claim, soften it to a marked inference, or ask the user/leave a
  visible `!!! note "Needs a source"` for the owner to fill;
- carry every open `source gap` into the phase-9 delivery report.

## Numbers, quotes, and read-times
- **Numbers/stats/quotes:** copy them verbatim from the source, with the citation.
  If you're computing something (e.g. a read-time from word count), say how
  (`~N min at 200 wpm`) — that's a marked, reproducible inference, not a fabrication.
- **Quotes:** exact text + attribution, or don't quote.

## Why it also helps LLMs
A ledger is agent-readable provenance: an LLM reusing the page can see which claims
are load-bearing and which are inferences, and cite the same source. It's the
integrity half of [llm-readability.md](llm-readability.md).
