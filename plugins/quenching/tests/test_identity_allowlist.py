"""Executable proofs for the identity allowlist (`quenching.common.identity`)."""
from __future__ import annotations

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
from quenching.common import identity
from test_leak_scan import git, init_repo

ALLOWED = ["dev@example.org", "*@users.noreply.github.com"]
OUTSIDE = "someone@corp.example"


def declare(root: str, value) -> None:
    path = pathlib.Path(root, ".agents", "quenching.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    document = {"backend": "git", "shared": {}}
    if value is not ...:
        document["shared"]["gitIdentity"] = value
    path.write_text(json.dumps(document), encoding="utf-8")


class IdentityRepo(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        clean_env = {k: v for k, v in os.environ.items()
                     if not k.startswith(("GIT_AUTHOR_", "GIT_COMMITTER_"))}
        clean_env["QUENCHING_USER_CONFIG"] = os.path.join(self._tmp.name, "no-user-layer.json")
        patcher = mock.patch.dict(os.environ, clean_env, clear=True)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.repo = str(pathlib.Path(self._tmp.name, "repo"))
        os.mkdir(self.repo)
        init_repo(self.repo)


class Declaration(IdentityRepo):
    def test_absent_declares_nothing(self):
        self.assertIsNone(identity.load_allowlist(self.repo))
        declare(self.repo, ...)
        self.assertIsNone(identity.load_allowlist(self.repo))
        declare(self.repo, {})
        self.assertIsNone(identity.load_allowlist(self.repo))

    def test_a_list_is_read_and_trimmed(self):
        declare(self.repo, {"allowedEmails": [" dev@example.org ", "*@x.org"]})
        self.assertEqual(identity.load_allowlist(self.repo), ["dev@example.org", "*@x.org"])

    def test_malformed_shapes_fail_closed(self):
        for value in ([], "dev@example.org", ["ok@x.org", ""], ["ok@x.org", 3], None):
            declare(self.repo, {"allowedEmails": value})
            with self.subTest(value=value), self.assertRaises(identity.AllowlistInvalid):
                identity.load_allowlist(self.repo)
        declare(self.repo, ["dev@example.org"])
        with self.assertRaises(identity.AllowlistInvalid):
            identity.load_allowlist(self.repo)


class Matching(unittest.TestCase):
    def test_exact_glob_and_case(self):
        self.assertTrue(identity.allowed("dev@example.org", ALLOWED))
        self.assertTrue(identity.allowed("Dev@Example.ORG", ALLOWED))
        self.assertTrue(identity.allowed("1+bot@users.noreply.github.com", ALLOWED))
        self.assertFalse(identity.allowed(OUTSIDE, ALLOWED))
        self.assertFalse(identity.allowed("dev@example.org.evil", ALLOWED))
        self.assertFalse(identity.allowed("", ALLOWED))


class Staged(IdentityRepo):
    def test_the_configured_identity_inside_the_list_is_clean(self):
        self.assertEqual(identity.staged_findings(self.repo, ALLOWED), [])

    def test_an_identity_outside_the_list_is_found_and_named(self):
        git(self.repo, "config", "user.email", OUTSIDE)
        found = identity.staged_findings(self.repo, ALLOWED)
        self.assertEqual([(f.where, f.label, f.excerpt) for f in found], [
            ("git var GIT_AUTHOR_IDENT", "email-not-allowed", OUTSIDE),
            ("git var GIT_COMMITTER_IDENT", "email-not-allowed", OUTSIDE)])

    def test_the_author_override_git_exports_is_judged(self):
        with mock.patch.dict(os.environ, {"GIT_AUTHOR_EMAIL": OUTSIDE}):
            found = identity.staged_findings(self.repo, ALLOWED)
        self.assertEqual([f.where for f in found], ["git var GIT_AUTHOR_IDENT"])


class Push(IdentityRepo):
    def commit(self, name: str, **env: str) -> str:
        pathlib.Path(self.repo, name).write_text(name + "\n", encoding="utf-8")
        git(self.repo, "add", name)
        with mock.patch.dict(os.environ, env):
            git(self.repo, "commit", "-q", "-m", name)
        return git(self.repo, "rev-parse", "HEAD").strip()

    def test_author_and_committer_of_each_published_commit_are_judged(self):
        base = self.commit("a.txt")
        self.commit("b.txt", GIT_AUTHOR_EMAIL=OUTSIDE)
        head = self.commit("c.txt", GIT_COMMITTER_EMAIL=OUTSIDE)
        line = f"refs/heads/main {head} refs/heads/main {base}\n"
        found = identity.push_findings(self.repo, line, ALLOWED)
        self.assertEqual(sorted(f.where.split(" (")[1] for f in found), ["author)", "committer)"])
        self.assertTrue(all(f.excerpt == OUTSIDE for f in found))

    def test_a_clean_push_and_a_deletion_have_no_findings(self):
        base = self.commit("a.txt")
        head = self.commit("b.txt")
        self.assertEqual(identity.push_findings(
            self.repo, f"refs/heads/main {head} refs/heads/main {base}\n", ALLOWED), [])
        self.assertEqual(identity.push_findings(
            self.repo, f"(delete) {'0' * 40} refs/heads/x {base}\n", ALLOWED), [])


if __name__ == "__main__":
    unittest.main()
