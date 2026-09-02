"""Provider-backed specs tests: GitHub Issues and Azure Boards share the canonical
transport contract, while unknown and legacy local providers refuse without creating a store.

The transport fixtures are strict and offline. They record every native request so parity means
both the canonical observations and the provider-specific wire shape remain covered.
"""

import argparse
import contextlib
import io
import json
import os
import pathlib
import socket
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

try:
    import _paths  # noqa: F401  — must precede the `quenching` import; see its docstring
except ModuleNotFoundError:  # package-qualified unittest invocation from the repository root
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    import _paths  # noqa: F401
from quenching.common.frontmatter import parse_frontmatter
from quenching.specs.backends import azure as az_mod
from quenching.specs.backends import github as gh_mod
from quenching.specs.backends.azure import AzureBoardsBackend
from quenching.specs.backends.base import BackendRefusal, SpecBackend
from quenching.specs.backends.github import (GH_MISSING, GH_NOT_AUTHENTICATED, GitHubBackend,
                                             empty_listing_refusal, gh_refusal,
                                             listing_is_suspect)
from quenching.specs.backends.hybrid import (GH_BODY_MAX, GH_PART_MAX, HYBRID_TITLE_MAX,
                                             hybrid_join, hybrid_project, hybrid_short_title,
                                             hybrid_split, hybrid_title_join, hybrid_title_split,
                                             hybrid_unwrap, hybrid_unwrap_part, hybrid_wrap,
                                             hybrid_wrap_part)
from quenching.specs.commands.doctor import cmd_doctor
from quenching.specs.commands.next import _candidate
from quenching.specs.commands.output import Emitter
from quenching.specs.commands.validate import merge_record_finding, validate_spec
from quenching.specs import backends as backends_mod
from quenching.specs import config as config_mod
from quenching.specs.parse import FIELD_KEYS, PHASES, derive_info, derive_labels
from quenching.specs.parse.edit import upsert_section
from quenching.specs.parse.fields import (legacy_marker_fold, set_frontmatter_key,
                                          set_frontmatter_record)
from quenching.specs.parse.records import spec_records
from quenching.specs.parse.tasks import parse_tasks, task_progress
from quenching.specs.schema import capture_form, load_schema


def _case_doc(title: str = "Alpha") -> str:
    # A FIXED date, never `today()`: it is the fact the case asserts travels intact through
    # each store, and one computed at call time would compare equal to itself no matter what
    # either backend did with it.
    return (capture_form().replace("<TITLE>", title)
            .replace("<DATE>", "2026-01-01").replace("<VERIFICATION>", "per-task"))


def _external_case_doc(title: str = "Alpha") -> str:
    """One small, discriminant document shared by the two external-backend fixtures.

    The document carries every value whose storage is split between the canonical body and
    native tracker fields: title, declared tag, assignee, work-item type, one section and one
    task.  The sequence below owns the order; each transport fixture owns its wire shape and
    remote state.
    """
    doc = _case_doc(title)
    close = doc.index("\n---\n")
    doc = (doc[:close]
           + '\ntags: ["fixture"]\nassignee: fixture@example.test\n'
           + 'workItemType: incidente'
           + doc[close:])
    info = derive_info({"phase": "plans"}, doc)
    doc, _ = upsert_section(info, "Problem", "## Problem\n\nA discriminant fixture.\n")
    info = derive_info({"phase": "plans"}, doc)
    doc, _ = upsert_section(info, "Tasks", "## Tasks\n\n- [ ] 1.1 fixture task\n")
    return doc


def _external_updated_doc(text: str) -> str:
    """Make one write that changes both canonical content and native-backed fields."""
    info = derive_info({"phase": "plans"}, text)
    text, _ = upsert_section(info, "Problem", "## Problem\n\nUpdated by the fixture.\n")
    for key, value in (("tags", '["fixture", "updated"]'),
                       ("assignee", "updated@example.test"),
                       ("start", "2026-01-01"), ("target", "2026-02-01")):
        text = set_frontmatter_key(text, key, value)
    return text


# THE ID IS NATIVE, so the two transports cannot agree on its VALUE and must agree on
# everything else — GitHub's fixture allocates 101, Azure's 201, and demanding they match
# would be demanding one of them invent an identity it does not own. The equivalence
# normalises the value to this sentinel and `IdentityIsAllocatedByTheStore` separately
# asserts what the value has to satisfy: allocated by the store, and the same one at every
# step of the sequence.
NATIVE_ID = "<allocated-by-the-store>"


def _listing(backend: SpecBackend) -> list[dict]:
    """A provider-neutral listing, excluding the native locator and the native ID's value."""
    return [{key: (NATIVE_ID if key == "id" else value)
             for key, value in row.items() if key != "path"}
            for row in backend.list_specs()]


def _external_observable(info: dict | None) -> dict:
    """Canonical read result, excluding locators, parser-only positions and transport state.

    A LEADING UNDERSCORE MEANS "what this transport already had in hand", never a derived
    answer — `github` carries `_github_parts` and `_github_labels` off the read so its next
    write costs no second round trip. `spec-backend.md` §The interface is the document
    forbids a backend DERIVING anything, and none of these do; they are also not part of what
    the two classes must agree on, because one transport having cached what the other cannot
    is exactly the difference between them. Excluding them by prefix keeps the equivalence
    over the canonical fields alone, where a real disagreement would show."""
    if info is None:
        return {}
    result = {key: (NATIVE_ID if key == "id" else value)
              for key, value in info.items()
              if key not in ("path", "text", "sections", "tasks")
              and not key.startswith("_")}
    result["sections"] = {
        heading: {key: section[key] for key in ("filled", "body")}
        for heading, section in info["sections"].items()
    }
    positional = {"lineno", "blockEndLineno", "subjectLineno", "commitLineno",
                  "metaInsertAt", "metaIndent"}
    result["tasks"] = [{key: value for key, value in task.items() if key not in positional}
                       for task in info["tasks"]]
    return result


def _external_sequence(backend: SpecBackend) -> dict:
    """Exercise the five primitives in one shared order against a real backend class.

    The return value is deliberately transport-blind: the later GitHub and Azure tests compare
    these observations while their fixtures separately assert every request they consumed.
    """
    result = {"empty": _listing(backend)}
    backend.create_spec("plans", _external_case_doc())
    result["after_create"] = _listing(backend)

    # THE ID COMES FROM THE LISTING, never from a name the fixture chose. That is the
    # property under test: a spec is resolved by what the store allocated, and the two
    # transports must agree on it without either inventing one.
    spec_id = backend.list_specs()[0]["id"]
    result["allocatedId"] = spec_id
    info, error = backend.read_spec(spec_id)
    if error or info is None:
        raise AssertionError(f"fixture could not read created spec: {error}")
    result["read"] = _external_observable(info)

    backend.write_spec(info, _external_updated_doc(info["text"]))
    updated, error = backend.read_spec(spec_id)
    if error or updated is None:
        raise AssertionError(f"fixture could not read written spec: {error}")
    result["after_write"] = _external_observable(updated)

    backend.move_spec(updated, "archive")
    moved, error = backend.read_spec(spec_id)
    if error or moved is None:
        raise AssertionError(f"fixture could not read moved spec: {error}")
    result["after_move"] = _external_observable(moved)
    result["archive_listing"] = _listing(backend)
    return result


class GithubRemoteFixture:
    """A strict offline `gh` transport with one issue as its remote state."""

    def __init__(self):
        self.calls: list[dict] = []
        self.issues: dict[int, dict] = {}
        self.type_edits: list[tuple[int, str]] = []

    @staticmethod
    def _copy(issue: dict) -> dict:
        return json.loads(json.dumps(issue))

    def _record_api(self, argv: tuple[str, ...], stdin: str | None) -> dict:
        args = list(argv[1:])
        path = next((arg for arg in args if arg.startswith("repos/")), None)
        if path is None:
            raise AssertionError(f"GitHub fixture received no repository endpoint: {argv!r}")
        method = args[args.index("-X") + 1] if "-X" in args else "GET"
        payload = json.loads(stdin) if stdin else None
        self.calls.append({"kind": "api", "method": method, "path": path,
                           "argv": args, "payload": payload})

        if path.endswith("/issues?state=all&per_page=100") and method == "GET":
            return [[self._copy(issue) for issue in self.issues.values()]]

        if path.endswith("/issues") and method == "POST":
            if not isinstance(payload, dict) or set(payload) != {"title", "body", "labels",
                                                                  "assignees"}:
                raise AssertionError(f"unexpected GitHub create payload: {payload!r}")
            number = 101
            self.issues[number] = {
                "number": number, "state": "open", "title": payload["title"],
                "body": payload["body"],
                "labels": [{"name": name} for name in payload["labels"]],
                "assignees": [{"login": name} for name in payload["assignees"]],
                "html_url": f"https://github.test/issues/{number}",
            }
            return self._copy(self.issues[number])

        marker = "/issues/"
        # THE DIRECT READ, which is the whole point of a native ID: `read_spec` asks for one
        # issue by number instead of paginating the tracker to find it. A fixture that only
        # answered the listing would let a backend that still swept pass unnoticed.
        if marker in path and method == "GET":
            number = int(path.rsplit(marker, 1)[1])
            if number not in self.issues:
                raise AssertionError(f"GitHub fixture holds no issue {number}")
            return self._copy(self.issues[number])

        if marker in path and method == "PATCH":
            number = int(path.rsplit(marker, 1)[1])
            issue = self.issues[number]
            if not isinstance(payload, dict):
                raise AssertionError("GitHub mutation did not carry JSON on stdin")
            for key in ("title", "body", "state"):
                if key in payload:
                    issue[key] = payload[key]
            if "labels" in payload:
                issue["labels"] = [{"name": name} for name in payload["labels"]]
            if "assignees" in payload:
                issue["assignees"] = [{"login": name} for name in payload["assignees"]]
            return self._copy(issue)

        raise AssertionError(f"unexpected GitHub API request: {argv!r}, {payload!r}")

    def __call__(self, cwd: str, *argv: str, stdin: str | None = None):
        if argv[:2] == ("issue", "list"):
            self.calls.append({"kind": "lean", "argv": list(argv), "payload": None})
            return 0, json.dumps(getattr(self, "lean_issues", [])), ""
        if argv[:2] == ("issue", "edit"):
            if argv[2:4] != ("101", "--repo") or "--type" not in argv:
                raise AssertionError(f"unexpected GitHub type request: {argv!r}")
            self.type_edits.append((int(argv[2]), argv[argv.index("--type") + 1]))
            return 0, "", ""
        if argv[:1] == ("api",):
            return 0, json.dumps(self._record_api(argv, stdin)), ""
        raise AssertionError(f"unexpected GitHub command: {argv!r}")


class GithubExternalRoundTrip(unittest.TestCase):
    """The GitHub backend's five primitives over a strict, request-driven remote."""

    def test_real_backend_closes_the_common_sequence_over_gh_wire_format(self):
        transport = GithubRemoteFixture()
        backend = GitHubBackend("owner/repo", os.getcwd(),
                                types={"incidente": "Bug"}, open_issues=0)
        with mock.patch.object(gh_mod, "_gh_run", side_effect=transport):
            result = _external_sequence(backend)

        self.assertEqual(result["empty"], [])
        self.assertEqual(result["after_create"][0]["phase"], "plans")
        self.assertEqual(result["read"]["frontmatter"]["tags"], ["fixture"])
        self.assertEqual(result["read"]["frontmatter"]["assignee"], "fixture@example.test")
        self.assertEqual(result["after_write"]["frontmatter"]["tags"],
                         ["fixture", "updated"])
        self.assertEqual(result["after_write"]["frontmatter"]["assignee"],
                         "updated@example.test")
        self.assertEqual(result["after_write"]["frontmatter"]["start"], "2026-01-01")
        self.assertEqual(result["after_move"]["phase"], "archive")
        self.assertEqual(result["archive_listing"][0]["phase"], "archive")

        # THE WIRE SHAPE IS THE MEASUREMENT, and it shows both halves of the read path.
        # The FIRST read costs nothing: `_listing` has just paginated, so the document is
        # already in hand and going back for it would buy a request. The two after it come
        # after a write invalidated the cache, and each is ONE `GET .../issues/101` — the
        # direct fetch the native ID buys, where finding a document by a slug buried in
        # every body cost a full paginated sweep. The `GET .../issues` calls left are
        # `list_specs` asking the question it is actually for.
        api_calls = [call for call in transport.calls if call["kind"] == "api"]
        self.assertEqual([(call["method"], call["path"].split("?")[0])
                          for call in api_calls], [
                              ("GET", "repos/owner/repo/issues"),
                              ("POST", "repos/owner/repo/issues"),
                              ("GET", "repos/owner/repo/issues"),
                              ("PATCH", "repos/owner/repo/issues/101"),
                              ("GET", "repos/owner/repo/issues/101"),
                              ("PATCH", "repos/owner/repo/issues/101"),
                              ("GET", "repos/owner/repo/issues/101"),
                              ("GET", "repos/owner/repo/issues"),
                          ])
        self.assertEqual(sum(1 for call in api_calls
                             if call["path"].split("?")[0].endswith("/issues/101")
                             and call["method"] == "GET"), 2,
                         "a read off a cold cache costs one direct fetch, never a sweep")
        mutations = [call for call in api_calls if call["method"] in ("POST", "PATCH")]
        self.assertTrue(all(call["argv"][-2:] == ["--input", "-"] for call in mutations))
        self.assertTrue(all(call["payload"] for call in mutations))
        # THE MARKER CARRIES NO PAYLOAD. It says "this issue is a spec" and stops there —
        # identity is the issue number, and a marker that also named the spec was a second
        # answer to the same question.
        self.assertTrue(api_calls[1]["payload"]["body"].startswith(
            "<!-- quenching-spec -->\n"))
        self.assertIn("Updated by the fixture.", api_calls[3]["payload"]["body"])
        self.assertEqual(api_calls[1]["payload"]["labels"], ["fixture"])
        self.assertEqual(api_calls[3]["payload"]["labels"], ["fixture", "updated"])
        self.assertEqual(api_calls[5]["payload"], {"state": "closed"})
        self.assertEqual(transport.type_edits, [(101, "Bug")])


class AzureRemoteFixture:
    """A strict offline `az` transport with one work item as its remote state."""

    def __init__(self):
        self.calls: list[dict] = []
        self.items: dict[int, dict] = {}
        self.format_writes: list[str] = []

    @staticmethod
    def _copy(item: dict) -> dict:
        return json.loads(json.dumps(item))

    def _patch(self, argv: tuple[str, ...]) -> dict:
        if argv[0:2] != ("rest", "--method") or argv[2] != "PATCH":
            raise AssertionError(f"unexpected Azure mutation: {argv!r}")
        if argv[argv.index("--resource") + 1] != az_mod.AZ_DEVOPS_RESOURCE_ID:
            raise AssertionError(f"Azure PATCH used the wrong resource: {argv!r}")
        if argv[argv.index("--headers") + 1] != "Content-Type=application/json-patch+json":
            raise AssertionError(f"Azure PATCH used the wrong content type: {argv!r}")
        uri = argv[argv.index("--uri") + 1]
        item_id = int(uri.rsplit("/", 1)[1].split("?", 1)[0])
        path = argv[argv.index("--body") + 1]
        if not path.startswith("@"):
            raise AssertionError("Azure PATCH did not use a request body file")
        with open(path[1:], encoding="utf-8") as stream:
            operations = json.load(stream)
        self.calls.append({"kind": "patch", "uri": uri, "argv": argv,
                           "operations": operations})
        item = self.items[item_id]
        for operation in operations:
            target = operation["path"]
            if target.startswith("/fields/"):
                item["fields"][target.rsplit("/", 1)[1]] = operation["value"]
            elif target.startswith("/multilineFieldsFormat/"):
                self.format_writes.append(target.rsplit("/", 1)[1])
            elif target == "/relations/-":
                item.setdefault("relations", []).append(operation["value"])
            else:
                raise AssertionError(f"unexpected Azure PATCH path: {target}")
        return self._copy(item)

    def __call__(self, cwd: str, *argv: str, stdin: str | None = None):
        del stdin
        if argv[:3] == ("boards", "work-item", "create"):
            if "--project" not in argv or "--type" not in argv or "--title" not in argv:
                raise AssertionError(f"unexpected Azure create request: {argv!r}")
            if "--state" in argv or "--fields" in argv \
                    or argv[argv.index("--org") + 1] != "org":
                raise AssertionError(f"Azure create bypassed the PATCH placement: {argv!r}")
            project = argv[argv.index("--project") + 1]
            title = argv[argv.index("--title") + 1]
            item_id = 201
            self.items[item_id] = {"id": item_id, "fields": {
                "System.Id": item_id, "System.Title": title, "System.State": "New",
            }}
            self.calls.append({"kind": "create", "argv": argv,
                               "project": project, "title": title,
                               "type": argv[argv.index("--type") + 1]})
            return 0, json.dumps({"id": item_id, "fields": self.items[item_id]["fields"]}), ""

        if argv[:2] == ("boards", "query"):
            if argv[argv.index("--org") + 1] != "org":
                raise AssertionError(f"Azure query used the wrong organization: {argv!r}")
            wiql = argv[argv.index("--wiql") + 1]
            expected = az_mod.azure_query_wiql("proj", None, "quenching-spec")
            if wiql != expected:
                raise AssertionError(f"unexpected Azure WIQL: {wiql!r}")
            self.calls.append({"kind": "query", "argv": argv, "wiql": wiql})
            return 0, json.dumps([{"id": item_id} for item_id in self.items]), ""

        if argv[:4] == ("devops", "invoke", "--area", "wit"):
            if argv[argv.index("--resource") + 1] != "workitemsbatch":
                raise AssertionError(f"unexpected Azure batch resource: {argv!r}")
            if argv[argv.index("--org") + 1] != "org":
                raise AssertionError(f"Azure batch used the wrong organization: {argv!r}")
            path = argv[argv.index("--in-file") + 1]
            with open(path, encoding="utf-8") as stream:
                request = json.load(stream)
            fields = request.get("fields") or []
            for required in ("System.Id", "System.Title", "System.State",
                              "System.Description", "System.Tags", "System.AssignedTo",
                              "Microsoft.VSTS.Scheduling.StartDate",
                              "Microsoft.VSTS.Scheduling.TargetDate", "System.Parent"):
                if required not in fields:
                    raise AssertionError(f"Azure batch omitted {required}")
            self.calls.append({"kind": "batch", "argv": argv, "request": request})
            return 0, json.dumps({"value": [self._copy(item) for item in self.items.values()]}), ""

        if argv[:1] == ("rest",):
            return 0, json.dumps(self._patch(argv)), ""
        raise AssertionError(f"unexpected Azure command: {argv!r}")


class AzureExternalRoundTrip(unittest.TestCase):
    """The Azure backend's five primitives over a strict, request-driven remote."""

    def test_real_backend_closes_the_common_sequence_over_az_wire_format(self):
        transport = AzureRemoteFixture()
        backend = AzureBoardsBackend(
            "org", "proj", {"plans": "Active", "archive": "Closed"}, os.getcwd(),
            discovery_tag="quenching-spec",
            types={"incidente": {"description": "fixture", "azure": "Bug"}},
        )
        with mock.patch.object(az_mod, "_az_run", side_effect=transport), \
                contextlib.redirect_stderr(io.StringIO()):
            result = _external_sequence(backend)

        self.assertEqual(result["empty"], [])
        self.assertEqual(result["after_create"][0]["phase"], "plans")
        self.assertEqual(result["read"]["frontmatter"]["tags"], ["fixture"])
        self.assertEqual(result["read"]["frontmatter"]["assignee"], "fixture@example.test")
        self.assertEqual(result["after_write"]["frontmatter"]["tags"],
                         ["fixture", "updated"])
        self.assertEqual(result["after_write"]["frontmatter"]["assignee"],
                         "updated@example.test")
        self.assertEqual(result["after_write"]["frontmatter"]["target"], "2026-02-01")
        self.assertEqual(result["after_move"]["phase"], "archive")
        self.assertEqual(result["archive_listing"][0]["phase"], "archive")

        # `read_spec` off a cold cache is one `batch` for the item named, never a query that
        # sweeps the area to find a slug — the same direct fetch `github`'s
        # `GET .../issues/101` makes; off a warm one it is no call at all. The three `query`
        # calls left are `list_specs`, and this sequence is request-for-request identical to
        # the one before the native ID landed.
        self.assertEqual([call["kind"] for call in transport.calls], [
            "query", "create", "patch", "query", "batch", "patch", "batch", "patch",
            "batch", "query", "batch",
        ])
        create = next(call for call in transport.calls if call["kind"] == "create")
        self.assertEqual(create["type"], "Bug")
        patches = [call for call in transport.calls if call["kind"] == "patch"]
        create_paths = [op["path"] for op in patches[0]["operations"]]
        self.assertIn("/fields/System.Description", create_paths)
        self.assertIn("/multilineFieldsFormat/System.Description", create_paths)
        self.assertEqual(transport.format_writes, ["System.Description"] * 2)
        self.assertTrue(patches[0]["operations"])
        # The payload-free div marker, in the exact shape Azure stores it.
        self.assertIn(
            '<div style="display:none;">quenching-spec </div>',
            next(op["value"] for op in patches[0]["operations"]
                 if op["path"] == "/fields/System.Description"),
        )
        write_paths = [op["path"] for op in patches[1]["operations"]]
        self.assertIn("/fields/System.Tags", write_paths)
        self.assertIn("/fields/Microsoft.VSTS.Scheduling.StartDate", write_paths)
        self.assertIn("/fields/Microsoft.VSTS.Scheduling.TargetDate", write_paths)
        self.assertEqual(patches[2]["operations"], [{
            "op": "add", "path": "/fields/System.State", "value": "Closed",
        }])


class ExternalBackendDiscrimination(unittest.TestCase):
    """The common observations agree while the two remote machines stay independent."""

    def _run_github(self):
        transport = GithubRemoteFixture()
        backend = GitHubBackend("owner/repo", os.getcwd(),
                                types={"incidente": "Bug"}, open_issues=0)
        with mock.patch.object(gh_mod, "_gh_run", side_effect=transport):
            result = _external_sequence(backend)
        return result, transport

    def _run_azure(self):
        transport = AzureRemoteFixture()
        backend = AzureBoardsBackend(
            "org", "proj", {"plans": "Active", "archive": "Closed"}, os.getcwd(),
            discovery_tag="quenching-spec",
            types={"incidente": {"description": "fixture", "azure": "Bug"}},
        )
        with mock.patch.object(az_mod, "_az_run", side_effect=transport), \
                contextlib.redirect_stderr(io.StringIO()):
            result = _external_sequence(backend)
        return result, transport

    def test_the_two_real_classes_agree_on_every_canonical_observation(self):
        github_result, _ = self._run_github()
        azure_result, _ = self._run_azure()
        self.assertEqual(set(github_result), set(azure_result))
        for step in github_result:
            if step == "allocatedId":
                continue  # native by definition — asserted below, never compared
            with self.subTest(step=step):
                self.assertEqual(
                    json.dumps(github_result[step], sort_keys=True, default=str),
                    json.dumps(azure_result[step], sort_keys=True, default=str),
                )

    def test_each_store_allocates_its_own_identity_and_keeps_it_for_the_sequence(self):
        """The half of identity the equivalence cannot assert: each store hands back an ID
        of its own, and the whole sequence resolves against that one value.

        This is what `sp-ambiguous-slug` was retired in favour of — two specs cannot share a
        native ID, so the four-rung tolerant resolution collapses into "it exists or it does
        not". A backend that went back to deriving identity from the document would have to
        produce the SAME value here as the other transport, which is what this refuses."""
        github_result, _ = self._run_github()
        azure_result, _ = self._run_azure()
        gh_id, az_id = github_result["allocatedId"], azure_result["allocatedId"]
        self.assertNotEqual(gh_id, az_id,
                            "a store that agreed with the other on an ID did not allocate it")
        for result, allocated in ((github_result, gh_id), (azure_result, az_id)):
            self.assertTrue(str(allocated).strip(), "an empty ID resolves nothing")
            # Every listing row in the run is the one spec, normalised — so the sequence
            # never silently resolved a second, differently identified document.
            for step in ("after_create", "archive_listing"):
                self.assertEqual([row["id"] for row in result[step]], [NATIVE_ID])

    def test_each_transport_has_its_own_state_and_a_request_for_each_wire_operation(self):
        github_result, github = self._run_github()
        azure_result, azure = self._run_azure()
        del github_result, azure_result

        github_api = [call for call in github.calls if call["kind"] == "api"]
        self.assertEqual(len(github_api), 8)
        self.assertEqual(sum(call["method"] == "POST" for call in github_api), 1)
        self.assertEqual(sum(call["method"] == "PATCH" for call in github_api), 2)
        # A COLD READ IS ONE DIRECT FETCH; A WARM ONE IS NO REQUEST AT ALL. The sequence
        # reads three times and pays for two, because the first follows a listing that
        # already carried the document. The sweeps left belong to `list_specs` alone.
        self.assertEqual(sum(call["method"] == "GET"
                             and call["path"].split("?")[0].endswith("/issues/101")
                             for call in github_api), 2)
        self.assertEqual(sum(call["method"] == "GET"
                             and call["path"].split("?")[0].endswith("/issues")
                             for call in github_api), 3)
        self.assertEqual(len(github.type_edits), 1)

        self.assertEqual([call["kind"] for call in azure.calls], [
            "query", "create", "patch", "query", "batch", "patch", "batch", "patch",
            "batch", "query", "batch",
        ])
        self.assertEqual(sum(call["kind"] == "query" for call in azure.calls), 3)
        self.assertEqual(sum(call["kind"] == "batch" for call in azure.calls), 4)
        self.assertEqual(sum(call["kind"] == "patch" for call in azure.calls), 3)
        self.assertEqual(len(azure.items), 1)
        self.assertEqual(len(github.issues), 1)
        self.assertIsNot(github.issues, azure.items)
        self.assertEqual(github.issues[101]["state"], "closed")
        self.assertEqual(azure.items[201]["fields"]["System.State"], "Closed")
        self.assertIn("Updated by the fixture.", github.issues[101]["body"])
        self.assertIn("Updated by the fixture.", azure.items[201]["fields"]["System.Description"])


# --------------------------------------------------------------------------- #
# gh_refusal — the classifier, asserted against gh's real output
# --------------------------------------------------------------------------- #
# (label, gh exit, stdout, stderr, expected code) — the literal streams `gh` 2.97 produces,
# captured by running it. Every one is exit 2: a refusal, never a finding.
GH_REFUSAL_CASES = (
    ("no binary on PATH", GH_MISSING, "", "", "sp-gh-missing"),
    ("no host authenticated", GH_NOT_AUTHENTICATED, "",
     "To get started with GitHub CLI, please run:  gh auth login\n",
     "sp-gh-unauthenticated"),
    ("a revoked token", 1, '{"message":"Bad credentials","status":"401"}',
     "gh: Bad credentials (HTTP 401)\n", "sp-gh-unauthenticated"),
    ("a repository that is not there", 1, '{"message":"Not Found","status":"404"}',
     "gh: Not Found (HTTP 404)\n", "sp-gh-api-error"),
    ("rate limited", 1,
     '{"message":"API rate limit exceeded for user ID 1.","status":"403"}',
     "gh: API rate limit exceeded (HTTP 403)\n", "sp-gh-api-error"),
)


class GhRefusal(unittest.TestCase):
    """`gh_refusal`, asserted against gh's real output, and the two marker round trips it
    guards on the way past.

    THE ONE THING THIS BACKEND PROMISES BEFORE IT PROMISES ANYTHING ELSE is that no failure
    reaches a human as a traceback and that each one arrives with the remedy that fixes it.
    That promise is decided by string matching on another program's stderr, so the cases hold
    the literal streams rather than a paraphrase of them — a `gh` release that reworded one
    line would break it silently otherwise.

    Self-contained: no network, no `gh`, no repository."""

    DOC = "---\ntitle: Alpha\n---\n\n## Problem\n\nUm problema.\n"

    def test_every_case_classifies_as_an_exit_2_refusal_with_a_message(self):
        for label, code, out, err, want in GH_REFUSAL_CASES:
            with self.subTest(case=label):
                got = gh_refusal("reading a spec", code, out, err)
                self.assertEqual(got.get("code"), want)
                self.assertEqual(got.get("exit"), 2)
                self.assertTrue(str(got.get("message") or "").strip())

    def test_missing_binary_and_unauthenticated_name_gh_auth_login(self):
        # A missing binary or a missing login that did not name the remedy would leave the
        # reader installing the CLI and stopping there.
        for code in (GH_MISSING, GH_NOT_AUTHENTICATED):
            with self.subTest(code=code):
                msg = gh_refusal("reading a spec", code, "", "")["message"]
                self.assertIn("gh auth login", msg)

    def test_comment_marker_round_trip_survives_gh_and_its_crlf(self):
        for label, body in (("as written", hybrid_wrap(self.DOC)),
                            ("as GitHub returns it",
                             hybrid_wrap(self.DOC).replace("\n", "\r\n"))):
            with self.subTest(case=label):
                self.assertEqual(hybrid_unwrap(body), (self.DOC, 1))

    def test_the_marker_this_tool_writes_carries_no_payload(self):
        # Identity is the issue number. A marker that also named the spec was a second
        # answer to the same question, and the one that had to be kept in sync by hand.
        self.assertTrue(hybrid_wrap(self.DOC).startswith("<!-- quenching-spec -->\n"))
        self.assertTrue(hybrid_wrap(self.DOC, fmt="div").startswith(
            '<div style="display:none;">quenching-spec </div>\n'))

    def test_a_marker_with_no_parts_reads_as_a_single_part_document(self):
        # A marker written WITHOUT `parts=` is the form every spec but a spilled one is stored
        # in, and the form every issue already in a repository carries.
        self.assertEqual(hybrid_unwrap("<!-- quenching-spec -->\n" + self.DOC)[1], 1)

    def test_a_legacy_payload_still_reads_and_is_discarded_unread(self):
        # The 154 specs captured before the native ID landed carry `: <slug>.md` in their
        # marker, and none of them is rewritten. The reader accepts the shape and hands back
        # the document alone — the payload is not a third return value any more, because
        # nothing may resolve identity from it.
        for body in ("<!-- quenching-spec: x.md -->\n" + self.DOC,
                     '<div style="display:none;">quenching-spec: x.md </div>\n' + self.DOC):
            with self.subTest(body=body[:40]):
                self.assertEqual(hybrid_unwrap(body), (self.DOC, 1))

    def test_an_issue_with_no_marker_is_not_read_as_a_spec(self):
        self.assertEqual(hybrid_unwrap("An ordinary bug report.\n"), ("", 0))

    def test_div_marker_round_trip_survives_az_and_its_own_normalisation(self):
        # `azure-boards`'s own marker (task 6.1): a comment does not survive
        # `System.Description`, a `display:none` div does. Round-tripped as written, and as
        # the org's own `az` gives it back — the `style` attribute gets a trailing `;` and the
        # marker text a trailing space, measured on the real board.
        for label, body in (
            ("as written", hybrid_wrap(self.DOC, fmt="div")),
            ("as az returns it",
             '<div style="display:none;">quenching-spec </div>\n' + self.DOC),
        ):
            with self.subTest(case=label):
                self.assertEqual(hybrid_unwrap(body), (self.DOC, 1))


# --------------------------------------------------------------------------- #
# GitHubBackend._native_fields
# --------------------------------------------------------------------------- #
GH_NATIVE_FIELD_CASES = (
    ({}, {}, "no labels and no assignees reassembles nothing"),
    ({"labels": [{"name": "bug"}, {"name": "Vertical: Risco"}]},
     {"tags": ["bug", "Vertical: Risco"]}, "every label becomes a tag, in order"),
    ({"assignees": [{"login": "holetz"}, {"login": "second"}]},
     {"assignee": "holetz"},
     "only the FIRST assignee is reflected — the canonical field is singular"),
    ({"labels": [{"name": "bug"}], "assignees": [{"login": "holetz"}]},
     {"tags": ["bug"], "assignee": "holetz"}, "both together"),
)


class GithubNativeFields(unittest.TestCase):
    """`GitHubBackend._native_fields`, over fake issue payloads shaped exactly like the REST
    API's own (`labels: [{name}, …]`, `assignees: [{login}, …]`) — no network, no repository."""

    def test_reassembles_tags_and_assignee_from_labels_and_assignees(self):
        gh = GitHubBackend("owner/repo", ".")
        for issue, want, label in GH_NATIVE_FIELD_CASES:
            with self.subTest(case=label):
                self.assertEqual(gh._native_fields(issue), want)


# --------------------------------------------------------------------------- #
# create_spec's `type` projection
# --------------------------------------------------------------------------- #
class GithubCreateType(unittest.TestCase):
    """`create_spec`'s `type` projection — `_set_type` (`gh issue edit`), never a field on
    the create payload: MEASURED live that the REST create silently drops an invalid `type`
    instead of refusing, which is why `_set_type` is its own porcelain call rather than a JSON
    key. Three branches: a resolved name reaches `_set_type`, no key declared calls it not at
    all, and a key with no `github` translation calls it not at all either but says why on
    stderr — never a refusal, since an entry may exist for one backend only."""

    def setUp(self):
        self.gh = GitHubBackend("owner/repo", ".", types={"incidente": "Bug"})
        self.gh._api = lambda action, *argv, stdin=None: {"number": 1, "html_url": "x"}
        self.applied: list[tuple[int, str]] = []
        self.gh._set_type = lambda number, name: self.applied.append((number, name))

    def test_a_resolved_work_item_type_reaches_set_type(self):
        doc = _case_doc()
        close = doc.index("\n---\n")
        typed = doc[:close] + "\nworkItemType: incidente" + doc[close:]
        self.gh.create_spec("plans", typed)
        self.assertEqual(self.applied, [(1, "Bug")])

    def test_no_declared_work_item_type_calls_set_type_not_at_all(self):
        self.gh.create_spec("plans", _case_doc())
        self.assertEqual(self.applied, [])

    def test_a_type_with_no_github_translation_advises_on_stderr_and_calls_nothing(self):
        doc = _case_doc()
        close = doc.index("\n---\n")
        untranslated = doc[:close] + "\nworkItemType: tarefa" + doc[close:]
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            self.gh.create_spec("plans", untranslated)
        self.assertEqual(self.applied, [])
        self.assertIn("tarefa", stderr.getvalue())

    def test_set_type_on_an_impossible_cwd_raises_a_backend_refusal_that_exits_2(self):
        # Unmocked: a `cwd` that cannot exist makes `_gh_run` fail exactly as a real `gh`
        # refusal would, self-contained and with no network — proving the raise reaches the
        # caller as `BackendRefusal`, classified by the same `gh_refusal` every other
        # transport failure already is.
        broken = GitHubBackend("owner/repo", "/does/not/exist")
        with self.assertRaises(BackendRefusal) as ctx:
            broken._set_type(1, "Bug")
        self.assertEqual(ctx.exception.err.get("exit"), 2)


# --------------------------------------------------------------------------- #
# the GitHub issue body ceiling
# --------------------------------------------------------------------------- #
class GhBodyCeiling(unittest.TestCase):
    """A body over the ceiling refuses BEFORE any call is made — proved with a transport that
    records every call it is asked to make and fails the check if it was asked at all.

    No network and no `gh`: the point is not that GitHub says no, it is that this backend
    never gives it the chance."""

    def setUp(self):
        self.backend = GitHubBackend("owner/repo", os.getcwd())
        self.calls: list[str] = []
        self.backend._api = lambda action, *argv, stdin=None: self.calls.append(action)

    def test_an_oversized_body_refuses_and_makes_no_call(self):
        with self.assertRaises(BackendRefusal) as ctx:
            self.backend._write_api("creating an issue", "POST", "repos/owner/repo/issues",
                                    {"title": "x", "body": "a" * (GH_BODY_MAX + 1)})
        self.assertEqual(ctx.exception.err.get("code"), "sp-gh-body-too-large")
        self.assertEqual(ctx.exception.err.get("exit"), 2)
        self.assertEqual(self.calls, [])

    def test_a_body_exactly_at_the_ceiling_is_accepted_the_ceiling_is_inclusive(self):
        self.backend._write_api("creating an issue", "POST", "repos/owner/repo/issues",
                                {"title": "x", "body": "a" * GH_BODY_MAX})
        self.assertEqual(len(self.calls), 1)


# --------------------------------------------------------------------------- #
# the gh transport's bounded retry contract
# --------------------------------------------------------------------------- #
class GhTransport(unittest.TestCase):
    """Transient transport failures retry three times at most and keep the final attempt."""

    def test_timeout_retries_then_becomes_a_named_refusal(self):
        timeout = subprocess.TimeoutExpired(["gh", "api"], 30)
        with mock.patch("subprocess.run", side_effect=timeout), \
                mock.patch.object(gh_mod.time, "sleep") as sleep:
            result = gh_mod._gh_run(os.getcwd(), "api")

        self.assertEqual(result[0], gh_mod.GH_TIMEOUT)
        self.assertEqual(result[3], 3)
        self.assertEqual(len(sleep.call_args_list), 2)
        refusal = gh_mod.gh_refusal("reading a spec", *result[:3], attempts=result[3])
        self.assertEqual(refusal["code"], "sp-gh-timeout")
        self.assertEqual(refusal["attempts"], 3)

    def test_rate_limit_retries_and_success_keeps_attempt_count(self):
        failed = subprocess.CompletedProcess(
            ["gh", "api"], 1, stdout='{"message":"rate limit"}',
            stderr="gh: API rate limit exceeded (HTTP 429)\n")
        passed = subprocess.CompletedProcess(["gh", "api"], 0, stdout="{}", stderr="")
        with mock.patch("subprocess.run", side_effect=[failed, passed]), \
                mock.patch.object(gh_mod.time, "sleep") as sleep:
            result = gh_mod._gh_run(os.getcwd(), "api")

        self.assertEqual(result[:3], (0, "{}", ""))
        self.assertEqual(result[3], 2)
        sleep.assert_called_once_with(gh_mod.GH_RETRY_BACKOFF[0])

    def test_permanent_api_error_is_not_retried(self):
        failed = subprocess.CompletedProcess(
            ["gh", "api"], 1, stdout='{"message":"Not Found"}',
            stderr="gh: Not Found (HTTP 404)\n")
        with mock.patch("subprocess.run", return_value=failed), \
                mock.patch.object(gh_mod.time, "sleep") as sleep:
            result = gh_mod._gh_run(os.getcwd(), "api")

        self.assertEqual(result[0], 1)
        self.assertEqual(result[3], 1)
        sleep.assert_not_called()


# --------------------------------------------------------------------------- #
# a listing that never arrived, told apart from a front that is genuinely empty
# --------------------------------------------------------------------------- #
class GhEmptyListing(unittest.TestCase):
    """The incident this guard exists for, as an assertion: a listing that fails to arrive
    must refuse, never report itself as an empty front with `ok: true` and exit 0.

    `_gh_run` is what gets patched, never `_api` — the laundering under test IS `_api`'s own
    `json.loads(out or "null")`, the line that turns "gh printed nothing" into data, and a
    stub one level higher would step straight over it. No network and no `gh`."""

    def setUp(self):
        self.backend = GitHubBackend("owner/repo", os.getcwd(), open_issues=38)

    def _load_returning(self, stdout: str, open_issues: int | None = 38):
        self.backend.open_issues = open_issues
        with mock.patch.object(gh_mod, "_gh_run", lambda cwd, *a, **k: (0, stdout, "")):
            return self.backend._load()

    def test_empty_stdout_with_exit_0_refuses_instead_of_reporting_an_empty_front(self):
        with self.assertRaises(BackendRefusal) as ctx:
            self._load_returning("")
        self.assertEqual(ctx.exception.err.get("code"), "sp-gh-empty-listing")
        self.assertEqual(ctx.exception.err.get("exit"), 2)

    def test_zero_pages_refuses_because_an_empty_front_answers_with_one_empty_page(self):
        with self.assertRaises(BackendRefusal) as ctx:
            self._load_returning("[]")
        self.assertEqual(ctx.exception.err.get("code"), "sp-gh-empty-listing")

    def test_one_empty_page_is_a_genuinely_empty_front_and_does_not_refuse(self):
        self.assertEqual(self._load_returning("[[]]", open_issues=0), [])

    def test_a_write_whose_legitimate_answer_is_empty_still_does_not_refuse(self):
        # The DELETE of a stale continuation comment: GitHub answers 204 No Content, `gh`
        # prints nothing, and `None` is the RIGHT answer there. This case is the whole
        # reason the guard belongs to the caller and never to `_api`.
        with mock.patch.object(gh_mod, "_gh_run", lambda cwd, *a, **k: (0, "", "")):
            self.assertIsNone(self.backend._api(
                "deleting a stale continuation comment on #1",
                "-X", "DELETE", "repos/owner/repo/issues/comments/1"))

    def test_a_healthy_listing_passes_the_predicate_untouched(self):
        self.assertIsNone(empty_listing_refusal("listing", [[{"number": 1}], [{"number": 2}]]))


# --------------------------------------------------------------------------- #
# the OTHER half: an empty front that may be genuine, said out loud as a suspicion
# --------------------------------------------------------------------------- #
class GhListingSuspect(unittest.TestCase):
    """`[[]]` — one empty page — is a shape that proves nothing on its own. A positive open-issue
    count now makes the contradiction strong enough for the listing guard to refuse.

    A repository with no open issues, or with an unknown count, remains an allowed empty result.

    The process-level flag is restored, so this class cannot change what a later test or a
    later command prints."""

    def setUp(self):
        self._held = set(gh_mod._LISTING_SUSPECT_ANNOUNCED)
        gh_mod._LISTING_SUSPECT_ANNOUNCED.clear()
        self.addCleanup(self._restore)

    def _restore(self):
        gh_mod._LISTING_SUSPECT_ANNOUNCED.clear()
        gh_mod._LISTING_SUSPECT_ANNOUNCED.update(self._held)

    def _load_empty(self, open_issues):
        backend = GitHubBackend("owner/repo", os.getcwd(), open_issues=open_issues)
        err, out = io.StringIO(), io.StringIO()
        with mock.patch.object(gh_mod, "_gh_run", lambda cwd, *a, **k: (0, "[[]]", "")), \
                contextlib.redirect_stderr(err), contextlib.redirect_stdout(out):
            rows = backend._load()
        return rows, err.getvalue(), out.getvalue()

    def test_zero_rows_with_open_issues_refuses_instead_of_being_read_as_empty(self):
        with self.assertRaises(BackendRefusal) as ctx:
            self._load_empty(38)
        self.assertEqual(ctx.exception.err["code"], "sp-gh-empty-listing")

    def test_zero_rows_with_no_open_issues_says_nothing(self):
        # A repository with no issues at all corroborates nothing, and a warning here would
        # fire on every fresh workspace — the noise that trains a reader to ignore the line.
        self.assertEqual(self._load_empty(0)[1], "")

    def test_an_unknown_count_is_never_read_as_zero_and_never_as_proof(self):
        self.assertEqual(self._load_empty(None)[1], "")

    def test_empty_result_never_reaches_stdout_where_the_json_payload_is(self):
        self.assertEqual(self._load_empty(0)[2], "")

    def test_the_warning_is_one_line_per_process_and_not_one_per_call(self):
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            gh_mod.announce_listing_suspect("owner/repo", 38)
            gh_mod.announce_listing_suspect("owner/repo", 38)
        self.assertEqual(err.getvalue().count("warning:"), 1)

    def test_a_front_that_read_rows_is_never_suspect_however_many_issues_are_open(self):
        self.assertFalse(listing_is_suspect(1, 38))


class GhLeanListing(unittest.TestCase):
    """The cheap index shares the empty-list guard and refuses its hard result ceiling."""

    def _lean(self, issues, open_issues):
        backend = GitHubBackend("owner/repo", os.getcwd(), open_issues=open_issues)
        with mock.patch.object(gh_mod, "_gh_run",
                               return_value=(0, json.dumps(issues), "")):
            return backend._lean_rows()

    def test_empty_lean_listing_with_open_issues_is_a_refusal(self):
        with self.assertRaises(BackendRefusal) as ctx:
            self._lean([], 38)
        self.assertEqual(ctx.exception.err["code"], "sp-gh-empty-listing")
        self.assertEqual(ctx.exception.err["openIssues"], 38)

    def test_empty_lean_listing_without_positive_count_is_allowed(self):
        self.assertEqual(self._lean([], 0), [])
        self.assertEqual(self._lean([], None), [])

    def test_lean_listing_at_the_gh_limit_refuses_as_potentially_truncated(self):
        with self.assertRaises(BackendRefusal) as ctx:
            self._lean([{}] * gh_mod.GH_LEAN_LIMIT, 0)
        self.assertEqual(ctx.exception.err["code"], "sp-gh-lean-truncated")
        self.assertEqual(ctx.exception.err["limit"], gh_mod.GH_LEAN_LIMIT)

    def test_lean_limit_refusal_names_the_observed_ceiling(self):
        refusal = gh_mod.lean_limit_refusal("listing specs", gh_mod.GH_LEAN_LIMIT, attempts=2)
        self.assertEqual(refusal["observed"], gh_mod.GH_LEAN_LIMIT)
        self.assertEqual(refusal["attempts"], 2)
        self.assertIn("paginate below the limit", refusal["message"])

    def test_lean_listing_below_the_limit_projects_spec_rows(self):
        rows = self._lean([{"number": 12, "title": "Alpha", "state": "OPEN",
                            "labels": [{"name": "spec:approved"}]}], 0)
        self.assertEqual(rows, [{
            "id": 12, "title": "Alpha", "state": "open",
            "records": ["spec:approved"], "phase": "plans", "folder": "plans",
            "legacy": False, "path": "https://github.com/owner/repo/issues/12",
        }])

    def test_lean_preserves_a_transport_timeout_and_its_attempt_count(self):
        backend = GitHubBackend("owner/repo", os.getcwd(), open_issues=0)
        with mock.patch.object(gh_mod, "_gh_run",
                               return_value=(gh_mod.GH_TIMEOUT, "", "timed out", 3)):
            with self.assertRaises(BackendRefusal) as ctx:
                backend.list_specs(lean=True)
        self.assertEqual(ctx.exception.err["code"], "sp-gh-timeout")
        self.assertEqual(ctx.exception.err["attempts"], 3)

    def test_remote_fixture_answers_the_real_gh_issue_list_wire_shape(self):
        transport = GithubRemoteFixture()
        transport.lean_issues = [{
            "number": 17, "title": "Lean", "state": "OPEN",
            "labels": [{"name": "spec:built"}],
        }]
        backend = GitHubBackend("owner/repo", os.getcwd(), open_issues=0)
        with mock.patch.object(gh_mod, "_gh_run", side_effect=transport):
            self.assertEqual(backend.list_specs(lean=True)[0]["id"], 17)
        self.assertEqual([call["kind"] for call in transport.calls], ["lean"])
        self.assertIn("--limit", transport.calls[0]["argv"])
        self.assertIn(str(gh_mod.GH_LEAN_LIMIT), transport.calls[0]["argv"])


# --------------------------------------------------------------------------- #
# the hybrid serialisation both external backends share
# --------------------------------------------------------------------------- #
# The fields `parse_tasks` derives, minus the ones a rebuild reproduces only because the
# document does: `lineno`/`blockEndLineno`/`metaInsertAt`/`metaIndent`/`subjectLineno`/
# `commitLineno` are POSITIONS. They are covered by the byte-for-byte equality checks
# elsewhere in this class — a document that comes back identical necessarily reparses to the
# same line numbers — so this tuple stays what it is: the semantic comparison that names WHICH
# task drifted when the stricter check has already said the document did.
HYBRID_TASK_SEMANTIC_KEYS = ("id", "state", "checked", "blocked", "reason", "text", "parallel",
                             "files", "pattern", "verify", "subject", "commit")


class HybridSerialization(unittest.TestCase):
    """The one obligation `spec-backend.md` puts on an external backend: it reassembles the
    canonical document on read, BYTE FOR BYTE.

    It used to be a hard claim, because `## Tasks` was stored apart from the rest and the
    document had to be rebuilt from an anchored pile of blocks. With the whole document in one
    body the claim is nearly free — which is most of why the mapping was retired — and what is
    left to prove is the part that is still real:

    - a document under the ceiling is ONE part, stored and returned unchanged;
    - a document over it splits, and the parts JOIN BACK to exactly what went in;
    - both survive the CRLF a tracker really stores bodies with, applied per part, because
      that is how the parts come back — separately, each normalised on its own;
    - `parse_tasks` reads the same tasks out the other end, since that shared derivation is the
      only thing that ever decides a task is checked or blocked.

    The fixture stays grouped under `### N.` headings with a line of prose inside `## Tasks`. It
    was written for the loss that motivated it — the shell used to empty that section, and 47 of
    this repository's 66 specs came back a structure short with no error anywhere — and it stays
    because a split is still free to cut through a group heading.

    Self-contained: no network, no `gh`."""

    DOC = ("---\ntitle: Alpha\nverification: per-task\n---\n\n"
          "## Problem\n\nAlgo.\n\n"
          "## Tasks\n\n"
          "### 1. Primeiro grupo\n\n"
          "Uma linha de prosa dentro de `## Tasks`, que tambem tem de voltar.\n\n"
          "- [ ] 1.1 primeira\n      files: a.py, b.py\n      verify: pytest\n"
          "- [x] 1.2 segunda\n\n"
          "### 2. Segundo grupo\n\n"
          "- [!] 2.1 terceira — blocked: esperando review\n\n"
          "- [ ] [P] quarta sem id\n\n"
          "## Outcome\n\n")

    # THE FIXTURE IS THE SHAPE OF A REAL DOCUMENT, not a minimal one. Three properties, each
    # from a way this repository's own specs really look: an accented title, because the
    # harness language is pt-BR and an accent is where a title projection loses bytes if it
    # ever re-encodes; `### N.` groups with prose inside `## Tasks`, because 49 of 68 specs
    # carry groups and that is precisely the structure the retired sub-issue mapping dropped;
    # and task metadata lines, because they are what a split is most likely to cut through.
    CANONICAL = (
        "---\nslug: alpha\ntitle: Avaliar o fluxo de criação de specs\ndate: 2026-01-01\n"
        "verification: per-section\n---\n\n"
        "# Avaliar o fluxo de criação de specs\n\n"
        "## Problem\n\nO documento não volta como entrou.\n\n"
        "## Tasks\n\n"
        "### 1. Primeiro grupo\n\n"
        "Uma linha de prosa dentro de `## Tasks`, que também tem de voltar.\n\n"
        "- [ ] 1.1 primeira\n      files: a.py, b.py\n      verify: pytest\n"
        "- [x] 1.2 segunda\n\n"
        "### 2. Segundo grupo\n\n"
        "- [!] 2.1 terceira — blocked: esperando revisão\n\n"
        "## Outcome\n\n")

    # The same document over GitHub's 65,536 ceiling. This is the case the title projection
    # makes newly interesting: the frontmatter and the `# <TITLE>` heading it removes both
    # live in the HEAD chunk, which is exactly the chunk a spill cuts. Two of this
    # repository's specs are over the ceiling as whole documents, one of them an active plan.
    BIG = CANONICAL.replace(
        "## Outcome\n\n",
        "### 3. Grupo grande\n\n"
        + "".join(f"- [ ] 3.{i} tarefa com acentuação — número {i}\n"
                  for i in range(1, 2600))
        + "\n## Outcome\n\n")

    def _store(self, chunks: list[tuple[str, bool]]) -> str:
        """What comes back after a store-and-reload, with each part CRLF'd on its own."""
        wrapped = [hybrid_wrap(chunks[0][0], len(chunks))] + [
            hybrid_wrap_part(i, len(chunks), c, eol)
            for i, (c, eol) in enumerate(chunks[1:], start=2)]
        stored = [w.replace("\n", "\r\n") for w in wrapped]
        head, parts = hybrid_unwrap(stored[0])
        self.assertEqual(parts, len(chunks),
                         "the marker declared a different part count than the document has "
                         "— a reader would stop early or ask for one too many")
        back = [(head, False)]
        for body in stored[1:]:
            index, chunk, eol = hybrid_unwrap_part(body)
            self.assertTrue(index, "a continuation comment did not read back as one")
            back.append((chunk, eol))
        return hybrid_join(back)

    def test_a_one_part_document_round_trips_byte_for_byte(self):
        # ONE PART — the case every spec in this repository but two takes.
        whole = hybrid_split(self.DOC, GH_PART_MAX)
        self.assertEqual(len(whole), 1)
        self.assertEqual(self._store(whole), self.DOC)

    def test_a_spilled_document_joins_back_byte_for_byte(self):
        # MANY PARTS, forced with a ceiling small enough that this fixture spills. A real
        # spill is a 70 KB document and would make the check unreadable; what a split has to
        # survive is the same either way, and a small ceiling exercises MORE boundaries per
        # character, including cuts that land inside a group and inside a task's own metadata
        # block.
        spilled = hybrid_split(self.DOC, 90)
        self.assertGreaterEqual(len(spilled), 3,
                                "a 90-character ceiling did not exercise the multi-part path")
        for chunk, _ in spilled:
            self.assertLessEqual(len(chunk), 90,
                                 "a chunk came back over the ceiling it was split to")
        self.assertEqual(self._store(spilled), self.DOC)

    def test_a_line_longer_than_one_part_survives_the_split_without_hanging(self):
        # The pathological single line longer than a whole part. It must not hang and it must
        # not lose a byte; nothing in this repository takes this branch, and a split that
        # could not make progress would take it as an infinite loop rather than as an error.
        long_line = "x" * 250 + "\n"
        cut = hybrid_split(long_line, 90)
        self.assertEqual(hybrid_join(cut), long_line)

    def test_a_rebuilt_document_reparses_to_the_same_tasks(self):
        # A part joined back must reparse to the same tasks — the shared derivation is the
        # only thing that reads state, so this is what "identical" means to every caller
        # downstream.
        tasks = parse_tasks(self.DOC)
        tasks2 = parse_tasks(self._store(hybrid_split(self.DOC, 90)))
        self.assertEqual(len(tasks2), len(tasks))
        for before, after in zip(tasks, tasks2):
            with self.subTest(task=before["id"] or before["index"]):
                b = {k: before[k] for k in HYBRID_TASK_SEMANTIC_KEYS}
                a = {k: after[k] for k in HYBRID_TASK_SEMANTIC_KEYS}
                self.assertEqual(a, b)

    def test_an_ordinary_comment_is_not_read_as_a_continuation_part(self):
        # A comment a human left on a spec issue is not a document part. The reverse of the
        # marker rule one level up: a repo's issues belong to its humans, and a backend that
        # read every comment as its own storage would splice a note into the middle of the
        # spec.
        index, _, _ = hybrid_unwrap_part("Concordo, mas a task 2.1 depende da 1.2.\n")
        self.assertFalse(index)

    def test_hybrid_short_title_cuts_on_a_word_boundary_and_marks_the_cut(self):
        # THE TITLE IS CUT, THE DOCUMENT IS NOT. The tracker caps a title; the body is the
        # only half `parse_tasks` ever reads. This repository's own longest task line is 946
        # characters, so the cut is exercised on a length it really carries.
        long_text = "9.9 " + " ".join(f"palavra{i:03d}" for i in range(120))
        short = hybrid_short_title(long_text)
        self.assertLessEqual(len(short), HYBRID_TITLE_MAX)
        self.assertTrue(short.endswith("…"))
        self.assertTrue(long_text.startswith(short[:-1].rstrip()),
                        "a cut title is not a prefix of the line it came from")

    def test_hybrid_short_title_leaves_a_title_that_already_fits_untouched(self):
        self.assertEqual(hybrid_short_title("9.9 curta"), "9.9 curta")

    def test_the_big_fixture_actually_crosses_the_github_body_ceiling(self):
        self.assertGreater(len(self.BIG), GH_BODY_MAX,
                           "the over-ceiling fixture does not reach the ceiling it exists "
                           "to cross")

    def test_title_projection_removes_the_duplicated_title_and_is_reversible(self):
        # THE TITLE PROJECTION, on the shape `new` actually stamps. What the store holds must
        # carry neither `title:` nor the `# <TITLE>` heading, and putting the native title
        # back must return the document byte for byte — the same obligation the body is held
        # to, on the one field that is no longer inside it.
        proj = hybrid_title_split(self.CANONICAL)
        self.assertIsNotNone(
            proj, "the capture form's own shape was refused by the title projection — every "
                  "spec `new` creates would be stored with a duplicated title")
        stored, native = proj
        self.assertNotIn("title:", stored)
        self.assertNotIn(f"# {native}", stored)
        self.assertEqual(native, str(parse_frontmatter(self.CANONICAL).get("title", "")).strip())
        self.assertEqual(hybrid_title_join(stored, native), self.CANONICAL)

    def test_title_projection_refuses_a_document_outside_the_capture_shape(self):
        # A document the projection REFUSES is stored whole, and a read must not then graft a
        # second title onto it. `DOC` is exactly that shape: no `slug:`, no heading.
        self.assertIsNone(hybrid_title_split(self.DOC))
        self.assertEqual(hybrid_title_join(self.DOC, "whatever the tracker says"), self.DOC)

    def test_round_trip_is_identical_across_github_and_azure_boards_ceilings(self):
        # THE SAME ROUND TRIP, AGAINST BOTH EXTERNAL BACKENDS — each with the ceiling it
        # really passes to `hybrid_split`: `github` splits at GH_PART_MAX, `azure-boards`
        # hands None and gets one chunk. Two stores that serialise a title differently is the
        # drift `spec-backend.md` forbids, and it is cheap to refute here: the projection, the
        # wrap, the split and the reassembly are the whole write path, and none of it needs a
        # network.
        for backend_name, ceiling in (("github", GH_PART_MAX), ("azure-boards", None)):
            for label, source in (("one part", self.CANONICAL), ("over the ceiling", self.BIG)):
                with self.subTest(backend=backend_name, doc=label):
                    stored, native = hybrid_project(source)
                    self.assertEqual(native,
                                     str(parse_frontmatter(source).get("title", "")).strip())
                    self.assertNotIn("title:", stored.split("\n---\n", 1)[0])
                    rebuilt = hybrid_title_join(self._store(hybrid_split(stored, ceiling)),
                                               native)
                    self.assertEqual(rebuilt, source)

    def test_a_quoted_title_is_refused_by_the_projection(self):
        # A QUOTED title is refused, and this one was found by the corpus rather than by
        # reasoning. `title: "…"` parses to the same string with the quotes gone, so a rebuild
        # from the value writes an unquoted line and the document comes back two characters
        # short — 4 of this repository's 73 specs quote their title, and all four failed the
        # byte-for-byte round trip before the raw line was checked instead of the parsed value.
        quoted = self.CANONICAL.replace(
            "title: Avaliar o fluxo de criação de specs\n",
            'title: "Avaliar o fluxo de criação de specs"\n', 1)
        self.assertIsNone(hybrid_title_split(quoted))

    def test_a_title_over_the_trackers_ceiling_is_refused(self):
        # A title the tracker would cut is refused, because a cut title is now a renamed spec.
        long_title = ("---\nslug: alpha\ntitle: " + "t" * (HYBRID_TITLE_MAX + 1) +
                     "\ndate: 2026-01-01\n---\n\n# " + "t" * (HYBRID_TITLE_MAX + 1) +
                     "\n\n## Problem\n\nAlgo.\n")
        self.assertIsNone(hybrid_title_split(long_title))

    def test_the_marker_fold_moves_the_capture_date_out_of_the_basename(self):
        # The marker fold is the only thing that moves a capture date out of a basename.
        folded = legacy_marker_fold("2026-07-25-alpha.md", self.CANONICAL)
        self.assertIsNotNone(folded)
        self.assertEqual(folded[0], "alpha.md")
        # The basename's copy is never allowed to win over a `date:` the document already
        # declares.
        self.assertEqual(str(parse_frontmatter(folded[1]).get("date", "")), "2026-01-01")

    def test_the_marker_fold_carries_the_basenames_date_when_the_document_has_none(self):
        # The prefix is the only copy of the capture date, so dropping it without moving it
        # would lose it outright.
        undated = self.CANONICAL.replace("date: 2026-01-01\n", "", 1)
        folded = legacy_marker_fold("2026-07-25-alpha.md", undated)
        self.assertIsNotNone(folded)
        self.assertEqual(str(parse_frontmatter(folded[1]).get("date", "")), "2026-07-25")

    def test_the_marker_fold_does_not_fire_on_an_already_folded_basename(self):
        undated = self.CANONICAL.replace("date: 2026-01-01\n", "", 1)
        self.assertIsNone(legacy_marker_fold("alpha.md", undated))




class ProviderSelection(unittest.TestCase):
    def setUp(self):
        backends_mod._BACKEND_CACHE.clear()
        self.addCleanup(backends_mod._BACKEND_CACHE.clear)

    def test_repository_hosts_select_the_external_provider(self):
        cases = (
            ("git@github.com:owner/repo.git", "github", "github.com"),
            ("https://dev.azure.com/org/project/_git/repo", "azure-boards", "dev.azure.com"),
            ("https://forge.example.test/org/repo.git", None, "forge.example.test"),
        )
        with tempfile.TemporaryDirectory() as tmp:
            for remote, provider, host in cases:
                with self.subTest(remote=remote):
                    def current_git(_cwd, *argv, remote=remote):
                        if argv == ("rev-parse", "--show-toplevel"):
                            return tmp
                        if argv == ("remote", "get-url", "origin"):
                            return remote
                        return ""
                    with mock.patch.object(config_mod, "_git", side_effect=current_git):
                        self.assertEqual(config_mod.detect_provider(tmp), (provider, host))

    def test_factory_opens_the_provider_selected_by_the_repository(self):
        sentinel = object()
        with mock.patch.object(backends_mod, "load_config",
                               return_value={"backend": "github"}),                 mock.patch.object(backends_mod, "open_github_backend",
                                  return_value=(sentinel, {})) as opener:
            backend, error = backends_mod.open_backend("/repo")
        self.assertIs(backend, sentinel)
        self.assertEqual(error, {})
        opener.assert_called_once_with("/repo")

    def test_legacy_files_configuration_refuses_before_any_local_store_is_created(self):
        with mock.patch.object(backends_mod, "load_config", return_value={
                "backend": None, "unknownBackend": "files"}):
            backend, error = backends_mod.open_backend("/repo")
        self.assertIsNone(backend)
        self.assertEqual(error["code"], "sp-backend-removed")
        self.assertEqual(error["exit"], 2)
        self.assertIn("no local store", error["message"])

    def test_unknown_provider_refuses_without_falling_back_to_a_local_backend(self):
        with mock.patch.object(backends_mod, "load_config", return_value={
                "backend": None, "unknownProvider": "forge.example.test"}):
            backend, error = backends_mod.open_backend("/repo")
        self.assertIsNone(backend)
        self.assertEqual(error["code"], "sp-provider-unknown")
        self.assertEqual(error["exit"], 2)
        self.assertNotIn("files", error["message"])


if __name__ == "__main__":
    unittest.main()
