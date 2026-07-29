#!/usr/bin/env python3
"""session.py — read a Claude Code session transcript as evidence.

Payload of the `quenching` plugin, but NOT a fourth sibling of `assets/bin/specs.py`,
`assets/bin/skills.py` and `assets/hooks/okf-validate.py`: those three are **installed
into a target repository** by their own align, and this one never is.

WHY IT IS NOT INSTALLED
-----------------------
The three shipped tools read the repo being aligned, so each target needs its own copy
and each align upgrades that copy by comparing `--version`. This tool's input is
`~/.claude/projects/**` — the *operator's machine*, not the repo. There is nothing for a
target repo to hold, so nothing installs it.

Two consequences follow, and both are deliberate:

  * It is **outside the six-artifact lockstep** of `docs/standards/ci-cd/versioning-release.md`.
    That lockstep exists because an align must decide whether an installed copy is stale;
    with no installed copy there is no such decision. `VERSION` below tracks the plugin for
    a legible `--version`, and no align compares it against anything.
  * `skills.py`'s stated contract — it reads `commands/**` and nothing else — stays intact.
    Folding a transcript reader into it would have broken that sentence.

WHAT A TRANSCRIPT HOLDS
-----------------------
One JSONL file per session at `~/.claude/projects/<encoded-cwd>/<session-id>.jsonl`, one
JSON object per line. The fields this tool reads, all verified against live sessions in
this repo rather than assumed:

  type              "user" | "assistant" | "attachment" | "system" | ...
  uuid              stable per record; the dedup key
  timestamp         ISO-8601
  sessionId, cwd, gitBranch, version
  attributionSkill  THE command a turn belongs to, e.g. "quenching:specs:develop"
  attributionPlugin the plugin that owns it, e.g. "quenching"
  message.content   str, or a list of blocks: text | thinking | tool_use | tool_result

THE TWO ENTRY FORMS, AND WHY ATTRIBUTION BEATS BOTH
---------------------------------------------------
A command is reached two ways, and each leaves a *different* mark:

  typed   a user turn whose content string carries a `<command-name>` block
  skill   an assistant `tool_use` block named `Skill`, whose input names the command

Detecting only the first makes every conducted stage invisible. But neither mark tells you
what the command then *did* — they are both single points, and the work is a span.

`attributionSkill` covers both: every turn a command drives carries the command's name,
including turns inside a stage a conductor invoked. The invoking `Skill` call is attributed
to the **caller** and the stage's own turns to the **callee**, so a command is found even
when its entry mark fell outside a compacted window.

WHAT ATTRIBUTION IS NOT: A SPAN
-------------------------------
It is a *most-recently-entered* pointer. It is set on entry and **never cleared on return**
— measured across all 43 Skill stages in an 86-transcript corpus: attribution returns to
the conductor **once**, never returns to any command 36 times, and jumps to a third command
6 times.

The consequence is not academic. In the session that answered this spec's own go/no-go,
`/specs:develop` invoked `/specs:isolate` as a stage; isolate finished at its "Isolated."
turn, and the conductor's next five `AskUserQuestion` calls — its own spec-shape bank — are
still stamped `quenching:specs:isolate`. Reported naively that is "the isolation stage asked
the human five questions", which is false and entirely plausible.

There is no end marker in the transcript to fix this with. Inventing one would manufacture
findings, so this tool does the other thing: it **detects and names the misread**. A command
entered as a stage whose caller never regained attribution is marked `closed: false`, and
every count on it is reported as an upper bound that may include the caller's own work. That
is `docs/standards/quality/parse-honesty.md` applied to a pointer instead of a parser — name
the *misread*, never the *consequence*.

So the entry marks are read for *how a command was reached and with what arguments*, and
attribution for *what it plausibly cost*, with the honesty flag attached.

THE TOOL CONTRACT
-----------------
Same shape as its three siblings, so a command body branches on DATA and never on prose:
every subcommand takes `--json`, and the exit code is the whole decision.

    0   ok            read clean: every record parsed and every stage's attribution closed
    1   findings      read and reported, with an anomaly against it — an unparsable record,
                      or a stage whose counts are an upper bound. The numbers are real; the
                      coverage is not provably complete
    2   refusal       nothing usable: no transcript, an empty one, a non-empty one that
                      yielded no command, or a `--command` that is not in it

Exit 1 exists so a caller can tell "clean read" from "read with holes" without parsing the
anomaly list. It is not a failure — the findings are printed either way.

PARSE HONESTY
-------------
Per `docs/standards/quality/parse-honesty.md`: this tool narrows a transcript into a
command model, so it must be able to say what it could not read. A line that fails to
parse is counted and reported as an anomaly ahead of the content, because "no commands
found" and "I could not read this file" look identical in a report and lead to opposite
actions.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

VERSION = "4.2.0"  # tracks the plugin; deliberately OUTSIDE the six-artifact lockstep (see above)

OK, FINDINGS, REFUSAL = 0, 1, 2

# Claude Code encodes a project's cwd by replacing \ / : . with '-'. chr(92) IS the
# backslash, spelled this way so no quoting layer can eat the escape. Same rule as
# /docs:import-memory uses to find `memory/` — one encoding, not two.
PUNCT = set(chr(92) + "/:.")

COMMAND_NAME_RE = re.compile(r"<command-name>([^<]+)</command-name>")
COMMAND_ARGS_RE = re.compile(r"<command-args>([^<]*)</command-args>")


def encode_cwd(path) -> str:
    return "".join("-" if c in PUNCT else c for c in str(path))


def projects_root() -> Path:
    return Path.home() / ".claude" / "projects"


def resolve_project_dir(cwd: Path) -> tuple[Path | None, str]:
    """The transcript directory for `cwd`, nearest ancestor first.

    A git worktree or a subdirectory has no directory of its own, and falls back to the
    checkout it was cut from — the same nearest-first walk /docs:import-memory does.
    """
    root = projects_root()
    if not root.is_dir():
        return None, f"no transcript root at {root}"
    # .lower(): a Windows drive letter's case is not stable (c:\ vs C:\); the rest is exact.
    have = {d.name.lower(): d for d in root.glob("*") if d.is_dir()}
    for p in (cwd, *cwd.parents):
        hit = have.get(encode_cwd(p).lower())
        if hit is not None:
            return hit, "exact" if p == cwd else f"ancestor {p}"
    return None, f"no transcript directory for {encode_cwd(cwd)}"


def resolve_transcript(arg: str | None, cwd: Path) -> tuple[Path | None, str]:
    """An explicit path, a bare session id, or the most recent session for `cwd`."""
    if arg:
        p = Path(arg).expanduser()
        if p.is_file():
            return p, "explicit path"
        d, how = resolve_project_dir(cwd)
        if d is not None:
            byid = d / f"{arg}.jsonl"
            if byid.is_file():
                return byid, f"session id in {how} project dir"
        return None, f"no transcript at {arg}"
    d, how = resolve_project_dir(cwd)
    if d is None:
        return None, how
    files = sorted(d.glob("*.jsonl"), key=lambda f: f.stat().st_mtime, reverse=True)
    if not files:
        return None, f"no transcript files in {d}"
    return files[0], f"most recent in {how} project dir"


def normalize(name: str) -> str:
    """`/quenching:specs:develop` and `quenching:specs:develop` are one command."""
    return name.strip().lstrip("/").strip()


class Command:
    """One command, aggregated across every turn attributed to it."""

    __slots__ = ("name", "plugin", "invocations", "tools", "first", "last",
                 "first_ts", "last_ts", "reads", "touches", "shell", "closed", "may_include")

    def __init__(self, name: str):
        self.name = name
        self.plugin = None
        self.invocations = []      # how it was reached, in order
        self.tools = {}            # tool name -> count, attributed turns only
        self.first = self.last = None
        self.first_ts = self.last_ts = None
        self.reads = {}            # file path -> [window, ...], one entry per Read
        self.touches = {}          # file path -> count of Edit/Write, which are not reads
        self.shell = {}            # bash command string -> count
        # True until proven otherwise: only a stage whose caller never resumed is unclosed.
        self.closed = True
        self.may_include = None

    def touch(self, index: int, ts):
        if self.first is None:
            self.first, self.first_ts = index, ts
        self.last, self.last_ts = index, ts

    @property
    def tool_calls(self) -> int:
        return sum(self.tools.values())

    @property
    def entry_forms(self) -> list:
        return sorted({i["form"] for i in self.invocations})

    def as_dict(self) -> dict:
        return {
            "command": self.name,
            "plugin": self.plugin,
            "entryForms": self.entry_forms or ["attributed"],
            "invocations": self.invocations,
            "toolCalls": self.tool_calls,
            "tools": dict(sorted(self.tools.items(), key=lambda kv: (-kv[1], kv[0]))),
            # Named `attributedRun`, not `span`: these are the turns for which this command
            # was the most recently entered one, which is NOT proof it was still executing.
            "attributedRun": {
                "firstLine": self.first,
                "lastLine": self.last,
                "firstTimestamp": self.first_ts,
                "lastTimestamp": self.last_ts,
                "closed": self.closed,
                "mayIncludeTurnsFrom": self.may_include,
            },
        }


def read_window(inp: dict) -> str:
    """`Read`'s slice of a file. Two looks at the same window are redundant; two looks at
    different windows are paging, and a digest that conflates them invents a finding."""
    offset, limit = inp.get("offset"), inp.get("limit")
    if offset is None and limit is None:
        return "full"
    return f"{offset or 0}+{limit if limit is not None else 'end'}"


INTERRUPT = "[Request interrupted by user"
COMPACTION = "This session is being continued from a previous conversation"


def classify_user_turn(text: str) -> str | None:
    """What a human turn is evidence OF, or None when it is not evidence at all.

    An interrupt is the strongest signal a command misfired — the human stopped it
    mid-flight. An interjection is weaker but is still the human supplying something the
    command should have known. A compaction notice is neither; it is the harness talking,
    and counting it as a correction would blame the command for running long.
    """
    stripped = text.strip()
    if not stripped:
        return None
    if INTERRUPT in stripped:
        return "interrupt"
    if stripped.startswith(COMPACTION):
        return "compaction"
    if stripped.startswith("<"):        # a command invocation or a harness-injected block
        return None
    return "interjection"


def blocks(record: dict):
    """The content blocks of a record, as a list — a bare string yields none."""
    content = (record.get("message") or {}).get("content")
    return [b for b in content if isinstance(b, dict)] if isinstance(content, list) else []


def close_attribution(ordered: list, timeline: list, anomalies: list) -> None:
    """Mark every stage whose caller never took attribution back.

    A stage invoked by a conductor at line N is `closed` only if the conductor appears in
    the attribution timeline again after N. When it does not, attribution stayed pointing at
    the stage while the conductor carried on working, and every count on that stage is an
    upper bound that silently includes the conductor's own turns.

    This is the only claim the transcript actually supports. Guessing where the stage really
    stopped would turn an unknown into a fabricated finding, which is the failure the whole
    tool exists to avoid.
    """
    for cmd in ordered:
        for inv in cmd.invocations:
            caller = inv.get("invokedBy")
            if inv["form"] != "skill" or not caller:
                continue
            resumed = next((line for line, name in timeline
                            if line > inv["line"] and name == caller), None)
            if resumed is None:
                cmd.closed = False
                cmd.may_include = caller
                anomalies.append({
                    "code": "se-attribution-unclosed", "line": inv["line"],
                    "message": f"{cmd.name} was invoked as a stage by {caller}, which never "
                               f"regained attribution — counts for {cmd.name} are an upper "
                               f"bound and may include {caller}'s own turns"})
            else:
                # The conductor came back, so the stage's run genuinely ends before it.
                cmd.last = min(cmd.last, resumed - 1) if cmd.last is not None else None


def read_session(path: Path) -> dict:
    """One streaming pass. Never holds the transcript, only the model built from it."""
    commands: dict[str, Command] = {}
    anomalies, seen_uuids, corrections = [], set(), []
    timeline = []                  # (line, command) for every attributed record, in order
    lines = unparsed = unattributed_tools = 0
    session = {"sessionId": None, "cwd": None, "gitBranch": None, "version": None}

    def command(name: str) -> Command:
        return commands.setdefault(name, Command(name))

    with path.open(encoding="utf-8", errors="replace") as fh:
        for index, raw in enumerate(fh, start=1):
            raw = raw.strip()
            if not raw:
                continue
            lines += 1
            try:
                rec = json.loads(raw)
            except (ValueError, TypeError):
                rec = None
            if not isinstance(rec, dict):
                # Both arms are the same fact — this line contributed no evidence — so both
                # are counted and reported. Silence here is what makes an unreadable file
                # look like a clean one.
                unparsed += 1
                if len(anomalies) < 10:
                    anomalies.append({"code": "se-unparsed-line", "line": index,
                                      "message": "line is not a JSON object and was skipped"})
                continue

            for key in session:
                if session[key] is None and rec.get(key) is not None:
                    session[key] = rec[key]

            # A compact summary re-embeds earlier turns; counting them doubles the run.
            uuid = rec.get("uuid")
            if uuid is not None:
                if uuid in seen_uuids:
                    continue
                seen_uuids.add(uuid)
            if rec.get("isCompactSummary"):
                continue

            ts = rec.get("timestamp")
            attributed = rec.get("attributionSkill")
            if attributed:
                cmd = command(normalize(attributed))
                if cmd.plugin is None:
                    cmd.plugin = rec.get("attributionPlugin")
                cmd.touch(index, ts)
                timeline.append((index, cmd.name))

            if rec.get("type") == "user":
                content = (rec.get("message") or {}).get("content")
                # A human turn reaches the transcript BOTH ways: as a bare string, and as
                # `text` blocks in a list beside the tool_results the harness also files
                # under "user". Reading only the string form loses every interjection and
                # every interrupt — measured, not assumed: the string form in this repo's
                # largest transcript holds nothing but compaction notices.
                if isinstance(content, str):
                    text = content
                else:
                    text = "\n".join(b.get("text") or "" for b in blocks(rec)
                                     if b.get("type") == "text").strip()

                # Entry form 1 — a typed `/` invocation.
                if "<command-name>" in text:
                    for name in COMMAND_NAME_RE.findall(text):
                        args = COMMAND_ARGS_RE.search(text)
                        cmd = command(normalize(name))
                        cmd.touch(index, ts)
                        cmd.invocations.append({
                            "form": "typed", "line": index, "timestamp": ts,
                            "args": (args.group(1).strip() if args else "") or None,
                            "invokedBy": None,
                        })
                elif text and not rec.get("isMeta"):
                    # isMeta marks a turn the HARNESS wrote into the user slot — chiefly the
                    # expanded body of the command just invoked. It reads like a long human
                    # message and is the opposite of one; counting it would score every
                    # command as having been corrected at its own first turn.
                    kind = classify_user_turn(text)
                    if kind:
                        corrections.append({"line": index, "timestamp": ts, "kind": kind,
                                            "text": " ".join(text.split())})

            # Entry form 2 — a conductor's stage, as a `Skill` tool_use.
            for block in blocks(rec):
                if block.get("type") != "tool_use":
                    continue
                name = block.get("name")
                inp_ = block.get("input") or {}
                if attributed:
                    cmd = command(normalize(attributed))
                    cmd.tools[name] = cmd.tools.get(name, 0) + 1
                    # Only what identifies a target is kept — never the payload. `Edit` and
                    # `Write` carry whole file bodies in `new_string`/`content`, so touching
                    # those inputs at all is how a digest quietly becomes the transcript.
                    target = inp_.get("file_path")
                    if target and name == "Read":
                        cmd.reads.setdefault(target, []).append(read_window(inp_))
                    elif target and name in ("Edit", "Write", "NotebookEdit"):
                        # A write is NOT a read. Lumping them together reported 51 edits to
                        # one file as a "redundant read x72" — a confident, plausible,
                        # entirely wrong finding of exactly the kind this tool must not make.
                        cmd.touches[target] = cmd.touches.get(target, 0) + 1
                    elif name == "Bash":
                        shell = (inp_.get("command") or "").strip()
                        if shell:
                            cmd.shell[shell] = cmd.shell.get(shell, 0) + 1
                else:
                    unattributed_tools += 1
                if name == "Skill":
                    target = inp_.get("skill")
                    if target:
                        callee = command(normalize(target))
                        callee.touch(index, ts)
                        callee.invocations.append({
                            "form": "skill", "line": index, "timestamp": ts,
                            "args": (inp_.get("args") or None),
                            "invokedBy": normalize(attributed) if attributed else None,
                        })

    ordered = sorted(commands.values(), key=lambda c: (c.first if c.first is not None else 0))
    close_attribution(ordered, timeline, anomalies)
    return {
        "transcript": str(path),
        "session": session,
        "lines": lines,
        "unparsed": unparsed,
        "anomalies": anomalies,
        "unattributedToolCalls": unattributed_tools,
        "commands": [c.as_dict() for c in ordered],
        "_commands": ordered,          # the objects, for digest; never serialised
        "corrections": corrections,
    }


def refuse(payload: dict, as_json: bool) -> int:
    """Every refusal leaves by this door: exit 2, a code, and a stated reason."""
    if as_json:
        print(json.dumps({"ok": False, **payload}, indent=2, ensure_ascii=False))
    else:
        print(f"refused: {payload['message']}", file=sys.stderr)
    return REFUSAL


def silence_refusal(model: dict) -> dict | None:
    """Why a zero-command parse must refuse rather than report nothing.

    "No commands found" and "I could not read this file" produce the same empty report and
    call for opposite actions — rerun against another session, or fix the parser. A format
    drift in Claude Code's undocumented JSONL would otherwise land as a clean run forever,
    which is the failure mode `## Risks` names first. So a transcript that HELD something
    and yielded nothing is an exit-2 refusal carrying its reason.
    """
    if model["commands"]:
        return None
    if model["lines"] == 0:
        return {"code": "se-empty-transcript",
                "message": f"{model['transcript']} holds no records — nothing to report, "
                           f"and an empty report would not have said so"}
    unparsed = model["unparsed"]
    detail = (f", and {unparsed} of them could not be parsed — the transcript format has "
              f"likely drifted" if unparsed else
              ", all of which parsed — this session ran no command, or the attribution "
              "and entry-form marks have changed shape")
    return {"code": "se-no-command-parsed",
            "message": f"read {model['lines']} record(s) from {model['transcript']}{detail}"}


def clip(text: str, limit: int) -> str:
    text = " ".join(text.split())
    return text if len(text) <= limit else text[:limit - 1] + "…"


def assign_corrections(corrections: list, ordered: list) -> tuple[dict, list]:
    """Attach each human turn to the command it is evidence about.

    Inside a span is unambiguous. The harder case is the turn that lands just *after* one:
    an interrupt ENDS the span it belongs to, so the strongest evidence a command misfired
    always falls outside it by construction. Those attach to the command that just stopped,
    tagged `after` rather than `during`, because a report that cannot tell the two apart is
    guessing and should say so.
    """
    spans = [(c.first, c.last, c) for c in ordered if c.first is not None]
    spans.sort(key=lambda s: s[0])
    out, unassigned = {c.name: [] for c in ordered}, []
    for corr in corrections:
        line, hit = corr["line"], None
        for lo, hi, cmd in spans:
            if lo <= line <= hi:
                hit = (cmd, "during")
                break
        if hit is None:
            # the nearest span that ended before this turn, with no other span in between
            prior = [s for s in spans if s[1] < line]
            nxt = [s for s in spans if s[0] > line]
            if prior and (not nxt or prior[-1][1] < nxt[0][0]):
                hit = (prior[-1][2], "after")
        if hit is None:
            unassigned.append(corr)
        else:
            out[hit[0].name].append(dict(corr, when=hit[1]))
    return out, unassigned


def digest_command(cmd: Command, corrections: list, limit: int, cap: int) -> dict:
    """One command's evidence, bounded. Counts are exact; quotes are clipped."""
    repeated_reads = []
    for target, windows in cmd.reads.items():
        if len(windows) < 2:
            continue
        tally = {}
        for w in windows:
            tally[w] = tally.get(w, 0) + 1
        repeated_reads.append({
            "target": target,
            "count": len(windows),
            "windows": dict(sorted(tally.items(), key=lambda kv: (-kv[1], kv[0]))),
            # The same window fetched twice is a redundant read. Different windows are
            # paging through one file, which is the tool working as intended.
            "redundant": max(tally.values()) > 1,
        })
    repeated_reads.sort(key=lambda r: (-r["count"], r["target"]))

    repeated_shell = [{"command": clip(c, limit), "count": n}
                      for c, n in sorted(cmd.shell.items(), key=lambda kv: (-kv[1], kv[0]))
                      if n > 1]

    mine = corrections           # already attached to this command by assign_corrections

    out = cmd.as_dict()
    out["repeatedReads"] = repeated_reads[:cap]
    out["repeatedShell"] = repeated_shell[:cap]
    out["corrections"] = [{"line": c["line"], "timestamp": c["timestamp"],
                           "kind": c["kind"], "when": c["when"],
                           "quote": clip(c["text"], limit)}
                          for c in mine[:cap]]
    out["counts"] = {
        "toolCalls": cmd.tool_calls,
        "distinctFilesRead": len(cmd.reads),
        "distinctFilesWritten": len(cmd.touches),
        "writes": sum(cmd.touches.values()),
        "repeatedReadTargets": sum(1 for r in repeated_reads if r["redundant"]),
        "repeatedShellCommands": len(repeated_shell),
        "interrupts": sum(1 for c in mine if c["kind"] == "interrupt"),
        "interjections": sum(1 for c in mine if c["kind"] == "interjection"),
    }
    for key in ("repeatedReads", "repeatedShell", "corrections"):
        dropped = {"repeatedReads": len(repeated_reads), "repeatedShell": len(repeated_shell),
                   "corrections": len(mine)}[key] - len(out[key])
        if dropped > 0:
            out.setdefault("truncated", {})[key] = dropped
    return out


def cmd_digest(args) -> int:
    path, how = resolve_transcript(args.transcript, Path.cwd().resolve())
    if path is None:
        return refuse({"code": "se-no-transcript", "message": how}, args.json)

    model = read_session(path)
    model_objects = model.pop("_commands")
    objects = model_objects
    corrections = model["corrections"]

    silent = silence_refusal(model)
    if silent:
        return refuse(silent, args.json)

    if args.command:
        want = normalize(args.command)
        objects = [c for c in objects if c.name == want]
        if not objects:
            return refuse({"code": "se-unknown-command",
                           "message": f"no command named {want!r} in this transcript; "
                                      f"found {', '.join(c.name for c in model_objects)}"},
                          args.json)

    # Assignment runs over EVERY command in the session, not just the ones being digested:
    # a `--command` filter must not silently hand one command a turn that belonged to the
    # stage running next to it.
    attached, unassigned = assign_corrections(corrections, model_objects)
    digested = [digest_command(c, attached[c.name], args.max_quote, args.cap)
                for c in objects]

    payload = {
        "ok": bool(digested),
        "transcript": model["transcript"],
        "resolvedBy": how,
        "session": model["session"],
        "lines": model["lines"],
        "unparsed": model["unparsed"],
        "anomalies": model["anomalies"],
        "unattributedToolCalls": model["unattributedToolCalls"],
        "maxQuote": args.max_quote,
        "commands": digested,
        "unassignedCorrections": [{"line": c["line"], "kind": c["kind"],
                                   "quote": clip(c["text"], args.max_quote)}
                                  for c in unassigned[:args.cap]],
    }

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(f"transcript: {path}  ({how})   lines={payload['lines']}"
              f"  unparsed={payload['unparsed']}")
        for a in payload["anomalies"]:
            print(f"  ! {a['code']} line {a['line']}: {a['message']}")
        for c in digested:
            n = c["counts"]
            print(f"\n{c['command']}  [{', '.join(c['entryForms'])}]"
                  f"  lines {c['attributedRun']['firstLine']}-{c['attributedRun']['lastLine']}"
                  f"{'' if c['attributedRun']['closed'] else '  [UNCLOSED]'}")
            print(f"  tool calls: {n['toolCalls']}"
                  f"  | files read: {n['distinctFilesRead']}"
                  f"  | files written: {n['distinctFilesWritten']} ({n['writes']} writes)"
                  f"  | redundant read targets: {n['repeatedReadTargets']}"
                  f"  | repeated shell: {n['repeatedShellCommands']}"
                  f"  | interrupts: {n['interrupts']}"
                  f"  | interjections: {n['interjections']}")
            if c["tools"]:
                print("  tools: " + ", ".join(f"{k}={v}" for k, v in c["tools"].items()))
            for r in c["repeatedReads"]:
                if r["redundant"]:
                    print(f"  redundant read x{r['count']}: {r['target']}  {r['windows']}")
            for s in c["repeatedShell"]:
                print(f"  repeated shell x{s['count']}: {s['command']}")
            for k in c["corrections"]:
                print(f"  {k['kind']} ({k['when']}) @ line {k['line']}: {k['quote']}")
            # A capped list that does not say it was capped reads as a complete one.
            for key, n in sorted(c.get("truncated", {}).items()):
                print(f"  … {n} more {key} not shown (--cap {args.cap})")
    return FINDINGS if payload["anomalies"] else OK


# --------------------------------------------------------------------------------------
# selftest
#
# The fixture is a synthetic transcript exercising every rule the parser was WRONG about
# at least once during its own construction. Each record below is a defect that shipped a
# silent zero or a confident false count before it was caught; the fixture is what stops
# each from coming back.
#
# It deliberately does NOT assert where a command's span ENDS, nor which command a human
# turn attaches to. Attribution has no reliable end (measured: it reverts to the conductor
# in 1 of 43 Skill stages across an 86-transcript corpus), and closing the span on the
# Skill boundary is an open `## Design` correction. Freezing today's answer here would
# make the fix look like a regression.
# --------------------------------------------------------------------------------------

FIXTURE = [
    # A typed `/` invocation: a user turn whose content is a STRING.
    {"type": "user", "uuid": "u1", "timestamp": "2026-07-28T10:00:00Z",
     "message": {"content": "<command-message>demo:conduct</command-message>\n"
                            "<command-name>/demo:conduct</command-name>\n"
                            "<command-args>alpha beta</command-args>"}},
    # The harness-injected command body. Reads exactly like a long human message; isMeta
    # is the only thing separating them, and without it every command scores a correction
    # against itself at its own first turn.
    {"type": "user", "uuid": "u2", "isMeta": True, "timestamp": "2026-07-28T10:00:01Z",
     "message": {"content": [{"type": "text", "text": "# /demo:conduct — the expanded body"}]}},
    # Two Reads of the SAME window: redundant.
    {"type": "assistant", "uuid": "u3", "attributionSkill": "demo:conduct",
     "attributionPlugin": "demo", "timestamp": "2026-07-28T10:00:02Z",
     "message": {"content": [{"type": "tool_use", "name": "Read", "input": {"file_path": "/a.py"}}]}},
    {"type": "assistant", "uuid": "u4", "attributionSkill": "demo:conduct",
     "message": {"content": [{"type": "tool_use", "name": "Read", "input": {"file_path": "/a.py"}}]}},
    # Two Reads of DIFFERENT windows: paging, not redundancy.
    {"type": "assistant", "uuid": "u5", "attributionSkill": "demo:conduct",
     "message": {"content": [{"type": "tool_use", "name": "Read",
                              "input": {"file_path": "/b.py", "offset": 1, "limit": 50}}]}},
    {"type": "assistant", "uuid": "u6", "attributionSkill": "demo:conduct",
     "message": {"content": [{"type": "tool_use", "name": "Read",
                              "input": {"file_path": "/b.py", "offset": 60, "limit": 50}}]}},
    # An Edit is a WRITE. Counting it as a read once reported 51 edits as "redundant x72".
    {"type": "assistant", "uuid": "u7", "attributionSkill": "demo:conduct",
     "message": {"content": [{"type": "tool_use", "name": "Edit",
                              "input": {"file_path": "/a.py", "old_string": "x", "new_string": "y"}}]}},
    # A conductor's stage. The Skill call is attributed to the CALLER.
    {"type": "assistant", "uuid": "u8", "attributionSkill": "demo:conduct",
     "message": {"content": [{"type": "tool_use", "name": "Skill",
                              "input": {"skill": "demo:stage", "args": "gamma"}}]}},
    {"type": "assistant", "uuid": "u9", "attributionSkill": "demo:stage",
     "message": {"content": [{"type": "tool_use", "name": "Bash",
                              "input": {"command": "echo hi"}}]}},
    {"type": "assistant", "uuid": "u10", "attributionSkill": "demo:stage",
     "message": {"content": [{"type": "tool_use", "name": "Bash",
                              "input": {"command": "echo hi"}}]}},
    # A human turn as a text BLOCK in a list. Reading only the string form found ZERO
    # interjections on a real session that visibly had several.
    {"type": "user", "uuid": "u11", "timestamp": "2026-07-28T10:00:11Z",
     "message": {"content": [{"type": "text", "text": "no, use the other file"}]}},
    {"type": "user", "uuid": "u12", "timestamp": "2026-07-28T10:00:12Z",
     "message": {"content": [{"type": "text", "text": "[Request interrupted by user]"}]}},
    "{ this line is not JSON",          # must be COUNTED and REPORTED, never silently dropped
    # A replayed uuid: a compact summary re-embeds earlier turns, which would double the run.
    {"type": "user", "uuid": "u12",
     "message": {"content": [{"type": "text", "text": "[Request interrupted by user]"}]}},
    # The harness talking, not the human. Counting it blames the command for running long.
    {"type": "user", "uuid": "u15",
     "message": {"content": "This session is being continued from a previous conversation "
                            "that ran out of context."}},
]


# The rare good case: the conductor DOES take attribution back, so the stage's run genuinely
# ends and its counts are exact. Measured at 1 of 43 stages, which is exactly why the other
# 42 must not be reported as though they looked like this.
CLOSED_FIXTURE = [
    {"type": "user", "uuid": "c1",
     "message": {"content": "<command-name>/demo:conduct</command-name>"}},
    {"type": "assistant", "uuid": "c2", "attributionSkill": "demo:conduct",
     "message": {"content": [{"type": "tool_use", "name": "Skill",
                              "input": {"skill": "demo:stage"}}]}},
    {"type": "assistant", "uuid": "c3", "attributionSkill": "demo:stage",
     "message": {"content": [{"type": "tool_use", "name": "Bash", "input": {"command": "a"}}]}},
    {"type": "assistant", "uuid": "c4", "attributionSkill": "demo:conduct",
     "message": {"content": [{"type": "tool_use", "name": "Bash", "input": {"command": "b"}}]}},
]


# A transcript that plainly HELD something and yielded no command. The point of the case
# is that this must never come back as a clean, empty report.
SILENT_FIXTURE = [
    {"type": "user", "uuid": "s1", "message": {"content": "just a conversation"}},
    {"type": "assistant", "uuid": "s2",
     "message": {"content": [{"type": "tool_use", "name": "Bash", "input": {"command": "ls"}}]}},
]


def selftest_failures() -> list:
    """Every assertion the fixture exists to make. Returns the failures, [] on pass."""
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "fixture.jsonl"
        path.write_text("\n".join(json.dumps(r) if isinstance(r, dict) else r
                                  for r in FIXTURE) + "\n", encoding="utf-8")
        model = read_session(path)

        silent_path = Path(tmp) / "silent.jsonl"
        silent_path.write_text("\n".join(json.dumps(r) for r in SILENT_FIXTURE) + "\n",
                               encoding="utf-8")
        silent_model = read_session(silent_path)
        silent_model.pop("_commands")

        empty_path = Path(tmp) / "empty.jsonl"
        empty_path.write_text("", encoding="utf-8")
        empty_model = read_session(empty_path)
        empty_model.pop("_commands")

        closed_path = Path(tmp) / "closed.jsonl"
        closed_path.write_text("\n".join(json.dumps(r) for r in CLOSED_FIXTURE) + "\n",
                               encoding="utf-8")
        closed_model = read_session(closed_path)
        closed_by_name = {c.name: c for c in closed_model.pop("_commands")}

    fail = []
    by_name = {c.name: c for c in model["_commands"]}

    def check(label, got, want):
        if got != want:
            fail.append(f"{label}: expected {want!r}, got {got!r}")

    check("commands found", sorted(by_name), ["demo:conduct", "demo:stage"])
    if fail:
        return fail          # nothing below this line is meaningful without both commands

    conduct, stage = by_name["demo:conduct"], by_name["demo:stage"]

    check("typed entry form", conduct.entry_forms, ["typed"])
    check("typed args", [i["args"] for i in conduct.invocations], ["alpha beta"])
    check("attributionPlugin", conduct.plugin, "demo")
    check("skill entry form", stage.entry_forms, ["skill"])
    check("stage invokedBy", [i["invokedBy"] for i in stage.invocations], ["demo:conduct"])
    check("stage args", [i["args"] for i in stage.invocations], ["gamma"])

    # The Skill call itself belongs to the caller, and the stage's work to the callee.
    check("conduct tool counts", conduct.tools, {"Read": 4, "Edit": 1, "Skill": 1})
    check("stage tool counts", stage.tools, {"Bash": 2})

    check("reads exclude writes", sorted(conduct.reads), ["/a.py", "/b.py"])
    check("same window twice", conduct.reads.get("/a.py"), ["full", "full"])
    check("paged reads differ", conduct.reads.get("/b.py"), ["1+50", "60+50"])
    check("writes counted apart", conduct.touches, {"/a.py": 1})
    check("repeated shell", stage.shell, {"echo hi": 2})

    # Corrections: what was collected, not where it was attached (see the note above).
    kinds = [(c["line"], c["kind"]) for c in model["corrections"]]
    check("corrections collected", kinds,
          [(11, "interjection"), (12, "interrupt"), (15, "compaction")])

    # Attribution honesty: the stage's caller never resumed here, so its counts are capped.
    check("conductor's own run is closed", conduct.closed, True)
    check("unresumed stage is unclosed", stage.closed, False)
    check("and names whose turns it may hold", stage.may_include, "demo:conduct")
    check("the misread is reported, not just flagged",
          [a["code"] for a in model["anomalies"] if a["code"] == "se-attribution-unclosed"],
          ["se-attribution-unclosed"])
    # ...and the good case is not flagged, or the signal would mean nothing.
    closed_stage = closed_by_name.get("demo:stage")
    check("a resumed stage IS closed", closed_stage and closed_stage.closed, True)
    check("a closed stage's run ends before the conductor resumes",
          closed_stage and closed_stage.last, 3)
    check("no anomaly on the clean case",
          [a["code"] for a in closed_model["anomalies"]], [])

    unparsed_anomalies = [a for a in model["anomalies"] if a["code"] == "se-unparsed-line"]
    check("unparsed counted", model["unparsed"], 1)
    check("unparsed reported", len(unparsed_anomalies), 1)
    check("unparsed line number", [a["line"] for a in unparsed_anomalies], [13])

    # Silence must refuse, never report clean.
    check("a parsed run does not refuse", silence_refusal(model), None)
    silent = silence_refusal(silent_model)
    check("non-empty zero-command refuses",
          silent and silent["code"], "se-no-command-parsed")
    check("the refusal states how much it read",
          bool(silent and "2 record(s)" in silent["message"]), True)
    empty = silence_refusal(empty_model)
    check("empty transcript refuses", empty and empty["code"], "se-empty-transcript")

    # The uniform contract, proved against the parser rather than against the docstring:
    # a subcommand added without --json is the whole failure mode this catches.
    subparsers = [a for a in build_parser()._actions
                  if isinstance(a, argparse._SubParsersAction)]
    check("the parser has subcommands", bool(subparsers), True)
    for name, sub in (subparsers[0].choices.items() if subparsers else []):
        opts = {o for action in sub._actions for o in action.option_strings}
        check(f"{name} accepts --json", "--json" in opts, True)
    check("exit codes are 0/1/2", (OK, FINDINGS, REFUSAL), (0, 1, 2))
    return fail


def cmd_selftest(args) -> int:
    fail = selftest_failures()
    if args.json:
        print(json.dumps({"ok": not fail, "cases": len(FIXTURE), "failures": fail}, indent=2))
    else:
        print(f"session selftest — {len(FIXTURE)} fixture record(s)")
        for f in fail:
            print(f"  FAIL {f}")
        print("\n  PASS" if not fail else f"\n  FAIL — {len(fail)} assertion(s)")
    return OK if not fail else FINDINGS


def cmd_list(args) -> int:
    path, how = resolve_transcript(args.transcript, Path.cwd().resolve())
    if path is None:
        return refuse({"code": "se-no-transcript", "message": how}, args.json)

    model = read_session(path)
    model.pop("_commands")
    model.pop("corrections")
    model["resolvedBy"] = how

    silent = silence_refusal(model)
    if silent:
        return refuse(silent, args.json)
    model["ok"] = True

    if args.json:
        print(json.dumps(model, indent=2, ensure_ascii=False))
    else:
        s = model["session"]
        print(f"transcript: {path}  ({how})")
        print(f"session:    {s['sessionId']}  cwd={s['cwd']}  branch={s['gitBranch']}")
        print(f"lines:      {model['lines']}  unparsed={model['unparsed']}"
              f"  unattributed tool calls={model['unattributedToolCalls']}")
        for a in model["anomalies"]:
            print(f"  ! {a['code']} line {a['line']}: {a['message']}")
        # A zero-command parse never reaches here — silence_refusal already exited 2.
        print(f"\n{len(model['commands'])} command(s):")
        for c in model["commands"]:
            run = c["attributedRun"]
            print(f"  {c['command']}")
            print(f"    entry: {', '.join(c['entryForms'])}"
                  f"  lines {run['firstLine']}-{run['lastLine']}"
                  f"  tool calls: {c['toolCalls']}"
                  f"{'' if run['closed'] else '  [UNCLOSED]'}")
            if not run["closed"]:
                print(f"    ! attribution never returned to {run['mayIncludeTurnsFrom']} — "
                      f"these counts are an upper bound")
            if c["tools"]:
                top = ", ".join(f"{k}={v}" for k, v in list(c["tools"].items())[:6])
                print(f"    tools: {top}")
            for inv in c["invocations"]:
                by = f" (invoked by {inv['invokedBy']})" if inv["invokedBy"] else ""
                arg = f" args={inv['args']!r}" if inv["args"] else ""
                print(f"    - {inv['form']} at line {inv['line']}{by}{arg}")
    return FINDINGS if model["anomalies"] else OK


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="session.py",
                                description="read a Claude Code session transcript as evidence")
    p.add_argument("--version", action="store_true", help="print the version and exit")
    sub = p.add_subparsers(dest="cmd")
    sp = sub.add_parser("list", help="every command a session ran, with its tool-call span")
    sp.add_argument("transcript", nargs="?",
                    help="path to a .jsonl transcript, or a session id; "
                         "default: the most recent session for this cwd")
    sp.add_argument("--json", action="store_true", help="machine-readable output")
    sp.set_defaults(func=cmd_list)

    dg = sub.add_parser("digest", help="one command's evidence: counts, redundant reads, corrections")
    dg.add_argument("transcript", nargs="?", help="path to a .jsonl transcript, or a session id")
    dg.add_argument("--command", help="digest only this command (default: all of them)")
    dg.add_argument("--json", action="store_true", help="machine-readable output")
    dg.add_argument("--max-quote", type=int, default=200, metavar="N",
                    help="clip every quoted string to N characters (default: 200)")
    dg.add_argument("--cap", type=int, default=20, metavar="N",
                    help="at most N items per evidence list (default: 20)")
    dg.set_defaults(func=cmd_digest)

    st = sub.add_parser("selftest", help="prove the transcript-parsing rules against the fixture")
    st.add_argument("--json", action="store_true", help="machine-readable output")
    st.set_defaults(func=cmd_selftest)
    return p


def main(argv: list[str]) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.version:
        print(f"session {VERSION}")
        return OK
    if not getattr(args, "func", None):
        parser.print_help()
        return OK
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
