"""`dispatch.py` — every hook of one matcher in one process, combined, failing open."""

import json
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest

PLUGIN_ROOT = pathlib.Path(__file__).resolve().parent.parent
HOOKS = PLUGIN_ROOT / "assets" / "hooks"
BODIES = ("deny-claude-coauthor", "warn-git-add-all")


def payload(command):
    return json.dumps({"tool_name": "Bash", "tool_input": {"command": command}})


class TheDispatcher(unittest.TestCase):
    def setUp(self):
        self.dir = pathlib.Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.dir)
        for name in ("dispatch", *BODIES):
            shutil.copy(HOOKS / f"{name}.py", self.dir)

    def run_it(self, raw, *names):
        done = subprocess.run([sys.executable, "-I", str(self.dir / "dispatch.py"), *names],
                              input=raw, capture_output=True, text=True)
        self.assertEqual(0, done.returncode, done.stderr)
        return json.loads(done.stdout)

    def test_one_process_combines_a_deny_and_a_warning(self):
        out = self.run_it(payload('git add -A && git commit -m x -m "Co-Authored-By: Claude '
                                  '<noreply@anthropic.com>"'), *BODIES)
        inner = out["hookSpecificOutput"]
        self.assertEqual("deny", inner["permissionDecision"])
        self.assertIn("co-authorship", inner["permissionDecisionReason"])
        self.assertIn("git add -A", inner["additionalContext"])
        self.assertIn("/quenching-git commit", out["systemMessage"])
        self.assertEqual("PreToolUse", inner["hookEventName"])

    def test_each_body_alone_answers_as_it_did_standalone(self):
        for command in ("git add .", "git commit --no-verify -m wip", "ls"):
            with self.subTest(command=command):
                alone = json.loads(subprocess.run(
                    [sys.executable, str(self.dir / "warn-git-add-all.py")], input=payload(command),
                    capture_output=True, text=True).stdout)
                self.assertEqual(alone, self.run_it(payload(command), *BODIES))

    def test_nothing_matched_prints_an_empty_object(self):
        self.assertEqual({}, self.run_it(payload("git status"), *BODIES))
        self.assertEqual({}, self.run_it(payload("git add -A")))

    def test_a_missing_or_unsafe_body_is_skipped(self):
        (self.dir / "deny-claude-coauthor.py").unlink()
        out = self.run_it(payload("git add -A"), "deny-claude-coauthor", "../x", "dispatch",
                          "warn-git-add-all")
        self.assertIn("/quenching-git commit", out["systemMessage"])

    def test_a_body_that_raises_is_skipped_and_the_others_still_answer(self):
        (self.dir / "broken.py").write_text("def decide(raw):\n    raise RuntimeError('boom')\n")
        (self.dir / "noisy.py").write_text("raise ImportError('at import')\n")
        out = self.run_it(payload("git add -A"), "broken", "noisy", "warn-git-add-all")
        self.assertIn("/quenching-git commit", out["systemMessage"])

    def test_input_that_is_not_json_fails_open(self):
        self.assertEqual({}, self.run_it("not json", *BODIES))
        out = self.run_it("git add -A co-authored-by noreply@anthropic", *BODIES)
        self.assertNotIn("permissionDecision", out.get("hookSpecificOutput", {}))


if __name__ == "__main__":
    unittest.main()
