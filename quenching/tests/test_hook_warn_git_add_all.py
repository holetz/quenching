"""`warn-git-add-all.py` — the PreToolUse guard that flags blanket staging without ever blocking."""

import json
import pathlib
import subprocess
import sys
import unittest

PLUGIN_ROOT = pathlib.Path(__file__).resolve().parent.parent
HANDLER = PLUGIN_ROOT / "assets" / "hooks" / "warn-git-add-all.py"


def run(command):
    payload = json.dumps({"tool_name": "Bash", "tool_input": {"command": command}})
    done = subprocess.run([sys.executable, str(HANDLER)], input=payload, capture_output=True, text=True)
    assert done.returncode == 0, done.stderr
    return json.loads(done.stdout)


class TheStagingWarning(unittest.TestCase):
    def test_it_warns_on_blanket_staging(self):
        for command in ("git add -A", "git add --all", "git add .", "cd x && git add . && git status",
                        "git -C repo add -A", "GIT_DIR=x git add --all", "true;git add .",
                        "make && git -c core.x=1 add . | cat", "ls\ngit add .",
                        "git commit -m 'a\nb' && git add -A"):
            with self.subTest(command=command):
                out = run(command)
                self.assertIn("/quenching-git commit", out["systemMessage"])
                self.assertEqual("PreToolUse", out["hookSpecificOutput"]["hookEventName"])
                self.assertNotIn("permissionDecision", out["hookSpecificOutput"])

    def test_it_stays_silent_on_everything_else(self):
        for command in ("git add file.py", "git add ./docs/a.md", "git add src/", "git status", "ls"):
            with self.subTest(command=command):
                self.assertEqual({}, run(command))

    def test_it_warns_when_a_command_skips_the_git_hooks(self):
        for command in ("git commit --no-verify -m wip", "git push --no-verify origin main",
                        "git commit -n -m wip", "git commit -n",
                        "git -c core.hooksPath=/dev/null commit -m wip"):
            with self.subTest(command=command):
                out = run(command)
                self.assertIn("skips the repository's git hooks", out["systemMessage"])
                self.assertIn("leak and identity gates", out["hookSpecificOutput"]["additionalContext"])
                self.assertNotIn("permissionDecision", out["hookSpecificOutput"])

    def test_both_rules_report_in_one_answer(self):
        out = run("git add . && git commit --no-verify -m wip")
        self.assertIn("/quenching-git commit", out["systemMessage"])
        self.assertIn("skips the repository's git hooks", out["systemMessage"])

    def test_lookalikes_of_the_bypass_stay_silent(self):
        for command in ("git push -n origin main", "git add -n .x", "git log --no-walk",
                        "git config core.hooksPath .agents/quenching/assets/githooks",
                        "echo no-verify"):
            with self.subTest(command=command):
                self.assertNotIn("skips", run(command).get("systemMessage", ""))

    def test_a_message_that_only_mentions_the_bypass_stays_silent(self):
        for command in ("git commit -m 'never use --no-verify'", 'echo "git commit -n"',
                        "git commit -m 'skip -n and core.hooksPath=x'"):
            with self.subTest(command=command):
                self.assertEqual({}, run(command))

    def test_it_stays_silent_on_text_that_only_mentions_it(self):
        for command in ('echo "git add ."', "printf 'never git add -A'",
                        "git commit -m 'stop using git add --all'",
                        "cat <<'EOF' > notes.md\nnever git add .\nEOF", "grep -r 'git add .' docs"):
            with self.subTest(command=command):
                self.assertEqual({}, run(command))

    def test_an_unparseable_command_keeps_the_regex_verdict(self):
        out = run("git add . 'unterminated")
        self.assertIn("/quenching-git commit", out["systemMessage"])

    def test_it_exits_zero_on_garbage(self):
        done = subprocess.run([sys.executable, str(HANDLER)], input="{garbage", capture_output=True, text=True)
        self.assertEqual(0, done.returncode)
        self.assertEqual({}, json.loads(done.stdout))


if __name__ == "__main__":
    unittest.main()
