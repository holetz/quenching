"""Offline capture cases for the provider-derived specs contract.

Each case uses a throwaway Git repository with a real origin URL. No provider CLI is invoked:
configuration is read without opening a backend, while refusal cases prove that unknown and
legacy local providers fail before a local store can appear.
"""
from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
PLUGIN_ROOT = HERE.parent
CQ = PLUGIN_ROOT / "assets" / "bin" / "cq"
FIXTURE_DIR = HERE / "fixtures" / "golden"

CASES = {
    "provider-github-config": {
        "remote": "git@github.com:owner/repo.git",
        "command": ["config", "--json"],
        "fixture": "provider-github-config.json",
    },
    "provider-azure-config": {
        "remote": "https://dev.azure.com/org/project/_git/repo",
        "command": ["config", "--json"],
        "fixture": "provider-azure-config.json",
    },
    "provider-unknown-refusal": {
        "remote": "https://forge.example.test/org/repo.git",
        "command": ["list", "--json"],
        "fixture": "provider-unknown-refusal.json",
    },
    "legacy-files-refusal": {
        "remote": "git@github.com:owner/repo.git",
        "config": {"backend": "files"},
        "command": ["list", "--json"],
        "fixture": "legacy-files-refusal.json",
    },
}


def _git(cwd: pathlib.Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True)


def build_workspace(dest: pathlib.Path, remote: str, config: dict | None = None) -> pathlib.Path:
    dest.mkdir(parents=True)
    _git(dest, "init", "-q", "-b", "main")
    _git(dest, "remote", "add", "origin", remote)
    if config is not None:
        (dest / ".claude").mkdir()
        (dest / ".claude" / "quenching.json").write_text(
            json.dumps(config) + "\n", encoding="utf-8")
    return dest


def normalize(text: str, workspace: pathlib.Path) -> str:
    return text.replace(str(workspace), "<WS>")


def capture_case(name: str, root: pathlib.Path) -> dict:
    case = CASES[name]
    workspace = build_workspace(root / name, case["remote"], case.get("config"))
    proc = subprocess.run(
        [sys.executable, str(CQ), "specs", "--root", str(workspace), *case["command"]],
        cwd=str(PLUGIN_ROOT), capture_output=True, text=True)
    return {
        "stdout": normalize(proc.stdout, workspace),
        "stderr": normalize(proc.stderr, workspace),
        "exit": proc.returncode,
        "fixture": case["fixture"],
    }


def capture_all() -> list[dict]:
    with tempfile.TemporaryDirectory(prefix="quenching-provider-capture-") as raw:
        root = pathlib.Path(raw)
        return [capture_case(name, root) for name in CASES]


def main() -> int:
    for result in capture_all():
        print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
