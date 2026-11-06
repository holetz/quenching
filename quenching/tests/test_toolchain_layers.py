"""The `integration` layer: registered, applied by its plugin, and selectable end to end.

The plugin is exercised with fake items for the unit of the decision, and once against the real
suite with `--collect-only`: a marker that does not reach collection would make the affected run
silently larger than promised, which is the failure this file is here to catch.
"""

from __future__ import annotations

import importlib.util
import pathlib
import subprocess
import sys
import tomllib
import unittest
from types import SimpleNamespace

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.toolchain import layers  # noqa: E402

TESTS_DIR = pathlib.Path(__file__).resolve().parent
HAS_PYTEST = importlib.util.find_spec("pytest") is not None


class Marker(unittest.TestCase):
    def test_it_is_registered_as_a_marker(self):
        config = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        markers = config["tool"]["pytest"]["ini_options"]["markers"]
        self.assertTrue(any(entry.startswith("integration:") for entry in markers), markers)

    def test_only_the_listed_modules_get_the_marker(self):
        marked: list[str] = []

        def item(name: str):
            return SimpleNamespace(path=pathlib.Path("tests") / name,
                                   add_marker=lambda marker, name=name: marked.append(name))

        layers.pytest_collection_modifyitems(
            None, [item("test_git.py"), item("test_toolchain_layers.py"), item("test_deploy.py")])
        self.assertEqual(["test_git.py", "test_deploy.py"], marked)

    def test_the_listed_modules_all_exist(self):
        for name in sorted(layers.INTEGRATION_MODULES):
            with self.subTest(name=name):
                self.assertTrue((TESTS_DIR / name).is_file())

    @unittest.skipUnless(HAS_PYTEST, "pytest is not installed in this interpreter")
    def test_collection_selects_only_the_listed_modules(self):
        proc = subprocess.run(
            [sys.executable, "-m", "pytest", "quenching/tests", "-q", "--collect-only",
             "-p", "scripts.toolchain.layers", "-m", "integration"],
            cwd=REPO_ROOT, capture_output=True, text=True)
        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
        collected = [line.split("::")[0] for line in proc.stdout.splitlines() if "::" in line]
        self.assertTrue(collected, "no test collected under the integration marker")
        names = {pathlib.Path(path).name for path in collected}
        self.assertEqual(set(layers.INTEGRATION_MODULES), names)


if __name__ == "__main__":
    unittest.main()
