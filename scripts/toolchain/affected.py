"""Select the tests a change reaches, with the whole suite as the safe answer.

The task loop runs a `verify:` for every task, several times per spec, in several worktrees at
once — the load this spec exists to remove. This module narrows that run to the tests a diff can
break. It follows SAFRA's `scripts/toolchain/afetados.py`: a table maps each source surface to the
tests that cover it, each test's direct imports are read from the AST to catch cross-module use, and
the diff is the merge base plus the working tree plus untracked files.

**Any doubt runs the whole suite.** That is a decision, never an error: a global file, a path no
rule covers, a rule pointing at a test that no longer exists, an unresolvable base, a source change
that selected nothing. A selector that guesses is worse than no selector, because a green run would
mean less than it says.

The heavy layer (`integration`, applied by `scripts.toolchain.layers`) is not this module's
business: the runner decides whether to keep it.

Usage::

    python -m scripts.toolchain.affected --base origin/main --json
    python -m scripts.toolchain.affected quenching/assets/bin/quenching/git/audit.py
"""

from __future__ import annotations

import argparse
import ast
import dataclasses
import json
import pathlib
import subprocess
import sys

TESTS_DIR = "quenching/tests"
GLOBAL = (
    "pyproject.toml",
    "uv.lock",
    ".coverage-floor.json",
    "zensical.toml",
    "quenching/assets/modules.json",
    "quenching/assets/bin/quenching/common/",
    "scripts/verify_repo.sh",
    "scripts/toolchain/",
)
IRRELEVANT = (
    "docs/",
    "site/",
    "site-source/",
    ".agents/",
    ".claude/",
    ".opencode/",
    ".quenching/",
    "experiments/",
    "design-system/",
)


@dataclasses.dataclass(frozen=True)
class Rule:
    """One source surface and the tests that cover it; a `*` in a test name is a glob stem."""

    prefixes: tuple[str, ...]
    tests: tuple[str, ...]


# The table is deliberately generous: an extra test costs seconds, a missing one costs a green that
# lied. Every entry names real files, and `select` fails open when one of them stops existing.
RULES: tuple[Rule, ...] = (
    Rule(("quenching/assets/bin/quenching/git/",),
         ("test_git", "test_git_*", "test_identity_*", "test_orchestrator_*", "test_spec_runner_wait")),
    Rule(("quenching/assets/bin/quenching/specs/",),
         ("test_specs_*", "test_spec_runner_wait", "test_handoff_command", "test_orchestrator_*",
          "test_autopilot_*")),
    Rule(("quenching/assets/bin/quenching/components/",),
         ("test_components*", "test_commands_catalog", "test_router_descriptions",
          "test_readme_surface", "test_surface_listings")),
    Rule(("quenching/assets/bin/quenching/knowledge/",),
         ("test_knowledge*", "test_zensical_*", "test_frontmatter*", "test_surface_listings")),
    Rule(("quenching/assets/bin/quenching/proof/",),
         ("test_proof", "test_worker_budget_estimate")),
    Rule(("quenching/assets/bin/quenching/deploy/",),
         ("test_deploy*", "test_install_profiles", "test_opensource_controls")),
    Rule(("quenching/assets/bin/quenching/security/",),
         ("test_security", "test_leak_*", "test_public_readiness", "test_opensource_*")),
    Rule(("quenching/assets/bin/quenching/ops/",), ("test_ops", "test_delivery")),
    Rule(("quenching/assets/bin/quenching/delivery/",), ("test_delivery",)),
    Rule(("quenching/assets/bin/quenching/design/",), ("test_design",)),
    Rule(("quenching/assets/bin/quenching/opensource/",), ("test_opensource_*",)),
    Rule(("quenching/assets/bin/quenching/toolchain/",), ("test_toolchain*",)),
    Rule(("quenching/assets/bin/quenching/portal/",), ("test_portal_*", "test_quenching_mcp*")),
    Rule(("quenching/assets/bin/quenching/mcp/",), ("test_quenching_mcp*", "test_specs_mcp")),
    Rule(("quenching/assets/bin/quenching/session/",),
         ("test_session*", "test_context_distribution", "test_autopilot_*")),
    Rule(("quenching/assets/bin/quenching/config/",),
         ("test_config_*", "test_user_config_layer", "test_owner_controls")),
    Rule(("quenching/assets/bin/quenching/controls/",), ("test_owner_controls",)),
    Rule(("quenching/assets/bin/quenching/codex/",), ("test_codex_*",)),
    Rule(("quenching/skills/quenching-specs/",),
         ("test_specs_*", "test_autopilot_*", "test_handoff_command", "test_spec_runner_wait",
          "test_orchestrator_*")),
    Rule(("quenching/skills/quenching-git/",), ("test_git*", "test_identity_*")),
    Rule(("quenching/skills/quenching-knowledge/",),
         ("test_knowledge*", "test_frontmatter*", "test_sections", "test_front_mold",
          "test_study_material")),
    Rule(("quenching/skills/quenching-components/",),
         ("test_components*", "test_commands_catalog", "test_router_descriptions",
          "test_surface_listings")),
    Rule(("quenching/skills/quenching-proof/",), ("test_proof",)),
    Rule(("quenching/skills/quenching-ops/",), ("test_ops",)),
    Rule(("quenching/skills/quenching-delivery/",), ("test_delivery",)),
    Rule(("quenching/skills/quenching-design/",), ("test_design",)),
    Rule(("quenching/skills/quenching-opensource/",), ("test_opensource_*",)),
    Rule(("quenching/skills/quenching-security/",), ("test_security", "test_leak_*")),
    Rule(("quenching/skills/quenching-toolchain/",), ("test_toolchain*",)),
    Rule(("quenching/skills/quenching-handoff/",), ("test_handoff_command",)),
    Rule(("quenching/skills/quenching-align/",), ("test_align_contract",)),
    Rule(("quenching/references/",),
         ("test_commands_catalog", "test_surface_listings", "test_readme_surface",
          "test_align_contract", "test_frontmatter*")),
    Rule(("quenching/agents/",),
         ("test_components*", "test_opensource_controls", "test_public_readiness")),
    Rule(("quenching/assets/knowledge/",),
         ("test_knowledge*", "test_frontmatter*", "test_specs_assets", "test_surface_listings")),
    Rule(("quenching/assets/checks/",),
         ("test_verify_repo_functional", "test_functional_checks_isolation",
          "test_public_readiness", "test_opensource_controls")),
    Rule(("quenching/assets/hooks/",), ("test_hook_*", "test_deploy_settings")),
    Rule(("quenching/assets/templates/",), ("test_deploy*", "test_components*")),
    Rule(("quenching/VERSION",),
         ("test_readme_surface", "test_deploy*", "test_specs_release", "test_opensource_controls",
          "test_public_readiness")),
    Rule(("AGENTS.md",), ("test_deploy", "test_components_migrate")),
    Rule((".github/",), ("test_proof", "test_public_readiness", "test_opensource_controls")),
    Rule(("scripts/",),
         ("test_toolchain_*", "test_verify_repo_functional", "test_opensource_controls",
          "test_suite")),
)


@dataclasses.dataclass(frozen=True)
class Selection:
    """What to run, and why — `complete` means the answer is the whole suite."""

    base: str | None
    changed: tuple[str, ...]
    tests: tuple[str, ...]
    reasons: tuple[str, ...]
    complete: bool

    def as_json(self) -> dict:
        return {"base": self.base, "changed": list(self.changed), "tests": list(self.tests),
                "reasons": list(self.reasons), "complete": self.complete}


def _run(root: pathlib.Path, *argv: str) -> tuple[int, str, str]:
    try:
        proc = subprocess.run(["git", *argv], cwd=root, capture_output=True, text=True)
    except OSError as exc:
        return 127, "", str(exc)
    return proc.returncode, proc.stdout, proc.stderr


def _covers(path: str, prefix: str) -> bool:
    return path == prefix or path.startswith(prefix if prefix.endswith("/") else prefix + "/")


def import_root() -> pathlib.Path:
    """The repository root, from this file's position."""
    return pathlib.Path(__file__).resolve().parents[2]


def merge_base(root: pathlib.Path, base: str) -> str:
    """The commit the diff is taken from, or raise :class:`ValueError`."""
    code, out, err = _run(root, "merge-base", base, "HEAD")
    if code != 0:
        raise ValueError(f"cannot resolve the merge base with {base}: {err.strip() or out.strip()}")
    return out.strip()


def changed_paths(root: pathlib.Path, base: str | None = None) -> tuple[str, ...]:
    """Tracked changes since the merge base, plus the working tree and untracked files."""
    code, inside, _ = _run(root, "rev-parse", "--is-inside-work-tree")
    if code != 0 or inside.strip() != "true":
        raise ValueError("not a git working tree")
    reference = merge_base(root, base) if base else None
    paths: set[str] = set()
    if reference:
        code, out, err = _run(root, "diff", "--name-only", "--no-renames", reference)
        if code != 0:
            raise ValueError(f"git diff failed: {err.strip()}")
        paths.update(line for line in out.splitlines() if line)
    for argv in (("diff", "--name-only", "--no-renames", "HEAD"),
                 ("ls-files", "--others", "--exclude-standard")):
        code, out, err = _run(root, *argv)
        if code != 0:
            raise ValueError(f"git {argv[0]} failed: {err.strip()}")
        paths.update(line for line in out.splitlines() if line)
    return tuple(sorted(path.replace("\\", "/") for path in paths if path))


def _module_of(path: str) -> str | None:
    """The dotted module a shipped Python file defines, or None outside the shipped package."""
    if not path.endswith(".py") or not path.startswith("quenching/assets/bin/"):
        return None
    parts = list(pathlib.PurePosixPath(path).relative_to("quenching/assets/bin").with_suffix("").parts)
    if parts and parts[-1] == "__init__":
        parts.pop()
    return ".".join(parts) or None


def _imports_of(path: pathlib.Path) -> frozenset[str]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError, UnicodeDecodeError):
        return frozenset()
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            names.add(node.module)
    return frozenset(names)


def _imports_module(imported: str, module: str) -> bool:
    return (imported == module or imported.startswith(module + ".")
            or module.startswith(imported + "."))


def _tests_importing(root: pathlib.Path, modules: set[str]) -> set[str]:
    """Every test module whose direct imports reach one of `modules`."""
    if not modules:
        return set()
    found: set[str] = set()
    for path in sorted((root / TESTS_DIR).glob("test_*.py")):
        for imported in _imports_of(path):
            if any(_imports_module(imported, module) for module in modules):
                found.add(str(path.relative_to(root)).replace("\\", "/"))
                break
    return found


def _rule_for(path: str) -> Rule | None:
    for rule in RULES:
        if any(_covers(path, prefix) for prefix in rule.prefixes):
            return rule
    return None


def _resolve_tests(root: pathlib.Path, stems: tuple[str, ...]) -> tuple[list[str], str | None]:
    """Expand a rule's test stems into existing paths, or name the literal one that is missing."""
    tests: list[str] = []
    directory = root / TESTS_DIR
    for stem in stems:
        if stem.endswith("*"):
            matches = sorted(directory.glob(stem + ".py"))
        else:
            matches = [directory / f"{stem}.py"]
            if not matches[0].is_file():
                return [], f"rule names {TESTS_DIR}/{stem}.py, which does not exist"
        tests.extend(str(match.relative_to(root)).replace("\\", "/")
                     for match in matches if match.is_file())
    return tests, None


def _reduce(tests: list[str]) -> tuple[str, ...]:
    """Sort and drop a path already covered by a selected directory."""
    reduced: list[str] = []
    for test in sorted(set(tests)):
        if any(test.startswith(parent.rstrip("/") + "/") for parent in reduced):
            continue
        reduced.append(test)
    return tuple(reduced)


def select(root: pathlib.Path, base: str | None = None,
           files: list[str] | None = None) -> Selection:
    """The selection for `files`, or for the diff against `base`; never raises on doubt."""
    try:
        changed = tuple(files) if files is not None else changed_paths(root, base)
    except ValueError as exc:
        return Selection(base, (), (), (f"fail-open: {exc}",), True)
    changed = tuple(path.replace("\\", "/") for path in changed if path)
    if not changed:
        return Selection(base, (), (), ("nothing changed",), False)

    deleted_tests = [path for path in changed
                     if path.startswith(TESTS_DIR + "/") and not (root / path).exists()]
    if deleted_tests:
        return Selection(base, changed, (),
                         (f"fail-open: {deleted_tests[0]} was deleted or moved",), True)

    selected: set[str] = set()
    modules: set[str] = set()
    reasons: list[str] = []
    covered = 0
    for path in changed:
        if any(_covers(path, prefix) for prefix in GLOBAL):
            return Selection(base, changed, (), (f"fail-open: {path} is global",), True)
        if path.startswith(TESTS_DIR + "/"):
            name = pathlib.PurePosixPath(path).name
            if not (name.startswith("test_") and name.endswith(".py")):
                return Selection(base, changed, (), (f"fail-open: {path} sustains the whole suite",), True)
            selected.add(path)
            reasons.append(f"{path} -> itself")
            covered += 1
            continue
        rule = _rule_for(path)
        if rule is None:
            if any(_covers(path, prefix) for prefix in IRRELEVANT):
                continue
            return Selection(base, changed, (), (f"fail-open: no rule covers {path}",), True)
        tests, problem = _resolve_tests(root, rule.tests)
        if problem:
            return Selection(base, changed, (), (f"fail-open: {problem}",), True)
        selected.update(tests)
        reasons.append(f"{path} -> {rule.prefixes[0]}")
        module = _module_of(path)
        if module:
            modules.add(module)
        covered += 1

    if not covered:
        return Selection(base, changed, (), ("change outside the tested surfaces",), False)
    selected.update(_tests_importing(root, modules))
    if not selected:
        return Selection(base, changed, (), (f"fail-open: {changed[0]} selected no test",), True)
    return Selection(base, changed, _reduce(list(selected)), tuple(dict.fromkeys(reasons)), False)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("--base", default=None, help="merge-base reference (default: the working tree only)")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("paths", nargs="*", help="explicit paths; without them the git diff decides")
    args = parser.parse_args(argv)
    selection = select(import_root(), args.base, args.paths or None)
    if args.json:
        print(json.dumps(selection.as_json(), indent=2))
    else:
        for test in selection.tests:
            print(test)
        for reason in selection.reasons:
            print(f"[affected] {reason}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
