"""`adopt-worktree.py` — the SessionStart hook that adopts the worktree the harness already cut.

The body is exercised as the deployment runs it: a process, stdin JSON, stdout JSON. A fake
`cq` stands in for the verb so the plumbing is read without a real worktree, and one case runs
against this repository's real primary checkout to prove the no-op."""
from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

PLUGIN_ROOT = pathlib.Path(__file__).resolve().parent.parent
REPO_ROOT = PLUGIN_ROOT.parent
HANDLER = PLUGIN_ROOT / "assets" / "hooks" / "adopt-worktree.py"
CQ = pathlib.Path(".agents") / "quenching" / "bin" / "cq"


def run(payload, cwd=None):
    text = payload if isinstance(payload, str) else json.dumps(payload)
    done = subprocess.run([sys.executable, str(HANDLER)], input=text, capture_output=True,
                          text=True, encoding="utf-8", cwd=str(cwd) if cwd else None)
    assert done.returncode == 0, done.stderr
    return json.loads(done.stdout)


def fake_cq(root: pathlib.Path, payload: dict | str, code: int = 0) -> None:
    path = root / CQ
    path.parent.mkdir(parents=True, exist_ok=True)
    body = payload if isinstance(payload, str) else json.dumps(payload)
    path.write_text("import json, sys\n"
                    f"print({body!r})\n"
                    f"sys.exit({code})\n", encoding="utf-8")


ADOPTED = {"ok": True, "adopted": True, "worktree": "/tmp/repo.worktrees/copilot-x",
           "branch": "copilot/x", "base": "main", "baseInferred": True,
           "alreadySetup": False}


class TheAdoptionContext(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = pathlib.Path(tmp.name)

    def test_a_linked_worktree_is_announced_with_its_path_branch_and_base(self):
        fake_cq(self.root, ADOPTED)
        out = run({"cwd": str(self.root)})
        inner = out["hookSpecificOutput"]
        self.assertEqual("SessionStart", inner["hookEventName"])
        self.assertIn("/tmp/repo.worktrees/copilot-x", inner["additionalContext"])
        self.assertIn("copilot/x", inner["additionalContext"])
        self.assertIn("main", inner["additionalContext"])
        self.assertIn("Do not cut another worktree", inner["additionalContext"])

    def test_every_payload_spelling_of_the_session_directory_is_read(self):
        fake_cq(self.root, ADOPTED)
        for payload in ({"workingDirectory": str(self.root)},
                        {"working_directory": str(self.root)},
                        {"cwd": str(self.root)}):
            with self.subTest(payload=payload):
                self.assertIn("copilot/x", run(payload)["hookSpecificOutput"]["additionalContext"])

    def test_no_payload_directory_falls_back_to_the_process_cwd(self):
        fake_cq(self.root, ADOPTED)
        out = run({}, cwd=self.root)
        self.assertIn("copilot/x", out["hookSpecificOutput"]["additionalContext"])


class TheNoOps(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = pathlib.Path(tmp.name)

    def test_no_deployed_cq_is_silent(self):
        self.assertEqual({}, run({"cwd": str(self.root)}))

    def test_a_refusal_is_silent(self):
        fake_cq(self.root, {"ok": False, "code": "git-worktree-slot"}, code=2)
        self.assertEqual({}, run({"cwd": str(self.root)}))

    def test_unparseable_cq_output_is_silent(self):
        fake_cq(self.root, "not json")
        self.assertEqual({}, run({"cwd": str(self.root)}))

    def test_a_payload_without_adoption_is_silent(self):
        fake_cq(self.root, {"ok": True})
        self.assertEqual({}, run({"cwd": str(self.root)}))

    def test_invalid_input_is_silent(self):
        self.assertEqual({}, run("not json"))

    def test_the_real_primary_checkout_is_a_noop(self):
        # REPO_ROOT is a linked worktree when the suite runs from one; the primary checkout
        # is the parent of the shared git dir, so the no-op is proven against that.
        common = subprocess.run(["git", "rev-parse", "--path-format=absolute", "--git-common-dir"],
                                capture_output=True, text=True, cwd=str(REPO_ROOT), check=True)
        primary = pathlib.Path(common.stdout.strip()).parent
        self.assertEqual({}, run({"cwd": str(primary)}))
