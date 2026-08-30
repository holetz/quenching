"""Focused proofs for the ops verifier's registry boundary."""
from __future__ import annotations

import importlib
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

import _paths  # noqa: F401 — must precede the `quenching` import
from quenching.ops.checks import (
    check_adhoc_root,
    check_disabled_check,
    check_no_router,
    check_orphan,
    check_registry_stale,
    check_unarmed_write,
    check_undocumented,
    check_untyped_exit,
    inventory_digest,
    run_checks,
)
from quenching.ops.cli import _status_payload
from quenching.ops.doctor import doctor, inspect_ops
from quenching.ops.inventory import build_inventory
from quenching.ops.model import EntryPoint, Inventory, Router
from quenching.ops.registry import (
    REGISTRY_END,
    REGISTRY_START,
    render_registry_document,
    write_registry,
)


HERE = pathlib.Path(__file__).resolve().parent
GOLDEN = HERE / "fixtures" / "golden" / "ops-registry-absent.json"
ALIGN_BODY = HERE.parent / "commands" / "ops" / "align.md"
STATUS_BODY = HERE.parent / "commands" / "ops" / "status.md"


class AlignCleanPath(unittest.TestCase):
    def test_conformant_fixture_stops_after_two_calls_before_inventory(self):
        """The clean branch proves the probe-first stop, not just a prose substring.

        The body is a Markdown workflow rather than executable Python, so the fixture runs the
        real doctor and the assertions bind its clean result to the body's first branch. The
        transcript contains the body read and the probe; inventory is explicitly absent.
        """
        with tempfile.TemporaryDirectory() as raw:
            root = pathlib.Path(raw)
            (root / ".claude").mkdir()
            scripts = root / "scripts"
            scripts.mkdir()
            (root / ".claude" / "quenching.json").write_text(
                json.dumps({"opsRoot": "scripts", "router": "pyproject.toml"}),
                encoding="utf-8")
            (root / "pyproject.toml").write_text(
                "[project.scripts]\nrun = 'run:main'\n", encoding="utf-8")
            (scripts / "run.py").write_text(
                "def main():\n    return 0\n\n"
                "if __name__ == '__main__':\n    raise SystemExit(main())\n",
                encoding="utf-8")
            registry = scripts / "README.md"
            registry.write_text("`run.py` — active\n", encoding="utf-8")
            inventory, inventory_error = build_inventory(str(scripts))
            self.assertEqual(inventory_error, {})
            assert inventory is not None
            registry.write_text(render_registry_document("", inventory), encoding="utf-8")

            payload, err, exit_code = doctor(str(root))
            self.assertEqual(err, {})
            self.assertIsNotNone(payload)
            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["findings"], [])

            body = ALIGN_BODY.read_text(encoding="utf-8")
            probe = ('python3 "${CLAUDE_PLUGIN_ROOT}/assets/bin/cq" --root '
                     '"$TARGET_ROOT" ops doctor --json')
            inventory = ('python3 "${CLAUDE_PLUGIN_ROOT}/assets/bin/cq" --root '
                         '"$TARGET_ROOT" ops inventory --json')
            probe_at = body.index(probe)
            clean_stop_at = body.index("When it exits `0` with no findings", probe_at)
            inventory_at = body.index(inventory, clean_stop_at)
            self.assertLess(probe_at, clean_stop_at)
            self.assertLess(clean_stop_at, inventory_at)
            clean_branch = " ".join(body[clean_stop_at:inventory_at].split())
            self.assertIn("Do not run `ops inventory`, ask for confirmation, or write anything.",
                          clean_branch)

            transcript = [
                ("Read", str(ALIGN_BODY)),
                ("Bash", probe),
            ]
            self.assertEqual(len(transcript), 2)
            self.assertNotIn("inventory", " ".join(call for _, call in transcript))


class AlignThreeBands(unittest.TestCase):
    def test_fixture_has_one_finding_per_band_and_body_routes_each_disposition(self):
        with tempfile.TemporaryDirectory() as raw:
            root = pathlib.Path(raw)
            (root / ".claude").mkdir()
            scripts = root / "scripts"
            scripts.mkdir()
            (root / ".claude" / "quenching.json").write_text(
                json.dumps({"opsRoot": "scripts", "router": "pyproject.toml"}),
                encoding="utf-8")
            (root / "pyproject.toml").write_text(
                "[project.scripts]\nrun = 'run:main'\n", encoding="utf-8")
            (scripts / "run.py").write_text(
                "from pathlib import Path\n\n"
                "def verify():\n    return None\n\n"
                "ROOT = Path(__file__).resolve()\n\n"
                "def main():\n    # verify()\n    return 0\n\n"
                "if __name__ == '__main__':\n    raise SystemExit(main())\n",
                encoding="utf-8")
            registry = scripts / "README.md"
            registry.write_text("`run.py` — active\n", encoding="utf-8")

            payload, err, exit_code = doctor(str(root))
            self.assertEqual(err, {})
            self.assertIsNotNone(payload)
            self.assertEqual(exit_code, 1)
            self.assertEqual(
                {finding["code"] for finding in payload["findings"]},
                {"op-registry-stale", "op-adhoc-root", "op-disabled-check"},
            )
            self.assertEqual(len(payload["findings"]), 3)

            body = ALIGN_BODY.read_text(encoding="utf-8")
            classification = body.split("### 3. Classify the findings", 1)[1].split(
                "### 4. Present one plan and gate once", 1)[0]
            self.assertEqual(
                [classification.index(band) for band in ("Mechanical", "Structural", "Judgement")],
                sorted(classification.index(band) for band in ("Mechanical", "Structural", "Judgement")),
            )
            self.assertIn("Build one plan grouped by the three bands", classification)

            gate = body.split("### 4. Present one plan and gate once", 1)[1].split(
                "### 5. Apply only the first two bands", 1)[0]
            self.assertEqual(gate.count("Ask once for authorization"), 1)
            self.assertIn("each judgement finding and its closing command",
                          " ".join(gate.split()))

            apply = body.split("### 5. Apply only the first two bands", 1)[1].split(
                "### 6. Report the cycle", 1)[0]
            self.assertIn("mechanical closures and the bounded structural repairs", apply)
            self.assertIn(
                "Never arm a write-capable entry point, archive an entry point, re-enable a disabled check",
                " ".join(apply.split()),
            )
            self.assertIn(
                "every judgement finding with its evidence and exact command that closes it",
                " ".join(body.split()),
            )


class StatusReadOnly(unittest.TestCase):
    def test_status_reports_all_bands_without_dirtying_a_git_target(self):
        with tempfile.TemporaryDirectory() as raw:
            root = pathlib.Path(raw)
            (root / ".claude").mkdir()
            scripts = root / "scripts"
            scripts.mkdir()
            (root / ".claude" / "quenching.json").write_text(
                json.dumps({"opsRoot": "scripts", "router": "pyproject.toml"}),
                encoding="utf-8")
            (root / "pyproject.toml").write_text(
                "[project.scripts]\nrun = 'run:main'\n", encoding="utf-8")
            (scripts / "run.py").write_text(
                "from pathlib import Path\n\n"
                "def verify():\n    return None\n\n"
                "ROOT = Path(__file__).resolve()\n\n"
                "def main():\n    # verify()\n    return 0\n\n"
                "if __name__ == '__main__':\n    raise SystemExit(main())\n",
                encoding="utf-8")
            (scripts / "README.md").write_text(
                "<!-- quenching-ops-registry-sha256 " + "0" * 64 + " -->\n"
                "`run.py` — active\n",
                encoding="utf-8")

            subprocess.run(["git", "init", "-q", str(root)], check=True,
                           capture_output=True, text=True)
            subprocess.run(["git", "-C", str(root), "add", "."], check=True)
            subprocess.run(
                ["git", "-C", str(root), "-c", "user.name=ops-fixture",
                 "-c", "user.email=ops-fixture@example.invalid", "commit", "-qm", "fixture"],
                check=True,
                capture_output=True,
                text=True,
            )
            before = subprocess.run(
                ["git", "-C", str(root), "status", "--porcelain"],
                check=True,
                capture_output=True,
                text=True,
            ).stdout

            result = subprocess.run(
                [sys.executable, str(HERE.parent / "assets" / "bin" / "cq"),
                 "--root", str(root), "ops", "status", "--json"],
                cwd=HERE.parent,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 1)
            status = json.loads(result.stdout)
            self.assertEqual(set(status["findings"]),
                             {"op-registry-stale", "op-adhoc-root", "op-disabled-check"})
            self.assertEqual(sum(status["findings"].values()), 3)

            after = subprocess.run(
                ["git", "-C", str(root), "status", "--porcelain"],
                check=True,
                capture_output=True,
                text=True,
            ).stdout
            self.assertEqual(before, "")
            self.assertEqual(after, "")

            body = STATUS_BODY.read_text(encoding="utf-8")
            self.assertIn('python3 "${CLAUDE_PLUGIN_ROOT}/assets/bin/cq" --root "$TARGET_ROOT" ops status --json',
                          " ".join(body.split()))
            self.assertIn("It never repairs a finding, writes a registry, or turns an absent optional artifact into a healthy one.",
                          " ".join(body.split()))
            self.assertNotIn("registry --write", body)


class RegistryStale(unittest.TestCase):
    def _inventory(self, root: pathlib.Path) -> Inventory:
        return Inventory(
            str(root),
            Router("pyproject.toml", "python-console-script", True),
            (EntryPoint("run.py", "run", "/run", "Run the job.", lifecycle="active"),),
        )

    def _write_source(self, root: pathlib.Path) -> None:
        (root / "run.py").write_text(
            '"""Run the job."""\n\n'
            "def main():\n    return 0\n",
            encoding="utf-8",
        )

    def test_registry_write_is_idempotent(self):
        with tempfile.TemporaryDirectory() as raw:
            root = pathlib.Path(raw)
            self._write_source(root)
            path = root / "registry.md"
            inventory = self._inventory(root)
            self.assertTrue(write_registry(path, inventory))
            first = path.read_text(encoding="utf-8")
            self.assertFalse(write_registry(path, inventory))
            self.assertEqual(path.read_text(encoding="utf-8"), first)

    def test_registry_write_preserves_authored_prose_outside_generated_zone(self):
        with tempfile.TemporaryDirectory() as raw:
            root = pathlib.Path(raw)
            self._write_source(root)
            prefix = "# Hand-written registry notes\n\n| `manual.py` | not generated |\n"
            suffix = "\n## Notes\nKeep this paragraph.\n"
            old_zone = f"{REGISTRY_START}\nold rows\n{REGISTRY_END}"
            path = root / "registry.md"
            path.write_text(prefix + old_zone + suffix, encoding="utf-8")

            write_registry(path, self._inventory(root))
            updated = path.read_text(encoding="utf-8")
            start = updated.index(REGISTRY_START)
            end = updated.index(REGISTRY_END) + len(REGISTRY_END)
            self.assertEqual(updated[:start], prefix)
            self.assertEqual(updated[end:], suffix)

    def test_stale_check_delegates_to_registry_generator(self):
        with tempfile.TemporaryDirectory() as raw:
            root = pathlib.Path(raw)
            source = "def main():\n    return 0\n"
            (root / "run.py").write_text(source, encoding="utf-8")
            inventory = Inventory(
                str(root),
                Router("pyproject.toml", "python-console-script", True),
                (EntryPoint("run.py", "run", "/run", "", lifecycle="active"),),
            )
            registry = "`run.py` — active\n"
            (root / "registry.md").write_text(registry, encoding="utf-8")
            with mock.patch("quenching.ops.registry.render_registry_document",
                            return_value="different") as generator:
                findings = check_registry_stale(inventory)
            generator.assert_called_once_with(registry, inventory)
            self.assertEqual([finding.code for finding in findings], ["op-registry-stale"])

    def test_absent_registry_is_silent_until_a_generator_can_create_one(self):
        expected = json.loads(GOLDEN.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as raw:
            root = pathlib.Path(raw)
            (root / "run.py").write_text(
                "def main():\n    return 0\n\n"
                "if __name__ == '__main__':\n    raise SystemExit(main())\n",
                encoding="utf-8",
            )
            inventory = Inventory(
                str(root),
                Router("../pyproject.toml", "python-console-script", False),
                (EntryPoint("run.py", "run", "/run", "", language="python"),),
            )
            self.assertFalse((root / "registry.md").exists())
            self.assertEqual(check_registry_stale(inventory), expected["findings"])


class GoldenPayloads(unittest.TestCase):
    def test_doctor_and_status_match_the_frozen_inventory_shape(self):
        doctor_expected = json.loads(
            (HERE / "fixtures" / "golden" / "ops-doctor.json").read_text(encoding="utf-8"))
        status_expected = json.loads(
            (HERE / "fixtures" / "golden" / "ops-status.json").read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as raw:
            root = pathlib.Path(raw)
            (root / ".claude").mkdir()
            scripts = root / "scripts" / "pkg"
            scripts.mkdir(parents=True)
            (root / ".claude" / "quenching.json").write_text(
                json.dumps({"opsRoot": "scripts", "router": "pyproject.toml"}),
                encoding="utf-8")
            (root / "pyproject.toml").write_text(
                "[project.scripts]\nrun = 'pkg.run:main'\n", encoding="utf-8")
            (scripts / "run.py").write_text(
                '"""Run a job."""\nimport argparse\n'
                'parser = argparse.ArgumentParser()\nparser.add_argument("--json")\n',
                encoding="utf-8")
            (scripts / "deploy.sh").write_text("#!/bin/sh\n", encoding="utf-8")

            payload, err = inspect_ops(str(root / "scripts"))
            self.assertEqual(err, {})
            assert payload is not None
            payload["root"] = "<OPS_ROOT>"
            self.assertEqual(payload, doctor_expected)
            self.assertEqual(_status_payload(payload), status_expected)


class FindingFixtures(unittest.TestCase):
    def _inventory(self, source: str, *, lifecycle: str | None = "active",
                   router: Router | None = None, registry: str | None = None) -> Inventory:
        root = pathlib.Path(self.raw.name)
        (root / "run.py").write_text(source, encoding="utf-8")
        if registry is not None:
            (root / "registry.md").write_text(registry, encoding="utf-8")
        return Inventory(
            str(root),
            router or Router("pyproject.toml", "python-console-script", True),
            (EntryPoint("run.py", "run", "/run", "", lifecycle=lifecycle),),
        )

    def setUp(self):
        self.raw = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.raw.cleanup()

    def test_one_minimal_fixture_trips_each_code(self):
        cases = (
            ("op-undocumented", check_undocumented,
             "def main():\n    return 0\n", "active", None, ""),
            ("op-registry-stale", check_registry_stale,
             "def main():\n    return 0\n", "active", None,
             "<!-- quenching-ops-registry-sha256 " + "0" * 64 + " -->\n`run.py`\n"),
            ("op-adhoc-root", check_adhoc_root,
             "from pathlib import Path\nROOT = Path(__file__).resolve()\n", "active", None, None),
            ("op-untyped-exit", check_untyped_exit,
             "def main():\n    return 0\n\n"
             "if __name__ == '__main__':\n    main()\n", "active", None, None),
            ("op-unarmed-write", check_unarmed_write,
             "import requests\nrequests.write('payload')\n", "active", None, None),
            ("op-disabled-check", check_disabled_check,
             "def main():\n    # verify()\n    return 0\n", "active", None, None),
            ("op-orphan", check_orphan,
             "def main():\n    return 0\n", None, None, None),
            ("op-no-router", check_no_router,
             "def main():\n    return 0\n", "active",
             Router("pyproject.toml", "python-console-script", False), None),
        )
        for code, check, source, lifecycle, router, registry in cases:
            with self.subTest(code=code):
                inventory = self._inventory(source, lifecycle=lifecycle,
                                            router=router, registry=registry)
                self.assertEqual([finding.code for finding in check(inventory)], [code])

    def test_a_conformant_fixture_is_silent_for_all_eight_checks(self):
        source = (
            "from argparse import ArgumentParser\n"
            "def main():\n"
            "    parser = ArgumentParser()\n"
            "    parser.add_argument('--write')\n"
            "    return 0\n\n"
            "if __name__ == '__main__':\n"
            "    raise SystemExit(main())\n"
        )
        inventory = self._inventory(source)
        registry = render_registry_document("", inventory)
        inventory = self._inventory(source, registry=registry)
        self.assertEqual(run_checks(inventory), [])

    def test_each_finding_fixture_stops_after_its_minimal_mutation(self):
        cases = (
            (check_undocumented,
             "def main():\n    return 0\n",
             lambda inv: self._inventory(
                 "def main():\n    return 0\n", registry="`run.py` — active\n")),
            (check_adhoc_root,
             "from pathlib import Path\nROOT = Path(__file__).resolve()\n",
             lambda inv: self._inventory("ROOT = 'configured'\n")),
            (check_untyped_exit,
             "def main():\n    return 0\n\nif __name__ == '__main__':\n    main()\n",
             lambda inv: self._inventory(
                 "def main():\n    return 0\n\n"
                 "if __name__ == '__main__':\n    raise SystemExit(main())\n")),
            (check_unarmed_write,
             "import requests\nrequests.write('payload')\n",
             lambda inv: self._inventory(
                 "import requests\nfrom argparse import ArgumentParser\n"
                 "parser = ArgumentParser()\nparser.add_argument('--write')\n"
                 "requests.write('payload')\n")),
            (check_disabled_check,
             "def main():\n    # verify()\n    return 0\n",
             lambda inv: self._inventory(
                 "def verify():\n    return None\n\n"
                 "def main():\n    verify()\n    return 0\n")),
            (check_orphan,
             "def main():\n    return 0\n", lambda inv: self._inventory(
                 "def main():\n    return 0\n", lifecycle="active")),
        )
        for check, source, corrected in cases:
            with self.subTest(check=check.__name__):
                broken = self._inventory(source, lifecycle=None if check is check_orphan else "active")
                self.assertEqual(len(check(broken)), 1)
                fixed = corrected(broken)
                self.assertEqual(check(fixed), [])

        stale = self._inventory(
            "def main():\n    return 0\n",
            registry="<!-- quenching-ops-registry-sha256 " + "0" * 64 + " -->\n`run.py`\n",
        )
        self.assertEqual([finding.code for finding in check_registry_stale(stale)],
                         ["op-registry-stale"])
        good_registry = render_registry_document("", stale)
        corrected = self._inventory("def main():\n    return 0\n", registry=good_registry)
        self.assertEqual(check_registry_stale(corrected), [])

        no_router = self._inventory(
            "def main():\n    return 0\n",
            router=Router("pyproject.toml", "python-console-script", False),
        )
        self.assertEqual([finding.code for finding in check_no_router(no_router)],
                         ["op-no-router"])
        good_router = self._inventory(
            "def main():\n    return 0\n",
            router=Router("pyproject.toml", "python-console-script", True),
        )
        self.assertEqual(check_no_router(good_router), [])

    def test_doctor_never_imports_or_executes_target_code(self):
        with tempfile.TemporaryDirectory() as raw:
            root = pathlib.Path(raw)
            (root / ".claude").mkdir()
            scripts = root / "scripts"
            scripts.mkdir()
            (root / ".claude" / "quenching.json").write_text(
                json.dumps({"opsRoot": "scripts", "router": "pyproject.toml"}),
                encoding="utf-8")
            (root / "pyproject.toml").write_text(
                "[project.scripts]\nrun = 'run:main'\n", encoding="utf-8")
            (scripts / "run.py").write_text(
                "import importlib\nimport subprocess\n"
                "def main():\n    subprocess.run(['dangerous'])\n    return 0\n",
                encoding="utf-8")
            with mock.patch.object(importlib, "import_module", side_effect=AssertionError("imported")), \
                    mock.patch.object(subprocess, "run", side_effect=AssertionError("executed")):
                payload, err, code = doctor(str(scripts))
            self.assertEqual(err, {})
            self.assertIsNotNone(payload)
            self.assertEqual(code, 1)


if __name__ == "__main__":
    unittest.main()
