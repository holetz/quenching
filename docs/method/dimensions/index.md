# The 15 dimensions

We said the harness has parts. Here they are — the anatomy of the
[knowledge surface](../../context/knowledge-surface.md), 15 of them. Each is a
distinct piece of what tells a Claude Code agent how this repo works — the CLAUDE.md
it loads, the docs it reads, the skills and hooks it runs, the boundaries that keep
each fact in one place — and each maps back to a component of the paper's *harness*
or one of its six context types (**Instructions, Knowledge, Memory, Examples, Tools,
Guardrails**). The method scores every one of them
([Present / Partial / Drifted / Absent](../../plugin/workflow.md), with `file:line`
evidence). Each dimension below has its own page: *what it is · why it belongs in
the method (with the research behind it) · what good looks like · how it drifts ·
how the method closes the gap*.

The 15 aren't a flat list — they fall into four layers, and the layers are just the
harness sorted by *where the knowledge lives and when it's paid for*. Reading them in
this order is the shortest path to the whole picture.

### The entry point — loaded every session

The **static** rule file: the one artifact that enters context *before the first
message*, so every word in it costs budget forever.

- [1 · CLAUDE.md entry map](01-claude-md.md)

### The versioned knowledge base — `docs/`

The paper's **Knowledge** context type: the durable, human-and-agent-shared record —
what is true now, where you're headed, what's still open, what's decided, and the
domain itself. **Dynamic** — loaded on demand, so it costs nothing until something
pulls it in.

- [2 · Standards (`docs/standards/`)](02-standards.md)
- [3 · Vision (`docs/vision/`)](03-vision.md)
- [4 · Backlog](04-backlog.md)
- [5 · ADR (`docs/decisions/`)](05-adr.md)
- [11 · Catalog (`docs/catalog/`)](11-catalog.md)

### The active surface — `.claude/`

The harness's executable components — the paper's **Tools**, procedural knowledge,
and **Guardrails**: capabilities, isolated workers, deterministic automation,
shortcuts, what it learned, and its external reach.

- [6 · Skills](06-skills.md)
- [7 · Sub-agents](07-subagents.md)
- [8 · Hooks (+ the `scripts/` home)](08-hooks.md)
- [9 · Commands](09-commands.md)
- [10 · Memory](10-memory.md)
- [15 · MCP — external integration](15-mcp.md)

### The cross-cutting doctrine

The rules that hold the other thirteen together — the paper's **Guardrails** plus
the binding principle: one home per fact, written conventions, and how the agent
should behave.

- [12 · Boundary doctrine](12-boundary-doctrine.md)
- [13 · Conventions](13-conventions.md)
- [14 · Guardrails](14-guardrails.md)

## At a glance

| # | Dimension | What it covers | Canonical home | Type |
| --- | --- | --- | --- | --- |
| [1](01-claude-md.md) | CLAUDE.md entry map | the always-loaded map; progressive disclosure; pruning | adaptive | skill + hook |
| [2](02-standards.md) | Standards | the current/active standards layer; index in sync | `docs/standards/` · fixed | skills + scaffold |
| [3](03-vision.md) | Vision | where the repo is heading, no timeline | `docs/vision/` · fixed | proposes only |
| [4](04-backlog.md) | Backlog | what's still missing, by pillar | `docs/backlog/` · fixed | scaffold |
| [5](05-adr.md) | ADR | open decisions with weighed alternatives | `docs/decisions/` · fixed | scaffold |
| [6](06-skills.md) | Skills | trigger-routed capabilities, no bloat | adaptive | skill |
| [7](07-subagents.md) | Sub-agents | isolated-context workers with a return contract | adaptive | sub-agents |
| [8](08-hooks.md) | Hooks | lifecycle/tool-event automation; the `scripts/` home | `scripts/` · fixed | hooks + scaffold |
| [9](09-commands.md) | Commands | composable, model-invocable steps | adaptive | command-skill |
| [10](10-memory.md) | Memory | hygiene, load ceiling, CLAUDE.md × Auto Memory | adaptive | proposes only |
| [11](11-catalog.md) | Catalog | generated × curated separation | `docs/catalog/` · fixed | scaffold |
| [12](12-boundary-doctrine.md) | Boundary doctrine | one home per fact; the quadrant test | transversal | proposes only |
| [13](13-conventions.md) | Conventions | naming/prefix taxonomy, frontmatter | adaptive | skill |
| [14](14-guardrails.md) | Guardrails | behavioral rules + deterministic enforcement | adaptive | skill + hook |
| [15](15-mcp.md) | MCP | versioned `.mcp.json`, secrets via `${VAR}` | `.mcp.json` · adaptive | skill |

**Fixed vs. adaptive.** A *fixed* home is canonical — the repo converges to that
name (`docs/standards/`, not `docs/arquitetura/`), with your OK. An *adaptive* home
is derived from the repo — language, prefixes and exact paths bend to fit. The full
doctrine is on the [architecture page](../architecture.md).

!!! note "Three dimensions never install"
    Vision (3), memory (10) and boundary doctrine (12) are **human content
    decisions**. The method only **proposes** the text or diff; the repo writes it.
    This is the line the method never crosses — *modulate the method, never define
    the content*.

The exhaustive per-dimension catalog (every detection grep and every smell) lives in
the skill's
[`references/dimensions-template.md`](https://github.com/holetz/claude-quenching/blob/main/plugins/claude-quenching/skills/quenching-management/references/dimensions-template.md).
The pages here tell the story and the *why*; that file is the full reference.

---

That is the *what* — the harness, part by part. To actually **run** the method
against a repo and act on these dimensions, continue to the Technical guide:
[Install & run](../../plugin/install.md) and the
[8-step workflow](../../plugin/workflow.md).
