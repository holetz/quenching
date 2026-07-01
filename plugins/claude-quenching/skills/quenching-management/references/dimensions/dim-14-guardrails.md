# 14. Behavioral guardrails — how the LLM should code

> **Back path:** [../dimensions-template.md](../dimensions-template.md) (dimensions index +
> transversal doctrine) · [../../SKILL.md](../../SKILL.md) (agent roadmap).

- **Purpose:** how the LLM should behave when coding (think-before-coding, simplicity, surgical, goal-driven) — assisted-coding guardrails. **Two targets:** (a) the LLM's behavior *in the target repo* (the guardrails skill cited by CLAUDE.md) and (b) the **quality of the executable artifacts themselves** that this surface exposes to the agent — hooks, audit scripts, skill tools — which speak to the agent **through their failure messages**.

- **How "good" looks:**
  - a guardrails skill present and **cited** (not copied) by the root CLAUDE.md.
  - **Actionable error (the agent speaks to the tool through failure):** every hook/script/tool the agent can trigger returns, on failure, a message that says **what is wrong and how to fix it** — not an opaque code or raw stack trace. Official source: *«you can prompt-engineer your error responses to communicate specific, actionable improvements, instead of opaque error codes or tracebacks»* — a well-written response **guides the agent** to the correct input (e.g.: *"Dimension 'ADR' not found: `docs/adr/` absent or empty — create the folder or run the package skeleton"*, not `KeyError: 'ADR'`).
  - **Poka-yoke (prevent the error before it happens):** *«change the arguments so that it is harder to make a mistake»* — the **parameter** design, not just the message, controls the error rate (canonical: switching a **relative to absolute** filepath eliminated an entire class of errors). Verifiable test: *for each plausible invalid input to a hook/script, does the failure message allow the agent to self-correct without blindly retrying?* If not, the opaque error becomes an **expensive retry loop**.
  - **Deterministic enforcement > probabilistic guardrail (third thread, crosses dim 8):** where the doctrine wants to **guarantee** an invariant — above all, **keeping generated artifacts intact** (rule «X defines Y») — prose guidance in CLAUDE.md **is not enough** (the model can ignore it). The good approach is a **guardrail by code**: a **PreToolUse hook** that **blocks** editing of the generated artifact **before** it occurs (`permissionDecision: "deny"` with actionable reason pointing to the source-of-truth), `«deterministic limits are more reliable than probabilistic guardrails»`. The protected list is **derived from the target** (`protectedGlobs`), never fixed paths.

- **Detection:** look for a behavioral guardrails skill; verify the citation (not the copy) in CLAUDE.md. Inspect the **executable hooks/scripts** the package installs (and the repo's pre-existing ones) for actionable failure messages vs. raw tracebacks / `exit` without explanatory stderr (item **14b** in [../detection-and-smells.md](../detection-and-smells.md)).

- **Smells:**
  - guardrail duplicated in prose in CLAUDE.md instead of linked; guardrail absent in a repo that codes heavily.
  - **opaque error** — audit hook/script that fails with raw stack trace, numeric code, or `exit 2` without stderr saying **how to fix** (leaves the agent in a blind self-correction loop).
  - **error-prone parameter** — tool/script that accepts a relative path / ambiguous format where an absolute / fixed format would eliminate the error class (poka-yoke not applied).

- **Remediation:** replace the copy with a link; ensure the citation; install the skill if absent. For executables: **rewrite the failure message** to point to the concrete fix (what's missing + the action); **harden the parameter** (absolute > relative, enum > free string) to make the error impossible. The hooks the package carries should already be born with this pattern.

- **Payload:** skill-template [../../assets/skills/quenching-guardrails/](../../assets/skills/quenching-guardrails/) (4 generic directives; the repo cites, does not copy) + **PreToolUse enforcement hook** [../../assets/hooks/protect-generated.py](../../assets/hooks/protect-generated.py).
  - The hook is the **by-code guardrail** that **blocks** editing of generated artifacts (`protectedGlobs` derived from target; `permissionDecision: "deny"` + actionable reason pointing to the source-of-truth; wins even in `bypassPermissions`) — the invariant "keep generated artifacts intact" imposed deterministically (full mechanics in dim 8).
  - *The quality of failure messages from installed hooks/scripts is the package's responsibility* — the payloads in [../../assets/hooks/](../../assets/hooks/) must emit actionable errors by construction; where the repo has its own hook/script with an opaque error, the method **signals** (does not rewrite the repo's script without OK).
