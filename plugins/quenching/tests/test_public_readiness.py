"""Executable proofs for the read-only pre-publication readiness assessment.

Every scanner here is a fake on a PATH that holds nothing else but git, so no installed tool is
ever reached and no credential is ever verified. The sentinel is what a leak would look like: it
must never reach any output path.
"""
from __future__ import annotations

import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

try:
    import _paths  # noqa: F401 — must precede the `quenching` import
except ModuleNotFoundError:  # package-qualified unittest invocation from the repository root
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    import _paths  # noqa: F401
from quenching.opensource.readiness import CLASSES, assess, location

SENTINEL = "QCKSENTINELAKIA9Z8Y7X6W5V4U3T2S1"
FAKE = r'''#!{python}
import json, os, sys, time
name = os.path.basename(sys.argv[0])
mode = os.environ.get("FAKE_%s_MODE" % name.upper(), "ok")
sys.stderr.write("leaked {sentinel}\n")
if len(sys.argv) > 1 and sys.argv[1] in ("version", "--version"):
    print(os.environ.get("FAKE_%s_VERSION" % name.upper(), {versions}[name]))
    sys.exit(0)
if mode == "sleep":
    time.sleep(10)
if mode == "fail":
    print("error {sentinel}")
    sys.exit(3)
rows = json.loads(os.environ.get("FAKE_%s_ROWS" % name.upper(), "[]"))
if name == "gitleaks":
    path = sys.argv[sys.argv.index("--report-path") + 1]
    with open(path, "w") as handle:
        handle.write("not json {sentinel}" if mode == "malformed" else json.dumps(rows))
elif name == "trufflehog":
    if mode == "malformed":
        print("{{{sentinel}")
    for row in rows:
        print(json.dumps(row))
else:
    if mode == "malformed":
        print("[{sentinel}")
    else:
        print(json.dumps(rows))
        sys.exit(1 if isinstance(rows, dict) and rows.get("non_compliant", {{}}).get("missing_licensing_info") else 0)
'''
VERSIONS = {"gitleaks": "8.21.2", "trufflehog": "trufflehog 3.82.6", "reuse": "reuse 5.0.2"}


def git(root: str, *argv: str, env: dict | None = None) -> str:
    return subprocess.run(["git", *argv], cwd=root, check=True, capture_output=True, text=True,
                          env=env).stdout


def commit(root: str, path: str, content: bytes | str, message: str = "c",
           email: str = "dev@users.noreply.github.com") -> str:
    target = pathlib.Path(root, path)
    target.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(content, str):
        target.write_text(content, encoding="utf-8")
    else:
        target.write_bytes(content)
    env = dict(os.environ, GIT_AUTHOR_NAME="Dev", GIT_AUTHOR_EMAIL=email,
               GIT_COMMITTER_NAME="Dev", GIT_COMMITTER_EMAIL=email)
    git(root, "add", "--", path)
    git(root, "commit", "-q", "-m", message, env=env)
    return git(root, "rev-parse", "HEAD").strip()


def snapshot(root: str) -> tuple[str, str, str]:
    """Tracked/untracked/ignored status, every ref and the object inventory."""
    return (git(root, "status", "--porcelain", "--ignored", "--untracked-files=all"),
            git(root, "for-each-ref", "--format=%(refname) %(objectname)"),
            git(root, "count-objects", "-v"))


class ReadinessCase(unittest.TestCase):
    """A disposable repository and a PATH holding only git and the scanners a test installs."""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = os.path.join(self.tmp.name, "repo")
        self.bin = os.path.join(self.tmp.name, "bin")
        os.makedirs(self.root)
        os.makedirs(self.bin)
        os.symlink(shutil.which("git"), os.path.join(self.bin, "git"))
        git(self.root, "init", "-q", "-b", "main")
        self.env = mock.patch.dict(os.environ, {"PATH": self.bin})
        self.env.start()

    def tearDown(self) -> None:
        self.env.stop()
        self.tmp.cleanup()

    def install(self, *names: str) -> None:
        for name in names:
            path = os.path.join(self.bin, name)
            pathlib.Path(path).write_text(
                FAKE.format(python=sys.executable, sentinel=SENTINEL, versions=json.dumps(VERSIONS)),
                encoding="utf-8")
            os.chmod(path, 0o755)

    def evidence(self, licenses: dict | None = None, consent: dict | None = None) -> str:
        path = os.path.join(self.tmp.name, "evidence.json")
        data = {}
        if licenses is not None:
            data["dependencyLicenses"] = licenses
        if consent is not None:
            data["historyConsent"] = consent
        pathlib.Path(path).write_text(json.dumps(data), encoding="utf-8")
        return path

    def assess(self, **kwargs) -> tuple[dict, int]:
        before = snapshot(self.root)
        payload, code = assess(self.root, **kwargs)
        self.assertEqual(before, snapshot(self.root), "the assessment changed the target")
        self.assertNotIn(SENTINEL, json.dumps(payload))
        self.assertNotIn(self.tmp.name, json.dumps(payload), "an absolute machine path leaked")
        return payload, code

    def coverage(self, payload: dict) -> dict[str, dict]:
        return {row["class"]: row for row in payload["coverage"]}


class EngineTest(ReadinessCase):
    def test_a_directory_outside_git_refuses_every_class(self):
        plain = os.path.join(self.tmp.name, "plain")
        os.makedirs(plain)
        payload, code = assess(plain)
        self.assertEqual(2, code)
        self.assertEqual(list(CLASSES), [row["class"] for row in payload["coverage"]])
        self.assertTrue(all(row["state"] == "refused" for row in payload["coverage"]))

    def test_a_repository_without_commits_is_refused_not_clean(self):
        payload, code = self.assess()
        self.assertEqual(2, code)
        self.assertEqual({"pr-no-commits"}, {row["code"] for row in payload["coverage"]})

    def test_no_scanner_and_no_evidence_leave_categories_unmeasured(self):
        commit(self.root, "README.md", "hello\n")
        payload, code = self.assess()
        self.assertEqual(2, code)
        self.assertFalse(payload["ok"])
        cover = self.coverage(payload)
        self.assertEqual("pr-no-safe-scanner", cover["secrets"]["code"])
        self.assertEqual("not-measured", cover["attribution"]["state"])
        self.assertEqual("pr-evidence-absent", cover["dependency-license"]["code"])
        self.assertEqual("pr-evidence-absent", cover["history-consent"]["code"])
        self.assertEqual({"absent"}, {row["state"] for row in payload["scanners"]})
        self.assertFalse(payload["grantsPublication"])

    def test_a_scanner_finding_is_a_sanitized_blocker(self):
        sha = commit(self.root, "config/app.env", "TOKEN=x\n")
        self.install("gitleaks")
        rows = [{"File": "config/app.env", "Commit": sha, "Secret": SENTINEL, "Match": SENTINEL,
                 "RuleID": SENTINEL, "Email": "dev@example.com"}]
        with mock.patch.dict(os.environ, {"FAKE_GITLEAKS_ROWS": json.dumps(rows)}):
            payload, code = self.assess()
        self.assertEqual(2, code, "attribution and legal evidence are still unmeasured")
        [blocker] = payload["blockers"]
        self.assertEqual({"code": "pr-secret", "class": "secrets", "severity": "blocker",
                          "location": "config/app.env", "commit": sha}, {
            k: blocker[k] for k in ("code", "class", "severity", "location", "commit")})
        self.assertNotIn("dev@example.com", json.dumps(payload))
        self.assertEqual("measured", self.coverage(payload)["secrets"]["state"])

    def test_a_complete_measured_clean_assessment_exits_zero_without_approval(self):
        commit(self.root, "README.md", "hello\n")
        self.install("gitleaks", "reuse")
        reuse = {"non_compliant": {}, "summary": {"compliant": True}}
        evidence = self.evidence({"state": "compatible", "reviewedBy": "owner"},
                                 {"state": "granted", "reviewedBy": "owner"})
        with mock.patch.dict(os.environ, {"FAKE_REUSE_ROWS": json.dumps(reuse)}):
            payload, code = self.assess(evidence=evidence)
        self.assertEqual(0, code, payload["coverage"])
        self.assertTrue(payload["ok"])
        self.assertFalse(payload["grantsPublication"])
        self.assertEqual({"refs/heads/main"}, {row["ref"] for row in payload["scope"]["refs"]})
        self.assertTrue(payload["scope"]["historyComplete"])

    def test_a_location_that_could_carry_a_value_becomes_opaque(self):
        self.assertEqual("src/app.py", location("src/app.py"))
        for unsafe in (f"keys/{SENTINEL}.txt", "/home/user/repo/a.py", "../outside", "a b/c", None, 7):
            self.assertTrue(location(unsafe).startswith("opaque:"), unsafe)


if __name__ == "__main__":
    unittest.main()
