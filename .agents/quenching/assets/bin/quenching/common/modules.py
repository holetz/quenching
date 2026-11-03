"""The deploy manifest (`assets/modules.json`): installable modules, the plugins that are not
installed into a repository, and the release surfaces that carry the version."""
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
    """The deploy manifest: the modules `cq deploy` installs, and the few plugins that are not."""
    data = json.loads(safe_path(root, MANIFEST).read_text(encoding="utf-8"))
    if data.get("schemaVersion") != 2 or not isinstance(data.get("modules"), list):
        raise ValueError("unsupported module manifest schema")
    for field in ("source", "marketplace", "versionConstant"):
        safe_path(root, data[field])
    names = set()
    planned_owners = set()
    for module in data["modules"]:
        name = module["name"]
        if not isinstance(name, str) or not name or name in names:
            raise ValueError(f"duplicate or invalid module identity: {name}")
        names.add(name)
        if not isinstance(module["owned"].get("mcp", False), bool):
            raise ValueError(f"{name}: owned.mcp must be boolean")
        for package in module["owned"]["packages"]:
            if package in planned_owners:
                raise ValueError(f"duplicate package owner: {package}")
            planned_owners.add(package)
        for rel in module["owned"]["commands"]:
            safe_path(root / data["source"] / "commands", rel)
        support = module["generatedSupport"]
        for package in [*module["owned"]["packages"], *support["packages"]]:
            if not safe_path(root / data["source"] / "assets/bin/quenching", package).is_dir():
                raise ValueError(f"missing package source: {package}")
        for reference in support["references"]:
            if not safe_path(root / data["source"] / "assets/references", reference).is_dir():
                raise ValueError(f"missing reference source: {reference}")
    plugins = data.get("plugins", [])
    if not isinstance(plugins, list):
        raise ValueError("plugins must be a list")
    paths = {data["source"]}
    for plugin in plugins:
        name, path = plugin.get("name"), plugin.get("path")
        if not isinstance(name, str) or not name or name in names or path in paths:
            raise ValueError(f"duplicate or invalid plugin identity: {name}")
        names.add(name)
        paths.add(path)
        safe_path(root, path)
        if not isinstance(plugin.get("marketplace"), bool):
            raise ValueError(f"{name}: marketplace must be boolean")
    return data


def release_artifacts(manifest: dict) -> tuple[tuple[str, str], ...]:
    """Every file that carries the release version: the source, the marketplace plugins, the
    marketplace catalog and the `cq` version constant."""
    source = manifest["source"]
    artifacts = [(source + "/VERSION", "plain"), (source + "/.claude-plugin/plugin.json", "json")]
    artifacts += [(plugin["path"] + "/.claude-plugin/plugin.json", "json")
                  for plugin in manifest.get("plugins", []) if plugin["marketplace"]]
    return tuple(artifacts + [(manifest["marketplace"], "jsonall"),
                              (manifest["versionConstant"], "py")])


def distribution_findings(root: Path, manifest: dict) -> list[str]:
    """Prove the Claude marketplace lists exactly the marketplace plugins, at their paths.

    Shared by the repository gate and release preflight, before any version is written."""
    rel = manifest["marketplace"]
    expected = {p["name"]: p for p in manifest.get("plugins", []) if p["marketplace"]}
    findings = []
    try:
        catalog = json.loads(safe_path(root, rel).read_text(encoding="utf-8"))
        if not isinstance(catalog, dict) or not isinstance(catalog.get("plugins"), list):
            raise ValueError("catalog must contain a plugins list")
        entries = catalog["plugins"]
        if any(not isinstance(entry, dict) for entry in entries):
            raise ValueError("catalog entries must be objects")
        if len(entries) != len(expected) or {e.get("name") for e in entries} != set(expected):
            findings.append(f"{rel}: marketplace membership disagrees with the marketplace plugins")
        for entry in entries:
            plugin = expected.get(entry.get("name"))
            if plugin is not None and entry.get("source") != "./" + plugin["path"]:
                findings.append(f"{rel}: marketplace source disagrees: {plugin['name']}")
        for plugin in expected.values():
            path = safe_path(root, plugin["path"] + "/.claude-plugin/plugin.json")
            if json.loads(path.read_text(encoding="utf-8")).get("name") != plugin["name"]:
                findings.append(f"{path.relative_to(root)}: plugin identity disagrees")
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
        findings.append(f"{rel}: distribution refused: {exc}")
    return findings


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
