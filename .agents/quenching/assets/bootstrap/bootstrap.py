#!/usr/bin/env python3
"""Per-user setup that `cq deploy` cannot do inside the repository.

Generated into `.quenching/bootstrap/` by `cq deploy`; run it by hand. Nothing here runs on its own.

    bootstrap.py --check    read-only: report each item (default); exit 0 all done, 1 pending or
                            manual, 2 error
    bootstrap.py --write    list every write outside the repository, back up each file it changes
                            into .quenching/bootstrap/backups/<date-time>/, then apply

Idempotent: a second `--write` with everything done writes nothing. A JSON file carrying comments
is never rewritten; its item is `manual` and prints the exact snippet to paste.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

CONFIG = json.loads(r"""__CONFIG__""")

DEPTH = 4
MAX_REQUESTS = 100
MARKETPLACE = "quenching"
MARKETPLACE_SOURCE = "holetz/quenching"
CLAUDE_PLUGINS = ("quenching-hud", "quenching-cache")
VSCODE_EXTENSIONS = ("GitHub.copilot", "GitHub.copilot-chat")
OPENCODE_NAMES = ("opencode.json", "opencode.jsonc", "config.json")
VITRINE = "integrations/opencode-vitrine"

REPO = Path(__file__).resolve().parents[2]
WINDOWS = os.name == "nt"

POSIX_LAUNCHER = """#!/bin/sh
# cq launcher installed by the quenching bootstrap: the nearest repository's own launcher wins,
# this checkout's is the fallback.
dir=$PWD
while :; do
  if [ -x "$dir/.agents/quenching/bin/cq" ]; then exec "$dir/.agents/quenching/bin/cq" "$@"; fi
  parent=$(dirname "$dir")
  [ "$parent" = "$dir" ] && break
  dir=$parent
done
exec "@REPO@/.agents/quenching/bin/cq" "$@"
"""

WINDOWS_LAUNCHER = """@echo off\r
rem cq launcher installed by the quenching bootstrap: the nearest repository's own launcher wins,\r
rem this checkout's is the fallback.\r
setlocal\r
set "dir=%CD%"\r
:up\r
if exist "%dir%\\.agents\\quenching\\bin\\cq.cmd" goto run\r
for %%I in ("%dir%\\..") do set "parent=%%~fI"\r
if /i "%parent%"=="%dir%" goto fallback\r
set "dir=%parent%"\r
goto up\r
:fallback\r
set "dir=@REPO@"\r
:run\r
endlocal & "%dir%\\.agents\\quenching\\bin\\cq.cmd" %*\r
"""


def home() -> Path:
    return Path(os.path.expanduser("~"))


def launcher_path() -> Path:
    return home() / ".local" / "bin" / ("cq.cmd" if WINDOWS else "cq")


def launcher_text() -> str:
    return (WINDOWS_LAUNCHER if WINDOWS else POSIX_LAUNCHER).replace("@REPO@", str(REPO))


def jsonc_loads(text: str):
    """JSON with `//` and `/* */` comments and trailing commas."""
    out, index, size = [], 0, len(text)
    while index < size:
        char = text[index]
        if char == '"':
            end = index + 1
            while end < size and text[end] != '"':
                end += 2 if text[end] == "\\" else 1
            out.append(text[index:end + 1])
            index = end + 1
        elif text.startswith("//", index):
            newline = text.find("\n", index)
            index = size if newline < 0 else newline
        elif text.startswith("/*", index):
            close = text.find("*/", index + 2)
            index = size if close < 0 else close + 2
        else:
            out.append(char)
            index += 1
    return json.loads(re.sub(r",(\s*[}\]])", r"\1", "".join(out)))


def read_document(path: Path):
    """`(document, strict, error)`: `strict` is False when only the comment-tolerant read worked."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return None, False, str(exc)
    try:
        return json.loads(text), True, None
    except ValueError:
        pass
    try:
        return jsonc_loads(text), False, None
    except ValueError as exc:
        return None, False, f"not JSON: {exc}"


def dump(document) -> str:
    return json.dumps(document, indent=2, ensure_ascii=False) + "\n"


def action(item: str, state: str, detail: str, writes=(), apply=None, snippet: str | None = None) -> dict:
    return {"item": item, "state": state, "detail": detail, "writes": [str(w) for w in writes],
            "apply": apply, "snippet": snippet}


# ---- launcher -------------------------------------------------------------------------------

def path_entries(value: str) -> list[str]:
    return [part for part in value.split(os.pathsep) if part]


def with_path_entry(value: str, entry: str) -> str:
    """`value` with `entry` appended unless it is already a (case-folded, slash-folded) member."""
    fold = lambda part: part.replace("/", "\\").rstrip("\\").lower()
    if any(fold(part) == fold(entry) for part in path_entries(value)):
        return value
    return os.pathsep.join([*path_entries(value), entry])


def _write_launcher() -> None:
    target = launcher_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(launcher_text().encode("utf-8"))
    if not WINDOWS:
        os.chmod(target, 0o755)


def _user_path():
    import winreg
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0,
                        winreg.KEY_READ | winreg.KEY_SET_VALUE) as key:
        try:
            value, kind = winreg.QueryValueEx(key, "Path")
        except FileNotFoundError:
            value, kind = "", winreg.REG_EXPAND_SZ
    return value, kind


def _set_user_path(entry: str, backup: Path) -> None:
    import winreg
    value, kind = _user_path()
    backup.mkdir(parents=True, exist_ok=True)
    (backup / "user-path.txt").write_text(value, encoding="utf-8")
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_SET_VALUE) as key:
        winreg.SetValueEx(key, "Path", 0, kind, with_path_entry(value, entry))


def plan_launcher(backup: Path) -> list[dict]:
    target = launcher_path()
    current = target.read_bytes().decode("utf-8", "replace") if target.is_file() else None
    executable = WINDOWS or (target.is_file() and os.access(target, os.X_OK))
    if current == launcher_text() and executable:
        out = [action("launcher", "ok", f"{target} is current")]
    else:
        what = "create" if current is None else "replace (backed up)"
        out = [action("launcher", "todo", f"{what} {target}", [target], _write_launcher)]
    directory = str(target.parent)
    if WINDOWS:
        value, _kind = _user_path()
        if with_path_entry(value, directory) == value:
            out.append(action("launcher-path", "ok", f"{directory} is on the user PATH"))
        else:
            out.append(action("launcher-path", "todo",
                              f"append {directory} to the user PATH (HKCU\\Environment\\Path; the old "
                              f"value is saved to {backup / 'user-path.txt'})",
                              ["HKCU\\Environment\\Path"], lambda: _set_user_path(directory, backup)))
    elif directory in path_entries(os.environ.get("PATH", "")):
        out.append(action("launcher-path", "ok", f"{directory} is on PATH"))
    else:
        out.append(action("launcher-path", "manual", f"{directory} is not on PATH; this script edits "
                          "no shell profile",
                          snippet=f'export PATH="{directory}:$PATH"   # in your shell profile'))
    return out


# ---- OpenCode -------------------------------------------------------------------------------

def opencode_files() -> list[Path]:
    """The user's OpenCode config files that exist, as OpenCode reads them."""
    paths = [Path(os.environ["OPENCODE_CONFIG"])] if os.environ.get("OPENCODE_CONFIG") else []
    base = os.environ.get("XDG_CONFIG_HOME") or str(home() / ".config")
    paths += [Path(base) / "opencode" / name for name in OPENCODE_NAMES]
    return [path for path in dict.fromkeys(paths) if path.is_file()]


def _edit_json(path: Path, mutate) -> None:
    document, _strict, _error = read_document(path)
    mutate(document)
    path.write_text(dump(document), encoding="utf-8", newline="\n")


def plan_opencode_depth() -> list[dict]:
    out = []
    for path in opencode_files():
        document, strict, error = read_document(path)
        if error or not isinstance(document, dict):
            out.append(action("opencode-depth", "manual", f"{path} could not be read ({error})"))
            continue
        block = document.get("experimental")
        if not isinstance(block, dict) or not block:
            continue  # no global block to hide: the deploy writes the depth into the project file
        if isinstance(block.get("subagent_depth"), int) and block["subagent_depth"] >= DEPTH:
            out.append(action("opencode-depth", "ok", f"{path} sets experimental.subagent_depth"))
        elif not strict:
            out.append(action("opencode-depth", "manual",
                              f"{path} carries comments, so it is not rewritten",
                              snippet=f'add to its "experimental" block:  "subagent_depth": {DEPTH}'))
        else:
            out.append(action("opencode-depth", "todo",
                              f"set experimental.subagent_depth to {DEPTH} in {path} (a project "
                              "`experimental` block replaces this one, so the depth lives here)",
                              [path], lambda p=path: _edit_json(
                                  p, lambda d: d["experimental"].update(subagent_depth=DEPTH))))
    return out or [action("opencode-depth", "ok", "no global `experimental` block; the project file "
                          "carries the depth")]


def vitrine_dir(checkout: str | None) -> Path | None:
    for base in (checkout, os.environ.get("QUENCHING_CHECKOUT"), str(REPO)):
        if base and (Path(base) / VITRINE / "package.json").is_file():
            return Path(base) / VITRINE
    return None


def plan_opencode_plugin(checkout: str | None) -> list[dict]:
    package = vitrine_dir(checkout)
    if package is None:
        return [action("opencode-plugin", "manual", "no quenching checkout with "
                       f"{VITRINE}; rerun with --quenching-checkout <path>")]
    if not (package / "dist").is_dir():
        return [action("opencode-plugin", "manual", f"{package} has no dist/; build it first",
                       snippet=f"cd {package} && npm ci && npm run build")]
    entry = str(package)
    existing = opencode_files()
    target = existing[0] if existing else Path(
        os.environ.get("XDG_CONFIG_HOME") or str(home() / ".config")) / "opencode" / "opencode.json"
    document, strict, error = (read_document(target) if existing else ({}, True, None))
    if error or not isinstance(document, dict):
        return [action("opencode-plugin", "manual", f"{target} could not be read ({error})")]
    plugins = document.get("plugins")
    if isinstance(plugins, list) and entry in plugins:
        return [action("opencode-plugin", "ok", f"{target} lists the vitrine")]
    if not strict:
        return [action("opencode-plugin", "manual", f"{target} carries comments, so it is not rewritten",
                       snippet=f'add to its "plugins" array:  "{entry}"')]

    def apply() -> None:
        target.parent.mkdir(parents=True, exist_ok=True)
        doc = read_document(target)[0] if target.is_file() else {}
        listed = doc.get("plugins") if isinstance(doc.get("plugins"), list) else []
        doc["plugins"] = [*listed, entry]
        target.write_text(dump(doc), encoding="utf-8", newline="\n")
    return [action("opencode-plugin", "todo", f"list the vitrine in {target}: {entry}", [target], apply)]


# ---- Claude Code ----------------------------------------------------------------------------

def claude_dir() -> Path:
    return Path(os.environ.get("CLAUDE_CONFIG_DIR") or home() / ".claude")


def claude_installed() -> tuple[set[str], set[str]]:
    """`(installed plugin ids, known marketplace names)`, read from Claude Code's own files."""
    plugins, markets = set(), set()
    document = read_document(claude_dir() / "plugins" / "installed_plugins.json")[0]
    if isinstance(document, dict) and isinstance(document.get("plugins"), dict):
        plugins = set(document["plugins"])
    document = read_document(claude_dir() / "plugins" / "known_marketplaces.json")[0]
    if isinstance(document, dict):
        markets = set(document)
    return plugins, markets


def claude_commands(plugins: set[str], markets: set[str]) -> list[list[str]]:
    commands = []
    if MARKETPLACE not in markets:
        commands.append(["claude", "plugin", "marketplace", "add", MARKETPLACE_SOURCE])
    commands += [["claude", "plugin", "install", f"{name}@{MARKETPLACE}", "--scope", "user"]
                 for name in CLAUDE_PLUGINS if f"{name}@{MARKETPLACE}" not in plugins]
    return commands


def run_all(commands: list[list[str]]) -> None:
    for command in commands:
        done = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace")
        if done.returncode != 0:
            raise RuntimeError(f"`{' '.join(command)}` exited {done.returncode}: "
                               f"{(done.stderr or done.stdout).strip()[-300:]}")


def plan_claude_plugins() -> list[dict]:
    plugins, markets = claude_installed()
    commands = claude_commands(plugins, markets)
    if not commands:
        return [action("claude-plugins", "ok", "marketplace and plugins are installed")]
    text = "; ".join(" ".join(c) for c in commands)
    if shutil.which("claude") is None:
        return [action("claude-plugins", "manual", "`claude` is not on PATH; run: " + text)]
    root = claude_dir()
    writes = [root / "plugins" / "known_marketplaces.json", root / "plugins" / "installed_plugins.json",
              root / "settings.json"]
    return [action("claude-plugins", "todo", "run: " + text, writes, lambda: run_all(commands))]


# ---- VS Code --------------------------------------------------------------------------------

def vscode_settings() -> Path:
    if WINDOWS:
        return Path(os.environ.get("APPDATA") or home() / "AppData" / "Roaming") / "Code" / "User" / "settings.json"
    if sys.platform == "darwin":
        return home() / "Library" / "Application Support" / "Code" / "User" / "settings.json"
    return Path(os.environ.get("XDG_CONFIG_HOME") or home() / ".config") / "Code" / "User" / "settings.json"


def plan_vscode() -> list[dict]:
    out = []
    target = vscode_settings()
    if target.is_file():
        document, strict, error = read_document(target)
    else:
        document, strict, error = {}, True, None
    value = document.get("chat.agent.maxRequests") if isinstance(document, dict) else None
    snippet = f'"chat.agent.maxRequests": {MAX_REQUESTS}'
    if error or not isinstance(document, dict):
        out.append(action("vscode-settings", "manual", f"{target} could not be read ({error})", snippet=snippet))
    elif isinstance(value, int) and value >= MAX_REQUESTS:
        out.append(action("vscode-settings", "ok", f"{target} sets chat.agent.maxRequests"))
    elif not strict:
        out.append(action("vscode-settings", "manual", f"{target} carries comments, so it is not rewritten",
                          snippet=snippet))
    else:
        def apply() -> None:
            doc = read_document(target)[0] if target.is_file() else {}
            doc["chat.agent.maxRequests"] = MAX_REQUESTS
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(dump(doc), encoding="utf-8", newline="\n")
        out.append(action("vscode-settings", "todo", f"set chat.agent.maxRequests to {MAX_REQUESTS} in {target}",
                          [target], apply))
    code = shutil.which("code")
    if code is None:
        out.append(action("vscode-extensions", "manual", "`code` is not on PATH; install: "
                          + ", ".join(VSCODE_EXTENSIONS)))
        return out
    done = subprocess.run([code, "--list-extensions"], capture_output=True, text=True,
                          encoding="utf-8", errors="replace")
    have = {line.strip().lower() for line in done.stdout.splitlines()}
    missing = [name for name in VSCODE_EXTENSIONS if name.lower() not in have]
    if done.returncode != 0:
        out.append(action("vscode-extensions", "manual", "`code --list-extensions` failed"))
    elif not missing:
        out.append(action("vscode-extensions", "ok", "the extensions are installed"))
    else:
        commands = [[code, "--install-extension", name] for name in missing]
        out.append(action("vscode-extensions", "todo",
                          "run: " + "; ".join(f"code --install-extension {n}" for n in missing),
                          [], lambda: run_all(commands)))
    return out


# ---- driver ---------------------------------------------------------------------------------

def build_plan(backup: Path, checkout: str | None = None) -> list[dict]:
    harnesses = CONFIG.get("harnesses", [])
    out = plan_launcher(backup)
    if "opencode" in harnesses:
        out += plan_opencode_depth() + plan_opencode_plugin(checkout)
    if "claude" in harnesses:
        out += plan_claude_plugins()
    if CONFIG.get("vscode"):
        out += plan_vscode()
    return out


def back_up(path: str, backup: Path) -> str | None:
    source = Path(path)
    if not source.is_file():
        return None
    name = re.sub(r"[^A-Za-z0-9._-]+", "_", str(source).lstrip("/\\"))
    backup.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, backup / name)
    return str(backup / name)


def report(actions: list[dict]) -> None:
    for item in actions:
        print(f"  {item['state']:<6} {item['item']}: {item['detail']}")
        if item["snippet"]:
            print(f"         paste: {item['snippet']}")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="bootstrap", description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="read-only report (default)")
    mode.add_argument("--write", action="store_true", help="list, back up and apply")
    parser.add_argument("--quenching-checkout", default=None,
                        help="a quenching checkout, for the OpenCode vitrine path")
    args = parser.parse_args(argv)
    stamp = time.strftime("%Y%m%dT%H%M%S")
    backup = REPO / ".quenching" / "bootstrap" / "backups" / stamp
    try:
        actions = build_plan(backup, args.quenching_checkout)
    except OSError as exc:
        print(f"bootstrap: {exc}", file=sys.stderr)
        return 2
    print(f"quenching bootstrap {CONFIG.get('version', '')} — {REPO}")
    report(actions)
    todo = [a for a in actions if a["state"] == "todo"]
    if not args.write:
        return 1 if any(a["state"] in ("todo", "manual") for a in actions) else 0
    if not todo:
        print("nothing to write")
        return 1 if any(a["state"] == "manual" for a in actions) else 0
    print("\nabout to write outside the repository:")
    for item in todo:
        for path in item["writes"] or ["(runs a command; no file of its own)"]:
            print(f"  {item['item']}: {path}")
    print(f"backups go to {backup}\n")
    failed = False
    for item in todo:
        for path in item["writes"]:
            saved = back_up(path, backup)
            if saved:
                print(f"  backed up {path} -> {saved}")
        try:
            item["apply"]()
            print(f"  done   {item['item']}")
        except (OSError, RuntimeError, ValueError) as exc:
            failed = True
            print(f"  failed {item['item']}: {exc}", file=sys.stderr)
    if failed:
        return 2
    remaining = [a for a in build_plan(backup, args.quenching_checkout) if a["state"] in ("todo", "manual")]
    return 1 if remaining else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
