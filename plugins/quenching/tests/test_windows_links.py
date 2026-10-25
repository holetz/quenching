"""`quenching.git.worktree` link helpers — the Windows junction fallback, driven by patching `os`."""
from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from unittest import mock

import _paths  # noqa: F401  — must precede the `quenching` import; see its docstring
from quenching.git import worktree


def _done(code):
    return subprocess.CompletedProcess([], code, "", "")


class MakeLinkTest(unittest.TestCase):
    def test_symlink_is_used_when_allowed(self):
        with mock.patch("os.symlink") as sym, mock.patch("subprocess.run") as run:
            worktree._make_link("store", "link")
        sym.assert_called_once_with("store", "link", target_is_directory=True)
        run.assert_not_called()

    def test_junction_when_symlink_refused_on_windows(self):
        with mock.patch("os.symlink", side_effect=OSError("privilege")), \
             mock.patch("os.name", "nt"), \
             mock.patch("subprocess.run", return_value=_done(0)) as run:
            worktree._make_link("store", "link")
        self.assertEqual(run.call_args.args[0], ["cmd", "/c", "mklink", "/J", "link", "store"])

    def test_refusal_propagates_on_posix(self):
        with mock.patch("os.symlink", side_effect=OSError("denied")), \
             mock.patch("subprocess.run") as run:
            with self.assertRaises(OSError):
                worktree._make_link("store", "link")
        run.assert_not_called()

    def test_failed_junction_propagates(self):
        with mock.patch("os.symlink", side_effect=OSError("privilege")), \
             mock.patch("os.name", "nt"), \
             mock.patch("subprocess.run", return_value=_done(1)):
            with self.assertRaises(OSError):
                worktree._make_link("store", "link")


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
                 mock.patch("os.name", "nt"), \
                 mock.patch("subprocess.run", return_value=_done(0)) as run:
                result = worktree._materialise(repo, "shared", store)
        self.assertEqual(result["state"], "created")
        self.assertEqual(run.call_args.args[0][:4], ["cmd", "/c", "mklink", "/J"])


if __name__ == "__main__":
    unittest.main()
