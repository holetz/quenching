"""`warn-git-add-all.sh` — the PreToolUse guard that flags blanket staging without ever blocking."""

import json
import pathlib
import subprocess
import unittest

PLUGIN_ROOT = pathlib.Path(__file__).resolve().parent.parent
HANDLER = PLUGIN_ROOT / "assets" / "hooks" / "warn-git-add-all.sh"


def run(command):
    payload = json.dumps({"tool_name": "Bash", "tool_input": {"command": command}})
    done = subprocess.run(["bash", str(HANDLER)], input=payload, capture_output=True, text=True)
    assert done.returncode == 0, done.stderr
    return json.loads(done.stdout)


class TheStagingWarning(unittest.TestCase):
    def test_it_warns_on_blanket_staging(self):
        for command in ("git add -A", "git add --all", "git add .", "cd x && git add . && git status"):
            with self.subTest(command=command):
                out = run(command)
                self.assertIn("/quenching-git commit", out["systemMessage"])
                self.assertEqual("PreToolUse", out["hookSpecificOutput"]["hookEventName"])
                self.assertNotIn("permissionDecision", out["hookSpecificOutput"])

    def test_it_stays_silent_on_everything_else(self):
        for command in ("git add file.py", "git add ./docs/a.md", "git add src/", "git status", "ls"):
            with self.subTest(command=command):
                self.assertEqual({}, run(command))

    def test_it_exits_zero_on_garbage(self):
        done = subprocess.run(["bash", str(HANDLER)], input="{garbage", capture_output=True, text=True)
        self.assertEqual(0, done.returncode)
        self.assertEqual({}, json.loads(done.stdout))


if __name__ == "__main__":
    unittest.main()
