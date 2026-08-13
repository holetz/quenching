"""The 69 goldens `capture_golden.py` froze, re-run through `cq` and compared byte-for-byte.

The goldens were originally STDOUT captured from the four pre-refactor scripts (specs, components,
session, knowledge); every case a rename or route change left stale has since been refreshed
against `cq` itself instead (`renomear-docs-para-knowledge`, task 6.1, 2026-08-13 — see `UNROUTED`
below, which the rename branch emptied down to the unrelated `pr`-record gap
`vincular-spec-a-branch-commits-e-pr` opened). `capture_golden.py`'s own `main()` cannot do that refresh: its `SCRIPTS` name
files a prior refactor deleted (see that module's docstring). `INDEX.json` names the exact exit
code and stderr behind each one, but not which workspace builder or transcript fixture produced
it — that is unrecoverable from the index, so this suite does not replay from it. It instead
imports `capture_specs`/`capture_skills`/`capture_session`/`capture_okf` and runs them again,
unmodified, against a `Capture` subclass whose `run` shells out to `cq` instead of the old script
and records the comparison instead of writing a new golden. The fixture-building code is therefore
identical on both sides of the comparison; only the binary under test changes.
"""
import json
import pathlib
import re
import subprocess
import sys
import tempfile
import unittest

import capture_golden as cg

CQ = cg.PLUGIN_ROOT / "assets" / "bin" / "cq"

# `capture_golden.normalize` replaces the capture date wherever it appears as a literal, but
# `next --front` also reports it as arithmetic — `ageDays`, and the `Nd old` it renders into
# `reason`. Those count from the wall clock, so the goldens holding them went stale the day
# after they were captured: the untouched pre-refactor specs script disagrees with its own
# golden today, which is proof the drift is the clock's and not the package's.
#
# Neutralising them costs this suite any regression in the age arithmetic itself. That is the
# cheaper side: the alternative is a fixture that reports a failure every day it is not the day
# of the capture, and a suite that cries wolf daily is one nobody reads. Applied to BOTH sides
# of every comparison, so it can never hide a difference between them.
CLOCK_DERIVED = ((re.compile(r'"ageDays": \d+'), '"ageDays": <AGE>'),
                 (re.compile(r"\b\d+d old\b"), "<AGE>d old"))


def declock(text: str) -> str:
    for pattern, token in CLOCK_DERIVED:
        text = pattern.sub(token, text)
    return text

# Golden ids `cq` does not reproduce today, and why. Two kinds live here and the reason line says
# which: a route that does not exist at all, and a route that exists over content this spec
# deliberately changed. A case leaves this set only when a later task mounts the route it is
# missing, or re-captures the golden against what the route reproduces today — never by loosening
# the comparison that proves it is still missing.
#
# What does NOT belong here is a case whose bytes still match and whose verdict alone moved: that
# is `CORRECTED_EXIT` below, which keeps asserting the stdout comparison. Parking such a case here
# would silently drop a byte-for-byte guarantee the package still meets.
#
# EMPTIED of everything but the `pr`-record gap by `renomear-docs-para-knowledge` (task 6.1,
# 2026-08-13): the fourteen entries the rename branch found here — four retired verbs with no
# route (`specs-selftest`, `skills-selftest`, `session-selftest`, `okf-selftest`),
# `session-version`'s unreachable-`--version` quirk, `skills-drift`'s removed subcommand, and
# eleven cases stale from earlier renames (`skills-lint`/`-one`,
# `skills-read-index`/`-section`/`-rules-only`, `okf-hook-posttooluse`, `okf-version`,
# `okf-validate-skeleton`/`-text`/`-findings`, `specs-status-alpha`/`-beta`) — are all
# **reproducible** through `cq` today; `capture_golden.py`'s stale `assets/docs`/`.docs`/
# `commands/docs/add.md` paths (this spec's own tasks 1.1/6.1) were the last thing standing
# between "no route" and "a route whose bytes moved." A retired verb still routes to a `cq`
# usage refusal every time it is asked — that refusal, frozen, is exactly as reproducible as any
# other case; there was never a case here where `cq` itself could not answer, only ones where the
# golden asked a stale question. The three below are unrelated to that rename — `records` gained
# a `pr` key (`vincular-spec-a-branch-commits-e-pr`) after these three were frozen.
UNROUTED = {
    "specs-list": "the `records` dict gained a `pr` key — a new write-many record, `{number, url, "
                  "date}`, narrating a PR opened but not yet merged. The frozen payload predates "
                  "the record.",
    "specs-record-unknown": "same added record as `specs-list`: the `sp-unknown-record` refusal "
                             "lists every declared record name, and `pr` is now one of them.",
    "specs-root-too-high-control-list": "same added record as `specs-list`, on the control arm of "
                                         "the root-override fixture — it lists a real spec, so its "
                                         "`records` dict carries `pr` too. The frozen payload was "
                                         "captured on the base, before the record existed.",
}

# Golden ids whose STDOUT still reproduces byte-for-byte but whose EXIT CODE the package
# deliberately corrected: `{id: (exit now, why)}`.
#
# This is a DIFFERENT claim from `UNROUTED`, and it is kept in its own set for that reason. An
# unrouted case says "no `cq` invocation reproduces this at all"; a corrected exit says "the route
# is there, the bytes are identical, and one verdict changed on purpose". Folding the second into
# the first would let a real routing loss hide behind a behaviour-change reason, which is the drift
# `test_the_unrouted_set_is_exactly_what_still_has_no_cq_equivalent` exists to catch.
#
# An entry here cannot sit vacuously: `test_a_corrected_exit_still_matches_stdout_and_really_moved`
# asserts the stdout comparison still passes AND that the frozen code and the corrected one really
# differ, so an entry that stops being a correction fails instead of being ignored.
CORRECTED_EXIT = {
    "specs-validate-all": (
        0,
        "the frozen exit of 1 came from a single `severity: warn` finding "
        "(`sp-impact-uncovered`) under a body that printed `\"ok\": true` in the same breath — the "
        "pre-refactor script's `return 1 if findings else 0` contradicted its own payload and the "
        "errors-only rule `components lint`, `components doctor` and `common.output.exit_for` all "
        "keep. The package routes this line through `exit_for`, so a warn-only workspace now "
        "exits 0 with byte-identical output.",
    ),
}


def to_cq_argv(script: str, argv: list[str]) -> list[str]:
    """The mechanical half of the translation: which pillar token(s) `cq` needs in front of
    an old script's argv. The pre-refactor specs and components scripts parsed their OWN
    `--root`, so nothing about the rest of `argv` changes crossing into `cq specs …` /
    `cq components …` — `argparse.REMAINDER` forwards it untouched. The pre-refactor session
    script mounts under `components` and carries no `--root` of its own, and the pre-refactor
    knowledge validator's CLI/hook split becomes the declared verb `cq knowledge` now routes
    on explicitly (see that pillar's `main`)."""
    if script == "specs":
        return ["specs", *argv]
    if script == "skills":
        return ["components", *argv]
    if script == "session":
        return ["components", "session", *argv]
    if script == "okf":
        if argv[:1] == ["--version"]:
            return ["knowledge", "--version"]
        if not argv:
            return ["knowledge", "hook"]
        return ["knowledge", "validate", *argv]
    raise ValueError(f"unknown script key: {script!r}")


class Replay(cg.Capture):
    """`capture_golden.Capture`, aimed at `cq` — the only seam this suite touches.

    Every write case builds its own throwaway workspace, and `outcome_for` appends `## Outcome`
    to a spec before a case reads it; both happen in `capture_specs` before `run` is ever
    called, so overriding `run` alone is enough to swap the binary under test without
    reconstructing anything the index cannot tell us.
    """

    def __init__(self, tmp: pathlib.Path) -> None:
        super().__init__(tmp)
        self.results: list[dict] = []

    def run(self, name: str, script: str, argv: list[str], *, cwd, ws=None, stdin=None,
            ext: str = "json") -> None:
        cq_argv = to_cq_argv(script, argv)
        proc = subprocess.run([sys.executable, str(CQ)] + cq_argv, cwd=str(cwd), env=self.env(),
                              input=stdin, capture_output=True, text=True)
        self.results.append({
            "name": name,
            "golden": f"{name}.{ext}",
            "stdout": declock(cg.normalize(proc.stdout, ws)),
            "stderr": declock(cg.normalize(proc.stderr, ws)),
            "exit": proc.returncode,
        })


class GoldenContract(unittest.TestCase):
    """Every case `capture_golden.py` froze, re-run through `cq`."""

    BY_GOLDEN = {
        e["golden"]: e
        for e in json.loads((cg.GOLDEN_DIR / "INDEX.json").read_text(encoding="utf-8"))["captured"]
    }

    @classmethod
    def setUpClass(cls) -> None:
        cls._tmp = tempfile.TemporaryDirectory(prefix="quenching-golden-replay-")
        tmp = pathlib.Path(cls._tmp.name)
        (tmp / "tmpdir").mkdir()
        replay = Replay(tmp)
        cg.capture_specs(replay)
        cg.capture_skills(replay)
        cg.capture_session(replay)
        cg.capture_okf(replay)
        cls.results = replay.results
        cls.skipped = replay.skipped

    @classmethod
    def tearDownClass(cls) -> None:
        cls._tmp.cleanup()

    def _golden_and_entry(self, result: dict) -> tuple[str, dict]:
        entry = dict(self.BY_GOLDEN[result["golden"]])
        entry["stderr"] = declock(entry["stderr"])
        golden_text = declock((cg.GOLDEN_DIR / result["golden"]).read_text(encoding="utf-8"))
        return golden_text, entry

    def _expected_exit(self, result: dict, entry: dict) -> int:
        """The frozen exit code, unless this case is one the package deliberately corrected."""
        if result["name"] in CORRECTED_EXIT:
            return CORRECTED_EXIT[result["name"]][0]
        return entry["exit"]

    def _matches_golden(self, result: dict) -> bool:
        golden_text, entry = self._golden_and_entry(result)
        return (result["stdout"] == golden_text
                and result["exit"] == self._expected_exit(result, entry)
                and result["stderr"] == entry["stderr"])

    def test_the_unrouted_set_is_exactly_what_still_has_no_cq_equivalent(self):
        # Derived from the actual comparison, not from UNROUTED's own keys — a case that
        # starts matching (routed) or stops matching (regressed) shows up as a set difference
        # either way, which is the one drift this suite exists to catch.
        observed = {r["name"] for r in self.results if not self._matches_golden(r)}
        self.assertEqual(observed, set(UNROUTED))

    def test_every_routed_case_matches_its_golden_through_cq(self):
        for result in self.results:
            if result["name"] in UNROUTED:
                continue
            with self.subTest(case=result["name"]):
                golden_text, entry = self._golden_and_entry(result)
                self.assertEqual(result["stdout"], golden_text)
                self.assertEqual(result["exit"], self._expected_exit(result, entry))
                self.assertEqual(result["stderr"], entry["stderr"])

    def test_a_corrected_exit_still_matches_stdout_and_really_moved(self):
        by_name = {r["name"]: r for r in self.results}
        for name, (corrected, _reason) in CORRECTED_EXIT.items():
            with self.subTest(case=name):
                result = by_name[name]
                golden_text, entry = self._golden_and_entry(result)
                # The correction is about the verdict, never about the output: a case whose bytes
                # also drifted is an unrouted case wearing this set's name.
                self.assertEqual(result["stdout"], golden_text)
                self.assertEqual(result["stderr"], entry["stderr"])
                self.assertNotEqual(entry["exit"], corrected)
                self.assertEqual(result["exit"], corrected)

    def test_the_unrouted_cases_are_skipped_by_name_not_by_a_silent_if(self):
        for name, reason in UNROUTED.items():
            with self.subTest(case=name):
                self.skipTest(reason)

    def test_specs_release_was_never_captured_and_stays_uncompared(self):
        # `release` rewrites this repo's own version and tags a commit — there is no dry-run
        # to have captured, so nothing here may pretend a golden exists for it.
        self.assertEqual([s["id"] for s in self.skipped], ["specs-release"])
        self.assertFalse(any(p.stem == "specs-release" for p in cg.GOLDEN_DIR.iterdir()))


if __name__ == "__main__":
    unittest.main()
