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
from quenching.specs import backends as backends_mod
from quenching.specs import portal as portal_mod
from quenching.specs.backends.base import BackendRefusal, SpecBackend
from quenching.specs.backends.memory import MemoryBackend

TOKEN = "t0ken"
PORT = 4321
HOST = {"Host": f"127.0.0.1:{PORT}"}
AUTH = {**HOST, "X-Quenching-Token": TOKEN}
JSON = {**AUTH, "Content-Type": "application/json"}

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

    def test_detail_carries_sections_tasks_and_records(self):
        status, body = self.get("/api/specs/1")
        self.assertEqual(status, 200)
        self.assertEqual(body["spec"]["title"], "Alpha")
        problem = next(s for s in body["sections"] if s["heading"] == "Problem")
        self.assertIn("Something is wrong", problem["body"])
        self.assertEqual(len(body["tasks"]), 2)
        self.assertEqual(body["executeCommand"], "/quenching:specs:execute 1")
        self.assertEqual(self.get("/api/specs/99")[0], 404)

    def test_search_finds_text_in_any_section(self):
        status, body = self.get("/api/search?q=something+is+wrong")
        self.assertEqual((status, body["count"]), (200, 3))
        self.assertEqual(self.get("/api/search?q=zzzz")[1]["count"], 0)

    def test_epics_are_hidden_when_no_spec_is_an_epic(self):
        self.assertFalse(self.get("/api/epics")[1]["supported"])

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
        self.assertEqual(self.portal.handle("POST", "/api/capture", HOST, b"{}")[0], 401)

    def test_token_in_the_query_reads_but_never_writes(self):
        self.assertEqual(self.portal.handle("GET", f"/api/specs?token={TOKEN}", HOST)[0], 200)
        status, _, _ = self.portal.handle(
            "POST", f"/api/reorder?token={TOKEN}",
            {**HOST, "Content-Type": "application/json"}, b'{"order":[1]}')
        self.assertEqual(status, 401)

    def test_the_page_needs_the_token_but_assets_do_not(self):
        self.assertEqual(self.portal.handle("GET", "/", HOST)[0], 401)
        self.assertEqual(self.portal.handle("GET", f"/?token={TOKEN}", HOST)[0], 200)
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
                                {**AUTH, "Origin": f"http://127.0.0.1:{PORT}"})
        self.assertEqual(ok[0], 200)

    def test_writes_need_json_and_traversal_is_closed(self):
        status, _, _ = self.portal.handle("POST", "/api/reorder", AUTH, b'{"order":[1]}')
        self.assertEqual(status, 415)
        self.assertEqual(self.portal.handle("GET", "/..%2f..%2fetc/passwd", HOST)[0], 404)
        self.assertEqual(self.portal.handle("GET", "/../../etc/passwd", HOST)[0], 404)

    def test_non_loopback_host_is_refused_before_binding(self):
        self.assertTrue(portal_mod.is_loopback("127.0.0.1"))
        self.assertFalse(portal_mod.is_loopback("0.0.0.0"))
        self.assertFalse(portal_mod.is_loopback("192.168.1.5"))


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


TOKEN_HEADER = portal_mod.TOKEN_HEADER

if __name__ == "__main__":
    unittest.main()
