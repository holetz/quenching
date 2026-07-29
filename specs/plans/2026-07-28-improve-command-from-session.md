---
slug: improve-command-from-session
title: Mine a session for improvements to the command that started it
verification: per-section
priority: {level: 26, criticality: low, date: 2026-07-28}
branch: {base: main, work: plan/improve-command-from-session}
refined: {mode: gate, date: 2026-07-28}
approved: {date: 2026-07-28}
---

# Mine a session for improvements to the command that started it

<!-- ONE spec is ONE file for its whole lifecycle. Phases enrich it; they never split it.

     `specs.py new` stamps the frontmatter and `## Problem` ALONE — a captured spec is four
     lines of body, not a thirteen-heading skeleton. Every other heading below is created on
     first write by `specs.py section <slug> "<Heading>" --write`, which inserts it in the
     canonical position with the guidance comment kept here.

     THE STAGE-SCOPED EXPLICIT-NONE RULE. A heading is required — and required to carry
     `- none — <reason>` when it has nothing in it — only once ITS OWN gate is reached:

       new (capture)        `## Problem`
       ready (derived)      the nine definition sections (`## Problem` .. `## Risks`)
                            AND `## Tasks`
       ready (warn only)    `## Handoff` non-empty
       promote -> archive/  `## Outcome`

     `ready` is a DERIVED STAGE, not a folder: a spec lives in `plans/` for its whole active
     life, and filling those ten sections is what makes it ready. Nothing refuses on that
     gate — it is a floor `execute` reports against, and the human's go-ahead is the
     `approved:` frontmatter record, asked for inline.

     Before its gate, a heading's absence is NOT an omission — it is a not-yet. After its
     gate, three rules decide whether a section counts as filled:

       1. `- none — <reason>` counts as filled. An omission and a null are different facts.
       2. A heading present with an EMPTY body is malformed and refuses. It is neither an
          answer nor a not-yet.
       3. An absent heading before its gate is legal.

     Headings are a PARSED contract — canonical English, exactly as written here. Body prose
     follows the repo's language. A heading outside this set is a stray and validate flags it.

     AUDIENCE. Each section names who reads it. `## Problem`/`## Proposal`/`## Design` are for
     the human — examples and plain language belong there. `## Handoff`/`## Tasks` are for
     agents — terse, with `files:`/`verify:`/`pattern:` metadata. An orchestrator never sends
     the human sections to an executor; that is what lets one file serve both audiences
     without bloating agent context. -->

## Problem

A command's body is only ever revised from taste — nobody reads back the session the command
actually drove. The evidence of what a command costs, repeats, gets wrong or leaves unresolved is
right there in the transcript that ran it, and it is thrown away when the session ends.

Wanted: a command that analyses the current session against the command that started it, and
reports the improvements the run itself evidences — performance (tool calls, redundant reads),
redundancy (steps that repeat what a prior step already established), bugs (a step that misfired
or was worked around), and unresolved problems (what the human had to correct by hand).

## Proposal

- A command on the `.claude/` front reports the improvements a **single session** evidences for
  **one command** that ran in it.
- The report's findings split four ways: **performance** (counted tool calls, redundant reads),
  **redundancy** (a step that re-establishes what an earlier step already established), **bugs** (a
  step that misfired or was worked around), and **unresolved problems** (what the human had to
  correct by hand).
- Every **counted** claim comes from code reading the transcript, never from a model recalling its
  own session.
- Evidence comes from the session transcript JSONL when reachable, and from in-context reflection
  when it is not — and the report states which arm produced it.
- Both entry forms are detected: a typed `/` invocation (a `<command-name>` block) and a Skill-tool
  invocation, so a command reached as a conductor's stage is never invisible.
- A session holding more than one command lists them with their tool-call span and targets **one**,
  defaulting to the session opener.
- A session where no command is found is a refusal carrying the reason, not an empty report.
- Every finding is reported with the `/skill:new` invocation that closes it; nothing is applied.

## Out of Scope

- **Cross-session aggregation** — trends over N runs of the same command. Ruled out: it needs a
  durable store and a corpus scan over multi-megabyte transcripts, while one session with quoted
  evidence is already actionable. Deferred rather than rejected — worth its own spec.
- **Agents and hooks** — this covers commands only. Ruled out: a hook's evidence in a transcript is
  a fired/not-fired line rather than a workflow, which is a different instrument even though
  `skills.py` covers all three artifact kinds.
- **Rewriting the command body** — findings are reported with the `/skill:new` invocation that
  closes each, never applied. Ruled out by the front's existing doctrine (`/skill:eval` never
  rewrites a body either); stated here so it stops being re-proposed.

## Impact

### Standards this spec will write into docs/standards/

- `docs/standards/automation/session-evidence.md` — how a session transcript is read as evidence:
  where transcripts live, the two entry forms, the JSONL-first ladder with the arm declared in the
  output, and the rule that a counted claim comes from code rather than from a model recalling its
  own session. Born `authority: background`, graduating on the `## Validation` gate.

### Product code this spec expects to touch

- `plugins/quenching/assets/bin/session.py` — new, plugin-side only, never installed into a target
- `plugins/quenching/commands/**` — the new command file
- `plugins/quenching/assets/claude/QUENCHING.md` — each manual enumerates its own front's surface

### Contracts this must not contradict

- `docs/standards/architecture/read-only-views.md` — a read-only view is its own command, and its
  grant carries no `Write` and no `Edit`
- `docs/standards/automation/context-budget.md` — a command's `description` is resident in every
  session before anything fires
- `docs/standards/automation/skill-evaluation.md` — a one-arm retro never claims a measured delta

## Validation

The go/no-go, stated as a kill criterion so the spec has an honest way to be abandoned:

- The retro must surface **at least one finding backed by a count that no participant stated during
  the run**. A report whose findings a careful human re-reading the same transcript would have
  listed anyway is an expensive way to reread a transcript.
- First test: run it against a real `/specs:develop` session that conducted a stage (a session with
  both entry forms present), and check the finding against what was actually said in it.
- Failing that criterion, the spec is abandoned via `/specs:conclude` with the reason recorded — not
  left to go stale.

## Design

**The evidence ladder.** The transcript JSONL is the primary source; in-context reflection is the
declared fallback, and the report always says which one produced it. Compaction destroys tool-call
detail before it destroys anything else, so the countable half of the report is unmeasurable from
context alone — but a command that refuses in a sandbox or under another harness is worse than one
that degrades and says so.

**What the transcript actually holds** (verified against a live session, not assumed):

- JSONL, one file per session, at `~/.claude/projects/<cwd-slug>/<session-id>.jsonl` — the same
  tree `/docs:import-memory` already drains `memory/` from.
- A typed `/` invocation carries a `<command-name>` block in a user turn.
- A command invoked as a conductor's stage appears as a `tool_use` named `Skill`, and carries **no**
  `<command-name>`. Detecting only the first form makes every conducted stage invisible.
- Tool calls are exactly countable by name from `tool_use` blocks.
- The current session's file is readable **while that session runs**; only the in-flight turn is
  missing.
- Files reach ~2.4 MB in this repo, so a filter pass runs before anything enters context.

**Target selection.** Every command found is listed with its tool-call span; the session opener is
the default; `AskUserQuestion` decides when more than one is present. One command per run keeps the
output actionable by a single `/skill:new` — the same scoping `/skill:eval` uses.

**The extractor is plugin-side only, and is never installed into a target repo.** The three existing
tools are self-contained because targets install them into `.claude/hooks/` — that install is what
makes `CANONICAL_CASES` triplicated, `VERSION` kept in lockstep, and an align responsible for
upgrading each copy. A transcript reader's input is `~/.claude/projects/`, which belongs to the
operator's machine rather than to the repo being aligned, so nothing installs it and none of that
cost applies. This also leaves `skills.py`'s stated contract intact: it reads `commands/**` and
nothing else, which a transcript reader would have broken.

**Contracts this must not contradict.** `/skill:eval` owns measured with/without deltas; a retro has
one arm and never claims one. Authoring stays `/skill:new`'s.
## Alternatives Considered

- **A mode of `/skill:eval`** — rejected. Eval's first invariant is *both arms, always*; a session
  retro has one arm and no control, so it would need an exemption from the rule that gives eval its
  meaning. It would also reintroduce the mode flag this plugin deliberately removed from
  `/specs:develop`, where the lesson was that a second command beats a flag on a command whose
  doctrine does not fit.
- **A case generator feeding `/skill:eval`** — rejected as *this* spec's shape, kept as a follow-up.
  Mining a session for eval cases turns anecdote into a measured delta, which is genuinely valuable,
  but it does not deliver the report the problem asks for. The two compose: a retro finding can
  later become an eval case.
- **In-context reflection only** — rejected as the sole source. It costs nothing and works anywhere,
  but the exact things the problem asks to count — tool calls, redundant reads — are the first
  thing summarization destroys. Kept as the fallback arm rather than dropped.
- **First-invoked-wins**, and **a findings block per command in the session** — both rejected in
  favour of targeting one chosen command. The first drops every conducted stage; the second splits
  the analysis budget and turns an `/align` retro into a wall of thin reports.

## Open Decisions

- **Whether the retro handles transcript redaction.** It was deliberately NOT ruled out of scope,
  and it is not designed either. Transcripts hold whatever was pasted into them. Decided by
  evidence: the retro reads locally and writes locally, so the question becomes real only if a run
  surfaces content that must not leave the machine — settle on the first such run rather than up
  front.
## Risks

- **Transcript format drift** — the JSONL shape is Claude Code's internal format, undocumented and
  unversioned. It changes, the extractor reads nothing, and "no findings" looks like success.
  *Mitigation:* a fixture-backed `selftest` in the mold of the three existing tools, plus a refusal
  (exit 2) on a zero-command parse of a non-empty transcript, so silence can never masquerade as a
  clean run.
- **Context blowup on a large transcript** — files already reach ~2.4 MB in this repo, and an
  unfiltered read overflows immediately. *Mitigation:* the code-side filter pass is a hard
  precondition, never an optimisation — a model reads the digest, never the file.
- **Plausible-but-wrong findings** — the model narrates a redundant read that never happened, which
  is exactly the failure `/skill:eval` guards against. *Mitigation:* the same rule — every counted
  claim carries its count and its quoted turn, or it is dropped.
- **The command's always-on cost** — per `docs/standards/automation/context-budget.md` a command's
  `description` is resident in every session before anything fires, while a retro runs rarely.
  *Mitigation:* price it against that standard before minting and record the figure; if the cost is
  not payable, the spec fails its own go/no-go rather than shipping anyway.
- **The in-flight turn is not flushed to the transcript** — a retro can never see the action it is
  currently taking. `ACCEPTED — the blind spot is one turn wide, and it is the one turn the human is
  already looking at.`

## Handoff

State of the tree after task 5.1. Sections 1–4 complete; 5.1 confirmed the surface still conforms
(`skills.py doctor` — 26 commands, 0 findings) with no code change of its own. Only 5.2 remains:
`functional-checks.sh` must exit 0 since `commands/**` changed this session (the mint at 3.2). It
was already run clean (9/9) after the mint in task 3.2's own verification, and again as a fresh
full run during this session's diagnosis of a since-not-reproduced flake — 5.2 reruns it one more
time as the task's own declared check and records the result.

Everything else — `session.py`, `retro.md`, the manuals, `session-evidence.md` — is unchanged
since task 4.1; see that Handoff entry (in git history) for their state.

Corpus: 87 transcripts under `~/.claude/projects/-home-holetz-Projects-claude-quenching/`. 81 exit
0, 6 refuse with `se-no-command-parsed`, none crash. Largest is 7.1 MB and digests to 4.6 KB
against a stated 64 KB budget.

Next: 5.2, the last task. At 100% the run offers to chain into `/specs:conclude`.
## Tasks

### 1. Gate — prove the retro finds anything

- [x] 1.1 Write `assets/bin/session.py`: list every command a session ran, by both entry forms, with its tool-call span, under `--json`
      verify: `python3 plugins/quenching/assets/bin/session.py list --json <transcript>` returns at least one command with non-zero tool counts on a real session file
      files: plugins/quenching/assets/bin/session.py
      subject: plan/improve-command-from-session: 1.1 Write assets/bin/session.py: list every command a session ran, by both entry forms, with its tool-call span, under --json
- [x] 1.2 Add the digest pass: per-command tool-call counts by name, repeated read targets, and the turns where the human corrected course
      verify: the digest of the largest file in `~/.claude/projects/` stays under a stated size and the transcript itself is never emitted
      files: plugins/quenching/assets/bin/session.py
      subject: plan/improve-command-from-session: 1.2 Add the digest pass: per-command tool-call counts by name, repeated read targets, and the turns where the human corrected course
- [x] 1.3 Answer the go/no-go in writing against a real `/specs:develop` session that conducted a stage
      verify: at least one counted finding no participant stated is recorded in `## Discoveries` with its count and its quoted turn; none means stop and abandon per `## Validation`
      subject: plan/improve-command-from-session: 1.3 Answer the go/no-go in writing against a real /specs:develop session that conducted a stage

### 2. The tool, hardened

- [x] 2.1 Add a fixture-backed `selftest` subcommand proving the transcript-parsing rule
      verify: `python3 plugins/quenching/assets/bin/session.py selftest` exits 0
      files: plugins/quenching/assets/bin/session.py
      subject: plan/improve-command-from-session: 2.1 Add a fixture-backed selftest subcommand proving the transcript-parsing rule
- [x] 2.2 Refuse with exit 2 on a zero-command parse of a non-empty transcript, so silence cannot look clean
      verify: a non-empty fixture holding no command yields exit 2 and a stated reason
      files: plugins/quenching/assets/bin/session.py
      subject: plan/improve-command-from-session: 2.2 Refuse with exit 2 on a zero-command parse of a non-empty transcript, so silence cannot look clean
- [x] 2.3 Bring it onto the uniform tool contract — `--json` on every subcommand, exit codes 0/1/2
      verify: every subcommand accepts `--json` and the three exit codes match the contract
      files: plugins/quenching/assets/bin/session.py
      subject: plan/improve-command-from-session: 2.3 Bring it onto the uniform tool contract — --json on every subcommand, exit codes 0/1/2

### 3. The command

- [x] 3.1 Price the command's always-on `description` against `docs/standards/automation/context-budget.md` and record the figure
      verify: `python3 plugins/quenching/assets/bin/skills.py --root plugins/quenching budget` run before and after, with the delta stated
      subject: plan/improve-command-from-session: 3.1 Price the command's always-on description against context-budget.md and record the figure
- [x] 3.2 Mint the command via `/skill:new` — a read-only grant with no `Write` and no `Edit`, target selection via `AskUserQuestion`
      verify: `python3 plugins/quenching/assets/bin/skills.py --root plugins/quenching lint` clean on the new file
      subject: plan/improve-command-from-session: 3.2 Mint the command via /skill:new
- [x] 3.3 Add the command to `assets/claude/QUENCHING.md` and update the surface counts in `CLAUDE.md` and `README.md`
      verify: the stated counts agree with `skills.py --root plugins/quenching doctor --json`
      subject: plan/improve-command-from-session: 3.3 Add the command to assets/claude/QUENCHING.md and update surface counts

### 4. The standard

- [x] 4.1 Write `docs/standards/automation/session-evidence.md` at `authority: background` with its graduation gate stated
      verify: `python3 plugins/quenching/assets/hooks/okf-validate.py docs` reports 0 errors
      files: docs/standards/automation/session-evidence.md
      subject: plan/improve-command-from-session: 4.1 Write docs/standards/automation/session-evidence.md at authority: background

### 5. Surface checks

- [x] 5.1 The command surface still conforms at 26 commands
      verify: `python3 plugins/quenching/assets/bin/skills.py --root plugins/quenching doctor --json` shows 26 commands and no findings
      subject: plan/improve-command-from-session: 5.1 The command surface still conforms at 26 commands
- [ ] 5.2 The surface actually loads, since `commands/**` changed
      verify: `./assets/bin/functional-checks.sh` exits 0

## Discoveries

- Transcripts carry a per-line attributionSkill/attributionPlugin field naming the command each turn belongs to — it covers BOTH entry forms at once and yields the per-command tool-call span directly, which the <command-name>+Skill parse in ## Design only approximates. The entry marks are still read, but for how a command was reached and with what args, not for what it cost.
- A Skill tool_use is attributed to the CALLER while the stage own turns are attributed to the CALLEE, so a conductor and its stages separate without inferring nesting.
- session.py sits OUTSIDE the six-artifact lockstep in docs/standards/ci-cd/versioning-release.md: that lockstep exists so an align can decide whether an installed copy is stale, and this tool is never installed into a target. The standard does not yet say what a plugin-side-only tool does about --version.
- A human turn reaches the transcript as text BLOCKS in a list, not only as a bare content string — reading only the string form finds zero interjections and zero interrupts on a session that visibly had both. The string slot in the largest transcript holds nothing but compaction notices.
- isMeta: true marks a turn the HARNESS wrote into the user slot, chiefly the expanded body of the command just invoked. Without excluding it, every command scores a human correction at its own first turn.
- An interrupt ENDS the span it belongs to, so the strongest evidence a command misfired always falls just OUTSIDE its attributed span. Corrections are therefore attached as during|after, and a report that cannot tell those apart is guessing.
- LIMITATION: Command is keyed by name, so two invocations of the same command in one session merge into ONE span (seen with /compact twice). A command run twice over-claims its span and can absorb a correction from the gap between runs. Per-invocation spans are a deliberate design change, not a patch — take it to /specs:develop before the report is trusted on repeat runs.
- Counting Edit/Write against a file as a "read" reported 51 edits as "redundant read x72" — a confident, plausible, entirely wrong finding. Reads and writes are now counted separately; the honest redundant-read number for that same run is 0.
- GO/NO-GO ANSWERED — PASS (task 1.3, against session 94120e96, a /specs:develop run that conducted /specs:isolate as a stage). THE COUNTED FINDING NO PARTICIPANT STATED: the digest credits /specs:isolate with 18 tool calls against its conductor /specs:develop 7, and with ALL 5 of the session AskUserQuestion calls — which are the shape-bank questions [Evidence] [Shape] [Target] [Boundary] [Go/no-go] at lines 67-89, unmistakably /specs:develop own. QUOTED TURN, line 127 (assistant): "**Bank** — shape. 5 questions asked, 5 answered." The participant counted the questions and believed they were develop; nobody stated a tool-call count anywhere in the session (a scan for count-language found only "5 questions"/"10 asked, 10 answered"), and nobody noticed the transcript credits them to the stage. Also uncounted by anyone: 28 of the session 53 tool calls (53%) carry no command attribution at all.
- CORRECTS the earlier discovery that "attributionSkill yields the per-command tool-call span directly" — it does NOT. Measured across all 43 Skill stages in the 86-transcript corpus: attribution reverts to the conductor after the stage returns exactly 1 time; 36 times it never returns to any command, and 6 times it jumps to a different one. attributionSkill marks where a command STARTS driving and has no reliable end, so a span derived from it alone over-credits the last stage invoked. The span must be closed by the Skill call boundary, not by the next attribution change — a design correction for /specs:develop before task 3.2 mints the command.
- A selftest that passes on first write proves nothing. This one was mutation-checked: breaking the isMeta rule, the text-block rule, the reads-vs-writes split and the uuid dedup each made it fail (1-2 assertions apiece). The same cheap mutation pass would be worth running against the three shipped tools selftests, which have never been shown to fail.
- TASK 3.1 — THE PRICE, measured not estimated (skills.py budget, parsed values). BEFORE: 25 commands, 12726 chars always on (~3182 tokens), ceiling 12726. DRAFT DESCRIPTION: 830 chars — inside both per-command caps, 706 under the 1536 sk-metadata-cap error and 194 under the 1024 sk-description-portable warning. AFTER (measured on a scratch copy of the surface, nothing minted): 26 commands, 13556 chars (~3389 tokens). DELTA +830 chars, ~+207 tokens, +6.5% on every session before anything fires.
- The +830 crosses the zero-headroom ceiling and sk-budget-ceiling fires — by design, per docs/standards/automation/context-budget.md, which predicts the next command minted crosses it and treats that as the signal working (budget reports, never refuses). BUT the re-set is a three-file bookkeeping change — DEFAULT_CEILING in skills.py, the figure transcribed in context-budget.md, and README.md — and NO TASK IN THIS SPEC DECLARES IT. ## Impact lists neither skills.py nor context-budget.md. The standard names this exact cost ("a ratchet with no headroom converts every new command into a three-file bookkeeping change"), so the gap is in this spec, not in the standard. Needs a task before 3.2, via /specs:develop.
- functional-checks.sh assertion 1 (the /quenching:specs:status reference-citation probe) showed one stray FAIL against this worktree that did not reproduce on an immediate rerun or a fresh full run (9/9 passed) — likely --max-turns 10 being too tight for a claude -p subprocess that sometimes explores sibling worktrees first; probe flakiness, not a regression from session.py or retro.md, neither of which touch /specs:status's body or its cited references
