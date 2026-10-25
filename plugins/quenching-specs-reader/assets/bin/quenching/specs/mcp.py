"""`cq specs mcp` — the specs service's MCP read surface, over stdio.

A second port of the SAME core `cq specs` runs on. Every tool builds the argv of the CLI verb it
mirrors and dispatches it in-process through `quenching.specs.commands.cli.main`, so the backend,
the CAS, the refusals and the exit codes are the CLI's; this module owns the protocol, the argument
validation, the paging and the size ceiling, and nothing about the store.

* Transport: JSON-RPC 2.0, one message per line on stdin/stdout. stdout carries protocol lines
  ONLY — every verb runs with stdout and stderr captured.
* Read-only by construction: the tool table is a closed map from a tool name to a fixed verb. No
  tool takes an argv, so no argument can reach a write verb.
* Size is a contract: no tool returns a whole spec. Reads go by section and by task, listings are
  paged, and a final guard cuts any answer above `MAX_CHARS` with `truncated: true`.
"""
from __future__ import annotations

import contextlib
import io
import json
import re
import sys

from quenching.common.output import OK
from quenching.common.version import VERSION
from quenching.specs.parse import PHASES

PROTOCOL_VERSIONS = ("2025-06-18", "2025-03-26", "2024-11-05")
MAX_CHARS = 60_000
DEFAULT_LIMIT, MAX_LIMIT = 50, 200
MOMENTS = ("decision", "build", "close")
SCOPES = ("global", "current")

ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


class ToolArgs(ValueError):
    """A tool argument that fails validation — reported as a tool error, never a crash."""


def _text(args: dict, key: str, required: bool = False) -> str | None:
    value = args.get(key)
    if value is None:
        if required:
            raise ToolArgs(f"`{key}` is required")
        return None
    if isinstance(value, bool) or not isinstance(value, (str, int)):
        raise ToolArgs(f"`{key}` must be a string")
    value = str(value).strip()
    if not value or value.startswith("-") or "\n" in value:
        raise ToolArgs(f"`{key}` is not a valid value")
    return value


def _id(args: dict, key: str, required: bool = False) -> str | None:
    value = _text(args, key, required)
    if value is not None and not ID.match(value):
        raise ToolArgs(f"`{key}` must be a spec id")
    return value


def _choice(args: dict, key: str, allowed: tuple) -> str | None:
    value = _text(args, key)
    if value is not None and value not in allowed:
        raise ToolArgs(f"`{key}` must be one of {', '.join(allowed)}")
    return value


def _int(args: dict, key: str, default: int, low: int, high: int) -> int:
    value = args.get(key, default)
    if isinstance(value, bool) or not isinstance(value, int) or not low <= value <= high:
        raise ToolArgs(f"`{key}` must be an integer from {low} to {high}")
    return value


def _page(args: dict) -> tuple[int, int]:
    return _int(args, "limit", DEFAULT_LIMIT, 1, MAX_LIMIT), _int(args, "offset", 0, 0, 10**9)


def _paged(payload: dict, key: str, args: dict) -> dict:
    limit, offset = _page(args)
    rows = payload.get(key)
    if not isinstance(rows, list):
        return payload
    window = rows[offset:offset + limit]
    end = offset + len(window)
    payload[key] = window
    payload.update({"returned": len(window), "offset": offset,
                    "nextOffset": end if end < len(rows) else None})
    return payload


def _list(args: dict) -> list[str]:
    argv = ["list", "--lean"]
    phase = _choice(args, "phase", PHASES)
    return argv + (["--phase", phase] if phase else [])


def _status(args: dict) -> list[str]:
    return ["status", "--spec", _id(args, "spec", True)]


def _show(args: dict) -> list[str]:
    argv = ["show", _id(args, "spec", True)]
    tasks = args.get("tasks") or []
    if not isinstance(tasks, list) or len(tasks) > 20:
        raise ToolArgs("`tasks` must be a list of at most 20 task ids")
    for task in tasks:
        argv += ["--task", _text({"task": task}, "task", True)]
    return argv


def _section(args: dict) -> list[str]:
    argv = ["section", _id(args, "spec", True)]
    headings, moment = _text(args, "headings"), _choice(args, "moment", MOMENTS)
    if bool(headings) == bool(moment):
        raise ToolArgs("give exactly one of `headings` or `moment`")
    if headings:
        argv.append(headings)
    else:
        argv += ["--moment", moment]
    scope = _choice(args, "scope", SCOPES)
    return argv + (["--scope", scope] if scope else [])


def _next(args: dict) -> list[str]:
    epic, spec = _id(args, "epic"), _id(args, "spec")
    if epic and spec:
        raise ToolArgs("give `epic` or `spec`, not both")
    if epic:
        return ["next", "--epic", epic, "--limit", str(_page(args)[0])]
    if spec:
        return ["next", "--spec", spec]
    return ["next", "--front"]


def _epic(args: dict) -> list[str]:
    return ["status", "--epic", _id(args, "epic", True)]


def _schema(props: dict, required: list[str] | None = None) -> dict:
    return {"type": "object", "properties": props, "required": required or [],
            "additionalProperties": False}


SPEC = {"type": ["string", "integer"], "description": "the spec id"}
PAGE = {"limit": {"type": "integer", "minimum": 1, "maximum": MAX_LIMIT,
                  "description": f"page size (default {DEFAULT_LIMIT})"},
        "offset": {"type": "integer", "minimum": 0, "description": "rows to skip"}}

# name -> (description, input schema, argv builder, paged payload key or None)
TOOLS: dict[str, tuple] = {
    "specs_list": (
        "List the specs (id, title, phase, state, path), paged. Lean: no stage or task counts.",
        _schema({"phase": {"type": "string", "enum": list(PHASES)}, **PAGE}), _list, "specs"),
    "specs_status": (
        "One spec's derived stage, section states, task progress, records and ready gate. "
        "Carries no section body.",
        _schema({"spec": SPEC}, ["spec"]), _status, None),
    "specs_show": (
        "One spec's map, or only the named tasks (`tasks`: ids) with their files, pattern and "
        "verify. Never the whole document.",
        _schema({"spec": SPEC, "tasks": {"type": "array", "items": {"type": "string"},
                                          "maxItems": 20}}, ["spec"]), _show, None),
    "specs_section": (
        "Read spec sections: `headings` (comma-separated canonical headings) or `moment` "
        "(decision, build, close); `scope` narrows ## Handoff. An answer above the ceiling is cut "
        "and flagged `truncated`.",
        _schema({"spec": SPEC, "headings": {"type": "string"},
                 "moment": {"type": "string", "enum": list(MOMENTS)},
                 "scope": {"type": "string", "enum": list(SCOPES)}}, ["spec"]), _section, None),
    "specs_next": (
        "The next action of one spec (`spec`), the member specs of an epic ready to run now "
        "(`epic`), or the ranked front of every active spec (neither), paged.",
        _schema({"spec": SPEC, "epic": SPEC, **PAGE}), _next, None),
    "specs_epic_progress": (
        "One epic's progress per group, its blocked items and critical path.",
        _schema({"epic": SPEC}, ["epic"]), _epic, None),
}


def run_core(argv: list[str], root: str) -> tuple[int, dict | None, str]:
    """The CLI verb, in this process, with its output captured: `(exit code, payload, stderr)`."""
    from quenching.specs.commands import cli       # lazy: cli mounts this module's `cmd_mcp`
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            code = cli.main(["--root", root, *argv, "--json"])
        except SystemExit as exc:
            code = exc.code if isinstance(exc.code, int) else 2
    try:
        payload = json.loads(out.getvalue())
    except ValueError:
        payload = None
    return code, payload, err.getvalue().strip()


def _guard(payload: dict) -> dict:
    """The last line of defence: an answer above the ceiling is cut and says so."""
    text = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    if len(text) <= MAX_CHARS:
        return payload
    return {"ok": payload.get("ok", True), "truncated": True, "chars": len(text),
            "kept": MAX_CHARS,
            "hint": "narrow the call: fewer headings, `specs_show` with `tasks`, or a smaller "
                    "`limit`",
            "text": text[:MAX_CHARS]}


def call_tool(name: str, args: dict, root: str) -> tuple[dict, bool]:
    """`(payload, is_error)` for one tool call. Raises KeyError for an unknown tool."""
    _, _, build, page_key = TOOLS[name]
    try:
        argv = build(args)
    except ToolArgs as exc:
        return {"ok": False, "code": "mcp-bad-arguments", "message": str(exc)}, True
    code, payload, stderr = run_core(argv, root)
    if payload is None:
        return {"ok": False, "code": "mcp-core-failure", "exit": code,
                "message": stderr or "the core answered with no JSON"}, True
    if page_key is None and name == "specs_next" and "candidates" in payload:
        page_key = "candidates"
    if page_key:
        try:
            payload = _paged(payload, page_key, args)
        except ToolArgs as exc:
            return {"ok": False, "code": "mcp-bad-arguments", "message": str(exc)}, True
    return _guard(payload), code > 1


def _result(request_id, result: dict) -> dict:
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def _error(request_id, code: int, message: str) -> dict:
    return {"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}}


def handle(message, root: str):
    """One JSON-RPC message in, its response out (`None` for a notification)."""
    if isinstance(message, list):
        replies = [r for r in (handle(m, root) for m in message) if r is not None]
        return replies or None
    if not isinstance(message, dict) or message.get("jsonrpc") != "2.0" \
            or not isinstance(message.get("method"), str):
        return _error(message.get("id") if isinstance(message, dict) else None,
                      -32600, "invalid request")
    method, request_id = message["method"], message.get("id")
    params = message.get("params") or {}
    if "id" not in message:
        return None
    if method == "initialize":
        asked = params.get("protocolVersion")
        return _result(request_id, {
            "protocolVersion": asked if asked in PROTOCOL_VERSIONS else PROTOCOL_VERSIONS[0],
            "capabilities": {"tools": {"listChanged": False}},
            "serverInfo": {"name": "quenching-specs", "version": VERSION}})
    if method == "ping":
        return _result(request_id, {})
    if method == "tools/list":
        return _result(request_id, {"tools": [
            {"name": name, "description": spec[0], "inputSchema": spec[1],
             "annotations": {"readOnlyHint": True, "destructiveHint": False,
                             "idempotentHint": True, "openWorldHint": False}}
            for name, spec in TOOLS.items()]})
    if method == "tools/call":
        name, args = params.get("name"), params.get("arguments") or {}
        if name not in TOOLS or not isinstance(args, dict):
            return _error(request_id, -32602, f"unknown tool or bad arguments: {name!r}")
        payload, failed = call_tool(name, args, root)
        return _result(request_id, {
            "content": [{"type": "text",
                         "text": json.dumps(payload, ensure_ascii=False,
                                            separators=(",", ":"))}],
            "isError": failed})
    return _error(request_id, -32601, f"method not found: {method}")


def serve(root: str, stdin=None, stdout=None) -> int:
    """The stdio loop: one JSON message per line until EOF."""
    stdin, stdout = stdin or sys.stdin, stdout or sys.stdout
    for line in stdin:
        line = line.strip()
        if not line:
            continue
        try:
            reply = handle(json.loads(line), root)
        except ValueError:
            reply = _error(None, -32700, "parse error")
        if reply is not None:
            stdout.write(json.dumps(reply, ensure_ascii=False, separators=(",", ":")) + "\n")
            stdout.flush()
    return OK


def cmd_mcp(args, root: str, out) -> int:
    for stream in (sys.stdin, sys.stdout):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, OSError, ValueError):
            pass
    return serve(root)
