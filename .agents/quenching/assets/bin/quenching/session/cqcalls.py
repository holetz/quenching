"""Which `cq` calls of a session went through the shell and which through the MCP server.

Both are read off the transcript, never recalled: a `Bash` whose command runs `cq <verb>` is a shell
call, and a call to a `quenching` MCP tool — `mcp__quenching__<tool>` in Claude Code,
`quenching_<tool>` in OpenCode, `tools.quenching.<tool>(` inside a Code Mode `execute` — is an MCP
call. A shell call is reduced to the verb path the catalog coverage scan uses
(`quenching.mcp.coverage.verb_path`), so `cq git worktree acquire` is one verb and a bare `cq specs`
in prose is none. A published `<pillar>_<class>` tool is counted under the logical name its `verb`
argument names (`git_read` with `verb="state"` is `git_state`), so the tally keeps one entry per verb.

"Connected" is the one fact a transcript proves: the session made at least one MCP call to the
server. `connected: false` therefore means no MCP call was seen, not that the server was absent, and
only a connected session reports `fellToShell` — the verbs that have a tool and ran as `cq` anyway.
"""
from __future__ import annotations

import re

# `cq` as a word, optionally behind a path (`.agents/quenching/bin/cq`) and the global `--root`,
# followed by the lowercase words a verb path is made of.
SHELL_CQ = re.compile(
    r"(?:^|[\s;&|(`'\"=/])cq(?:\.cmd)?(?:[ \t]+--root[ \t]+\S+)?((?:[ \t]+[a-z][a-z0-9-]*)+)")
MCP_NAME = re.compile(r"^(?:mcp__quenching__|quenching_)(?P<tool>[A-Za-z0-9_]+)$")
CODE_MODE = re.compile(r"tools\.quenching(?:\.([A-Za-z_]\w*)|\[\s*[\"']([\w-]+)[\"']\s*\])")
# The `verb` of a Code Mode call, read from the object literal that opens its arguments.
CODE_MODE_VERB = re.compile(r"\s*\(\s*\{[^{}]*?\bverb[\"']?\s*:\s*[\"'](\w+)[\"']")
CLASSES = ("read", "write", "external")


def logical(tool: str, verb: object) -> str:
    """The logical name one call serves: `<pillar>_<verb>` for a published `<pillar>_<class>` tool
    called with a `verb`, else the tool name itself (a per-verb name, or `verb="help"`)."""
    pillar, _, cls = tool.rpartition("_")
    if pillar and cls in CLASSES and isinstance(verb, str) and verb and verb != "help":
        return f"{pillar}_{verb}"
    return tool


def shell_verbs(command: str | None) -> list[tuple[str, ...]]:
    """The `(pillar, *verb)` of every `cq` call in one shell command line."""
    if not isinstance(command, str):
        return []
    out = []
    for match in SHELL_CQ.finditer(command):
        words = match.group(1).split()
        path = _verb_path(words)
        if path:
            out.append(path)
    return out


def _verb_path(words: list[str]) -> tuple[str, ...] | None:
    try:
        from quenching.mcp import coverage
        return coverage.verb_path(words)
    except Exception:       # the router cannot load here: the first two words still name the verb
        return tuple(words[:2]) if len(words) >= 2 else None


def code_mode_tools(code: str | None) -> list[str]:
    """The `quenching` tools a Code Mode script calls, in order."""
    if not isinstance(code, str):
        return []
    out = []
    for match in CODE_MODE.finditer(code):
        verb = CODE_MODE_VERB.match(code, match.end())
        out.append(logical((match.group(1) or match.group(2)).replace("-", "_"),
                           verb.group(1) if verb else None))
    return out


def mcp_tools(name: str | None, inp: dict | None) -> list[str]:
    """The `quenching` MCP tools one `tool_use` block calls."""
    found = MCP_NAME.match(name or "")
    if found:
        return [logical(found.group("tool"), (inp or {}).get("verb"))]
    return code_mode_tools((inp or {}).get("code"))


def tally(into: dict, key: str, count: int = 1) -> None:
    into[key] = into.get(key, 0) + count


def _served() -> set:
    """The verb paths an MCP tool serves, the by-decision exceptions left out."""
    try:
        from quenching.mcp import coverage
        return coverage.covered() - set(coverage.EXCEPTIONS)
    except Exception:
        return set()


def summarize(shell: dict, mcp: dict, connected: bool | None = None) -> dict:
    """One scope's report: counts, the connected reading and the verbs that fell to the shell.

    `connected` is the session's reading when the scope is one command of it; left out, the scope's
    own MCP calls decide."""
    served = _served()
    if connected is None:
        connected = sum(mcp.values()) > 0
    fell, kept = {}, {}
    for verb, count in shell.items():
        path = tuple(verb.split())
        if connected and path in served:
            fell[verb] = count
        elif path not in served:
            kept[verb] = count
    shell_calls, mcp_calls = sum(shell.values()), sum(mcp.values())
    total = shell_calls + mcp_calls
    order = lambda d: dict(sorted(d.items(), key=lambda kv: (-kv[1], kv[0])))  # noqa: E731
    return {
        "shellCalls": shell_calls, "mcpCalls": mcp_calls,
        "shellRatio": round(shell_calls / total, 3) if total else None,
        "connected": connected,
        "shell": order(shell), "mcp": order(mcp),
        "fellToShell": order(fell), "cliByDesign": order(kept),
        "connectedBy": "an MCP call to the quenching server was seen in this scope",
    }
