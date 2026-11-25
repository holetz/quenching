"""The one cache root: where it resolves per platform, and the silent move of the legacy root."""

import os
import tempfile
import unittest
from unittest import mock

import _paths  # noqa: F401  — must precede the `quenching` import; see its docstring
from quenching.common import cache


class ResolveTest(unittest.TestCase):
    def test_xdg_wins_on_every_platform(self):
        for platform in ("linux", "win32", "darwin"):
            env = {"XDG_CACHE_HOME": "/x", "LOCALAPPDATA": "C:/L", "HOME": "/h"}
            self.assertEqual(os.path.join("/x", "quenching"),
                             cache.resolve_cache_root(env, platform))

    def test_windows_uses_localappdata(self):
        env = {"LOCALAPPDATA": "C:/Users/u/AppData/Local", "HOME": "/h"}
        self.assertEqual(os.path.join("C:/Users/u/AppData/Local", "quenching"),
                         cache.resolve_cache_root(env, "win32"))

    def test_posix_uses_home_cache(self):
        env = {"LOCALAPPDATA": "C:/L", "HOME": "/h"}
        self.assertEqual(os.path.join("/h", ".cache", "quenching"),
                         cache.resolve_cache_root(env, "linux"))

    def test_cache_path_joins_under_the_root(self):
        with mock.patch.dict(os.environ, {"XDG_CACHE_HOME": "/x"}):
            self.assertEqual(os.path.join("/x", "quenching", "git", "a.json"),
                             cache.cache_path("git", "a.json"))


class MigrateTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.env = {"HOME": os.path.join(self.tmp, "home")}
        self.legacy = os.path.join(self.tmp, "home", ".cache", "quenching")
        self.root = os.path.join(self.tmp, "local", "quenching")

    def test_moves_the_legacy_root_when_the_new_one_is_absent(self):
        os.makedirs(os.path.join(self.legacy, "mirrors"))
        self.assertTrue(cache.migrate_legacy(self.root, self.env))
        self.assertTrue(os.path.isdir(os.path.join(self.root, "mirrors")))
        self.assertFalse(os.path.exists(self.legacy))

    def test_keeps_both_when_the_new_root_exists(self):
        os.makedirs(self.legacy)
        os.makedirs(self.root)
        self.assertFalse(cache.migrate_legacy(self.root, self.env))
        self.assertTrue(os.path.isdir(self.legacy))

    def test_nothing_to_move_and_same_path_are_no_ops(self):
        self.assertFalse(cache.migrate_legacy(self.root, self.env))
        os.makedirs(self.legacy)
        self.assertFalse(cache.migrate_legacy(self.legacy, self.env))
        self.assertTrue(os.path.isdir(self.legacy))

    def test_a_failed_move_leaves_the_legacy_root(self):
        os.makedirs(self.legacy)
        with mock.patch.object(cache.os, "replace", side_effect=OSError("busy")):
            self.assertFalse(cache.migrate_legacy(self.root, self.env))
        self.assertTrue(os.path.isdir(self.legacy))


if __name__ == "__main__":
    unittest.main()
