"""`cq specs mcp` — the specs service's MCP surface (reads, writes, gated moves), over stdio.

A second port of the SAME core `cq specs` runs on. Every tool builds the argv of the CLI verb it
mirrors and dispatches it in-process through `quenching.specs.commands.cli.main`, so the backend,
the CAS, the refusals and the exit codes are the CLI's; this module owns the protocol, the argument
validation, the paging and the size ceiling, and nothing about the store.

* Transport: JSON-RPC 2.0, one message per line on stdin/stdout. stdout carries protocol lines
  ONLY — every verb runs with stdout and stderr captured.
* Closed by construction: the tool tables are closed maps from a tool name to a fixed verb. No
  tool takes an argv, so no argument can reach a verb the table does not name.
* Gated moves (`approved`, `reviewed`, `merge`, `outcome` records and `promote`) stamp a human
  decision, so the server asks the human through the client (`elicitation/create`) and runs the
  verb only on an accept. There is no argument that confirms: a client without the `elicitation`
  capability gets a refusal, never a silent pass. `approved` is always written `by=human`, and
  only after that confirmation.
* Size is a contract: no tool returns a whole spec. Reads go by section and by task, listings are
  paged, and a final guard cuts any answer above `MAX_CHARS` with `truncated: true`.
* Resources (read-only context): the specs configuration (`quenching://config`, the payload of
  `cq specs config`), the standards under `docs/standards/` and the OKF glossary. A document is
  read whole only when it fits `DOC_WHOLE`; otherwise by outline and `?section=`; the glossary by
  `?term=`. A URI resolves only to the two fixed files or to a `.md` inside `docs/standards/`.
"""
from __future__ import annotations

import contextlib
import io
import json
import os
import re
import sys
from datetime import date
from urllib.parse import parse_qs, urlsplit

from quenching.common.output import OK
from quenching.common.version import VERSION
from quenching.specs.parse import PHASES

PROTOCOL_VERSIONS = ("2025-06-18", "2025-03-26", "2024-11-05")
MAX_CHARS = 60_000
DEFAULT_LIMIT, MAX_LIMIT = 50, 200
MOMENTS = ("decision", "build", "close")
SCOPES = ("global", "current")

DOC_WHOLE = 24_000
RESOURCE_SCHEME = "quenching"
RESOURCE_PATH = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]*$")
GLOSSARY_ENTRY = re.compile(
    r"^\s*[*-]\s+(?:\[(?P<linked>[^\]]+)\]\([^)]*\)|\*\*(?P<plain>[^*]+)\*\*)")
MAX_TERMS = 20
NOT_FOUND, BAD_PARAMS = -32002, -32602

ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
FIELD = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")
MAX_BODY = 200_000
GATED_RECORDS = ("approved", "reviewed", "merge", "outcome")
FREE_RECORDS = ("priority", "refined", "branch", "pr", "buildCost", "run")
TASK_ACTIONS = ("check", "uncheck", "block", "descope")


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


def _rec_fields(args: dict) -> list[str]:
    fields = args.get("fields")
    if not isinstance(fields, dict) or not fields or len(fields) > 20:
        raise ToolArgs("`fields` must be an object of 1 to 20 entries")
    argv = []
    for key, value in fields.items():
        if not FIELD.match(str(key)):
            raise ToolArgs(f"`{key}` is not a field name")
        if isinstance(value, bool) or not isinstance(value, (str, int, float)):
            raise ToolArgs(f"field `{key}` must be a string or a number")
        value = str(value).strip()
        if not value or "\n" in value:
            raise ToolArgs(f"field `{key}` is not a valid value")
        argv += ["--set", f"{key}={value}"]
    return argv


def _w_new(args: dict) -> list[str]:
    argv = ["new", _text(args, "name", True)]
    for key, flag in (("title", "--title"), ("type", "--type"), ("tags", "--tags"),
                      ("complexity", "--complexity")):
        value = _text(args, key)
        if value:
            argv += [flag, value]
    policy = _choice(args, "verification", ("per-task", "per-section", "end-of-plan"))
    return argv + (["--verification", policy] if policy else [])


def _w_section(args: dict) -> list[str]:
    heading = _text(args, "heading", True)
    if "," in heading:
        raise ToolArgs("write one `heading` per call")
    argv = ["section", _id(args, "spec", True), heading, "--write"]
    scope = _choice(args, "scope", SCOPES)
    return argv + (["--scope", scope] if scope else [])


def _w_section_stdin(args: dict) -> str:
    body = args.get("body")
    if not isinstance(body, str) or not body.strip():
        raise ToolArgs("`body` is required")
    if len(body) > MAX_BODY:
        raise ToolArgs(f"`body` is above {MAX_BODY} characters; write the section in parts")
    return body if body.endswith("\n") else body + "\n"


def _record_name(args: dict) -> str:
    name = _text(args, "name", True)
    if name not in FREE_RECORDS + GATED_RECORDS:
        raise ToolArgs(f"`name` must be one of {', '.join(FREE_RECORDS + GATED_RECORDS)}")
    return name


def _w_record(args: dict) -> list[str]:
    name = _record_name(args)
    if name == "approved":
        if args.get("fields") is not None:
            raise ToolArgs("`approved` takes no fields: the server writes date and by=human "
                           "after the human confirms")
        return ["record", _id(args, "spec", True), name,
                "--set", f"date={date.today().isoformat()}", "--set", "by=human"]
    return ["record", _id(args, "spec", True), name, *_rec_fields(args)]


def _w_task(args: dict) -> list[str]:
    action = _choice(args, "action", TASK_ACTIONS)
    if not action:
        raise ToolArgs("`action` is required")
    argv = ["task", "--spec", _id(args, "spec", True), f"--{action}", _text(args, "task", True)]
    reason = args.get("reason")
    if action in ("block", "descope") and not reason:
        raise ToolArgs(f"`reason` is required to {action}")
    for key in ("reason", "subject", "commit"):
        value = args.get(key)
        if value is not None:
            if not isinstance(value, str) or not value.strip() or "\n" in value:
                raise ToolArgs(f"`{key}` must be a one-line string")
            argv += [f"--{key}", value.strip()]
    return argv


def _w_epic_add(args: dict) -> list[str]:
    argv = ["epic", "add", _id(args, "epic", True), _id(args, "spec", True)]
    for key in ("after", "group", "label"):
        value = _text(args, key)
        if value:
            argv += [f"--{key}", value]
    return argv + (["--move"] if args.get("move") is True else [])


def _w_discover(args: dict) -> list[str]:
    text = args.get("text")
    if not isinstance(text, str) or not text.strip() or "\n" in text or len(text) > 2000:
        raise ToolArgs("`text` must be a one-line string of at most 2000 characters")
    return ["discover", _id(args, "spec", True), text.strip()]


def _w_promote(args: dict) -> list[str]:
    argv = ["promote", _id(args, "spec", True)]
    to, outcome = _choice(args, "to", ("plans", "archive")), _choice(args, "outcome",
                                                                       ("done", "abandoned"))
    return argv + (["--to", to] if to else []) + (["--outcome", outcome] if outcome else [])


def _gate_record(args: dict) -> str | None:
    name = _record_name(args)
    if name not in GATED_RECORDS:
        return None
    return f"Stamp the `{name}` record on spec {_id(args, 'spec', True)}? This records a human decision."


def _gate_promote(args: dict) -> str | None:
    target = _choice(args, "to", ("plans", "archive")) or "the next phase"
    return (f"Promote spec {_id(args, 'spec', True)} to {target}"
            f" (outcome: {_choice(args, 'outcome', ('done', 'abandoned')) or 'done'})? "
            "This is a human decision.")


def _preflight_record(args: dict, root: str) -> dict | None:
    """`approved` only on a spec that met the ready gate: refuse before asking the human."""
    if _record_name(args) != "approved":
        return None
    code, payload, stderr = run_core(["status", "--spec", _id(args, "spec", True)], root)
    if payload is None or code > 1:
        return payload or {"ok": False, "code": "mcp-core-failure", "message": stderr}
    ready = payload.get("ready") or {}
    if payload.get("phase") == "plans" and not ready.get("ok"):
        return {"ok": False, "code": "mcp-not-ready",
                "message": "the ready gate is not met; fill the missing sections first",
                "missing": ready.get("missing"), "malformed": ready.get("malformed")}
    return None


def _preflight_promote(args: dict, root: str) -> dict | None:
    """The CLI's own `--dry-run` refusals reach the human's eyes before the question does."""
    code, payload, stderr = run_core(_w_promote(args) + ["--dry-run"], root)
    if payload is None:
        return {"ok": False, "code": "mcp-core-failure", "exit": code, "message": stderr}
    return payload if code != 0 or payload.get("ok") is False else None


# name -> (description, schema, argv builder, stdin builder, gate text builder, preflight)
WRITES: dict[str, tuple] = {
    "specs_create": (
        "Capture a new spec into plans/ (`name`, optional `title`, `type`, `tags`, "
        "`complexity`, `verification`).",
        _schema({"name": {"type": "string"}, "title": {"type": "string"},
                 "type": {"type": "string"}, "tags": {"type": "string"},
                 "complexity": {"type": "string", "enum": ["low", "medium", "high", "xhigh"]},
                 "verification": {"type": "string",
                                  "enum": ["per-task", "per-section", "end-of-plan"]}},
                ["name"]), _w_new, None, None, None),
    "specs_section_write": (
        "Replace ONE section's body (`heading`, `body`); `scope` narrows ## Handoff to one block. "
        f"A body is at most {MAX_BODY} characters: write a long section in parts.",
        _schema({"spec": SPEC, "heading": {"type": "string"}, "body": {"type": "string"},
                 "scope": {"type": "string", "enum": list(SCOPES)}},
                ["spec", "heading", "body"]), _w_section, _w_section_stdin, None, None),
    "specs_record": (
        f"Merge fields into ONE record. Free: {', '.join(FREE_RECORDS)}. Gated, they ask the "
        f"human first: {', '.join(GATED_RECORDS)}; `approved` takes no fields (the server writes "
        "date and by=human after the confirmation, and only on a spec that met the ready gate).",
        _schema({"spec": SPEC, "name": {"type": "string",
                                         "enum": list(FREE_RECORDS + GATED_RECORDS)},
                 "fields": {"type": "object"}}, ["spec", "name"]),
        _w_record, None, _gate_record, _preflight_record),
    "specs_task": (
        "Check, uncheck, block or descope ONE task (`action`, `task`); block and descope need a "
        "`reason`; check takes optional `subject` and `commit`.",
        _schema({"spec": SPEC, "action": {"type": "string", "enum": list(TASK_ACTIONS)},
                 "task": {"type": "string"}, "reason": {"type": "string"},
                 "subject": {"type": "string"}, "commit": {"type": "string"}},
                ["spec", "action", "task"]), _w_task, None, None, None),
    "specs_epic_add": (
        "List a spec as an epic item and stamp `epic:` on it.",
        _schema({"epic": SPEC, "spec": SPEC, "after": {"type": "string"},
                 "group": {"type": "string"}, "label": {"type": "string"},
                 "move": {"type": "boolean"}}, ["epic", "spec"]), _w_epic_add, None, None, None),
    "specs_discover": (
        "Append one finding line to the spec's ## Discoveries.",
        _schema({"spec": SPEC, "text": {"type": "string"}}, ["spec", "text"]),
        _w_discover, None, None, None),
    "specs_promote": (
        "Move a spec between plans/ and archive/ (`to`, `outcome`). Gated: the human confirms "
        "through the client first. Never forced.",
        _schema({"spec": SPEC, "to": {"type": "string", "enum": ["plans", "archive"]},
                 "outcome": {"type": "string", "enum": ["done", "abandoned"]}}, ["spec"]),
        _w_promote, None, _gate_promote, _preflight_promote),
}


class Session:
    """What one stdio connection negotiated: whether the client can ask the human, and how."""

    def __init__(self, ask=None, elicitation: bool = False):
        self.ask, self.elicitation = ask, elicitation

    def confirm(self, message: str) -> bool | None:
        """True on an accept, False on a decline/cancel, None when the human cannot be asked."""
        if not (self.elicitation and self.ask):
            return None
        reply = self.ask(message)
        if not isinstance(reply, dict) or reply.get("action") != "accept":
            return False
        return (reply.get("content") or {}).get("confirm") is True


def run_core(argv: list[str], root: str,
             stdin: str | None = None) -> tuple[int, dict | None, str]:
    """The CLI verb, in this process, with its output captured: `(exit code, payload, stderr)`."""
    from quenching.specs.commands import cli       # lazy: cli mounts this module's `cmd_mcp`
    out, err = io.StringIO(), io.StringIO()
    held = sys.stdin
    sys.stdin = io.StringIO(stdin or "")      # a verb never reads the protocol's own stdin
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                code = cli.main(["--root", root, *argv, "--json"])
            except SystemExit as exc:
                code = exc.code if isinstance(exc.code, int) else 2
    finally:
        sys.stdin = held
    try:
        payload = json.loads(out.getvalue())
    except ValueError:
        payload = None
    return code, payload, err.getvalue().strip()


class ResourceError(Exception):
    """A resource read that fails: a JSON-RPC error with the MCP code, never a crash."""

    def __init__(self, code: int, message: str):
        super().__init__(message)
        self.code, self.message = code, message


def _dump(payload: dict) -> str:
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


def _split_frontmatter(text: str) -> tuple[dict, str]:
    """`(metadata, body)`: the leading `---` block read as flat `key: value` lines."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, text
    for end in range(1, len(lines)):
        if lines[end].strip() == "---":
            meta = {}
            for line in lines[1:end]:
                key, sep, value = line.partition(":")
                if sep and key.strip() and not key.startswith((" ", "\t")):
                    meta[key.strip()] = value.strip()
            return meta, "\n".join(lines[end + 1:]).lstrip("\n")
    return {}, text


def _docs_dir(root: str, *parts: str) -> str:
    return os.path.join(root, "docs", *parts)


def _inside(base: str, path: str) -> bool:
    base, path = os.path.realpath(base), os.path.realpath(path)
    return path.startswith(base + os.sep)


def _standard_files(root: str) -> list[str]:
    """Relative paths (no `.md`) of every standard that really lives under `docs/standards`."""
    base = _docs_dir(root, "standards")
    found = []
    for folder, dirs, files in os.walk(base, followlinks=False):
        dirs.sort()
        for name in sorted(files):
            full = os.path.join(folder, name)
            if name.endswith(".md") and _inside(base, full) and os.path.isfile(full):
                found.append(os.path.relpath(full, base)[:-3].replace(os.sep, "/"))
    return found


def _read_text(path: str) -> str:
    with open(path, encoding="utf-8", errors="replace") as handle:
        return handle.read()


def _cut(text: str, mime: str, hint: str) -> tuple[str, str]:
    """`(mime, text)` bounded by `MAX_CHARS`; above it the answer says it was cut."""
    if len(text) <= MAX_CHARS:
        return mime, text
    return "application/json", _dump({"ok": True, "truncated": True, "chars": len(text),
                                      "kept": MAX_CHARS, "hint": hint,
                                      "text": text[:MAX_CHARS]})


def list_resources(root: str) -> list[dict]:
    items = [{"uri": "quenching://config", "name": "config",
              "title": "Specs service configuration",
              "description": "The repository's specs configuration (`cq specs config`): "
                             "backend, hooks, profiles.",
              "mimeType": "application/json"}]
    glossary = _docs_dir(root, "glossary.md")
    if os.path.isfile(glossary):
        items.append({"uri": "quenching://glossary", "name": "glossary",
                      "title": "OKF glossary",
                      "description": "The term list; read `?term=<term>` for the entries.",
                      "mimeType": "application/json"})
    files = _standard_files(root)
    if files:
        items.append({"uri": "quenching://standards", "name": "standards",
                      "title": "Standards index",
                      "description": "Every standard under docs/standards with its authority.",
                      "mimeType": "application/json"})
    for rel in files:
        meta, _ = _split_frontmatter(_read_text(_docs_dir(root, "standards", rel + ".md")))
        description = meta.get("description", "")
        if meta.get("authority"):
            description = f"[{meta['authority']}] {description}".strip()
        items.append({"uri": f"quenching://standards/{rel}", "name": rel,
                      "title": meta.get("title") or rel, "description": description,
                      "mimeType": "text/markdown"})
    return items


def resource_templates() -> list[dict]:
    return [{"uriTemplate": "quenching://standards/{path}{?section}", "name": "standard",
             "title": "A standard, whole when small, else by section",
             "mimeType": "text/markdown"},
            {"uriTemplate": "quenching://glossary{?term}", "name": "glossary-term",
             "title": "Glossary entries by term", "mimeType": "text/markdown"}]


def _outline(heads: list[dict]) -> list[dict]:
    return [{"level": h["level"], "heading": h["heading"], "chars": len(h["body"])}
            for h in heads]


def _read_config(root: str) -> tuple[str, str]:
    code, payload, stderr = run_core(["config"], root)
    if payload is None or code > 1:
        raise ResourceError(NOT_FOUND, stderr or "the core answered with no JSON")
    return _cut(_dump(payload), "application/json", "the configuration is above the ceiling")


def _read_standards_index(root: str) -> tuple[str, str]:
    rows = []
    for rel in _standard_files(root):
        meta, _ = _split_frontmatter(_read_text(_docs_dir(root, "standards", rel + ".md")))
        rows.append({"uri": f"quenching://standards/{rel}", "title": meta.get("title"),
                     "authority": meta.get("authority")})
    return _cut(_dump({"ok": True, "count": len(rows), "standards": rows}), "application/json",
                "read one standard instead")


def _read_standard(root: str, rel: str, query: dict) -> list[tuple[str, str]]:
    from quenching.components.sections import markdown_sections, select_sections
    if not RESOURCE_PATH.match(rel) or any(p in ("", ".", "..") for p in rel.split("/")):
        raise ResourceError(BAD_PARAMS, "not a standard path")
    base = _docs_dir(root, "standards")
    full = os.path.join(base, *rel.split("/")) + ".md"
    if not _inside(base, full) or not os.path.isfile(full):
        raise ResourceError(NOT_FOUND, f"no such standard: {rel}")
    text = _read_text(full)
    meta, body = _split_frontmatter(text)
    heads = markdown_sections(text)
    wanted = query.get("section")
    if wanted:
        got, missing = select_sections(heads, wanted)
        if missing:
            raise ResourceError(BAD_PARAMS, "no such section: " + "; ".join(missing)
                                + " — read the standard without `section` for its outline")
        merged = "\n\n".join(f"{'#' * h['level']} {h['heading']}\n\n{h['body']}".rstrip()
                             for h in got)
        return [_cut(merged, "text/markdown", "ask for fewer sections")]
    outline = _dump({"ok": True, "title": meta.get("title"), "authority": meta.get("authority"),
                     "chars": len(body), "outline": _outline(heads)})
    if len(body) <= DOC_WHOLE:
        return [("text/markdown", body), ("application/json", outline)]
    note = _dump({"ok": True, "title": meta.get("title"), "authority": meta.get("authority"),
                  "chars": len(body), "truncated": True,
                  "hint": "above the document ceiling: ask `?section=<heading>` for one section",
                  "outline": _outline(heads)})
    return [_cut(note, "application/json", "ask for one section")]


def _glossary_entries(text: str) -> list[tuple[str, str]]:
    """`(term, entry text)` for each bullet; an indented line continues the entry above it."""
    entries: list[tuple[str, list[str]]] = []
    open_entry = False
    for line in text.splitlines():
        found = GLOSSARY_ENTRY.match(line)
        if found:
            entries.append(((found.group("linked") or found.group("plain")).strip(), [line]))
            open_entry = True
        elif open_entry and line.startswith((" ", "\t")) and line.strip():
            entries[-1][1].append(line)
        else:
            open_entry = False
    return [(term, "\n".join(lines)) for term, lines in entries]


def _read_glossary(root: str, query: dict) -> tuple[str, str]:
    path = _docs_dir(root, "glossary.md")
    if not os.path.isfile(path):
        raise ResourceError(NOT_FOUND, "this repository has no docs/glossary.md")
    entries = _glossary_entries(_read_text(path))
    terms = query.get("term")
    if not terms:
        return _cut(_dump({"ok": True, "count": len(entries), "terms": [t for t, _ in entries],
                           "hint": "read `quenching://glossary?term=<term>` for the entries"}),
                    "application/json", "ask for a term")
    if len(terms) > MAX_TERMS:
        raise ResourceError(BAD_PARAMS, f"at most {MAX_TERMS} terms per read")
    chosen, missing = [], []
    for term in terms:
        key = " ".join(term.split()).casefold()
        hits = [e for e in entries if e[0].casefold() == key] \
            or [e for e in entries if e[0].casefold().startswith(key)]
        (chosen.extend(h for h in hits if h not in chosen) if hits and key else missing.append(term))
    if missing:
        raise ResourceError(BAD_PARAMS, "no glossary entry for: " + "; ".join(missing)
                            + " — read `quenching://glossary` for the terms")
    return _cut("\n".join(text for _, text in chosen), "text/markdown", "ask for fewer terms")


def read_resource(uri, root: str) -> list[dict]:
    """The `contents` of one `resources/read`. Raises `ResourceError`."""
    if not isinstance(uri, str) or len(uri) > 500:
        raise ResourceError(BAD_PARAMS, "`uri` must be a string")
    try:
        parts = urlsplit(uri)
        query = parse_qs(parts.query, keep_blank_values=True, strict_parsing=bool(parts.query))
    except ValueError:
        raise ResourceError(BAD_PARAMS, "malformed uri") from None
    name, rest = parts.netloc, parts.path.lstrip("/")
    if parts.scheme != RESOURCE_SCHEME or name not in ("config", "glossary", "standards"):
        raise ResourceError(NOT_FOUND, f"unknown resource: {uri}")
    allowed = {"config": (), "glossary": ("term",), "standards": ("section",)}[name]
    if set(query) - set(allowed) or (name != "standards" and rest):
        raise ResourceError(BAD_PARAMS, f"`{name}` does not take that part of the uri")
    if name == "config":
        pairs = [_read_config(root)]
    elif name == "glossary":
        pairs = [_read_glossary(root, query)]
    elif not rest:
        if query:
            raise ResourceError(BAD_PARAMS, "the standards index takes no `section`")
        pairs = [_read_standards_index(root)]
    else:
        pairs = _read_standard(root, rest, query)
    return [{"uri": uri, "mimeType": mime, "text": text} for mime, text in pairs]


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


def _refusal(code: str, message: str) -> tuple[dict, bool]:
    return {"ok": False, "code": code, "message": message}, True


def call_write(name: str, args: dict, root: str, session: Session) -> tuple[dict, bool]:
    _, _, build, stdin, gate, pre = WRITES[name]
    try:
        argv = build(args)
        body = stdin(args) if stdin else None
        question = gate(args) if gate else None
        refused = pre(args, root) if pre else None
    except ToolArgs as exc:
        return _refusal("mcp-bad-arguments", str(exc))
    if refused is not None:
        return refused, True
    if question is not None:
        answer = session.confirm(question)
        if answer is None:
            return _refusal("mcp-confirmation-unavailable",
                            "this move needs the human's confirmation and the client cannot ask "
                            "(no `elicitation` capability); do it through the CLI or the portal")
        if not answer:
            return _refusal("mcp-confirmation-refused", "the human did not confirm; nothing changed")
    code, payload, stderr = run_core(argv, root, body)
    if payload is None:
        return {"ok": False, "code": "mcp-core-failure", "exit": code,
                "message": stderr or "the core answered with no JSON"}, True
    return _guard(payload), code > 1 or payload.get("ok") is False


def call_tool(name: str, args: dict, root: str,
              session: Session | None = None) -> tuple[dict, bool]:
    """`(payload, is_error)` for one tool call. Raises KeyError for an unknown tool."""
    if name in WRITES:
        return call_write(name, args, root, session or Session())
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


def handle(message, root: str, session: Session | None = None):
    """One JSON-RPC message in, its response out (`None` for a notification)."""
    session = session if session is not None else Session()
    if isinstance(message, list):
        replies = [r for r in (handle(m, root, session) for m in message) if r is not None]
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
        session.elicitation = isinstance((params.get("capabilities") or {}).get("elicitation"),
                                         dict)
        return _result(request_id, {
            "protocolVersion": asked if asked in PROTOCOL_VERSIONS else PROTOCOL_VERSIONS[0],
            "capabilities": {"tools": {"listChanged": False},
                             "resources": {"subscribe": False, "listChanged": False}},
            "serverInfo": {"name": "quenching-specs", "version": VERSION}})
    if method == "ping":
        return _result(request_id, {})
    if method == "tools/list":
        return _result(request_id, {"tools": [
            {"name": name, "description": spec[0], "inputSchema": spec[1],
             "annotations": {"readOnlyHint": True, "destructiveHint": False,
                             "idempotentHint": True, "openWorldHint": False}}
            for name, spec in TOOLS.items()] + [
            {"name": name, "description": spec[0], "inputSchema": spec[1],
             "annotations": {"readOnlyHint": False, "destructiveHint": spec[4] is not None,
                             "idempotentHint": False, "openWorldHint": False}}
            for name, spec in WRITES.items()]})
    if method == "resources/list":
        return _result(request_id, {"resources": list_resources(root)})
    if method == "resources/templates/list":
        return _result(request_id, {"resourceTemplates": resource_templates()})
    if method == "resources/read":
        try:
            return _result(request_id, {"contents": read_resource(params.get("uri"), root)})
        except ResourceError as exc:
            return _error(request_id, exc.code, exc.message)
    if method == "tools/call":
        name, args = params.get("name"), params.get("arguments") or {}
        if name not in TOOLS and name not in WRITES or not isinstance(args, dict):
            return _error(request_id, -32602, f"unknown tool or bad arguments: {name!r}")
        payload, failed = call_tool(name, args, root, session)
        return _result(request_id, {
            "content": [{"type": "text",
                         "text": json.dumps(payload, ensure_ascii=False,
                                            separators=(",", ":"))}],
            "isError": failed})
    return _error(request_id, -32601, f"method not found: {method}")


def _emit(stdout, message: dict) -> None:
    stdout.write(json.dumps(message, ensure_ascii=False, separators=(",", ":")) + "\n")
    stdout.flush()


def serve(root: str, stdin=None, stdout=None) -> int:
    """The stdio loop: one JSON message per line until EOF."""
    stdin, stdout = stdin or sys.stdin, stdout or sys.stdout
    lines = iter(stdin)
    counter = [0]

    def ask(message: str):
        """Server-to-client `elicitation/create`, read synchronously: the loop is serial, so the
        next line answering this id is the human's reply. Anything else meanwhile is dropped."""
        counter[0] += 1
        request_id = f"elicit-{counter[0]}"
        _emit(stdout, {"jsonrpc": "2.0", "id": request_id, "method": "elicitation/create",
                       "params": {"message": message, "requestedSchema": {
                           "type": "object",
                           "properties": {"confirm": {"type": "boolean", "title": "Confirm"}},
                           "required": ["confirm"]}}})
        for line in lines:
            try:
                reply = json.loads(line)
            except ValueError:
                continue
            if isinstance(reply, dict) and reply.get("id") == request_id:
                result = reply.get("result")
                return result if isinstance(result, dict) else {"action": "cancel"}
        return {"action": "cancel"}

    session = Session(ask=ask)
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            reply = handle(json.loads(line), root, session)
        except ValueError:
            reply = _error(None, -32700, "parse error")
        if reply is not None:
            _emit(stdout, reply)
    return OK


def cmd_mcp(args, root: str, out) -> int:
    for stream in (sys.stdin, sys.stdout):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, OSError, ValueError):
            pass
    return serve(root)
