---
description: Wire ONE scoped hook — the narrowest scope and the cheapest handler that still catch what it must. Use when the user asks to "create a hook", "add a validation hook", "check this after every edit", "block that command before it runs", or "catch it automatically whenever a migration lands". Walks the scope ladder, states the hook's cost claim, and applies on one OK — warn by default, block only by the human's word. Not for: a command → /skill:new; a subagent → /skill:agent:new; the /.docs/ conformance hook → /quenching:knowledge:align (it installs and upgrades okf-validate.py).
argument-hint: [what-the-hook-should-catch]
allowed-tools: Bash(python3:*), Bash(py:*), Read, Grep, Glob, Write, Edit
---

# /quenching:skill:hook:new — wire ONE scoped hook

**Input**: `$ARGUMENTS` (what the hook should catch — a behavior, a rule, an observed
failure).

Installs or edits **ONE hook** in the target repo: a wiring (which decides its scope) plus,
for a `command` handler, a script under `.claude/hooks/`. The scope ladder, the handler
ladder, and the policy defaults live in
[skill-new/capabilities.md](${CLAUDE_PLUGIN_ROOT}/assets/references/skill-new/capabilities.md)
§Hooks — applied here, never restated. The mold is
`${CLAUDE_PLUGIN_ROOT}/assets/templates/automation/hook.md`.

## Doctrine

- **A hook charges other people's operations.** It fires on events this mint does not own,
  so every widening of scope is a tax on every iteration in the repo — the plan prices it.
- **The rule governs; the plan proposes.** In a target repo the rule is
  `/.docs/standards/automation/hooks.md`; absent + OKF bundle present → the plan offers
  creating it from `automation/hooks-standard.md`, born `authority: background`. No bundle →
  write the hook only, suggest `/quenching:docs:align` once.
- **One plan, one OK, nothing before.** The check, the rung, the handler, the cost claim,
  the action, and every file appear in ONE plan; a declined plan writes nothing.
- **MERGE, never clobber.** A `settings.json` block is merged into the existing file; a
  frontmatter `hooks:` block is merged into the owning command's frontmatter. Existing hooks
  are never rewritten and never deleted by this skill.
- **Warn by default; block by consent.** `action: block` (a `PreToolUse` deny, a `Stop`
  block) is chosen by the human in the plan, per rule — and an intrusive rule is born
  disabled, its body saying when to enable it.

## Workflow

### 1. Read the rule
Read `/.docs/standards/automation/hooks.md` and confirm the bundle (`/.docs/index.md` carries
`okf_version`). Rule present → it governs (a repo delta there beats the plugin default).
Absent + bundle → plan its creation from the mold. No bundle → note the tail as skipped and
plan the `/quenching:docs:align` suggestion. **Done when:** the governing rule (or its planned
creation, or the no-bundle note) is fixed.

### 2. Name what the hook catches
State the check as **event + condition + consequence**: *"on every `Write|Edit` under
`db/migrations/`, refuse a file with no rollback section"*. A hook whose condition cannot be
stated this way is not a hook yet — it is a doctrine question for the human. **Done when:**
the one-sentence check is fixed.

### 3. Choose the rung and the handler
Walk [capabilities.md](${CLAUDE_PLUGIN_ROOT}/assets/references/skill-new/capabilities.md)
§Hooks top-down. Scope: a check tied to ONE command's workflow → its frontmatter `hooks:`; an
operation → event + `matcher` (+ `if`); a wide event → dirty-gated or `once: true`; unmatched
session-wide only with the stated reason nothing narrower suffices. Handler: `command` first
— climb to `prompt`, then `agent`, only when the rung below cannot express the check. Then
write the **cost claim**: event × how often it fires in this repo × handler cost per firing ×
fast-path cost on no-match. **Done when:** rung, matcher, handler, and the cost-claim line
are fixed.

### 4. Draft from the mold
Fill the chosen shape from `automation/hook.md`: the wiring block, and for a `command`
handler the script — fail **open** on infrastructure (a crash never blocks), fail **closed**
on scope (an unclassifiable event matches nothing), `{}` on the fast path, a `timeout` sized
to the event's frequency, `stop_hook_active` honored on `Stop`. **Done when:** the draft
matches the mold's skeleton and the chosen action.

### 5. Present ONE plan → gate on the OK
Show: the check, the rung **and why not narrower**, the handler **and why not cheaper**, the
cost claim, the action (warn / block / born-disabled) as the human's explicit choice, and
every file — the `settings.json` MERGE shown as a diff, or the frontmatter block with its
owning command, the script, the rule if planned. Wait for the single confirmation. **Done
when:** the user has answered; declined → report "nothing written" and stop.

### 6. Apply
Merge the wiring, write the script. Never overwrite `settings.json` — read it, add this
hook's block, preserve everything else including hooks the plugin does not own. **Done
when:** every planned file is applied and the diff touches only the planned block.

### 7. Verify the wiring
```bash
python3 -m json.tool .claude/settings.json          # the merge left valid JSON
echo '{"hook_event_name":"<other>"}' | python3 .claude/hooks/<name>.py   # fast path → {}
```
Then feed one **matching** synthetic payload and confirm the finding fires with the chosen
action. A frontmatter wiring is checked with `skills.py lint <owning-command> --json`
instead. **Done when:** the fast path prints `{}`, the matching payload fires, and the wiring
parses.

### 8. OKF tail and report
Bundle present: write the rule if planned, per
[docs-add/homes.md](${CLAUDE_PLUGIN_ROOT}/assets/references/docs-add/homes.md). Report: the
check, the installed scope, the cost claim **as installed**, and — for a born-disabled rule —
the exact line that enables it. **Done when:** the report states the cost claim.

## Invariants

- Never write before the single OK; a declined plan leaves the repo untouched.
- Never overwrite `settings.json` or an existing hook — MERGE; never delete a hook without
  the human stating it is obsolete.
- Never default to `block` — the action is the human's explicit choice, and an intrusive
  rule ships disabled.
- Never wire a `prompt`/`agent` handler onto a tool event without its stated reason
  (`sk-hook-llm-frequent`).
- Never install an unmatched tool-event hook without its stated reason (`sk-hook-unmatched`).
- Never hand this command file `context: fork` — the plan gate is mid-flow.
