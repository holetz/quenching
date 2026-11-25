"""`cq mcp` — the whole `quenching` MCP server over stdio.

    cq [--root PATH] mcp [--only <pillars>]

The server is the references resources plus the catalog of CLI verbs (with the specs tools when
the `specs` pillar is present). The workspace is the cwd it is launched in, or `--root`; one call
names another tree with its `root` argument. `cq specs mcp` stays the specs-only mount of the same
core, and `--only` publishes just the pillars it names, which is what a named mount such as `core`
expands to in the registered `.mcp.json`.
"""
from __future__ import annotations

import json
import os

from quenching.common.output import CQArgumentParser
from quenching.mcp import catalog, resources, server


def build_parser() -> CQArgumentParser:
    parser = CQArgumentParser(
        prog="cq mcp",
        description="serve the quenching MCP server over stdio: the catalogued verbs as tools "
                    "and every skill's references as quenching://references/ resources")
    parser.add_argument("--root", help="the workspace the tools run in (default: current directory)")
    parser.add_argument("--only", metavar="PILLARS",
                        help="publish only these pillars, comma-separated "
                             "(e.g. specs,git,components); the default publishes every one present")
    return parser


def only_pillars(value: str | None) -> tuple[tuple[str, ...] | None, dict | None]:
    """The pillars `--only` names, and the refusal when one of them names no routed pillar."""
    if value is None:
        return None, None
    names = tuple(part.strip() for part in value.split(",") if part.strip())
    unknown = catalog.mount_refusal(",".join(names))
    if unknown:
        return None, {"ok": False, "code": "ct-mcp-only",
                      "message": f"`--only` names no pillar this process routes: "
                                 f"{', '.join(unknown)}",
                      "pillars": sorted(catalog.router().PILLARS), "only": value}
    return names, None


def surface(present=None, only=None) -> server.Composite:
    return server.Composite("quenching", [resources.ReferencesSurface(),
                                          catalog.surface(present, only)])


def main(argv: list[str]) -> int:
    args = build_parser().parse_args(argv)
    only, refusal = only_pillars(args.only)
    if refusal:
        print(json.dumps(refusal, ensure_ascii=False))
        return 2
    return server.run_stdio(os.path.abspath(args.root or os.getcwd()), surface(only=only))
