"""Executable proofs for `cq portal` — the project registry. Every test runs under a temp HOME."""
from __future__ import annotations

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

try:
    import _paths  # noqa: F401 — must precede the `quenching` import
except ModuleNotFoundError:  # package-qualified unittest invocation from the repository root
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    import _paths  # noqa: F401
from quenching.portal import main

REAL = pathlib.Path(__file__).resolve().parent.parent / "assets" / "bin" / "cq"


def _git(cwd, *argv):
    subprocess.run(["git", "-C", str(cwd), *argv], check=True, capture_output=True)


class PortalRegistry(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = pathlib.Path(self._tmp.name).resolve()
        self.home = self.tmp / "home"
        self.home.mkdir()
        patch = mock.patch.dict(os.environ, {"HOME": str(self.home)})
        patch.start()
        self.addCleanup(patch.stop)
        self.registry = self.home / ".config" / "quenching" / "projects.json"

    def repo(self, name):
        path = self.tmp / name
        path.mkdir()
        _git(path, "init", "-q")
        return path

    def run_cq(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = main(list(argv))
        return code, out.getvalue(), err.getvalue()

    def projects(self):
        return json.loads(self.registry.read_text())["projects"]

    def test_list_without_a_file_is_empty_and_writes_nothing(self):
        code, out, _ = self.run_cq("list", "--json")
        self.assertEqual(0, code)
        self.assertEqual([], json.loads(out)["projects"])
        self.assertFalse(self.registry.exists())

    def test_add_is_idempotent_and_lands_under_the_temp_home(self):
        repo = self.repo("alpha")
        code, out, _ = self.run_cq("add", str(repo), "--json")
        self.assertEqual(0, code)
        self.assertTrue(json.loads(out)["added"])
        code, out, _ = self.run_cq("add", str(repo), "--json")
        self.assertEqual(0, code)
        self.assertFalse(json.loads(out)["added"])
        self.assertEqual([{"name": "alpha", "path": str(repo)}], self.projects())

    def test_add_from_a_worktree_registers_the_main_root(self):
        repo = self.repo("main")
        _git(repo, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty",
             "-m", "x")
        wt = self.tmp / "wt"
        _git(repo, "worktree", "add", "-q", str(wt), "-b", "side")
        self.assertEqual(0, self.run_cq("add", str(wt / "."))[0])
        self.assertEqual([str(repo)], [p["path"] for p in self.projects()])

    def test_add_refuses_a_folder_outside_git_and_a_taken_name(self):
        plain = self.tmp / "plain"
        plain.mkdir()
        self.assertEqual(2, self.run_cq("add", str(plain), "--json")[0])
        self.assertEqual(0, self.run_cq("add", str(self.repo("a")), "--name", "x")[0])
        self.assertEqual(2, self.run_cq("add", str(self.repo("b")), "--name", "x")[0])

    def test_remove_by_name_and_by_path_and_refusal_when_absent(self):
        a, b = self.repo("a"), self.repo("b")
        self.run_cq("add", str(a))
        self.run_cq("add", str(b))
        self.assertEqual(0, self.run_cq("remove", "a")[0])
        self.assertEqual(0, self.run_cq("remove", str(b))[0])
        self.assertEqual([], self.projects())
        self.assertEqual(2, self.run_cq("remove", "a", "--json")[0])

    def test_corrupt_registry_is_refused_and_not_overwritten(self):
        self.registry.parent.mkdir(parents=True)
        self.registry.write_text("{not json")
        self.assertEqual(2, self.run_cq("add", str(self.repo("a")))[0])
        self.assertEqual("{not json", self.registry.read_text())

    def _orca(self, repos):
        orca = self.tmp / "orca"
        profile = orca / "profiles" / "local-default"
        profile.mkdir(parents=True)
        (profile / "orca-data.json").write_text(json.dumps({
            "schemaVersion": 1, "apiToken": "SECRET-ROOT-TOKEN", "repos": repos}))
        (profile / "orca-data.json.sqlite-export.1.json").write_text(
            json.dumps({"repos": [{"path": str(self.repo("ignored"))}]}))
        return orca

    def test_orca_import_keeps_only_paths_and_names_and_is_one_time(self):
        good = self.repo("good")
        orca = self._orca([
            {"id": "1", "path": str(good), "displayName": "Good One", "token": "SECRET-REPO-TOKEN",
             "hookSettings": {"apiKey": "SECRET-KEY"}},
            {"id": "2", "path": str(self.tmp / "gone"), "displayName": "Gone"},
        ])
        code, out, _ = self.run_cq("add", "--from-orca", str(orca), "--json")
        self.assertEqual(0, code)
        payload = json.loads(out)
        self.assertEqual([{"name": "Good One", "path": str(good)}], payload["added"])
        self.assertEqual(1, len(payload["skipped"]))
        for text in (out, self.registry.read_text()):
            self.assertNotIn("SECRET", text)
        self.assertEqual([{"name": "Good One", "path": str(good)}], self.projects())
        self.assertEqual(2, self.run_cq("add", "--from-orca", str(orca))[0])

    def test_orca_import_refuses_a_missing_dir(self):
        self.assertEqual(2, self.run_cq("add", "--from-orca", str(self.tmp / "nope"))[0])

    def test_dispatcher_routes_portal_under_a_temp_home(self):
        env = dict(os.environ, HOME=str(self.home))
        run = subprocess.run([sys.executable, str(REAL), "portal", "list", "--json"],
                             capture_output=True, text=True, env=env)
        self.assertEqual(0, run.returncode, run.stderr)
        self.assertEqual([], json.loads(run.stdout)["projects"])


if __name__ == "__main__":
    unittest.main()
