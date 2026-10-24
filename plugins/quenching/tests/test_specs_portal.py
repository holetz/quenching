"""The local spec portal, offline: handlers over the memory fake, and the security gates."""

import json
import pathlib
import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from unittest import mock

try:
    import _paths  # noqa: F401  — must precede the `quenching` import
except ModuleNotFoundError:
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    import _paths  # noqa: F401
from quenching.common import lent as lent_mod
from quenching.specs import backends as backends_mod
from quenching.specs import portal as portal_mod
from quenching.specs.backends.base import BackendRefusal, SpecBackend
from quenching.specs.backends.memory import MemoryBackend

TOKEN = "t0ken"
PORT = 4321
HOST = {"Host": f"127.0.0.1:{PORT}"}
AUTH = {**HOST, "X-Quenching-Token": TOKEN}
ORIGIN = {"Origin": f"http://127.0.0.1:{PORT}"}
JSON = {**AUTH, **ORIGIN, "Content-Type": "application/json"}

READY = """---
title: {title}
date: 2026-01-01
tags: ["alpha"]
---

## Problem

Something is wrong.

## Tasks

- [x] 1. first
- [ ] 2. second
"""


class StaleMemory(MemoryBackend):
    """A memory store whose writes refuse like a CAS conflict."""
    def write_spec(self, info, text):
        raise BackendRefusal({"code": "sp-gh-stale-write", "exit": 2,
                              "message": "the issue changed after it was read"})


class PortalCase(unittest.TestCase):
    backend_cls = MemoryBackend
    read_only = False

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="quenching-portal-")
        self.addCleanup(__import__("shutil").rmtree, self.tmp, True)
        self.backend = self.backend_cls()
        backends_mod._BACKEND_CACHE.clear()
        backends_mod._BACKEND_CACHE[self.tmp] = self.backend
        self.addCleanup(backends_mod._BACKEND_CACHE.clear)
        for title in ("Alpha", "Beta", "Gamma"):
            self.backend.create_spec("plans", READY.format(title=title))
        self.portal = portal_mod.Portal(self.tmp, TOKEN, self.read_only, "127.0.0.1", PORT)

    def get(self, target, headers=AUTH):
        status, _, body = self.portal.handle("GET", target, headers)
        return status, json.loads(body)

    def post(self, route, data, headers=JSON):
        status, _, body = self.portal.handle("POST", f"/api/{route}", headers,
                                             json.dumps(data).encode())
        return status, json.loads(body)


class ChangeToken(PortalCase):
    def raw(self, target, headers=AUTH):
        return self.portal.handle("GET", target, headers)

    def test_list_reads_carry_an_etag_and_a_match_is_a_bodyless_304(self):
        for route in ("specs", "epics", "human"):
            status, hdrs, _ = self.raw(f"/api/{route}")
            self.assertEqual(status, 200)
            etag = hdrs["ETag"]
            status, hdrs, body = self.raw(f"/api/{route}", {**AUTH, "If-None-Match": etag})
            self.assertEqual((status, body, hdrs["ETag"]), (304, b"", etag))
            self.assertEqual(self.raw(f"/api/{route}", {**AUTH, "If-None-Match": '"x"'})[0], 200)

    def test_the_token_survives_a_snapshot_rebuild_and_moves_with_content(self):
        etag = self.raw("/api/specs")[1]["ETag"]
        again = self.raw("/api/specs?refresh=1")
        self.assertEqual(again[1]["ETag"], etag)
        self.backend.create_spec("plans", READY.format(title="Delta"))
        self.assertNotEqual(self.raw("/api/specs?refresh=1")[1]["ETag"], etag)

    def test_a_304_still_needs_the_token_and_the_host(self):
        etag = self.raw("/api/specs")[1]["ETag"]
        self.assertEqual(self.raw("/api/specs", {**HOST, "If-None-Match": etag})[0], 401)
        self.assertEqual(self.raw("/api/specs", {"Host": "evil:1", "X-Quenching-Token": TOKEN,
                                                 "If-None-Match": etag})[0], 403)


class Handlers(PortalCase):
    def test_list_is_lean_with_derived_stage_progress_and_rank(self):
        status, body = self.get("/api/specs")
        self.assertEqual(status, 200)
        self.assertEqual(body["count"], 3)
        row = body["specs"][0]
        self.assertEqual(row["title"], "Alpha")
        self.assertEqual(row["progress"], {"checked": 1, "blocked": 0, "total": 2})
        self.assertEqual(row["tags"], ["alpha"])
        self.assertIn(row["stage"], body["stages"])
        self.assertEqual(sorted(r["rank"] for r in body["specs"]), [1, 2, 3])

    def test_list_and_detail_carry_the_runner_record_field_by_field(self):
        text = READY.format(title="Ran").replace(
            "tags:", "run: {state: done, verifier: pass, date: 2026-10-17, note: leak}\ntags:")
        self.backend.create_spec("plans", text)
        _, body = self.get("/api/specs")
        ran = next(r for r in body["specs"] if r["title"] == "Ran")
        self.assertEqual(ran["run"], {"state": "done", "verifier": "pass", "date": "2026-10-17"})
        plain = next(r for r in body["specs"] if r["title"] == "Alpha")
        self.assertIsNone(plain["run"])
        _, detail = self.get(f"/api/specs/{ran['id']}")
        self.assertIn("run", [t["record"] for t in detail["timeline"]])

    def test_a_blocked_task_moves_the_spec_to_the_blocked_stage(self):
        text = READY.format(title="Stuck").replace("- [ ] 2. second", "- [!] 2. second — waits")
        self.backend.create_spec("plans", text)
        _, body = self.get("/api/specs")
        stuck = next(r for r in body["specs"] if r["title"] == "Stuck")
        self.assertEqual(stuck["progress"]["blocked"], 1)
        self.assertEqual(stuck["stage"], "blocked")
        self.assertIn("blocked", body["stages"])
        self.assertNotIn("blocked", [r["stage"] for r in body["specs"] if r["title"] != "Stuck"])

    def test_detail_carries_sections_tasks_and_records(self):
        status, body = self.get("/api/specs/1")
        self.assertEqual(status, 200)
        self.assertEqual(body["spec"]["title"], "Alpha")
        problem = next(s for s in body["sections"] if s["heading"] == "Problem")
        self.assertIn("Something is wrong", problem["body"])
        self.assertEqual(len(body["tasks"]), 2)
        self.assertEqual(body["executeCommand"], "/quenching-specs:specs:execute 1")
        self.assertEqual(self.get("/api/specs/99")[0], 404)

    def test_search_finds_text_in_any_section(self):
        status, body = self.get("/api/search?q=something+is+wrong")
        self.assertEqual((status, body["count"]), (200, 3))
        self.assertEqual(self.get("/api/search?q=zzzz")[1]["count"], 0)

    def test_epics_are_hidden_when_no_spec_is_an_epic(self):
        self.assertFalse(self.get("/api/epics")[1]["supported"])

    def test_epics_carry_waves_dependencies_and_critical_path(self):
        epic = """---
title: Program
date: 2026-01-01
workItemType: epic
---

## Tasks

### 1. First

- [ ] S1 One — spec: #1
- [ ] S2 Two — spec: #2 — after: S1

### 2. Second

- [ ] S3 Three — spec: #3 — after: S2
"""
        self.backend.create_spec("plans", epic)
        body = self.get("/api/epics")[1]
        self.assertTrue(body["supported"])
        row = body["epics"][0]
        self.assertEqual([i["label"] for i in row["items"]], ["S1", "S2", "S3"])
        self.assertEqual(row["items"][1]["after"], ["S1"])
        self.assertEqual(row["items"][1]["status"], "waiting")
        self.assertEqual([g["group"] for g in row["groups"]], [1, 2])
        self.assertEqual(row["criticalPath"], ["S1", "S2", "S3"])
        self.assertIsNone(row["cycle"])
        self.assertNotIn("member", row["items"][0])

    def test_epics_report_a_dependency_cycle(self):
        epic = """---
title: Loop
date: 2026-01-01
workItemType: epic
---

## Tasks

- [ ] S1 One — spec: #1 — after: S2
- [ ] S2 Two — spec: #2 — after: S1
"""
        self.backend.create_spec("plans", epic)
        row = self.get("/api/epics")[1]["epics"][0]
        self.assertTrue(row["cycle"])
        self.assertEqual(row["criticalPath"], [])

    def test_human_lists_epic_members_blocked_tasks_and_unapproved_ready(self):
        self.backend.create_spec("plans", READY.format(title="Member"))
        mid = self.get("/api/specs")[1]["specs"][-1]["id"]
        epic = f"""---
title: Autopilot - decidir com o humano
date: 2026-01-01
workItemType: epic
---

## Tasks

- [ ] S1 Decide it — spec: #{mid}
- [ ] S2 Loose item
"""
        self.backend.create_spec("plans", epic)
        other = """---
title: Program
date: 2026-01-01
---

## Tasks

- [ ] S1 Elsewhere — spec: #1
"""
        self.backend.create_spec("plans", other)
        blocked = READY.format(title="Stuck").replace(
            "- [ ] 2. second", "- [!] 2. second — blocked: needs a call")
        self.backend.create_spec("plans", blocked)
        status, body = self.get("/api/human?refresh=1")
        self.assertEqual(status, 200)
        self.assertEqual([m["label"] for m in body["epicMembers"]], ["S1", "S2"])
        self.assertEqual(body["epicMembers"][0]["id"], str(mid))
        self.assertEqual(len(body["blocked"]), 1)
        self.assertIn("needs a call", body["blocked"][0]["reasons"][0]["reason"])
        self.assertEqual(body["count"], len({str(m["id"]) for m in body["epicMembers"] if m["id"]}
                                            | {str(b["id"]) for b in body["blocked"]}
                                            | {str(a["id"]) for a in body["awaitingApproval"]}) + 1)

    def test_human_ignores_plain_specs_and_archived_epics_titled_like_the_mark(self):
        plain = """---
title: Painel decidir com o humano
date: 2026-01-01
---

## Tasks

- [ ] 1.1 Implement it
"""
        self.backend.create_spec("plans", plain)
        status, body = self.get("/api/human?refresh=1")
        self.assertEqual(status, 200)
        self.assertEqual(body["epicMembers"], [])
        self.assertEqual(body["count"], 0)

    def _remote_epic(self, title="Program"):
        self.backend.create_spec("plans", f"""---
title: {title}
date: 2026-01-01
workItemType: epic
---

## Tasks

- [ ] S1 Here — spec: #1
- [ ] S2 There — spec: holetz/quenching#7 — after: S1
- [ ] S3 Gone — spec: holetz/forge#9
""")

    def _remote_read(self, backend, keys, root):
        self.assertEqual(["holetz/forge#9", "holetz/quenching#7"], keys)
        local = self.backend.read_specs(["2"])["2"]
        foreign = dict(local, id=7, phase="archive",
                       frontmatter={**local["frontmatter"], "outcome": "done"})
        return {"holetz/quenching#7": foreign, "holetz/forge#9": None}, {"holetz/forge#9"}

    def test_epics_resolve_cross_repository_members_from_their_store(self):
        self._remote_epic()
        with mock.patch.object(portal_mod, "read_members", side_effect=self._remote_read):
            row = self.get("/api/epics?refresh=1")[1]["epics"][0]
        status = {i["label"]: i["status"] for i in row["items"]}
        self.assertEqual("done", status["S2"])
        self.assertEqual("unreadable", status["S3"])

    def test_epics_without_cross_repository_members_read_no_other_store(self):
        self.backend.create_spec("plans", """---
title: Program
date: 2026-01-01
workItemType: epic
---

## Tasks

- [ ] S1 Here — spec: #1
""")
        with mock.patch.object(portal_mod, "read_members") as reader:
            self.assertTrue(self.get("/api/epics?refresh=1")[1]["supported"])
        reader.assert_not_called()

    def test_human_lists_a_cross_repository_member_with_its_own_title_and_stage(self):
        self._remote_epic("Autopilot - decidir com o humano")
        with mock.patch.object(portal_mod, "read_members", side_effect=self._remote_read):
            body = self.get("/api/human?refresh=1")[1]
        by_label = {m["label"]: m for m in body["epicMembers"]}
        self.assertNotIn("S2", by_label)  # an archived foreign member is done
        self.assertEqual(("holetz/forge#9", "unreadable", "unreadable"),
                         (by_label["S3"]["id"], by_label["S3"]["stage"],
                          by_label["S3"]["status"]))

    def test_human_needs_the_token(self):
        status, _, _ = self.portal.handle("GET", "/api/human", HOST, b"")
        self.assertEqual(status, 401)

    def test_capture_creates_a_spec_through_the_cli_verb(self):
        status, body = self.post("capture", {"title": "Delta", "problem": "It hurts."})
        self.assertEqual(status, 200, body)
        self.assertTrue(body["ok"])
        self.assertEqual(len(self.backend.docs), 4)
        self.assertIn("It hurts.", self.backend.docs[4][1])

    def test_capture_without_a_problem_is_refused_and_writes_nothing(self):
        status, body = self.post("capture", {"title": "Delta"})
        self.assertEqual((status, body["code"]), (400, "sp-portal-bad-input"))
        self.assertEqual(len(self.backend.docs), 3)

    def test_section_edit_and_discovery(self):
        status, body = self.post("section", {"spec": 1, "heading": "Problem", "body": "New text."})
        self.assertEqual(status, 200, body)
        self.assertIn("New text.", self.backend.docs[1][1])
        status, body = self.post("discovery", {"spec": 1, "text": "found a thing"})
        self.assertEqual(status, 200, body)
        self.assertIn("- found a thing", self.backend.docs[1][1])

    def test_approve_records_a_human_and_is_write_once(self):
        # The ready gate is not met by a Problem-only document: refused, nothing written.
        status, body = self.post("approve", {"spec": 1})
        self.assertEqual((status, body["code"]), (422, "sp-portal-not-ready"))
        self.assertNotIn("approved", self.backend.docs[1][1])
        with mock.patch.object(portal_mod, "ready_report",
                               return_value={"ok": True, "missing": [], "malformed": []}):
            status, body = self.post("approve", {"spec": 1})
            self.assertEqual(status, 200, body)
            self.assertIn("by: human", self.backend.docs[1][1])
            status, body = self.post("approve", {"spec": 1})
        self.assertEqual((status, body["ok"]), (409, False))
        self.assertEqual(body["code"], "sp-record-write-once")

    def test_reorder_writes_priority_levels(self):
        status, body = self.post("reorder", {"order": [3, 1, 2]})
        self.assertEqual(status, 200, body)
        self.assertEqual(body["written"], 3)
        self.assertFalse(body["batched"])
        ranked = [r["id"] for r in sorted(self.get("/api/specs?refresh=1")[1]["specs"],
                                          key=lambda r: r["rank"])]
        self.assertEqual(ranked, [3, 1, 2])

    def test_reorder_uses_the_batch_helper_when_the_backend_has_one(self):
        calls = []
        self.backend.write_specs = lambda items: calls.append(len(items)) or [
            self.backend.write_spec(i, t) for i, t in items]
        status, body = self.post("reorder", {"order": [2, 3, 1]})
        self.assertEqual((status, body["batched"], calls), (200, True, [3]))

    def test_reorder_with_an_unknown_id_writes_nothing(self):
        status, body = self.post("reorder", {"order": [1, 99]})
        self.assertNotEqual(status, 200)
        self.assertFalse(body["ok"])
        self.assertNotIn("priority", self.backend.docs[1][1])

    def test_a_cas_conflict_is_an_error_with_its_code_never_a_success(self):
        stale = StaleMemory()
        stale.docs = dict(self.backend.docs)
        backends_mod._BACKEND_CACHE[self.tmp] = stale
        for route, data in (("section", {"spec": 1, "heading": "Problem", "body": "x"}),
                            ("discovery", {"spec": 1, "text": "x"}),
                            ("reorder", {"order": [2, 1]})):
            with self.subTest(route=route):
                status, body = self.post(route, data)
                self.assertEqual((status, body["ok"], body["code"]), (409, False,
                                                                       "sp-gh-stale-write"))


class Security(PortalCase):
    def test_missing_or_wrong_token_is_401_on_every_api_route(self):
        for route in ("specs", "specs/1", "search?q=a", "epics"):
            with self.subTest(route=route):
                self.assertEqual(self.portal.handle("GET", f"/api/{route}", HOST)[0], 401)
        self.assertEqual(self.portal.handle(
            "GET", "/api/specs", {**HOST, "X-Quenching-Token": "nope"})[0], 401)
        self.assertEqual(self.portal.handle("POST", "/api/capture", {**HOST, **ORIGIN}, b"{}")[0], 401)

    def test_the_query_token_is_never_accepted(self):
        self.assertEqual(self.portal.handle("GET", f"/api/specs?token={TOKEN}", HOST)[0], 401)
        self.assertEqual(self.portal.handle("GET", f"/?token={TOKEN}", HOST)[0], 401)

    def test_the_cookie_authenticates_reads_and_writes(self):
        jar = {**HOST, **ORIGIN, "Cookie": f"qtoken={TOKEN}", "Content-Type": "application/json"}
        self.assertEqual(self.portal.handle("GET", "/api/specs", jar)[0], 200)
        self.assertEqual(self.portal.handle("GET", "/", jar)[0], 200)
        self.assertEqual(self.portal.handle("POST", "/api/reorder", jar, b'{"order":[1]}')[0], 200)
        bad = {**jar, "Cookie": "qtoken=nope"}
        self.assertEqual(self.portal.handle("GET", "/api/specs", bad)[0], 401)

    def test_a_post_without_origin_is_refused_even_with_a_valid_token(self):
        headers = {**AUTH, "Content-Type": "application/json"}
        status, _, body = self.portal.handle("POST", "/api/reorder", headers, b'{"order":[1]}')
        self.assertEqual((status, json.loads(body)["code"]), (403, "sp-portal-bad-origin"))

    def test_the_nonce_trades_once_for_an_httponly_strict_cookie(self):
        nonce = self.portal.nonce
        status, headers, _ = self.portal.handle("GET", f"/?nonce={nonce}", HOST)
        self.assertEqual((status, headers["Location"]), (303, "/"))
        cookie = headers["Set-Cookie"]
        for part in (f"qtoken={TOKEN}", "HttpOnly", "SameSite=Strict", "Path=/"):
            self.assertIn(part, cookie)
        self.assertEqual(self.portal.handle("GET", f"/?nonce={nonce}", HOST)[0], 401)
        self.assertEqual(self.portal.handle("GET", "/?nonce=wrong", HOST)[0], 401)

    def test_the_client_keeps_no_token(self):
        js = (portal_mod.static_dir() / "app.js").read_text()
        for needle in ("X-Quenching-Token", "sessionStorage", "?token", 'get("token")'):
            self.assertNotIn(needle, js)

    def test_the_waiting_panel_shows_the_pending_tool_as_a_chip(self):
        js = (portal_mod.static_dir() / "app.js").read_text()
        self.assertIn('s.pendingTool ? h("span", { class: "chip" }, s.pendingTool) : null', js)

    def test_the_open_url_carries_the_nonce_and_never_the_token(self):
        server = portal_mod.make_server(self.tmp, token=TOKEN)
        self.addCleanup(server.server_close)
        args = mock.Mock(host="127.0.0.1", port=0, read_only=False, json=True, open=True)
        out = mock.Mock()
        opened = []
        with mock.patch.object(portal_mod, "make_server", return_value=server), \
                mock.patch("webbrowser.open", side_effect=opened.append), \
                mock.patch.object(server, "serve_forever", side_effect=KeyboardInterrupt):
            portal_mod.cmd_serve(args, self.tmp, out)
        self.assertEqual(len(opened), 1)
        self.assertNotIn(TOKEN, opened[0])
        self.assertIn(f"nonce={server.portal.nonce}", opened[0])

    def test_the_page_needs_the_token_but_assets_do_not(self):
        self.assertEqual(self.portal.handle("GET", "/", HOST)[0], 401)
        self.assertEqual(self.portal.handle("GET", "/", AUTH)[0], 200)
        self.assertEqual(self.portal.handle("GET", "/app.js", HOST)[0], 200)

    def test_bad_host_is_refused_even_with_a_valid_token(self):
        for host in ("evil.example", f"evil.example:{PORT}", "127.0.0.1", "127.0.0.1:1"):
            with self.subTest(host=host):
                status, _, body = self.portal.handle("GET", "/api/specs",
                                                     {**AUTH, "Host": host})
                self.assertEqual(status, 403)
                self.assertEqual(json.loads(body)["code"], "sp-portal-bad-host")

    def test_bad_origin_is_refused_and_a_matching_one_passes(self):
        status, _, body = self.portal.handle(
            "POST", "/api/reorder", {**JSON, "Origin": "http://evil.example"}, b'{"order":[1]}')
        self.assertEqual((status, json.loads(body)["code"]), (403, "sp-portal-bad-origin"))
        ok = self.portal.handle("GET", "/api/specs",
                                {**AUTH, **ORIGIN})
        self.assertEqual(ok[0], 200)

    def test_writes_need_json_and_traversal_is_closed(self):
        status, _, _ = self.portal.handle("POST", "/api/reorder", {**AUTH, **ORIGIN}, b'{"order":[1]}')
        self.assertEqual(status, 415)
        self.assertEqual(self.portal.handle("GET", "/..%2f..%2fetc/passwd", HOST)[0], 404)
        self.assertEqual(self.portal.handle("GET", "/../../etc/passwd", HOST)[0], 404)

    def test_non_loopback_host_is_refused_before_binding(self):
        self.assertTrue(portal_mod.is_loopback("127.0.0.1"))
        self.assertFalse(portal_mod.is_loopback("0.0.0.0"))
        self.assertFalse(portal_mod.is_loopback("192.168.1.5"))


class Sessions(PortalCase):
    """`GET /api/sessions` exists only under `--sessions`, and returns fixed fields only."""
    SECRET = "SECRET-do-not-leak"
    FIELDS = {"sessionId", "cwd", "worktree", "state", "status", "statusSince", "lastEvent",
              "pendingQuestion", "pendingTool", "subagents", "activity"}

    def setUp(self):
        super().setUp()
        import os
        import subprocess
        from datetime import datetime, timedelta, timezone
        from quenching.session.transcript import encode_cwd
        subprocess.run(["git", "init", "-q", "-b", "main", self.tmp], check=True)
        self.claude = pathlib.Path(tempfile.mkdtemp(prefix="quenching-claude-"))
        self.addCleanup(__import__("shutil").rmtree, self.claude, True)
        now = datetime.now(timezone.utc)

        def ts(minutes):
            return (now - timedelta(minutes=minutes)).strftime("%Y-%m-%dT%H:%M:%S.000Z")

        def session(name, sid, cwd, events):
            info = {"pid": os.getpid(), "sessionId": sid, "cwd": cwd, "status": "busy",
                    "statusUpdatedAt": int(now.timestamp() * 1000),
                    "messagingSocketPath": "/tmp/" + self.SECRET, "name": self.SECRET}
            (self.claude / "sessions").mkdir(exist_ok=True)
            (self.claude / "sessions" / f"{name}.json").write_text(json.dumps(info))
            (self.claude / "sessions" / f"{name}.{self.SECRET}.key").write_text(self.SECRET)
            folder = self.claude / "projects" / encode_cwd(cwd)
            folder.mkdir(parents=True, exist_ok=True)
            (folder / f"{sid}.jsonl").write_text(
                "\n".join(json.dumps(e) for e in events) + "\n")
            return folder / sid / "subagents"

        sub = os.path.join(self.tmp, "sub")
        os.mkdir(sub)
        agents = session("1", "s-in", sub, [
            {"type": "user", "timestamp": ts(3), "message": {"content": self.SECRET}},
            {"type": "assistant", "timestamp": ts(2), "message": {"content": [
                {"type": "tool_use", "id": "b1", "name": "Bash",
                 "input": {"command": self.SECRET}}]}},
            {"type": "user", "timestamp": ts(2), "message": {"content": [
                {"type": "tool_result", "tool_use_id": "b1", "content": self.SECRET}]}},
            {"type": "assistant", "timestamp": ts(1), "message": {"content": [
                {"type": "tool_use", "id": "q1", "name": "AskUserQuestion",
                 "input": {"questions": [{"question": "Merge now?"}]}}]}}])
        agents.mkdir(parents=True)
        (agents / "agent-a.jsonl").write_text(json.dumps(
            {"type": "assistant", "timestamp": ts(1), "message": {"content": self.SECRET}}) + "\n")
        (agents / "agent-a.meta.json").write_text(json.dumps(
            {"agentType": "quenching:spec-runner", "prompt": self.SECRET}))
        session("2", "s-out", "/elsewhere/other-repo", [
            {"type": "user", "timestamp": ts(1), "message": {"content": "x"}}])
        from quenching.session.portal import reader
        self.on = portal_mod.Portal(self.tmp, TOKEN, False, "127.0.0.1", PORT, sessions={
            "read": reader(self.claude, self.claude / "projects")})

    def test_without_the_flag_the_route_is_404_and_nothing_is_read(self):
        with mock.patch("quenching.session.portal.read_live",
                        side_effect=AssertionError("read without --sessions")):
            status, body = self.get("/api/sessions")
        self.assertEqual((status, body["code"]), (404, "sp-portal-not-found"))
        self.assertFalse(self.get("/api/config")[1]["sessions"])

    def test_with_the_flag_only_the_fixed_fields_of_this_repo_surface(self):
        status, _, raw = self.on.handle("GET", "/api/sessions", AUTH)
        self.assertEqual(status, 200)
        self.assertNotIn(self.SECRET, raw.decode("utf-8"))
        body = json.loads(raw)
        self.assertEqual([s["sessionId"] for s in body["sessions"]], ["s-in"])
        row = body["sessions"][0]
        self.assertEqual(set(row), self.FIELDS)
        self.assertEqual((row["state"], row["pendingQuestion"]), ("waiting", "Merge now?"))
        self.assertEqual(row["worktree"]["branch"], "main")
        self.assertEqual(set(row["subagents"][0]), {"agentType", "start", "end", "active"})
        self.assertEqual(row["subagents"][0]["agentType"], "quenching:spec-runner")
        self.assertEqual(len(row["activity"]), body["windowMinutes"])
        self.assertTrue(json.loads(self.on.handle("GET", "/api/config", AUTH)[2])["sessions"])

    def test_an_unchanged_poll_is_a_304(self):
        _, headers, _ = self.on.handle("GET", "/api/sessions", AUTH)
        again = self.on.handle("GET", "/api/sessions", {**AUTH, "If-None-Match": headers["ETag"]})
        self.assertEqual(again[0], 304)

    def test_a_copy_without_the_session_reader_refuses_the_flag(self):
        with mock.patch.dict(lent_mod._LENT, clear=True):
            source, refusal = portal_mod.sessions_source()
        self.assertIsNone(source)
        self.assertEqual(refusal["code"], "sp-portal-sessions-unavailable")

    def test_the_lent_reader_answers_the_flag(self):
        with mock.patch.dict(lent_mod._LENT, {portal_mod.SESSIONS: "quenching.session.portal"}), \
                mock.patch.dict("os.environ", {"QUENCHING_CLAUDE_ROOT": str(self.claude)}):
            source, refusal = portal_mod.sessions_source()
        self.assertIsNone(refusal)
        self.assertEqual(set(source), {"read"})

    def test_the_portal_never_imports_the_session_pillar(self):
        source = pathlib.Path(portal_mod.__file__).read_text()
        self.assertNotRegex(source, r"(?m)^\s*(?:from|import) quenching\.session")


class ReadOnly(PortalCase):
    read_only = True

    def test_every_write_route_is_refused_server_side_and_nothing_is_written(self):
        before = dict(self.backend.docs)
        for route, data in (("capture", {"title": "x", "problem": "y"}),
                            ("section", {"spec": 1, "heading": "Problem", "body": "z"}),
                            ("approve", {"spec": 1}), ("reorder", {"order": [1, 2]}),
                            ("discovery", {"spec": 1, "text": "d"})):
            with self.subTest(route=route):
                status, body = self.post(route, data)
                self.assertEqual((status, body["code"]), (403, "sp-read-only"))
        self.assertEqual(self.backend.docs, before)
        self.assertEqual(self.get("/api/specs")[0], 200)
        self.assertFalse(self.get("/api/config")[1]["writable"])


class ReadOnlyBackend(PortalCase):
    def test_a_read_only_backend_disables_writes_without_the_flag(self):
        with mock.patch.object(SpecBackend, "read_only", True):
            status, body = self.post("reorder", {"order": [1, 2]})
        self.assertEqual((status, body["code"]), (403, "sp-read-only"))


class LiveServer(PortalCase):
    def test_a_real_socket_serves_the_page_and_rejects_a_forged_host(self):
        server = portal_mod.make_server(self.tmp, token=TOKEN)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(thread.join, 5)
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        port = server.server_address[1]
        self.assertEqual(server.server_address[0], "127.0.0.1")
        req = urllib.request.Request(f"http://127.0.0.1:{port}/api/specs",
                                     headers={TOKEN_HEADER: TOKEN})
        with urllib.request.urlopen(req) as resp:
            self.assertEqual(json.loads(resp.read())["count"], 3)
        forged = urllib.request.Request(f"http://127.0.0.1:{port}/api/specs",
                                        headers={TOKEN_HEADER: TOKEN, "Host": "evil.example"})
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            urllib.request.urlopen(forged)
        self.assertEqual(ctx.exception.code, 403)


class StdoutIsolation(unittest.TestCase):
    def test_two_portals_never_capture_each_others_verb_output(self):
        import time
        roots = ["/repo/a", "/repo/b"]
        portals = [portal_mod.Portal(r, TOKEN, False, "127.0.0.1", PORT) for r in roots]

        def verb(args, root, emitter):
            time.sleep(0.01)
            print(json.dumps({"ok": True, "root": root}))
            return 0

        results, errors = [], []

        def run(portal, root):
            for _ in range(10):
                try:
                    results.append((root, portal._verb(verb, {})))
                except Exception as e:  # noqa: BLE001
                    errors.append(e)

        threads = [threading.Thread(target=run, args=(p, r)) for p, r in zip(portals, roots)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(10)
        self.assertEqual(errors, [])
        self.assertEqual(len(results), 20)
        for root, payload in results:
            self.assertEqual(payload.get("root"), root)


TOKEN_HEADER = portal_mod.TOKEN_HEADER

if __name__ == "__main__":
    unittest.main()
