---
description: >-
  Mine ONE session for what it evidences about ONE command that ran in it — performance,
  redundancy, bugs, and the problems the human had to fix by hand. Reach for it when you want
  to ask "what did this command cost", "retro this session", "what went wrong in this run",
  "improve the command that started this session", or "what should this command do
  differently". Counts come from code reading the session transcript, never from a model
  recalling its own run, and every counted claim is reported with its count and the turn that
  evidences it. Each finding lands with the `/quenching:components:command:new` invocation that would close it, and
  nothing is applied. Typed-only by design: a retro reads your transcripts, so a human chooses
  it. Not for: measuring a command against a control arm → /quenching:components:command:eval; minting or editing a
  command → /quenching:components:command:new; auditing every body on the surface → /quenching:components:align.
argument-hint: "[session id or transcript path — omit for this session; optionally a command name]"
allowed-tools: Read, AskUserQuestion, Bash(python3:*), Bash(py:*)
disable-model-invocation: true
---

# /quenching:skill:retro — what one session proves about the command that drove it

**Input**: `$ARGUMENTS` — optionally a session id or transcript path, and optionally the
command to analyse. Omitted → this session, and the command that opened it.

A command body is otherwise only ever revised from taste. The session that ran it holds the
evidence of what it cost, what it repeated, where it misfired and what the human had to fix —
and that evidence is discarded when the session ends. This command reads it back.

**Counting is the extractor's job, never yours.** `${CLAUDE_PLUGIN_ROOT}/assets/bin/session.py`
reads the transcript JSONL and returns a bounded digest; you read the digest and judge it. It
resolves the transcript itself (explicit path, bare session id, or the newest session for this
cwd), so this body never globs `~/.claude/projects/**`. Invoke it by its literal resolved path
with `python3`/`py`, and branch on the **exit code** — 0 read clean · 1 read with an anomaly
against it · 2 refusal — never on prose.

**This command reports. It never edits a command body**, and it never claims a measured delta:
a retro has one arm and no control, which is what separates it from `/quenching:components:command:eval`.

## Workflow

### 1. List what ran
Split `$ARGUMENTS` first: at most one token names a transcript (a session id or a path), and
any remainder names the command to analyse. Pass **only** the transcript token below, and
carry the rest to step 2; nothing given → pass nothing and let the tool resolve this session.

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/assets/bin/session.py list --json <transcript-or-nothing>
```
Exit 2 is a refusal carrying its reason — an absent transcript, an empty one, or a non-empty
one that yielded no command. Show the reason and stop; a session that proved nothing is never
reported as a session with nothing to improve.
**Done when:** the transcript is resolved and its commands are in hand, or the refusal is shown.

### 2. Choose ONE command
One command per run keeps the output actionable by a single `/quenching:components:command:new`. A command named in
`$ARGUMENTS` → take it. Otherwise one command found → take it; several → **AskUserQuestion**,
one option per command showing its `attributedRun` line range and its `toolCalls`, defaulting
to the session opener.
**Done when:** exactly one command is chosen and named back to the user.

### 3. Get its evidence
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/assets/bin/session.py digest --command "<chosen>" --json <transcript-or-nothing>
```
An unknown `--command` refuses with exit 2 and lists what the session did hold — reach step 2's
question rather than repeating the call.
Read `counts`, `tools`, `repeatedReads`, `repeatedShell`, `corrections` and `anomalies`. The
digest is bounded by construction — quotes are clipped and lists capped, and a `truncated`
block says what was dropped. Report what it says was dropped rather than implying full coverage.
**Done when:** the digest for the chosen command is in hand.

### 4. Establish what the counts are worth
`attributedRun.closed` decides how every number in this report may be spoken.

- `closed: true` → the counts are exact. State them plainly.
- `closed: false` → the command was invoked as a stage and its conductor never regained
  attribution, so its counts are an **upper bound that includes the conductor's own turns**.
  `mayIncludeTurnsFrom` names the conductor. Say so beside every number, and quote the
  `se-attribution-unclosed` anomaly rather than burying it.

Attribution returns to the conductor in roughly one stage in forty, so `closed: false` is the
common case for any conducted command. "The isolation stage asked the human five questions"
when the conductor asked them is the precise false-but-plausible finding this step exists to
prevent.
**Done when:** each count is marked exact or upper-bound, and any anomaly is quoted.

### 5. Report the findings, in four classes
Under each heading, list what the digest evidences — and omit the heading when it evidences
nothing there, rather than padding it.

- **Performance** — `toolCalls`, the `tools` breakdown, and `repeatedReads` entries whose
  `redundant` is `true`. A `redundant: false` entry is paging through one file, which is the
  tool working; reporting it as waste is a fabricated finding.
- **Redundancy** — `repeatedShell`, and steps whose evidence shows a later turn re-establishing
  what an earlier turn already had.
- **Bugs** — `corrections` of kind `interrupt`, and turns where the run visibly worked around
  its own step. `when: "after"` means the turn landed past the attributed run, which is where
  an interrupt always lands, so treat it as evidence about this command and say that it did.
- **Unresolved problems** — `corrections` of kind `interjection`: what the human had to supply
  by hand. Kind `compaction` is the harness talking and is never a correction.

Every **counted** claim carries its number and the quoted turn behind it. Anything the digest
did not count is offered as an observation in plain words, never dressed as a figure.
**Done when:** each finding carries either a count with its quoted turn, or no number at all.

### 6. Hand each finding to the command that closes it
End every finding with the `/quenching:components:command:new` invocation that would fix the body, phrased so it can
be run as-is. Where a finding is about the target repo's contracts rather than the command's
wording, name `/quenching:docs:add` instead.
**Done when:** each finding names the one command that closes it.

### 7. Self-check
Confirm the report matches what ran: the transcript and command analysed are named, the
evidence arm is stated (`session.py` on the transcript, or in-context reflection when the
transcript was unreachable), every count is marked exact or upper-bound, and no command body
was edited. State the `session.py` exit code.
**Done when:** the report names its source, its arm, and its exit code, and the surface is
unchanged.

## Invariants

- Analyse ONE command per run, chosen by the human when the session held several.
- Take every count from `session.py`. Never count tool calls by recalling the session, and
  never state a number the digest did not produce.
- Speak an unclosed command's counts as an upper bound, always naming the conductor whose
  turns they may include.
- Report a refusal with its reason. An empty run is never presented as a clean one.
- Report findings; apply none. Editing a command body is `/quenching:components:command:new`'s, and a measured
  with/without delta is `/quenching:components:command:eval`'s.
