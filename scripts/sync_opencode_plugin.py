#!/usr/bin/env python3
"""Generate and validate the OpenCode distribution of the quenching plugin.

`plugins/quenching/` is the only editable source. This generator lays the command surface out as
an OpenCode configuration directory, `plugins/quenching-opencode/`:

  commands/quenching-<front>-<verb>.md   one OpenCode command per source command
  agents/quenching-<agent>.md            one OpenCode subagent per source agent (deny-only permissions)
  quenching/                             the payload: references, templates, specs, knowledge,
                                         design, portal, agent protocols and the bundled `cq`

Markdown is translated from the Claude source with the OpenCode vocabulary below; the `cq`
payload (`quenching/scripts/`) is the Codex translator's own output, carried verbatim, so `cq`
behaves on OpenCode exactly as it does on Codex. `--check` compares bytes and validates the
generated tree; `--write` regenerates it.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "plugins/quenching/assets/bin"))
from quenching.components.commands import translate  # noqa: E402

SOURCE = REPO / "plugins/quenching"
TARGET = REPO / "plugins/quenching-opencode"
CODEX_TARGET = REPO / "plugins/quenching-codex"
MANIFEST = ".generated-files.json"
ROOT = "~/.config/opencode/quenching"
PAYLOAD_DIRS = ("references", "templates", "specs", "knowledge", "design", "portal")
AGENT_PREFIX = "quenching-"

OPENCODE_CQ_WRAPPER = ('cq() { python3 "${QUENCHING_OPENCODE_ROOT:-${XDG_CONFIG_HOME:-$HOME/.config}'
                       '/opencode/quenching}/scripts/cq" "$@"; }')

# Order matters: the longest, most specific prefix first.
REPLACEMENTS = (
    ("python3 ${CLAUDE_PLUGIN_ROOT}/assets/bin/cq", "cq"),
    ("${CLAUDE_PLUGIN_ROOT}/assets/bin/cq", "cq"),
    ("${CLAUDE_PLUGIN_ROOT}/assets/", ROOT + "/"),
    ("${CLAUDE_PLUGIN_ROOT}/agents/", ROOT + "/agents/"),
    ("${CLAUDE_PLUGIN_ROOT}", ROOT),
    ("${CLAUDE_PROJECT_DIR}", "."),
    ("plugins/quenching/agents/", ROOT + "/agents/"),
    (".claude/commands/", ".opencode/commands/"),
    (".claude/agents/", ".opencode/agents/"),
    (".claude/skills/", ".opencode/skills/"),
    ("CLAUDE.md", "AGENTS.md"),
)
# Literal strings that name the Claude side on purpose and must survive the word mapping.
PROTECTED = ("Claude or Codex", ".claude/quenching.json", "~/.claude/projects/",
             "Claude Code project memory", "Claude Code memory")
FORBIDDEN = ("${CLAUDE_PLUGIN_ROOT}", "${CLAUDE_PROJECT_DIR}", "CLAUDE_PLUGIN_ROOT",
             "codex plugin list", "../../scripts/cq")


def agent_names() -> list[str]:
    return sorted(path.stem for path in (SOURCE / "agents").glob("*.md"))


def platform(text: str) -> str:
    """Translate Claude vocabulary, paths and module-qualified ids to their OpenCode form."""
    masks = {f"\x00P{index}\x00": literal for index, literal in enumerate(PROTECTED)}
    for marker, literal in masks.items():
        text = text.replace(literal, marker)
    for old, new in REPLACEMENTS:
        text = text.replace(old, new)
    owners = translate.module_owners()

    def command_id(match: re.Match) -> str:
        module, ident = match.group(1), match.group(2)
        if owners.get(ident.split(":", 1)[0]) != module:
            raise ValueError(f"no module owns /{module}:{ident}")
        return "quenching-" + ident.replace(":", "-")

    text = re.sub(r"/(quenching-[a-z]+):([A-Za-z0-9:-]+)", command_id, text)
    agents = "|".join(map(re.escape, agent_names()))
    text = re.sub(rf"\bquenching-[a-z]+:({agents})\b", lambda m: AGENT_PREFIX + m.group(1), text)
    text = text.replace("Claude Code", "OpenCode").replace("Claude", "OpenCode")
    for marker, literal in masks.items():
        text = text.replace(marker, literal)
    for marker in FORBIDDEN:
        if marker in text:
            raise ValueError(f"untranslated platform marker: {marker}")
    return text


def markdown(text: str) -> str:
    """Platform pass, then the per-call `cq` wrapper in every bash block that invokes it."""
    shelled = translate.transform_codex_shell_blocks(platform(text))
    return shelled.replace(translate.CODEX_CQ_WRAPPER, OPENCODE_CQ_WRAPPER)


def tool_resolution(text: str) -> str:
    start = text.index("## Resolving the tool")
    return text[:start] + f"""## Resolving the tool

OpenCode does **not** require `cq` on the user's PATH. A bare `cq` in the examples below means the
shell function defined at the start of the same bash call:

```bash
{OPENCODE_CQ_WRAPPER}
```

It runs the bundled `scripts/cq` of the installed payload — `$QUENCHING_OPENCODE_ROOT` when set,
else `~/.config/opencode/quenching`. Define it again in every bash call: shell state does not
survive between calls, and a subagent may start with a fresh environment. Never install `cq`
into a target repository and never edit the user's PATH to make it resolve.

Branch on the **exit code** (0 ok · 1 findings · 2 refusal) and the `--json` payload, never on
prose.

### Write the resolved path literally on every invocation

Do not copy a relative path from a reference into a command; the wrapper above is the portable
form, including for subagents.

**Chain several writes so a failure stops the run** — `set -e`, or `&&` between them.
"""


def runtime_policy() -> str:
    return ("## OpenCode runtime\n\n"
            "Delegate only through OpenCode's task tool, to the registered subagents named "
            "`quenching-<agent>` (protocol copies live under `" + ROOT + "/agents/`). Never launch "
            "the Claude CLI and never request a Claude model during an OpenCode run. Source model "
            "tiers are not pinned here: every command and subagent runs on the model the OpenCode "
            "session configures; a declared tier or effort below is a preference to report, not a "
            "switch. Token usage comes from host telemetry when it exists, otherwise it is "
            "`not measured`; `cq components session cost` and `context` read no OpenCode log and "
            "refuse (exit 2, unmeasured). If delegation is unavailable, report the limitation; never "
            "replace a required independent verification with self-review.\n\n")


def frontmatter(raw: str, path: Path) -> tuple[dict[str, str], str]:
    """The source's scalar frontmatter fields (folded descriptions joined) and its body."""
    if not raw.startswith("---\n") or (end := raw.find("\n---\n", 4)) < 0:
        raise ValueError(f"missing or malformed frontmatter: {path}")
    fields, lines, index = {}, raw[4:end].splitlines(), 0
    while index < len(lines):
        key, _, value = lines[index].partition(":")
        value, index = value.strip(), index + 1
        if value in {">", ">-", "|", "|-"}:
            pieces = []
            while index < len(lines) and lines[index].startswith((" ", "\t")):
                pieces.append(lines[index].strip())
                index += 1
            value = " ".join(pieces)
        fields[key.strip()] = value
    if not fields.get("description"):
        raise ValueError(f"no description: {path}")
    return fields, raw[end + len("\n---\n"):]


def preferences(fields: dict[str, str]) -> str:
    text = f"Source model tier: `{fields['model']}`.\n\n" if fields.get("model") else ""
    return text + (f"Declared effort: `{fields['effort']}`.\n\n" if fields.get("effort") else "")


def permissions(tools: str | None) -> dict[str, str]:
    """Deny-only mapping of a source `tools:` list: the generated agent is never wider."""
    if tools is None:
        return {}
    names = [item.strip() for item in re.split(r",\s*(?![^()]*\))", tools) if item.strip()]
    heads = {name.split("(", 1)[0] for name in names}
    granted = {}
    granted["edit"] = "allow" if heads & {"Edit", "Write", "NotebookEdit"} else "deny"
    granted["webfetch"] = "allow" if "WebFetch" in heads else "deny"
    granted["bash"] = "allow" if "Bash" in names else "ask" if "Bash" in heads else "deny"
    granted["task"] = "allow" if heads & {"Agent", "Task"} else "deny"
    return granted


def command_file(command: Path) -> str:
    fields, body = frontmatter(command.read_text(encoding="utf-8"), command)
    origin = "plugins/quenching/commands/" + command.relative_to(SOURCE / "commands").as_posix()
    return ("---\n" + f"description: {json.dumps(platform(fields['description']), ensure_ascii=False)}\n"
            + f"---\n\n<!-- GENERATED FROM {origin} -->\n\n<!-- OPENCODE RUNTIME START -->\n"
            + preferences(fields) + runtime_policy() + "<!-- OPENCODE RUNTIME END -->\n\n"
            + markdown(body))


def agent_files(agent: Path) -> tuple[str, str]:
    """The registered OpenCode subagent and its protocol copy under the payload."""
    fields, body = frontmatter(agent.read_text(encoding="utf-8"), agent)
    protocol = markdown(body) + "\n" + runtime_policy()
    granted = permissions(fields.get("tools"))
    tools = {"task": False} if granted.pop("task", "allow") == "deny" else {}
    header = ["---", f"description: {json.dumps(platform(fields['description']), ensure_ascii=False)}",
              "mode: subagent"]
    if granted:
        header += ["permission:"] + [f"  {key}: {value}" for key, value in granted.items()]
    if tools:
        header += ["tools:"] + [f"  {key}: false" for key in tools]
    origin = f"plugins/quenching/agents/{agent.name}"
    registered = ("\n".join(header) + f"\n---\n\n<!-- GENERATED FROM {origin} -->\n\n"
                  + preferences(fields) + protocol)
    return registered, protocol


def readme(commands: int, agents: int) -> str:
    return f"""# quenching-opencode (generated)

This OpenCode distribution is generated from `plugins/quenching/`, the only editable source. Run
`python3 scripts/sync_opencode_plugin.py --write` to refresh it; never edit it by hand.

It carries {commands} commands (`commands/`), {agents} subagents (`agents/`) and the payload they
cite (`quenching/`, including the bundled `cq`).

## Install

Copy the three parts into the OpenCode configuration directory:

```bash
mkdir -p ~/.config/opencode
cp -R commands agents ~/.config/opencode/
cp -R quenching ~/.config/opencode/quenching
```

Commands run as `/quenching-<front>-<verb>` (`opencode run --command quenching-specs-status`).
Prose paths assume `{ROOT}`; `cq` honours `QUENCHING_OPENCODE_ROOT` for another root.
Commands and subagents pin no model: the session's configured model runs every role.
"""


def generated_tree() -> dict[str, bytes]:
    out: dict[str, str | bytes] = {}
    commands = sorted((SOURCE / "commands").rglob("*.md"))
    for command in commands:
        name = "quenching-" + "-".join(command.relative_to(SOURCE / "commands").with_suffix("").parts)
        out[f"commands/{name}.md"] = command_file(command)
    for name in agent_names():
        registered, protocol = agent_files(SOURCE / "agents" / f"{name}.md")
        out[f"agents/{AGENT_PREFIX}{name}.md"] = registered
        out[f"quenching/agents/{name}.md"] = protocol
    for directory in PAYLOAD_DIRS:
        root = SOURCE / "assets" / directory
        for path in sorted(p for p in root.rglob("*") if p.is_file() and not translate._is_build_artefact(p)):
            relative = path.relative_to(root)
            if relative.name == "CLAUDE.md":
                relative = relative.with_name("AGENTS.md")
            text = path.read_text(encoding="utf-8")
            if relative.as_posix() == "align/tool-resolution.md" and directory == "references":
                text = tool_resolution(text)
            out[f"quenching/{directory}/{relative.as_posix()}"] = (
                markdown(text) if path.suffix == ".md" else platform(text))
    translate.configure(str(SOURCE), str(CODEX_TARGET))
    for rel, content in translate.generated_tree().items():
        if rel.startswith("scripts/"):
            out[f"quenching/{rel}"] = content
    out["README.md"] = readme(len(commands), len(agent_names()))
    out[".generated-from.json"] = json.dumps({"source": "plugins/quenching",
        "generator": "scripts/sync_opencode_plugin.py", "command_count": len(commands),
        "agent_count": len(agent_names())}, indent=2) + "\n"
    return {rel: value if isinstance(value, bytes) else value.encode("utf-8")
            for rel, value in sorted(out.items())}


def validate(tree: dict[str, bytes]) -> list[str]:
    """Structural findings over the generated tree; empty means it is usable on OpenCode."""
    problems = []
    commands = [rel for rel in tree if rel.startswith("commands/")]
    agents = [rel for rel in tree if rel.startswith("agents/")]
    if len(commands) != len(list((SOURCE / "commands").rglob("*.md"))):
        problems.append("command count differs from the source")
    if len(agents) != len(agent_names()):
        problems.append("agent count differs from the source")
    for rel in commands + agents:
        text = tree[rel].decode("utf-8")
        if not re.match(r"---\ndescription: \".+\"\n", text):
            problems.append(f"{rel}: no description frontmatter")
        if rel.startswith("agents/") and "\nmode: subagent\n" not in text.split("\n---\n", 1)[0]:
            problems.append(f"{rel}: not mode: subagent")
        if re.search(r"\.\./\.\./(?:references|templates|specs|knowledge|scripts|agents|checks)/", text):
            problems.append(f"{rel}: relative payload path")
    for rel, content in tree.items():
        if not rel.endswith(".md") or rel.startswith("quenching/scripts/"):
            continue
        text = content.decode("utf-8")
        for marker in FORBIDDEN:
            if marker in text:
                problems.append(f"{rel}: carries {marker}")
        for block in re.findall(r"^\s*```bash\n([\s\S]*?)^\s*```", text, re.MULTILINE):
            if translate.has_cq_invocation(block) and OPENCODE_CQ_WRAPPER not in block:
                problems.append(f"{rel}: a bash block invokes cq without the OpenCode wrapper")
    return problems


def manifest_document(tree: dict[str, bytes]) -> bytes:
    return (json.dumps({"files": sorted(tree), "sha256": {rel: hashlib.sha256(content).hexdigest()
                        for rel, content in sorted(tree.items())}}, indent=2) + "\n").encode()


def on_disk(target: Path) -> set[str]:
    if not target.is_dir():
        return set()
    return {path.relative_to(target).as_posix() for path in target.rglob("*")
            if path.is_file() and path.name != MANIFEST and not translate._is_build_artefact(path)}


def differences(tree: dict[str, bytes], target: Path) -> list[str]:
    changed = [rel for rel in sorted(set(tree) | on_disk(target))
               if rel not in tree or not (target / rel).is_file() or (target / rel).read_bytes() != tree[rel]]
    manifest = target / MANIFEST
    if not manifest.is_file() or manifest.read_bytes() != manifest_document(tree):
        changed.append(MANIFEST)
    return changed


def write(tree: dict[str, bytes], target: Path) -> None:
    previous = translate.previous_files(target / MANIFEST, target)
    previous = on_disk(target) if previous is None else previous
    translate.contain(previous | set(tree), target, "the destination")
    for rel in sorted(previous - set(tree)):
        if (target / rel).is_file():
            (target / rel).unlink()
    for rel, content in tree.items():
        (target / rel).parent.mkdir(parents=True, exist_ok=True)
        (target / rel).write_bytes(content)
    (target / MANIFEST).write_bytes(manifest_document(tree))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="sync_opencode_plugin.py", description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--write", action="store_true")
    parser.add_argument("--target", default=str(TARGET))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    target = Path(args.target).resolve()
    try:
        tree = generated_tree()
    except ValueError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}) if args.json else f"refused: {exc}", file=sys.stderr)
        return 2
    problems = validate(tree)
    if args.write and not problems:
        write(tree, target)
    changed = [] if args.write and not problems else differences(tree, target)
    payload = {"ok": not problems and not changed, "commands": sum(r.startswith("commands/") for r in tree),
               "agents": sum(r.startswith("agents/") for r in tree), "changed": changed,
               "count": len(changed), "findings": problems}
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"opencode distribution — {payload['commands']} commands, {payload['agents']} agents, "
              f"{len(changed)} changed file(s), {len(problems)} finding(s)")
        for line in problems + [f"drift: {rel}" for rel in changed]:
            print("  " + line)
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
