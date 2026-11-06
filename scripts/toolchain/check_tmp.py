"""Refuse a test that escapes the single temp root: a literal temp path used as a location, or a
write to `tempfile.tempdir`.

The suite moves its temporary files by exporting `TMPDIR`/`TEMP`/`TMP` once (`_paths.py` and the
gate), which works only while no test pins a path of its own. Two ways to escape it exist, and both
are silent: a literal `/tmp/...` handed to the filesystem, and an assignment to `tempfile.tempdir`.
This guard reads the AST and refuses both.

A literal used as **data** is not a violation — a JSON payload field, a mocked registry value, a
string an assertion compares against. That is why the rule is a context, not a path: the literal is
a finding only inside a call that consumes a path, a `dir=`/`cwd=` keyword, or an assignment into
`TMPDIR`/`TEMP`/`TMP`. The rule is what allow-lists the suite's data literals; there is no per-path
waiver. It is a lint, not taint analysis: a `"/tmp"` stored in a dict and read as a path later is
out of its reach, and that is accepted.

Run as `python -m scripts.toolchain.check_tmp [<dir>...]`; exit 1 with one line per finding.
"""

from __future__ import annotations

import argparse
import ast
import pathlib
import sys

DEFAULT_DIR = "quenching/tests"
TEMP_ROOTS = ("/tmp", "/var/tmp", "/dev/shm", "/run/user", "/private/tmp",
              "%TEMP%", "%TMP%", "C:\\Windows\\Temp")
TEMP_KEYS = ("TMPDIR", "TEMP", "TMP")
# Calls whose arguments are consumed as filesystem locations.
PATH_CALLS = frozenset({
    "open", "Path", "PurePath", "PosixPath", "WindowsPath", "chdir", "mkdir", "makedirs",
    "rmtree", "remove", "unlink", "rename", "replace", "copytree", "copy2", "copyfile", "move",
    "glob", "rglob", "walk", "scandir", "read_text", "write_text", "read_bytes", "write_bytes",
    "mkdtemp", "mkstemp", "NamedTemporaryFile", "TemporaryDirectory", "TemporaryFile", "joinpath",
    "exists", "is_dir", "is_file",
})
# Keyword names that are a path wherever they appear.
PATH_KEYWORDS = frozenset({"dir", "cwd"})


def _rooted(value: str) -> bool:
    """Whether the string names a temp location, by its first path segment."""
    lowered = value.lower()
    for root in TEMP_ROOTS:
        root = root.lower()
        if lowered == root or lowered.startswith(root.rstrip("/") + "/") or \
                lowered.startswith(root.rstrip("\\") + "\\"):
            return True
    return False


def _literal(node: ast.AST) -> str | None:
    """The constant text of a string literal or the static head of an f-string."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.JoinedStr):
        head = "".join(part.value for part in node.values
                       if isinstance(part, ast.Constant) and isinstance(part.value, str))
        return head or None
    return None


def _callee(node: ast.Call) -> str:
    func = node.func
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        return func.attr
    return ""


def _env_assignment(node: ast.AST) -> bool:
    """`os.environ["TMPDIR"] = ...` — a temp location behind an environment write."""
    if not isinstance(node, (ast.Assign, ast.AnnAssign)):
        return False
    targets = node.targets if isinstance(node, ast.Assign) else [node.target]
    for target in targets:
        if isinstance(target, ast.Subscript) and _literal(target.slice) in TEMP_KEYS:
            return True
    return False


def scan_source(source: str, filename: str = "<string>") -> list[str]:
    """Every finding in one module, as `path:line: message`."""
    try:
        tree = ast.parse(source, filename=filename)
    except SyntaxError as exc:
        return [f"{filename}:{exc.lineno or 0}: cannot parse: {exc.msg}"]
    findings: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for target in targets:
                if isinstance(target, ast.Attribute) and target.attr == "tempdir" and \
                        isinstance(target.value, ast.Name) and target.value.id == "tempfile":
                    findings.append(f"{filename}:{node.lineno}: assigns to tempfile.tempdir; "
                                    "the root is resolved once, not per test")
            if _env_assignment(node):
                findings.append(f"{filename}:{node.lineno}: assigns a temp location into the "
                                "environment; the root is resolved once, not per test")
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and \
                node.func.id == "setattr" and len(node.args) >= 2 and \
                isinstance(node.args[0], ast.Name) and node.args[0].id == "tempfile" and \
                _literal(node.args[1]) == "tempdir":
            findings.append(f"{filename}:{node.lineno}: sets tempfile.tempdir through setattr")
        if not isinstance(node, ast.Call):
            continue
        name = _callee(node)
        slots = [arg for arg in node.args if name in PATH_CALLS]
        slots += [kw.value for kw in node.keywords if kw.arg in PATH_KEYWORDS]
        for slot in slots:
            value = _literal(slot)
            if value and _rooted(value):
                findings.append(f"{filename}:{node.lineno}: {value!r} is a hard-coded temp "
                                "location; use the resolved root")
    return findings


def scan(paths: list[pathlib.Path]) -> list[str]:
    findings: list[str] = []
    for path in paths:
        findings.extend(scan_source(path.read_text(encoding="utf-8"), str(path)))
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("paths", nargs="*", default=[DEFAULT_DIR])
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    files: list[pathlib.Path] = []
    for raw in args.paths:
        path = pathlib.Path(raw)
        files.extend(sorted(path.rglob("*.py")) if path.is_dir() else [path])
    findings = scan(files)
    if args.json:
        import json

        print(json.dumps({"ok": not findings, "findings": findings}, indent=2))
    else:
        print(f"temp-root guard — {len(files)} file(s), {len(findings)} finding(s)")
        for finding in findings:
            print(f"  {finding}")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
