"""Executable proofs for `cq security leak`, run in a temporary repository."""
from __future__ import annotations

import contextlib
import io
import json
import os
import pathlib
import sys
import tempfile
import unittest
from unittest import mock

try:
    import _paths  # noqa: F401 — must precede the `quenching` import
except ModuleNotFoundError:  # package-qualified unittest invocation from the repository root
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    import _paths  # noqa: F401
from quenching.common import leak
from quenching.security import main
from test_leak_scan import DATABRICKS_HOST, HOME, git, init_repo


def run(argv: list[str], stdin: str = "") -> tuple[int, dict]:
    out = io.StringIO()
    with contextlib.redirect_stdout(out), mock.patch.object(sys, "stdin", io.StringIO(stdin)):
        code = main([*argv, "--json"])
    return code, json.loads(out.getvalue())


class LeakVerb(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.denylist = pathlib.Path(self._tmp.name, "denylist.txt")
        self.denylist.write_text("acme-corp\n", encoding="utf-8")
        patcher = mock.patch.dict(os.environ, {"HOME": HOME, leak.DENYLIST_ENV: str(self.denylist)})
        patcher.start()
        self.addCleanup(patcher.stop)
        self.repo = str(pathlib.Path(self._tmp.name, "repo"))
        os.mkdir(self.repo)
        init_repo(self.repo)
        pathlib.Path(self.repo, "a.txt").write_text("clean\n", encoding="utf-8")
        git(self.repo, "add", "a.txt")
        git(self.repo, "commit", "-q", "-m", "base")

    def test_staged_finding_exits_one_with_label_and_line(self):
        pathlib.Path(self.repo, "b.txt").write_text(f"x\n{DATABRICKS_HOST}\n", encoding="utf-8")
        git(self.repo, "add", "b.txt")
        code, payload = run(["leak", "--staged", "--root", self.repo])
        self.assertEqual(code, 1)
        self.assertEqual([(f["where"], f["line"], f["label"]) for f in payload["findings"]],
                         [("b.txt", 2, "azure-databricks-host")])

    def test_clean_tree_exits_zero(self):
        self.assertEqual(run(["leak", "--all", "--root", self.repo])[0], 0)

    def test_missing_denylist_refuses_unless_generic_only(self):
        self.denylist.unlink()
        code, payload = run(["leak", "--staged", "--root", self.repo])
        self.assertEqual((code, payload["code"]), (2, "leak-denylist-missing"))
        self.assertEqual(run(["leak", "--staged", "--generic-only", "--root", self.repo])[0], 0)

    def test_pre_push_reads_the_hook_lines_from_stdin(self):
        base = git(self.repo, "rev-parse", "HEAD").strip()
        git(self.repo, "commit", "-q", "--allow-empty", "-m", "about acme-corp")
        head = git(self.repo, "rev-parse", "HEAD").strip()
        code, payload = run(["leak", "--pre-push", "--root", self.repo],
                            f"refs/heads/main {head} refs/heads/main {base}\n")
        self.assertEqual((code, payload["mode"]), (1, "pre-push"))

    def test_leak_without_a_mode_refuses_and_audit_keeps_its_flags_clean(self):
        self.assertEqual(run(["leak", "--root", self.repo])[1]["code"], "leak-mode-missing")
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            main(["audit", "--staged", "--root", self.repo])


if __name__ == "__main__":
    unittest.main()
