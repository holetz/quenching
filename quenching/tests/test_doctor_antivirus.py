"""`cq doctor --antivirus`: what it lists, how it prints it, and that it applies nothing."""

import contextlib
import io
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

import _paths  # noqa: F401  — must precede the `quenching` import; see its docstring
from quenching.common import doctor

CQ = pathlib.Path(__file__).resolve().parents[1] / "assets" / "bin" / "cq"


def _which(found: dict):
    return lambda name: found.get(name)


class AntivirusReportTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.repo = os.path.join(self.tmp, "proj")
        subprocess.run(["git", "init", "-q", self.repo], check=True)
        os.makedirs(os.path.join(self.repo, ".venv"))
        os.makedirs(os.path.join(self.tmp, "proj-slot-1"))
        self.env = mock.patch.dict(os.environ, {"XDG_CACHE_HOME": os.path.join(self.tmp, "c")})
        self.env.start()
        self.addCleanup(self.env.stop)

    def report(self, found=None):
        with mock.patch.object(doctor.subprocess, "run", wraps=subprocess.run) as spawn:
            report = doctor.antivirus_report(self.repo, which=_which(found or {}))
        return report, spawn

    def test_lists_the_repository_slots_cache_and_venv(self):
        report, _ = self.report()
        paths = [p["path"] for p in report["paths"]]
        root = os.path.realpath(self.repo)
        self.assertEqual(root, os.path.realpath(report["root"]))
        self.assertIn(os.path.join(os.path.dirname(report["root"]), "proj-slot-*"), paths)
        self.assertIn(os.path.join(os.path.dirname(report["root"]), "proj-slot-1"), paths)
        self.assertIn(os.path.join(self.tmp, "c", "quenching"), paths)
        self.assertIn(os.path.join(report["root"], ".venv"), paths)
        self.assertEqual(os.path.abspath(sys.executable), report["processes"][0]["path"])

    def test_no_uv_means_no_spawn_beyond_git(self):
        _, spawn = self.report()
        self.assertFalse(any(call.args[0][1:3] == ["cache", "dir"] for call in spawn.call_args_list))

    def test_uv_cache_dir_is_listed_when_uv_answers(self):
        done = subprocess.CompletedProcess(["uv"], 0, stdout="/u/cache\n", stderr="")
        with mock.patch.object(doctor.subprocess, "run", return_value=done) as spawn:
            path = doctor._uv_cache_dir(_which({"uv": "/bin/uv"}))
        self.assertEqual("/u/cache", path)
        self.assertEqual(["/bin/uv", "cache", "dir"], spawn.call_args.args[0])

    def test_system_temp_is_informational_never_a_command(self):
        report, _ = self.report()
        human = doctor._antivirus_human(report)
        temp = tempfile.gettempdir()
        self.assertNotIn(f"-ExclusionPath '{temp}'", human)
        self.assertEqual(temp, report["informational"][0]["path"])

    def test_human_output_prints_defender_commands_plain_list_and_caveat(self):
        report, _ = self.report({"git": "/usr/bin/git"})
        human = doctor._antivirus_human(report)
        self.assertIn(f"Add-MpPreference -ExclusionPath '{report['root']}'", human)
        self.assertIn("Add-MpPreference -ExclusionProcess '/usr/bin/git'", human)
        self.assertIn("Plain list", human)
        self.assertIn("Tamper Protection", human)
        self.assertIn("Nothing here is applied", human)

    def test_single_quotes_are_escaped_for_powershell(self):
        self.assertEqual("'C:\\it''s'", doctor._ps_quote("C:\\it's"))


class AntivirusPrimaryRootTest(unittest.TestCase):
    """The repository is the primary worktree, never the folder holding a separate git dir."""

    def setUp(self):
        self.tmp = os.path.realpath(tempfile.mkdtemp())
        self.env = mock.patch.dict(os.environ, {"XDG_CACHE_HOME": os.path.join(self.tmp, "c")})
        self.env.start()
        self.addCleanup(self.env.stop)

    def _git(self, *argv):
        subprocess.run(["git", *argv], check=True, capture_output=True)

    def _repo(self, *init):
        repo = os.path.join(self.tmp, "sep")
        self._git("init", "-q", *init, repo)
        self._git("-C", repo, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q",
                  "--allow-empty", "-m", "x")
        with open(os.path.join(repo, "README.md"), "w", encoding="utf-8") as fh:
            fh.write("x\n")
        self._git("-C", repo, "add", "README.md")
        self._git("-C", repo, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "y")
        slot = os.path.join(self.tmp, "sep-slot-1")
        self._git("-C", repo, "worktree", "add", "-q", slot)
        return repo, slot

    def _paths(self, root):
        report = doctor.antivirus_report(root, which=_which({}))
        return report, [p["path"] for p in report["paths"]]

    def test_separate_git_dir_lists_the_worktree_never_the_git_dir_parent(self):
        gd = os.path.join(self.tmp, "gd")
        os.makedirs(gd)
        repo, slot = self._repo("--separate-git-dir", os.path.join(gd, ".git"))
        for root in (repo, slot):
            report, paths = self._paths(root)
            self.assertEqual(repo, report["root"], root)
            self.assertIn(os.path.join(self.tmp, "sep-slot-*"), paths)
            self.assertNotIn(gd, paths)
            self.assertNotIn(os.path.join(self.tmp, "gd-slot-*"), paths)
            self.assertIn(os.path.join(gd, ".git"), [p["path"] for p in report["informational"]])

    def test_a_slot_of_a_plain_repository_lists_the_primary_worktree(self):
        repo, slot = self._repo()
        report, paths = self._paths(slot)
        self.assertEqual(repo, report["root"])
        self.assertIn(slot, paths)
        self.assertNotIn(os.path.join(repo, ".git"), [p["path"] for p in report["informational"]])

    def test_a_stale_stat_in_the_primary_still_proves_it_and_rewrites_no_index(self):
        repo, slot = self._repo()
        os.utime(os.path.join(repo, "README.md"), (1, 1))
        index = os.path.join(repo, ".git", "index")
        before = pathlib.Path(index).read_bytes()
        report, _ = self._paths(slot)
        self.assertEqual(repo, report["root"])
        self.assertEqual(before, pathlib.Path(index).read_bytes())

    def test_a_slot_that_cannot_prove_its_primary_falls_back_to_itself(self):
        gd = os.path.join(self.tmp, "gd")
        os.makedirs(gd)
        repo, _ = self._repo("--separate-git-dir", os.path.join(gd, ".git"))
        odd = os.path.join(self.tmp, "elsewhere")
        self._git("-C", repo, "worktree", "add", "-q", odd)
        report, paths = self._paths(odd)
        self.assertEqual(odd, report["root"])
        self.assertNotIn(gd, paths)

    def _separate(self, name, *, tracked):
        """`name` checked out with its git dir in `gd<name>/.git`; `tracked` is committed."""
        gd = os.path.join(self.tmp, f"gd{name}")
        repo = os.path.join(self.tmp, name)
        os.makedirs(gd)
        self._git("init", "-q", "--separate-git-dir", os.path.join(gd, ".git"), repo)
        for rel in tracked:
            os.makedirs(os.path.dirname(os.path.join(repo, rel)) or repo, exist_ok=True)
            with open(os.path.join(repo, rel), "w", encoding="utf-8") as fh:
                fh.write("x\n")
            self._git("-C", repo, "add", rel)
        self._git("-C", repo, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q",
                  "--allow-empty", "-m", "x")
        return gd, repo

    def _assert_never_the_git_dir_parent(self, root, gd):
        report, paths = self._paths(root)
        self.assertEqual(root, report["root"])
        self.assertNotIn(gd, paths)
        self.assertNotIn(f"{gd}-slot-*", paths)

    def test_a_same_named_unrelated_file_is_no_proof(self):
        gd, repo = self._separate("A", tracked=["README.md"])
        with open(os.path.join(gd, "README.md"), "w", encoding="utf-8") as fh:
            fh.write("unrelated\n")
        odd = os.path.join(self.tmp, "elsewhereA")
        self._git("-C", repo, "worktree", "add", "-q", odd)
        self._assert_never_the_git_dir_parent(odd, gd)

    def test_a_same_named_directory_is_no_proof_once_the_primary_is_gone(self):
        gd, repo = self._separate("C", tracked=[os.path.join("src", "a")])
        os.makedirs(os.path.join(gd, "src"))
        slot = os.path.join(self.tmp, "C-slot-1")
        self._git("-C", repo, "worktree", "add", "-q", slot)
        shutil.rmtree(repo)
        self._assert_never_the_git_dir_parent(slot, gd)

    def test_nothing_tracked_is_no_proof(self):
        gd, repo = self._separate("B", tracked=[])
        slot = os.path.join(self.tmp, "B-slot-1")
        self._git("-C", repo, "worktree", "add", "-q", slot)
        shutil.rmtree(repo)
        self._assert_never_the_git_dir_parent(slot, gd)


class AntivirusBroadPathTest(unittest.TestCase):
    def test_disk_root_home_ancestor_and_temp_are_too_broad(self):
        home = os.path.expanduser("~")
        for path in (os.path.abspath(os.sep), home, os.path.dirname(home),
                     tempfile.gettempdir()):
            self.assertTrue(doctor._too_broad(path), path)

    def test_a_folder_inside_home_or_temp_is_not_too_broad(self):
        for path in (os.path.join(os.path.expanduser("~"), "proj"),
                     os.path.join(tempfile.gettempdir(), "proj")):
            self.assertFalse(doctor._too_broad(path), path)

    def test_outside_a_repository_the_report_is_a_refusal(self):
        outside = tempfile.mkdtemp()
        report = doctor.antivirus_report(outside, which=_which({}))
        self.assertEqual("cq-antivirus-no-repo", report["refusal"]["code"])
        self.assertNotIn("paths", report)

    def test_a_repository_at_the_home_is_refused(self):
        home = os.path.realpath(os.path.expanduser("~"))
        with mock.patch.object(doctor, "_primary_root", return_value=home):
            report = doctor.antivirus_report(home, which=_which({}))
        self.assertEqual("cq-antivirus-unsafe-root", report["refusal"]["code"])

    def test_a_broad_cache_moves_to_not_listed(self):
        tmp = tempfile.mkdtemp()
        repo = os.path.join(tmp, "proj")
        subprocess.run(["git", "init", "-q", repo], check=True)
        home = os.path.expanduser("~")
        with mock.patch.object(doctor, "cache_root", return_value=home):
            report = doctor.antivirus_report(repo, which=_which({}))
        self.assertNotIn(home, [p["path"] for p in report["paths"]])
        self.assertIn(home, [p["path"] for p in report["informational"]])
        self.assertNotIn(f"-ExclusionPath '{home}'", doctor._antivirus_human(report))


class AntivirusCliTest(unittest.TestCase):
    def _cq(self, root):
        return subprocess.run([sys.executable, str(CQ), "doctor", "--antivirus", "--root", root],
                              capture_output=True, text=True, timeout=120)

    def test_disk_root_and_home_are_refused_without_a_command(self):
        for root in (os.path.abspath(os.sep), os.path.expanduser("~"), tempfile.mkdtemp()):
            if subprocess.run(["git", "-C", root, "rev-parse"], capture_output=True).returncode == 0:
                continue
            out = self._cq(root)
            self.assertEqual(2, out.returncode, (root, out.stdout, out.stderr))
            self.assertNotIn("Add-MpPreference", out.stdout + out.stderr)
            self.assertIn("not inside a git repository", out.stderr)

    def test_json_carries_paths_processes_and_caveat(self):
        out = subprocess.run([sys.executable, str(CQ), "doctor", "--antivirus", "--json"],
                             capture_output=True, text=True, timeout=120,
                             cwd=str(CQ.parents[3]))
        self.assertEqual(0, out.returncode, out.stderr)
        payload = json.loads(out.stdout)
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["paths"] and payload["processes"] and payload["caveat"])

    def test_write_with_antivirus_is_refused(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(io.StringIO()):
            code = doctor.run(True, tempfile.mkdtemp(), antivirus=True, write=True)
        self.assertEqual(2, code)


if __name__ == "__main__":
    unittest.main()
