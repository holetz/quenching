#!/usr/bin/env python3
"""Generate manifest-declared plugin consumers and check published version lockstep."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "plugins/quenching/assets/bin"))
from quenching.common.modules import (MANIFEST, load_manifest, namespace_map,  # noqa: E402
                                      distribution_findings, release_artifacts, safe_path)


def build_artifact(path: Path) -> bool:
    return "__pycache__" in path.parts or path.suffix == ".pyc"


def generated_tree(root: Path, manifest: dict, module: dict) -> dict:
    source = root / manifest["source"]
    tree = {}
    for rel in module["generated"]["trees"]:
        for path in sorted((source / rel).rglob("*")):
            if path.is_file() and not build_artifact(path):
                tree[path.relative_to(source).as_posix()] = (
                    path.read_bytes(), 0o755 if path.stat().st_mode & 0o111 else 0o644)
    for rel in module["generated"].get("files", []):
        path = source / rel
        tree[rel] = (path.read_bytes(), 0o755 if path.stat().st_mode & 0o111 else 0o644)
    version = (source / "VERSION").read_text().strip()
    original = json.loads((source / ".claude-plugin/plugin.json").read_text())
    metadata = module["generated"]["metadata"]
    plugin = {"name": module["name"], "version": version,
              "description": metadata["description"], "author": original["author"],
              "license": original["license"], "keywords": metadata["keywords"]}
    record = {"source": manifest["source"], "manifest": MANIFEST,
              "generator": "scripts/generate_plugin_modules.py",
              "copied": module["generated"]["trees"] + module["generated"].get("files", [])}
    tree["VERSION"] = (version.encode() + b"\n", 0o644)
    for rel, payload in ((".claude-plugin/plugin.json", plugin),
                         (".generated-from.json", record)):
        tree[rel] = ((json.dumps(payload, indent=2, ensure_ascii=False) + "\n").encode(), 0o644)
    for rel in tree:
        target = safe_path(root / module["path"], rel)
        if target.exists() and not target.is_file():
            raise ValueError(f"generated file target is not a file: {target}")
    return tree


def copy_files(tree: dict, source: Path, rel: str) -> None:
    base = source / rel
    paths = [base] if base.is_file() else sorted(base.rglob("*"))
    for path in paths:
        if path.is_file() and not build_artifact(path):
            tree[path.relative_to(source).as_posix()] = (
                path.read_bytes(), 0o755 if path.stat().st_mode & 0o111 else 0o644)


def principal_tree(root: Path, manifest: dict, module: dict) -> dict:
    """A principal module: its owned surface plus the generated support closure, all from source."""
    source = root / manifest["source"]
    owned, support = module["owned"], module["generatedSupport"]
    tree: dict = {}
    for rel in owned["commands"]:
        copy_files(tree, source, "commands/" + rel)
    if owned["agents"]:
        copy_files(tree, source, "agents")
    if owned.get("hooks"):
        copy_files(tree, source, "hooks")
    for package in [*owned["packages"], *support["packages"]]:
        copy_files(tree, source, "assets/bin/quenching/" + package)
    for reference in support["references"]:
        copy_files(tree, source, "assets/references/" + reference)
    for child in sorted((source / "assets").iterdir()):
        if child.name not in {"bin", "references"}:
            copy_files(tree, source, "assets/" + child.name)
    if support["router"]:
        copy_files(tree, source, "assets/bin/cq")
    if module["cqPathOwner"]:
        copy_files(tree, source, "bin/cq")
    copy_files(tree, source, "README.md")
    version = (source / "VERSION").read_text().strip()
    original = json.loads((source / ".claude-plugin/plugin.json").read_text())
    fronts = ", ".join(rel.removesuffix(".md") for rel in owned["commands"])
    metadata = module.get("metadata", {})
    plugin = {"name": module["name"], "version": version,
              "description": metadata.get("description", f"quenching module for {fronts}. "
                                          "Generated from plugins/quenching."),
              "author": original["author"], "license": original["license"],
              "keywords": metadata.get("keywords", original["keywords"])}
    record = {"source": manifest["source"], "manifest": MANIFEST,
              "generator": "scripts/generate_plugin_modules.py",
              "owned": owned, "generatedSupport": support}
    tree["VERSION"] = (version.encode() + b"\n", 0o644)
    for rel, payload in ((".claude-plugin/plugin.json", plugin), (".generated-from.json", record)):
        tree[rel] = ((json.dumps(payload, indent=2, ensure_ascii=False) + "\n").encode(), 0o644)
    return tree


CITATION = re.compile(r"\$\{CLAUDE_PLUGIN_ROOT\}/([A-Za-z0-9_./-]+)")
MODULE_ID = re.compile(r"\b(quenching-[a-z]+):([a-z][a-z-]*)")
IMPORT = re.compile(r"^\s*(?:from|import) quenching\.([a-z_]+)", re.M)


def closure_findings(root: Path, manifest: dict, module: dict, tree: dict) -> list[str]:
    """Every own-root citation resolves, every import is shipped, every module id has an owner."""
    mapping = namespace_map(root, manifest)
    folders = set(tree) | {p.as_posix() for rel in tree for p in Path(rel).parents}
    shipped = {rel.split("/")[3] for rel in tree if rel.startswith("assets/bin/quenching/")}
    principal = {m["name"] for m in manifest["modules"] if "owned" in m}
    findings = []
    for rel, (data, _) in sorted(tree.items()):
        if rel.endswith(".md"):
            text = data.decode("utf-8", "replace")
            for match in CITATION.finditer(text):
                cited = match.group(1).rstrip("./")
                if cited not in folders:
                    findings.append(f"{module['name']}: dangling citation {cited} in {rel}")
            if "/quenching:" in text:
                findings.append(f"{module['name']}: unpublished /quenching: id in {rel}")
            for name, head in MODULE_ID.findall(text):
                if name in principal and mapping.get(head) != name:
                    findings.append(f"{module['name']}: {name}:{head} has no owner in {rel}")
        elif rel.endswith(".py"):
            for package in IMPORT.findall(data.decode("utf-8", "replace")):
                if package not in shipped:
                    findings.append(f"{module['name']}: imports unshipped quenching.{package} in {rel}")
    return findings


PILLAR = re.compile(r'Pillar\(\s*"quenching\.([a-z_]+)')


def ownership_findings(root: Path, manifest: dict) -> list[str]:
    """Every shipped package, `cq` pillar and reference has a module that embeds it."""
    source = root / manifest["source"]
    principal = [m for m in manifest["modules"] if "owned" in m]
    if not principal:
        return []
    owned = {p for m in principal for p in m["owned"]["packages"]}
    packages = owned | {p for m in principal for p in m["generatedSupport"]["packages"]}
    references = {r for m in principal for r in m["generatedSupport"]["references"]}
    findings = []
    for path in sorted((source / "assets/bin/quenching").iterdir()):
        if path.is_dir() and path.name != "__pycache__" and path.name not in packages:
            findings.append(f"package {path.name} has no owner module in the manifest")
    for package in sorted(set(PILLAR.findall((source / "assets/bin/cq").read_text(encoding="utf-8")))):
        if package not in owned:
            findings.append(f"cq pillar package {package} has no owner module (owned.packages)")
    for path in sorted((source / "assets/references").iterdir()):
        if path.is_dir() and path.name not in references:
            findings.append(f"reference {path.name} is shipped by no module")
    if (source / "hooks").is_dir() and not any(m["owned"].get("hooks") for m in principal):
        findings.append("hooks/ is shipped by no module (owned.hooks)")
    return findings


def authored_findings(root: Path, module: dict) -> list[str]:
    """A consumer's hand-written prose never names an unpublished /quenching: id."""
    findings = []
    for rel in module.get("authored", []):
        path = root / module["path"] / rel
        if rel.endswith(".md") and path.is_file() and "/quenching:" in path.read_text(
                encoding="utf-8", errors="replace"):
            findings.append(f"{module['name']}: unpublished /quenching: id in {rel}")
    return findings


def existing_generated(root: Path, module: dict) -> set[str]:
    target = root / module["path"]
    if "owned" in module:
        return {p.relative_to(target).as_posix() for p in target.rglob("*")
                if p.is_file() and not build_artifact(p)} if target.is_dir() else set()
    found = set()
    for tree in module["generated"]["trees"]:
        found.update(p.relative_to(target).as_posix() for p in (target / tree).rglob("*")
                     if p.is_file() and not build_artifact(p))
    for rel in [*module["generated"].get("files", []),
                "VERSION", ".claude-plugin/plugin.json", ".generated-from.json"]:
        if (target / rel).is_file():
            found.add(rel)
    return found


def differences(root: Path, module: dict, tree: dict) -> list[str]:
    target = root / module["path"]
    drift = []
    for rel, (data, mode) in sorted(tree.items()):
        path = target / rel
        if not path.is_file():
            drift.append(f"missing {module['path']}/{rel}")
        elif path.read_bytes() != data:
            drift.append(f"changed {module['path']}/{rel}")
        elif bool(path.stat().st_mode & 0o111) != bool(mode & 0o111):
            drift.append(f"mode {module['path']}/{rel}")
    drift.extend(f"stale {module['path']}/{rel}"
                 for rel in sorted(existing_generated(root, module) - tree.keys()))
    return drift


def write_tree(root: Path, module: dict, tree: dict) -> None:
    target = root / module["path"]
    for rel in existing_generated(root, module) - tree.keys():
        (target / rel).unlink()
    for rel, (data, mode) in tree.items():
        path = target / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.is_file() or path.read_bytes() != data:
            path.write_bytes(data)
        path.chmod(mode)
    for rel in module["generated"]["trees"] if "generated" in module else ["."]:
        for directory in sorted((target / rel).rglob("*"), reverse=True):
            if directory.is_dir() and not any(directory.iterdir()):
                directory.rmdir()


def published_findings(root: Path, manifest: dict) -> list[str]:
    source_version = (root / manifest["source"] / "VERSION").read_text().strip()
    findings = distribution_findings(root, manifest)
    for rel, kind in release_artifacts(manifest):
        path = safe_path(root, rel)
        if not path.is_file():
            findings.append(f"missing version surface {rel}")
            continue
        text = path.read_text()
        if kind == "plain":
            versions = [text.strip()]
        elif kind == "py":
            versions = re.findall(r'^VERSION\s*=\s*[\"\']([^\"\']+)', text, re.M)
        else:
            data = json.loads(text)
            if kind == "jsonall":
                entries = data["plugins"]
                expected = {m["name"] for m in manifest["modules"] if m["published"]}
                if len(entries) != len(expected) or {m["name"] for m in entries} != expected:
                    findings.append("marketplace membership disagrees with published modules")
                for entry in entries:
                    owner = next((m for m in manifest["modules"] if m["name"] == entry["name"]), None)
                    if owner and entry.get("source") != "./" + owner["path"]:
                        findings.append(f"marketplace source disagrees: {entry['name']}")
                versions = [entry.get("version") for entry in entries]
            else:
                versions = [data.get("version")]
                owner = next((m for m in manifest["modules"]
                              if rel == m["path"] + "/.claude-plugin/plugin.json"), None)
                if owner and data.get("name") != owner["name"]:
                    findings.append(f"plugin identity disagrees: {rel}")
        if not versions or any(v != source_version for v in versions):
            findings.append(f"version drift {rel}: {versions}, source={source_version}")
    for module in manifest["modules"]:
        if module["published"]:
            shim = safe_path(root, module["path"] + "/bin/cq")
            if shim.is_file() != module["cqPathOwner"]:
                findings.append(f"PATH cq ownership drift: {module['name']}")
            elif shim.is_file() and not shim.stat().st_mode & 0o111:
                findings.append(f"PATH cq is not executable: {module['name']}")
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    try:
        manifest = load_manifest(ROOT)
        consumers = [(m, generated_tree(ROOT, manifest, m)) for m in manifest["modules"]
                     if m["published"] and "generated" in m]
        consumers += [(m, principal_tree(ROOT, manifest, m)) for m in manifest["modules"]
                      if m["published"] and "owned" in m]
        # Preflight the complete plan, including published surfaces, before any file mutation.
        findings = published_findings(ROOT, manifest) + ownership_findings(ROOT, manifest)
        # Planned principal modules are proved closed too, in memory, before they are activated.
        findings += [line for module in manifest["modules"] if "owned" in module
                     for line in closure_findings(ROOT, manifest, module,
                                                  principal_tree(ROOT, manifest, module))]
        findings += [line for module in manifest["modules"] if module["published"]
                     for line in authored_findings(ROOT, module)]
        drift = [line for module, tree in consumers for line in differences(ROOT, module, tree)]
        if args.check:
            if findings or drift:
                print("\n".join(findings + drift), file=sys.stderr)
                print("run: python3 scripts/generate_plugin_modules.py --write", file=sys.stderr)
                return 1
            print(f"generated modules in lockstep ({len(consumers)} consumers); published versions and PATH cq agree")
            return 0
        for module, tree in consumers:
            write_tree(ROOT, module, tree)
        print(f"generated modules rewritten ({len(drift)} paths changed)")
        # Generation repairs copied surfaces only; authored version drift remains a finding.
        remaining = published_findings(ROOT, manifest) + ownership_findings(ROOT, manifest) + [
            line for module, tree in consumers if "owned" in module
            for line in closure_findings(ROOT, manifest, module, tree)] + [
            line for module, _ in consumers for line in authored_findings(ROOT, module)]
        if remaining:
            print("\n".join(remaining), file=sys.stderr)
            return 1
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"module manifest refused: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
