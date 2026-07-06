# 7. Sub-agents — .claude/agents/

> **Back path:** [../dimensions-template.md](../dimensions-template.md) (dimensions index +
> transversal doctrine) · [../../SKILL.md](../../SKILL.md) (agent roadmap).

- **Purpose:** isolated work that keeps the parent's context clean — runs in its **own context window** and returns **only the condensed result**. Home of **verbose/disposable** work: the sweep/log/dependency scan happens in isolation and the parent receives the summary, not the dump.

- **How "good" looks:**

  **Healthy sub-agent form:**
  - complete frontmatter (`name`/`description`/`tools`/`model`); body = role + inputs + numbered steps + **explicit return format**.
  - `tools` **minimal and always declared** (allowlist via `tools`, or denylist via `disallowedTools`); invoked by a sibling skill.
  - read-only audit profile = Explore-like: `tools: Read, Grep, Glob`, cheap model (`haiku`), `permissionMode: plan` (built-ins Explore/Plan **skip CLAUDE.md** to reduce sweep cost — weighs on dim 1 budget). The package carries a mold for this profile: [../../assets/agents/quenching-auditor.md](../../assets/agents/quenching-auditor.md).

  **Return contract (what makes the "explicit format" *good*)** — the sub-agent runs in its own window *precisely so* the parent receives **only the high signal**:
  - (a) **condensed summary** (target ~1-2k tokens) only with high-entropy fields for the parent's next step, **never the dump** of consumed context;
  - (b) **semantic identifiers** the parent understands — `file:line`, slug, dimension name — and not opaque IDs/UUID/hash (the official doc shows that resolving cryptic IDs to interpretable language **reduces hallucination** in retrieval);
  - (c) optionally a verbosity axis (summary × detail-on-demand) for the parent to control cost.
  - **Violation detector (by proportion):** if the return is order-of-magnitude close to the **context it consumed** (returned nearly everything it read), the isolation was breached — it became a read proxy, not a condensing worker.

  **Choice criterion (sub-agent × skill × command × hook)** — aligned with dim 12 (each purpose → one home):

  | Home | When |
  | --- | --- |
  | **sub-agent** | the intermediate output would *flood* the main context with non-re-referenced results (deep search, log, dep audit), **or** the same worker is repeatedly spawned with the same instructions |
  | **skill** | the procedure must *happen in the main thread* so the operator **sees and directs each step** |
  | **command** | it's just a manual invocation shortcut |
  | **hook** | the action must be guaranteed **deterministically** (enforcement, not judgment — dim 8) |

  **When to CREATE a domain-specific sub-agent** (sub-agent side of the dim 6 criterion):
  - **Trigger:** a **recurring verbose domain side-task** — diagnosing job logs/runs, sweeping a family of artifacts, dependency audit (*«a side task floods your conversation… → route it through a subagent»*; *«you keep spawning the same kind of worker with the same instructions»*).
  - **The method proposes the skeleton** (frontmatter + minimal `tools` + condensed return contract); the repo fills in the **content** (a **portability boundary** — the package can't carry a repo-coupled procedure — not the human-direction limit of Step 6).
  - The package **does not carry** ready domain sub-agents (they break self-contained), only the generic read-only mold above.

- **Detection:** `ls .claude/agents/`; read frontmatters and bodies; verify that **every** agent declares `tools`/`disallowedTools` (item **7b** in [../detection-and-smells.md](../detection-and-smells.md)).

- **Smells:**
  - agent without defined return format.
  - **flooding return** — task instruction that tells it to return what it read ("return the file contents", "the entire log", without ceiling/summary) or whose observed return is close in size to the consumed context (does not condense — breaks isolation).
  - **opaque identifier in the return** — summary with UUID/hash/internal ID instead of `file:line`/slug/name (degrades parent precision).
  - **missing `tools`** — without the field, the sub-agent **inherits all tools** from the parent session (breaks least-privilege: a read-only audit agent gets `Edit`/`Write`/`Bash`/MCP); overly broad `tools`.
  - orphan (no skill/flow triggers it); missing `model` where it matters (cheap audit demands `haiku`).
  - **flow in the wrong home** — sub-agent for a step the operator needs to direct (should be skill), or skill that dumps verbose disposable output in the main context (should be sub-agent).

- **Remediation:** fix the **return contract** (condensed high-entropy summary + semantic identifiers `file:line`, never the dump); **declare minimal `tools`** (or `disallowedTools` for read-only); give `model`/`permissionMode` to the audit profile; connect to a skill; move the flow to the right home by the choice criterion above.

- **Payload:** skill-template [../../assets/skills/quenching-skills/](../../assets/skills/quenching-skills/) (same authoring discipline) + mold [../../assets/agents/quenching-auditor.md](../../assets/agents/quenching-auditor.md) + template [../../assets/templates/claude/agent.md](../../assets/templates/claude/agent.md). *Exception:* the **home choice** (skill, sub-agent, command, or hook?) is cross-artifact confrontation — method core (dim 12 applied to mechanisms): it **decides the home** and authoring comes from the `quenching-skills`/`quenching-config` templates.
