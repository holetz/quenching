"""The temp-root guard: it catches a pinned location and leaves a data literal alone.

Each case is a source string, so the guard is exercised on shapes the suite must refuse without any
of them existing on disk. The last case is the real `quenching/tests/`, which is the regression that
matters: a new test pinning a temp path fails here before it fails in the gate.
"""

from __future__ import annotations

import contextlib
import io
import pathlib
import sys
import tempfile
import unittest

try:
    import _paths  # noqa: F401 — the suite's temp root and git isolation, before any test runs
except ModuleNotFoundError:
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    import _paths  # noqa: F401

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.toolchain import check_tmp  # noqa: E402

TESTS_DIR = pathlib.Path(__file__).resolve().parent


class GuardCase(unittest.TestCase):
    def findings(self, source: str) -> list[str]:
        return check_tmp.scan_source(source, "m.py")

    def test_a_literal_handed_to_the_filesystem_is_a_finding(self):
        got = self.findings('import pathlib\npathlib.Path("/tmp/x")\n')
        self.assertEqual(len(got), 1)
        self.assertTrue(got[0].startswith("m.py:2: "))
        self.assertIn("/tmp/x", got[0])

    def test_a_data_literal_is_not_a_finding(self):
        source = (
            "payload = {'path': '/tmp/x', 'socket': '/tmp/' + secret}\n"
            "self.assertEqual(value, '/tmp/x')\n"
            "self.assertIn('/tmp', text)\n"
            "text = f'prefix /tmp/x and {tail}'\n"
        )
        self.assertEqual(self.findings(source), [])

    def test_the_dir_and_cwd_keywords_are_findings(self):
        source = ('import tempfile, subprocess\n'
                  'tempfile.TemporaryDirectory(dir="/tmp/x")\n'
                  'subprocess.run(["git", "init"], cwd="/tmp/x")\n')
        self.assertEqual(len(self.findings(source)), 2)

    def test_an_f_string_that_starts_at_a_temp_root_is_a_finding(self):
        got = self.findings('open(f"/tmp/{name}.txt")\n')
        self.assertEqual(len(got), 1)

    def test_an_assignment_to_tempfile_tempdir_is_a_finding(self):
        for source in ('import tempfile\ntempfile.tempdir = "/x"\n',
                       'import tempfile\nsetattr(tempfile, "tempdir", "/x")\n'):
            with self.subTest(source=source):
                self.assertEqual(len(self.findings(source)), 1)

    def test_an_environment_write_of_a_temp_root_is_a_finding(self):
        got = self.findings('import os\nos.environ["TMPDIR"] = "/tmp/x"\n')
        self.assertEqual(len(got), 1)

    def test_a_syntax_error_is_reported_not_skipped(self):
        got = self.findings("def broken(:\n")
        self.assertIn("cannot parse", got[0])

    def test_the_cli_fails_on_a_planted_violation_and_passes_a_clean_tree(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            (root / "test_clean.py").write_text("value = {'path': '/tmp'}\n", encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(check_tmp.main([str(root)]), 0)
            (root / "test_dirty.py").write_text('import pathlib\n'
                                                'pathlib.Path("/tmp/x")\n', encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()) as out:
                self.assertEqual(check_tmp.main([str(root)]), 1)
            self.assertIn("test_dirty.py", out.getvalue())

    def test_the_real_suite_has_no_findings(self):
        self.assertEqual(check_tmp.scan(sorted(TESTS_DIR.glob("*.py"))), [])


if __name__ == "__main__":
    unittest.main()
