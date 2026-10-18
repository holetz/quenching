"""`deny-claude-coauthor.sh` — the plugin-wide PreToolUse hook that keeps Claude off commit and PR messages.

It runs on every Bash call in every repo that enables `quenching-specs`, so both halves matter: it
denies exactly the message-writing commands that carry the attribution, and it prints `{}` for
everything else — including a malformed input, since a crashed guard must never block a session.
"""

import json
import os
import pathlib
import subprocess
import unittest

PLUGIN_ROOT = pathlib.Path(__file__).resolve().parent.parent
HANDLER = PLUGIN_ROOT / "assets" / "hooks" / "deny-claude-coauthor.sh"
WIRING = PLUGIN_ROOT / "hooks" / "hooks.json"


def run(command, raw=None, **env):
    payload = raw if raw is not None else json.dumps({"tool_name": "Bash", "tool_input": {"command": command}})
    done = subprocess.run(["bash", str(HANDLER)], input=payload, capture_output=True, text=True,
                          env={**os.environ, "QUENCHING_ALLOW_CLAUDE_COAUTHOR": "", **env})
    assert done.returncode == 0, done.stderr
    return json.loads(done.stdout)


def denied(out):
    return out.get("hookSpecificOutput", {}).get("permissionDecision") == "deny"


class TheCoauthorHook(unittest.TestCase):
    def test_it_denies_the_attribution_on_message_writing_commands(self):
        for command in (
            'git commit -m "$(cat <<\'EOF\'\nfeat: x\n\nCo-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>\nEOF\n)"',
            'git -C repo commit -m "fix" -m "Co-authored-by: Claude <noreply@anthropic.com>"',
            'gh pr create --title t --body "x\n\n🤖 Generated with [Claude Code](https://claude.com/claude-code)"',
            'cq git commit --subject "x\n\nCo-Authored-By: Claude <noreply@anthropic.com>"',
        ):
            with self.subTest(command=command):
                self.assertTrue(denied(run(command)))

    def test_it_lets_everything_else_through(self):
        for command in ('git commit -m "feat: y"',
                        'git commit -m y -m "Co-Authored-By: Maria <maria@example.com>"',
                        'grep -rn "Co-Authored-By: Claude" docs', "ls"):
            with self.subTest(command=command):
                self.assertEqual({}, run(command))

    def test_it_fails_open_and_honours_the_opt_out(self):
        self.assertEqual({}, run(None, raw="{garbage co-authored-by"))
        self.assertEqual({}, run('git commit -m x -m "Co-Authored-By: Claude <noreply@anthropic.com>"',
                                 QUENCHING_ALLOW_CLAUDE_COAUTHOR="1"))

    def test_the_wiring_points_at_the_handler_behind_its_guard(self):
        hook = json.loads(WIRING.read_text())["hooks"]["PreToolUse"][0]
        self.assertEqual("Bash", hook["matcher"])
        command = hook["hooks"][0]["command"]
        self.assertTrue(command.startswith('test -f "${CLAUDE_PLUGIN_ROOT}/assets/hooks/deny-claude-coauthor.sh" || exit 0;'))
        self.assertIn("timeout", hook["hooks"][0])


if __name__ == "__main__":
    unittest.main()
