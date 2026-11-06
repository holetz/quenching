"""The ignored-content rules and the one read of git's ignored entries, proved without running
git or writing fixtures to disk."""
from __future__ import annotations

import os
from types import SimpleNamespace
import unittest
from unittest import mock

import _paths  # noqa: F401  — must precede the `quenching` import
from quenching.git import ignored


class RegenerableRulesTests(unittest.TestCase):
    def test_default_list(self):
        self.assertEqual(ignored.DEFAULT_REGENERABLE, (
            ".venv", "venv", "__pycache__", "*.py[cod]", ".pytest_cache", ".ruff_cache",
            ".mypy_cache", ".pyright", ".tox", ".nox", "htmlcov", ".coverage*",
            "*.egg-info", ".eggs", "pip-wheel-metadata", ".cache", ".ipynb_checkpoints",
            ".hypothesis", "node_modules",
        ))
        rules = ignored.declared_regenerable({})
        for entry in ("build/", "dist/", "nested/build/manual.txt", "nested/dist/manual.txt"):
            with self.subTest(entry=entry):
                self.assertFalse(ignored.is_regenerable(entry, rules))

    def test_defaults_match_at_any_depth(self):
        rules = ignored.declared_regenerable({})
        entries = (".venv/", "pkg/venv/lib/file", "pkg/__pycache__/x.pyc",
                   "pkg/x.pyc", "pkg/x.pyo", "pkg/x.pyd", "pkg/.pytest_cache/",
                   "pkg/.ruff_cache/", "pkg/.mypy_cache/", "pkg/.pyright/", "pkg/.tox/",
                   "pkg/.nox/", "pkg/htmlcov/", "pkg/.coverage", "pkg/.coverage.worker",
                   "pkg/demo.egg-info/PKG-INFO", "pkg/.eggs/", "pkg/pip-wheel-metadata/",
                   "pkg/.cache/", "pkg/.ipynb_checkpoints/", "pkg/.hypothesis/",
                   "pkg/node_modules/dependency/index.js")
        for entry in entries:
            with self.subTest(entry=entry):
                self.assertTrue(ignored.is_regenerable(entry, rules))
        for entry in ("x.py", "x.pycc", "my.venv/", "node_modules_backup/file"):
            with self.subTest(entry=entry):
                self.assertFalse(ignored.is_regenerable(entry, rules))

    def test_config_adds_normalized_rules_after_defaults(self):
        config = {"namespaces": {"shared": {"regenerablePaths": [
            " build/ ", "./generated//reports/", "cache", "", "   ", None, 12,
            "/absolute", "../outside", "cache/../outside",
        ]}}}
        rules = ignored.declared_regenerable(config)
        self.assertEqual(rules, list(ignored.DEFAULT_REGENERABLE) + [
            "build/", os.path.join("generated", "reports") + "/", "cache",
        ])
        self.assertTrue(ignored.is_regenerable("build/manual.txt", rules))
        self.assertEqual(config["namespaces"]["shared"]["regenerablePaths"][0], " build/ ")

    def test_invalid_config_and_returned_lists_do_not_remove_defaults(self):
        for config in ({}, {"namespaces": {"shared": {}}},
                       {"namespaces": {"shared": {"regenerablePaths": []}}},
                       {"namespaces": {"shared": {"regenerablePaths": "build/"}}}):
            with self.subTest(config=config):
                rules = ignored.declared_regenerable(config)
                self.assertEqual(rules, list(ignored.DEFAULT_REGENERABLE))
                rules.clear()
                self.assertTrue(ignored.declared_regenerable(config))

    def test_component_rules_match_whole_components(self):
        for entry in ("cache", "cache/file", "nested/cache/file"):
            self.assertTrue(ignored.is_regenerable(entry, ["cache"]))
        self.assertFalse(ignored.is_regenerable("nested/cache-old/file", ["cache"]))

    def test_anchored_rules_preserve_trailing_slash_and_literal_wildcards(self):
        for rule in ("data/", "output/data", "output/data/"):
            root = rule.rstrip("/")
            with self.subTest(rule=rule):
                self.assertTrue(ignored.is_regenerable(root, [rule]))
                self.assertTrue(ignored.is_regenerable(root + "/file", [rule]))
                self.assertFalse(ignored.is_regenerable("nested/" + root + "/file", [rule]))
                self.assertFalse(ignored.is_regenerable(root + "-old/file", [rule]))
        self.assertFalse(ignored.is_regenerable("output/demo.egg-info/file", ["output/*.egg-info"]))
        self.assertTrue(ignored.is_regenerable("output/*.egg-info/file", ["output/*.egg-info"]))
        self.assertFalse(ignored.is_regenerable("demo.egg-info/file", ["*.egg-info/"]))


class IgnoredEntriesTests(unittest.TestCase):
    @mock.patch.object(ignored, "_is_link", return_value=False)
    @mock.patch.object(ignored, "_git_run")
    def test_reads_only_ignored_lines_with_bounded_status(self, run, is_link):
        run.return_value = (0, " M tracked.txt\n?? untracked.txt\n!! .cache/\n!! notes.txt\n", "")
        self.assertEqual(ignored.ignored_entries("repo"), [".cache/", "notes.txt"])
        run.assert_called_once_with("repo", *ignored.SAFE, "status", "--porcelain",
                                    "--untracked-files=normal", "--ignored=matching")
        self.assertEqual(is_link.call_args_list, [
            mock.call(os.path.join("repo", ".cache")),
            mock.call(os.path.join("repo", "notes.txt")),
        ])

    @mock.patch.object(ignored, "_git_run")
    def test_failed_inspection_is_not_empty(self, run):
        run.return_value = (128, "!! .cache/\n", "failure")
        self.assertIsNone(ignored.ignored_entries("repo"))
        run.return_value = (0, "", "")
        self.assertEqual(ignored.ignored_entries("repo"), [])

    @mock.patch.object(ignored, "_is_link", side_effect=[True, True, False])
    @mock.patch.object(ignored, "_git_run", return_value=(
        0, "!! .venv/\n!! shared-file\n!! local.txt\n", ""))
    def test_excludes_shared_directory_and_file_links(self, run, is_link):
        self.assertEqual(ignored.ignored_entries("repo"), ["local.txt"])

    def test_link_detection(self):
        with mock.patch.object(ignored.os.path, "islink", return_value=True):
            self.assertTrue(ignored._is_link("shared"))
        with mock.patch.object(ignored.os.path, "islink", return_value=False):
            with mock.patch.object(ignored.os.path, "isjunction", create=True, return_value=True):
                self.assertTrue(ignored._is_link("shared"))
            with mock.patch.object(ignored.os.path, "isjunction", create=True, new=None):
                with mock.patch.object(ignored.os, "lstat", return_value=SimpleNamespace(
                        st_file_attributes=0x400)):
                    self.assertTrue(ignored._is_link("shared"))
                with mock.patch.object(ignored.os, "lstat", return_value=SimpleNamespace()):
                    self.assertFalse(ignored._is_link("local"))
                with mock.patch.object(ignored.os, "lstat", side_effect=OSError):
                    self.assertFalse(ignored._is_link("missing"))


class UndeclaredTests(unittest.TestCase):
    @mock.patch.object(ignored.os, "walk")
    def test_known_cache_does_not_expand(self, walk):
        self.assertEqual(ignored.undeclared("repo", ["pkg/.venv/"],
                                           ignored.declared_regenerable({})), [])
        walk.assert_not_called()

    @mock.patch.object(ignored.os, "walk")
    def test_wholly_ignored_directory_separates_declared_and_unknown_files(self, walk):
        walk.return_value = [
            (os.path.join("repo", "output"), ["cache"], ["notes.txt", ".coverage"]),
            (os.path.join("repo", "output", "cache"), [], ["result.txt"]),
        ]
        rules = ignored.declared_regenerable({
            "namespaces": {"shared": {"regenerablePaths": ["output/cache"]}},
        })
        self.assertEqual(ignored.undeclared("repo", ["output/", "private.txt"], rules),
                         [os.path.join("output", "notes.txt"), "private.txt"])
        walk.assert_called_once_with(os.path.join("repo", "output/"))

    @mock.patch.object(ignored.os, "walk", return_value=[])
    def test_unknown_empty_directory_is_preserved(self, walk):
        self.assertEqual(ignored.undeclared("repo", ["unknown/"], []), ["unknown/"])


if __name__ == "__main__":
    unittest.main()
