"""Collect security evidence without changing the target repository."""
from __future__ import annotations

import os
import re
import subprocess
import tempfile
from pathlib import Path

from quenching.security.model import QuestionResult, SecurityReport


_WORKFLOW_SUFFIXES = frozenset({".yml", ".yaml"})
_ADVISORY_FILES = (
    ".github/dependabot.yml",
    ".github/dependabot.yaml",
    ".renovate.json",
    "renovate.json",
    "renovate.json5",
)
_ACCESS_FILES = (
    ".github/CODEOWNERS",
    "CODEOWNERS",
    "docs/CODEOWNERS",
    ".github/OWNERS",
    "OWNERS",
)


def _read(path: Path) -> tuple[str | None, str | None]:
    try:
        return path.read_text(encoding="utf-8"), None
    except FileNotFoundError:
        return None, "missing"
    except (OSError, UnicodeDecodeError):
        return None, "unreadable"


def _workflow_files(root: Path) -> list[Path]:
    directory = root / ".github" / "workflows"
    if not directory.is_dir():
        return []
    return sorted(path for path in directory.rglob("*")
                  if path.is_file() and path.suffix.lower() in _WORKFLOW_SUFFIXES)


def _relative(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


_PERMISSIONS = re.compile(r"^(\s*)permissions\s*:\s*([^#]*?)\s*(?:#.*)?$")
_SCOPE = re.compile(r"^\s*([A-Za-z-]+)\s*:\s*([A-Za-z-]+)")


def _grants(lines: list[str]) -> tuple[list[str], list[str]]:
    """Every `write-all` and every scope granted `write`, as `workflow` or `job:<line>` plus the
    scope. Line-based, like the counts: an inline value, a flow mapping or the block below."""
    write_all: list[str] = []
    write_scopes: list[str] = []
    for number, line in enumerate(lines, start=1):
        match = _PERMISSIONS.match(line)
        if not match:
            continue
        indent, inline = len(match.group(1)), match.group(2)
        where = "workflow" if indent == 0 else f"job:{number}"
        if inline == "write-all":
            write_all.append(where)
            continue
        if inline.startswith("{"):
            pairs = [item.split(":", 1) for item in inline.strip("{}").split(",") if ":" in item]
        elif inline:
            continue
        else:
            pairs = []
            for below in lines[number:]:
                if not below.strip() or below.lstrip().startswith("#"):
                    continue
                if len(below) - len(below.lstrip()) <= indent:
                    break
                scope = _SCOPE.match(below)
                if scope:
                    pairs.append([scope.group(1), scope.group(2)])
        write_scopes += [f"{where}:{key.strip()}" for key, value in pairs
                         if value.strip() == "write"]
    return write_all, write_scopes


def workflow_permissions(root: Path) -> QuestionResult:
    """Report whether recognized workflows declare workflow or job permissions, and where a
    declaration grants `write-all`, the one grant unbounded by its own definition."""
    files = _workflow_files(root)
    if not files:
        return QuestionResult(
            "workflow-permissions",
            "Are workflow and job permissions explicit and bounded?",
            "missing",
            ({"path": ".github/workflows", "reason": "no workflow files measured"},),
        )

    evidence: list[dict[str, object]] = []
    for path in files:
        text, error = _read(path)
        relative = _relative(root, path)
        if error:
            evidence.append({"path": relative, "reason": error})
            continue
        assert text is not None
        lines = text.splitlines()
        workflow_declarations = sum(bool(re.match(r"^permissions\s*:", line)) for line in lines)
        job_declarations = sum(bool(re.match(r"^\s{2,}permissions\s*:", line)) for line in lines)
        write_all, write_scopes = _grants(lines)
        evidence.append({
            "path": relative,
            "workflowDeclarations": workflow_declarations,
            "jobDeclarations": job_declarations,
            "writeAll": write_all,
            "writeScopes": write_scopes,
        })

    if any("reason" in item for item in evidence):
        state = "refused"
    elif any(item["writeAll"] for item in evidence):
        state = "unbounded"
    elif any(item["workflowDeclarations"] or item["jobDeclarations"] for item in evidence):
        state = "present"
    else:
        state = "missing"
    return QuestionResult(
        "workflow-permissions",
        "Are workflow and job permissions explicit and bounded?",
        state,
        tuple(evidence),
    )


_SECRET_CLASSES = ("environment-files", "private-keys", "credential-files")
_SECRET_SAMPLES = {
    "environment-files": (".env",),
    "private-keys": ("server.pem", "server.key", "id_rsa"),
    "credential-files": ("credentials.json", "secrets.json", "token.json"),
}


def _secret_class(pattern: str) -> str | None:
    value = pattern.lower().lstrip("/")
    while value.startswith("**/"):
        value = value[3:].lstrip("/")
    value = value.rstrip("/")
    if value.startswith(".env") or value == "*.env":
        return "environment-files"
    if any(value.endswith(suffix) for suffix in (".pem", ".key", ".p12", ".pfx")) \
            or value.startswith("id_rsa"):
        return "private-keys"
    if any(token in value for token in ("secret", "credential", "token")):
        return "credential-files"
    return None


def _ignored_names(text: str, names: list[str]) -> set[str] | None:
    """Ask git itself which names the ignore text hides; None when git cannot answer."""
    env = {**{k: v for k, v in os.environ.items() if not k.startswith("GIT_")},
           "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1"}
    try:
        with tempfile.TemporaryDirectory() as raw:
            subprocess.run(["git", "init", "-q", raw], check=True, env=env,
                           capture_output=True)
            Path(raw, ".gitignore").write_text(text, encoding="utf-8")
            ignored: set[str] = set()
            for name in names:
                done = subprocess.run(
                    ["git", "-C", raw, "-c", "core.excludesFile=", "check-ignore",
                     "--no-index", "-q", "--", name],
                    env=env, capture_output=True)
                if done.returncode == 0:
                    ignored.add(name)
                elif done.returncode != 1:
                    return None
            return ignored
    except (OSError, subprocess.SubprocessError):
        return None


def secret_ignore_coverage(root: Path) -> QuestionResult:
    """Report recognized secret classes the repository ignore file really hides from git."""
    path = root / ".gitignore"
    text, error = _read(path)
    if error:
        return QuestionResult(
            "secret-ignore-coverage",
            "Do ignore rules cover the secret classes the repository exposes?",
            "missing" if error == "missing" else "refused",
            ({"path": ".gitignore", "reason": error},),
        )
    assert text is not None
    candidates: dict[str, list[str]] = {}
    for line in text.splitlines():
        pattern = line.strip()
        if not pattern or pattern.startswith("#") or pattern.startswith("!"):
            continue
        category = _secret_class(pattern)
        if category:
            candidates.setdefault(category, []).append(pattern)
    names = sorted({name for samples in _SECRET_SAMPLES.values() for name in samples}
                   | {p.lstrip("/") for ps in candidates.values() for p in ps
                      if not re.search(r"[*?\[]|/$", p)})
    ignored = _ignored_names(text, names)
    if ignored is None:
        return QuestionResult(
            "secret-ignore-coverage",
            "Do ignore rules cover the secret classes the repository exposes?",
            "refused",
            ({"path": ".gitignore", "reason": "git could not evaluate the ignore rules"},),
        )
    coverage: dict[str, list[str]] = {}
    for category, patterns in candidates.items():
        literal = set() if category == "environment-files" \
            else {p.lstrip("/") for p in patterns}
        if ignored & (set(_SECRET_SAMPLES[category]) | literal):
            coverage[category] = patterns
    uncovered = sorted(set(_SECRET_CLASSES) - set(coverage))
    state = "missing" if uncovered else "present"
    details: dict[str, object] = {}
    if coverage:
        details["patterns"] = coverage
    if uncovered:
        details["uncovered"] = uncovered
    return QuestionResult(
        "secret-ignore-coverage",
        "Do ignore rules cover the secret classes the repository exposes?",
        state,
        ({"path": ".gitignore", "classes": sorted(coverage)},),
        details,
    )


def advisory_dependency_configuration(root: Path) -> QuestionResult:
    """Report known static dependency-advisory configuration files."""
    candidates = [root / relative for relative in _ADVISORY_FILES]
    present = [_relative(root, path) for path in candidates if path.is_file()]
    pyproject = root / "pyproject.toml"
    text, error = _read(pyproject)
    if error == "unreadable":
        return QuestionResult(
            "advisory-dependency-configuration",
            "Is advisory dependency configuration present?",
            "refused",
            ({"path": "pyproject.toml", "reason": error},),
        )
    if text and any(marker in text.lower() for marker in ("pip-audit", "safety", "cargo-audit")):
        present.append("pyproject.toml")
    present = sorted(set(present))
    return QuestionResult(
        "advisory-dependency-configuration",
        "Is advisory dependency configuration present?",
        "present" if present else "missing",
        tuple({"path": path} for path in present)
        or ({"path": ".github/dependabot.yml", "reason": "no known advisory configuration"},),
    )


def access_ownership(root: Path) -> QuestionResult:
    """Report provider ownership declarations without inspecting owner values."""
    present = [relative for relative in _ACCESS_FILES
               if (root / relative).is_file()]
    return QuestionResult(
        "access-ownership",
        "Who may touch the relevant security surface?",
        "present" if present else "missing",
        tuple({"path": path} for path in present)
        or ({"path": ".github/CODEOWNERS", "reason": "no known ownership declaration"},),
    )


def build_report(root: str) -> SecurityReport:
    """Build all security answers from static files under ``root``."""
    repository = Path(root).resolve()
    questions = (
        workflow_permissions(repository),
        secret_ignore_coverage(repository),
        advisory_dependency_configuration(repository),
        access_ownership(repository),
    )
    return SecurityReport(str(repository), questions)
