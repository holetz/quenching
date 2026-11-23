"""Portable stand-ins for the programs a test puts on an isolated PATH.

Three things a POSIX-only test writes by hand do not exist on Windows:

- **a bash.** `subprocess.run(["bash", ...])` there resolves `C:\\Windows\\System32\\bash.exe`,
  the WSL launcher, before any PATH entry; :func:`bash` returns Git Bash instead, or ``None``.
- **a fake tool.** A script with a shebang and no extension is neither found by `shutil.which`
  nor runnable (`[WinError 193]`); :func:`fake_tool` writes the Python body behind a `.cmd`
  launcher there, and as a shebang script elsewhere.
- **a real tool linked into the PATH.** `os.symlink` needs a privilege an ordinary Windows account
  lacks (`[WinError 1314]`); :func:`link_tool` writes a `.cmd` that forwards to the real binary.

Every helper returns the path it wrote, which is what `shutil.which(name, path=bin_dir)` finds.
A `.cmd` is reached by `shutil.which` and by `subprocess.run([path])`; a bare
`subprocess.run([name], env={"PATH": bin_dir})` is not, because Windows searches the parent's PATH
for `.exe` only, so the product resolves through `shutil.which` and the test does too.

Not named `test*.py`, therefore never collected as a test.
"""

from __future__ import annotations

import os
import pathlib
import shutil
import sys

WINDOWS = os.name == "nt"


def _is_wsl_launcher(path: str) -> bool:
    system_root = os.environ.get("SystemRoot", r"C:\Windows")
    return os.path.normcase(os.path.dirname(os.path.abspath(path))).startswith(
        os.path.normcase(os.path.join(system_root, ""))
    )


def bash() -> str | None:
    """A bash that runs POSIX scripts here: Git Bash on Windows, never the WSL launcher."""
    if not WINDOWS:
        return shutil.which("bash")
    candidates = []
    git = shutil.which("git")
    if git:
        # `<Git>/cmd/git.exe` or `<Git>/bin/git.exe` or `<Git>/mingw64/bin/git.exe`.
        here = pathlib.Path(git).resolve().parent
        for root in (here.parent, here.parent.parent):
            candidates += [root / "bin" / "bash.exe", root / "usr" / "bin" / "bash.exe"]
    for variable in ("ProgramFiles", "ProgramW6432", "ProgramFiles(x86)"):
        base = os.environ.get(variable)
        if base:
            candidates.append(pathlib.Path(base, "Git", "bin", "bash.exe"))
    found = shutil.which("bash")
    if found and not _is_wsl_launcher(found):
        candidates.insert(0, pathlib.Path(found))
    for candidate in candidates:
        if candidate.is_file():
            return str(candidate)
    return None


def _write_launcher(bin_dir: pathlib.Path, name: str, target: list[str]) -> pathlib.Path:
    quoted = " ".join(f'"{part}"' for part in target)
    launcher = bin_dir / f"{name}.cmd"
    launcher.write_text(f"@echo off\r\n{quoted} %*\r\nexit /b %ERRORLEVEL%\r\n", encoding="utf-8")
    return launcher


def fake_tool(bin_dir: str | os.PathLike, name: str, source: str) -> pathlib.Path:
    """Write a program called `name` into `bin_dir` that runs the Python `source` with its argv.

    The interpreter is this test run's own (`sys.executable`), so the body may import the stdlib
    and nothing has to be installed. Returns the path `shutil.which(name, path=bin_dir)` finds.
    """
    bin_dir = pathlib.Path(bin_dir)
    bin_dir.mkdir(parents=True, exist_ok=True)
    if WINDOWS:
        body = bin_dir / f"{name}.py"
        body.write_text(source, encoding="utf-8")
        return _write_launcher(bin_dir, name, [sys.executable, str(body)])
    script = bin_dir / name
    script.write_text(f"#!{sys.executable}\n{source}", encoding="utf-8")
    script.chmod(0o755)
    return script


def link_tool(bin_dir: str | os.PathLike, name: str, target: str | None = None) -> pathlib.Path:
    """Put the real `name` (or `target`) into `bin_dir` without needing a symlink privilege.

    POSIX gets the symlink a test would write by hand; Windows gets a `.cmd` forwarding to the
    absolute binary. Raises `FileNotFoundError` when the tool is not installed, so the caller
    decides whether that is a skip.
    """
    bin_dir = pathlib.Path(bin_dir)
    bin_dir.mkdir(parents=True, exist_ok=True)
    real = target or shutil.which(name)
    if not real:
        raise FileNotFoundError(f"{name} is not on PATH")
    if WINDOWS:
        return _write_launcher(bin_dir, name, [str(pathlib.Path(real).resolve())])
    link = bin_dir / name
    link.symlink_to(real)
    return link
