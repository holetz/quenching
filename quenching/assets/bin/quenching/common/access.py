"""Out-of-tree access: the worktree slots and the sibling stores, one derivation per client.

The slots (`<parent>/<repo>-slot-*`) and the sibling stores (`<primary>.*`) live outside the
project folder. Every client asks for them in its own artifact: OpenCode under
`permission.external_directory` and `permission.bash`, Claude Code under `permissions.allow`, the
VS Code workspace under `chat.tools.terminal.*`. This module derives the family once, from the
repository's git common dir (so a command run inside a slot names the primary's family), and
renders each declaration and the report `cq doctor --access` prints.

Read-only: nothing here writes a file.
"""
from __future__ import annotations

import glob
import json
import os
import subprocess

from quenching.common.jsonc import jsonc_loads

OPENCODE = "opencode.json"
CLAUDE = ".claude/settings.json"
VSCODE = ".vscode/settings.json"

AUTO_APPROVE = "chat.tools.terminal.autoApprove"
BLOCK_WRITES = "chat.tools.terminal.blockDetectedFileWrites"
BLOCK_VALUE = "never"

# The `cq` entry point with any arguments: the relative form, the `./` form and the python-prefixed
# form the hooks and the fallback use. VS Code matches the regex against each command of a chain.
VSCODE_AUTO_APPROVE = {
    r"/^\.agents\/quenching\/bin\/cq(\s|$)/": True,
    r"/^\.\/\.agents\/quenching\/bin\/cq(\s|$)/": True,
    r"/^python3? \.agents\/quenching\/bin\/cq(\s|$)/": True,
}

# The Bash rules the deploy appends to `.claude/settings.json`; the file tools get one rule per
# family pattern, so `Read/Edit/Write` name the slots and the stores exactly.
CLAUDE_BASH = (
    "Bash(.agents/quenching/bin/cq:*)",
    "Bash(./.agents/quenching/bin/cq:*)",
    "Bash(python3 .agents/quenching/bin/cq:*)",
    "Bash(python .agents/quenching/bin/cq:*)",
)
CLAUDE_FILE_TOOLS = ("Read", "Edit", "Write")

# The shell patterns the deploy writes under `permission.bash`; OpenCode matches the command text.
OPENCODE_BASH = (
    ".agents/quenching/bin/cq",
    ".agents/quenching/bin/cq *",
    "./.agents/quenching/bin/cq *",
    "python3 .agents/quenching/bin/cq *",
    "python .agents/quenching/bin/cq *",
)

_TIMEOUT = 15


def primary(root: str) -> tuple[str | None, str | None]:
    """`(primary checkout, reason)` from the git common dir: a slot resolves to its primary."""
    try:
        done = subprocess.run(["git", "-C", str(root), "rev-parse", "--path-format=absolute",
                               "--git-common-dir"], capture_output=True, text=True,
                              encoding="utf-8", errors="replace", timeout=_TIMEOUT)
    except (OSError, subprocess.SubprocessError) as error:
        return None, str(error)
    common = done.stdout.strip()
    if done.returncode != 0 or not common:
        return None, "not a git checkout"
    common = os.path.normpath(common)
    if os.path.basename(common) != ".git":
        return None, "the git directory does not end in .git"
    return os.path.dirname(common), None


def patterns(primary_root: str, home: str | None = None) -> list[str]:
    """The family as OpenCode/Claude read it: slots and store, `~/` when under the home dir."""
    path = os.path.normpath(primary_root).replace(os.sep, "/")
    parent, name = path.rsplit("/", 1)
    found = [f"{parent}/{name}-slot-*", f"{path}.*"]
    if home:
        home = os.path.normpath(home).replace(os.sep, "/").rstrip("/")
        found = ["~" + item[len(home):] if item.startswith(home + "/") else item
                 for item in found]
    return found


def _rule_path(pattern: str) -> str:
    """A family pattern as a Claude permission rule path: `~/` stays, absolute takes `//`."""
    return pattern if pattern.startswith("~/") else "//" + pattern.lstrip("/")


def claude_rules(primary_root: str, home: str | None = None) -> list[str]:
    """The `permissions.allow` rules that name the family and the CLI entry point."""
    rules = list(CLAUDE_BASH)
    for pattern in patterns(primary_root, home):
        rules.extend(f"{tool}({_rule_path(pattern)}/**)" for tool in CLAUDE_FILE_TOOLS)
    return rules


def vscode_block() -> dict:
    """The workspace keys that stop the terminal prompt and the outside-workspace write block."""
    return {AUTO_APPROVE: dict(VSCODE_AUTO_APPROVE), BLOCK_WRITES: BLOCK_VALUE}


def vscode_snippet() -> str:
    """The JSONC block `cq doctor --access` prints, with the risk it carries in its header."""
    header = (
        "// The quenching terminal access: the `cq` entry point is approved without a prompt,\n"
        "// and `blockDetectedFileWrites: never` stops the outside-workspace write block that the\n"
        "// slots and the sibling stores would otherwise trigger. It applies to every command in\n"
        "// this workspace. `cq doctor --access` checks these keys.\n"
    )
    return header + json.dumps(vscode_block(), indent=2, ensure_ascii=False) + "\n"


def sibling_directories(primary_root: str) -> list[str]:
    """The slot and store directories that exist beside the primary checkout, sorted."""
    path = os.path.normpath(primary_root)
    parent, name = os.path.split(path)
    found = sorted(glob.glob(os.path.join(glob.escape(parent), glob.escape(name) + "-slot-*")))
    found += sorted(glob.glob(os.path.join(glob.escape(parent), glob.escape(name) + ".*")))
    return [item for item in found if os.path.isdir(item)]


def copilot_invocation(primary_root: str) -> str:
    """The Copilot CLI invocation: one `--add-dir` per existing sibling directory, never the parent."""
    directories = sibling_directories(primary_root)
    return " ".join(["copilot", *(f'--add-dir "{item}"' for item in directories)])


def _static_parent(pattern: str) -> str:
    """The directory before the first glob segment: the part a moved checkout stops matching."""
    path = os.path.expanduser(pattern)
    kept: list[str] = []
    for part in path.split("/"):
        if any(char in part for char in "*?["):
            break
        kept.append(part)
    return "/".join(kept) or os.sep


def _read_json(path: str) -> tuple[dict | None, str | None]:
    try:
        with open(path, encoding="utf-8") as handle:
            text = handle.read()
    except OSError:
        return None, "absent"
    try:
        document = json.loads(text)
    except ValueError as error:
        return None, f"unreadable: {error}"
    if not isinstance(document, dict):
        return None, "unreadable: the root must be an object"
    return document, None


def _read_jsonc(path: str) -> tuple[dict | None, str | None]:
    try:
        with open(path, encoding="utf-8") as handle:
            text = handle.read()
    except OSError:
        return None, "absent"
    try:
        document = jsonc_loads(text)
    except ValueError as error:
        return None, f"unreadable: {error}"
    if not isinstance(document, dict):
        return None, "unreadable: the root must be an object"
    return document, None


def _opencode_report(root: str, wanted: list[str]) -> dict:
    path = os.path.join(root, OPENCODE)
    document, error = _read_jsonc(path)
    out = {"path": OPENCODE, "state": "absent" if error == "absent" else "present",
           "patterns": [], "missingPatterns": list(wanted), "stalePatterns": [],
           "bash": [], "missingBash": list(OPENCODE_BASH)}
    if document is None:
        if error != "absent":
            out.update(state="unreadable", reason=error)
        return out
    permission = document.get("permission")
    permission = permission if isinstance(permission, dict) else {}
    directories = permission.get("external_directory")
    recorded = list(directories) if isinstance(directories, dict) else []
    bash = permission.get("bash")
    shell = list(bash) if isinstance(bash, dict) else []
    out.update(patterns=recorded, missingPatterns=[p for p in wanted if p not in recorded],
               stalePatterns=[p for p in recorded if not os.path.isdir(_static_parent(p))],
               bash=shell, missingBash=[p for p in OPENCODE_BASH if p not in shell])
    return out


def _claude_report(root: str, wanted: list[str]) -> dict:
    path = os.path.join(root, CLAUDE)
    document, error = _read_json(path)
    out = {"path": CLAUDE, "state": "absent" if error == "absent" else "present",
           "rules": [], "missingRules": list(wanted)}
    if document is None:
        if error != "absent":
            out.update(state="unreadable", reason=error)
        return out
    permissions = document.get("permissions")
    allow = permissions.get("allow") if isinstance(permissions, dict) else None
    rules = [rule for rule in allow if isinstance(rule, str)] if isinstance(allow, list) else []
    out.update(rules=rules, missingRules=[rule for rule in wanted if rule not in rules])
    return out


def _vscode_report(root: str) -> dict:
    path = os.path.join(root, VSCODE)
    document, error = _read_jsonc(path)
    out = {"path": VSCODE, "state": "absent" if error == "absent" else "present",
           "keys": {key: False for key in (AUTO_APPROVE, BLOCK_WRITES)},
           "autoApprove": {}, "blockDetectedFileWrites": None, "complete": False}
    if document is None:
        if error != "absent":
            out.update(state="unreadable", reason=error)
        return out
    approve = document.get(AUTO_APPROVE)
    approve = approve if isinstance(approve, dict) else {}
    block = document.get(BLOCK_WRITES)
    keys = {key: False for key in (AUTO_APPROVE, BLOCK_WRITES)}
    keys[AUTO_APPROVE] = all(approve.get(pattern) is True for pattern in VSCODE_AUTO_APPROVE)
    keys[BLOCK_WRITES] = block == BLOCK_VALUE
    return {"path": VSCODE, "state": "present", "keys": keys,
            "autoApprove": {pattern: approve[pattern] for pattern in VSCODE_AUTO_APPROVE
                            if pattern in approve},
            "blockDetectedFileWrites": block, "complete": all(keys.values())}


def report(root: str) -> dict:
    """What each client declares today, and what is missing or stale against the live family."""
    root = os.path.abspath(root)
    home = os.path.expanduser("~")
    primary_root, reason = primary(root)
    family = {"state": "absent", "reason": reason}
    wanted: list[str] = []
    rules: list[str] = []
    directories: list[str] = []
    invocation = None
    if primary_root:
        wanted = patterns(primary_root, home)
        rules = claude_rules(primary_root, home)
        directories = sibling_directories(primary_root)
        invocation = copilot_invocation(primary_root)
        family = {"state": "present", "primary": primary_root, "patterns": wanted,
                  "directories": directories}
    opencode = _opencode_report(root, wanted)
    claude = _claude_report(root, rules)
    vscode = _vscode_report(root)
    complete = (family["state"] == "present"
                and not opencode["missingPatterns"] and not opencode["missingBash"]
                and not opencode["stalePatterns"]
                and not claude["missingRules"] and vscode["complete"])
    return {"root": root, "family": family, "opencode": opencode, "claude": claude,
            "vscode": vscode,
            "copilotCli": {"invocation": invocation, "directories": directories},
            "complete": complete}


def summary(value: dict) -> str:
    """One line for the default `cq doctor`: what each client still lacks."""
    family = value["family"]
    if family["state"] != "present":
        return f"access: no family — {family.get('reason')}"
    gaps = []
    for name, item, missing in (("opencode", value["opencode"], "missingPatterns"),
                                ("opencode", value["opencode"], "missingBash"),
                                ("claude", value["claude"], "missingRules")):
        if item[missing]:
            gaps.append(f"{name} {len(item[missing])} missing")
    if value["opencode"]["stalePatterns"]:
        gaps.append(f"opencode {len(value['opencode']['stalePatterns'])} stale")
    if not value["vscode"]["complete"]:
        gaps.append(f"vscode {value['vscode']['state']}")
    if not gaps:
        gaps.append("complete")
    return ("access: " + ", ".join(gaps)
            + f" — copilot CLI {len(value['copilotCli']['directories'])} dir(s)")


def human(value: dict) -> str:
    """The full `cq doctor --access` text: every client, the VS Code block and the CLI line."""
    lines = [f"cq doctor --access — {value['root']}", ""]
    family = value["family"]
    if family["state"] != "present":
        lines.append(f"family: absent — {family.get('reason')}")
    else:
        lines.append(f"family: {family['primary']}")
        lines.extend(f"  {pattern}" for pattern in family["patterns"])
    for name in ("opencode", "claude", "vscode"):
        item = value[name]
        lines.append(f"{name}: {item['path']} ({item['state']})")
        if name == "opencode":
            lines.extend(f"  missing pattern: {pattern}"
                         for pattern in item["missingPatterns"])
            lines.extend(f"  stale pattern: {pattern}" for pattern in item["stalePatterns"])
            lines.extend(f"  missing bash: {pattern}" for pattern in item["missingBash"])
        elif name == "claude":
            lines.extend(f"  missing rule: {rule}" for rule in item["missingRules"])
        else:
            lines.extend(f"  missing key: {key}" for key, present in item["keys"].items()
                         if not present)
    cli = value["copilotCli"]
    lines += ["", "Copilot CLI (no repository-level permission key; launch with):",
              f"  {cli['invocation']}" if cli["invocation"] else "  (not a git checkout)"]
    lines += ["", "VS Code `.vscode/settings.json` (paste under the root object):",
              vscode_snippet()]
    return "\n".join(lines)
