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
from quenching.common.modules import MANIFEST, load_manifest, release_artifacts, safe_path  # noqa: E402


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


def existing_generated(root: Path, module: dict) -> set[str]:
    target = root / module["path"]
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
    for rel in module["generated"]["trees"]:
        for directory in sorted((target / rel).rglob("*"), reverse=True):
            if directory.is_dir() and not any(directory.iterdir()):
                directory.rmdir()


def published_findings(root: Path, manifest: dict) -> list[str]:
    source_version = (root / manifest["source"] / "VERSION").read_text().strip()
    findings = []
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
        # Preflight the complete plan, including published surfaces, before any file mutation.
        findings = published_findings(ROOT, manifest)
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
        remaining = published_findings(ROOT, manifest)
        if remaining:
            print("\n".join(remaining), file=sys.stderr)
            return 1
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"module manifest refused: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
