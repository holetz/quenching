"""A `base` qualified by the remote (`origin/main`) names the same base as `main`.

The fetch is of `refs/heads/<base>`, so `acquire` used to build `refs/heads/origin/main` and
refuse with `git-worktree-fetch-failed`; the prefix is dropped before the fetch."""
from __future__ import annotations

import _paths  # noqa: F401  — must precede the `quenching` import; see its docstring
import test_git_worktree_slots as base


class RemoteQualifiedBase(base.SlotRepo):
    def test_acquire_accepts_origin_slash_base(self):
        code, out = self.run_verb("acquire", branch="plan/1-a", base="origin/main")
        self.assertEqual(code, 0, out)
        self.assertEqual(out["base"], "main")
        self.assertEqual(out["start"], "origin/main")

    def test_bare_base_still_works(self):
        code, out = self.run_verb("acquire", branch="plan/1-a", base="main")
        self.assertEqual(code, 0, out)
        self.assertEqual(out["start"], "origin/main")

    def test_a_branch_whose_name_only_starts_like_the_remote_is_kept(self):
        from quenching.git.audit import _strip_remote
        self.assertEqual(_strip_remote("origin", "origin"), "origin")
        self.assertEqual(_strip_remote("origin/", "origin"), "origin/")
        self.assertEqual(_strip_remote("originx/main", "origin"), "originx/main")


if __name__ == "__main__":
    import unittest
    unittest.main()
