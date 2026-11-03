"""`quenching.session.live` — fixed fields only, against synthetic fixtures."""
from __future__ import annotations

import json
import contextlib
import io
import os
import tempfile
import unittest
from types import SimpleNamespace
from unittest import mock
from datetime import datetime, timedelta, timezone
from pathlib import Path

import _paths  # noqa: F401  — must precede the `quenching` import; see its docstring
from quenching.session.commands.live import cmd_live
from quenching.session import live
from quenching.session.live import read_live
from quenching.session.transcript import encode_cwd

NOW = datetime(2026, 10, 16, 12, 0, 0, tzinfo=timezone.utc)
SECRET = "SECRET-TOKEN-do-not-leak"
FIELDS = {"sessionId", "pid", "cwd", "status", "statusSince", "lastEvent", "state",
          "pendingQuestion", "pendingTool", "subagents", "activity", "unparsed"}


def _ts(minutes_ago):
    return (NOW - timedelta(minutes=minutes_ago)).strftime("%Y-%m-%dT%H:%M:%S.000Z")


def _write(path, lines):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(row if isinstance(row, str) else json.dumps(row) for row in lines) + "\n")


class LiveTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.repo = "/work/repo.one"
        self.other = "/elsewhere/repo"

    def _session(self, pid, sid, cwd, status, events, extra=None):
        info = {"pid": pid, "sessionId": sid, "cwd": cwd, "status": status,
                "statusUpdatedAt": int((NOW - timedelta(minutes=2)).timestamp() * 1000),
                "messagingSocketPath": "/tmp/" + SECRET, "name": SECRET}
        _write(self.root / "sessions" / f"{pid}.json", [info])
        (self.root / "sessions" / f"{pid}.{SECRET}.key").write_text(SECRET)
        _write(self.root / "projects" / encode_cwd(cwd) / f"{sid}.jsonl", events)

    def _read(self, **kw):
        return read_live(self.root, now=NOW, alive=lambda pid: pid != 9, **kw)

    def test_fields_are_fixed_and_secrets_never_surface(self):
        self._session(1, "s1", self.repo, "busy", [
            {"type": "user", "timestamp": _ts(3), "message": {"content": SECRET}},
            {"type": "assistant", "timestamp": _ts(1), "message": {"content": [
                {"type": "tool_use", "id": "t1", "name": "Bash",
                 "input": {"command": SECRET}}]}},
            "not json " + SECRET,
        ])
        out = self._read()
        self.assertEqual(set(out), {"generatedAt", "windowMinutes", "sessions"})
        (row,) = out["sessions"]
        self.assertEqual(set(row), FIELDS)
        self.assertEqual((row["state"], row["unparsed"], row["lastEvent"]),
                         ("busy", 1, "2026-10-16T11:59:00Z"))
        self.assertNotIn(SECRET, json.dumps(out))
        for word in ("messagingSocketPath", "tool_result", "input"):
            self.assertNotIn(word, json.dumps(out))

    def test_pending_question_waits_until_a_result_arrives(self):
        ask = {"type": "assistant", "timestamp": _ts(5), "message": {"content": [
            {"type": "tool_use", "id": "q1", "name": "AskUserQuestion",
             "input": {"questions": [{"question": "Which one?", "options": [SECRET]}]}}]}}
        self._session(1, "s1", self.repo, "idle", [ask])
        (row,) = self._read()["sessions"]
        self.assertEqual((row["state"], row["pendingQuestion"]), ("waiting", "Which one?"))
        self.assertEqual(row["pendingTool"], "AskUserQuestion")
        self.assertNotIn(SECRET, json.dumps(row))
        answer = {"type": "user", "timestamp": _ts(4), "message": {"content": [
            {"type": "tool_result", "tool_use_id": "q1", "content": SECRET}]}}
        self._session(1, "s1", self.repo, "idle", [ask, answer])
        (row,) = self._read()["sessions"]
        self.assertEqual((row["state"], row["pendingQuestion"]), ("idle", None))
        self.assertIsNone(row["pendingTool"])

    def test_plan_approval_is_pending_as_plan(self):
        self._session(1, "s1", self.repo, "idle", [
            {"type": "assistant", "timestamp": _ts(1), "message": {"content": [
                {"type": "tool_use", "id": "p1", "name": "ExitPlanMode",
                 "input": {"plan": SECRET}}]}}])
        (row,) = self._read()["sessions"]
        self.assertEqual((row["state"], row["pendingQuestion"]), ("waiting", "plan"))
        self.assertEqual(row["pendingTool"], "ExitPlanMode")

    def test_activity_is_per_minute_oldest_first(self):
        self._session(1, "s1", self.repo, "busy", [
            {"type": "user", "timestamp": _ts(0.5)}, {"type": "assistant", "timestamp": _ts(0.2)},
            {"type": "user", "timestamp": _ts(10.5)}, {"type": "user", "timestamp": _ts(90)}])
        act = self._read()["sessions"][0]["activity"]
        self.assertEqual(len(act), 60)
        self.assertEqual((act[59], act[49], sum(act)), (2, 1, 3))

    def test_subagents_type_window_and_active(self):
        self._session(1, "s1", self.repo, "busy", [{"type": "user", "timestamp": _ts(1)}])
        sub = self.root / "projects" / encode_cwd(self.repo) / "s1" / "subagents"
        _write(sub / "agent-a.jsonl", [{"type": "assistant", "timestamp": _ts(20)},
                                       {"type": "assistant", "timestamp": _ts(0.5)}])
        (sub / "agent-a.meta.json").write_text(json.dumps({"agentType": "x:y", "model": SECRET}))
        _write(sub / "agent-old.jsonl", [{"type": "assistant", "timestamp": _ts(300)}])
        (row,) = self._read()["sessions"]
        self.assertEqual(row["subagents"], [{"agentType": "x:y", "start": "2026-10-16T11:40:00Z",
                                             "end": "2026-10-16T11:59:30Z", "active": True}])
        self.assertNotIn(SECRET, json.dumps(row))

    def test_dead_pid_is_skipped_and_cwd_filter_keeps_the_repository(self):
        self._session(9, "dead", self.repo, "idle", [])
        self._session(1, "s1", self.repo, "idle", [])
        self._session(2, "s2", self.other, "idle", [])
        self.assertEqual({r["sessionId"] for r in self._read()["sessions"]}, {"s1", "s2"})
        kept = self._read(cwds=[self.repo])["sessions"]
        self.assertEqual([r["sessionId"] for r in kept], ["s1"])

    def test_structured_identity_fields_drop_the_record_and_never_leak(self):
        self._session(1, "s1", self.repo, "idle", [])
        bad = {"sessionId": {"messagingSocketPath": SECRET}, "cwd": self.repo, "status": "idle"}
        for pid, patch in ((2, {"pid": 2}), (3, {"pid": 3, "cwd": [SECRET], "sessionId": "x"}),
                           (4, {"pid": True, "sessionId": "x", "cwd": self.repo}),
                           (5, {"pid": "5", "sessionId": "x", "cwd": self.repo})):
            _write(self.root / "sessions" / f"{pid}.json", [{**bad, **patch}])
        out = self._read()
        self.assertEqual([r["sessionId"] for r in out["sessions"]], ["s1"])
        self.assertNotIn(SECRET, json.dumps(out))

    def test_out_of_range_timestamp_becomes_null_and_keeps_other_sessions(self):
        self._session(1, "good", self.repo, "idle", [])
        for pid, value in ((2, 253402300800000), (3, 1e30), (4, float("inf")),
                           (5, float("nan")), (6, True)):
            _write(self.root / "sessions" / f"{pid}.json", [{
                "pid": pid, "sessionId": f"s{pid}", "cwd": self.repo, "status": "idle",
                "statusUpdatedAt": value}])
        rows = {r["sessionId"]: r for r in self._read()["sessions"]}
        self.assertEqual(len(rows), 6)
        self.assertIsNotNone(rows["good"]["statusSince"])
        for sid in ("s2", "s3", "s4", "s5", "s6"):
            self.assertIsNone(rows[sid]["statusSince"])

    def test_no_sessions_is_an_empty_result(self):
        (self.root / "sessions").mkdir()
        self.assertEqual(self._read()["sessions"], [])

    def test_transcripts_derive_from_the_configured_claude_root(self):
        waiting = [{"type": "assistant", "timestamp": _ts(1), "message": {"content": [
            {"type": "tool_use", "id": "q", "name": "AskUserQuestion",
             "input": {"questions": [{"question": "Pick?"}]}}]}}]
        self._session(os.getpid(), "s1", self.repo, "busy", waiting)
        elsewhere = self.root / "elsewhere"
        elsewhere.mkdir()

        def run(env):
            with mock.patch.dict(os.environ, env), contextlib.redirect_stdout(io.StringIO()) as out:
                self.assertEqual(cmd_live(SimpleNamespace(json=True, cwd=None)), 0)
            return json.loads(out.getvalue())["sessions"][0]

        only_root = {"QUENCHING_CLAUDE_ROOT": str(self.root)}
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("QUENCHING_TRANSCRIPTS_ROOT", None)
            self.assertEqual(run(only_root)["pendingQuestion"], "Pick?")
        explicit = {**only_root, "QUENCHING_TRANSCRIPTS_ROOT": str(elsewhere)}
        self.assertIsNone(run(explicit)["pendingQuestion"])


if __name__ == "__main__":
    unittest.main()


class AliveWindows(unittest.TestCase):
    """`_alive_nt` sem tocar em kernel32: uma API falsa decide cada desfecho."""

    class Api:
        def __init__(self, handle=7, code=259, error=0):
            self.handle, self.code, self.error = handle, code, error
            self.closed = []

        def open(self, pid):
            return self.handle

        def exit_code(self, handle):
            return self.code

        def close(self, handle):
            self.closed.append(handle)

        def last_error(self):
            return self.error

    def test_processo_vivo_quando_o_codigo_e_still_active(self):
        api = self.Api(code=259)
        self.assertTrue(live._alive_nt(123, api))  # noqa: SLF001
        self.assertEqual(api.closed, [7])

    def test_processo_morto_quando_o_codigo_ja_saiu(self):
        self.assertFalse(live._alive_nt(123, self.Api(code=0)))  # noqa: SLF001

    def test_acesso_negado_conta_como_vivo(self):
        self.assertTrue(live._alive_nt(123, self.Api(handle=0, error=5)))  # noqa: SLF001

    def test_outro_erro_ao_abrir_conta_como_morto(self):
        self.assertFalse(live._alive_nt(123, self.Api(handle=0, error=87)))  # noqa: SLF001

    def test_falha_ao_ler_o_codigo_conta_como_vivo(self):
        self.assertTrue(live._alive_nt(123, self.Api(code=None)))  # noqa: SLF001
