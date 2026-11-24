"""Catalog coverage: every `cq <pillar> <verb>` a skill, agent or reference body cites has an MCP tool.

A citation's verb path is what the pillar's own parser consumes — subparsers, and positionals whose
`choices` carry the word (`git worktree acquire`, `security leak`) — stopping at the first word that
is not a verb. A citation that ends on a group (`cq specs`, `cq git pr`) or on an unfilled
`choices` positional names no verb: it is prose, and is not counted. A covered verb is a catalog
row, a hand-written specs tool (`specs.mcp.COVERS`), or an entry of `EXCEPTIONS`, each with its
reason.
"""
from __future__ import annotations

import os
import re
from typing import Iterable

from quenching.mcp import catalog

# Top-level verbs of the `cq` router that are not pillars: they pass only through EXCEPTIONS.
ROUTER_VERBS = ("deploy", "modules")

EXCEPTIONS: dict[tuple[str, ...], str] = {
    ("deploy",): "installs the surface into a target; the operator runs it",
    ("modules",): "`tools/list` already answers which pillars are present",
    ("mcp",): "the server itself",
    ("specs", "mcp"): "the specs-only mount of the server itself",
    ("specs", "serve"): "long-running local portal",
    ("portal", "serve"): "long-running central portal",
    ("codex", "implement"): "long-running per-task executor",
    ("specs", "migrate"): "one-time store migration the operator runs; may create remote work items",
    ("specs", "export"): "writes a directory of files outside the store, for the operator",
    ("specs", "claim", "take"): "taking a live lease is the human's call only; no agent grant may reach it",
}

# The bodies the coverage holds for, relative to the plugin root (`quenching/`): the references
# the bodies load cite verbs too.
SOURCES = ("skills", "agents", "references")

CITE = re.compile(r"\bcq(?:\.cmd)?((?:[ \t]+[a-z][a-z0-9-]*)+)")


def _unfilled_choice(parser, filled: set) -> bool:
    return any(not a.option_strings and a.choices and a.dest not in filled
               for a in parser._actions)


def verb_path(words: list[str]) -> tuple[str, ...] | None:
    """`(pillar, *verb)` for one citation's words, or None when they name no verb."""
    if not words:
        return None
    if words[0] in ROUTER_VERBS:
        return (words[0],)
    if words[0] not in catalog.router().PILLARS:
        return None
    parser, path, filled = catalog._pillar_parser(words[0]), [words[0]], set()
    for word in words[1:]:
        subs = catalog._subparsers(parser)
        if subs is not None and word in subs.choices:
            parser = subs.choices[word]
            path.append(word)
            continue
        slot = next((a for a in parser._actions if not a.option_strings
                     and a.dest not in filled and a.choices and word in a.choices), None)
        if slot is None:
            break
        filled.add(slot.dest)
        path.append(word)
    if catalog._subparsers(parser) is not None or _unfilled_choice(parser, filled):
        return None
    return tuple(path)


def covered() -> set[tuple[str, ...]]:
    from quenching.specs import mcp as specs_mcp
    return ({(row.pillar, *row.path) for row in catalog.CATALOG.values()}
            | {("specs", *path) for path in specs_mcp.COVERS.values()}
            | set(EXCEPTIONS))


# A verb no generated grant may reach, through a tool or through the shell residue below.
DENIED = {("specs", "claim", "take")}


def _children(parser, path: tuple[str, ...]) -> list[tuple[tuple[str, ...], object]]:
    """The verb words under one parser: its subparsers, else its first `choices` positional."""
    subs = catalog._subparsers(parser)
    if subs is not None:
        return [((*path, word), sub) for word, sub in subs.choices.items()]
    slot = next((a for a in parser._actions if not a.option_strings and a.choices), None)
    return [((*path, str(word)), None) for word in slot.choices] if slot is not None else []


def _residue(path: tuple[str, ...], parser, tools: set) -> tuple[list[tuple[str, ...]], bool]:
    """`(paths, whole)`: the fewest verb paths under `path` a tool does not cover, and whether
    `path` itself is one of them — nothing below it covered nor denied, so one grant holds it."""
    if path in DENIED or path in tools:
        return [], False
    children = _children(parser, path) if parser is not None else []
    if not children:
        return [path], True
    out, whole = [], True
    for child, sub in children:
        paths, child_whole = _residue(child, sub, tools)
        out.extend(paths)
        whole = whole and child_whole
    return ([path], True) if whole else (out, False)


def cli_residue(prefix: tuple[str, ...]) -> list[tuple[str, ...]] | None:
    """The fewest verb paths under a `cq <prefix…>` grant that no MCP tool covers: the shell
    grants a narrowed deploy keeps. `EXCEPTIONS` count as uncovered, `DENIED` is never reached,
    and an empty prefix is the whole router. `None` when the prefix names no verb path, so the
    caller keeps the grant it cannot reason about."""
    from quenching.specs import mcp as specs_mcp
    tools = ({(row.pillar, *row.path) for row in catalog.CATALOG.values()}
             | {("specs", *path) for path in specs_mcp.COVERS.values()})
    if not prefix:
        out: list[tuple[str, ...]] = [(verb,) for verb in (*ROUTER_VERBS, "mcp")]
        for pillar in catalog.router().PILLARS:
            out.extend(path for path in cli_residue((pillar,)) or [] if path not in out)
        return out
    if prefix[0] in ROUTER_VERBS or prefix == ("mcp",):
        return [prefix]
    if prefix[0] not in catalog.router().PILLARS:
        return None
    parser, path = catalog._pillar_parser(prefix[0]), (prefix[0],)
    for word in prefix[1:]:
        child = next(((p, sub) for p, sub in _children(parser, path) if p[-1] == word), None)
        if child is None:
            return None
        path, parser = child
    # A tool on an ancestor covers everything under it.
    if any(prefix[:n] in tools for n in range(1, len(prefix))):
        return []
    return _residue(prefix, parser, tools)[0]


def uncovered(texts: Iterable[tuple[str, str]]) -> list[tuple[str, tuple[str, ...]]]:
    """`(label, verb path)` for every citation in `texts` (`(label, text)` pairs) no tool covers."""
    known, out = covered(), []
    for label, text in texts:
        for match in CITE.finditer(text):
            path = verb_path(match.group(1).split())
            if path is not None and path not in known and (label, path) not in out:
                out.append((label, path))
    return out


def bodies(plugin_root: str) -> list[tuple[str, str]]:
    """`(relative path, text)` of every markdown body under `SOURCES`."""
    out = []
    for source in SOURCES:
        for base, dirs, files in os.walk(os.path.join(plugin_root, source)):
            dirs.sort()
            for name in sorted(files):
                if name.endswith(".md"):
                    path = os.path.join(base, name)
                    with open(path, encoding="utf-8") as handle:
                        out.append((os.path.relpath(path, plugin_root), handle.read()))
    return out
