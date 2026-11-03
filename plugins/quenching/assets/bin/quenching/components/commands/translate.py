"""The Claude-to-Codex prose translation a repository's legacy `.claude/` surface received.

The packaged Codex plugin this module once generated was retired with the plugin model (spec
2160): a target now gets its Codex skills from `cq deploy`. What stays is the per-file
translation `cq components migrate` uses to recognise a legacy translated copy, and the shell
helpers the Omnigent generator reuses. `CODEX_CQ_WRAPPER` is the exact text those legacy copies
carry, kept so they are still recognised.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from pathlib import Path

from quenching.common.output import NoAbbrevParser, finding, refuse, report_findings
from quenching.components.surface import generic_surface


SOURCE: Path | None = None
TARGET: Path | None = None
MANIFEST: Path | None = None
DROP_FRONTMATTER = {"argument-hint", "allowed-tools", "model", "context", "hooks"}
FORBIDDEN_AFTER_TRANSLATION = ("${CLAUDE_PLUGIN_ROOT}", "${CLAUDE_PROJECT_DIR}", "CLAUDE_PLUGIN_ROOT")
PLATFORM_NEUTRAL_CLAUDE_CODEX = "\u0043laude or \u0043odex"

CODEX_CQ_WRAPPER = r"""cq() {
  local plugin_root="${CODEX_PLUGIN_ROOT:-${PLUGIN_ROOT:-}}"
  if [ -z "$plugin_root" ]; then
    plugin_root="$(set -o pipefail
codex plugin list --json | python3 -c '
import json, os, sys
from pathlib import Path
plugins = [p for p in json.load(sys.stdin)["installed"] if p.get("name") == "quenching-codex" and p.get("enabled")]
if len(plugins) != 1:
    sys.exit("quenching-codex: enable exactly one installation, or provide its plugin root")
p = plugins[0]
home = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex")))
print(p.get("installedPath") or home / "plugins/cache" / p["marketplaceName"] / p["name"] / p["version"])
')" || return 2
  fi
  if [ -z "$plugin_root" ] || [ ! -f "$plugin_root/scripts/cq" ]; then
    echo "quenching-codex: installed plugin root not found; enable the plugin first" >&2
    return 2
  fi
  python3 "$plugin_root/scripts/cq" "$@"
}"""

CQ_INVOCATION = re.compile(r"(?<![A-Za-z0-9_./-])cq(?=\s+(?:--root|--version|--help|specs|knowledge|design|components|git|ops|proof|toolchain|delivery|security|opensource|config|portal|session)\b)")
EXPLICIT_CQ_INVOCATION = re.compile(r"python3\s+(?:\"?\.\./\.\./scripts/cq\"?|\"?scripts/bin/cq\"?)")
RELATIVE_CQ_PATH = re.compile(r"(?<![A-Za-z0-9_./])(?:python3\s+)?\"?\.\./\.\./scripts/cq\"?")


def payload_root() -> Path:
    """The installed payload — the source, or a target's `.agents/quenching/` — found by walking up
    to the directory that carries the adaptation map, whatever sits above it."""
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "assets" / "translation" / "codex-adaptation.json").is_file():
            return parent
    raise ValueError("the installed payload does not carry assets/translation/codex-adaptation.json")


def configure(source: str, target: str) -> None:
    """Resolve the pair once per invocation: a repository (or a payload) and where it translates to."""
    global SOURCE, TARGET, MANIFEST
    # The adaptation is part of the distributed translator, not of a target repository.
    MANIFEST = payload_root() / "assets" / "translation" / "codex-adaptation.json"
    SOURCE, TARGET = Path(source).resolve(), Path(target).resolve()


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


def read_adaptation() -> dict:
    return json.loads(manifest().read_text(encoding="utf-8"))


# Build artefacts are not source: `__pycache__/` and compiled files are gitignored, so a tree walk
# that hashes or copies them differs between a machine that ran `cq` and a fresh clone.
def _is_build_artefact(path: Path) -> bool:
    return "__pycache__" in path.parts or path.suffix in (".pyc", ".pyo")


def module_owners() -> dict[str, str]:
    """Command head -> owning module, from the distribution's own module manifest."""
    data = json.loads((payload_root() / "assets" / "modules.json").read_text(encoding="utf-8"))
    return {rel.removesuffix(".md"): module["name"] for module in data["modules"]
            for rel in module.get("owned", {}).get("commands", [])}


def transform_platform(text: str, adaptation: dict) -> str:
    neutral_marker = "\x00QUENCHING_PLATFORM_NEUTRAL_CLAUDE_CODEX\x00"
    text = text.replace(PLATFORM_NEUTRAL_CLAUDE_CODEX, neutral_marker)
    text = text.replace(".claude/quenching.json", "\x00SHARED_CONFIG\x00")
    text = text.replace("~/.claude/projects/", "\x00SOURCE_MEMORY_ROOT\x00")
    text = text.replace("Claude Code memory", "\x00SOURCE_MEMORY_NAME\x00")
    text = text.replace("Claude Code project memory", "\x00SOURCE_PROJECT_MEMORY_NAME\x00")
    for old, new in adaptation["replacements"].items():
        text = text.replace(old, new)
    owners = module_owners()

    def skill_id(match: re.Match) -> str:
        module, ident = match.group(1), match.group(2)
        if owners.get(ident.split(":", 1)[0]) != module:
            raise ValueError(f"no module owns /{module}:{ident}")
        return "quenching-" + ident.replace(":", "-")

    # Codex ships one plugin, so the module that owns a front leaves the skill id.
    text = re.sub(r"/(quenching-[a-z]+):([A-Za-z0-9:-]+)", skill_id, text)
    text = text.replace("Claude Code", "Codex").replace("Claude", "Codex")
    text = text.replace(neutral_marker, PLATFORM_NEUTRAL_CLAUDE_CODEX)
    text = text.replace("\x00SHARED_CONFIG\x00", ".claude/quenching.json")
    text = text.replace("\x00SOURCE_MEMORY_ROOT\x00", "~/.claude/projects/")
    text = text.replace("\x00SOURCE_MEMORY_NAME\x00", "Claude Code memory")
    text = text.replace("\x00SOURCE_PROJECT_MEMORY_NAME\x00", "Claude Code project memory")
    for marker in FORBIDDEN_AFTER_TRANSLATION:
        if marker in text:
            raise ValueError(f"untranslated platform marker: {marker}")
    return text


def transform_codex_runtime(text: str, adaptation: dict) -> str:
    """Adapt executable Markdown, keeping code examples and source runtime pins intact."""
    models = adaptation["runtime"]["models"]
    # Fenced fixtures and historical snippets are data. Agent YAML frontmatter is active.
    pieces = re.split(r"(```[^\n]*\n[\s\S]*?```)", text)
    for index in range(0, len(pieces), 2):
        pieces[index] = re.sub(r"\b(opus|sonnet|haiku)\b",
                               lambda match: models[match.group()], pieces[index])
        pieces[index] = pieces[index].replace("`TaskStop`", "the host's interrupt-agent tool")
    text = "".join(pieces)
    text = re.sub(r"8\. \*\*Telemetry\.\*\*[\s\S]*?(?=\n## Hard prohibitions)",
        "8. **Telemetry.** Record host-provided usage per Codex model and agent role, never sum "
        "tiers. If the host exposes no token telemetry, report `not measured`; never invoke "
        "Claude transcript/session tools or infer tokens from output length. Audit launched roles "
        "from host agent metadata; state when that audit could not run.\n", text)
    text = text.replace("read with\n`cq components session cost`", "from host-provided Codex telemetry (otherwise `not measured`)")
    text = text.replace("fresh `claude -p`", "fresh Codex host sessions")
    text = text.replace(", Bash(cq components session cost:*)", "")
    text = text.replace("for `claude --agent`", "for the source platform's top-level agent launcher")
    text = text.replace("A worker with no activity for more than **20 min** (its transcript's mtime) and no\n  live child process is stopped with the host's interrupt-agent tool and relaunched **once**.",
        "A worker confirmed inactive for more than **20 min** through host activity/status metadata "
        "and with no active work is interrupted through the host tool and relaunched **once**. "
        "If the host cannot expose activity or active-work evidence, report liveness as unmeasured; "
        "do not infer a stall or restart from silence alone.")
    return text


def codex_runtime_policy(adaptation: dict) -> str:
    models = adaptation["runtime"]["models"]
    return ("## Codex runtime\n\n"
        "Use Codex host sub-agents only. Never launch Claude CLI, request Claude models, or "
        "fall back to Claude during a Codex run. The Claude source may separately delegate "
        "development to Codex. Read each named agent protocol and pass its role, prohibitions, "
        "model and effort to the host's spawn-agent tool; protocol files are not automatically "
        "registered agent types. Use host messaging, completion notifications and interrupt tools "
        "for lifecycle management. If delegation is unavailable, report the limitation; do not "
        "silently replace required independent verification with self-review.\n\n"
        f"Tier mapping: opus → `{models['opus']}`; sonnet → `{models['sonnet']}`; "
        f"haiku → `{models['haiku']}`. Preserve declared effort. Pass model explicitly; "
        "when the host requires a fresh context for model overrides, use that mode and include "
        "the necessary brief and protocol. Use gpt-6-luna for product code only on ONE task "
        "whose `cq specs estimate --task` reports `oracleProtected` and `smallTierEligible` "
        "(an executable `verify:` whose tests sit outside the task's `files:`, nothing under "
        "`/docs/`, projected context at or under 80k); a failed `verify:` returns it to the "
        "session model. Never use gpt-6-luna for judgment roles or for import-memory "
        "classification/executor roles. Report tokens per model and role only "
        "when host telemetry provides them; otherwise `not measured`. Claude session logs and "
        "`cq components session cost` do not measure this Codex run.\n\n")


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
        "The executable checker is `cq`\n(`cq knowledge validate docs` → exit 0 = conforms). Invoke it by its **literal quoted\n"
        "path** on every call, never through a shell variable holding the interpreter plus the path —",
        "The executable checker is `cq`\n(`cq knowledge validate docs` → exit 0 = conforms). Define the per-call wrapper from\n"
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
    wrapper resolving the enabled plugin copy instead of relying on state from a
    previous call or on a host-specific PATH mutation.
    """
    lines = text.splitlines()
    output: list[str] = []
    in_bash = False
    block: list[str] = []

    def flush_block() -> None:
        if has_cq_invocation("\n".join(block)):
            body = [EXPLICIT_CQ_INVOCATION.sub("cq", line) for line in block]
            output.extend(CODEX_CQ_WRAPPER.splitlines())
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


def skill_name(command: Path) -> str:
    commands = source() / "commands" if plugin_translation() else claude_surface() / "commands"
    return "quenching-" + "-".join(command.relative_to(commands).with_suffix("").parts)


def skill_description(description: str) -> str:
    """Keep the source description, including its routing boundary, intact."""
    return description.strip()


FLOW_SHORTCUTS = frozenset(f"specs/{flow}" for flow in (
    "create", "develop", "execute", "conclude", "triage", "status", "orchestrate"))


def apply_removals(body: str, command_id: str, adaptation: dict) -> str:
    """Cut the spans `removals` declares for this command (a Codex run never nests Codex).

    A marker the source no longer carries is an error: the rule would otherwise go silent.
    """
    for rule in adaptation.get("removals", []):
        if rule["command"] != command_id:
            continue
        start = body.find(rule["from"])
        if start < 0:
            raise ValueError(f"removal marker not found in {command_id}: {rule['from'][:60]!r}")
        stop = start + len(rule["from"])
        if "until" in rule:
            stop = body.find(rule["until"], stop)
            if stop < 0:
                raise ValueError(f"removal end marker not found in {command_id}: {rule['until'][:60]!r}")
        body = body[:start] + rule["replace"] + body[stop:]
    return body


def command_to_skill(command: Path, adaptation: dict, raw: str | None = None) -> str:
    """`raw` translates another version of `command`'s text (`cq components migrate` reads history)."""
    raw = command.read_text(encoding="utf-8") if raw is None else raw
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
              f"description: {json.dumps(transform_platform(skill_description(fields['description']), adaptation), ensure_ascii=False)}\n" +
              f"---\n\n<!-- GENERATED FROM {origin} -->\n\n")
    pin = re.search(r"^model: (opus|sonnet|haiku)$", raw[4:end], re.MULTILINE)
    preference = ("Preferred model: `" + adaptation["runtime"]["models"][pin.group(1)] + "`.\n\n") if pin else ""
    effort = re.search(r"^effort: ([a-z]+)$", raw[4:end], re.MULTILINE)
    if command.name == "import-memory.md":
        preference += ("Memory input: existing Claude-format project memory data under `~/.claude/projects/`; "
                       "reading this data does not launch Claude. No Codex memory layout is assumed.\n\n")
    if effort:
        preference += "Declared effort: `" + effort.group(1) + "`.\n\n"
    commands_dir = source() / "commands" if plugin_translation() else claude_surface() / "commands"
    command_id = command.relative_to(commands_dir).with_suffix("").as_posix()
    body = raw[end + len("\n---\n"):]
    if command_id not in FLOW_SHORTCUTS:  # a shortcut's removals run on its flow's reference
        body = apply_removals(body, command_id, adaptation)
    return header + "<!-- CODEX RUNTIME START -->\n" + preference + codex_runtime_policy(adaptation) + "<!-- CODEX RUNTIME END -->\n\n" + transform_codex_markdown(transform_platform(
        transform_codex_runtime(body, adaptation), adaptation))


def skill_policy(command: Path, raw: str | None = None) -> bytes | None:
    """Codex's `agents/openai.yaml` that keeps a `disable-model-invocation` command human-only."""
    raw = command.read_text(encoding="utf-8") if raw is None else raw
    end = raw.find("\n---\n", 4) if raw.startswith("---\n") else -1
    flagged = any(line.strip().lower() == "disable-model-invocation: true"
                  for line in raw[4:end].splitlines()) if end > 0 else False
    return b"policy:\n  allow_implicit_invocation: false\n" if flagged else None


def reference_translation(reference: Path, text: str, adaptation: dict) -> str:
    """What a repository's `.claude/references/<rel>` becomes under `.agents/references/<rel>`."""
    if reference.suffix == ".md" and reference.parent.name == "specs-flows":
        # A moved flow keeps the removals its command declared (a Codex run never nests Codex).
        text = apply_removals(text, f"specs/{reference.stem}", adaptation)
    if reference.suffix == ".md":
        text = transform_codex_runtime(text, adaptation)
    text = transform_platform(text, adaptation)
    if reference.suffix == ".md":
        text = transform_codex_markdown(text)
    return text


def previous_files(manifest: Path, destination: Path) -> set[str] | None:
    """Read the paths a previous run owned, refusing any that would leave the destination.

    The manifest is versioned and mergeable, so every entry is untrusted input: all are checked
    before the caller deletes the first. A manifest that is not JSON at all (merge conflict
    markers) returns None: the caller recovers by regenerating it.
    """
    if not manifest.exists():
        return set()
    try:
        document = json.loads(manifest.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    try:
        files = document["files"]
    except (KeyError, TypeError) as exc:
        raise ValueError(f"{manifest.name} is unreadable or has no `files`: {exc!r}") from exc
    if not isinstance(files, (list, dict)):
        raise ValueError(f"{manifest.name} `files` must be a list or an object")
    contain(files, destination, manifest.name)
    return set(files)


def contain(files, destination: Path, origin: str) -> None:
    """Refuse any path that would resolve outside the destination, before the caller touches one."""
    root = destination.resolve()
    for rel in files:
        if not isinstance(rel, str) or not rel or Path(rel).is_absolute() \
                or not (destination / rel).resolve().is_relative_to(root):
            raise ValueError(f"{origin} names a path outside the destination: {rel!r}")


