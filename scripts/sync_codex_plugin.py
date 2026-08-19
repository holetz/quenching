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

CODEX_CQ_WRAPPER = r'''cq() {
  local plugin_root="${PLUGIN_ROOT:-${CODEX_PLUGIN_ROOT:-}}"
  [ -n "$plugin_root" ] || plugin_root="$(codex plugin list 2>/dev/null | awk '$1 ~ /^quenching-codex@/ {print $NF; exit}')"
  [ -n "$plugin_root" ] || plugin_root="$(find "${CODEX_HOME:-$HOME/.codex}" "$HOME/.codex" -type f \( -path '*/quenching-codex/*/scripts/cq' -o -path '*/quenching-codex/scripts/cq' \) -print -quit 2>/dev/null | sed 's#/scripts/cq$##')"
  if [ -z "$plugin_root" ] || [ ! -f "$plugin_root/scripts/cq" ]; then
    echo "quenching-codex: installed plugin root not found; enable the plugin first" >&2
    return 2
  fi
  python3 "$plugin_root/scripts/cq" "$@"
}'''

CQ_INVOCATION = re.compile(r"(?<![A-Za-z0-9_./-])cq(?=\s+(?:specs|knowledge|components|git)\b)")
EXPLICIT_CQ_INVOCATION = re.compile(r"python3\s+(?:\"?\.\./\.\./scripts/cq\"?|\"?scripts/bin/cq\"?)")
RELATIVE_CQ_PATH = re.compile(r"(?<![A-Za-z0-9_./])(?:python3\s+)?\"?\.\./\.\./scripts/cq\"?")
CODEX_CQ_COMMAND = 'python3 "$(find "${CODEX_HOME:-$HOME/.codex}" "$HOME/.codex" -type f -path \'*/quenching-codex*/scripts/cq\' -print -quit 2>/dev/null)"'


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


def has_cq_invocation(text: str) -> bool:
    return bool(CQ_INVOCATION.search(text) or EXPLICIT_CQ_INVOCATION.search(text))


def transform_codex_cq_references(text: str) -> str:
    """Keep generated Codex prose from teaching an unusable relative CLI path."""
    text = RELATIVE_CQ_PATH.sub("cq", text)
    text = text.replace(
        "§Resolving the tool, §Write the resolved path literally on every invocation: bare `cq specs` where\n"
        "the `bin/` shim is on `PATH`, else the plugin path `cq specs`\n"
        "invoked with `python3` or `py` (`allowed-tools: Bash(python3:*), Bash(py:*)`) — **two doors onto one\n"
        "file, and no third rung**.",
        "§Resolving the tool: define the per-call wrapper there, then invoke the bundled `cq specs`\n"
        "function in the same Bash call — **one door onto one file, and no third rung**.",
    )
    text = text.replace(
        "The executable checker is `cq`\n(`cq knowledge validate /.knowledge` → exit 0 = conforms). Invoke it by its **literal quoted\n"
        "path** on every call, never through a shell variable holding the interpreter plus the path —",
        "The executable checker is `cq`\n(`cq knowledge validate /.knowledge` → exit 0 = conforms). Define the per-call wrapper from\n"
        "the tool-resolution reference, then invoke `cq` in that same Bash call —",
    )
    text = text.replace(
        "Every rung above that fallback is the plugin's own file — bare `cq` through the `bin/` shim on\n"
        "`PATH`, or the plugin path — and nothing else is one. This sentence used to name a rung outside the",
        "The only supported route above that fallback is the plugin's own per-call `cq` wrapper; it resolves\n"
        "the installed plugin copy and nothing else. This sentence used to name a rung outside the",
    )
    return text


def transform_codex_shell_blocks(text: str) -> str:
    """Make every generated shell invocation independent of the user's PATH.

    A Codex Bash call starts a fresh shell, so each cq invocation carries its own
    one-line lookup of the installed plugin copy instead of relying on state from a
    previous call or on a host-specific PATH mutation.
    """
    lines = text.splitlines()
    output: list[str] = []
    in_bash = False
    block: list[str] = []

    def flush_block() -> None:
        if has_cq_invocation("\n".join(block)):
            body = [EXPLICIT_CQ_INVOCATION.sub(CODEX_CQ_COMMAND, line) for line in block]
            body = [CQ_INVOCATION.sub(CODEX_CQ_COMMAND, line) for line in body]
            output.extend(body)
        else:
            output.extend(block)

    for line in lines:
        opening = re.match(r"^\s*```bash\s*$", line)
        if opening:
            in_bash = True
            block = []
            output.append(line)
        elif in_bash and re.match(r"^\s*```\s*$", line):
            flush_block()
            output.append(line)
            in_bash = False
        elif in_bash:
            block.append(line)
        else:
            output.append(line)
    if in_bash:
        output.extend(block)
    return "\n".join(output) + ("\n" if text.endswith("\n") else "")


def codex_tool_resolution(text: str) -> str:
    """Replace the Claude/host-PATH contract with Codex's per-call resolver."""
    start = text.index("## Resolving the tool")
    resolution = f'''## Resolving the tool

Codex does **not** require `cq` to be installed in the user's PATH.  A bare `cq` in the
examples below means the shell function defined at the start of the same Bash call; never
assume that `cq` is an independently installed command, and never ask the user to add it to
their shell startup files.

```bash
{CODEX_CQ_WRAPPER}
```

The function uses the plugin-provided root when the host exposes one, otherwise it resolves the
installed `quenching-codex` copy through `codex plugin list` or the standard Codex cache.  It then
executes the bundled `scripts/cq` by absolute path.  Defining it again in each Bash call is
intentional: shell state does not survive between calls, and sub-agents may receive a fresh
environment.

There is no target-repository installation step and no third rung: never look for a copy under a
target's `.agents/hooks/`, never install one there, and never modify the user's PATH to make this
tool resolve.

Branch on the **exit code** (0 ok · 1 findings · 2 refusal) and the `--json` payload, never on
prose.

### Write the resolved path literally on every invocation

The wrapper resolves the installed plugin at the point of execution.  Do not copy a relative path
from this reference into a command: a fresh Bash call has no shared working-directory or shell
state to make a plugin-relative path reliable.  Defining the function again in every Bash call is
the portable form, including for sub-agents.

**Chain several writes so a failure stops the run** — `set -e`, or `&&` between them.
'''
    return text[:start] + resolution


def codex_readme(text: str) -> str:
    """Keep the generated README aligned with Codex's actual tool-loading contract."""
    install = text.index("The tool itself is reached through **two doors onto one file**.")
    upgrade = text.index("## Upgrade", install)
    text = (
        text[:install]
        + "The CLI is bundled inside the plugin and is **not** installed in the user's PATH. "
          "Codex skills define a per-call `cq` wrapper that resolves the installed plugin and "
          "executes `scripts/cq` by absolute path; the wrapper is repeated because each Bash call "
          "and each sub-agent may start with a fresh shell. The resolver and its no-global-install "
          "rule live in `references/align/tool-resolution.md`.\n\n"
        + text[upgrade:]
    )
    upgrade = text.index("## Upgrade")
    publishing = text.index("Publishing the bump itself is mechanized", upgrade)
    text = (
        text[:upgrade]
        + "## Upgrade\n\n"
          "Resolution is **plugin-first, with no user-level install**: every skill resolves the "
          "installed plugin copy at call time, so a version bump reaches consumers when Codex "
          "refreshes the plugin. There is no global `cq` executable to keep in sync.\n\n"
        + text[publishing:]
    )
    return text


def transform_asset(relative: Path, text: str, adaptation: dict) -> str:
    """Apply the few structural adaptations that cannot be expressed as token swaps."""
    text = transform_platform(text, adaptation)
    if relative.as_posix() == "align/tool-resolution.md":
        text = codex_tool_resolution(text)
    if relative.suffix == ".md":
        text = transform_codex_cq_references(text)
        text = transform_codex_shell_blocks(text)
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
    body = transform_codex_cq_references(body)
    body = transform_codex_shell_blocks(body)
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
            content = codex_readme(content)
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
