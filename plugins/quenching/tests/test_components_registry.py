import contextlib
import io
import json
import pathlib
import subprocess
import tempfile
import unittest
from types import SimpleNamespace

import _paths  # noqa: F401
from quenching.components.commands.registry import cmd_registry

ZONE = "# Automation\n\n<!-- GENERATED:BEGIN -->\nold\n<!-- GENERATED:END -->\n"


def registry_path(base: pathlib.Path) -> pathlib.Path:
    return base / "docs" / "documentation" / "reference" / "automation.md"


def target_in(parent: pathlib.Path) -> pathlib.Path:
    target = parent / "target"
    (target / "commands" / "x").mkdir(parents=True)
    (target / "commands" / "x" / "y.md").write_text(
        '---\ndescription: do it. Use for "run y".\n---\n\nBody.\n', encoding="utf-8")
    subprocess.run(["git", "init", "-q", str(target)], check=True)
    return target


def reindex(target: pathlib.Path, registry: str | None = None):
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        status = cmd_registry(SimpleNamespace(registry=registry, json=True), str(target))
    return status, json.loads(output.getvalue())


class RegistryStaysInsideTheTargetRepo(unittest.TestCase):
    def test_an_ancestor_registry_outside_the_repo_is_never_rewritten(self):
        parent = pathlib.Path(tempfile.mkdtemp())
        target = target_in(parent)
        ancestor = registry_path(parent)
        ancestor.parent.mkdir(parents=True)
        ancestor.write_text(ZONE, encoding="utf-8")
        status, payload = reindex(target)
        self.assertEqual(status, 1)
        self.assertEqual(payload["findings"][0]["code"], "sk-no-registry")
        self.assertEqual(ancestor.read_text(encoding="utf-8"), ZONE)

    def test_a_registry_inside_the_repo_is_rewritten(self):
        parent = pathlib.Path(tempfile.mkdtemp())
        target = target_in(parent)
        own = registry_path(target)
        own.parent.mkdir(parents=True)
        own.write_text(ZONE, encoding="utf-8")
        status, payload = reindex(target)
        self.assertEqual(status, 0)
        self.assertTrue(payload["changed"])
        self.assertIn("/x:y", own.read_text(encoding="utf-8"))

    def test_an_explicit_registry_outside_the_repo_still_holds(self):
        parent = pathlib.Path(tempfile.mkdtemp())
        target = target_in(parent)
        outside = registry_path(parent)
        outside.parent.mkdir(parents=True)
        outside.write_text(ZONE, encoding="utf-8")
        status, payload = reindex(target, registry=str(outside))
        self.assertEqual(status, 0)
        self.assertIn("/x:y", outside.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
