#!/usr/bin/env python3
"""Generate the Codex sibling plugin from the Claude plugin.

The Claude plugin is the source of truth.  This generator deliberately has no
LLM step: paths, names, frontmatter, and platform substitutions are all
deterministic and unknown substitutions are errors.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "plugins" / "quenching"
TARGET = ROOT / "plugins" / "quenching-codex"
VERSION = SOURCE / "VERSION"
MANIFEST = ROOT / "scripts" / "codex-adaptation.json"

COPY_DIRS = ("assets/references", "assets/templates", "assets/specs", "assets/knowledge", "assets/checks", "assets/bin")
COPY_FILES = ("bin/cq", "README.md", "VERSION")
DROP_FRONTMATTER = {"argument-hint", "allowed-tools", "model", "context", "hooks"}
FORBIDDEN_AFTER_TRANSLATION = ("${CLAUDE_PLUGIN_ROOT}", "${CLAUDE_PROJECT_DIR}", "CLAUDE_PLUGIN_ROOT")


def read_adaptation() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def source_files() -> list[Path]:
    files = []
    for path in sorted((SOURCE / "commands").rglob("*.md")):
        files.append(path)
    for rel in COPY_FILES:
        files.append(SOURCE / rel)
    for rel in COPY_DIRS:
        files.extend(sorted((SOURCE / rel).rglob("*")))
    return [p for p in files if p.is_file()]


def skill_name(command: Path) -> str:
    return "quenching-" + "-".join(command.relative_to(SOURCE / "commands").with_suffix("").parts)


def transform_platform(text: str, adaptation: dict) -> str:
    replacements = adaptation["replacements"]
    for old, new in replacements.items():
        text = text.replace(old, new)
    text = re.sub(r"/quenching:([A-Za-z0-9:-]+)", lambda m: "quenching-" + m.group(1).replace(":", "-"), text)
    text = text.replace("Claude Code", "Codex")
    text = text.replace("Claude", "Codex")
    for marker in FORBIDDEN_AFTER_TRANSLATION:
        if marker in text:
            raise ValueError(f"untranslated platform marker: {marker}")
    return text


def transform_asset(relative: Path, text: str, adaptation: dict) -> str:
    """Apply the few structural adaptations that cannot be expressed as token swaps."""
    text = transform_platform(text, adaptation)
    if relative.as_posix() == "quenching/components/surface.py":
        start = text.index("def discover_commands(")
        end = text.index("\ndef discover_references(", start)
        replacement = '''def discover_commands(commands_dir: str) -> list[dict]:
    """Discover Codex skills as one entry point per ``skills/<name>/SKILL.md``."""
    if not os.path.isdir(commands_dir):
        return []
    out = []
    for dirpath, _dirnames, filenames in os.walk(commands_dir):
        if "SKILL.md" not in filenames:
            continue
        path = os.path.join(dirpath, "SKILL.md")
        name = rel(dirpath, commands_dir)
        text = read_text(path) or ""
        body = body_after_frontmatter(text)
        hooks, hooks_parsed = parse_frontmatter_hooks(text)
        out.append({
            "command": "/" + name.replace(os.sep, "-"),
            "path": path,
            "relpath": name + ".md",
            "frontmatter": parse_frontmatter(text),
            "anomalies": frontmatter_anomalies(text),
            "hooks": hooks,
            "hooksParsed": hooks_parsed,
            "body": body,
            "bodyLines": len(body.splitlines()),
        })
    return sorted(out, key=lambda c: c["command"])
'''
        text = text[:start] + replacement + text[end:]
    return text


def command_to_skill(command: Path, adaptation: dict) -> str:
    raw = command.read_text(encoding="utf-8")
    if not raw.startswith("---\n"):
        raise ValueError(f"command has no frontmatter: {command}")
    end = raw.find("\n---\n", 4)
    if end < 0:
        raise ValueError(f"malformed frontmatter: {command}")
    front = raw[4:end]
    body = raw[end + len("\n---\n"):]
    fields = {"name": skill_name(command), "description": None}
    front_lines = front.splitlines()
    index = 0
    while index < len(front_lines):
        line = front_lines[index]
        if line.startswith("description:"):
            value = line[len("description:"):].strip()
            if value in {">", ">-", "|", "|-"}:
                pieces = []
                index += 1
                while index < len(front_lines) and (front_lines[index].startswith(" ") or front_lines[index].startswith("\t")):
                    pieces.append(front_lines[index].strip())
                    index += 1
                fields["description"] = " ".join(pieces)
                continue
            fields["description"] = value
        elif line.split(":", 1)[0] not in DROP_FRONTMATTER and ":" in line:
            # Codex skills only need the portable identity and routing fields.
            key, value = line.split(":", 1)
            if key in {"name", "description"}:
                fields[key] = value.strip()
        index += 1
    if not fields["description"]:
        raise ValueError(f"command has no description: {command}")
    description = transform_platform(fields["description"], adaptation)
    body = transform_platform(body, adaptation)
    header = (
        "---\n"
        f"name: {fields['name']}\n"
        f"description: {json.dumps(description, ensure_ascii=False)}\n"
        "---\n\n"
        "<!-- GENERATED FROM plugins/quenching/commands/"
        f"{command.relative_to(SOURCE / 'commands')} -->\n\n"
    )
    return header + body


def generated_tree() -> dict[str, bytes]:
    adaptation = read_adaptation()
    output: dict[str, bytes] = {}
    version = VERSION.read_text(encoding="utf-8").strip()
    output[".codex-plugin/plugin.json"] = json.dumps({
        "name": "quenching-codex",
        "version": version,
        "description": "Codex translation of the quenching Claude plugin, generated from the Claude source plugin.",
        "author": {"name": "Israel Holetz", "email": "holetz@gmail.com"},
        "license": "MIT",
        "keywords": ["codex", "knowledge-management", "documentation", "spec-driven", "automation"],
        "skills": "./skills/",
        "interface": {
            "displayName": "Quenching Codex",
            "shortDescription": "Deterministic knowledge and spec alignment workflows for Codex",
            "longDescription": "Generated Codex sibling of the Claude quenching plugin. Claude is the source of truth.",
            "developerName": "Israel Holetz",
            "category": "Developer Tools",
            "capabilities": ["Interactive", "Write"],
            "defaultPrompt": [
                "Align this repository with quenching.",
                "Run the quenching knowledge workflow.",
                "Check the Codex plugin for drift.",
            ],
            "brandColor": "#0F766E",
            "screenshots": [],
        },
    }, indent=2, ensure_ascii=False).encode() + b"\n"
    for command in sorted((SOURCE / "commands").rglob("*.md")):
        rel = command.relative_to(SOURCE / "commands").with_suffix("")
        out = Path("skills") / skill_name(command) / "SKILL.md"
        output[str(out)] = command_to_skill(command, adaptation).encode()
    for rel in COPY_FILES:
        destination = Path(rel)
        if rel == "bin/cq":
            destination = Path("scripts/cq")
        elif rel == "README.md":
            destination = Path("README.md")
        content = transform_platform((SOURCE / rel).read_text(encoding="utf-8"), adaptation)
        if rel == "README.md":
            content = ("# quenching-codex (generated)\n\n"
                       "This plugin is generated from `plugins/quenching/`, which is the only editable source.\n"
                       "Run `python3 scripts/sync_codex_plugin.py --write` to refresh it.\n\n" + content)
        output[str(destination)] = content.encode()
    for rel in COPY_DIRS:
        source_dir = SOURCE / rel
        destination_root = Path(rel.replace("assets/", ""))
        if rel == "assets/bin":
            destination_root = Path("scripts/bin")
        for path in sorted(source_dir.rglob("*")):
            if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc":
                relative = path.relative_to(source_dir)
                if relative.name == "CLAUDE.md":
                    relative = relative.with_name("AGENTS.md")
                output[str(destination_root / relative)] = transform_asset(relative, path.read_text(encoding="utf-8"), adaptation).encode()
    output[".generated-from.json"] = json.dumps({
        "source": "plugins/quenching",
        "source_sha256": source_digest(),
        "generator": "scripts/sync_codex_plugin.py",
        "command_count": len(list((SOURCE / "commands").rglob("*.md"))),
    }, indent=2).encode() + b"\n"
    return output


def source_digest() -> str:
    digest = hashlib.sha256()
    for path in source_files() + [MANIFEST]:
        digest.update(str(path.relative_to(ROOT)).encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()


def compare(tree: dict[str, bytes]) -> list[str]:
    differences = []
    expected = set(tree)
    actual = {str(p.relative_to(TARGET)) for p in TARGET.rglob("*")
              if p.is_file() and p.name != ".generated-files.json"
              and "__pycache__" not in p.parts and p.suffix != ".pyc"} if TARGET.exists() else set()
    for rel in sorted(expected | actual):
        path = TARGET / rel
        actual_bytes = path.read_bytes() if path.exists() else None
        if rel not in tree or actual_bytes != tree[rel]:
            differences.append(rel)
    return differences


def write_tree(tree: dict[str, bytes]) -> None:
    TARGET.mkdir(parents=True, exist_ok=True)
    old = set()
    old_manifest = TARGET / ".generated-files.json"
    if old_manifest.exists():
        old = set(json.loads(old_manifest.read_text(encoding="utf-8"))["files"])
    for rel in sorted(old - set(tree)):
        path = TARGET / rel
        if path.exists():
            path.unlink()
    for rel, data in tree.items():
        path = TARGET / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    (TARGET / ".generated-files.json").write_text(json.dumps({"files": sorted(tree)}, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--diff", action="store_true")
    parser.add_argument("--report", action="store_true")
    args = parser.parse_args()
    try:
        tree = generated_tree()
    except ValueError as exc:
        parser.error(str(exc))
    differences = compare(tree)
    if args.report or args.diff:
        print(json.dumps({"changed": differences, "count": len(differences), "source_sha256": source_digest()}, indent=2))
    if args.write:
        write_tree(tree)
        print(f"generated {len(tree)} files in {TARGET}")
        return 0
    return 1 if differences else 0


if __name__ == "__main__":
    raise SystemExit(main())
