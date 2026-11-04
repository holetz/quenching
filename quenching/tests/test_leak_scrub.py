"""Executable proofs for `cq specs scrub` on the memory backend.

The listing writes nothing; `--apply` writes only the path normalization and leaves a denylist
hit for a human to remove. The denylisted term and `$HOME` are the test's own."""
from __future__ import annotations

import argparse
import contextlib
import io
import json
import os
import pathlib
import sys
import tempfile
import unittest
from unittest import mock

try:
    import _paths  # noqa: F401 — must precede the `quenching` import
except ModuleNotFoundError:  # package-qualified unittest invocation from the repository root
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    import _paths  # noqa: F401
from quenching.common import leak
from quenching.specs.backends.memory import MemoryBackend
from quenching.specs.commands.output import Emitter
from quenching.specs.commands.scrub import cmd_scrub

HOME = "/home/alice"
TERM = "acme-corp"


def spec(body: str) -> str:
    return f"---\ntitle: scrub\n---\n\n## Problem\n\n{body}\n"


class Scrub(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        denylist = pathlib.Path(tmp.name, "denylist.txt")
        denylist.write_text(f"{TERM}\n", encoding="utf-8")
        patcher = mock.patch.dict(os.environ, {"HOME": HOME, leak.DENYLIST_ENV: str(denylist)})
        patcher.start()
        self.addCleanup(patcher.stop)
        self.backend = MemoryBackend()
        self.backend.docs = {1: ("plans", spec("clean")),
                             2: ("plans", spec(f"see {HOME}/repo/notes.md")),
                             3: ("archive", spec(f"org {TERM} at {HOME}/x"))}

    def run_scrub(self, apply: bool) -> tuple[int, dict]:
        args = argparse.Namespace(apply=apply, json=True)
        buffer = io.StringIO()
        with mock.patch("quenching.specs.commands.scrub.open_backend",
                        return_value=(self.backend, {})), contextlib.redirect_stdout(buffer):
            code = cmd_scrub(args, f"{HOME}/repo", Emitter())
        return code, json.loads(buffer.getvalue())

    def test_listing_names_paths_and_leaks_and_writes_nothing(self):
        before = dict(self.backend.docs)
        code, body = self.run_scrub(apply=False)
        self.assertEqual(code, 1)
        self.assertEqual([(row["id"], row["paths"], [f["label"] for f in row["findings"]])
                          for row in body["specs"]],
                         [(2, True, []), (3, True, ["denylist:1"])])
        self.assertEqual((body["applied"], body["normalized"], body["denylist"]),
                         (False, 0, "present"))
        self.assertEqual(self.backend.docs, before)

    def test_apply_normalizes_paths_only_and_keeps_the_denylist_hit(self):
        code, body = self.run_scrub(apply=True)
        self.assertEqual(code, 1)
        self.assertEqual(body["normalized"], 2)
        self.assertIn("see notes.md", self.backend.docs[2][1])
        self.assertIn(f"org {TERM} at ~/x", self.backend.docs[3][1])
        self.assertEqual(self.backend.docs[1][1], spec("clean"))

    def test_a_clean_store_exits_zero(self):
        self.backend.docs = {1: ("plans", spec("clean"))}
        self.assertEqual(self.run_scrub(apply=False), (0, {
            "ok": True, "applied": False, "normalized": 0, "denylist": "present", "specs": []}))


if __name__ == "__main__":
    unittest.main()
