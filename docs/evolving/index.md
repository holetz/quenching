# Evolving the method

`claude-quenching` is a **living method**, not a static plugin. The shipped skill
describes **only the present** — what the method does today. **How it got there**
(rounds, revisions, superseded decisions) lives in the non-shipped
[`evolution/`](https://github.com/israelholetz/claude-quenching/tree/main/evolution)
layer, alongside two maintainer agents at the repository root in
[`.claude/agents/`](https://github.com/israelholetz/claude-quenching/tree/main/.claude/agents).

> This is **maintainer tooling**. It is versioned in the repo but **never shipped**
> to a target repo, and never installed by the method.

## Two complementary agents

- **`quenching-evolutionist` — advances the frontier.** Each round (`R*`) makes
  **one** improvement beyond today's state, on a topic not yet addressed, and
  increments `current-round`.
- **`quenching-reviewer` — critiques and refines what exists.** Each invocation
  (`Rev*`) revisits an already-made definition and improves it (sharpens a smell,
  fixes a stale source, merges/prunes, supersedes a round) **without** advancing
  the frontier.

Both read the next action from the spine
([`evolution/README.md`](https://github.com/israelholetz/claude-quenching/blob/main/evolution/README.md)) —
which holds the **anchor state**, the **exclusion index** (one line per addressed
boundary), the **advance backlog** and the **review queue** — and write the detail
into the right per-context file in
[`evolution/log/`](https://github.com/israelholetz/claude-quenching/tree/main/evolution/log).
The research input lives in
[`evolution/research/`](https://github.com/israelholetz/claude-quenching/tree/main/evolution/research);
every round requires **≥1 citable source** (URL + date).

## Evaluating the method as a production tool

The method **is an agent tool**, so it is evaluated against **realistic tasks**.
Before closing a round that changes a detection rule, the evolutionist runs a
**fixtures harness** — small sample repos with one **planted gap** each — and reads
three measures:

- **hit rate** per dimension (was the planted gap flagged, with `file:line`?);
- **false-negative rate** — the metric that matters most (a real gap that slips
  through means the base *looks* audited and isn't);
- **cost** per dimension (does one dimension consume disproportionately?).

The *fit-to-repo* prescription layer is evaluated the same way, with
**planted-profile** fixtures carrying the expected emphasis/roadmap as ground
truth (a clearly-shaped repo that comes out with flat emphasis is the key failure;
an ambiguous-shape repo *should* get flat emphasis).

## Contributing

The full maintainer guide — how to invoke the agents, the golden rule against
hand-editing the method, and the repository conventions — is in
[`CONTRIBUTING.md`](https://github.com/israelholetz/claude-quenching/blob/main/CONTRIBUTING.md).
