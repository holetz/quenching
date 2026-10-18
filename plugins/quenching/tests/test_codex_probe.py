"""Executable proofs for `cq codex probe`, against a fake `codex` — never the real one.

Every test runs with `PATH` reduced to the fake binary's directory and `CODEX_HOME` pointed at a
fixture or a temporary directory, so no test can reach the user's Codex or spend its quota.
"""
from __future__ import annotations

import contextlib
import io
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock

try:
    import _paths  # noqa: F401 — must precede the `quenching` import
except ModuleNotFoundError:  # package-qualified unittest invocation from the repository root
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    import _paths  # noqa: F401
from quenching.codex import main
from quenching.codex.config import DEFAULTS, load_settings
from quenching.codex.probe import APP_SERVER_ARGV, judge, probe, read_sessions

HERE = pathlib.Path(__file__).resolve().parent
FIXTURE_HOME = HERE / "fixtures" / "codex"
CQ = HERE.parent / "assets" / "bin" / "cq"

FAKE = r'''
import json, os, sys, time
log = os.environ.get("FAKE_CODEX_LOG")
if log:
    with open(log, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(sys.argv[1:]) + "\n")
mode = os.environ.get("FAKE_CODEX_MODE", "ok")
if sys.argv[1:2] == ["app-server"]:
    if any("approval_policy" in a for a in sys.argv):
        sys.stderr.write('Error: approval_policy = "untrusted" is no longer supported; remove this setting\n')
        sys.exit(1)
    if mode == "hang":
        time.sleep(30)
    if mode == "crash":
        sys.exit(1)
    for line in sys.stdin:
        message = json.loads(line)
        if "id" not in message:
            continue
        if message["method"] == "initialize":
            reply = {"id": message["id"], "result": {"userAgent": "fake"}}
        elif mode == "error":
            reply = {"id": message["id"], "error": {"code": -32601, "message": "method not found"}}
        else:
            reply = {"id": message["id"], "result": json.loads(os.environ["FAKE_CODEX_LIMITS"])}
        print(json.dumps({"method": "account/rateLimits/updated", "params": {}}), flush=True)
        print(json.dumps(reply), flush=True)
    sys.exit(0)
if sys.argv[1:2] == ["exec"]:
    prompt = sys.stdin.read()
    if log:
        with open(log, "a", encoding="utf-8") as handle:
            handle.write(json.dumps({"stdin": prompt}) + "\n")
    if mode == "hang":
        time.sleep(30)
    cwd = sys.argv[sys.argv.index("-C") + 1]
    if mode == "write":
        with open(os.path.join(cwd, "stray.txt"), "w", encoding="utf-8") as handle:
            handle.write("x\n")
    if mode == "edit":
        with open(os.path.join(cwd, "kept.py"), "a", encoding="utf-8") as handle:
            handle.write("z = 3\n")
    if mode == "commit":
        import subprocess
        subprocess.run(["git", "-C", cwd, "commit", "-q", "--allow-empty", "-m", "codex"],
                       check=True)
    out = sys.argv[sys.argv.index("-o") + 1]
    events = [{"type": "thread.started"},
              {"type": "token_count", "info": {"total_token_usage": {"total_tokens": 100}}},
              {"type": "token_count", "info": {"total_token_usage": {"total_tokens": 4242}}}]
    if mode == "no-usage":
        events = [{"type": "thread.started"}]
    for event in events:
        print(json.dumps(event), flush=True)
    with open(out, "w", encoding="utf-8") as handle:
        handle.write("# review\n\nno findings\n")
        if mode == "env":
            handle.write(json.dumps(sorted(os.environ)) + "\n")
    sys.exit(3 if mode == "fail" else 0)
sys.exit(64)
'''


def write_fake(directory: pathlib.Path) -> pathlib.Path:
    """Write an executable fake `codex` into `directory` and return it."""
    binary = directory / "codex"
    binary.write_text(f"#!{sys.executable}\n{FAKE}", encoding="utf-8")
    binary.chmod(0o755)
    return binary


def limits(primary: float = 10, secondary: float = 20, allowed=True, reached=None) -> dict:
    return {"ordinaryUsageAllowed": allowed,
            "rateLimits": {"rateLimitReachedType": reached,
                           "primary": {"usedPercent": primary, "windowDurationMins": 300,
                                       "resetsAt": 4102444800},
                           "secondary": {"usedPercent": secondary, "windowDurationMins": 10080,
                                         "resetsAt": 4102444800}}}


class FakeCodex(unittest.TestCase):
    """A temporary directory holding the fake binary, a log, and an env that reaches nothing else."""

    def setUp(self):
        self.tmp = pathlib.Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.bin = self.tmp / "bin"
        self.bin.mkdir()
        write_fake(self.bin)
        self.log = self.tmp / "argv.log"
        self.env = {"PATH": str(self.bin), "CODEX_HOME": str(self.tmp / "home"),
                    "FAKE_CODEX_LOG": str(self.log),
                    "FAKE_CODEX_LIMITS": json.dumps(limits())}

    def settings(self, **overrides) -> dict:
        return {**DEFAULTS, "maxUsedPercent": dict(DEFAULTS["maxUsedPercent"]), **overrides}

    def calls(self) -> list:
        if not self.log.exists():
            return []
        return [json.loads(line) for line in self.log.read_text(encoding="utf-8").splitlines()]


class TheAppServerSource(FakeCodex):
    def test_under_both_ceilings_is_available(self):
        out = probe(self.settings(), env=self.env)
        self.assertEqual(("available", "app-server"), (out["state"], out["source"]))
        self.assertEqual(10, out["rateLimits"]["primary"]["usedPercent"])

    def test_the_app_server_never_asks_for_a_sandbox(self):
        probe(self.settings(), env=self.env)
        self.assertEqual([["app-server"]], self.calls())
        self.assertNotIn("sandbox", " ".join(APP_SERVER_ARGV))

    def test_primary_at_the_ceiling_is_unavailable(self):
        self.env["FAKE_CODEX_LIMITS"] = json.dumps(limits(primary=80))
        out = probe(self.settings(), env=self.env)
        self.assertEqual("unavailable", out["state"])
        self.assertIn("primary 80% >= 80%", out["reason"])

    def test_secondary_over_the_ceiling_is_unavailable(self):
        self.env["FAKE_CODEX_LIMITS"] = json.dumps(limits(secondary=95))
        self.assertEqual("unavailable", probe(self.settings(), env=self.env)["state"])

    def test_a_reached_limit_is_unavailable(self):
        self.env["FAKE_CODEX_LIMITS"] = json.dumps(limits(reached="rate_limit_reached"))
        out = probe(self.settings(), env=self.env)
        self.assertEqual("unavailable", out["state"])
        self.assertIn("rate_limit_reached", out["reason"])

    def test_usage_not_allowed_is_unavailable(self):
        self.env["FAKE_CODEX_LIMITS"] = json.dumps(limits(allowed=False))
        self.assertEqual("unavailable", probe(self.settings(), env=self.env)["state"])

    def test_usage_permission_unavailable_is_unknown_and_never_inferred(self):
        self.env["FAKE_CODEX_LIMITS"] = json.dumps(limits(allowed=None))
        out = probe(self.settings(), env=self.env)
        self.assertEqual(("unknown", "app-server"), (out["state"], out["source"]))

    def test_a_snapshot_without_windows_is_unknown(self):
        self.env["FAKE_CODEX_LIMITS"] = json.dumps({"ordinaryUsageAllowed": True,
                                                    "rateLimits": {}})
        self.assertEqual("unknown", probe(self.settings(), env=self.env)["state"])

    def test_configured_ceilings_are_the_ones_applied(self):
        self.env["FAKE_CODEX_LIMITS"] = json.dumps(limits(primary=50))
        out = probe(self.settings(maxUsedPercent={"primary": 40, "secondary": 90}), env=self.env)
        self.assertEqual("unavailable", out["state"])


class TheShortCircuits(FakeCodex):
    def test_cross_review_off_never_spawns_codex(self):
        out = probe(self.settings(crossReview="off"), env=self.env)
        self.assertEqual("unavailable", out["state"])
        self.assertEqual([], self.calls())

    def test_no_codex_on_path_is_unavailable(self):
        self.env["PATH"] = str(self.tmp / "empty")
        out = probe(self.settings(), env=self.env)
        self.assertEqual(("unavailable", "codex is not on PATH"), (out["state"], out["reason"]))


class TheSessionsFallback(FakeCodex):
    NOW_BEFORE_RESET = 1788100000

    def test_a_hung_app_server_falls_back_to_the_last_token_count(self):
        self.env.update(FAKE_CODEX_MODE="hang", CODEX_HOME=str(FIXTURE_HOME))
        started = time.monotonic()
        out = probe(self.settings(timeoutSeconds=1), env=self.env, now=self.NOW_BEFORE_RESET)
        self.assertLess(time.monotonic() - started, 10)
        self.assertEqual(("available", "sessions"), (out["state"], out["source"]))
        self.assertIn("did not answer", out["appServerError"])
        self.assertEqual(12.0, out["rateLimits"]["primary"]["usedPercent"])

    def test_the_app_server_stderr_is_reported(self):
        self.env.update(FAKE_CODEX_MODE="crash", CODEX_HOME=str(FIXTURE_HOME))
        module = sys.modules["quenching.codex.probe"]
        with mock.patch.object(module, "APP_SERVER_ARGV",
                               (*APP_SERVER_ARGV, "-c", 'approval_policy="untrusted"')):
            out = probe(self.settings(), env=self.env, now=self.NOW_BEFORE_RESET)
        self.assertIn("no longer supported", out["appServerError"])

    def test_a_json_rpc_error_falls_back(self):
        self.env.update(FAKE_CODEX_MODE="error", CODEX_HOME=str(FIXTURE_HOME))
        out = probe(self.settings(), env=self.env, now=self.NOW_BEFORE_RESET)
        self.assertEqual("sessions", out["source"])
        self.assertIn("method not found", out["appServerError"])

    def test_a_stale_snapshot_is_unknown(self):
        self.env.update(FAKE_CODEX_MODE="crash", CODEX_HOME=str(FIXTURE_HOME))
        out = probe(self.settings(), env=self.env, now=1788300000)
        self.assertEqual(("unknown", "sessions"), (out["state"], out["source"]))
        self.assertIn("stale", out["reason"])

    def test_no_source_at_all_is_unknown(self):
        self.env["FAKE_CODEX_MODE"] = "crash"
        out = probe(self.settings(), env=self.env)
        self.assertEqual(("unknown", None), (out["state"], out["source"]))
        self.assertIn("no token_count snapshot", out["reason"])

    def test_the_newest_event_of_the_newest_file_wins(self):
        snapshot, path = read_sessions(str(FIXTURE_HOME))
        self.assertTrue(path.endswith("rollout-fixture.jsonl"))
        self.assertEqual(12.0, snapshot["primary"]["usedPercent"])
        self.assertIsNone(snapshot["ordinaryUsageAllowed"])

    def test_a_session_snapshot_never_claims_authority(self):
        snapshot, _ = read_sessions(str(FIXTURE_HOME))
        state, _ = judge(snapshot, DEFAULTS["maxUsedPercent"], authoritative=False,
                         now=self.NOW_BEFORE_RESET)
        self.assertEqual("available", state)


class TheSettings(unittest.TestCase):
    def write(self, root: pathlib.Path, block) -> None:
        (root / ".claude").mkdir()
        (root / ".claude" / "quenching.json").write_text(
            json.dumps({"shared": {"codex": block}}), encoding="utf-8")

    def test_an_absent_block_is_every_default(self):
        with tempfile.TemporaryDirectory() as raw:
            (pathlib.Path(raw) / ".claude").mkdir()
            (pathlib.Path(raw) / ".claude" / "quenching.json").write_text("{}", encoding="utf-8")
            self.assertEqual((DEFAULTS, []), load_settings(raw))

    def test_declared_values_override_the_defaults(self):
        with tempfile.TemporaryDirectory() as raw:
            self.write(pathlib.Path(raw), {"crossReview": "off", "timeoutSeconds": 60,
                                           "model": "m", "maxUsedPercent": {"primary": 50}})
            settings, warnings = load_settings(raw)
        self.assertEqual([], warnings)
        self.assertEqual(("off", 60, "m"), (settings["crossReview"], settings["timeoutSeconds"],
                                            settings["model"]))
        self.assertEqual({"primary": 50, "secondary": 90}, settings["maxUsedPercent"])

    def test_bad_values_fall_back_and_are_named(self):
        with tempfile.TemporaryDirectory() as raw:
            self.write(pathlib.Path(raw), {"crossReview": "maybe", "timeoutSeconds": 0,
                                           "model": "", "maxUsedPercent": {"primary": 150}})
            settings, warnings = load_settings(raw)
        self.assertEqual(4, len(warnings))
        self.assertEqual(DEFAULTS["timeoutSeconds"], settings["timeoutSeconds"])
        self.assertEqual(80, settings["maxUsedPercent"]["primary"])

    def test_a_block_of_the_wrong_shape_is_named(self):
        with tempfile.TemporaryDirectory() as raw:
            self.write(pathlib.Path(raw), ["auto"])
            self.assertEqual(1, len(load_settings(raw)[1]))
        with tempfile.TemporaryDirectory() as raw:
            self.write(pathlib.Path(raw), {"maxUsedPercent": 80})
            self.assertEqual(1, len(load_settings(raw)[1]))


class TheExecutorSettings(unittest.TestCase):
    write = TheSettings.write

    def test_the_executor_is_on_by_default_and_outside_cross_review(self):
        with tempfile.TemporaryDirectory() as raw:
            self.write(pathlib.Path(raw), {"crossReview": "off"})
            settings, warnings = load_settings(raw)
        self.assertEqual([], warnings)
        self.assertEqual(DEFAULTS["executor"], settings["executor"])
        self.assertEqual((True, 20000, 10, 15),
                         tuple(settings["executor"][k] for k in (
                             "enabled", "maxTaskTokens", "reservePercent", "stopLossPercent")))
        self.assertFalse({"sandbox", "windowsSandbox"} & set(settings["executor"]))

    def test_declared_executor_values_override_the_defaults(self):
        with tempfile.TemporaryDirectory() as raw:
            self.write(pathlib.Path(raw), {"executor": {
                "enabled": False, "modelSmall": " s ", "maxTaskTokens": 5000,
                "reservePercent": 5}})
            settings, warnings = load_settings(raw)
        self.assertEqual([], warnings)
        executor = settings["executor"]
        self.assertEqual((False, "s", 5000, 5, 15),
                         (executor["enabled"], executor["modelSmall"], executor["maxTaskTokens"],
                          executor["reservePercent"], executor["stopLossPercent"]))

    def test_a_leftover_sandbox_key_is_ignored_and_never_reaches_the_executor(self):
        with tempfile.TemporaryDirectory() as raw:
            self.write(pathlib.Path(raw), {"executor": {"sandbox": "workspace-write",
                                                        "windowsSandbox": "elevated"}})
            settings, warnings = load_settings(raw)
        self.assertEqual([], warnings)
        self.assertEqual(DEFAULTS["executor"], settings["executor"])

    def test_bad_executor_values_fall_back_and_are_named(self):
        with tempfile.TemporaryDirectory() as raw:
            self.write(pathlib.Path(raw), {"executor": {
                "enabled": "yes", "modelVerified": "", "reasoningEffort": "max",
                "maxTaskTokens": True, "stopLossPercent": 101}})
            settings, warnings = load_settings(raw)
        self.assertEqual(5, len(warnings))
        self.assertEqual(DEFAULTS["executor"], settings["executor"])
        with tempfile.TemporaryDirectory() as raw:
            self.write(pathlib.Path(raw), {"executor": "on"})
            self.assertEqual(["shared.codex.executor is not an object; defaults apply"],
                             load_settings(raw)[1])


class TheCommandLine(FakeCodex):
    def run_main(self, argv: list[str]) -> tuple[int, str]:
        buffer = io.StringIO()
        with mock.patch.dict(os.environ, self.env, clear=False), \
                contextlib.redirect_stdout(buffer):
            code = main(argv)
        return code, buffer.getvalue()

    def test_the_exit_is_the_state(self):
        root = str(self.tmp)
        self.assertEqual(0, self.run_main(["--root", root, "probe"])[0])
        self.env["FAKE_CODEX_LIMITS"] = json.dumps(limits(primary=99))
        code, out = self.run_main(["--root", root, "probe", "--json"])
        self.assertEqual(1, code)
        self.assertEqual("unavailable", json.loads(out)["state"])
        self.assertFalse(json.loads(out)["ok"])
        self.env["FAKE_CODEX_MODE"] = "crash"
        self.assertEqual(2, self.run_main(["probe", "--root", root])[0])

    def test_the_probe_reports_no_sandbox(self):
        code, out = self.run_main(["--root", str(self.tmp), "probe", "--json"])
        self.assertEqual(0, code)
        self.assertNotIn("sandbox", json.loads(out))
        self.assertNotIn("sandbox", self.run_main(["--root", str(self.tmp), "probe"])[1])

    def test_a_missing_root_is_a_refusal(self):
        code, out = self.run_main(["--root", str(self.tmp / "nowhere"), "probe", "--json"])
        self.assertEqual(2, code)
        self.assertEqual("codex-root-missing", json.loads(out)["code"])

    def test_the_router_reaches_the_pillar(self):
        env = {**os.environ, **self.env}
        run = subprocess.run([sys.executable, str(CQ), "--root", str(self.tmp), "codex", "probe"],
                             capture_output=True, text=True, env=env)
        self.assertEqual(0, run.returncode, run.stderr)
        self.assertIn("codex probe — available (app-server)", run.stdout)


if __name__ == "__main__":
    unittest.main()
