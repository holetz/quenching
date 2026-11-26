"""`cq git worktree adopt` against real throwaway repositories.

The property under test is the one a harness-created worktree brings: the tree exists before
quenching sees it, so adoption may link and prepare it but may never cut, overwrite a path the
worktree already holds, or take a slot. The setup runs once per worktree, proven by a marker in
the worktree's own git dir."""
from __future__ import annotations

import json
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest

import _paths  # noqa: F401  — must precede the `quenching` import; see its docstring

CQ = pathlib.Path(__file__).resolve().parent.parent / "assets" / "bin" / "cq"


def _git(cwd, *args):
    return subprocess.run(["git", "-C", str(cwd), "-c", "user.name=t", "-c", "user.email=t@t",
                           *args], check=True, capture_output=True, text=True).stdout


class AdoptRepo(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.base = pathlib.Path(os.path.realpath(tmp.name))
        self.main = self.base / "repo"
        self.worktree = self.base / "repo.worktrees" / "copilot-x"
        self.remote = self.base / "origin.git"

    def make(self, shared: dict | None = None, detach: bool = False) -> pathlib.Path:
        """A primary checkout with the declared config, plus one linked worktree."""
        _git(self.base, "init", "-q", "--bare", "-b", "main", str(self.remote))
        _git(self.base, "init", "-q", "-b", "main", str(self.main))
        os.makedirs(self.main / ".agents", exist_ok=True)
        (self.main / ".agents" / "quenching.json").write_text(
            json.dumps({"shared": shared or {}}) + "\n", encoding="utf-8")
        with open(self.main / ".gitignore", "w", encoding="utf-8") as stream:
            stream.write(".venv/\nsite/\n")
        _git(self.main, "add", ".agents/quenching.json", ".gitignore")
        _git(self.main, "commit", "-q", "-m", "init")
        _git(self.main, "remote", "add", "origin", str(self.remote))
        _git(self.main, "push", "-q", "origin", "main")
        self.base.mkdir(exist_ok=True)
        (self.base / "repo.worktrees").mkdir(exist_ok=True)
        if detach:
            _git(self.main, "worktree", "add", "-q", "--detach", str(self.worktree))
        else:
            _git(self.main, "worktree", "add", "-q", "-b", "copilot/x", str(self.worktree))
        return self.worktree

    def adopt(self, path, *extra):
        done = subprocess.run([sys.executable, str(CQ), "git", "worktree", "adopt", "--json",
                               "--path", str(path), *extra],
                              capture_output=True, text=True, encoding="utf-8", cwd=str(path))
        try:
            payload = json.loads(done.stdout or "{}")
        except ValueError:
            payload = {}
        return done.returncode, payload, done.stderr


class Refusals(AdoptRepo):
    def test_the_primary_checkout_is_never_adopted(self):
        self.make()
        code, payload, _err = self.adopt(self.main)
        self.assertEqual(2, code)
        self.assertEqual("git-worktree-primary", payload["code"])

    def test_a_quenching_slot_is_never_adopted(self):
        self.make()
        slot = self.base / "repo-slot-1"
        _git(self.main, "worktree", "add", "-q", "-b", "slot-branch", str(slot))
        code, payload, _err = self.adopt(slot)
        self.assertEqual(2, code)
        self.assertEqual("git-worktree-slot", payload["code"])

    def test_a_directory_that_is_not_a_repository_is_refused_before_any_write(self):
        stray = self.base / "stray"
        stray.mkdir()
        code, payload, _err = self.adopt(stray)
        self.assertEqual(2, code)
        self.assertEqual("git-worktree-not-repository", payload["code"])


class Adoption(AdoptRepo):
    def test_shared_paths_and_regenerable_directories_are_linked_without_overwriting(self):
        worktree = self.make({"sharedPaths": ["dados"],
                              "regenerablePaths": [".venv", "site", "ja-existe",
                                                   "nao-existe", "*.tmp"]})
        (self.main / ".venv").mkdir()
        (self.main / "site").mkdir()
        (self.main / "ja-existe").mkdir()
        (worktree / "ja-existe").mkdir()

        code, payload, _err = self.adopt(worktree)

        self.assertEqual(0, code, payload)
        self.assertTrue(payload["adopted"])
        self.assertEqual(str(worktree), payload["worktree"])
        self.assertEqual("copilot/x", payload["branch"])
        self.assertEqual("main", payload["base"])
        self.assertTrue(payload["baseInferred"])

        shared = {item["path"]: item for item in payload["shared"]}
        self.assertIn("dados", shared)
        self.assertTrue(os.path.islink(worktree / "dados"))
        self.assertEqual(os.path.realpath(self.base / "repo.dados"),
                         os.path.realpath(worktree / "dados"))

        states = {item["path"]: item["state"] for item in payload["regenerable"]}
        self.assertEqual("linked", states[".venv"])
        self.assertEqual("linked", states["site"])
        self.assertEqual("present", states["ja-existe"])
        self.assertEqual("absent", states["nao-existe"])
        self.assertEqual("pattern", states["*.tmp"])
        self.assertTrue(os.path.islink(worktree / ".venv"))
        self.assertEqual(os.path.realpath(self.main / ".venv"),
                         os.path.realpath(worktree / ".venv"))
        self.assertFalse(os.path.islink(worktree / "ja-existe"))
        self.assertTrue((worktree / "ja-existe").is_dir())

    def test_a_declared_setup_runs_once_per_worktree(self):
        worktree = self.make({"worktreeSetup": "printf 'ran\\n' >> setup.log"})

        code, first, _err = self.adopt(worktree)

        self.assertEqual(0, code, first)
        self.assertFalse(first["alreadySetup"])
        self.assertTrue(first["setup"]["ok"], first["setup"])
        self.assertEqual(["ran"], (worktree / "setup.log").read_text().split())

        code, second, _err = self.adopt(worktree)

        self.assertEqual(0, code, second)
        self.assertTrue(second["alreadySetup"])
        self.assertIsNone(second["setup"])
        self.assertEqual(["ran"], (worktree / "setup.log").read_text().split())

    def test_the_setup_runs_when_stderr_has_no_descriptor(self):
        """The MCP server runs the verb in-process with stderr in a `StringIO`; the setup must
        still run, and its output still reach that stream."""
        import contextlib
        import io

        from quenching.git import worktree as worktree_module

        path = self.make({"worktreeSetup": "printf 'ran\\n' >> setup.log; echo out; echo err >&2"})
        with contextlib.redirect_stderr(io.StringIO()) as err:
            result = worktree_module._setup(str(path))
        self.assertEqual((True, 0), (result["ok"], result["exit"]), result)
        self.assertEqual(["ran"], (path / "setup.log").read_text().split())
        self.assertIn("out", err.getvalue())
        self.assertIn("err", err.getvalue())

    def test_no_setup_runs_nothing_and_leaves_the_marker_for_the_next_session(self):
        worktree = self.make({"worktreeSetup": "printf 'ran\\n' >> setup.log"})

        code, first, _err = self.adopt(worktree, "--no-setup")
        self.assertEqual(0, code, first)
        self.assertTrue(first["noSetup"])
        self.assertIsNone(first["setup"])
        self.assertFalse((worktree / "setup.log").exists())

        code, second, _err = self.adopt(worktree)
        self.assertEqual(0, code, second)
        self.assertFalse(second["alreadySetup"])
        self.assertTrue(second["setup"]["ok"])

    def test_a_detached_worktree_is_adopted_with_no_branch(self):
        worktree = self.make(detach=True)

        code, payload, _err = self.adopt(worktree)

        self.assertEqual(0, code, payload)
        self.assertIsNone(payload["branch"])
        self.assertTrue(payload["adopted"])
