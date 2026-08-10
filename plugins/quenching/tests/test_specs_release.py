"""The version lockstep — `bump_release_artifacts` proved against a disposable tree standing
in for the seven real artifacts, never the plugin's own, so this runs safely on every test
run without ever bumping a real version.

Migrated from `specs.py`'s `release_lockstep_failures`. Both directions matter: seven
agreeing values all move together, and one already-drifted value refuses before any of the
seven is touched — kept as two separate cases below rather than folded into one, so a failure
names which direction broke.
"""
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

    def test_seven_agreeing_artifacts_are_reported_moved(self):
        result = bump_release_artifacts(self.tmp, "9.10.0")
        self.assertTrue(result["ok"], result.get("error"))
        self.assertEqual((result["oldVersion"], result["newVersion"]), ("9.9.9", "9.10.0"))

    def test_every_artifact_reads_back_the_new_version(self):
        bump_release_artifacts(self.tmp, "9.10.0")
        pattern = {"plain": None, "json": _RELEASE_JSON_VERSION_RE, "py": _RELEASE_PY_VERSION_RE}
        for rel, kind in RELEASE_ARTIFACTS:
            with self.subTest(artifact=rel):
                text = read_text(os.path.join(self.tmp, rel))
                pat = pattern[kind]
                got = text.strip() if pat is None else pat.search(text).group(2)
                self.assertEqual(got, "9.10.0")

    def test_bumping_a_py_artifact_touches_only_the_quoted_value(self):
        # The substitution is a regex on the VERSION line, not a line replacement — a comment
        # riding the same line must survive it.
        bump_release_artifacts(self.tmp, "9.10.0")
        text = read_text(os.path.join(self.tmp, "plugins/quenching/assets/bin/specs.py"))
        self.assertIn("# a comment that must survive the bump", text)

    def test_a_lockstep_already_drifted_is_refused_rather_than_compounded(self):
        # Precondition: one artifact disagreeing with the rest BEFORE the bump is a refusal,
        # not an eighth value folded into the compare.
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


if __name__ == "__main__":
    unittest.main()
