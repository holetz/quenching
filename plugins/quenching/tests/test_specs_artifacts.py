"""The artifact capability: text stored beside the spec, read back through the same store.

The rule these tests exist for is that an artifact is a STORE WRITE and not a side file: it
must survive the pending ref, the replay onto a newer tip and the single-commit push exactly
as a document does. The cases that prove the second half live in `test_specs_git_backend` and
`test_specs_push`; this module owns the capability itself.
"""

import pathlib
import sys
import unittest

try:
    import _paths  # noqa: F401  — must precede the `quenching` import; see its docstring
except ModuleNotFoundError:  # package-qualified unittest invocation from the repository root
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    import _paths  # noqa: F401
from test_specs_git_backend import GitStoreFixture
from quenching.specs.backends.base import MAX_ARTIFACT_BYTES, BackendRefusal
from quenching.specs.backends.git import GitBackend
from quenching.specs.backends.github import GitHubBackend
from quenching.specs.backends.memory import MemoryBackend


def _seed(backend, spec_id: int = 1) -> str:
    return backend.create_spec("plans", f"---\ntitle: Spec {spec_id}\n---\n\n"
                               f"## Problem\n\nbody {spec_id}\n")


class RoundTrip(GitStoreFixture):
    def test_write_read_list_and_remove(self):
        backend = GitBackend(self.clone("a"))
        _seed(backend)
        locator = backend.write_artifact(1, "handoff-2026-11-01-x.md", "the handoff\n")
        self.assertEqual("quenching:specs/artifacts/1/handoff-2026-11-01-x.md", locator)
        self.assertEqual("the handoff\n", backend.read_artifact(1, "handoff-2026-11-01-x.md"))
        self.assertEqual([{"spec": 1, "name": "handoff-2026-11-01-x.md",
                           "path": locator}], backend.list_artifacts(1))
        self.assertEqual([], backend.list_artifacts())
        backend.remove_artifact(1, "handoff-2026-11-01-x.md")
        self.assertEqual([], backend.list_artifacts(1))
        with self.assertRaises(BackendRefusal) as caught:
            backend.read_artifact(1, "handoff-2026-11-01-x.md")
        self.assertEqual("sp-artifact-unknown", caught.exception.err["code"])

    def test_a_standalone_artifact_lives_under_handoffs(self):
        backend = GitBackend(self.clone("a"))
        _seed(backend)
        locator = backend.write_artifact(None, "handoff-2026-11-01-x.md", "no spec\n")
        self.assertEqual("quenching:specs/artifacts/_handoffs/handoff-2026-11-01-x.md", locator)
        self.assertEqual("no spec\n", backend.read_artifact(None, "handoff-2026-11-01-x.md"))
        self.assertEqual([], backend.list_artifacts(1))
        self.assertEqual(["handoff-2026-11-01-x.md"],
                         [row["name"] for row in backend.list_artifacts()])

    def test_writing_the_same_name_replaces_it(self):
        backend = GitBackend(self.clone("a"))
        _seed(backend)
        backend.write_artifact(1, "h.md", "first\n")
        backend.write_artifact(1, "h.md", "second\n")
        self.assertEqual("second\n", backend.read_artifact(1, "h.md"))
        self.assertEqual(1, len(backend.list_artifacts(1)))

    def test_an_attached_artifact_needs_a_spec(self):
        backend = GitBackend(self.clone("a"))
        for call in (lambda: backend.write_artifact(99, "h.md", "text\n"),
                     lambda: backend.read_artifact(99, "h.md"),
                     lambda: backend.list_artifacts(99),
                     lambda: backend.remove_artifact(99, "h.md")):
            with self.assertRaises(BackendRefusal) as caught:
                call()
            self.assertEqual("sp-unknown-id", caught.exception.err["code"])


class Refusals(GitStoreFixture):
    def test_the_name_is_one_segment(self):
        backend = GitBackend(self.clone("a"))
        _seed(backend)
        for name in ("", "../x", "a/b", ".hidden", "x" * 121):
            with self.subTest(name=name):
                with self.assertRaises(BackendRefusal) as caught:
                    backend.write_artifact(1, name, "text\n")
                self.assertEqual("sp-artifact-name", caught.exception.err["code"])

    def test_the_size_cap_refuses_before_anything_is_written(self):
        backend = GitBackend(self.clone("a"))
        _seed(backend)
        with self.assertRaises(BackendRefusal) as caught:
            backend.write_artifact(1, "big.md", "x" * (MAX_ARTIFACT_BYTES + 1))
        self.assertEqual("sp-artifact-too-large", caught.exception.err["code"])
        self.assertEqual([], backend.list_artifacts(1))

    def test_the_leak_guard_runs_on_the_artifact(self):
        backend = GitBackend(self.clone("a"))
        _seed(backend)
        # Assembled at run time: this file is scanned by the gate it is testing, and a
        # tax id written whole here would be the finding it is meant to catch.
        fake_tax_id = ".".join(["123", "456", "789"]) + "-" + "0" + "1"
        with self.assertRaises(BackendRefusal) as caught:
            backend.write_artifact(1, "h.md", f"cpf {fake_tax_id}\n")
        self.assertEqual("sp-leak", caught.exception.err["code"])
        self.assertEqual([], backend.list_artifacts(1))

    def test_a_backend_without_the_capability_refuses(self):
        backend = GitHubBackend("owner/repo", ".", types={}, open_issues=0)
        with self.assertRaises(BackendRefusal) as caught:
            backend.write_artifact(1, "h.md", "text\n")
        self.assertEqual("sp-artifact-unsupported", caught.exception.err["code"])
        self.assertEqual("github", caught.exception.err["message"].split("'")[1])


class MemoryEquivalence(unittest.TestCase):
    def test_the_fake_answers_the_same_shape(self):
        backend = MemoryBackend()
        _seed(backend)
        locator = backend.write_artifact(1, "h.md", "text\n")
        self.assertEqual("memory://artifacts/1/h.md", locator)
        self.assertEqual("text\n", backend.read_artifact(1, "h.md"))
        self.assertEqual([{"spec": 1, "name": "h.md", "path": locator}],
                         backend.list_artifacts(1))
        backend.remove_artifact(1, "h.md")
        self.assertEqual([], backend.list_artifacts(1))

    def test_the_fake_refuses_an_unknown_spec_and_a_bad_name(self):
        backend = MemoryBackend()
        with self.assertRaises(BackendRefusal) as caught:
            backend.write_artifact(7, "h.md", "text\n")
        self.assertEqual("sp-unknown-id", caught.exception.err["code"])
        _seed(backend)
        with self.assertRaises(BackendRefusal) as caught:
            backend.write_artifact(1, "a/b", "text\n")
        self.assertEqual("sp-artifact-name", caught.exception.err["code"])


if __name__ == "__main__":
    unittest.main()
