"""The Azure sync cache, offline: the `az` transport is an in-memory double of a work-item store
with revisions, the way Azure Boards numbers them. No `az` process, no network and no real
organisation is ever reached."""

import base64
import contextlib
import http.client
import io
import json
import os
import tempfile
import threading
import unittest
from unittest import mock

import _paths  # noqa: F401  — must precede the `quenching` import; see its docstring
from quenching.specs import sync
from quenching.specs.backends import azure as azure_mod
from quenching.specs.backends.azure import AzureBoardsBackend
from quenching.specs.backends.base import BackendRefusal
from argparse import Namespace
from quenching.specs.commands import sync as sync_cmd
from quenching.specs.commands.output import Emitter
from quenching.specs.backends.hybrid import hybrid_project, hybrid_wrap
from quenching.specs.schema import capture_form

STATES = {"plans": "Active", "archive": "Closed"}
FOREVER = 10 ** 9


def case_doc(slug: str) -> str:
    return (capture_form().replace("<SLUG>", slug).replace("<TITLE>", slug.title())
            .replace("<DATE>", "2026-01-01").replace("<VERIFICATION>", "per-task"))


class AzDouble:
    """A work-item store. `calls` records what the backend asked of the transport."""

    def __init__(self):
        self.items: dict[int, dict] = {}
        self.calls: list[tuple] = []
        self.patches: list[list] = []

    def put_spec(self, item_id: int, text: str) -> None:
        stored, title = hybrid_project(text)
        item = self.items.setdefault(item_id, {"id": item_id, "rev": 0, "fields": {}})
        item["rev"] += 1
        item["fields"].update({"System.Title": title, "System.State": "Active", "System.Tags": "",
                               "System.Description": hybrid_wrap(stored, fmt="div")})

    def put_plain(self, item_id: int) -> None:
        self.items[item_id] = {"id": item_id, "rev": 1, "fields": {
            "System.Title": "a bug", "System.State": "Active", "System.Tags": "",
            "System.Description": "<p>not a spec</p>"}}

    def text_of(self, item_id: int) -> str:
        from quenching.specs.backends.hybrid import hybrid_unwrap
        return hybrid_unwrap(self.items[item_id]["fields"]["System.Description"])[0]

    def count(self, kind: str) -> int:
        return sum(1 for c in self.calls if c[0] == kind)

    def __call__(self, cwd, *argv, stdin=None):
        if argv[:2] == ("boards", "query"):
            self.calls.append(("query",))
            return 0, json.dumps([{"id": i} for i in sorted(self.items)]), ""
        if argv[:2] == ("devops", "invoke"):
            with open(argv[argv.index("--in-file") + 1], encoding="utf-8") as fh:
                request = json.load(fh)
            lean = "System.Description" not in request["fields"]
            self.calls.append(("batch", tuple(request["ids"]), lean))
            return 0, json.dumps({"value": [self.items[i] for i in request["ids"]
                                            if i in self.items]}), ""
        if argv[0] == "rest":
            return self._patch(argv)
        raise AssertionError(f"the double does not know {argv!r}")

    def _patch(self, argv):
        item_id = int(argv[argv.index("--uri") + 1].split("/workitems/")[1].split("?")[0])
        with open(argv[argv.index("--body") + 1][1:], encoding="utf-8") as fh:
            ops = json.load(fh)
        self.patches.append(ops)
        item = self.items[item_id]
        for op in ops:
            if op["op"] == "test" and op["value"] != item["rev"]:
                return 1, "", "TF26071: test operation failed on /rev"
        for op in ops:
            if op["path"].startswith("/fields/"):
                item["fields"][op["path"][len("/fields/"):]] = op["value"]
        item["rev"] += 1
        return 0, json.dumps({"id": item_id, "rev": item["rev"]}), ""


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.az = AzDouble()
        patcher = mock.patch.object(azure_mod, "_az_run", self.az)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.az.put_spec(1, case_doc("alpha"))
        self.az.put_spec(2, case_doc("beta"))
        self.clock = [1000.0]
        self.cache = sync.SyncCache(os.path.join(self.tmp.name, "cache"))
        self.inner = AzureBoardsBackend("https://example.invalid/org", "proj", STATES, ".")
        self.backend = sync.SyncedBackend(self.inner, self.cache, ttl=FOREVER,
                                          clock=lambda: self.clock[0])

    def event(self, kind, item_id, rev=None):
        resource = {"workItemId": item_id}
        if rev is not None:
            resource["rev"] = rev
        return {"eventType": kind, "resource": resource}


class WarmReads(Base):
    def test_a_warm_read_and_a_warm_listing_cost_no_transport_call(self):
        self.assertEqual([1, 2], [r["id"] for r in self.backend.list_specs()])
        info, err = self.backend.read_spec(1)
        self.assertEqual({}, err)
        self.az.calls.clear()
        again, _ = self.backend.read_spec(1)
        self.assertEqual([1, 2], [r["id"] for r in self.backend.list_specs()])
        self.assertEqual([], self.az.calls)
        self.assertEqual(info["text"], again["text"])
        self.assertEqual(info["stage"], again["stage"])
        self.assertEqual(1, again["_azure_rev"])

    def test_the_cached_info_equals_the_one_the_adapter_derives(self):
        cached, _ = self.backend.read_spec(2)
        fresh, _ = AzureBoardsBackend("https://example.invalid/org", "proj", STATES,
                                      ".").read_spec(2)
        for key in ("text", "frontmatter", "sections", "tasks", "stage", "verification",
                    "date", "path", "phase"):
            self.assertEqual(fresh[key], cached[key], key)

    def test_an_unknown_id_is_the_adapters_refusal_and_is_not_cached(self):
        info, err = self.backend.read_spec(99)
        self.assertIsNone(info)
        self.assertEqual("sp-unknown-id", err["code"])
        self.assertIsNone(self.cache.get(99))

    def test_a_corrupt_or_missing_entry_is_a_miss_not_a_failure(self):
        self.backend.read_spec(1)
        with open(os.path.join(self.cache.items_dir, "1.json"), "w") as fh:
            fh.write("{not json")
        self.az.calls.clear()
        info, err = self.backend.read_spec(1)
        self.assertEqual({}, err)
        fresh, _ = AzureBoardsBackend("https://example.invalid/org", "proj", STATES,
                                      ".").read_spec(1)
        self.assertEqual(fresh["text"], info["text"])
        self.assertEqual(2, self.az.count("batch"))
        os.unlink(os.path.join(self.cache.directory, "meta.json"))
        self.assertEqual([1, 2], [r["id"] for r in self.backend.list_specs()])


class RevisionStaleness(Base):
    def test_a_higher_rev_marks_the_entry_stale_and_one_batch_call_refetches_it(self):
        self.backend.read_spec(1)
        self.az.put_spec(1, case_doc("alpha") + "\nchanged remotely\n")
        result = sync.apply_event(self.cache, self.event("workitem.updated", 1, 2))
        self.assertEqual("stale", result["action"])
        self.az.calls.clear()
        info, _ = self.backend.read_spec(1)
        self.assertIn("changed remotely", info["text"])
        self.assertEqual(2, info["_azure_rev"])
        self.assertEqual([("batch", (1,), False)], self.az.calls)
        self.az.calls.clear()
        self.backend.read_spec(1)
        self.assertEqual([], self.az.calls)

    def test_an_equal_or_lower_rev_changes_nothing(self):
        self.backend.read_spec(1)
        for rev in (1, 0):
            result = sync.apply_event(self.cache, self.event("workitem.updated", 1, rev))
            self.assertEqual("current", result["action"])
        self.assertFalse(self.cache.get(1)["stale"])

    def test_deleted_drops_the_entry_and_the_listing_follows(self):
        self.backend.list_specs()
        del self.az.items[2]
        result = sync.apply_event(self.cache, self.event("workitem.deleted", 2))
        self.assertEqual("dropped", result["action"])
        self.assertEqual([1], [r["id"] for r in self.backend.list_specs()])

    def test_created_makes_the_listing_reconcile_and_a_plain_item_leaves_no_entry(self):
        self.backend.list_specs()
        self.az.put_plain(3)
        self.az.put_spec(4, case_doc("delta"))
        for item_id in (3, 4):
            sync.apply_event(self.cache, self.event("workitem.created", item_id, 1))
        self.assertTrue(self.cache.status()["dirty"])
        self.assertEqual([1, 2, 4], [r["id"] for r in self.backend.list_specs()])
        self.assertIsNone(self.cache.get(3))
        self.assertEqual({"3": 1}, self.cache.meta()["notSpecs"])
        self.az.calls.clear()
        self.backend.reconcile()
        self.assertEqual([("query",), ("batch", (1, 2, 3, 4), True)], self.az.calls)

    def test_an_unreadable_event_is_an_error_not_a_skip(self):
        for payload in (None, [], {"eventType": "git.push", "resource": {}},
                        {"eventType": "workitem.updated"},
                        {"eventType": "workitem.updated", "resource": {"x": 1}},
                        {"eventType": "workitem.updated", "resource": {"id": 1, "rev": "x"}}):
            with self.subTest(payload=payload), self.assertRaises(sync.EventError):
                sync.apply_event(self.cache, payload)

    def test_the_revision_may_come_from_the_revision_object(self):
        self.assertEqual(("workitem.updated", 5, 9), sync.parse_event(
            {"eventType": "workitem.updated",
             "resource": {"workItemId": 5, "revision": {"rev": 9}}}))


class Reconciliation(Base):
    def test_only_what_differs_is_refetched_and_what_left_is_dropped(self):
        self.backend.list_specs()
        self.az.put_spec(1, case_doc("alpha") + "\nchanged\n")
        self.az.put_spec(3, case_doc("gamma"))
        del self.az.items[2]
        self.az.calls.clear()
        self.clock[0] = 2000.0
        report = self.backend.reconcile()
        self.assertEqual({"checked": 2, "refetched": 2, "dropped": 1, "notSpecs": 0}, report)
        fetched = sorted(i for c in self.az.calls if c[0] == "batch" and not c[2] for i in c[1])
        self.assertEqual([1, 3], fetched)
        self.assertEqual([1, 3], self.cache.ids())
        self.assertEqual(2000.0, self.cache.meta()["reconciledAt"])
        self.assertFalse(self.cache.meta()["dirty"])

    def test_a_read_past_the_ttl_reconciles_first(self):
        backend = sync.SyncedBackend(self.inner, self.cache, ttl=60, clock=lambda: self.clock[0])
        backend.read_spec(1)
        self.az.put_spec(1, case_doc("alpha") + "\nzzmarker\n")
        self.clock[0] += 30
        self.assertNotIn("zzmarker", backend.read_spec(1)[0]["text"])
        self.clock[0] += 31
        self.assertIn("zzmarker", backend.read_spec(1)[0]["text"])

    def test_many_changes_are_read_with_one_bulk_listing(self):
        for item_id in range(10, 40):
            self.az.put_spec(item_id, case_doc(f"s{item_id}"))
        self.backend.list_specs()
        bulk = [c for c in self.az.calls if c[0] == "batch" and not c[2]]
        self.assertEqual(1, len(bulk))
        self.assertEqual(32, len(self.cache.ids()))

    def test_the_status_names_the_directory_and_counts(self):
        self.backend.list_specs()
        sync.apply_event(self.cache, self.event("workitem.updated", 1, 5))
        status = self.cache.status()
        self.assertEqual((2, 1, False), (status["items"], status["stale"], status["dirty"]))
        self.assertEqual(self.cache.directory, status["path"])


class WriteThrough(Base):
    def test_a_write_goes_through_the_adapter_and_the_next_read_sees_it(self):
        info, _ = self.backend.read_spec(1)
        self.backend.write_spec(info, info["text"] + "\nedited\n")
        self.assertIn("edited", self.az.text_of(1))
        self.assertEqual(["test"], [op["op"] for op in self.az.patches[0] if op["op"] == "test"])
        self.assertEqual(1, self.az.patches[0][0]["value"])
        self.az.calls.clear()
        again, _ = self.backend.read_spec(1)
        self.assertIn("edited", again["text"])
        self.assertEqual(2, again["_azure_rev"])
        self.assertEqual([], self.az.calls)

    def test_a_write_over_a_newer_revision_is_refused_and_leaves_no_stale_entry(self):
        info, _ = self.backend.read_spec(1)
        self.az.put_spec(1, case_doc("alpha") + "\nsomeone else\n")
        with self.assertRaises(BackendRefusal) as caught:
            self.backend.write_spec(info, info["text"] + "\nmine\n")
        self.assertEqual("sp-az-stale-write", caught.exception.err["code"])
        self.assertNotIn("mine", self.az.text_of(1))
        self.assertIsNone(self.cache.get(1))
        self.assertIn("someone else", self.backend.read_spec(1)[0]["text"])

    def test_a_create_makes_the_next_listing_reconcile(self):
        self.backend.list_specs()
        self.az.put_spec(3, case_doc("gamma"))
        with mock.patch.object(AzureBoardsBackend, "create_spec", return_value="loc"):
            self.assertEqual("loc", self.backend.create_spec("plans", case_doc("gamma")))
        self.assertEqual([1, 2, 3], [r["id"] for r in self.backend.list_specs()])


class Wiring(Base):
    def test_what_the_wrapper_does_not_define_is_the_adapters(self):
        self.assertEqual("azure-boards", self.backend.name)
        for attr in ("board_findings", "predecessor_links", "marker_without_discovery_tag"):
            self.assertTrue(callable(getattr(self.backend, attr)), attr)

    def test_sync_is_off_unless_asked_for_and_only_wraps_azure(self):
        with mock.patch.dict(os.environ, {sync.ENV_ENABLE: ""}):
            self.assertIs(self.inner, sync.wrap_if_enabled(self.inner))
        with mock.patch.dict(os.environ, {sync.ENV_ENABLE: "1", "XDG_CACHE_HOME": self.tmp.name}):
            wrapped = sync.wrap_if_enabled(self.inner)
            self.assertIsInstance(wrapped, sync.SyncedBackend)
            self.assertTrue(wrapped.cache.directory.startswith(self.tmp.name))
            other = mock.Mock()
            other.name = "github"
            self.assertIs(other, sync.wrap_if_enabled(other))

    def test_the_cache_directory_is_keyed_by_organisation_and_project(self):
        a = sync.cache_dir("https://dev.azure.com/o", "p")
        self.assertNotEqual(a, sync.cache_dir("https://dev.azure.com/o", "q"))
        self.assertEqual(a, sync.cache_dir("https://dev.azure.com/o", "p"))


SECRET = "s3cret-value"


def basic(secret: str, user: str = "hook") -> str:
    return "Basic " + base64.b64encode(f"{user}:{secret}".encode()).decode()


class Receiver(Base):
    def setUp(self):
        super().setUp()
        self.server = sync_cmd.make_receiver(self.backend, "127.0.0.1", 0, SECRET)
        self.port = self.server.server_address[1]
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        self.addCleanup(self.server.server_close)
        self.addCleanup(self.server.shutdown)
        self.backend.read_spec(1)

    def call(self, method, path="/hooks/azure", body=None, auth=None):
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        headers = {"Authorization": auth} if auth else {}
        conn.request(method, path, body=json.dumps(body) if body is not None else None,
                     headers=headers)
        resp = conn.getresponse()
        data = json.loads(resp.read() or b"{}")
        conn.close()
        return resp.status, data

    def test_401_without_the_secret_and_with_a_wrong_one(self):
        event = self.event("workitem.updated", 1, 9)
        self.assertEqual(401, self.call("POST", body=event)[0])
        self.assertEqual(401, self.call("POST", body=event, auth=basic("nope"))[0])
        self.assertEqual(401, self.call("POST", body=event, auth="Bearer " + SECRET)[0])
        self.assertFalse(self.cache.get(1).get("stale"))

    def test_405_off_post(self):
        for method in ("GET", "PUT", "DELETE"):
            self.assertEqual(405, self.call(method, auth=basic(SECRET))[0])

    def test_200_and_a_stale_mark_with_the_secret(self):
        status, data = self.call("POST", body=self.event("workitem.updated", 1, 9),
                                 auth=basic(SECRET, user="anyone"))
        self.assertEqual(200, status)
        self.assertEqual("stale", data["action"])
        self.assertTrue(self.cache.get(1)["stale"])

    def test_an_unknown_shape_is_400_and_another_path_is_404(self):
        self.assertEqual(400, self.call("POST", body={"eventType": "x"}, auth=basic(SECRET))[0])
        self.assertEqual(404, self.call("POST", path="/other", body={}, auth=basic(SECRET))[0])

    def test_a_non_loopback_host_is_refused(self):
        with self.assertRaises(ValueError):
            sync_cmd.make_receiver(self.backend, "0.0.0.0", 0, SECRET)
        out, err = io.StringIO(), io.StringIO()
        args = Namespace(sync_cmd="serve", host="0.0.0.0", port=0, json=True)
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = sync_cmd.cmd_sync(args, ".", Emitter())
        self.assertEqual(2, code)
        self.assertIn("sp-serve-host", out.getvalue() + err.getvalue())


class Verbs(Base):
    def run_verb(self, verb, stdin="", **extra):
        args = Namespace(sync_cmd=verb, json=True, host="127.0.0.1", port=0, **extra)
        out = io.StringIO()
        with mock.patch.object(sync_cmd, "open_backend", return_value=(self.backend, {})), \
                mock.patch("sys.stdin", io.StringIO(stdin)), contextlib.redirect_stdout(out):
            code = sync_cmd.cmd_sync(args, ".", Emitter())
        return code, out.getvalue()

    def test_status_and_reconcile(self):
        code, text = self.run_verb("status")
        self.assertEqual(0, code)
        self.assertEqual(0, json.loads(text)["items"])
        code, text = self.run_verb("reconcile")
        self.assertEqual(0, code)
        self.assertEqual(2, json.loads(text)["refetched"])
        self.assertEqual(2, json.loads(self.run_verb("status")[1])["items"])

    def test_apply_reads_one_event_from_stdin(self):
        self.backend.read_spec(1)
        code, text = self.run_verb("apply", stdin=json.dumps(self.event("workitem.updated", 1, 7)))
        self.assertEqual(0, code)
        self.assertEqual("stale", json.loads(text)["action"])
        code, _ = self.run_verb("apply", stdin="{not json")
        self.assertEqual(2, code)

    def test_serve_refuses_to_start_without_the_secret_and_takes_none_in_argv(self):
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop(sync_cmd.ENV_SECRET, None)
            code, text = self.run_verb("serve")
        self.assertEqual(2, code)
        self.assertIn("sp-sync-secret", text)
        from quenching.specs.commands.cli import build_parser
        parser, _ = build_parser()
        with self.assertRaises(SystemExit), contextlib.redirect_stderr(io.StringIO()):
            parser.parse_args(["sync", "serve", "--secret", "x"])

    def test_the_secret_is_matched_in_constant_time_form_only(self):
        self.assertTrue(sync_cmd.secret_ok(basic(SECRET), SECRET))
        self.assertFalse(sync_cmd.secret_ok(basic(""), SECRET))
        self.assertFalse(sync_cmd.secret_ok("Basic !!!", SECRET))
        self.assertFalse(sync_cmd.secret_ok(basic(SECRET), ""))


if __name__ == "__main__":
    unittest.main()
