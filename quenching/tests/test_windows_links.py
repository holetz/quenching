"""`quenching.git.worktree` link helpers — the Windows junction fallback, driven by patching `os`."""
from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from unittest import mock

import _paths  # noqa: F401  — must precede the `quenching` import; see its docstring
from quenching.git import worktree


def _done(code, stderr=""):
    return subprocess.CompletedProcess([], code, "", stderr)


PRIVILEGE = "[WinError 1314] A required privilege is not held by the client"


def _no_winapi():
    """`import _winapi` raises ImportError: a `None` entry in sys.modules blocks the import."""
    return mock.patch.dict("sys.modules", {"_winapi": None})


def _winapi(create):
    return mock.patch.dict("sys.modules", {"_winapi": mock.Mock(CreateJunction=create)})


class MakeLinkTest(unittest.TestCase):
    def test_symlink_is_used_on_posix(self):
        with mock.patch("os.name", "posix"), \
             mock.patch("os.symlink") as sym, mock.patch("subprocess.run") as run:
            worktree._make_link("store", "link")
        sym.assert_called_once_with("store", "link", target_is_directory=True)
        run.assert_not_called()

    def test_create_junction_comes_first_on_windows(self):
        create = mock.Mock()
        with mock.patch("os.name", "nt"), _winapi(create), \
             mock.patch("os.symlink") as sym, mock.patch("subprocess.run") as run:
            worktree._make_link("store", "link")
        create.assert_called_once_with(os.path.abspath("store"), "link")
        sym.assert_not_called()
        run.assert_not_called()

    def test_mklink_when_create_junction_is_missing(self):
        with mock.patch("os.name", "nt"), _no_winapi(), \
             mock.patch("os.symlink") as sym, \
             mock.patch("subprocess.run", return_value=_done(0)) as run:
            worktree._make_link("store", "link")
        self.assertEqual(run.call_args.args[0],
                         ["cmd", "/c", "mklink", "/J", "link", os.path.abspath("store")])
        sym.assert_not_called()

    def test_mklink_when_create_junction_fails(self):
        create = mock.Mock(side_effect=OSError("junction refused"))
        with mock.patch("os.name", "nt"), _winapi(create), \
             mock.patch("os.symlink") as sym, \
             mock.patch("subprocess.run", return_value=_done(0)) as run:
            worktree._make_link("store", "link")
        self.assertEqual(run.call_args.args[0][:4], ["cmd", "/c", "mklink", "/J"])
        sym.assert_not_called()

    def test_symlink_is_the_last_resort_on_windows(self):
        with mock.patch("os.name", "nt"), _no_winapi(), \
             mock.patch("subprocess.run", return_value=_done(1, "Access is denied.")), \
             mock.patch("os.symlink") as sym:
            worktree._make_link("store", "link")
        sym.assert_called_once_with("store", "link", target_is_directory=True)

    @unittest.skipUnless(os.name == "nt", "a junction exists only on Windows")
    def test_a_git_path_with_forward_slashes_becomes_a_real_junction(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = os.path.realpath(tmp).replace("\\", "/")   # the form git prints
            store, link = f"{root}/store", f"{root}/link"
            os.mkdir(store)
            with mock.patch("os.symlink", side_effect=OSError("privilege")):
                worktree._make_link(store, link)
            self.assertTrue(worktree._is_link(link))
            self.assertEqual(os.path.realpath(link), os.path.realpath(store))
            os.rmdir(link)

    def test_refusal_propagates_on_posix(self):
        with mock.patch("os.symlink", side_effect=OSError("denied")), \
             mock.patch("os.name", "posix"), \
             mock.patch("subprocess.run") as run:
            with self.assertRaises(OSError):
                worktree._make_link("store", "link")
        run.assert_not_called()

    def test_every_cause_is_named_when_all_fail(self):
        create = mock.Mock(side_effect=OSError("junction refused"))
        with mock.patch("os.name", "nt"), _winapi(create), \
             mock.patch("subprocess.run",
                        return_value=_done(1, "Cannot create a file when that file already exists.")), \
             mock.patch("os.symlink", side_effect=OSError(PRIVILEGE)):
            with self.assertRaises(OSError) as caught:
                worktree._make_link("store", "link")
        message = str(caught.exception)
        self.assertIn("junction refused", message)
        self.assertIn("exited 1", message)
        self.assertIn("Cannot create a file when that file already exists.", message)
        self.assertIn(PRIVILEGE, message)

    def test_missing_create_junction_is_named_when_all_fail(self):
        with mock.patch("os.name", "nt"), _no_winapi(), \
             mock.patch("subprocess.run", return_value=_done(1, "boom")), \
             mock.patch("os.symlink", side_effect=OSError(PRIVILEGE)):
            with self.assertRaises(OSError) as caught:
                worktree._make_link("store", "link")
        self.assertIn("CreateJunction: unavailable", str(caught.exception))
        self.assertIn("boom", str(caught.exception))


class LinkReadTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.dir = os.path.realpath(tmp.name)

    def test_junction_counts_as_a_link(self):
        path = os.path.join(self.dir, "j")
        os.mkdir(path)
        self.assertFalse(worktree._is_link(path))
        with mock.patch("os.path.islink", return_value=False), \
             mock.patch("os.path.isjunction", create=True, return_value=True):
            self.assertTrue(worktree._is_link(path))

    def test_reparse_point_counts_as_a_link_without_isjunction(self):
        path = os.path.join(self.dir, "j")
        os.mkdir(path)
        fake = mock.Mock(st_file_attributes=0x400)
        with mock.patch("os.path.islink", return_value=False), \
             mock.patch.object(os.path, "isjunction", create=True, new=None), \
             mock.patch("os.lstat", return_value=fake):
            self.assertTrue(worktree._is_link(path))

    def test_remove_link_unlinks_a_symlink_and_rmdirs_a_junction(self):
        with mock.patch("os.path.islink", return_value=True), mock.patch("os.unlink") as un:
            worktree._remove_link("l")
        un.assert_called_once_with("l")
        with mock.patch("os.path.islink", return_value=False), mock.patch("os.rmdir") as rd:
            worktree._remove_link("l")
        rd.assert_called_once_with("l")


class MaterialiseFallbackTest(unittest.TestCase):
    def test_refused_symlink_falls_back_to_a_junction(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = os.path.realpath(tmp)
            store = os.path.join(repo, "store")
            with mock.patch("os.symlink", side_effect=OSError("privilege")), \
                 mock.patch("os.name", "nt"), _no_winapi(), \
                 mock.patch("subprocess.run", return_value=_done(0)) as run:
                result = worktree._materialise(repo, "shared", store)
        self.assertEqual(result["state"], "created")
        self.assertEqual(run.call_args.args[0][:4], ["cmd", "/c", "mklink", "/J"])


class LinkRefusalTest(unittest.TestCase):
    def test_a_failed_link_is_a_refusal_not_a_traceback(self):
        config = {"shared": {"sharedPaths": [".tmp"]}}
        with mock.patch.object(worktree, "load_config", return_value=config), \
             mock.patch.object(worktree, "namespace", side_effect=lambda c, k: c.get(k, {})), \
             mock.patch.object(worktree, "_store_names", return_value=("/s", "/s")), \
             mock.patch.object(worktree, "_migrate_store", return_value=None), \
             mock.patch.object(worktree, "_materialise", side_effect=OSError(PRIVILEGE)):
            results, refusal = worktree._link("/repo")
        self.assertIsNone(results)
        self.assertEqual(refusal["code"], "git-worktree-link-failed")
        self.assertEqual(refusal["path"], ".tmp")
        self.assertEqual(refusal["store"], "/s")
        self.assertIn(PRIVILEGE, refusal["message"])


if __name__ == "__main__":
    unittest.main()
