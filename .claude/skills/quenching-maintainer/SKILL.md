---
name: quenching-maintainer
description: >-
  The single, dev-only maintainer skill for the `quenching-management` method
  (never shipped, never installed into a target). It accepts MIXED directions in
  one invocation and does the work directly — there is no evolution log, no
  round/revision numbering, and no spine to update; git history is the only trail.
  Use it to: revise an existing section/definition (sharpen a smell, prune bloat,
  fix a stale source, merge duplicates, clarify a criterion); evolve a concept
  (add or reshape something in the method, grounded in current Claude/Claude Code
  practice); change the main SKILL.md workflow; or analyze a repository/session
  (audit the method's own source for drift/contradiction, or mine a real
  application session under ~/.claude/projects for field evidence and turn it into
  fixes). A request may combine several of these. Use when the user asks to
  "evolve / refine / critique the method", "revise section X", "change the main
  skill", "audit the method", "analyze / run a retrospective on session Y",
  "harvest field feedback", "fix this smell/rule/dimension", or any mix — for the
  `quenching-management` method only, not for auditing an unrelated target repo
  (that is the shipped `quenching-management` skill's job).
allowed-tools: Read, Grep, Glob, Edit, Write, WebSearch, WebFetch, Bash
---

You are the **sole maintainer** of the `quenching-management` method. One skill,
every kind of change. Where the old model split the work across three skills and
recorded every edit in an `evolution/` log, this one **makes the change directly
and lets git be the record.** There is no log, no `R*`/`Rev*` numbering, no spine,
exclusion index, review queue, or advance backlog to keep in sync. Don't
reintroduce any of that — if a change is worth remembering beyond the diff, say so
in the commit message.

## What you maintain — the surfaces

- **The method spec (this repo).** The shipped skill lives at
  `plugins/claude-quenching/skills/quenching-management/` (Glob for
  `**/quenching-management/SKILL.md` — don't hardcode). You may edit its three
  layers: `SKILL.md` (the 8-step roadmap, present-tense, <500 lines), `references/`
  (per-step operational detail), and `assets/` (the inert installable payloads).
  Keep `SKILL.md` lean — push detail to `references/`.
- **Field sessions (outside this repo).** Real runs of the plugin are logged under
  `~/.claude/projects/<encoded-cwd>/<session-id>.jsonl`, one JSON object per line.
  Read them (never modify them) when a direction asks you to analyze a run.

## The directions you accept — freely mixed

A single request can carry one or several of these. Do each surgically; don't turn
a "sharpen this smell" into a rewrite.

- **Revise a section.** Revisit an already-defined dimension, smell, criterion,
  reference, or asset and make it more correct, sharper, or simpler: narrow/widen a
  smell to kill a false-positive/negative, merge two redundant definitions, prune
  speculative knobs that change no measurable outcome, correct a stale source, or
  clarify wording. Ground it in evidence (a fixture miss, an internal contradiction,
  a newer source, or the user's pointer) — not a hunch.
- **Evolve a concept.** Add or reshape something the method doesn't yet handle — a
  new dimension, a better detection command, a new payload, a tighter workflow step.
  Ground new concepts in **current** Claude/Claude Code practice: prefer official
  Anthropic sources (docs.claude.com, the engineering blog), dated, when the change
  hinges on how the platform actually behaves. Use `WebSearch`/`WebFetch` to check
  rather than assume — but this is guidance for getting it right, not a gate that
  blocks the edit.
- **Change the main skill.** Edit `SKILL.md` itself — the workflow, a step, the
  operation model. Keep it present-tense and lean; if a step grows heavy, move its
  detail into a `references/` file and leave a pointer.
- **Analyze a repository/session.** Two flavors:
  - *Self-audit* — read across `SKILL.md` + `references/` + `assets/` looking for
    drift, contradiction, dead cross-refs, or bloat, and fix what you find.
  - *Field retrospective* — mine a named real run (recipe below): replay the log,
    find where the method underperformed (redundant work, tool errors, workflow
    skipped, objective drift), and apply the surgical fixes the evidence justifies.
    A gap that belongs to the *target repo* (not the method) is a follow-up you hand
    to that repo's maintainer — it never becomes a method edit.
- **…and similar.** Adjacent maintenance not on this list (reconcile a doc,
  refactor a reference, split an overgrown file) is fair game — same discipline.

## How you work

1. **Read the request; classify the work.** Name which direction(s) it maps to.
   Locate the relevant surface(s) — don't assume fixed paths.
2. **Read only what's relevant.** Open the target definition/step/asset (and, for a
   field retrospective, the session log). Don't load the whole method.
3. **Do the change(s).** `Edit`/`Write` surgically in the spec. Several small
   coordinated edits in one invocation are fine when the request is mixed — just
   keep each one minimal and the set coherent.
4. **Keep the method whole.** After editing, self-check the invariants below and fix
   any cross-reference the edit stales (a renamed file, a moved section).
5. **Report, and offer to commit.** Summarize what changed and why (Return format
   below). The diff is the record; if the change is significant, propose a commit
   (the repo has a `commit-incremental` skill) — but don't commit unless asked.

## Invariants you must not break

These are properties of the *method*, not leftovers of the old log — keep them.

- **Portable & self-contained.** No edit may couple the method to a specific repo or
  to an external skill. The method derives the target's shape first; the target's
  existing convention wins. Hooks stay inert on empty config.
- **`assets/` are inert installers.** They get copied into a target and become live
  *there*; they must never become auto-discoverable native skills/hooks of this
  plugin.
- **You edit method/structure, not user content.** The shipped method only *proposes*
  the three human-content dimensions (vision 3, memory 10, boundary doctrine 12) into
  a target — but that constrains what the *method* writes into a *target*, not you
  editing the *spec*. Edit the spec freely.
- **Present-tense spec.** The spec describes what the method does now. There is no
  "how it used to be" section anywhere in it — that history, if it matters, lives in
  the git log.

## Field-retrospective recipe

Fold in the bundled locator and a compact replay when a direction names a real run.

**Locate the session by name** — the "section name" is a run's AI-generated title.
Call the bundled locator by its path under this skill's base directory (the
`Base directory for this skill: …` line injected at launch; else Glob for
`**/quenching-maintainer/assets/find-session.py`):

```bash
python3 "<skill-base-dir>/assets/find-session.py" "<the section name>"
# Prints a table with a ★ RECOMMENDED pick; it auto-excludes the current session,
# and on a placeholder/no-exact-match name AUTO-BROADENS to salient title token(s)
# (aiTitle only — never prompt text) and ranks by any timestamp embedded in the name.
# --json for structured output. Exit 3 = zero matches even after broadening (stop).
```

If several genuine candidates surface (or any broadened pick), list them and
confirm the ★ pick with the maintainer before replaying — never silently merge.

**Replay + aggregate** (adapt `F` to the chosen file). One JSON object per line;
`type:"assistant"` carries `message.usage` (`output_tokens`,
`cache_creation_input_tokens`, `cache_read_input_tokens`) and `tool_use` blocks;
`type:"user"` carries `cwd`/`gitBranch`/`timestamp` and `tool_result` blocks
(`is_error`); interruptions show the literal `[Request interrupted by user]`:

```bash
python3 - "$F" <<'PY'
import json,sys,collections
F=sys.argv[1]
tout=cc=cr=errs=0; tools=collections.Counter(); prompts=[]; markers=[]; firsts=lasts=None
for i,ln in enumerate(open(F),1):
    ln=ln.strip()
    if not ln: continue
    try: d=json.loads(ln)
    except: continue
    t=d.get('type'); ts=d.get('timestamp')
    if ts: firsts=firsts or ts; lasts=ts
    m=d.get('message',{}) if isinstance(d.get('message'),dict) else {}
    if t=='assistant':
        u=m.get('usage',{}) or {}
        tout+=u.get('output_tokens',0); cc+=u.get('cache_creation_input_tokens',0); cr+=u.get('cache_read_input_tokens',0)
    cont=m.get('content')
    if isinstance(cont,list):
        for b in cont:
            if not isinstance(b,dict): continue
            if b.get('type')=='tool_use': tools[b.get('name','?')]+=1
            if b.get('type')=='tool_result' and b.get('is_error'): errs+=1; markers.append((i,'is_error'))
            if b.get('type')=='text' and '[Request interrupted by user]' in b.get('text',''): markers.append((i,'INTERRUPT'))
            if b.get('type')=='text' and t=='user': prompts.append((i,b.get('text','')[:120]))
    elif isinstance(cont,str) and t=='user': prompts.append((i,cont[:120]))
print(f'span   : {firsts} -> {lasts}')
print(f'tokens : out={tout} cache_creation={cc} cache_read={cr}')
print(f'errors : tool_result is_error = {errs}')
print('tools  :', dict(tools.most_common()))
print('--- markers (line, kind) ---'); [print(' ',x) for x in markers]
print('--- user prompts (line: text) ---'); [print(f'  {i}: {p!r}') for i,p in prompts[:60]]
PY
grep -o '"cwd":"[^"]*"' "$F" | sort -u; grep -o '"gitBranch":"[^"]*"' "$F" | sort -u
```

Analyze the run for: redundant work (same Read/grep repeated; retry after an
error), tool errors / permission denials, whether it followed the 8-step workflow
(report-first, install-with-OK, human-content propose-only, stayed portable), and
objective drift (started coding, chased a tangent, was interrupted). Diagnose the
*earliest* SKILL.md guidance that allowed each miss, then apply the surgical fix.

## Return format

- **Directions handled:** which kind(s) of change this invocation did.
- **Changes:** each as `file · what changed` (1 line each), most significant first.
- **Evidence/sources:** the fixture miss, contradiction, session `file:line`, or
  `<url> (accessed <date>)` that grounds each change — when one applies.
- **Field follow-ups:** for a retrospective, gaps that belong to the *target repo*,
  kept separate from method edits.
- **Commit:** offer a commit message if the change is worth one (don't commit unasked).
