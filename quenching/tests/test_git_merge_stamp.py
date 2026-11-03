"""`cq git pr merge --spec` stamps the spec's `merge` record once the PR is merged."""
from __future__ import annotations

import contextlib
import io
import json
from types import SimpleNamespace
import unittest
from unittest import mock

import _paths  # noqa: F401
from quenching.git import pull
from quenching.specs.backends.memory import MemoryBackend
from quenching.specs.parse.records import spec_records

URL = "https://github.com/o/r/pull/7"
GREEN = [{"name": "gate", "bucket": "pass"}]
CLEAN = {"headRefOid": "abc", "mergeStateStatus": "CLEAN"}
SPEC = "---\ntitle: S\ndate: 2026-10-25\n---\n## Problem\nx\n"



_SYNC_STUBS = [mock.patch(target, return_value={"ok": True, "skipped": "test"})
               for target in ("quenching.git.pull.sync_store",
                              "quenching.git.azure_pull.sync_store",
                              "quenching.specs.commands.push.sync_store")]


def setUpModule():
    """The code-side sync points would send this checkout's own pending store writes; every
    test here stubs them (`test_specs_push.py` proves the sync itself on a fixture remote)."""
    for patcher in _SYNC_STUBS:
        patcher.start()


def tearDownModule():
    for patcher in _SYNC_STUBS:
        patcher.stop()


class MergeStamp(unittest.TestCase):
    def setUp(self):
        self.backend = MemoryBackend()
        self.backend.create_spec("plans", SPEC)

    def merge(self, *, spec="1", already_merged=False, merge_code=0):
        def gh(*argv):
            if argv[:2] == ("pr", "merge"):
                return merge_code, "", ""
            if "state" in argv:
                return 0, json.dumps({"state": "MERGED" if already_merged else "OPEN"}), ""
            if "headRefName,number" in argv:
                return 0, json.dumps({"number": 7, "headRefName": "plan/1-x"}), ""
            return 0, json.dumps(CLEAN), ""

        backend = lambda *a, **k: (self.backend, {})  # noqa: E731
        with mock.patch.object(pull, "_gh", side_effect=gh), \
                mock.patch.object(pull, "_provider", return_value="github"), \
                mock.patch.object(pull, "_checks", return_value=("green", GREEN, "")), \
                mock.patch.object(pull, "open_backend", side_effect=backend), \
                mock.patch("quenching.specs.commands.fields.open_backend", side_effect=backend), \
                contextlib.redirect_stdout(io.StringIO()) as out:
            code = pull.cmd_pr(SimpleNamespace(action="merge", url=URL, wait=0, json=True,
                                               spec=spec))
        return code, json.loads(out.getvalue())

    def stored(self):
        return spec_records(self.backend.read_spec(1)[0]["frontmatter"])["merge"]

    def test_a_merge_with_a_spec_stamps_the_merge_record(self):
        code, payload = self.merge()
        self.assertEqual((code, payload["ok"], payload["merge"]["stamped"]), (0, True, True))
        self.assertEqual({"strategy": "merge-commit", "pr": "7",
                          "subject": "Merge pull request 7 from o/plan/1-x"}, self.stored())

    def test_an_already_merged_pull_request_is_stamped_too(self):
        code, payload = self.merge(already_merged=True)
        self.assertEqual((code, payload["alreadyMerged"], payload["merge"]["stamped"]),
                         (0, True, True))
        self.assertIsNotNone(self.stored())

    def test_a_record_already_present_is_kept_and_reported(self):
        self.merge()
        before = self.stored()
        code, payload = self.merge(already_merged=True)
        self.assertEqual((code, payload["merge"]["stamped"]), (0, False))
        self.assertEqual(before, self.stored())

    def test_without_a_spec_nothing_is_stamped(self):
        code, payload = self.merge(spec=None)
        self.assertEqual(code, 0)
        self.assertNotIn("merge", payload)
        self.assertIsNone(self.stored())

    def test_a_refused_merge_stamps_nothing(self):
        code, payload = self.merge(merge_code=1)
        self.assertEqual((code, payload["reason"]), (1, "merge-refused"))
        self.assertIsNone(self.stored())

    def test_an_unknown_spec_is_reported_as_a_failed_stamp(self):
        code, payload = self.merge(spec="99")
        self.assertEqual((code, payload["reason"]), (1, "stamp-failed"))


if __name__ == "__main__":
    unittest.main()
