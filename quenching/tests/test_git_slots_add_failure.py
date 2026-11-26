"""`cq git worktree acquire` when cutting a new slot fails for a reason other than the cap.

A `git worktree add` that fails with room left in the pool (a long path, an antivirus holding a
file) is not a full pool: `acquire` refuses with `git-worktree-add-failed` and git's own stderr,
never `git-worktree-slots-full`, and `--wait` does not turn it into a silent wait."""
from __future__ import annotations

import contextlib
import os
import unittest
from unittest import mock

import _paths  # noqa: F401  — must precede the `quenching` import; see its docstring
import test_git_worktree_slots as base
from quenching.git import slots

STDERR = "fatal: could not create leading directories: Filename too long"


def _failing_add(real):
    """`_git_run` with every `worktree add` failing the way Windows does on a long path."""
    def run(cwd, *args, **kw):
        if "worktree" in args and "add" in args:
            return 128, "", STDERR + "\n"
        return real(cwd, *args, **kw)
    return run


class AddFailure(base.SlotRepo):
    def test_a_failed_add_is_refused_as_add_failed_with_gits_stderr(self):
        with mock.patch.object(slots, "_git_run", _failing_add(slots._git_run)):
            code, out = self.run_verb("acquire", branch="plan/1-a")
        self.assertNotEqual(code, 0)
        self.assertEqual(out["code"], "git-worktree-add-failed")
        self.assertIn(STDERR, out["message"])
        self.assertEqual(os.path.basename(out["path"]), "repo-slot-1")
        self.assertEqual(out["max"], 3)
        self.assertNotIn("slots are held", out["message"])

    def test_with_wait_a_failed_add_is_refused_at_once(self):
        with mock.patch.object(slots, "_git_run", _failing_add(slots._git_run)), \
                mock.patch.object(slots.time, "sleep") as sleep:
            code, out = self.run_verb("acquire", branch="plan/1-a", wait=True)
        self.assertNotEqual(code, 0)
        self.assertEqual(out["code"], "git-worktree-add-failed")
        # `time` is shared: git retries and locks elsewhere sleep briefly; only the slot poll counts
        poll = slots.DEFAULTS["pollSeconds"]
        self.assertNotIn(mock.call(poll), sleep.call_args_list)

    def test_a_merged_holder_is_still_reused_before_refusing(self):
        _code, got = self.run_verb("acquire", branch="plan/1-a")
        with open(os.path.join(got["path"], "f.txt"), "w") as fh:
            fh.write("work")
        base._git(got["path"], "add", "f.txt")
        base._git(got["path"], "commit", "-q", "-m", "work")
        base._git(self.main, "merge", "-q", "--ff-only", "plan/1-a")
        base._git(self.main, "push", "-q", "origin", "main")
        with mock.patch.object(slots, "_git_run", _failing_add(slots._git_run)):
            code, out = self.run_verb("acquire", branch="plan/2-b")
        self.assertEqual(code, 0, out)
        self.assertEqual(out["path"], got["path"])
        self.assertFalse(out["created"])

    def test_a_creation_lock_timeout_is_a_refusal_not_a_traceback(self):
        @contextlib.contextmanager
        def stuck(_cwd, timeout=60.0):
            raise TimeoutError("slot creation lock held: /x/quenching-slots.lock")
            yield  # pragma: no cover

        with mock.patch.object(slots, "_creation_lock", stuck):
            code, out = self.run_verb("acquire", branch="plan/1-a")
        self.assertNotEqual(code, 0)
        self.assertEqual(out["code"], "git-worktree-slots-lock-timeout")
        self.assertIn("quenching-slots.lock", out["message"])

    def test_a_cap_really_reached_is_still_slots_full(self):
        self.config({"min": 1, "max": 1, "waitMinutes": 1, "pollSeconds": 1})
        self.assertEqual(self.run_verb("acquire", branch="plan/1-a")[0], 0)
        code, out = self.run_verb("acquire", branch="plan/2-b")
        self.assertNotEqual(code, 0)
        self.assertEqual(out["code"], "git-worktree-slots-full")


if __name__ == "__main__":
    unittest.main()
