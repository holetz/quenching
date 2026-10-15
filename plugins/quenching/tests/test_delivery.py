"""Executable proofs for the delivery probe, inventory and C3 findings."""
from __future__ import annotations

import json
import contextlib
import io
import pathlib
import sys
import tempfile
import unittest

try:
    import _paths  # noqa: F401 — must precede the `quenching` import
except ModuleNotFoundError:  # package-qualified unittest invocation from the repository root
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    import _paths  # noqa: F401
from quenching.delivery.cli import main
from quenching.delivery.doctor import doctor


HERE = pathlib.Path(__file__).resolve().parent
GOLDEN = HERE / "fixtures" / "golden" / "delivery-results.json"


class DeliveryResults(unittest.TestCase):
    def _run(self, files: dict[str, str]) -> tuple[dict, int]:
        with tempfile.TemporaryDirectory() as raw:
            root = pathlib.Path(raw)
            for name, content in files.items():
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding="utf-8")
            payload, error, code = doctor(str(root))
            self.assertEqual({}, error)
            assert payload is not None
            return payload, code

    def test_workflow_mapping_indentation_preserves_inventory_and_findings(self):
        baseline = None
        for trigger_width, job_width in ((2, 2), (4, 4), (2, 4), (4, 2), (6, 6)):
            with self.subTest(trigger_width=trigger_width, job_width=job_width):
                trigger = " " * trigger_width
                job = " " * job_width
                payload, code = self._run({
                    ".github/workflows/ci.yml": (
                        "on:\n # trigger comment\n\n"
                        + trigger + "push:\n"
                        + trigger + "  branches: [main]\n"
                        + trigger + "pull_request:\n"
                        "jobs:\n # job comment\n\n"
                        + job + "test:\n"
                        + job + "  strategy:\n"
                        + job + "    matrix:\n"
                        + job + "      python-version: ['3.12']\n"
                        + job + "  steps:\n"
                        + job + "    - uses: actions/checkout@v4\n"
                        + job + "    - run: python -m unittest\n"
                        + job + "lint:\n"
                        + job + "  needs: [test]\n"
                        + job + "  steps:\n"
                        + job + "    - uses: actions/checkout@v4\n"
                        + job + "    - run: python -m compileall .\n"
                    ),
                })
                workflow = payload["inventory"]["workflows"][0]
                self.assertEqual(["pull_request", "push"], workflow["triggers"])
                self.assertEqual(["lint", "test"], workflow["jobs"])
                details = {item["name"]: item for item in workflow["jobDetails"]}
                self.assertEqual({"test", "lint"}, set(details))
                self.assertEqual(["python -m unittest"], details["test"]["commands"])
                self.assertEqual(["python -m compileall ."], details["lint"]["commands"])
                self.assertEqual(["test"], details["lint"]["needs"])
                codes = {item["code"] for item in payload["findings"]}
                self.assertIn("delivery-setup-missing", codes)
                self.assertNotIn("delivery-trigger-unreachable", codes)
                self.assertEqual(1, code)
                observed = (workflow, payload["findings"], code)
                if baseline is None:
                    baseline = observed
                else:
                    self.assertEqual(baseline, observed)

    def test_step_condition_does_not_disable_its_job(self):
        for condition in ("false", "${{ false }}", "never"):
            with self.subTest(condition=condition):
                payload, _ = self._run({
                    ".github/workflows/ci.yml": (
                        "on: push\njobs:\n  test:\n    steps:\n"
                        "      - name: disabled\n        if: " + condition + "\n"
                        "        run: echo skipped\n"
                        "      - run: python -m unittest\n"
                    ),
                })
                job = payload["inventory"]["workflows"][0]["jobDetails"][0]
                self.assertTrue(job["active"])
                codes = {finding["code"] for finding in payload["findings"]}
                self.assertIn("delivery-checkout-missing", codes)
                self.assertIn("delivery-setup-missing", codes)

    def test_azure_top_level_step_condition_does_not_disable_synthetic_job(self):
        payload, _ = self._run({
            "azure-pipelines.yml": (
                "trigger: [main]\nsteps:\n- script: echo skipped\n  if: false\n"
                "- script: python -m unittest\n"
            ),
        })
        job = payload["inventory"]["workflows"][0]["jobDetails"][0]
        self.assertTrue(job["active"])
        self.assertIn("delivery-setup-missing", {item["code"] for item in payload["findings"]})

    def test_job_false_condition_stays_inactive(self):
        for indent in ("    ", "      "):
            with self.subTest(indent=len(indent)):
                payload, _ = self._run({
                    ".github/workflows/ci.yml": (
                        "on: push\njobs:\n  test:\n" + indent + "if: ${{ false }}\n"
                        + indent + "steps:\n" + indent + "  - run: python -m unittest\n"
                    ),
                })
                self.assertFalse(payload["inventory"]["workflows"][0]["jobDetails"][0]["active"])
                codes = {finding["code"] for finding in payload["findings"]}
                self.assertNotIn("delivery-checkout-missing", codes)
                self.assertNotIn("delivery-setup-missing", codes)

    def test_multiline_commands_preserve_runtime_and_publish_evidence(self):
        for marker in ("|", ">", "|-", ">+", "|2-"):
            for provider in ("github", "azure-bash", "azure-script", "azure-pwsh", "gitlab"):
                with self.subTest(provider=provider, marker=marker):
                    if provider == "github":
                        path = ".github/workflows/ci.yml"
                        body = ("on: push\njobs:\n  test:\n    steps:\n"
                                "      - run: " + marker + "\n"
                                "          echo starting\n          python -m build\n"
                                "          npm publish\n"
                                "        name: metadata\n      - run: echo next\n")
                    elif provider.startswith("azure"):
                        path = "azure-pipelines.yml"
                        key = provider.split("-", 1)[1]
                        body = ("trigger: [main]\nsteps:\n- " + key + ": " + marker + "\n"
                                "    echo starting\n    python -m build\n    npm publish\n"
                                "  displayName: metadata\n- script: echo next\n")
                    else:
                        path = ".gitlab-ci.yml"
                        body = ("test:\n  script: " + marker + "\n"
                                "    echo starting\n    python -m build\n    npm publish\n"
                                "  after_script:\n    - echo after\n")
                    payload, _ = self._run({path: body})
                    job = payload["inventory"]["workflows"][0]["jobDetails"][0]
                    self.assertEqual(["echo starting", "python -m build", "npm publish"] +
                                     ([] if provider == "gitlab" else ["echo next"]), job["commands"])
                    self.assertTrue(job["release"])
                    codes = {finding["code"] for finding in payload["findings"]}
                    self.assertIn("delivery-setup-missing", codes)
                    if provider != "gitlab":
                        self.assertIn("delivery-checkout-missing", codes)

    def test_absent_is_explicit_not_applicable(self):
        payload, code = self._run({})
        self.assertEqual(0, code)
        self.assertEqual("not-applicable", payload["applicability"]["state"])
        self.assertIsNone(payload["inventory"])
        self.assertEqual([], payload["findings"])

    def test_config_without_delivery_namespace_is_not_applicable(self):
        payload, code = self._run({".claude/quenching.json": "{}\n"})
        self.assertEqual(0, code)
        self.assertEqual("not-applicable", payload["applicability"]["state"])
        self.assertIsNone(payload["inventory"])
        self.assertEqual([], payload["findings"])

    def test_declared_delivery_without_workflow_is_applicable(self):
        payload, code = self._run({".claude/quenching.json": '{"delivery": {}}\n'})
        self.assertEqual(1, code)
        self.assertEqual("applicable", payload["applicability"]["state"])
        self.assertEqual([], payload["inventory"]["workflows"])
        self.assertEqual("delivery-provider-policy", payload["findings"][0]["code"])

    def test_azure_top_level_steps_prove_job_checkout_setup_and_runtime(self):
        payload, code = self._run({
            "azure-pipelines.yml": (
                "trigger: [main]\n"
                "steps:\n"
                "- checkout: self\n"
                "- task: UsePythonVersion@0\n"
                "  inputs:\n"
                "    versionSpec: '3.12'\n"
                "- script: python -m unittest\n"
            ),
        })
        self.assertEqual(0, code)
        workflow = payload["inventory"]["workflows"][0]
        self.assertEqual("azure", workflow["provider"])
        self.assertEqual(["default"], workflow["jobs"])
        job = workflow["jobDetails"][0]
        self.assertTrue(job["checkout"])
        self.assertTrue(job["setup"])
        self.assertEqual(["python:3.12"], job["runtimes"])
        self.assertEqual(["python -m unittest"], job["commands"])
        self.assertEqual([], payload["findings"])

    def test_azure_named_jobs_prove_dependency_chain(self):
        payload, code = self._run({
            "azure-pipelines.yml": (
                "trigger: [main]\n"
                "jobs:\n"
                "- job: build\n"
                "  steps:\n"
                "  - checkout: self\n"
                "  - task: UsePythonVersion@0\n"
                "    inputs:\n"
                "      versionSpec: '3.12'\n"
                "  - script: python -m build\n"
                "- deployment: deploy\n"
                "  dependsOn: build\n"
                "  steps:\n"
                "  - checkout: self\n"
                "  - task: UsePythonVersion@0\n"
                "    inputs:\n"
                "      versionSpec: '3.12'\n"
                "  - script: python -m deploy\n"
            ),
        })
        self.assertEqual(0, code)
        workflow = payload["inventory"]["workflows"][0]
        self.assertEqual("azure", workflow["provider"])
        self.assertEqual(["build", "deploy"], workflow["jobs"])
        self.assertEqual([[], ["build"]],
                         [job["needs"] for job in workflow["jobDetails"]])
        self.assertEqual([], payload["findings"])

    def test_conformant_workflow_is_stable_and_read_only(self):
        payload, code = self._run({
            ".github/workflows/ci.yml": (
                "name: CI\non: [push, pull_request]\njobs:\n"
                "  test:\n    runs-on: ubuntu-latest\n    steps:\n"
                "      - uses: actions/checkout@v4\n"
                "      - uses: actions/setup-python@v5\n"
                "        with:\n          python-version: '3.11'\n"
                "      - run: python -m unittest\n"
            ),
        })
        self.assertEqual(0, code)
        self.assertTrue(payload["ok"])
        self.assertEqual([".github/workflows/ci.yml"],
                         [item["path"] for item in payload["inventory"]["workflows"]])
        self.assertEqual([], payload["findings"])

    def test_structural_findings_cover_pipeline_reachability_and_provenance(self):
        payload, code = self._run({
            ".github/workflows/broken.yml": (
                "name: Broken\non: push\njobs:\n"
                "  test:\n    needs: missing\n    steps:\n      - run: pytest\n"
                "  py310:\n    steps:\n      - uses: actions/checkout@v4\n"
                "        - uses: actions/setup-python@v5\n"
                "          python-version: '3.10'\n"
                "  py311:\n    steps:\n      - uses: actions/checkout@v4\n"
                "        - uses: actions/setup-python@v5\n"
                "          python-version: '3.11'\n"
                "  release:\n    needs: missing-release\n    steps:\n      - run: echo pending\n"
            ),
        })
        self.assertEqual(1, code)
        codes = {item["code"] for item in payload["findings"]}
        self.assertTrue({
            "delivery-stage-unreachable",
            "delivery-checkout-missing",
            "delivery-setup-missing",
            "delivery-runtime-drift",
            "delivery-release-unreachable",
        } <= codes)
        self.assertTrue(all(item["band"] == "Structural"
                            for item in payload["findings"]))

    def test_list_form_triggers_are_triggers(self):
        github, _ = self._run({
            ".github/workflows/ci.yml": (
                "name: CI\non:\n  - push\njobs:\n  test:\n    runs-on: ubuntu-latest\n"
                "    steps:\n      - run: echo ok\n"
            ),
        })
        azure, _ = self._run({
            "azure-pipelines.yml": "trigger:\n- main\nsteps:\n- script: echo ok\n",
        })
        self.assertEqual(["push"], github["inventory"]["workflows"][0]["triggers"])
        self.assertEqual(["main"], azure["inventory"]["workflows"][0]["triggers"])
        for payload in (github, azure):
            self.assertNotIn("delivery-trigger-unreachable",
                             {item["code"] for item in payload["findings"]})

    def test_trigger_none_is_no_trigger(self):
        for body in ("trigger: none\n", "trigger:\n- none\n"):
            payload, _ = self._run({
                "azure-pipelines.yml": body + "steps:\n- script: echo ok\n",
            })
            self.assertEqual([], payload["inventory"]["workflows"][0]["triggers"])
            self.assertIn("delivery-trigger-unreachable",
                          {item["code"] for item in payload["findings"]})

    def test_azure_pr_and_schedules_are_triggers_with_trigger_none(self):
        bodies = {
            "pr": "trigger: none\npr:\n- main\n",
            "pr-branches": "trigger: none\npr:\n  branches:\n    include:\n    - main\n",
            "schedules": "trigger: none\nschedules:\n- cron: '0 0 * * *'\n  branches:\n    include: [main]\n",
        }
        for name, body in bodies.items():
            payload, _ = self._run({
                "azure-pipelines.yml": body + "steps:\n- script: echo ok\n",
            })
            self.assertNotEqual([], payload["inventory"]["workflows"][0]["triggers"], name)
            self.assertNotIn("delivery-trigger-unreachable",
                             {item["code"] for item in payload["findings"]}, name)

    def test_azure_pr_none_stays_without_trigger(self):
        for body in ("trigger: none\npr: none\n", "trigger: none\npr:\n- none\n"):
            payload, _ = self._run({
                "azure-pipelines.yml": body + "steps:\n- script: echo ok\n",
            })
            self.assertEqual([], payload["inventory"]["workflows"][0]["triggers"])
            self.assertIn("delivery-trigger-unreachable",
                          {item["code"] for item in payload["findings"]})

    def test_github_schedule_in_on_is_a_trigger(self):
        for on in ("on:\n  schedule:\n    - cron: '0 0 * * *'\n", "on: schedule\n"):
            payload, _ = self._run({
                ".github/workflows/nightly.yml": (
                    "name: N\n" + on + "jobs:\n  t:\n    runs-on: ubuntu-latest\n"
                    "    steps:\n      - run: echo ok\n"),
            })
            self.assertEqual(["schedule"], payload["inventory"]["workflows"][0]["triggers"])
            self.assertNotIn("delivery-trigger-unreachable",
                             {item["code"] for item in payload["findings"]})

    def test_matrix_setup_uv_and_bash_only_jobs_raise_no_false_errors(self):
        payload, code = self._run({
            ".github/workflows/ci.yml": (
                "name: CI\non:\n  push:\n    branches: [main]\njobs:\n"
                "  gate:\n    strategy:\n      matrix:\n"
                "        python-version: ['3.11', '3.13']\n    steps:\n"
                "      - uses: actions/checkout@v4\n"
                "      - uses: actions/setup-python@v5\n"
                "        with:\n          python-version: ${{ matrix.python-version }}\n"
                "      - run: python -m unittest\n"
                "  lint:\n    steps:\n      - uses: actions/checkout@v4\n"
                "      - uses: astral-sh/setup-uv@v5\n"
                "      - run: uv run ruff check .\n"
                "  functional:\n    steps:\n      - uses: actions/checkout@v4\n"
                "      - run: bash scripts/check.sh\n"
            ),
        })
        self.assertEqual([], [item for item in payload["findings"]
                              if item["severity"] == "error"])
        gate = payload["inventory"]["workflows"][0]["jobDetails"][0]
        self.assertEqual(["python:matrix:3.11", "python:matrix:3.13"], gate["runtimes"])

    def test_real_runtime_drift_still_reports_beside_a_matrix(self):
        payload, _ = self._run({
            ".github/workflows/ci.yml": (
                "name: CI\non: push\njobs:\n"
                "  gate:\n    steps:\n      - uses: actions/checkout@v4\n"
                "      - uses: actions/setup-python@v5\n"
                "        with:\n          python-version: ['3.11', '3.13']\n"
                "      - run: pytest\n"
                "  old:\n    steps:\n      - uses: actions/checkout@v4\n"
                "      - uses: actions/setup-python@v5\n"
                "        with:\n          python-version: '3.9'\n"
                "      - run: pytest\n"
            ),
        })
        self.assertIn("delivery-runtime-drift", {item["code"] for item in payload["findings"]})

    def test_judgement_findings_preserve_owner_boundaries(self):
        payload, code = self._run({
            ".github/workflows/release.yml": (
                "name: Release\non: push\npermissions:\n  contents: write\njobs:\n"
                "  publish:\n    environment: production\n    steps:\n"
                "      - uses: actions/checkout@v4\n"
                "      - uses: actions/setup-python@v5\n"
                "      - run: python -m build && twine upload dist/*\n"
            ),
        })
        self.assertEqual(1, code)
        codes = {item["code"] for item in payload["findings"]}
        self.assertEqual({"delivery-environment-policy", "delivery-publish-scope",
                          "delivery-permission-policy"}, codes)
        self.assertTrue(all(item["band"] == "Judgement"
                            for item in payload["findings"]))

    def test_second_provider_equivalent_target_uses_gitlab_shape(self):
        payload, code = self._run({
            ".gitlab-ci.yml": (
                "workflow:\n  rules:\n    - if: $CI_COMMIT_BRANCH\n"
                "stages:\n  - build\n  - release\n"
                "build:\n  stage: build\n  image: python:3.12\n  script:\n"
                "    - python -m build\n"
                "release:\n  stage: release\n  needs: [build]\n"
                "  image: python:3.12\n  script:\n    - echo complete\n"
            ),
        })
        self.assertEqual(0, code)
        workflow = payload["inventory"]["workflows"][0]
        self.assertEqual("gitlab", workflow["provider"])
        self.assertEqual(["build", "release"], workflow["jobs"])
        self.assertEqual(["build", "release"], workflow["stages"])
        self.assertEqual(["python:3.12", "python:3.12"],
                         [runtime for job in workflow["jobDetails"]
                          for runtime in job["runtimes"]])
        self.assertEqual([], payload["findings"])

    def test_unmeasured_provider_is_not_reported_as_conformant(self):
        payload, code = self._run({
            ".claude/quenching.json": '{"delivery": {"provider": "jenkins"}}\n',
        })
        self.assertEqual(1, code)
        self.assertEqual("applicable", payload["applicability"]["state"])
        self.assertEqual([], payload["inventory"]["workflows"])
        self.assertEqual("delivery-provider-policy", payload["findings"][0]["code"])


class FrozenDeliveryResults(unittest.TestCase):
    def test_golden_declares_all_result_classes(self):
        payload = json.loads(GOLDEN.read_text(encoding="utf-8"))
        self.assertEqual({"absent", "conformant", "mechanical", "structural",
                          "judgement", "not-measured"}, set(payload))
        self.assertEqual([], payload["mechanical"]["codes"])
        self.assertEqual({"delivery-stage-unreachable", "delivery-checkout-missing",
                          "delivery-setup-missing", "delivery-runtime-drift",
                          "delivery-release-unreachable"},
                         set(payload["structural"]["codes"]))
        self.assertEqual({"delivery-provider-policy", "delivery-environment-policy",
                          "delivery-publish-scope", "delivery-permission-policy"},
                         set(payload["judgement"]["codes"]))


class DeliveryCli(unittest.TestCase):
    def test_cli_routes_inventory_status_and_no_command(self):
        with tempfile.TemporaryDirectory() as raw:
            root = pathlib.Path(raw)
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(2, main(["--root", str(root)]))

            workflow = root / ".github" / "workflows" / "ci.yml"
            workflow.parent.mkdir(parents=True)
            workflow.write_text(
                "name: CI\non: [push, pull_request]\njobs:\n"
                "  test:\n    runs-on: ubuntu-latest\n    steps:\n"
                "      - uses: actions/checkout@v4\n"
                "      - uses: actions/setup-python@v5\n"
                "        with:\n          python-version: '3.11'\n"
                "      - run: python -m unittest\n", encoding="utf-8")
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(0, main(["--root", str(root), "inventory", "--json"]))
            self.assertEqual([".github/workflows/ci.yml"],
                             [item["path"] for item in json.loads(output.getvalue())["workflows"]])

            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(0, main(["--root", str(root), "status", "--json"]))
            self.assertTrue(json.loads(output.getvalue())["ok"])


if __name__ == "__main__":
    unittest.main()
