"""The version lockstep — `bump_release_artifacts` proved against a disposable tree standing
in for the four real artifacts and its changelog gate, never the plugin's own, so this runs
safely on every test run without ever bumping a real version.

Migrated from the pre-refactor specs script's `release_lockstep_failures`. Both directions
matter: four agreeing values all move together, and one already-drifted value refuses before
any of the four is touched — kept as two separate cases below rather than folded into one, so
a failure names which direction broke.
"""
import json
import os
import tempfile
import unittest

import _paths  # noqa: F401  — must precede the `quenching` import; see its docstring
from quenching.common.io import read_text, write_text
from quenching.specs.release import (
    RELEASE_ARTIFACTS,
    _RELEASE_JSON_VERSION_RE,
    _RELEASE_PY_VERSION_RE,
    bump_release_artifacts,
)

# One value per artifact `kind`, each pre-set to the old version the bump must move away from.
KINDS = {
    "plain": "9.9.9\n",
    "json": '{\n  "name": "x",\n  "version": "9.9.9"\n}\n',
    "jsonall": '{\n  "plugins": [\n    {"name": "a", "version": "9.9.9"},\n'
               '    {"name": "b", "version": "9.9.9"}\n  ]\n}\n',
    "py": 'VERSION = "9.9.9"  # a comment that must survive the bump\n',
}


class Lockstep(unittest.TestCase):
    def setUp(self):
        tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(tmpdir.cleanup)
        self.tmp = tmpdir.name
        for rel, kind in RELEASE_ARTIFACTS:
            path = os.path.join(self.tmp, rel)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            write_text(path, KINDS[kind])
        write_text(os.path.join(self.tmp, "CHANGELOG.md"), "# Changelog\n\n## 9.10.0\n")

    def test_four_agreeing_artifacts_are_reported_moved(self):
        result = bump_release_artifacts(self.tmp, "9.10.0")
        self.assertTrue(result["ok"], result.get("error"))
        self.assertEqual((result["oldVersion"], result["newVersion"]), ("9.9.9", "9.10.0"))

    def test_every_artifact_reads_back_the_new_version(self):
        bump_release_artifacts(self.tmp, "9.10.0")
        pattern = {"plain": None, "json": _RELEASE_JSON_VERSION_RE,
                   "jsonall": _RELEASE_JSON_VERSION_RE, "py": _RELEASE_PY_VERSION_RE}
        for rel, kind in RELEASE_ARTIFACTS:
            with self.subTest(artifact=rel):
                text = read_text(os.path.join(self.tmp, rel))
                pat = pattern[kind]
                got = ({text.strip()} if pat is None
                       else {m.group(2) for m in pat.finditer(text)})
                self.assertEqual(got, {"9.10.0"})

    def test_bumping_a_py_artifact_touches_only_the_quoted_value(self):
        # The substitution is a regex on the VERSION line, not a line replacement — a comment
        # riding the same line must survive it.
        bump_release_artifacts(self.tmp, "9.10.0")
        text = read_text(os.path.join(
            self.tmp, "plugins/quenching/assets/bin/quenching/common/version.py"))
        self.assertIn("# a comment that must survive the bump", text)

    def test_a_release_without_a_matching_changelog_entry_is_refused_before_writes(self):
        write_text(os.path.join(self.tmp, "CHANGELOG.md"), "# Changelog\n\n## 9.9.9\n")

        result = bump_release_artifacts(self.tmp, "9.10.0")

        self.assertFalse(result["ok"])
        self.assertIn("CHANGELOG.md", result["error"])
        self.assertIn("9.10.0", result["error"])
        for rel, kind in RELEASE_ARTIFACTS:
            with self.subTest(artifact=rel):
                self.assertEqual(read_text(os.path.join(self.tmp, rel)), KINDS[kind])

    def test_a_lockstep_already_drifted_is_refused_rather_than_compounded(self):
        # Precondition: one artifact disagreeing with the rest BEFORE the bump is a refusal,
        # not a fifth value folded into the compare.
        write_text(os.path.join(self.tmp, "plugins/quenching/VERSION"), "9.9.8\n")
        result = bump_release_artifacts(self.tmp, "9.10.0")
        self.assertFalse(result["ok"])

    def test_a_drifted_lockstep_is_refused_before_any_artifact_is_written(self):
        write_text(os.path.join(self.tmp, "plugins/quenching/VERSION"), "9.9.8\n")
        bump_release_artifacts(self.tmp, "9.10.0")
        for rel, kind in RELEASE_ARTIFACTS:
            if rel == "plugins/quenching/VERSION":
                continue
            with self.subTest(artifact=rel):
                self.assertEqual(read_text(os.path.join(self.tmp, rel)), KINDS[kind])

    def test_a_marketplace_entry_without_a_version_is_refused(self):
        path = os.path.join(self.tmp, ".claude-plugin/marketplace.json")
        write_text(path, '{"plugins": [{"name": "a", "version": "9.9.9"}, {"name": "b"}]}')
        self.assertFalse(bump_release_artifacts(self.tmp, "9.10.0")["ok"])


REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))


class RealRepoLockstep(unittest.TestCase):
    def test_every_published_version_is_equal(self):
        found = {}
        for rel, kind in RELEASE_ARTIFACTS:
            text = read_text(os.path.join(REPO, rel))
            self.assertIsNotNone(text, rel)
            if kind == "plain":
                found[rel] = text.strip()
            elif kind == "py":
                found[rel] = _RELEASE_PY_VERSION_RE.search(text).group(2)
            elif kind == "json":
                found[rel] = json.loads(text)["version"]
        market = json.loads(read_text(os.path.join(REPO, ".claude-plugin/marketplace.json")))
        for entry in market["plugins"]:
            self.assertIn("version", entry, entry["name"])
            found["marketplace:" + entry["name"]] = entry["version"]
        self.assertEqual(len(set(found.values())), 1, found)

    def test_manifests_carry_no_hard_coded_command_count(self):
        for rel in (".claude-plugin/marketplace.json",
                    "plugins/quenching/.claude-plugin/plugin.json"):
            self.assertNotRegex(read_text(os.path.join(REPO, rel)), r"\d+ commands", rel)


if __name__ == "__main__":
    unittest.main()
