"""`cq portal serve` — two projects behind one loopback server, offline, over the memory fake."""

import json
import os
import pathlib
import shutil
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
from quenching.portal import main as portal_main
from quenching.portal import serve as serve_mod
from quenching.session import worktrees as worktrees_mod
from quenching.specs import backends as backends_mod
from quenching.specs import portal as portal_mod
from quenching.specs.backends.memory import MemoryBackend

TOKEN = "t0ken"
PORT = 4321
HOST = {"Host": f"127.0.0.1:{PORT}"}
AUTH = {**HOST, "X-Quenching-Token": TOKEN}
JSON = {**AUTH, "Origin": f"http://127.0.0.1:{PORT}", "Content-Type": "application/json"}
DOC = "---\ntitle: {title}\ndate: 2026-01-01\n---\n\n## Problem\n\nSomething is wrong.\n"
TITLES = {"alpha": ("A1", "A2"), "beta b": ("B1", "B2", "B3")}


class CentralCase(unittest.TestCase):
    def setUp(self):
        self.tmp = pathlib.Path(tempfile.mkdtemp(prefix="quenching-central-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, True)
        backends_mod._BACKEND_CACHE.clear()
        self.addCleanup(backends_mod._BACKEND_CACHE.clear)
        self.projects, self.backends = [], {}
        for name, titles in TITLES.items():
            root = self.tmp / name.replace(" ", "-")
            root.mkdir()
            backend = MemoryBackend()
            for title in titles:
                backend.create_spec("plans", DOC.format(title=title))
            backends_mod._BACKEND_CACHE[str(root)] = backend
            self.backends[name] = backend
            self.projects.append({"name": name, "path": str(root)})
        self.central = serve_mod.Central(portal_mod, worktrees_mod.list_worktrees, self.projects,
                                         TOKEN, host="127.0.0.1", port=PORT)

    def call(self, method, target, headers=AUTH, data=None):
        body = json.dumps(data).encode() if data is not None else b""
        status, _, out = self.central.handle(method, target, headers, body)
        return status, json.loads(out) if out else None

    @staticmethod
    def prefix(name):
        return "/p/" + urllib.request.quote(name, safe="")


class Routing(CentralCase):
    def test_projects_lists_every_project_with_prefix_and_worktrees(self):
        status, body = self.call("GET", "/api/projects")
        self.assertEqual(status, 200, body)
        rows = {p["name"]: p for p in body["projects"]}
        self.assertEqual(set(rows), set(TITLES))
        self.assertEqual(rows["beta b"]["prefix"], "/p/beta%20b")
        for row in rows.values():
            self.assertEqual(row["worktrees"], [{"path": row["path"], "branch": None,
                                                 "main": True}])

    def test_each_prefix_reads_only_its_own_store(self):
        for name, titles in TITLES.items():
            status, body = self.call("GET", self.prefix(name) + "/api/specs")
            self.assertEqual(status, 200, body)
            self.assertEqual(sorted(r["title"] for r in body["specs"]), sorted(titles))

    def test_the_query_string_reaches_the_project(self):
        status, body = self.call("GET", self.prefix("alpha") + "/api/search?q=A2")
        self.assertEqual(status, 200, body)
        self.assertEqual([r["title"] for r in body["results"]], ["A2"])

    def test_unknown_project_and_non_api_paths_are_404(self):
        self.assertEqual(self.call("GET", "/p/nope/api/specs")[1]["code"],
                         "portal-unknown-project")
        self.assertEqual(self.call("GET", "/p/alpha/index.html")[0], 404)
        self.assertEqual(self.call("GET", "/api/specs")[0], 404)

    def test_concurrent_reads_and_captures_never_cross(self):
        errors, seen = [], []

        def work(name):
            for i in range(8):
                try:
                    status, body = self.call("POST", self.prefix(name) + "/api/capture", JSON,
                                             {"title": f"{name}-new-{i}", "problem": "p"})
                    self.assertEqual(status, 200, body)
                    status, body = self.call("GET", self.prefix(name) + "/api/specs?refresh=1")
                    seen.append((name, [r["title"] for r in body["specs"]]))
                except Exception as exc:  # noqa: BLE001
                    errors.append(exc)

        threads = [threading.Thread(target=work, args=(n,)) for n in TITLES]
        for t in threads:
            t.start()
        for t in threads:
            t.join(30)
        self.assertEqual(errors, [])
        other = {"alpha": "beta b", "beta b": "alpha"}
        for name, titles in seen:
            self.assertFalse([t for t in titles if t.startswith(other[name])
                              or t in TITLES[other[name]]], (name, titles))
        for name, backend in self.backends.items():
            texts = [text for _, text in backend.docs.values()]
            self.assertEqual(sum(f"{name}-new-" in t for t in texts), 8)
            self.assertFalse(any(f"{other[name]}-new-" in t for t in texts))


class Gates(CentralCase):
    def test_api_without_token_is_401(self):
        self.assertEqual(self.call("GET", "/api/projects", HOST)[0], 401)
        self.assertEqual(self.call("GET", "/p/alpha/api/specs", HOST)[0], 401)

    def test_the_door_401_names_the_central_command(self):
        status, _, body = self.central.handle("GET", "/", HOST)
        self.assertEqual(status, 401)
        self.assertIn(b"cq portal serve", body)
        self.assertNotIn(b"cq specs serve", body)

    def test_forged_host_is_403(self):
        forged = {**AUTH, "Host": "evil.example"}
        self.assertEqual(self.call("GET", "/p/alpha/api/specs", forged)[1]["code"],
                         "sp-portal-bad-host")

    def test_post_without_origin_is_403_and_writes_nothing(self):
        headers = {k: v for k, v in JSON.items() if k != "Origin"}
        status, body = self.call("POST", "/p/alpha/api/capture", headers,
                                 {"title": "x", "problem": "y"})
        self.assertEqual((status, body["code"]), (403, "sp-portal-bad-origin"))
        self.assertEqual(len(self.backends["alpha"].docs), 2)

    def test_the_nonce_trades_once_for_the_cookie(self):
        nonce = self.central.nonce
        status, headers, _ = self.central.handle("GET", f"/?nonce={nonce}", HOST)
        self.assertEqual(status, 303)
        self.assertIn("HttpOnly; SameSite=Strict; Path=/", headers["Set-Cookie"])
        self.assertEqual(self.central.handle("GET", f"/?nonce={nonce}", HOST)[0], 401)
        cookie = {**HOST, "Cookie": f"{portal_mod.COOKIE_NAME}={TOKEN}"}
        self.assertEqual(self.call("GET", "/api/projects", cookie)[0], 200)

    def test_read_only_reaches_every_project(self):
        central = serve_mod.Central(portal_mod, worktrees_mod.list_worktrees, self.projects,
                                    TOKEN, read_only=True, host="127.0.0.1", port=PORT)
        status, _, out = central.handle("POST", "/p/alpha/api/capture", JSON,
                                        json.dumps({"title": "x", "problem": "y"}).encode())
        self.assertEqual((status, json.loads(out)["code"]), (403, "sp-read-only"))


class Chat(CentralCase):
    def test_a_project_chat_runs_in_its_own_worktree_only(self):
        from test_specs_chat import install_fake
        claude, log = install_fake(self)
        chat = {"claude": claude, "budget": 0.5, "worktrees": None}
        central = serve_mod.Central(portal_mod, worktrees_mod.list_worktrees, self.projects,
                                    TOKEN, host="127.0.0.1", port=PORT, chat=chat)
        alpha, beta = (p["path"] for p in self.projects)
        status, _, out = central.handle("POST", "/p/alpha/api/chat", JSON,
                                        json.dumps({"question": "q", "worktree": beta}).encode())
        self.assertEqual((400, "sp-portal-chat-worktree"), (status, json.loads(out)["code"]))
        status, _, out = central.handle("POST", "/p/alpha/api/chat", JSON,
                                        json.dumps({"question": "q", "worktree": alpha}).encode())
        self.assertEqual(202, status, out)
        job = central.portals["alpha"].jobs[json.loads(out)["job"]]
        job.thread.join(10)
        self.assertEqual("done", job.status)
        self.assertEqual(alpha, os.path.realpath(json.loads(pathlib.Path(log).read_text())["cwd"]))
        status, _, out = central.handle("GET", f"/p/beta%20b/api/chat/{job.id}", AUTH)
        self.assertEqual(404, status)


class LiveServer(CentralCase):
    def test_a_real_socket_routes_to_a_project(self):
        server = serve_mod.make_central_server(self.central)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(thread.join, 5)
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        port = server.server_address[1]
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        req = urllib.request.Request(f"http://127.0.0.1:{port}/p/alpha/api/specs",
                                     headers={portal_mod.TOKEN_HEADER: TOKEN})
        with opener.open(req) as resp:
            self.assertEqual(json.loads(resp.read())["count"], 2)


class Command(unittest.TestCase):
    def setUp(self):
        home = tempfile.mkdtemp(prefix="quenching-home-")
        self.addCleanup(shutil.rmtree, home, True)
        patch = mock.patch.dict(os.environ, {"HOME": home})
        patch.start()
        self.addCleanup(patch.stop)
        lent = mock.patch.dict(lent_mod._LENT, clear=True)
        lent.start()
        self.addCleanup(lent.stop)

    def run_json(self, *argv):
        import contextlib
        import io
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            rc = portal_main(["serve", *argv, "--json"])
        return rc, json.loads(out.getvalue())

    def test_nothing_lent_is_refused(self):
        rc, body = self.run_json()
        self.assertEqual((rc, body["code"]), (2, "portal-serve-unavailable"))

    def test_an_empty_registry_is_refused_before_a_socket(self):
        lent_mod.lend(serve_mod.SPECS, "quenching.specs.portal")
        lent_mod.lend(serve_mod.WORKTREES, "quenching.session.worktrees")
        with mock.patch.object(serve_mod, "make_central_server") as server:
            rc, body = self.run_json()
        self.assertEqual((rc, body["code"]), (2, "portal-no-projects"))
        server.assert_not_called()

    def test_chat_with_a_bad_budget_is_refused_before_a_socket(self):
        lent_mod.lend(serve_mod.SPECS, "quenching.specs.portal")
        lent_mod.lend(serve_mod.WORKTREES, "quenching.session.worktrees")
        with mock.patch.object(serve_mod.registry, "list_projects",
                               return_value=[{"name": "a", "path": "/tmp"}]), \
                mock.patch.object(serve_mod, "make_central_server") as server:
            rc, body = self.run_json("--chat", "--chat-budget-usd", "0")
        self.assertEqual((rc, body["code"]), (2, "sp-portal-chat-budget"))
        server.assert_not_called()

    def test_a_non_loopback_host_is_refused(self):
        lent_mod.lend(serve_mod.SPECS, "quenching.specs.portal")
        lent_mod.lend(serve_mod.WORKTREES, "quenching.session.worktrees")
        rc, body = self.run_json("--host", "0.0.0.0")
        self.assertEqual((rc, body["code"]), (2, "sp-serve-host"))


if __name__ == "__main__":
    unittest.main()
