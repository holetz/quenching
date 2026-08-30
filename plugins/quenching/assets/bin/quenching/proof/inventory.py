"""Build the proof front's static read model.

The walker reads files and parses Python ASTs only. It never imports a target module and never
starts a test runner; later checks receive this one inventory so a finding cannot come from a
second, subtly different traversal.
"""
from __future__ import annotations

import ast
import configparser
import os
import re
import shlex
from pathlib import Path
from typing import Any

from quenching.proof.config import load_proof_config
from quenching.proof.ci import discover_ci
from quenching.proof.model import (
    Conftest,
    Fixture,
    GateConfig,
    Layer,
    ProofInventory,
    TestModule,
)


_SKIP_DIRS = frozenset({
    ".git", ".mypy_cache", ".pytest_cache", ".ruff_cache", "__pycache__",
    ".tox", ".venv", "venv",
})
_TEST_RE = re.compile(r"(?:^test_.*\.py$|^.*_test\.py$)")
_PYTEST_FIXTURE = re.compile(r"(?:^|\.)fixture$")


def _rel(path: str, root: str) -> str:
    return os.path.relpath(path, root).replace(os.sep, "/")


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""


def _parse(path: Path) -> ast.AST:
    try:
        return ast.parse(_read(path), filename=str(path))
    except (SyntaxError, ValueError):
        return ast.Module(body=[], type_ignores=[])


def _imports(tree: ast.AST) -> tuple[str, ...]:
    values: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            values.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            values.add(node.module)
    return tuple(sorted(values))


def _is_fixture_decorator(node: ast.AST) -> bool:
    if isinstance(node, ast.Name):
        return node.id == "fixture"
    if isinstance(node, ast.Attribute):
        return node.attr == "fixture"
    if isinstance(node, ast.Call):
        return _is_fixture_decorator(node.func)
    return False


def _fixture_names(tree: ast.AST) -> tuple[str, ...]:
    values: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if any(_is_fixture_decorator(decorator) for decorator in node.decorator_list):
            values.append(node.name)
    return tuple(sorted(set(values)))


def _test_count(tree: ast.AST) -> int:
    count = 0
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test"):
            count += 1
        elif isinstance(node, ast.ClassDef) and node.name.startswith("Test"):
            count += 1
    return count


def _layer_for(relative: str, layers: dict[str, dict[str, Any]]) -> str | None:
    parts = relative.split("/")
    return parts[0] if parts and parts[0] in layers else None


def _marker_for(layer: str | None) -> str | None:
    return layer


def _layer_models(proof_root: str, declarations: dict[str, dict[str, Any]]) -> tuple[Layer, ...]:
    result: list[Layer] = []
    for name, declaration in declarations.items():
        result.append(Layer(
            name=name,
            path=name,
            reach=declaration.get("reach"),
            budget=declaration.get("budget"),
            required=bool(declaration.get("required", False)),
        ))
    return tuple(result)


def _gate_from_toml(path: Path) -> tuple[dict[str, Any], str | None]:
    try:
        import tomllib
        data = tomllib.loads(_read(path))
    except (ImportError, TypeError, ValueError):
        return {}, None
    pytest = data.get("tool", {}).get("pytest", {}).get("ini_options", {})
    coverage_run = data.get("tool", {}).get("coverage", {}).get("run", {})
    coverage_report = data.get("tool", {}).get("coverage", {}).get("report", {})
    return {
        "addopts": pytest.get("addopts", ""),
        "markers": pytest.get("markers", []),
        "strict_markers": pytest.get("strict_markers", False),
        "coverage_sources": coverage_run.get("source", []),
        "coverage_floor": coverage_report.get("fail_under"),
    }, _rel(str(path), str(path.parent.parent))


def _gate_from_ini(path: Path) -> dict[str, Any]:
    parser = configparser.ConfigParser()
    try:
        parser.read(path, encoding="utf-8")
    except (OSError, UnicodeError, configparser.Error):
        return {}
    section = "pytest" if parser.has_section("pytest") else None
    if not section:
        return {}
    return {
        "addopts": parser.get(section, "addopts", fallback=""),
        "markers": [line.strip() for line in parser.get(section, "markers", fallback="").splitlines()
                    if line.strip()],
        "strict_markers": "--strict-markers" in parser.get(section, "addopts", fallback=""),
    }


def _tokens(value: Any) -> tuple[str, ...]:
    if isinstance(value, str):
        try:
            return tuple(shlex.split(value))
        except ValueError:
            return tuple(value.split())
    if isinstance(value, list):
        return tuple(str(item) for item in value if isinstance(item, (str, int, float)))
    return ()


def _markers(value: Any) -> tuple[str, ...]:
    if isinstance(value, str):
        values = [value]
    elif isinstance(value, list):
        values = [item for item in value if isinstance(item, str)]
    else:
        values = []
    return tuple(sorted(set(item.split(":", 1)[0].strip() for item in values if item.strip())))


def _gate(repo_root: str) -> GateConfig:
    root = Path(repo_root)
    path: str | None = None
    raw: dict[str, Any] = {}
    pyproject = root / "pyproject.toml"
    if pyproject.is_file():
        raw, _ = _gate_from_toml(pyproject)
        path = _rel(str(pyproject), repo_root)
    else:
        for name in ("pytest.ini", "tox.ini"):
            candidate = root / name
            if candidate.is_file():
                raw = _gate_from_ini(candidate)
                path = _rel(str(candidate), repo_root)
                break
    coverage_sources = raw.get("coverage_sources", [])
    if isinstance(coverage_sources, str):
        coverage_sources = [coverage_sources]
    return GateConfig(
        path=path,
        addopts=_tokens(raw.get("addopts", "")),
        markers=_markers(raw.get("markers", [])),
        strict_markers=bool(raw.get("strict_markers", False)) or
                       "--strict-markers" in _tokens(raw.get("addopts", "")),
        coverage_sources=tuple(str(value) for value in coverage_sources
                               if isinstance(value, str) and value.strip()),
        coverage_floor=(float(raw["coverage_floor"])
                        if isinstance(raw.get("coverage_floor"), (int, float))
                        and not isinstance(raw.get("coverage_floor"), bool) else None),
    )


def build_inventory(root: str) -> tuple[ProofInventory | None, dict]:
    """Walk one configured proof root and return a single static inventory."""
    config, err = load_proof_config(root)
    if err:
        return None, err
    assert config is not None
    repo_root = config["repoRoot"]
    proof_root = config["proofRoot"]
    if not os.path.isdir(proof_root):
        return None, {
            "code": "pf-root-missing",
            "exit": 2,
            "path": config["declaredProofRoot"],
            "message": f"configured proofRoot `{config['declaredProofRoot']}` does not exist",
        }

    layers = _layer_models(proof_root, config["layers"])
    tests: list[TestModule] = []
    fixtures: list[Fixture] = []
    conftests: list[Conftest] = []
    for directory, dirnames, filenames in os.walk(proof_root):
        dirnames[:] = sorted(name for name in dirnames if name not in _SKIP_DIRS)
        for filename in sorted(filenames):
            if not filename.endswith(".py"):
                continue
            absolute = Path(directory) / filename
            relative = _rel(str(absolute), proof_root)
            tree = _parse(absolute)
            imports = _imports(tree)
            fixture_names = _fixture_names(tree)
            is_library = relative == "fixtures/conftest.py" or relative.startswith("fixtures/")
            for name in fixture_names:
                fixtures.append(Fixture(name, relative, is_library))
            if filename == "conftest.py":
                conftests.append(Conftest(relative, relative.startswith("fixtures/"),
                                           fixture_names, imports))
            if _TEST_RE.match(filename) and not relative.startswith("fixtures/"):
                layer = _layer_for(relative, config["layers"])
                tests.append(TestModule(relative, layer, _marker_for(layer), imports,
                                        _test_count(tree)))

    gate = _gate(repo_root)
    measured = tuple(item["relative"] for item in config["measuredRoots"])
    exclusions = tuple(item["relative"] for item in config["proofExclusions"])
    return ProofInventory(repo_root, proof_root, layers, tuple(tests), tuple(fixtures),
                          tuple(conftests), gate, discover_ci(repo_root, proof_root),
                          measured, exclusions), {}


def inventory(root: str) -> tuple[ProofInventory | None, dict]:
    """Public alias for callers that use the operation's noun."""
    return build_inventory(root)
