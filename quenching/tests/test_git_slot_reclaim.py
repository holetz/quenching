"""Reclaiming a slot whose spec is archived: `release` carries `.quenching/handoff/` to the
primary checkout, `cq git stale` reports the held slot as `kind: slot` only with every piece of
evidence in favour, and `cq git prune --slot` releases it against the approved tip and id."""
from __future__ import annotations

import os
import pathlib
import unittest

import _paths  # noqa: F401  — must precede the `quenching` import; see its docstring
from test_git_worktree_slots import SlotRepo


class ReclaimRepo(SlotRepo):
    def setUp(self):
        super().setUp()
        exclude = pathlib.Path(self.main, ".git", "info", "exclude")
        exclude.parent.mkdir(parents=True, exist_ok=True)
        exclude.write_text(".quenching/\n.agents/\n", encoding="utf-8")

    def handoff(self, root, name, text):
        path = pathlib.Path(root, ".quenching", "handoff", name)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path


class ReleaseCarriesTheHandoff(ReclaimRepo):
    def test_a_handoff_is_moved_to_the_primary_checkout_and_the_slot_is_released(self):
        got = self.run_verb("acquire", branch="plan/1-a")[1]
        self.handoff(got["path"], "next.md", "slot\n")
        code, out = self.run_verb("release", path=got["path"])
        self.assertEqual(code, 0, out)
        self.assertTrue(out["released"])
        moved = pathlib.Path(self.main, ".quenching", "handoff", "next.md")
        self.assertEqual(moved.read_text(encoding="utf-8"), "slot\n")
        self.assertEqual([h["to"] for h in out["handoff"]], [str(moved)])
        self.assertFalse(pathlib.Path(got["path"], ".quenching", "handoff").exists())

    def test_a_name_taken_in_the_primary_is_never_overwritten(self):
        got = self.run_verb("acquire", branch="plan/1-a")[1]
        kept = self.handoff(self.main, "next.md", "primary\n")
        self.handoff(got["path"], "next.md", "slot\n")
        code, out = self.run_verb("release", path=got["path"])
        self.assertEqual(code, 0, out)
        self.assertEqual(kept.read_text(encoding="utf-8"), "primary\n")
        target = pathlib.Path(out["handoff"][0]["to"])
        self.assertEqual(target.name, f"next-{os.path.basename(got['path'])}-1.md")
        self.assertEqual(target.read_text(encoding="utf-8"), "slot\n")

    def test_other_ignored_content_still_keeps_the_slot_held(self):
        got = self.run_verb("acquire", branch="plan/1-a")[1]
        self.handoff(got["path"], "next.md", "slot\n")
        pathlib.Path(got["path"], ".tmp").mkdir()
        pathlib.Path(got["path"], ".tmp", "work.txt").write_text("w\n", encoding="utf-8")
        code, out = self.run_verb("release", path=got["path"])
        self.assertEqual(code, 1, out)
        self.assertFalse(out["released"])
        self.assertTrue(pathlib.Path(got["path"], ".quenching", "handoff", "next.md").exists())


if __name__ == "__main__":
    unittest.main()
