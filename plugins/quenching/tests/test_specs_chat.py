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
from quenching.specs import backends as backends_mod
from quenching.specs import chat as chat_mod
from quenching.specs import portal as portal_mod
from quenching.specs.backends.memory import MemoryBackend

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


TOKEN = "t0ken"
PORT = 4321
HOST = {"Host": f"127.0.0.1:{PORT}"}
AUTH = {**HOST, "X-Quenching-Token": TOKEN}
ORIGIN = {"Origin": f"http://127.0.0.1:{PORT}"}
JSON = {**AUTH, **ORIGIN, "Content-Type": "application/json"}


class ThePortalRoutes(unittest.TestCase):
    read_only = False

    def setUp(self):
        self.claude, self.log = install_fake(self)
        self.root = os.path.realpath(tempfile.mkdtemp(prefix="quenching-chat-root-"))
        self.addCleanup(shutil.rmtree, self.root, True)
        backends_mod._BACKEND_CACHE.clear()
        backends_mod._BACKEND_CACHE[self.root] = MemoryBackend()
        self.addCleanup(backends_mod._BACKEND_CACHE.clear)
        chat, refusal = portal_mod.chat_source(True, None)
        self.assertIsNone(refusal)
        self.portal = portal_mod.Portal(self.root, TOKEN, self.read_only, "127.0.0.1", PORT,
                                        chat=chat)

    def call(self, method, target, headers, data=None, portal=None):
        body = json.dumps(data).encode() if data is not None else b""
        status, _, out = (portal or self.portal).handle(method, target, headers, body)
        return status, json.loads(out)

    def ask(self, data=None, headers=JSON):
        return self.call("POST", "/api/chat", headers, data or {"question": "what is ready?"})

    def poll(self, job):
        end = time.time() + 10
        events, after = [], 0
        while time.time() < end:
            status, body = self.call("GET", f"/api/chat/{job}?after={after}", AUTH)
            self.assertEqual(200, status, body)
            events += body["events"]
            after = body["next"]
            if body["status"] != "running":
                return body, events
            time.sleep(0.05)
        self.fail("the chat job never finished")

    def test_config_reports_the_chat_and_its_budget(self):
        status, body = self.call("GET", "/api/config", AUTH)
        self.assertEqual((True, 0.5), (body["chat"], body["chatBudgetUsd"]))

    def test_a_question_is_a_job_polled_to_done_without_raw_tool_data(self):
        status, body = self.ask()
        self.assertEqual(202, status, body)
        self.assertEqual(self.root, body["worktree"])
        final, events = self.poll(body["job"])
        self.assertEqual("done", final["status"])
        self.assertEqual(["text", "tool", "result"], [e["kind"] for e in events])
        self.assertNotIn("RAW TOOL RESULT", json.dumps(events))
        self.assertEqual(self.root, os.path.realpath(
            json.loads(pathlib.Path(self.log).read_text())["cwd"]))

    def test_a_post_without_origin_is_refused(self):
        headers = {k: v for k, v in JSON.items() if k != "Origin"}
        status, body = self.ask(headers=headers)
        self.assertEqual((403, "sp-portal-bad-origin"), (status, body["code"]))
        self.assertFalse(os.path.exists(self.log))

    def test_a_foreign_origin_and_a_missing_token_are_refused(self):
        status, body = self.ask(headers={**JSON, "Origin": "http://evil.example"})
        self.assertEqual((403, "sp-portal-bad-origin"), (status, body["code"]))
        headers = {k: v for k, v in JSON.items() if k != "X-Quenching-Token"}
        status, body = self.ask(headers=headers)
        self.assertEqual((401, "sp-portal-token"), (status, body["code"]))
        self.assertFalse(os.path.exists(self.log))

    def test_a_worktree_outside_the_project_is_refused(self):
        status, body = self.ask({"question": "q", "worktree": "/"})
        self.assertEqual((400, "sp-portal-chat-worktree"), (status, body["code"]))

    def test_an_empty_or_long_question_is_refused(self):
        for question in ("  ", "x" * (chat_mod.MAX_QUESTION + 1), 3):
            status, body = self.ask({"question": question})
            self.assertEqual((400, "sp-portal-bad-input"), (status, body["code"]))

    def test_a_second_question_while_one_runs_is_busy(self):
        with mock.patch.dict(os.environ, {"FAKE_CLAUDE_MODE": "sleep"}):
            status, body = self.ask()
            self.assertEqual(202, status)
            job = self.portal.jobs[body["job"]]
            self.addCleanup(lambda: (job.proc.kill(), job.thread.join(5)))
            status, body = self.ask()
        self.assertEqual((409, "sp-portal-chat-busy"), (status, body["code"]))

    def test_an_unknown_job_is_404(self):
        status, body = self.call("GET", "/api/chat/nope", AUTH)
        self.assertEqual((404, "sp-portal-chat-unknown-job"), (status, body["code"]))

    def test_without_chat_the_routes_do_not_exist(self):
        off = portal_mod.Portal(self.root, TOKEN, False, "127.0.0.1", PORT)
        status, body = self.call("POST", "/api/chat", JSON, {"question": "q"}, portal=off)
        self.assertEqual((404, "sp-portal-not-found"), (status, body["code"]))
        self.assertEqual(404, self.call("GET", "/api/chat/x", AUTH, portal=off)[0])
        self.assertFalse(self.call("GET", "/api/config", AUTH, portal=off)[1]["chat"])

    def test_chat_needs_no_store_write_but_read_only_keeps_the_other_posts_closed(self):
        ro = portal_mod.Portal(self.root, TOKEN, True, "127.0.0.1", PORT, chat=self.portal.chat)
        status, body = self.call("POST", "/api/chat", JSON, {"question": "q"}, portal=ro)
        self.assertEqual(202, status, body)
        self.poll_on(ro, body["job"])
        status, body = self.call("POST", "/api/capture", JSON, {"title": "t", "problem": "p"},
                                 portal=ro)
        self.assertEqual((403, "sp-read-only"), (status, body["code"]))

    def poll_on(self, portal, job):
        wait(portal.jobs[job])


class TheChatSource(unittest.TestCase):
    def test_off_is_none_and_no_refusal(self):
        self.assertEqual((None, None), portal_mod.chat_source(False, None))

    def test_a_non_positive_budget_is_refused(self):
        for budget in (0, -1.0):
            chat, refusal = portal_mod.chat_source(True, budget)
            self.assertEqual("sp-portal-chat-budget", refusal["code"])

    def test_no_claude_on_path_is_refused(self):
        with mock.patch.object(chat_mod.shutil, "which", return_value=None):
            chat, refusal = portal_mod.chat_source(True, None)
        self.assertEqual("sp-portal-chat-unavailable", refusal["code"])

    def test_the_given_budget_is_kept(self):
        with mock.patch.object(chat_mod.shutil, "which", return_value="/bin/claude"):
            chat, _ = portal_mod.chat_source(True, 1.5)
        self.assertEqual({"claude": "/bin/claude", "budget": 1.5, "worktrees": None}, chat)


if __name__ == "__main__":
    unittest.main()
