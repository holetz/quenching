"""`cq specs validate` with no `--spec` answers with the summary by code, not the whole store."""
import argparse
import contextlib
import io
import json
import pathlib
import sys
import tempfile
import unittest
from unittest import mock

try:
    import _paths  # noqa: F401  — must precede the `quenching` import; see its docstring
except ModuleNotFoundError:  # package-qualified unittest invocation from the repository root
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    import _paths  # noqa: F401
from quenching.specs.backends.memory import MemoryBackend
from quenching.specs.commands import validate as validate_cmd
from quenching.specs.commands.output import Emitter


def run(backend, **kw):
    kw.setdefault("spec", None)
    kw.setdefault("phase", None)
    kw.setdefault("by_code", False)
    args = argparse.Namespace(json=True, **kw)
    buf = io.StringIO()
    with mock.patch.object(validate_cmd, "open_backend", return_value=(backend, {})), \
            contextlib.redirect_stdout(buf):
        code = validate_cmd.cmd_validate(args, tempfile.gettempdir(), Emitter())
    return code, json.loads(buf.getvalue())


class ValidateSummary(unittest.TestCase):
    def setUp(self):
        self.b = MemoryBackend()
        for n in range(3):
            self.b.create_spec("plans", f"---\ntitle: S{n}\ndate: 2026-01-01\nepic: 1\n---\n\n## Problem\n\nx\n")

    def test_whole_store_defaults_to_the_summary_without_the_spec_lists(self):
        _, got = run(self.b, full=False)
        self.assertTrue(got["summary"])
        self.assertNotIn("findings", got)
        self.assertTrue(got["byCode"])
        self.assertTrue(all("specs" not in r and r["count"] for r in got["byCode"]))

    def test_with_specs_lists_the_affected_specs(self):
        _, got = run(self.b, full=False, with_specs=True)
        self.assertTrue(all(r["specs"] for r in got["byCode"]))

    def test_full_and_spec_keep_the_findings(self):
        _, got = run(self.b, full=True)
        self.assertIn("findings", got)
        _, got = run(self.b, full=False, spec="1")
        self.assertIn("findings", got)


if __name__ == "__main__":
    unittest.main()
