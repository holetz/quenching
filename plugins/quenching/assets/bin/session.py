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

`attributionSkill` is that span: every turn a command drives carries the command's name,
including turns inside a stage a conductor invoked. The invoking `Skill` call is attributed
to the **caller**, and the stage's own turns to the **callee**, so a conductor and its
stages separate cleanly without inferring nesting from anything.

So the entry marks are read for *how a command was reached and with what arguments*, and
attribution is read for *what it cost*. A command may be found by attribution alone — a
stage whose entry mark fell outside a compacted window still has every turn it drove.

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
                 "first_ts", "last_ts", "reads", "touches", "shell")

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
            "span": {
                "firstLine": self.first,
                "lastLine": self.last,
                "firstTimestamp": self.first_ts,
                "lastTimestamp": self.last_ts,
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


def read_session(path: Path) -> dict:
    """One streaming pass. Never holds the transcript, only the model built from it."""
    commands: dict[str, Command] = {}
    anomalies, seen_uuids, corrections = [], set(), []
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
        if args.json:
            print(json.dumps({"ok": False, "code": "se-no-transcript", "message": how}, indent=2))
        else:
            print(f"refused: {how}", file=sys.stderr)
        return REFUSAL

    model = read_session(path)
    model_objects = model.pop("_commands")
    objects = model_objects
    corrections = model["corrections"]
    if args.command:
        want = normalize(args.command)
        objects = [c for c in objects if c.name == want]
        if not objects:
            msg = f"no command named {want!r} in this transcript"
            if args.json:
                print(json.dumps({"ok": False, "code": "se-unknown-command",
                                  "message": msg}, indent=2))
            else:
                print(f"refused: {msg}", file=sys.stderr)
            return REFUSAL

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
                  f"  lines {c['span']['firstLine']}-{c['span']['lastLine']}")
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
    return OK if digested else FINDINGS


def cmd_list(args) -> int:
    path, how = resolve_transcript(args.transcript, Path.cwd().resolve())
    if path is None:
        if args.json:
            print(json.dumps({"ok": False, "code": "se-no-transcript", "message": how}, indent=2))
        else:
            print(f"refused: {how}", file=sys.stderr)
        return REFUSAL

    model = read_session(path)
    model.pop("_commands")
    model.pop("corrections")
    model["resolvedBy"] = how
    model["ok"] = bool(model["commands"])

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
        if not model["commands"]:
            print("\nno commands found in this transcript")
        else:
            print(f"\n{len(model['commands'])} command(s):")
            for c in model["commands"]:
                span = c["span"]
                print(f"  {c['command']}")
                print(f"    entry: {', '.join(c['entryForms'])}"
                      f"  lines {span['firstLine']}-{span['lastLine']}"
                      f"  tool calls: {c['toolCalls']}")
                if c["tools"]:
                    top = ", ".join(f"{k}={v}" for k, v in list(c["tools"].items())[:6])
                    print(f"    tools: {top}")
                for inv in c["invocations"]:
                    by = f" (invoked by {inv['invokedBy']})" if inv["invokedBy"] else ""
                    arg = f" args={inv['args']!r}" if inv["args"] else ""
                    print(f"    - {inv['form']} at line {inv['line']}{by}{arg}")
    return OK if model["commands"] else FINDINGS


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
