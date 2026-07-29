---
type: standard
title: Session evidence
description: How a session transcript is read as evidence for the command that drove it — where transcripts live, the two entry forms, the JSONL-first arm ladder with the arm declared in the output, and the rule that a counted claim comes from code, never from a model recalling its own run
resource: plugins/quenching/assets/bin/session.py, plugins/quenching/commands/skill/retro.md
tags: [automation, transcript, evidence, session, retro]
timestamp: 2026-07-29
audience: both
authority: background
source: improve-command-from-session plan — the go/no-go this standard's gate restates was answered PASS at task 1.3, against a real /specs:develop session (94120e96) that conducted /specs:isolate as a stage
maintainer: quenching
---

# Session evidence

A command body is normally revised from taste alone — nobody reads back the session the command
actually drove. This standard is the contract for the one tool that does:
`plugins/quenching/assets/bin/session.py` (driven by `/skill:retro`,
`plugins/quenching/commands/skill/retro.md`) turns a session transcript into evidence about the
command that ran in it, so a finding can carry a count and a quoted turn instead of an impression.

## Where a transcript lives

One JSONL file per session, at `~/.claude/projects/<cwd-slug>/<session-id>.jsonl` — the same tree
`/docs:import-memory` already drains `memory/` from. `resolve_transcript`
(`session.py:148`) takes an explicit path, a bare session id, or resolves the newest file for the
current `cwd` by encoding it with the same `encode_cwd` charset (`session.py:122`) that convention
already uses. The file is readable while its own session is still running; only the in-flight
turn — the one the human is already looking at — is missing.

## The two entry forms

A command is reached two ways, and each leaves a different mark, both read
(`session.py:299` reads both; `Command.invocations`, `session.py:183`, keeps them distinct):

- **Typed**, a literal `/` invocation: a `<command-name>` block in a user turn
  (`COMMAND_NAME_RE`, `session.py:118`).
- **Conducted**, a stage a conductor reached by name: a `tool_use` named `Skill`, carrying no
  `<command-name>` at all.

Detecting only the typed form makes every conducted stage invisible — the exact failure this
standard exists to prevent, since a conductor's own stages are ordinary, frequent work.

## What a command's run cost — and what that claim is worth

`attributionSkill` marks the command each turn belongs to, covering both entry forms — but it is
a **pointer, not a span**: set on entry, never reliably cleared on return. Measured across all 43
Skill-invoked stages in an 86-transcript corpus, attribution reverts to the conductor after the
stage returns exactly **once**; it never returns 36 times, and jumps to a third command 6 times.
Reporting every command's counts as exact off this pointer alone over-credits a conducted stage
with its conductor's own later work — concretely, `/specs:isolate` was once credited with 5
`AskUserQuestion` calls that were `/specs:develop`'s own shape-bank questions (recorded in
`improve-command-from-session`'s `## Discoveries`, session 94120e96).

There is no end marker in the transcript that would let a tool fix this by construction —
inventing one manufactures findings instead of reporting them. `close_attribution`
(`session.py:267`) does the other thing: for every conducted invocation, it checks whether the
conductor reappears later in the attribution timeline. It does not → the stage is `closed: false`
and every count on it is an **upper bound** that may include the conductor's own turns
(`mayIncludeTurnsFrom` names it), reported as the `se-attribution-unclosed` anomaly. It does →
the stage's run is tightened to end just before the conductor resumes, which is the one claim the
transcript actually supports, and the stage is `closed: true`. This is
[parse-honesty.md](../quality/parse-honesty.md) applied to a pointer instead of a parser: name the
misread, never invent the consequence.

## The evidence ladder, and the declared arm

The transcript JSONL is the **primary** source; in-context reflection is the declared
**fallback** when a transcript cannot be reached (a sandbox, another harness). A report states
which arm produced it — never lets one silently stand in for the other. Compaction destroys
tool-call detail before it destroys anything else, so the countable half of a report — the whole
point of reading code instead of recalling a run — is unmeasurable from reflection alone; the
fallback exists so a run degrades and says so rather than refusing outright.

## The rule a counted claim must obey

**Every counted claim comes from code reading the transcript, never from a model recalling its
own session**, and is reported with its count and the quoted turn that evidences it
(`digest_command`, `session.py:507`). Two measured failures make this non-optional:

- Counting `Edit`/`Write` calls against a file as if they were `Read` calls reported 51 edits to
  one file as "redundant read x72" — confident, plausible, and entirely wrong. Reads and writes
  are counted separately (`cmd.reads` vs `cmd.touches`, `Command.__init__`, `session.py:187`).
- A human turn arriving as a `text` **block** inside a list `message.content`, rather than the
  bare content string, was silently unread — a session with several visible corrections digested
  to zero. `classify_user_turn` (`session.py:241`) is applied to both content shapes.

Anything the digest did not count is offered as an observation in plain words, never dressed
as a figure.

## Silence is a refusal, never a clean report

A non-empty transcript that yields zero commands exits **2**, distinguishing `se-empty-transcript`
(nothing to read) from `se-no-command-parsed` (read, nothing found) — `silence_refusal`
(`session.py:447`). A session that proved nothing is never reported as a session with nothing to
improve.

## The graduation gate

Born `authority: background`: the rules above are a contract this repo has stated, not yet proven
across repeated independent use. It graduates to `current` on the same criterion
`improve-command-from-session`'s own `## Validation` states — a run must surface **at least one
counted finding no participant stated during the session**, checked against a real conducted
session and not merely a rereading of the same transcript. That criterion has been met **once**
(task 1.3, session 94120e96, `## Discoveries`); graduation is a separate, later judgment for
whether `/skill:retro` keeps clearing that bar in independent use, not an automatic consequence of
this one internal test.
