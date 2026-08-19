"""Deterministically translate the packaged Claude surface into its Codex sibling."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from pathlib import Path

from quenching.common.output import finding, refuse, report_findings


REPOSITORY = Path(__file__).resolve().parents[7]
SOURCE: Path | None = None
TARGET: Path | None = None
MANIFEST: Path | None = None
COPY_DIRS = ("assets/references", "assets/templates", "assets/specs", "assets/knowledge", "assets/checks", "assets/bin")
COPY_FILES = ("bin/cq", "README.md", "VERSION")
DROP_FRONTMATTER = {"argument-hint", "allowed-tools", "model", "context", "hooks"}
FORBIDDEN_AFTER_TRANSLATION = ("${CLAUDE_PLUGIN_ROOT}", "${CLAUDE_PROJECT_DIR}", "CLAUDE_PLUGIN_ROOT")


def configure(source: str | None, target: str | None) -> None:
    """Resolve the pair once per invocation; callers may translate any checkout pair."""
    global SOURCE, TARGET, MANIFEST
    SOURCE = Path(source).resolve() if source else REPOSITORY / "plugins" / "quenching"
    TARGET = Path(target).resolve() if target else REPOSITORY / "plugins" / "quenching-codex"
    # The adaptation is part of the distributed translator, not of a target repository.
    MANIFEST = REPOSITORY / "plugins" / "quenching" / "assets" / "translation" / "codex-adaptation.json"


def source() -> Path:
    assert SOURCE is not None
    return SOURCE


def target() -> Path:
    assert TARGET is not None
    return TARGET


def manifest() -> Path:
    assert MANIFEST is not None
    return MANIFEST


def plugin_translation() -> bool:
    """Whether this invocation translates the packaged plugin rather than a repo surface."""
    return (source() / "commands").is_dir()


def claude_surface() -> Path:
    """Resolve a repository root or its `.claude` directory to the Claude surface."""
    return source() if source().name == ".claude" else source() / ".claude"


def codex_surface() -> Path:
    """Resolve a repository root or its `.agents` directory to the Codex surface."""
    return target() if target().name == ".agents" else target() / ".agents"


def read_adaptation() -> dict:
    return json.loads(manifest().read_text(encoding="utf-8"))


def source_files() -> list[Path]:
    if not plugin_translation():
        files = list(sorted((claude_surface() / "commands").rglob("*.md")))
        harness = claude_surface().parent / "CLAUDE.md"
        if harness.is_file():
            files.append(harness)
        files.append(manifest())
        return files
    files = list(sorted((source() / "commands").rglob("*.md")))
    files.extend(source() / rel for rel in COPY_FILES)
    for rel in COPY_DIRS:
        files.extend(sorted(path for path in (source() / rel).rglob("*") if path.is_file()))
    return [path for path in files if path.is_file()]


def source_digest() -> str:
    digest = hashlib.sha256()
    for path in source_files():
        try:
            relative = path.relative_to(source())
        except ValueError:
            relative = path.name
        digest.update(str(relative).encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()


def transform_platform(text: str, adaptation: dict) -> str:
    for old, new in adaptation["replacements"].items():
        text = text.replace(old, new)
    text = re.sub(r"/quenching:([A-Za-z0-9:-]+)",
                  lambda match: "quenching-" + match.group(1).replace(":", "-"), text)
    text = text.replace("Claude Code", "Codex").replace("Claude", "Codex")
    for marker in FORBIDDEN_AFTER_TRANSLATION:
        if marker in text:
            raise ValueError(f"untranslated platform marker: {marker}")
    return text


def transform_asset(relative: Path, text: str, adaptation: dict) -> str:
    text = transform_platform(text, adaptation)
    if relative.as_posix() != "quenching/components/surface.py":
        return text
    start = text.index("def discover_commands(")
    end = text.index("\ndef discover_references(", start)
    codex_discovery = '''def discover_commands(commands_dir: str) -> list[dict]:
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
        out.append({"command": "/" + name.replace(os.sep, "-"), "path": path,
                    "relpath": name + ".md", "frontmatter": parse_frontmatter(text),
                    "anomalies": frontmatter_anomalies(text), "hooks": hooks,
                    "hooksParsed": hooks_parsed, "body": body,
                    "bodyLines": len(body.splitlines())})
    return sorted(out, key=lambda command: command["command"])
'''
    return text[:start] + codex_discovery + text[end:]


def skill_name(command: Path) -> str:
    commands = source() / "commands" if plugin_translation() else claude_surface() / "commands"
    return "quenching-" + "-".join(command.relative_to(commands).with_suffix("").parts)


def command_to_skill(command: Path, adaptation: dict) -> str:
    raw = command.read_text(encoding="utf-8")
    if not raw.startswith("---\n"):
        raise ValueError(f"command has no frontmatter: {command}")
    end = raw.find("\n---\n", 4)
    if end < 0:
        raise ValueError(f"malformed frontmatter: {command}")
    fields = {"name": skill_name(command), "description": None}
    lines, index = raw[4:end].splitlines(), 0
    while index < len(lines):
        line = lines[index]
        if line.startswith("description:"):
            value = line[len("description:"):].strip()
            if value in {">", ">-", "|", "|-"}:
                index += 1
                pieces = []
                while index < len(lines) and lines[index].startswith((" ", "\t")):
                    pieces.append(lines[index].strip())
                    index += 1
                fields["description"] = " ".join(pieces)
                continue
            fields["description"] = value
        elif ":" in line and line.split(":", 1)[0] not in DROP_FRONTMATTER:
            key, value = line.split(":", 1)
            if key in fields:
                fields[key] = value.strip()
        index += 1
    if not fields["description"]:
        raise ValueError(f"command has no description: {command}")
    origin = ("plugins/quenching/commands/" + str(command.relative_to(source() / "commands"))
              if plugin_translation() else ".claude/commands/" + str(command.relative_to(claude_surface() / "commands")))
    header = ("---\n" + f"name: {fields['name']}\n" +
              f"description: {json.dumps(transform_platform(fields['description'], adaptation), ensure_ascii=False)}\n" +
              f"---\n\n<!-- GENERATED FROM {origin} -->\n\n")
    return header + transform_platform(raw[end + len("\n---\n"):], adaptation)


def generated_tree() -> dict[str, bytes]:
    adaptation, output = read_adaptation(), {}
    if not plugin_translation():
        commands = claude_surface() / "commands"
        for command in sorted(commands.rglob("*.md")):
            relative = command.relative_to(commands).with_suffix("")
            output[str(Path("skills") / relative / "SKILL.md")] = command_to_skill(command, adaptation).encode()
        harness = claude_surface().parent / "CLAUDE.md"
        if harness.is_file():
            output["AGENTS.md"] = transform_platform(harness.read_text(encoding="utf-8"), adaptation).encode()
        output[".generated-from.json"] = json.dumps({
            "source": str(claude_surface()), "source_sha256": source_digest(),
            "generator": "cq components translate",
            "command_count": len(list(commands.rglob("*.md"))),
        }, indent=2).encode() + b"\n"
        return output
    version = (source() / "VERSION").read_text(encoding="utf-8").strip()
    output[".codex-plugin/plugin.json"] = json.dumps({
        "name": "quenching-codex", "version": version,
        "description": "Codex translation of the quenching Claude plugin, generated from the Claude source plugin.",
        "author": {"name": "Israel Holetz", "email": "holetz@gmail.com"}, "license": "MIT",
        "keywords": ["codex", "knowledge-management", "documentation", "spec-driven", "automation"], "skills": "./skills/",
        "interface": {"displayName": "Quenching Codex", "shortDescription": "Deterministic knowledge and spec alignment workflows for Codex",
                      "longDescription": "Generated Codex sibling of the Claude quenching plugin. Claude is the source of truth.",
                      "developerName": "Israel Holetz", "category": "Developer Tools", "capabilities": ["Interactive", "Write"],
                      "defaultPrompt": ["Align this repository with quenching.", "Run the quenching knowledge workflow.", "Check the Codex plugin for drift."],
                      "brandColor": "#0F766E", "screenshots": []}}, indent=2, ensure_ascii=False).encode() + b"\n"
    for command in sorted((source() / "commands").rglob("*.md")):
        output[str(Path("skills") / skill_name(command) / "SKILL.md")] = command_to_skill(command, adaptation).encode()
    for rel in COPY_FILES:
        destination = Path("scripts/cq") if rel == "bin/cq" else Path(rel)
        content = transform_platform((source() / rel).read_text(encoding="utf-8"), adaptation)
        if rel == "README.md":
            content = "# quenching-codex (generated)\n\nThis plugin is generated from `plugins/quenching/`, which is the only editable source.\nRun `python3 scripts/sync_codex_plugin.py --write` to refresh it.\n\n" + content
        output[str(destination)] = content.encode()
    for rel in COPY_DIRS:
        source_dir, destination_root = source() / rel, Path(rel.replace("assets/", ""))
        if rel == "assets/bin":
            destination_root = Path("scripts/bin")
        for path in sorted(source_dir.rglob("*")):
            if not path.is_file() or "__pycache__" in path.parts or path.suffix == ".pyc":
                continue
            relative = path.relative_to(source_dir)
            if relative.name == "CLAUDE.md":
                relative = relative.with_name("AGENTS.md")
            output[str(destination_root / relative)] = transform_asset(relative, path.read_text(encoding="utf-8"), adaptation).encode()
    output[".generated-from.json"] = json.dumps({"source": "plugins/quenching", "source_sha256": source_digest(),
        "generator": "cq components translate", "command_count": len(list((source() / "commands").rglob("*.md")))}, indent=2).encode() + b"\n"
    return output


def differences(tree: dict[str, bytes]) -> list[str]:
    destination = target() if plugin_translation() else codex_surface()
    actual = {str(path.relative_to(destination)) for path in destination.rglob("*") if path.is_file() and path.name != ".generated-files.json" and "__pycache__" not in path.parts and path.suffix != ".pyc"} if destination.exists() else set()
    return [rel for rel in sorted(set(tree) | actual) if rel not in tree or not (destination / rel).exists() or (destination / rel).read_bytes() != tree[rel]]


def write_tree(tree: dict[str, bytes]) -> None:
    destination = target() if plugin_translation() else codex_surface()
    destination.mkdir(parents=True, exist_ok=True)
    generated_manifest = destination / ".generated-files.json"
    old = set(json.loads(generated_manifest.read_text(encoding="utf-8"))["files"]) if generated_manifest.exists() else set()
    for rel in old - set(tree):
        path = destination / rel
        if path.exists():
            path.unlink()
    for rel, content in tree.items():
        path = destination / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    generated_manifest.write_text(json.dumps({"files": sorted(tree)}, indent=2) + "\n", encoding="utf-8")


def add_arguments(parser: argparse.ArgumentParser) -> None:
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--diff", action="store_true")
    parser.add_argument("--source", help="Claude surface or plugin source")
    parser.add_argument("--target", help="Codex surface or generated destination")
    parser.add_argument("--json", action="store_true")


def cmd_translate(args, _root: str) -> int:
    try:
        configure(args.source, args.target)
        tree = generated_tree()
    except ValueError as exc:
        return refuse({"code": "ct-translation-refused", "message": str(exc)}, args.json)
    changed = differences(tree)
    payload = {"changed": changed, "count": len(changed), "source_sha256": source_digest()}
    if args.write:
        write_tree(tree)
        payload["changed"] = []
        payload["count"] = 0
    findings = [finding("ct-translation-drift", "error",
                        "generated translation differs from the Claude surface", path=path)
                for path in payload["changed"]]
    return report_findings(args.json, f"components translate — {payload['count']} changed file(s)",
                           payload, findings, "path")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="cq components translate")
    add_arguments(parser)
    return cmd_translate(parser.parse_args(argv), str(REPOSITORY))
