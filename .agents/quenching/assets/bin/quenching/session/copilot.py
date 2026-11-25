"""What a GitHub Copilot session spent, read from the two files the client keeps on disk.

`$COPILOT_HOME` (default `~/.copilot`) holds a **ledger** and a **log**, each for what only it has:

- `session-store.db` — `sessions` gives every session's cwd and timestamps, and
  `assistant_usage_events` is one row per request with the model, the token counts, the `agent_id`,
  `total_nano_aiu` and `request_multiplier`. Opened read-only; `sessions.summary` and the `turns`
  table hold message content and are never selected.
- `session-state/<id>/` — `events.jsonl` names each subagent (`subagent.started`) and links it to the
  tool call that launched it (the `tool.execution_start` of that call carries the parent's
  `agentId`; no `agentId` is the main agent), and `workspace.yaml` records the cwd, the git root and
  the client that wrote the session. The agent UUID is the one key the two share.

`inputTokens` is the whole prompt and `cacheReadTokens` is a subset of it — measured on every
record this machine produced, where the read never exceeds the total and the median ratio is 0.99,
and corroborated by the same record's `requestBodyBytes`. A request's **fresh input** is therefore
the difference, clamped at zero; the arithmetic inverting is an anomaly, never a silent zero."""

from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import NamedTuple

from quenching.session.commands.cost import parse_instant

HOME_ENV = "QUENCHING_COPILOT_HOME"
STORE = "session-store.db"
STATE = "session-state"
TABLES = ("sessions", "assistant_usage_events")
UNKNOWN = "unknown"
USAGE_COLUMNS = ("agent_id, model, input_tokens, output_tokens, cache_read_tokens, "
                 "cache_write_tokens, reasoning_tokens, total_nano_aiu, created_at")


class CopilotError(Exception):
    """A refusal the commands turn into `{code, message}`."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code, self.message = code, message


class Request(NamedTuple):
    """One request as the client's ledger records it: the prompt total, its cache subset, output."""

    session: str
    agent_id: str | None
    model: str
    at: datetime | None
    input: int
    cache_read: int
    cache_write: int
    output: int
    reasoning: int
    nano_aiu: int | None

    @property
    def fresh(self) -> int:
        """The prompt tokens the cache did not serve."""
        return max(0, self.input - self.cache_read - self.cache_write)


def home(explicit: str | None = None) -> Path:
    """The client's home: an explicit path, the quenching override, the client's own, else `~`."""
    for candidate in (explicit, os.environ.get(HOME_ENV), os.environ.get("COPILOT_HOME")):
        if candidate:
            return Path(candidate).expanduser()
    return Path.home() / ".copilot"


def wants_copilot(arg: str | None, explicit_home: str | None) -> bool:
    """Whether `cost`/`cache` is asked for the Copilot store: a home named, or the running client's.

    The client exports `COPILOT_HOME` to every child process, so inside a Copilot session the
    unasked default is that session — the same rule `OPENCODE_SESSION_ID` gives OpenCode."""
    return bool(explicit_home or os.environ.get(HOME_ENV) or os.environ.get("COPILOT_HOME"))


def store(root: Path) -> Path:
    return root / STORE


def _connect(root: Path) -> sqlite3.Connection:
    """The ledger, read-only. A missing file or table is a named refusal, never an empty answer."""
    path = store(root)
    if not path.is_file():
        raise CopilotError("se-no-transcript", f"no Copilot session store at {path}")
    try:
        db = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
        found = {row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}
    except sqlite3.Error as error:
        raise CopilotError("se-unreadable-transcript", f"{path}: {error}") from error
    if not set(TABLES) <= found:
        db.close()
        raise CopilotError("se-no-transcript", f"{path} has no Copilot usage ledger "
                            f"(needs {' and '.join(TABLES)}) — this reader knows no other schema")
    return db


def _n(value) -> int:
    return value if isinstance(value, int) and not isinstance(value, bool) else 0


def sessions(root: Path) -> dict:
    """Session id -> `{cwd, gitRoot, client, created, updated}` with no content selected."""
    db = _connect(root)
    try:
        rows = {row[0]: {"cwd": row[1], "created": parse_instant(row[2]), "updated": parse_instant(row[3])}
                for row in db.execute("SELECT id, cwd, created_at, updated_at FROM sessions")}
    except sqlite3.Error as error:
        raise CopilotError("se-unreadable-transcript", f"{store(root)}: {error}") from error
    finally:
        db.close()
    for sid in rows:
        rows[sid].update(_workspace(root, sid))
    return rows


def in_scope(row: dict, directory: Path) -> bool:
    """Whether a session belongs to `directory`: its cwd is it or inside it, or its git root is it.

    The git root is what keeps a spec's slot worktree in the checkout that cut it, as the Claude
    branch's nearest-ancestor walk does."""
    cwd = row.get("cwd")
    if isinstance(cwd, str) and cwd:
        here = Path(cwd)
        if here == directory or directory in here.parents:
            return True
    root = row.get("gitRoot")
    return isinstance(root, str) and bool(root) and Path(root) == directory


def resolve(root: Path, arg: str | None, cwd: Path) -> tuple[str, str]:
    """(session id, how it was found): the named session, or the most recent one for this cwd."""
    known = sessions(root)
    if arg:
        if arg not in known:
            raise CopilotError("se-no-transcript", f"no Copilot session {arg} in {store(root)}")
        return arg, "Copilot session id"
    inside = {sid: row for sid, row in known.items() if in_scope(row, cwd)}
    if not inside:
        raise CopilotError("se-no-transcript", f"no Copilot session for {cwd} in {store(root)}")
    floor = datetime.min.replace(tzinfo=timezone.utc)
    newest = max(inside, key=lambda sid: (inside[sid].get("updated") or floor,
                                          inside[sid].get("created") or floor))
    return newest, "most recent Copilot session in this directory"


def requests(root: Path, session_ids: list[str], since: datetime | None = None) -> tuple[dict, list]:
    """Session id -> its requests, oldest first, plus the anomalies of the read."""
    db = _connect(root)
    anomalies: list = []
    out: dict = {sid: [] for sid in session_ids}
    try:
        marks = ",".join("?" for _ in session_ids) or "''"
        rows = db.execute(f"SELECT session_id, {USAGE_COLUMNS} FROM assistant_usage_events "  # noqa: S608 — fixed columns
                          f"WHERE session_id IN ({marks}) ORDER BY created_at, id", session_ids)
        for sid, agent_id, model, inp, out_tokens, read, write, reasoning, nano, created in rows:
            when = parse_instant(created)
            if since is not None:
                if when is None:
                    anomalies.append({"file": STORE, "line": 0,
                                      "message": "a request has no parsable timestamp and is not counted under --since"})
                    continue
                if when < since:
                    continue
            request = Request(sid, agent_id if isinstance(agent_id, str) and agent_id else None,
                              model if isinstance(model, str) and model else UNKNOWN, when,
                              _n(inp), _n(read), _n(write), _n(out_tokens), _n(reasoning),
                              nano if isinstance(nano, int) and not isinstance(nano, bool) and nano >= 0 else None)
            if request.cache_read + request.cache_write > request.input:
                anomalies.append({"file": STORE, "line": 0, "message":
                                  "a request reports more cache tokens than prompt tokens; its fresh "
                                  "input reads as zero"})
            out[sid].append(request)
    except sqlite3.Error as error:
        raise CopilotError("se-unreadable-transcript", f"{store(root)}: {error}") from error
    finally:
        db.close()
    return out, anomalies


def _workspace(root: Path, session: str) -> dict:
    """The flat `key: value` fields of `workspace.yaml`; a block scalar is skipped, not parsed."""
    path = root / STATE / session / "workspace.yaml"
    found: dict = {}
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return found
    for line in lines:
        if not line or line[0].isspace() or ":" not in line:
            continue
        key, _, value = line.partition(":")
        value = value.strip()
        if key in ("cwd", "git_root", "client_name", "last_client_name") and value \
                and not value.startswith(("|", ">")):
            found[{"git_root": "gitRoot", "client_name": "client",
                   "last_client_name": "client"}.get(key, key)] = value
    return found


def events(root: Path, session: str) -> tuple[dict, dict]:
    """(agents by id, the session's own facts) from its event log, with the read's anomalies.

    Each agent carries `name`, `parent` — the `agentId` of the tool call that launched it, absent
    for one the main agent launched — `start` and `end`. `facts` names the client that wrote the
    session, its `cwd` and `gitRoot`, and `producer`. A missing log is a fact (the agents stay
    unnamed and unparented), not a refusal: the ledger still measures the requests."""
    path = root / STATE / session / "events.jsonl"
    agents: dict = {}
    launches: dict = {}
    tools: dict = {}
    facts: dict = {"client": None, "cwd": None, "gitRoot": None, "producer": None, "anomalies": []}
    if not path.is_file():
        facts["anomalies"].append({"file": path.name, "line": 0,
                                   "message": f"no event log at {path}; agents stay unnamed and unparented"})
        return agents, facts
    try:
        stream = path.open(encoding="utf-8", errors="replace")
    except OSError as error:
        facts["anomalies"].append({"file": path.name, "line": 0, "message": f"unreadable event log: {error}"})
        return agents, facts
    with stream:
        for line, raw in enumerate(stream, 1):
            if not raw.strip():
                continue
            try:
                record = json.loads(raw)
            except ValueError:
                facts["anomalies"].append({"file": path.name, "line": line, "message": "unparsable record"})
                continue
            if not isinstance(record, dict):
                facts["anomalies"].append({"file": path.name, "line": line,
                                           "message": "record is not a JSON object"})
                continue
            kind, data = record.get("type"), record.get("data")
            data = data if isinstance(data, dict) else {}
            agent = record.get("agentId") if isinstance(record.get("agentId"), str) else None
            if kind == "session.start":
                facts["producer"] = data.get("producer") if isinstance(data.get("producer"), str) else None
                context = data.get("context") if isinstance(data.get("context"), dict) else {}
                for key in ("cwd", "gitRoot"):
                    if isinstance(context.get(key), str) and context[key]:
                        facts[key] = context[key]
            elif kind == "tool.execution_start":
                call = data.get("toolCallId")
                if isinstance(call, str):
                    tools[call] = agent
            elif kind == "subagent.started":
                child = record.get("agentId")
                if isinstance(child, str):
                    name = data.get("agentName") or data.get("agentType")
                    agents[child] = {"name": name if isinstance(name, str) and name else None,
                                     "parent": None, "start": parse_instant(record.get("timestamp")),
                                     "end": None}
                    call = data.get("toolCallId")
                    if isinstance(call, str):
                        launches[child] = call
            elif kind == "subagent.completed":
                child = record.get("agentId")
                if isinstance(child, str) and child in agents:
                    agents[child]["end"] = parse_instant(record.get("timestamp"))
    for child, call in launches.items():
        agents[child]["parent"] = tools.get(call)
    workspace = _workspace(root, session)
    facts["client"] = workspace.get("client")
    facts["cwd"] = facts["cwd"] or workspace.get("cwd")
    facts["gitRoot"] = facts["gitRoot"] or workspace.get("gitRoot")
    return agents, facts


def agent_name(agent_id: str | None, agents: dict) -> str:
    """The name for a request's `agent_id`: `main` without one, else the log's name or `unknown <id>`."""
    if agent_id is None:
        return "main"
    found = agents.get(agent_id, {}).get("name")
    return found if found else f"{UNKNOWN} {agent_id[:8]}"


def descendant_ids(agents: dict, root_agent: str) -> list[str]:
    """Every agent launched, directly or not, by `root_agent` — the tree as the log recorded it."""
    children: dict = {}
    for agent_id, row in agents.items():
        children.setdefault(row.get("parent"), []).append(agent_id)
    out, queue = [], [root_agent]
    while queue:
        parent = queue.pop()
        for child in children.get(parent, []):
            out.append(child)
            queue.append(child)
    return out
