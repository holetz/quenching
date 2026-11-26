"""The published shape of the `quenching` server: one MCP tool per pillar and class.

The verb tables stay what they are — `catalog.CATALOG` and the specs adapter's `TOOLS`/`WRITES`,
keyed by the logical name `<pillar>_<verb>` (`git_state`, `specs_section_write`). This surface wraps
them and publishes only `<pillar>_<class>` (`git_read`, `specs_write`, `git_external`), each taking
`verb` — the logical name without its pillar — and that verb's own arguments beside it:

    git_state(root=X)            ->  git_read(verb="state", root=X)
    specs_section_write(...)     ->  specs_write(verb="section_write", ...)

* List: the tool's schema names `verb` (the enum of its class) and `root`; each verb's own schema is
  validated by the wrapped table on every call, and returned with a refused argument or on
  `verb="help"`, so the list stays small while every call is still checked.
* Annotations hold for the whole tool: read-only and idempotent only when every verb is, destructive
  and open-world when any verb is.
* Dispatch: the call goes to the wrapped surface under the logical name, so validation, the
  elicitation gate and the in-process run are the tables' own.
"""
from __future__ import annotations

from quenching.mcp import catalog, server

CLASSES = catalog.CLASSES
HELP = "help"
SUMMARY_CHARS = 60


def logical_class(name: str) -> str | None:
    """The class of one logical tool: its catalog row's, or the specs adapter's table's."""
    row = catalog.CATALOG.get(name)
    if row is not None:
        return row.cls
    from quenching.specs import mcp as specs_mcp
    if name in specs_mcp.TOOLS:
        return "read"
    if name in specs_mcp.WRITES:
        return "external" if name in specs_mcp.EXTERNAL else "write"
    return None


def split(name: str) -> tuple[str, str] | None:
    """`(pillar, verb)` of one logical name, or None when it is no tool of the catalog."""
    pillar = catalog.pillar_of(name)
    if pillar is None or not name.startswith(pillar + "_"):
        return None
    return pillar, name[len(pillar) + 1:]


def group_of(name: str) -> str | None:
    """The published tool that serves one logical name: `<pillar>_<class>`."""
    parts, cls = split(name), logical_class(name)
    return f"{parts[0]}_{cls}" if parts and cls else None


def logical(group: str, verb: str) -> str | None:
    """The logical name `verb` names inside `group`, or None when the group does not serve it."""
    pillar = group.rsplit("_", 1)[0]
    name = f"{pillar}_{verb}"
    return name if group_of(name) == group else None


def _summary(tool: dict) -> str:
    """One line per verb in the grouped description: the verb's own help, without its `cq` head
    and class tail."""
    text = tool.get("description") or ""
    if text.startswith("`cq "):
        text = text.split("` — ", 1)[1] if "` — " in text else ""
    text = text.split(" [class: ", 1)[0]
    text = catalog.first_sentence(text).rstrip(".")
    return text if len(text) <= SUMMARY_CHARS else text[:SUMMARY_CHARS - 1].rstrip() + "…"


def _annotations(tools: list[dict]) -> dict:
    hints = [tool.get("annotations") or {} for tool in tools]
    return {"readOnlyHint": all(h.get("readOnlyHint", False) for h in hints),
            "destructiveHint": any(h.get("destructiveHint", False) for h in hints),
            "idempotentHint": all(h.get("idempotentHint", False) for h in hints),
            "openWorldHint": any(h.get("openWorldHint", False) for h in hints)}


def describe(group: str, verbs: list[tuple[str, dict]]) -> dict:
    pillar, cls = group.rsplit("_", 1)
    lines = "; ".join(f"`{verb}` — {_summary(tool)}" if _summary(tool) else f"`{verb}`"
                      for verb, tool in verbs)
    return {
        "name": group,
        "description": (f"`cq {pillar}` {cls} verbs: pass `verb` and its own arguments beside it "
                        f"(`verb=\"help\"`, `of=<verb>`: its schema). {lines}."),
        "inputSchema": {
            "type": "object",
            "properties": {
                "verb": {"type": "string", "enum": [verb for verb, _ in verbs] + [HELP],
                         "description": "the verb to run"},
                "of": {"type": "string", "description": "help only: the one verb to describe"},
                "root": server.ROOT},
            "required": ["verb"],
            "additionalProperties": True},
        "annotations": _annotations([tool for _, tool in verbs])}


class GroupedSurface:
    """A surface (a `Composite` or one part) served as one tool per pillar and class."""

    def __init__(self, inner):
        self.inner = inner
        self.name = inner.name

    def _names(self) -> list[str]:
        """The logical names the wrapped surface serves, without describing a single one."""
        from quenching.specs import mcp as specs_mcp

        def walk(part) -> list[str]:
            if isinstance(part, server.Composite):
                return [name for child in part.parts for name in walk(child)]
            if isinstance(part, catalog.CatalogSurface):
                return list(part.tools())
            if part is specs_mcp.SURFACE:
                return [*specs_mcp.TOOLS, *specs_mcp.WRITES]
            return []
        return walk(self.inner)

    def groups(self) -> dict[str, list[str]]:
        """Each published tool and the logical names it serves, in the wrapped order."""
        out: dict[str, list[str]] = {}
        for name in self._names():
            group = group_of(name)
            if group is not None:
                out.setdefault(group, []).append(name)
        return out

    def has_tool(self, name: str) -> bool:
        return name in self.groups()

    def _described(self) -> dict[str, dict]:
        return {tool["name"]: tool for tool in self.inner.list_tools()}

    def list_tools(self) -> list[dict]:
        described = self._described()
        by_group: dict[str, list[tuple[str, dict]]] = {}
        for name, tool in described.items():
            group = group_of(name)
            if group is not None:
                by_group.setdefault(group, []).append((split(name)[1], tool))
        order = {pillar: i for i, pillar in enumerate(dict.fromkeys(
            group.rsplit("_", 1)[0] for group in by_group))}
        ranked = sorted(by_group, key=lambda g: (order[g.rsplit("_", 1)[0]],
                                                 CLASSES.index(g.rsplit("_", 1)[1])))
        return [describe(group, by_group[group]) for group in ranked]

    def _help(self, group: str, of) -> tuple[dict, bool]:
        names = self.groups()[group]
        if of is not None:
            name = logical(group, of) if isinstance(of, str) else None
            if name is None or name not in names:
                return self._unknown(group, of)
            names = [name]
        described = self._described()
        return {"ok": True, "tool": group,
                "verbs": [{"verb": split(name)[1],
                           "description": described[name].get("description", ""),
                           "inputSchema": described[name].get("inputSchema", {})}
                          for name in names if name in described]}, False

    def _unknown(self, group: str, verb) -> tuple[dict, bool]:
        verbs = [split(name)[1] for name in self.groups()[group]]
        return {"ok": False, "code": "mcp-unknown-verb",
                "message": f"`{group}` has no verb {verb!r}; pass one of `verbs`, or "
                           f"`verb=\"help\"` for their schemas",
                "verbs": verbs}, True

    def call_tool(self, name, args, root, session):
        if not isinstance(args, dict):
            return {"ok": False, "code": "mcp-bad-arguments",
                    "message": "`arguments` must be an object"}, True
        verb = args.get("verb")
        if verb == HELP:
            return self._help(name, args.get("of"))
        target = logical(name, verb) if isinstance(verb, str) else None
        if target is None or target not in self.groups()[name]:
            return self._unknown(name, verb)
        rest = {key: value for key, value in args.items() if key != "verb"}
        payload, failed = self.inner.call_tool(target, rest, root, session)
        if failed and isinstance(payload, dict) and payload.get("code") == "mcp-bad-arguments":
            tool = self._described().get(target)
            if tool is not None:
                payload = {**payload, "verb": verb, "inputSchema": tool.get("inputSchema")}
        return payload, failed

    def list_resources(self, root):
        return self.inner.list_resources(root)

    def resource_templates(self):
        return self.inner.resource_templates()

    def read_resource(self, uri, root):
        return self.inner.read_resource(uri, root)
