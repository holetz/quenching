"""Executable proofs for the owner answers to the open source controls catalog."""
from __future__ import annotations

import contextlib
import importlib
import io
import json
import pathlib
import sys
import tempfile
import unittest
from unittest import mock

try:
    import _paths  # noqa: F401 — must precede the `quenching` import
except ModuleNotFoundError:  # package-qualified unittest invocation from the repository root
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    import _paths  # noqa: F401
from quenching.controls.evaluate import (
    load_catalog,
    owner_controls,
    pinned_actions,
    untrusted_trigger,
)

GUIDE = pathlib.PurePosixPath("docs", "deep", "guide.txt").as_posix()
SHA = "0123456789abcdef0123456789abcdef01234567"


def _requirements(block: dict) -> dict:
    return {item["id"]: item for control in block["controls"] for item in control["requirements"]}


def _write(root: pathlib.Path, relative: str, text: str = "x\n") -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


class OwnerControls(unittest.TestCase):
    def test_only_the_owner_controls_are_returned(self):
        catalog = load_catalog()
        with tempfile.TemporaryDirectory() as raw:
            for owner in ("security", "delivery", "toolchain", "proof", "knowledge"):
                block = owner_controls(owner, raw, catalog)
                expected = {item["id"] for item in catalog["controls"] if item["owner"] == owner}
                self.assertEqual(owner, block["owner"])
                self.assertTrue(block["readOnly"])
                self.assertEqual(expected, {item["id"] for item in block["controls"]})

    def test_empty_repository_states_and_nothing_written(self):
        with tempfile.TemporaryDirectory() as raw:
            root = pathlib.Path(raw)
            block = owner_controls("security", root)
            states = _requirements(block)
            self.assertEqual([], sorted(root.iterdir()))
            self.assertEqual("missing", states["OSPS-VM-02.01"]["state"])
            self.assertTrue(states["OSPS-VM-02.01"]["humanRequired"])
            self.assertEqual("not-measured", states["OSPS-AC-04.01"]["state"])
            self.assertEqual("provider-not-read", states["OSPS-AC-04.01"]["reason"])
            self.assertEqual("retired", states["OSPS-BR-01.02"]["state"])
            self.assertEqual(1, block["summary"]["retired"])

    def test_candidate_evidence_is_present(self):
        with tempfile.TemporaryDirectory() as raw:
            root = pathlib.Path(raw)
            _write(root, "SECURITY.md")
            _write(root, GUIDE)
            states = _requirements(owner_controls("security", root))
            self.assertEqual("present", states["OSPS-VM-02.01"]["state"])
            self.assertEqual(["SECURITY.md"], states["OSPS-VM-02.01"]["evidence"])
            self.assertIn(GUIDE, states["OSPS-VM-01.01"]["evidence"])

    def test_git_directory_is_never_walked(self):
        with tempfile.TemporaryDirectory() as raw:
            root = pathlib.Path(raw)
            _write(root, ".git/objects/aa/bb")
            states = _requirements(owner_controls("toolchain", root))
            self.assertEqual([".git"], states["OSPS-QA-05.01"]["evidence"])

    def test_pinned_actions(self):
        with tempfile.TemporaryDirectory() as raw:
            root = pathlib.Path(raw)
            self.assertEqual("missing", pinned_actions(root)["state"])
            _write(root, ".github/workflows/ci.yml",
                   f"jobs:\n  a:\n    steps:\n      - uses: actions/checkout@{SHA}\n"
                   "      - uses: ./local\n")
            self.assertEqual("present", pinned_actions(root)["state"])
            _write(root, ".github/workflows/rel.yaml", "steps:\n  - uses: actions/setup-python@v5\n")
            result = pinned_actions(root)
            self.assertEqual("missing", result["state"])
            self.assertEqual([".github/workflows/rel.yaml:2"], result["evidence"])

    def test_untrusted_trigger(self):
        with tempfile.TemporaryDirectory() as raw:
            root = pathlib.Path(raw)
            self.assertEqual("missing", untrusted_trigger(root)["state"])
            _write(root, ".github/workflows/ci.yml", "on: [pull_request]\n")
            self.assertEqual("present", untrusted_trigger(root)["state"])
            _write(root, ".github/workflows/bad.yml", "on:\n  pull_request_target:\n")
            result = untrusted_trigger(root)
            self.assertEqual("missing", result["state"])
            self.assertEqual([".github/workflows/bad.yml"], result["evidence"])
            self.assertEqual("missing",
                             _requirements(owner_controls("security", root))["OSPS-BR-01.01"]["state"])


ROUTES = {
    "security": ("quenching.security", []),
    "delivery": ("quenching.delivery.cli", ["status"]),
    "toolchain": ("quenching.toolchain.cli", ["status"]),
    "proof": ("quenching.proof.cli", ["status"]),
    "knowledge": ("quenching.knowledge.cli", ["status"]),
}


def _run(module, argv: list[str]) -> tuple[int, dict]:
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        code = module.main(argv)
    return code, json.loads(out.getvalue())


class OwnerStatusRoutes(unittest.TestCase):
    def _repository(self, raw: str) -> pathlib.Path:
        root = pathlib.Path(raw)
        _write(root, ".claude/quenching.json", "{}\n")
        _write(root, "README.md")
        _write(root, "SECURITY.md")
        _write(root, "tests/test_unit.py", "def test_unit():\n    assert True\n")
        _write(root, "docs/index.md", "---\nokf_version: 0.1\n---\n# Index\n")
        _write(root, "pyproject.toml", "[project]\nname = 'x'\nversion = '1.0'\n")
        _write(root, ".github/workflows/ci.yml",
               f"on: [pull_request]\njobs:\n  a:\n    runs-on: ubuntu-latest\n"
               f"    steps:\n      - uses: actions/checkout@{SHA}\n      - run: python -m unittest\n")
        return root

    def test_each_status_carries_its_owner_block_without_moving_the_exit(self):
        catalog = load_catalog()
        stub = {"owner": "stub", "summary": {"present": 0, "missing": 0, "not-measured": 0}}
        with tempfile.TemporaryDirectory() as raw:
            root = self._repository(raw)
            for owner, (name, verb) in ROUTES.items():
                with self.subTest(owner=owner):
                    module = importlib.import_module(name)
                    argv = ["--root", str(root), *verb, "--json"] if owner != "knowledge" \
                        else ["status", "--root", str(root), "--json"]
                    code, payload = _run(module, argv)
                    block = payload["controls"]
                    owned = {item["id"] for item in catalog["controls"] if item["owner"] == owner}
                    self.assertEqual(owner, block["owner"])
                    self.assertEqual(owned, {item["id"] for item in block["controls"]})
                    with mock.patch.object(module, "owner_controls", return_value=stub):
                        stub_code, stub_payload = _run(module, argv)
                    self.assertEqual(code, stub_code)
                    self.assertEqual(payload["ok"], stub_payload["ok"])


if __name__ == "__main__":
    unittest.main()
