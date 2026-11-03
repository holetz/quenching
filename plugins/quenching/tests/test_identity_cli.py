"""Executable proofs for `cq security identity` and the identity findings `leak` adds."""
from __future__ import annotations

import contextlib
import io
import json
import os
import pathlib
import sys
import unittest
from unittest import mock

try:
    import _paths  # noqa: F401 — must precede the `quenching` import
except ModuleNotFoundError:  # package-qualified unittest invocation from the repository root
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    import _paths  # noqa: F401
from quenching.security import main
from test_identity_allowlist import ALLOWED, OUTSIDE, IdentityRepo, declare
from test_leak_scan import HOME, git


def run(argv: list[str], stdin: str = "", as_json: bool = True) -> tuple[int, object]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err), \
            mock.patch.object(sys, "stdin", io.StringIO(stdin)):
        code = main([*argv, "--json"] if as_json else argv)
    text = out.getvalue() or err.getvalue()
    return code, json.loads(text) if as_json else text


class IdentityVerb(IdentityRepo):
    def setUp(self):
        super().setUp()
        patcher = mock.patch.dict(os.environ, {"HOME": HOME})
        patcher.start()
        self.addCleanup(patcher.stop)
        pathlib.Path(self.repo, "a.txt").write_text("clean\n", encoding="utf-8")
        git(self.repo, "add", "a.txt")
        git(self.repo, "commit", "-q", "-m", "base")
        self.base = git(self.repo, "rev-parse", "HEAD").strip()

    def test_undeclared_judges_nothing(self):
        git(self.repo, "config", "user.email", OUTSIDE)
        code, out = run(["identity", "--staged", "--root", self.repo])
        self.assertEqual((code, out["declared"], out["findings"]), (0, False, []))
        code, text = run(["identity", "--staged", "--root", self.repo], as_json=False)
        self.assertEqual(code, 0)
        self.assertIn("nothing judged", text)

    def test_staged_outside_the_list_exits_one_naming_the_email_and_remedy(self):
        declare(self.repo, {"allowedEmails": ALLOWED})
        self.assertEqual(run(["identity", "--staged", "--root", self.repo])[0], 0)
        git(self.repo, "config", "user.email", OUTSIDE)
        code, out = run(["identity", "--staged", "--root", self.repo])
        self.assertEqual(code, 1)
        self.assertEqual({f["excerpt"] for f in out["findings"]}, {OUTSIDE})
        code, text = run(["identity", "--staged", "--root", self.repo], as_json=False)
        self.assertIn(OUTSIDE, text)
        self.assertIn("git config user.email", text)

    def test_pre_push_judges_the_published_commits(self):
        declare(self.repo, {"allowedEmails": ALLOWED})
        pathlib.Path(self.repo, "b.txt").write_text("b\n", encoding="utf-8")
        git(self.repo, "add", "b.txt")
        with mock.patch.dict(os.environ, {"GIT_AUTHOR_EMAIL": OUTSIDE}):
            git(self.repo, "commit", "-q", "-m", "b")
        head = git(self.repo, "rev-parse", "HEAD").strip()
        line = f"refs/heads/main {head} refs/heads/main {self.base}\n"
        code, text = run(["identity", "--pre-push", "--root", self.repo], line, as_json=False)
        self.assertEqual(code, 1)
        self.assertIn("--reset-author", text)
        self.assertIn(f"commit {head[:12]} (author)", text)

    def test_a_malformed_list_refuses_with_exit_two(self):
        declare(self.repo, {"allowedEmails": []})
        code, out = run(["identity", "--staged", "--root", self.repo])
        self.assertEqual((code, out["code"]), (2, "identity-allowlist-invalid"))
        code, out = run(["leak", "--staged", "--generic-only", "--root", self.repo])
        self.assertEqual((code, out["code"]), (2, "identity-allowlist-invalid"))

    def test_identity_needs_a_hook_mode(self):
        self.assertEqual(run(["identity", "--root", self.repo])[1]["code"], "identity-mode-missing")
        self.assertEqual(run(["identity", "--all", "--root", self.repo])[1]["code"],
                         "identity-mode-invalid")

    def test_leak_adds_the_identity_findings(self):
        declare(self.repo, {"allowedEmails": ALLOWED})
        git(self.repo, "config", "user.email", OUTSIDE)
        code, out = run(["leak", "--staged", "--generic-only", "--root", self.repo])
        self.assertEqual(code, 1)
        self.assertEqual({f["label"] for f in out["findings"]}, {"email-not-allowed"})


if __name__ == "__main__":
    unittest.main()
