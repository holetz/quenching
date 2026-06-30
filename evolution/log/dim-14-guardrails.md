# Dimension 14 — guardrails

> Part of the `quenching-management` evolution log. Index, anchor state, and backlog: [../README.md](../README.md). ID convention (R*/Rev*) and routing: [README.md](README.md).
>
> This file collects the rounds (`R*`) and revisions (`Rev*`) that touched **guardrails: actionable errors and poka-yoke in executables**.

## Current state

> Active summary of each boundary in this dimension (what is valid today). Detail and rationale are in the history below.

> **Cross-ref — R25 (recorded in [dim-08-hooks.md](dim-08-hooks.md)) materialises the
> *enforcement* axis of this dimension.** R11 established that the "good" of dim 14
> includes *actionable errors* in executables; R25 delivers the payload that **uses**
> that principle to **guarantee by code** the invariant "keep generated artifacts
> intact": the **PreToolUse hook**
> [`assets/hooks/protect-generated.py`](../../plugins/claude-quenching/skills/quenching-management/assets/hooks/protect-generated.py)
> **blocks** editing of a generated artifact (`permissionDecision: "deny"` with an
> actionable reason pointing to the source of truth; `protectedGlobs` derived from
> the target). This is "deterministic limits > probabilistic safeguards" applied. The
> round lives in dim-08 (hook family); only the pointer remains here.

- **R11 · Actionable errors + poka-yoke in executables (tool quality guardrail)**
  — dimension 14 (guardrails) stops being just "guardrail skill cited, not copied"
  and gains the **second target**: the quality of the **executable** artifacts that
  the surface exposes to the agent (hooks/audit scripts/skill tools), which **speak
  to the agent through the failure message**. Two verifiable axes: (1) **actionable
  error** — on failure, the executable returns *what-is-missing + how-to-fix* (e.g.,
  "Dimension 'ADR' not found: `docs/adr/` absent or empty — create the folder or
  run the skeleton"), **not** a raw stack trace / mute code / `exit 2` without
  explanatory stderr; an opaque error becomes an **expensive retry loop** (the agent
  re-calls blindly); (2) **poka-yoke** — the **parameter** design (not just the
  message) controls the error rate: hardening (absolute > relative, enum > free
  string) makes the error class **impossible** before any message (canonical example:
  relative filepath → absolute eliminated an entire class of errors). New smells:
  **opaque error** (hook/script that fails without stderr guiding correction) and
  **error-prone parameter** (accepts relative/ambiguous format where absolute/enum
  would eliminate the class). New cross-cutting item **14b** in
  `detection-and-smells.md` (greps that only list candidates: hook script without
  `sys.stderr`/`>&2`; `.py` without `try/except` that translates the traceback; use
  of relative path) + the read "simulate invalid input, does the message guide
  self-correction?". Crosses with **8b** (R7): the `exit 2` block **needs**
  actionable stderr — the exit code alone does not guide. Responsibility: `assets/hooks/`
  payloads must be born with actionable errors by construction; repo's own script
  with opaque error ⇒ the method **signals**, does not rewrite without approval.
  (round 11)

## Round and revision history

> Most recent rounds at the top. Revisions (`Rev*`) are nested under the round they refine.

### Round 11 — 2026-06-29 · boundary: Actionable errors + poka-yoke in executables (tool quality guardrail)

- **Change:** refined **dimension 14 (behavioural guardrails)** in `dimensions-template.md`
  and added a new cross-cutting item **14b** in `detection-and-smells.md`. The "What
  good looks like" was just "one guardrail skill present and **cited** (not copied)
  by CLAUDE.md" — a guardrail looking at **one** end (the LLM's behaviour in the
  repo). It now gains the **second target**, named in the purpose: the **quality of
  the executable artifacts** that this surface exposes to the agent (hooks, audit
  scripts, skill tools), which **speak to the agent through the failure message**.
  Two verifiable axes enter the "good": (1) **actionable error** — on failure, the
  executable returns *what-is-wrong + how-to-fix* (e.g., "Dimension 'ADR' not found:
  `docs/adr/` absent or empty — create the folder or run the package skeleton"),
  **not** an opaque code / raw stack trace / `exit 2` without explanatory stderr;
  a well-written error response **guides the agent** to the correct input, while an
  opaque error becomes an **expensive retry loop** (the agent re-calls without knowing
  what to change); (2) **poka-yoke** — the **parameter** design (not just the
  message) controls the error rate: *"change the arguments so that it is harder to
  make mistakes"* (absolute > relative, enum > free string) makes the error class
  **impossible** before any message (official canonical example: swapping relative
  filepath for absolute eliminated an entire class of errors). New smells: **opaque
  error** (hook/audit script that fails with raw traceback / mute code / `exit 2`
  without stderr saying how to fix) and **error-prone parameter** (accepts relative /
  ambiguous format where absolute / enum would eliminate the class). New cross-cutting
  block **14b** with greps that **only list candidates** (hook script without
  `sys.stderr`/`>&2`; `.py` without `try/except` that translates the traceback; use
  of relative path) + the read "simulate invalid input, does the message allow
  self-correction?". Conceptual diff: dimension 14 stops being just "guardrail skill
  cited vs copied" and gains a **quality test for the surface's executables** (failure
  message as the interface with the agent + poka-yoke in the parameter) — crossing
  with **8b** (R7): the `exit 2` block **needs** actionable stderr, the exit code
  alone does not guide. Stays at 15 dimensions.
- **Why:** it was the **next candidate** pointed out explicitly by R10, the last axis
  of the most anchored catalogue (`08-writing-tools-for-agents.md`, 10 confirmed
  sources) not yet attacked, reinforced by `09-building-effective-agents.md`
  (poka-yoke/ACI). Dimension 14 was the **least operational** of those not yet
  refined — it only covered the LLM-in-repo and said nothing about the **executables
  the method itself installs** (CLAUDE.md validation hooks, audit scripts), whose
  opaque failure would send the agent into a loop. The method **lives** by this: it
  carries `assets/hooks/validate-claude-md.py` and detects-via-script — if those
  payloads fail with `KeyError`/traceback instead of "directory X absent, do Y", the
  method contradicts the guardrail it purports to teach. R7 already established the
  **exit semantics** (exit 2 blocks); R11 establishes the **content** of the message
  that accompanies that exit (actionable, not mute).
- **Sources:** [Writing effective tools for AI agents — Anthropic Engineering](https://www.anthropic.com/engineering/writing-tools-for-agents)
  (accessed 2026-06-29, ✅ verified by WebFetch) — states **verbatim** *"you can
  prompt-engineer your error responses to clearly communicate specific and actionable
  improvements, rather than opaque error codes or tracebacks"* and *"Tool truncation
  and error responses can steer agents towards more token-efficient tool-use behaviors
  (using filters or pagination) or give examples of correctly formatted tool inputs"*;
  [Building effective agents — Anthropic Engineering](https://www.anthropic.com/engineering/building-effective-agents)
  (accessed 2026-06-29, ✅ verified by WebFetch) — **verbatim** *"Poka-yoke your
  tools. Change the arguments so that it is harder to make mistakes"* and the example
  *"we changed the tool to always require absolute filepaths—and we found that the
  model used this method flawlessly"*, plus the ACI principle *"plan to invest just
  as much effort in creating good agent-computer interfaces (ACI)"*. Catalogue:
  `research/08-writing-tools-for-agents.md` (line 29 "actionable error messages";
  line 239 "actionable error as guardrail: simulate each invalid parameter and verify
  self-correction without re-calling; opaque errors generate expensive retry loops")
  and `research/09-building-effective-agents.md` (poka-yoke/ACI; absolute filepath
  eliminated an error class).
- **Rejected/superseded:** discarded **creating a new dimension** "tool quality / ACI"
  — it is a refinement of existing dim 14; the axis enters as **14b** (like 1b/6b/7b/8b/9b),
  keeping 15 dimensions (Simplicity First). Discarded importing the tool result pattern
  `{success, data, error, metadata}` as a canonical contract — the ⚠️ catalogue
  verification note marks that attribution as `mischaracterised` (the Structured
  outputs docs **do not** recommend it as a standard); R9 already rejected it for the
  same reason. Discarded importing platform mechanisms (`strict: true`, `input_examples`,
  `tool_choice`) — they are API *tool use* config, not the `.claude/` surface the
  method audits (they live only in the catalogue). Discarded opening the **agent-guided
  evaluation cycle** (eval harness of the curator itself) from the same catalogue in
  this round: it is its own boundary (touches the *evolution workflow*, not the audit
  template) and would dilute the single evolution — enters as **next candidate**.
  Discarded **rewriting** the `validate-claude-md.py` payload to emit actionable errors
  right now — that is payload authoring (implementation), not template evolution; the
  template now **requires** the pattern and the 14b **detects** it, the implementation
  stays outside this single round.
- **Next candidate:** "Agent-guided evaluation cycle" (evolution workflow / dim 6 —
  catalogue `08-writing-tools-for-agents.md` line 235 + `13-skill-description-evals.md`:
  3-5 fixture harness measuring accuracy/tokens/false-negative, the curator evaluated
  as a production tool) or "Normative reference completeness / reconstruction test"
  (dim 2 — reopen with the right source, R2 deferred due to `mischaracterised`
  attribution).
