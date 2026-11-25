"""The citation form a body uses for a `cq` verb: the MCP tool, with named arguments.

`align/tool-resolution.md` §Citing a verb in a body owns the rule. Two findings hold it, inside the
bodies `ENFORCED` names:

* `sk-cq-cli-citation` — a `cq <pillar> <verb>` whose verb has a tool (a catalog row or a
  hand-written specs tool), on a line no `cli: <reason>` marker covers. A verb with no tool — an
  `EXCEPTIONS` entry of `mcp/coverage.py`, or one no row publishes — is the CLI's by right.
* `sk-mcp-unknown-tool` — a `<pillar>_<verb>(` citation that is no tool of the catalog.

`ENFORCED` is a ratchet: every quenching skill, every shared reference and every flow agent under
`agents/` is held to it, and the tuple stays as the one place a new body class would be added.
`skills/quenching-` keeps a target's own skills, which quenching does not author, out of it.
"""
from __future__ import annotations

import re

from quenching.common.output import finding
from quenching.mcp import catalog, coverage

# Path fragments, relative to the plugin root or to a target's `.agents/`, of the bodies held to
# the tool form. `agents/` is the flow agents' own folder; `references/` is the shared payload's: a skill's own `references/` is reached
# through its `skills/quenching-` folder, and a target's own skill never is.
ENFORCED = ("skills/quenching-", "references/", "agents/")

# The one body whose job is to spell the CLI: the fallback of the convention itself.
CLI_HOMES = ("references/align/tool-resolution.md",)

MARK = re.compile(r"(?:<!--\s*cli:\s*\S[^>]*-->|#\s*cli:\s*\S)")
MARK_LINE = re.compile(r"^\s*<!--\s*cli:\s*\S[^>]*-->\s*$")
FENCE = re.compile(r"^\s*(```|~~~)")


def enforced(path: str) -> bool:
    path = path.replace("\\", "/")
    if any(path.endswith(home) for home in CLI_HOMES):
        return False
    return any(path.startswith(frag) or f"/{frag}" in path if frag.startswith("skills/")
               else path.startswith(frag) or f"/quenching/{frag}" in path for frag in ENFORCED)


def tool_paths() -> dict[tuple[str, ...], str]:
    """`(pillar, *verb) -> tool name` for every verb a tool covers."""
    from quenching.specs import mcp as specs_mcp
    out = {(row.pillar, *row.path): name for name, row in catalog.CATALOG.items()}
    for name, path in specs_mcp.COVERS.items():
        out.setdefault(("specs", *path), name)
    return out


def tool_names() -> set[str]:
    from quenching.specs import mcp as specs_mcp
    return set(catalog.CATALOG) | set(specs_mcp.COVERS)


def _tool_call_re() -> re.Pattern:
    pillars = sorted({row.pillar for row in catalog.CATALOG.values()})
    return re.compile(r"(?<![\w.])((?:%s)_[a-z0-9_]+)\(" % "|".join(pillars))


def exempt_lines(lines: list[str]) -> set[int]:
    """0-based indexes of the lines a `cli:` marker covers: its own line, or — a marker alone on
    its line — the paragraph or fenced block that follows it."""
    out: set[int] = set()
    i = 0
    while i < len(lines):
        line = lines[i]
        if MARK_LINE.match(line):
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            if j < len(lines) and FENCE.match(lines[j]):
                out.add(j)
                j += 1
                while j < len(lines) and not FENCE.match(lines[j]):
                    out.add(j)
                    j += 1
                out.add(j)
            else:
                while j < len(lines) and lines[j].strip():
                    out.add(j)
                    j += 1
            out.add(i)
            i = j
            continue
        if MARK.search(line):
            out.add(i)
        i += 1
    return out


def findings(body: str, where: dict) -> list[dict]:
    """The citation-form findings of one body; `where["path"]` decides whether it is enforced."""
    if not enforced(str(where.get("path", ""))):
        return []
    tools, known, call_re = tool_paths(), tool_names(), _tool_call_re()
    lines = body.splitlines()
    skip = exempt_lines(lines)
    out: list[dict] = []
    for index, line in enumerate(lines):
        number = index + 1
        if index not in skip:
            for match in coverage.CITE.finditer(line):
                try:
                    path = coverage.verb_path(match.group(1).split())
                except ImportError:
                    # A pillar this install does not ship (a core-only target citing
                    # `cq security`) publishes no tool here, so the CLI form stands.
                    path = None
                if path is None or path not in tools:
                    continue
                cited = "cq " + " ".join(path)
                out.append(finding(
                    "sk-cq-cli-citation", "error",
                    f"`{cited}` at body line {number}: cite the tool, `{tools[path]}(…)` "
                    "(align/tool-resolution.md §Citing a verb in a body), or mark the line "
                    "`cli: <root|atomic|by|flag|fallback>`",
                    invocation=cited, line=number, **where))
        for match in call_re.finditer(line):
            if match.group(1) not in known:
                out.append(finding(
                    "sk-mcp-unknown-tool", "error",
                    f"`{match.group(1)}(` at body line {number} is no tool of the catalog",
                    invocation=match.group(1), line=number, **where))
    return out
