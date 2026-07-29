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
                 "first_ts", "last_ts")

    def __init__(self, name: str):
        self.name = name
        self.plugin = None
        self.invocations = []      # how it was reached, in order
        self.tools = {}            # tool name -> count, attributed turns only
        self.first = self.last = None
        self.first_ts = self.last_ts = None

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


def blocks(record: dict):
    """The content blocks of a record, as a list — a bare string yields none."""
    content = (record.get("message") or {}).get("content")
    return [b for b in content if isinstance(b, dict)] if isinstance(content, list) else []


def read_session(path: Path) -> dict:
    """One streaming pass. Never holds the transcript, only the model built from it."""
    commands: dict[str, Command] = {}
    anomalies, seen_uuids = [], set()
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

            # Entry form 1 — a typed `/` invocation, in a user turn's content string.
            if rec.get("type") == "user":
                content = (rec.get("message") or {}).get("content")
                if isinstance(content, str) and "<command-name>" in content:
                    for name in COMMAND_NAME_RE.findall(content):
                        args = COMMAND_ARGS_RE.search(content)
                        cmd = command(normalize(name))
                        cmd.touch(index, ts)
                        cmd.invocations.append({
                            "form": "typed", "line": index, "timestamp": ts,
                            "args": (args.group(1).strip() if args else "") or None,
                            "invokedBy": None,
                        })

            # Entry form 2 — a conductor's stage, as a `Skill` tool_use.
            for block in blocks(rec):
                if block.get("type") != "tool_use":
                    continue
                name = block.get("name")
                if attributed:
                    cmd = command(normalize(attributed))
                    cmd.tools[name] = cmd.tools.get(name, 0) + 1
                else:
                    unattributed_tools += 1
                if name == "Skill":
                    inp = block.get("input") or {}
                    target = inp.get("skill")
                    if target:
                        callee = command(normalize(target))
                        callee.touch(index, ts)
                        callee.invocations.append({
                            "form": "skill", "line": index, "timestamp": ts,
                            "args": (inp.get("args") or None),
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
    }


def cmd_list(args) -> int:
    path, how = resolve_transcript(args.transcript, Path.cwd().resolve())
    if path is None:
        if args.json:
            print(json.dumps({"ok": False, "code": "se-no-transcript", "message": how}, indent=2))
        else:
            print(f"refused: {how}", file=sys.stderr)
        return REFUSAL

    model = read_session(path)
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
