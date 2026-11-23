"""A common `cq` call imports a bounded set of modules and none of the heavy ones.

Every `cq` call starts a new interpreter, so each module imported on the way in is paid again and
re-scanned by the antivirus on every call. The count is the stable measure (milliseconds vary with
the machine); the named modules are the ones a pillar once pulled in through an eager import."""
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest

CQ = pathlib.Path(__file__).resolve().parents[1] / "assets" / "bin" / "cq"

# Measured on Python 3.14 after the lazy dispatch: 172 for `specs --help`, 176 for `specs status`,
# against 281 and 280 before. The ceiling leaves room for the interpreter's own version drift.
MODULE_CEILING = 230
FORBIDDEN = ("http.server", "http.client", "email", "socket", "statistics", "decimal")


def imported_modules(*argv: str) -> list[str]:
    env = {k: v for k, v in os.environ.items() if k not in ("PYTHONUTF8", "PYTHONIOENCODING")}
    result = subprocess.run([sys.executable, "-X", "importtime", str(CQ), *argv],
                            capture_output=True, env=env, timeout=120)
    lines = result.stderr.decode("utf-8", "replace").splitlines()
    return [line.rsplit("|", 1)[1].strip() for line in lines
            if line.startswith("import time:") and line.count("|") == 2
            and line.split("|")[0].split(":", 1)[1].strip().isdigit()]


class CqImportBudget(unittest.TestCase):
    def assert_budget(self, modules: list[str]) -> None:
        self.assertTrue(modules, "no `-X importtime` output was parsed")
        self.assertLessEqual(len(modules), MODULE_CEILING, f"{len(modules)} modules imported")
        heavy = sorted(set(modules) & set(FORBIDDEN))
        self.assertEqual(heavy, [], f"imported eagerly on a common call: {heavy}")

    def test_specs_help_stays_inside_the_budget(self):
        self.assert_budget(imported_modules("specs", "--help"))

    def test_specs_status_stays_inside_the_budget(self):
        with tempfile.TemporaryDirectory() as root:
            self.assert_budget(imported_modules("specs", "status", "--root", root, "--json"))

    def test_dispatch_resolves_each_row_to_a_function(self):
        sys.path.insert(0, str(CQ.parent))
        try:
            from quenching.specs.commands.cli import DISPATCH
            for verb in DISPATCH:
                self.assertTrue(callable(DISPATCH[verb]), verb)
        finally:
            sys.path.remove(str(CQ.parent))


if __name__ == "__main__":
    unittest.main()
