"""The `github` backend carries `dependsOn` as native issue dependencies ("blocked by").

Every case runs offline: the pure helpers take plain data, and the backend cases further down
drive a strict request-driven double of `gh api` patched over `_gh_run`. No test reaches a
real repository.
"""

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from unittest import mock

import _paths  # noqa: F401  — must precede the `quenching` import; see its docstring
import quenching.specs.backends.github as gh_mod
from quenching.specs import backends as backends_mod
from quenching.specs import mcp
from quenching.specs.backends.base import BackendRefusal
from quenching.specs.parse.fields import set_frontmatter_key
from test_specs_backends import GithubRemoteFixture, _external_case_doc
from quenching.specs.backends.azure import azure_predecessor_ids
from quenching.specs.backends.github import (
    GH_DEPENDENCY_LIMIT,
    GitHubBackend,
    github_blocked_by,
    github_dependency_diff,
    github_dependency_limit_refusal,
)


class PureDependencies(unittest.TestCase):
    def test_wanted_ids_keep_numeric_non_self_in_order_without_duplicates(self):
        fm = {"dependsOn": ["30", "slug", "owner/repo#4", "7", "30", "12"]}
        self.assertEqual([30, 7], azure_predecessor_ids(fm, 12))

    def test_the_current_set_comes_from_a_blocked_by_listing_page_or_pages(self):
        page = [{"number": 3, "id": 903}, {"number": 5, "id": 905}, {"title": "no number"}]
        self.assertEqual({3: 903, 5: 905}, github_blocked_by(page))
        self.assertEqual({3: 903, 5: 905}, github_blocked_by([page[:1], page[1:]]))
        self.assertEqual({}, github_blocked_by([]))
        self.assertEqual({}, github_blocked_by(None))

    def test_add_remove_and_no_op(self):
        current = {3: 903, 5: 905}
        self.assertEqual(([7], []), github_dependency_diff(current, [3, 5, 7]))
        self.assertEqual(([], [3]), github_dependency_diff(current, [5]))
        self.assertEqual(([7], [3, 5]), github_dependency_diff(current, [7]))
        self.assertEqual(([], []), github_dependency_diff(current, [5, 3]))
        self.assertEqual(([], []), github_dependency_diff({}, []))

    def test_over_the_limit_refuses_and_at_the_limit_does_not(self):
        at = list(range(1, GH_DEPENDENCY_LIMIT + 1))
        self.assertIsNone(github_dependency_limit_refusal(9, at))
        refusal = github_dependency_limit_refusal(9, at + [GH_DEPENDENCY_LIMIT + 1])
        self.assertEqual(("sp-gh-dependency-limit", 2), (refusal["code"], refusal["exit"]))
        self.assertIn("#9", refusal["message"])
        self.assertIn("new issue", github_dependency_limit_refusal(None, at + [999])["message"])


class DependencyFixture(GithubRemoteFixture):
    """The strict `gh` double plus the blocked-by endpoints and two plain issues (#3, #5)
    that a spec may wait for, each with a REST `id` of `900 + number`."""

    def __init__(self):
        super().__init__()
        self.blocked_by: dict[int, list[int]] = {}
        for number in (3, 5):
            self.issues[number] = {"number": number, "id": 900 + number, "state": "open",
                                   "title": f"plain {number}", "body": "", "labels": [],
                                   "assignees": []}

    def _record_api(self, argv, stdin):
        args = list(argv[1:])
        path = next(arg for arg in args if arg.startswith("repos/"))
        if "/dependencies/blocked_by" not in path:
            return super()._record_api(argv, stdin)
        method = args[args.index("-X") + 1] if "-X" in args else "GET"
        payload = json.loads(stdin) if stdin else None
        self.calls.append({"kind": "api", "method": method, "path": path,
                           "argv": args, "payload": payload})
        head, _, tail = path.partition("/dependencies/blocked_by")
        number = int(head.rsplit("/", 1)[1])
        held = self.blocked_by.setdefault(number, [])
        if method == "GET":
            return [[{"number": n, "id": 900 + n} for n in held]]
        if method == "POST":
            held.append(int(payload["issue_id"]) - 900)
            return {"number": held[-1], "id": payload["issue_id"]}
        if method == "DELETE":
            held.remove(int(tail.strip("/")) - 900)
            return None
        raise AssertionError(f"unexpected dependency request: {argv!r}")

    def dependency_calls(self):
        return [c for c in self.calls if "/dependencies/" in c["path"]]


def _with_deps(text: str, deps: str) -> str:
    return set_frontmatter_key(text, "dependsOn", deps)


class BackendDependencies(unittest.TestCase):
    def setUp(self):
        self.transport = DependencyFixture()
        self.backend = GitHubBackend("owner/repo", os.getcwd(),
                                     types={"incidente": "Bug"}, open_issues=0)
        patcher = mock.patch.object(gh_mod, "_gh_run", side_effect=self.transport)
        patcher.start()
        self.addCleanup(patcher.stop)

    def _create(self, deps="[3]"):
        self.backend.create_spec("plans", _with_deps(_external_case_doc(), deps))
        return self.backend.read_spec(101)[0]

    def test_a_spec_born_with_depends_on_is_blocked_by_those_issues(self):
        self._create("[3, 101, slug]")
        posts = [c for c in self.transport.dependency_calls() if c["method"] == "POST"]
        self.assertEqual([{"issue_id": 903}], [c["payload"] for c in posts])
        self.assertEqual([3], self.backend.predecessor_links(101))

    def test_a_change_removes_and_adds_before_the_body_patch(self):
        info = self._create("[3]")
        self.transport.calls.clear()
        self.backend.write_spec(info, _with_deps(info["text"], "[5]"))
        self.assertEqual([5], self.backend.predecessor_links(101))
        kinds = [(c["method"], c["path"]) for c in self.transport.calls
                 if c["method"] != "GET" and c["path"].startswith("repos/owner/repo/issues/101")]
        self.assertEqual([
            ("DELETE", "repos/owner/repo/issues/101/dependencies/blocked_by/903"),
            ("POST", "repos/owner/repo/issues/101/dependencies/blocked_by"),
            ("PATCH", "repos/owner/repo/issues/101"),
        ], kinds)

    def test_a_write_that_keeps_depends_on_makes_no_dependency_request(self):
        info = self._create("[3]")
        self.transport.calls.clear()
        text = info["text"].replace("A discriminant fixture.", "Changed prose.")
        self.backend.write_spec(info, text)
        self.assertEqual([], self.transport.dependency_calls())
        self.assertTrue(any(c["method"] == "PATCH" for c in self.transport.calls))

    def test_a_retry_after_linking_converges_without_duplicating(self):
        info = self._create("[]")
        self.transport.blocked_by[101] = [3]        # a link that landed before a failed PATCH
        self.transport.calls.clear()
        self.backend.write_spec(info, _with_deps(info["text"], "[3]"))
        self.assertEqual([("GET", "repos/owner/repo/issues/101/dependencies/blocked_by"
                                  "?per_page=100")],
                         [(c["method"], c["path"]) for c in self.transport.dependency_calls()])
        self.assertEqual([3], self.backend.predecessor_links(101))

    def test_over_the_limit_refuses_before_any_request(self):
        many = "[" + ", ".join(str(n) for n in range(1, GH_DEPENDENCY_LIMIT + 2)) + "]"
        with self.assertRaises(BackendRefusal) as ctx:
            self.backend.create_spec("plans", _with_deps(_external_case_doc(), many))
        self.assertEqual("sp-gh-dependency-limit", ctx.exception.err["code"])
        self.assertEqual([], self.transport.calls)


class BehindTheSpecsService(unittest.TestCase):
    """The stdio MCP server (2085) is a second port of the same core: a read tool answers
    from a spec the GitHub backend holds, over the same offline double."""

    def test_an_mcp_section_read_answers_from_the_github_backend(self):
        tmp = os.path.realpath(tempfile.mkdtemp(prefix="quenching-gh-mcp-"))
        self.addCleanup(shutil.rmtree, tmp, True)
        subprocess.run(["git", "init", "-q", tmp], check=True)
        transport = DependencyFixture()
        backend = GitHubBackend("owner/repo", tmp, types={"incidente": "Bug"}, open_issues=0)
        backends_mod._BACKEND_CACHE.clear()
        backends_mod._BACKEND_CACHE[tmp] = backend
        self.addCleanup(backends_mod._BACKEND_CACHE.clear)
        with mock.patch.object(gh_mod, "_gh_run", side_effect=transport):
            backend.create_spec("plans", _external_case_doc())
            before = len(transport.calls)
            payload, failed = mcp.call_tool("specs_section",
                                            {"spec": 101, "headings": "Problem"}, tmp)
        self.assertFalse(failed, payload)
        self.assertEqual(["Problem"], [s["heading"] for s in payload["sections"]])
        self.assertIn("A discriminant fixture.", json.dumps(payload))
        read = transport.calls[before:]
        self.assertTrue(read, "the MCP read reached the GitHub transport")
        self.assertEqual({"GET"}, {c.get("method", "GET") for c in read})


if __name__ == "__main__":
    unittest.main()
