"""Repository-owned plugin distribution and published release surfaces."""
from __future__ import annotations

import json
from pathlib import Path, PurePosixPath

MANIFEST = "plugins/quenching/assets/modules.json"


def safe_path(root: Path, value: str) -> Path:
    """Keep both lexical paths and existing symlink ancestors inside the repository."""
    if not isinstance(value, str) or not value:
        raise ValueError("a distribution path must be a nonempty string")
    rel = PurePosixPath(value)
    if rel.is_absolute() or ".." in rel.parts or "\\" in value or str(rel) != value:
        raise ValueError(f"unsafe distribution path: {value}")
    path = root / value
    for parent in (path, *path.parents):
        if parent == root:
            break
        if parent.is_symlink():
            raise ValueError(f"symlink distribution path: {value}")
        if parent != path and parent.exists() and not parent.is_dir():
            raise ValueError(f"non-directory distribution ancestor: {value}")
    return path


def load_manifest(root: Path) -> dict:
    data = json.loads(safe_path(root, MANIFEST).read_text(encoding="utf-8"))
    if data.get("schemaVersion") != 1 or not isinstance(data.get("modules"), list):
        raise ValueError("unsupported module manifest schema")
    for field in ("source", "marketplace", "versionConstant"):
        safe_path(root, data[field])
    names, paths = set(), set()
    planned_owners = set()
    for module in data["modules"]:
        name, path = module["name"], module["path"]
        if not isinstance(name, str) or not name or name in names or path in paths:
            raise ValueError(f"duplicate or invalid module identity: {name}")
        names.add(name)
        paths.add(path)
        safe_path(root, path)
        for flag in ("published", "versionFile", "cqPathOwner"):
            if not isinstance(module.get(flag), bool):
                raise ValueError(f"{name}: {flag} must be boolean")
        if "owned" in module:
            for package in module["owned"]["packages"]:
                if package in planned_owners:
                    raise ValueError(f"duplicate planned package owner: {package}")
                planned_owners.add(package)
            for rel in module["owned"]["commands"]:
                safe_path(root / data["source"] / "commands", rel)
            support = module["generatedSupport"]
            for package in [*module["owned"]["packages"], *support["packages"]]:
                path_ = safe_path(root / data["source"] / "assets/bin/quenching", package)
                if not path_.is_dir():
                    raise ValueError(f"missing planned package source: {package}")
            for reference in support["references"]:
                path_ = safe_path(root / data["source"] / "assets/references", reference)
                if not path_.is_dir():
                    raise ValueError(f"missing planned reference source: {reference}")
        generated = module.get("generated")
        if generated is None:
            continue
        if path == data["source"]:
            raise ValueError("the editable source cannot be generated")
        trees = generated["trees"]
        authored = module["authored"]
        if not isinstance(trees, list) or not trees or not isinstance(authored, list):
            raise ValueError(f"{name}: declare generated trees and authored paths")
        files = generated.get("files", [])
        owned = [*trees, *files, "VERSION", ".claude-plugin/plugin.json", ".generated-from.json"]
        for rel in [*owned, *authored]:
            safe_path(root / path, rel)
        for index, rel in enumerate(owned):
            for other in [*owned[index + 1:], *authored]:
                if rel == other or rel.startswith(other + "/") or other.startswith(rel + "/"):
                    raise ValueError(f"{name}: overlapping ownership: {rel}, {other}")
        for tree in trees:
            source = safe_path(root / data["source"], tree)
            if not source.is_dir():
                raise ValueError(f"missing generated source tree: {tree}")
            for child in source.rglob("*"):
                if child.is_symlink():
                    raise ValueError(f"symlink generated source: {child}")
            target = safe_path(root / path, tree)
            if target.exists() and not target.is_dir():
                raise ValueError(f"generated target is not a directory: {target}")
            for child in target.rglob("*"):
                if child.is_symlink():
                    raise ValueError(f"symlink generated target: {child}")
        for rel in files:
            if not safe_path(root / data["source"], rel).is_file():
                raise ValueError(f"missing generated source file: {rel}")
    published = [m for m in data["modules"] if m["published"]]
    if sum(m["cqPathOwner"] for m in published) != 1:
        raise ValueError("published modules must declare exactly one PATH cq owner")
    planned = [m for m in data["modules"] if not m["published"] and "owned" in m]
    if planned and sum(m["cqPathOwner"] for m in planned) != 1:
        raise ValueError("planned modules must declare exactly one future PATH cq owner")
    principal = [m for m in data["modules"] if "owned" in m]
    active = {m["published"] for m in principal}
    if len(active) > 1:
        raise ValueError("principal modules are activated together or not at all")
    source_published = data["source"] in {m["path"] for m in published}
    if active == {True} and source_published:
        raise ValueError("the editable source cannot stay published beside the principal modules")
    if active != {True} and not source_published:
        raise ValueError("the editable source must be a published module")
    for left in paths:
        for right in paths - {left}:
            if left.startswith(right + "/"):
                raise ValueError(f"overlapping module roots: {left}, {right}")
    return data


def release_artifacts(manifest: dict) -> tuple[tuple[str, str], ...]:
    artifacts = []
    for module in manifest["modules"]:
        if module["published"]:
            if module["versionFile"]:
                artifacts.append((module["path"] + "/VERSION", "plain"))
            artifacts.append((module["path"] + "/.claude-plugin/plugin.json", "json"))
    return tuple(artifacts + [(manifest["marketplace"], "jsonall"),
                              (manifest["versionConstant"], "py")])


def namespace_map(root: Path, manifest: dict) -> dict[str, str]:
    """Map each `quenching:<head>` id head (a command front, root command or agent) to its module."""
    source = root / manifest["source"]
    mapping = {}
    for module in manifest["modules"]:
        owned = module.get("owned")
        if not owned:
            continue
        heads = [rel.removesuffix(".md") for rel in owned["commands"]]
        if owned["agents"]:
            heads += sorted(p.stem for p in (source / "agents").glob("*.md"))
        for head in heads:
            if head in mapping:
                raise ValueError(f"duplicate namespace head: {head}")
            mapping[head] = module["name"]
    return mapping


def published_id(old: str, mapping: dict[str, str]) -> str:
    """`quenching:<front>:<verb>` -> `quenching-<module>:<front>:<verb>`; unknown heads are refused."""
    plugin, _, rest = old.partition(":")
    head = rest.split(":", 1)[0]
    if plugin != "quenching" or head not in mapping:
        raise ValueError(f"no module owns {old}")
    return f"{mapping[head]}:{rest}"
