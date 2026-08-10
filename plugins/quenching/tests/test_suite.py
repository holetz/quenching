"""The suite's own two properties: it collects something, and it needs nothing installed.

"Dependency-free stdlib Python" is the repo's oldest claim about its tools and it was never
measured — an `import yaml` added anywhere would have shipped, and the first person to find out
would be a user whose target repo has no PyYAML. `test_no_external_imports` turns the claim into
an assertion over the AST of every module the plugin ships and every module this suite runs.

`test_discovery_is_not_empty` covers the failure mode this suite is otherwise blind to: a run that
collects zero tests exits 0 and reads exactly like a run where everything passed.
"""

import ast
import pathlib
import sys
import unittest

TESTS_DIR = pathlib.Path(__file__).resolve().parent
PLUGIN_ROOT = TESTS_DIR.parent
PACKAGE_DIR = PLUGIN_ROOT / "assets" / "bin" / "quenching"

# `_paths` is first-party: it is how a test reaches the package, and it resolves nowhere on
# `sys.path` until `discover` puts this directory there.
FIRST_PARTY = {"quenching", "_paths"}


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
        allowed = sys.stdlib_module_names | FIRST_PARTY
        for path in files:
            with self.subTest(path=str(path.relative_to(PLUGIN_ROOT))):
                foreign = sorted(top_level_imports(path.read_text(encoding="utf-8")) - allowed)
                self.assertEqual([], foreign)

    def test_discovery_is_not_empty(self):
        """`discover -s tests` collects tests — an empty run is a green that proves nothing."""
        suite = unittest.defaultTestLoader.discover(str(TESTS_DIR), top_level_dir=str(TESTS_DIR))
        self.assertGreater(suite.countTestCases(), 0)
        self.assertEqual([], unittest.defaultTestLoader.errors)


if __name__ == "__main__":
    unittest.main()
