"""The suite's own two properties: it collects something, and it needs nothing installed.

"Dependency-free stdlib Python" is the repo's oldest claim about its tools and it was never
measured — an `import yaml` added anywhere would have shipped, and the first person to find out
would be a user whose target repo has no PyYAML. `test_no_external_imports` turns the claim into
an assertion over the AST of every module the plugin ships and every module this suite runs.

`test_discovery_is_not_empty` covers the failure mode this suite is otherwise blind to: a run that
collects zero tests exits 0 and reads exactly like a run where everything passed.
"""

import ast
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest

TESTS_DIR = pathlib.Path(__file__).resolve().parent
PLUGIN_ROOT = TESTS_DIR.parent
PACKAGE_DIR = PLUGIN_ROOT / "assets" / "bin" / "quenching"

def first_party() -> set[str]:
    """Names that resolve only because the suite runs from this repository.

    `tests/` joins `sys.path` through `discover`, and the repository root through `_paths.py`, which
    every test module imports first — `scripts` is this repository's own tooling, not a dependency.
    Derived from disk rather than listed: a hard-coded allowlist makes every new helper in
    `tests/` look like an external dependency, and the cheapest way out of that is to reach the
    helper through `importlib` — evading this check instead of satisfying it.
    """
    return {"quenching", "scripts"} | {path.stem for path in TESTS_DIR.glob("*.py")}


def top_level_imports(source: str) -> set[str]:
    """The root name of every module a file imports, ignoring relative imports."""
    names = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            names.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            names.add(node.module.split(".")[0])
    return names


class SuiteIntegrity(unittest.TestCase):
    def test_no_external_imports(self):
        """Every module the plugin ships, and every module this suite runs, imports stdlib only."""
        files = sorted(PACKAGE_DIR.rglob("*.py")) + sorted(TESTS_DIR.glob("*.py"))
        self.assertTrue(files, "no python files found to inspect")
        allowed = sys.stdlib_module_names | first_party()
        for path in files:
            with self.subTest(path=str(path.relative_to(PLUGIN_ROOT))):
                foreign = sorted(top_level_imports(path.read_text(encoding="utf-8")) - allowed)
                self.assertEqual([], foreign)

    def test_discovery_is_not_empty(self):
        """`discover -s tests` collects tests — an empty run is a green that proves nothing."""
        suite = unittest.defaultTestLoader.discover(str(TESTS_DIR), top_level_dir=str(TESTS_DIR))
        self.assertGreater(suite.countTestCases(), 0)
        self.assertEqual([], unittest.defaultTestLoader.errors)


class GitIsolation(unittest.TestCase):
    """The suite reads this configuration instead of the machine's — and proves it with git."""

    def test_the_global_file_replaces_the_machines(self):
        import _paths  # noqa: F401  — the import is what exports it

        global_file = pathlib.Path(os.environ["GIT_CONFIG_GLOBAL"])
        text = global_file.read_text(encoding="utf-8")
        self.assertEqual("1", os.environ.get("GIT_CONFIG_NOSYSTEM"))
        self.assertIn("defaultBranch = main", text)
        self.assertIn("fsync = none", text)
        self.assertNotIn("user", text)  # identity stays per repository, never command scope

    def test_a_fresh_repository_inherits_it(self):
        with tempfile.TemporaryDirectory() as tmp:
            subprocess.run(["git", "init", "-q", tmp], check=True)
            head = subprocess.run(["git", "-C", tmp, "symbolic-ref", "--short", "HEAD"],
                                  check=True, capture_output=True, text=True).stdout.strip()
            fsync = subprocess.run(["git", "-C", tmp, "config", "--get", "core.fsync"],
                                   check=True, capture_output=True, text=True).stdout.strip()
        self.assertEqual("main", head)
        self.assertEqual("none", fsync)

    def test_a_repository_setting_beats_the_global_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            subprocess.run(["git", "init", "-q", tmp], check=True)
            subprocess.run(["git", "-C", tmp, "config", "init.defaultBranch", "trunk"], check=True)
            read = subprocess.run(["git", "-C", tmp, "config", "--get", "init.defaultBranch"],
                                  check=True, capture_output=True, text=True).stdout.strip()
        self.assertEqual("trunk", read)


if __name__ == "__main__":
    unittest.main()
