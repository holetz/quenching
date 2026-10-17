"""The portal chat job, against a fake `claude` on PATH: the exact argv, the deny file, the
question on stdin, the projection that drops tool results and inputs, failure and timeout."""

import json
import os
import pathlib
import shutil
import stat
import sys
import tempfile
import time
import unittest
from unittest import mock

try:
    import _paths  # noqa: F401  — must precede the `quenching` import
except ModuleNotFoundError:
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    import _paths  # noqa: F401
from quenching.specs import chat as chat_mod

FAKE = """#!{python}
import json, os, sys, time
args = sys.argv[1:]
settings = args[args.index("--settings") + 1]
log = {{"argv": args, "cwd": os.getcwd(), "stdin": sys.stdin.read(),
        "settings": json.load(open(settings)),
        "mode": oct(os.stat(settings).st_mode & 0o777)}}
json.dump(log, open(os.environ["FAKE_CLAUDE_LOG"], "w"))
mode = os.environ.get("FAKE_CLAUDE_MODE", "ok")
if mode == "sleep":
    time.sleep(30)
if mode == "fail":
    sys.stderr.write("error: unknown option '--tools'\\n")
    sys.exit(1)
lines = [
    {{"type": "system", "subtype": "init", "cwd": os.getcwd(), "tools": ["Read"]}},
    {{"type": "assistant", "message": {{"content": [
        {{"type": "text", "text": "Looking."}},
        {{"type": "tool_use", "name": "Read", "input": {{"file_path": "/secret/input"}}}}]}}}},
    {{"type": "user", "message": {{"content": [
        {{"type": "tool_result", "content": "RAW TOOL RESULT"}}]}}}},
    "not json",
    {{"type": "result", "result": "Spec 1 is ready.", "total_cost_usd": 0.012,
      "is_error": False}},
]
for line in lines:
    print(line if isinstance(line, str) else json.dumps(line), flush=True)
"""


def install_fake(test: unittest.TestCase) -> tuple[str, str]:
    """A fake `claude` first on PATH; returns (its path, the log file it writes)."""
    bindir = tempfile.mkdtemp(prefix="quenching-fake-claude-")
    test.addCleanup(shutil.rmtree, bindir, True)
    claude = os.path.join(bindir, "claude")
    with open(claude, "w") as handle:
        handle.write(FAKE.format(python=sys.executable))
    os.chmod(claude, os.stat(claude).st_mode | stat.S_IXUSR)
    log = os.path.join(bindir, "log.json")
    patch = mock.patch.dict(os.environ, {"PATH": bindir + os.pathsep + os.environ["PATH"],
                                         "FAKE_CLAUDE_LOG": log})
    patch.start()
    test.addCleanup(patch.stop)
    return claude, log


def wait(job, seconds: float = 10.0):
    end = time.time() + seconds
    while job.running and time.time() < end:
        time.sleep(0.02)
    job.thread.join(5)
    return job


EXPECTED_ARGV = ["-p", "--model", "sonnet", "--output-format", "stream-json", "--verbose",
                 "--tools", "Read,Grep,Glob", "--strict-mcp-config",
                 "--no-session-persistence", "--disable-slash-commands",
                 "--permission-mode", "dontAsk", "--setting-sources", "project",
                 "--max-budget-usd"]


class TheJob(unittest.TestCase):
    def setUp(self):
        self.claude, self.log = install_fake(self)
        self.cwd = tempfile.mkdtemp(prefix="quenching-chat-tree-")
        self.addCleanup(shutil.rmtree, self.cwd, True)

    def logged(self) -> dict:
        return json.loads(pathlib.Path(self.log).read_text())

    def test_the_fake_is_the_claude_on_path(self):
        self.assertEqual(self.claude, chat_mod.find_claude())

    def test_argv_is_exact_and_the_question_goes_through_stdin(self):
        job = wait(chat_mod.Job(chat_mod.find_claude(), 0.5, self.cwd, "--evil what is 1815?"))
        log = self.logged()
        self.assertEqual(EXPECTED_ARGV + ["0.5", "--settings"], log["argv"][:-1])
        self.assertEqual("--evil what is 1815?", log["stdin"])
        self.assertNotIn("--evil what is 1815?", log["argv"])
        self.assertEqual(os.path.realpath(self.cwd), os.path.realpath(log["cwd"]))
        self.assertEqual("done", job.status)

    def test_the_budget_is_passed_through(self):
        wait(chat_mod.Job(self.claude, 1.25, self.cwd, "q"))
        argv = self.logged()["argv"]
        self.assertEqual("1.25", argv[argv.index("--max-budget-usd") + 1])

    def test_the_deny_file_denies_the_secrets_disables_hooks_and_is_removed(self):
        job = wait(chat_mod.Job(self.claude, 0.5, self.cwd, "q"))
        log = self.logged()
        self.assertEqual({"permissions": {"deny": [
            "Read(~/.ssh/**)", "Read(~/.config/**)", "Read(**/*.key)", "Read(**/.env)"]},
            "disableAllHooks": True}, log["settings"])
        self.assertEqual("0o600", log["mode"])
        self.assertFalse(os.path.exists(job.settings))

    def test_the_view_carries_text_tool_names_and_result_only(self):
        job = wait(chat_mod.Job(self.claude, 0.5, self.cwd, "q"))
        view = job.view()
        self.assertEqual([{"kind": "text", "text": "Looking."}, {"kind": "tool", "name": "Read"},
                          {"kind": "result", "text": "Spec 1 is ready.", "costUsd": 0.012,
                           "isError": False}], view["events"])
        self.assertEqual(0.012, view["costUsd"])
        dumped = json.dumps(view)
        self.assertNotIn("RAW TOOL RESULT", dumped)
        self.assertNotIn("/secret/input", dumped)
        self.assertEqual(3, view["next"])
        self.assertEqual(["result"], [e["kind"] for e in job.view(after=2)["events"]])
        self.assertEqual([], job.view(after=99)["events"])

    def test_a_failing_claude_is_failed_with_its_last_stderr_line(self):
        with mock.patch.dict(os.environ, {"FAKE_CLAUDE_MODE": "fail"}):
            job = wait(chat_mod.Job(self.claude, 0.5, self.cwd, "q"))
        self.assertEqual("failed", job.status)
        self.assertIn("unknown option", job.error)

    def test_the_timeout_kills_the_process(self):
        with mock.patch.dict(os.environ, {"FAKE_CLAUDE_MODE": "sleep"}):
            job = wait(chat_mod.Job(self.claude, 0.5, self.cwd, "q", timeout=0.5))
        self.assertEqual("timeout", job.status)
        self.assertIsNotNone(job.proc.poll())
        self.assertFalse(os.path.exists(job.settings))

    def test_a_missing_binary_is_failed_without_a_settings_file_left(self):
        job = chat_mod.Job(os.path.join(self.cwd, "nope"), 0.5, self.cwd, "q")
        self.assertEqual("failed", job.status)
        self.assertFalse(os.path.exists(job.settings))


if __name__ == "__main__":
    unittest.main()
