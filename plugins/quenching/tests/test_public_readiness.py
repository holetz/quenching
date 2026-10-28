"""Executable proofs for the read-only pre-publication readiness assessment.

Every scanner here is a fake on a PATH that holds nothing else but git, so no installed tool is
ever reached and no credential is ever verified. The sentinel is what a leak would look like: it
must never reach any output path.
"""
from __future__ import annotations

import io
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tarfile
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


def identity(email: str = "dev@users.noreply.github.com") -> dict:
    """A committer identity in the env, since a CI runner has no user.name/user.email configured."""
    return dict(os.environ, GIT_AUTHOR_NAME="Dev", GIT_AUTHOR_EMAIL=email,
                GIT_COMMITTER_NAME="Dev", GIT_COMMITTER_EMAIL=email)


def commit(root: str, path: str, content: bytes | str, message: str = "c",
           email: str = "dev@users.noreply.github.com") -> str:
    target = pathlib.Path(root, path)
    target.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(content, str):
        target.write_text(content, encoding="utf-8")
    else:
        target.write_bytes(content)
    git(root, "add", "--", path)
    git(root, "commit", "-q", "-m", message, env=identity(email))
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


class AdversarialTest(ReadinessCase):
    """Scanners that misbehave, history that hides things, and evidence nobody settled."""

    def gitleaks(self, rows: list[dict], **env: str) -> tuple[dict, int]:
        self.install("gitleaks")
        with mock.patch.dict(os.environ, {"FAKE_GITLEAKS_ROWS": json.dumps(rows), **env}):
            return self.assess()

    def test_a_secret_removed_from_the_tree_still_blocks_from_history(self):
        sha = commit(self.root, "deploy/key.pem", f"{SENTINEL}\n")
        git(self.root, "rm", "-q", "deploy/key.pem")
        git(self.root, "commit", "-q", "-m", "remove", env=identity())
        payload, _ = self.gitleaks([{"File": "deploy/key.pem", "Commit": sha, "Secret": SENTINEL}])
        [blocker] = payload["blockers"]
        self.assertEqual((sha, "deploy/key.pem"), (blocker["commit"], blocker["location"]))
        self.assertNotIn("deploy/key.pem", git(self.root, "ls-files"))

    def test_a_current_tree_secret_in_a_secret_like_path_is_opaque(self):
        name = f"keys/{SENTINEL}.txt"
        sha = commit(self.root, name, "x\n")
        payload, _ = self.gitleaks([{"File": name, "Commit": sha}, {"File": "a.txt", "Commit": SENTINEL}])
        first, second = payload["blockers"]
        self.assertTrue(first["location"].startswith("opaque:"))
        self.assertNotIn("commit", second, "an invalid commit hash is dropped, not echoed")

    def test_a_failing_scanner_falls_through_to_the_next_supported_one(self):
        sha = commit(self.root, "a.txt", "x\n")
        self.install("gitleaks", "trufflehog")
        rows = [{"SourceMetadata": {"Data": {"Git": {"file": "a.txt", "commit": sha}}}, "Raw": SENTINEL}]
        with mock.patch.dict(os.environ, {"FAKE_GITLEAKS_MODE": "fail", "FAKE_TRUFFLEHOG_ROWS": json.dumps(rows)}):
            payload, _ = self.assess()
        states = {row["name"]: (row["state"], row["code"]) for row in payload["scanners"]}
        self.assertEqual(("failed", "pr-scanner-failed"), states["gitleaks"])
        self.assertEqual(("used", None), states["trufflehog"])
        self.assertEqual("trufflehog", self.coverage(payload)["secrets"]["scanner"])
        self.assertEqual(sha, payload["blockers"][0]["commit"])

    def test_scanner_failures_leave_secrets_unmeasured(self):
        commit(self.root, "a.txt", "x\n")
        cases = {"fail": "pr-scanner-failed", "malformed": "pr-scanner-malformed", "sleep": "pr-scanner-timeout"}
        self.install("gitleaks")
        for mode, code in cases.items():
            with self.subTest(mode=mode), mock.patch.dict(os.environ, {"FAKE_GITLEAKS_MODE": mode}):
                payload, exit_code = self.assess(timeout=1)
                self.assertEqual(2, exit_code)
                self.assertEqual("not-measured", self.coverage(payload)["secrets"]["state"])
                self.assertEqual(code, payload["scanners"][0]["code"])

    def test_malformed_trufflehog_and_reuse_payloads_never_read_clean(self):
        commit(self.root, "a.txt", "x\n")
        self.install("trufflehog", "reuse")
        with mock.patch.dict(os.environ, {"FAKE_TRUFFLEHOG_MODE": "malformed", "FAKE_REUSE_MODE": "malformed"}):
            payload, code = self.assess()
        self.assertEqual(2, code)
        cover = self.coverage(payload)
        self.assertEqual("not-measured", cover["secrets"]["state"])
        self.assertEqual("pr-scanner-malformed", cover["attribution"]["code"])

    def test_unsupported_or_unknown_versions_are_refused_without_running(self):
        commit(self.root, "a.txt", "x\n")
        self.install("gitleaks", "trufflehog", "reuse")
        env = {"FAKE_GITLEAKS_VERSION": "8.10.0", "FAKE_TRUFFLEHOG_VERSION": "trufflehog dev",
               "FAKE_REUSE_VERSION": "reuse 1.1.0", "FAKE_GITLEAKS_MODE": "fail"}
        with mock.patch.dict(os.environ, env):
            payload, code = self.assess()
        self.assertEqual(2, code)
        self.assertEqual({"gitleaks": "pr-scanner-unsupported", "trufflehog": "pr-scanner-version-unknown",
                          "reuse": "pr-scanner-unsupported"},
                         {row["name"]: row["code"] for row in payload["scanners"]})
        self.assertEqual({"refused"}, {row["state"] for row in payload["scanners"]})

    def test_branches_and_tags_are_the_declared_history_scope(self):
        sha = commit(self.root, "a.txt", "x\n")
        git(self.root, "branch", "feature")
        git(self.root, "tag", "v1")
        payload, _ = self.assess()
        self.assertEqual({("refs/heads/feature", sha), ("refs/heads/main", sha), ("refs/tags/v1", sha)},
                         {(row["ref"], row["commit"]) for row in payload["scope"]["refs"]})

    def test_a_shallow_clone_is_partial_and_keeps_its_findings(self):
        commit(self.root, "a.txt", "x\n")
        sha = commit(self.root, "b.txt", "y\n")
        clone = os.path.join(self.tmp.name, "shallow")
        git(self.tmp.name, "clone", "-q", "--depth", "1", "file://" + self.root, clone)
        self.root = clone
        payload, code = self.gitleaks([{"File": "b.txt", "Commit": sha}])
        self.assertEqual(2, code)
        self.assertTrue(payload["scope"]["shallow"])
        self.assertFalse(payload["scope"]["historyComplete"])
        self.assertEqual(("partial", "pr-history-incomplete"),
                         (self.coverage(payload)["secrets"]["state"], self.coverage(payload)["secrets"]["code"]))
        self.assertEqual(1, len(payload["blockers"]))

    def test_large_generated_and_binary_files_are_warnings_only_where_text(self):
        commit(self.root, "assets/blob.bin", b"\x00\x01 10.0.0.1 " * 4)
        commit(self.root, "dist/app.js", "x\n")
        commit(self.root, "lib/app.min.js", "x\n")
        with mock.patch("quenching.opensource.readiness.LARGE_BYTES", 32):
            payload, _ = self.assess()
        codes = {(row["code"], row["location"]) for row in payload["warnings"]}
        self.assertIn(("pr-large-file", "assets/blob.bin"), codes)
        self.assertIn(("pr-generated-artifact", "dist/app.js"), codes)
        self.assertIn(("pr-generated-artifact", "lib/app.min.js"), codes)
        self.assertNotIn("pr-internal-identifier", {row["code"] for row in payload["warnings"]})

    def test_internal_identifiers_in_files_and_commit_metadata(self):
        commit(self.root, "conf/db.yml", "host: db.corp\nreplica: 192.168.1.20\n", email="ana@acme.example")
        commit(self.root, "README.md", "version 10.0.0.1.2 is not an address\n")
        payload, _ = self.assess()
        warnings = {row["code"]: row for row in payload["warnings"]}
        self.assertEqual("conf/db.yml", warnings["pr-internal-identifier"]["location"])
        self.assertEqual(1, warnings["pr-identity-in-metadata"]["addresses"])
        self.assertNotIn("acme", json.dumps(payload))

    def test_missing_attribution_counts_tracked_files_only(self):
        commit(self.root, "src/a.py", "x = 1\n")
        pathlib.Path(self.root, "scratch.py").write_text("y\n", encoding="utf-8")
        self.install("reuse")
        reuse = {"non_compliant": {"missing_licensing_info": ["src/a.py", "scratch.py"],
                                   "missing_copyright_info": ["src/a.py"], "missing_licenses": {"MIT": ["src/a.py"]}},
                 "summary": {"compliant": False}}
        with mock.patch.dict(os.environ, {"FAKE_REUSE_ROWS": json.dumps(reuse)}):
            payload, _ = self.assess()
        attribution = [(r["code"], r.get("location")) for r in payload["blockers"] if r["class"] == "attribution"]
        self.assertEqual([("pr-attribution-missing", "src/a.py"), ("pr-license-text-missing", None)], attribution)
        self.assertEqual(1, payload["scope"]["untracked"])
        self.assertFalse(payload["scope"]["untrackedScanned"])

    def test_incompatible_licenses_block_while_unknown_ones_stay_unmeasured(self):
        commit(self.root, "a.txt", "x\n")
        cases = [({"state": "incompatible", "reviewedBy": "Reviewer Ana"}, "measured", ["pr-license-incompatible"]),
                 ({"state": "unknown", "reviewedBy": "Reviewer Ana"}, "pr-evidence-ambiguous", []),
                 ({"state": "compatible", "reviewedBy": " "}, "pr-evidence-unreviewed", [])]
        for entry, expected, blockers in cases:
            with self.subTest(entry=entry):
                payload, _ = self.assess(evidence=self.evidence(licenses=entry))
                cover = self.coverage(payload)["dependency-license"]
                self.assertEqual(expected, cover["state"] if cover["state"] == "measured" else cover["code"])
                self.assertEqual(blockers, [r["code"] for r in payload["blockers"]])
                self.assertNotIn("Reviewer Ana", json.dumps(payload))

    def test_unknown_or_withheld_consent_never_reads_as_granted(self):
        commit(self.root, "a.txt", "x\n")
        payload, _ = self.assess(evidence=self.evidence(consent={"state": "withheld", "reviewedBy": "owner"}))
        self.assertEqual(["pr-consent-withheld"], [r["code"] for r in payload["blockers"]])
        payload, _ = self.assess(evidence=self.evidence())
        self.assertEqual("pr-evidence-absent", self.coverage(payload)["history-consent"]["code"])
        unreadable = os.path.join(self.tmp.name, "broken.json")
        pathlib.Path(unreadable).write_text(f"{{{SENTINEL}", encoding="utf-8")
        payload, _ = self.assess(evidence=unreadable)
        self.assertEqual("pr-evidence-unreadable", self.coverage(payload)["history-consent"]["code"])

    def test_a_scratch_directory_inside_the_target_refuses_the_scanner(self):
        commit(self.root, "a.txt", "x\n")
        self.install("gitleaks")
        with mock.patch.object(tempfile, "tempdir", self.root):
            payload, _ = self.assess()
        self.assertEqual("pr-scratch-inside-target", payload["scanners"][0]["code"])

    def test_the_cli_never_prints_the_sentinel_on_any_stream(self):
        sha = commit(self.root, f"k/{SENTINEL}", "x\n")
        self.install("gitleaks", "reuse")
        rows = [{"File": f"k/{SENTINEL}", "Commit": sha, "Secret": SENTINEL}]
        env = dict(os.environ, FAKE_GITLEAKS_ROWS=json.dumps(rows), FAKE_REUSE_MODE="malformed")
        cq = pathlib.Path(__file__).resolve().parent.parent / "assets" / "bin" / "cq"
        for extra in ([], ["--json"]):
            run = subprocess.run([sys.executable, str(cq), "--root", self.root, "opensource", "readiness", *extra],
                                 capture_output=True, text=True, env=env)
            with self.subTest(extra=extra):
                self.assertEqual(2, run.returncode, run.stderr)
                self.assertNotIn(SENTINEL, run.stdout + run.stderr)
                self.assertNotIn(self.tmp.name, run.stdout + run.stderr)


REPO = pathlib.Path(__file__).resolve().parents[3]


class CleanCloneTest(ReadinessCase):
    """The published quenching-opensource module, exported from the committed tree, runs the flow."""

    def export(self) -> pathlib.Path:
        if subprocess.run(["git", "-C", str(REPO), "rev-parse", "--verify", "-q", "HEAD"],
                          capture_output=True).returncode != 0:
            self.skipTest("the repository is not a git checkout")
        target = pathlib.Path(self.tmp.name, "export")
        target.mkdir()
        archive = subprocess.run(["git", "-C", str(REPO), "archive", "HEAD", "plugins/claude/quenching-opensource"],
                                 check=True, capture_output=True).stdout
        with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
            tar.extractall(target, filter="data")
        return target / "plugins" / "claude" / "quenching-opensource"

    def test_the_module_carries_the_command_and_the_reference_it_cites(self):
        module = self.export()
        command = (module / "commands" / "opensource" / "readiness.md").read_text(encoding="utf-8")
        self.assertIn("cq --root \"$TARGET_ROOT\" opensource readiness --json", command)
        self.assertIn("${CLAUDE_PLUGIN_ROOT}/assets/references/opensource-readiness/report.md", command)
        self.assertTrue((module / "assets" / "references" / "opensource-readiness" / "report.md").is_file())

    def test_the_module_route_measures_a_clean_fixture_end_to_end(self):
        module = self.export()
        commit(self.root, "README.md", "hello\n")
        self.install("gitleaks", "reuse")
        evidence = self.evidence({"state": "compatible", "reviewedBy": "owner"},
                                 {"state": "granted", "reviewedBy": "owner"})
        env = dict(os.environ, FAKE_REUSE_ROWS=json.dumps({"non_compliant": {}}))
        before = snapshot(self.root)
        run = subprocess.run([sys.executable, str(module / "assets" / "bin" / "cq"), "--root", self.root,
                              "opensource", "readiness", "--json", "--evidence", evidence],
                             capture_output=True, text=True, env=env)
        self.assertEqual(before, snapshot(self.root))
        self.assertEqual(0, run.returncode, run.stdout + run.stderr)
        payload = json.loads(run.stdout)
        self.assertEqual({"measured"}, {row["state"] for row in payload["coverage"]})
        self.assertFalse(payload["grantsPublication"])


if __name__ == "__main__":
    unittest.main()
