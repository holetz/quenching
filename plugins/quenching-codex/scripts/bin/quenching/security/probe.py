"""Collect security evidence without changing the target repository."""
from __future__ import annotations

import re
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


def workflow_permissions(root: Path) -> QuestionResult:
    """Report whether recognized workflows declare workflow or job permissions."""
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
        workflow_declarations = sum(
            bool(re.match(r"^permissions\s*:", line)) for line in text.splitlines()
        )
        job_declarations = sum(
            bool(re.match(r"^\s{2,}permissions\s*:", line)) for line in text.splitlines()
        )
        evidence.append({
            "path": relative,
            "workflowDeclarations": workflow_declarations,
            "jobDeclarations": job_declarations,
        })

    if any("reason" in item for item in evidence):
        state = "refused"
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


def _secret_class(pattern: str) -> str | None:
    value = pattern.lower().lstrip("/")
    if value == ".env" or value.startswith(".env."):
        return "environment-files"
    if any(value.endswith(suffix) for suffix in (".pem", ".key", ".p12", ".pfx")) \
            or value.startswith("id_rsa"):
        return "private-keys"
    if any(token in value for token in ("secret", "credential", "token")):
        return "credential-files"
    return None


def secret_ignore_coverage(root: Path) -> QuestionResult:
    """Report recognized secret classes covered by the repository ignore file."""
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
    coverage: dict[str, list[str]] = {}
    for line in text.splitlines():
        pattern = line.strip()
        if not pattern or pattern.startswith("#") or pattern.startswith("!"):
            continue
        category = _secret_class(pattern)
        if category:
            coverage.setdefault(category, []).append(pattern)
    state = "present" if coverage else "missing"
    return QuestionResult(
        "secret-ignore-coverage",
        "Do ignore rules cover the secret classes the repository exposes?",
        state,
        ({"path": ".gitignore", "classes": sorted(coverage)},),
        {"patterns": coverage} if coverage else {},
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
