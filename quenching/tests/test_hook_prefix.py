"""The deployed hook line answers as a pure function of the event, so the prompt prefix stays stable.

The line the deploy writes is part of the answer: a dispatcher found relative to the caller's
working directory answers the same command differently from a subdirectory and from the root. The
tests below start the real installed line, from the source's own `dispatch_command`, against a
throwaway target, and demand the same bytes from every directory of the project, under different
hash seeds and timezones, with no per-call token in the answer. The live prompt-cache measurement
is the VS Code cache explorer, recorded in the spec's `prompt-prefix.md` artifact.
"""

import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

PLUGIN_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PLUGIN_ROOT / "assets" / "bin"))

from quenching.deploy import settings  # noqa: E402

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import _paths  # noqa: E402,F401

BODIES = ("deny-claude-coauthor", "warn-git-add-all")
HOOKS = PLUGIN_ROOT / "assets" / "hooks"
MATCHING = {
    "coauthor": json.dumps({"tool_name": "Bash", "tool_input": {
        "command": 'git commit -m x -m "Co-Authored-By: Claude <noreply@anthropic.com>"'}}),
    "blanket": json.dumps({"tool_name": "Bash", "tool_input": {"command": "git add -A"}}),
    "bypass": json.dumps({"tool_name": "Bash", "tool_input": {"command": "git commit --no-verify -m wip"}}),
    "both": json.dumps({"tool_name": "Bash", "tool_input": {
        "command": "git add . && git commit --no-verify -m wip"}}),
}
QUIET = json.dumps({"tool_name": "Bash", "tool_input": {"command": "git status"}})
# The volatile shapes a hook answer must never carry: a clock reading, an absolute path of this
# machine, a process id, a call id and an ANSI escape. `/quenching-git` is a command, not a path.
VOLATILE = re.compile(r"\d{4}-\d{2}-\d{2}T|/home/|/Users/|/tmp/|[A-Za-z]:\\\\|pid[=: ]\d+"
                      r"|[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}|\x1b\[")


class HookPrefix(unittest.TestCase):
    """One real deployed line, started the way the harness starts it."""

    def setUp(self):
        self.tmp = pathlib.Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.target = self.tmp / "project"
        (self.target / ".agents" / "quenching" / "assets" / "hooks").mkdir(parents=True)
        for name in ("dispatch", *BODIES):
            shutil.copy(HOOKS / f"{name}.py", self.target / ".agents" / "quenching" / "assets" / "hooks")
        subprocess.run(["git", "-C", str(self.target), "init", "-q"], check=True,
                       capture_output=True)
        self.command = settings.dispatch_command(list(BODIES), prefix=[sys.executable])

    def env(self, **overrides):
        env = {key: value for key, value in os.environ.items()
               if key not in ("CLAUDE_PROJECT_DIR", "COPILOT_PROJECT_DIR")}
        env.update(overrides)
        return env

    def run_it(self, raw, cwd=None, **env):
        done = subprocess.run(self.command, shell=True, cwd=cwd or self.target, input=raw,
                              capture_output=True, text=True, env=self.env(**env))
        self.assertEqual(0, done.returncode, done.stderr)
        return done.stdout

    def test_the_same_event_answers_the_same_bytes_from_a_subdirectory(self):
        nested = self.target / "quenching" / "tests"
        nested.mkdir(parents=True)
        for name, raw in MATCHING.items():
            with self.subTest(payload=name):
                root = self.run_it(raw)
                below = self.run_it(raw, cwd=nested)
                self.assertEqual(root, below)
                self.assertIn("hookSpecificOutput", json.loads(root))

    def test_the_answer_does_not_change_with_hash_seed_or_timezone(self):
        for name, raw in MATCHING.items():
            with self.subTest(payload=name):
                first = self.run_it(raw, PYTHONHASHSEED="0", TZ="UTC")
                second = self.run_it(raw, PYTHONHASHSEED="1", TZ="America/Sao_Paulo")
                self.assertEqual(first, second)

    def test_the_answer_carries_no_per_call_token(self):
        for name, raw in MATCHING.items():
            with self.subTest(payload=name):
                answer = self.run_it(raw)
                self.assertIsNone(VOLATILE.search(answer), answer)
                self.assertEqual(answer, self.run_it(raw))

    def test_the_rules_keep_their_declared_order(self):
        answer = json.loads(self.run_it(MATCHING["both"]))
        message = answer["systemMessage"]
        self.assertLess(message.index("git add -A"), message.index("skips the repository"))

    def test_a_foreign_dispatcher_above_the_project_is_never_used(self):
        outer = self.tmp / "outer" / ".agents" / "quenching" / "assets" / "hooks"
        outer.mkdir(parents=True)
        (outer / "dispatch.py").write_text('print(\'{"systemMessage": "FOREIGN"}\')', encoding="utf-8")
        project = self.tmp / "outer" / "project"
        project.mkdir()
        self.assertEqual("{}\n", self.run_it(MATCHING["blanket"], cwd=project))
        (project / ".git").write_text("gitdir: elsewhere\n", encoding="utf-8")
        self.assertEqual("{}\n", self.run_it(MATCHING["blanket"], cwd=project))

    def test_the_absence_guard_answers_empty_and_exits_zero(self):
        outside = self.tmp / "outside"
        outside.mkdir()
        self.assertEqual("{}\n", self.run_it(QUIET, cwd=outside))
        self.assertEqual("{}\n", self.run_it(QUIET))


if __name__ == "__main__":
    unittest.main()
