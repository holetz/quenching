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
PLATFORM_NEUTRAL_CLAUDE_CODEX = "\u0043laude or \u0043odex"

CODEX_CQ_WRAPPER = r"""cq() {
  local plugin_root="${PLUGIN_ROOT:-${CODEX_PLUGIN_ROOT:-}}"
  [ -n "$plugin_root" ] || plugin_root="$(codex plugin list 2>/dev/null | awk '$1 ~ /^quenching-codex@/ {print $NF; exit}')"
  [ -n "$plugin_root" ] || plugin_root="$(find "${CODEX_HOME:-$HOME/.codex}" "$HOME/.codex" -type f \( -path '*/quenching-codex/*/scripts/cq' -o -path '*/quenching-codex/scripts/cq' \) -print -quit 2>/dev/null | sed 's#/scripts/cq$##')"
  if [ -z "$plugin_root" ] || [ ! -f "$plugin_root/scripts/cq" ]; then
    echo "quenching-codex: installed plugin root not found; enable the plugin first" >&2
    return 2
  fi
  python3 "$plugin_root/scripts/cq" "$@"
}"""

CQ_INVOCATION = re.compile(r"(?<![A-Za-z0-9_./-])cq(?=\s+(?:specs|knowledge|components|git)\b)")
EXPLICIT_CQ_INVOCATION = re.compile(r"python3\s+(?:\"?\.\./\.\./scripts/cq\"?|\"?scripts/bin/cq\"?)")
RELATIVE_CQ_PATH = re.compile(r"(?<![A-Za-z0-9_./])(?:python3\s+)?\"?\.\./\.\./scripts/cq\"?")
CODEX_CQ_COMMAND = 'python3 "$(find "${CODEX_HOME:-$HOME/.codex}" "$HOME/.codex" -type f -path \'*/quenching-codex*/scripts/cq\' -print -quit 2>/dev/null)"'


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
        references = claude_surface() / "references"
        if references.is_dir():
            files.extend(sorted(path for path in references.rglob("*") if path.is_file()))
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
    neutral_marker = "\x00QUENCHING_PLATFORM_NEUTRAL_CLAUDE_CODEX\x00"
    text = text.replace(PLATFORM_NEUTRAL_CLAUDE_CODEX, neutral_marker)
    for old, new in adaptation["replacements"].items():
        text = text.replace(old, new)
    text = re.sub(r"/quenching:([A-Za-z0-9:-]+)",
                  lambda match: "quenching-" + match.group(1).replace(":", "-"), text)
    text = text.replace("Claude Code", "Codex").replace("Claude", "Codex")
    text = text.replace(neutral_marker, PLATFORM_NEUTRAL_CLAUDE_CODEX)
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
        if re.match(r"^\s*```bash\s*$", line):
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


def transform_codex_markdown(text: str) -> str:
    """The two prose passes every translated Markdown asset and skill body receives."""
    return transform_codex_shell_blocks(transform_codex_cq_references(text))


def codex_tool_resolution(text: str) -> str:
    """Replace the Claude/host-PATH contract with Codex's per-call resolver."""
    start = text.index("## Resolving the tool")
    resolution = f"""## Resolving the tool

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
"""
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
    text = transform_platform(text, adaptation)
    if relative.as_posix() == "align/tool-resolution.md":
        text = codex_tool_resolution(text)
    if relative.suffix == ".md":
        text = transform_codex_markdown(text)
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
    return header + transform_codex_markdown(transform_platform(raw[end + len("\n---\n"):], adaptation))


def generated_tree() -> dict[str, bytes]:
    adaptation, output = read_adaptation(), {}
    if not plugin_translation():
        commands = claude_surface() / "commands"
        for command in sorted(commands.rglob("*.md")):
            relative = command.relative_to(commands).with_suffix("")
            output[str(Path("skills") / relative / "SKILL.md")] = command_to_skill(command, adaptation).encode()
        references = claude_surface() / "references"
        if references.is_dir():
            for reference in sorted(path for path in references.rglob("*") if path.is_file()):
                relative = reference.relative_to(references)
                translated = transform_platform(reference.read_text(encoding="utf-8"), adaptation)
                if reference.suffix == ".md":
                    translated = transform_codex_markdown(translated)
                output[str(Path("references") / relative)] = translated.encode()
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
            content = codex_readme(content)
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
    if not plugin_translation():
        # A repository's Codex marketplace and other configuration are not generated from
        # `.claude/`. Only the translated harness, skills, and their local references are owned.
        actual = {rel for rel in actual if rel in {"AGENTS.md", ".generated-from.json"}
                  or rel.startswith(("skills/", "references/"))}
    return [rel for rel in sorted(set(tree) | actual) if rel not in tree or not (destination / rel).exists() or (destination / rel).read_bytes() != tree[rel]]


def reconciliation(changed: list[str], digest: str) -> str:
    """Classify source and generated-tree changes from their recorded source hash."""
    destination = target() if plugin_translation() else codex_surface()
    recorded = destination / ".generated-from.json"
    try:
        previous = json.loads(recorded.read_text(encoding="utf-8")).get("source_sha256")
    except (OSError, ValueError, AttributeError):
        previous = None
    generated = destination / ".generated-files.json"
    try:
        hashes = json.loads(generated.read_text(encoding="utf-8")).get("sha256", {})
    except (OSError, ValueError, AttributeError):
        hashes = {}
    target_changed = any(not (destination / rel).is_file()
                         or hashes.get(rel) != hashlib.sha256((destination / rel).read_bytes()).hexdigest()
                         for rel in hashes)
    if previous is None or not hashes:
        return "untracked"
    if previous == digest:
        return "target-changed" if target_changed else "in-sync"
    return "both-changed" if target_changed else "source-changed"


def _body(text: str) -> str:
    """Return a translated skill's body, excluding generated metadata."""
    if text.startswith("---\n"):
        end = text.find("\n---\n", 4)
        if end >= 0:
            text = text[end + len("\n---\n"):]
    if text.startswith("\n<!-- GENERATED FROM"):
        marker_end = text.find("-->\n\n")
        if marker_end >= 0:
            text = text[marker_end + len("-->\n\n"):]
    return text


def _claude_body(text: str) -> str:
    return (text.replace("${CODEX_PLUGIN_ROOT}", "${CLAUDE_PLUGIN_ROOT}")
                .replace(".agents/", ".claude/")
                .replace("AGENTS.md", "CLAUDE.md")
                .replace("Codex", "Claude"))


def propagate_bodies_from_codex(tree: dict[str, bytes]) -> None:
    """Apply only body edits from a changed Codex tree back to its Claude source.

    Frontmatter and path changes are intentionally refused: the forward map drops information,
    so only the source side can author that structure.
    """
    destination = target() if plugin_translation() else codex_surface()
    for rel in differences(tree):
        if not rel.startswith("skills/") or not rel.endswith("/SKILL.md") or rel not in tree:
            raise ValueError(f"Codex structural change at {rel}; the Claude side is authoritative")
        if not (destination / rel).is_file():
            raise ValueError(f"Codex structural change at {rel}; the Claude side is authoritative")
        actual = (destination / rel).read_text(encoding="utf-8")
        expected = tree[rel].decode("utf-8")
        actual_header = actual.split("---\n", 2)[:2]
        expected_header = expected.split("---\n", 2)[:2]
        if actual_header != expected_header:
            raise ValueError(f"Codex frontmatter change at {rel}; the Claude side is authoritative")
        parts = Path(rel).parts[1:-1]
        source_command = ((source() / "commands") if plugin_translation() else claude_surface() / "commands")
        command = source_command.joinpath(*parts).with_suffix(".md")
        raw = command.read_text(encoding="utf-8")
        header_end = raw.find("\n---\n", 4)
        if header_end < 0:
            raise ValueError(f"Claude command has malformed frontmatter: {command}")
        command.write_text(raw[:header_end + len("\n---\n")] + "\n" + _claude_body(_body(actual)),
                           encoding="utf-8")


def write_tree(tree: dict[str, bytes]) -> None:
    destination = target() if plugin_translation() else codex_surface()
    destination.mkdir(parents=True, exist_ok=True)
    generated_manifest = destination / ".generated-files.json"
    if generated_manifest.exists():
        previous = json.loads(generated_manifest.read_text(encoding="utf-8"))["files"]
        old = set(previous if isinstance(previous, list) else previous.keys())
    else:
        old = set()
    for rel in old - set(tree):
        path = destination / rel
        if path.exists():
            path.unlink()
    for rel, content in tree.items():
        path = destination / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    generated_manifest.write_text(json.dumps({"files": sorted(tree), "sha256": {
        rel: hashlib.sha256(content).hexdigest() for rel, content in sorted(tree.items())}}, indent=2) + "\n",
                                  encoding="utf-8")


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
    changed, digest = differences(tree), source_digest()
    payload = {"changed": changed, "count": len(changed), "source_sha256": digest,
               "reconciliation": reconciliation(changed, digest)}
    if args.write:
        if reconciliation(changed, digest) == "target-changed":
            try:
                propagate_bodies_from_codex(tree)
            except ValueError as exc:
                return refuse({"code": "ct-reverse-refused", "message": str(exc)}, args.json)
            tree = generated_tree()
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
