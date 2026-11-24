"""`cq doctor --antivirus`: what it lists, how it prints it, and that it applies nothing."""

import contextlib
import io
import json
import os
import pathlib
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


class AntivirusCliTest(unittest.TestCase):
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
