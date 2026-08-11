"""The 69 goldens `capture_golden.py` froze, re-run through `cq` and compared byte-for-byte.

The goldens are STDOUT captured from the four pre-refactor scripts (specs, components, session,
knowledge) — four scripts a refactor cannot recapture from, only be measured against (see that module's
docstring). `INDEX.json` names the exact exit code and stderr behind each one, but not which
workspace builder or transcript fixture produced it — that is unrecoverable from the index, so
this suite does not replay from it. It instead imports `capture_specs`/`capture_skills`/
`capture_session`/`capture_okf` and runs them again, unmodified, against a `Capture` subclass
whose `run` shells out to `cq` instead of the old script and records the comparison instead of
writing a new golden. The fixture-building code is therefore identical on both sides of the
comparison; only the binary under test changes.
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

# Golden ids with no `cq` invocation that reproduces them today, and why. A case leaves this
# set only when a later task mounts the route it is missing — never by loosening the
# comparison that proves it is still missing.
UNROUTED = {
    "specs-selftest": "`selftest` is in no pillar's DISPATCH and is not coming back: task 6.3 "
                       "measured every suite behind it into `tests/`, including the embedded "
                       "asset lockstep that was its last non-unit-test reason to exist "
                       "(`test_specs_assets.py`).",
    "skills-selftest": "same decision as `specs-selftest`: the verb is retired, and what it "
                        "proved lives in `tests/test_components.py`.",
    "session-selftest": "same decision as `specs-selftest`: the verb is retired, and what it "
                         "proved lives in `tests/test_session.py`.",
    "okf-selftest": "same decision as `specs-selftest`: the knowledge pillar routes `hook` and "
                     "`validate` only, and what `selftest` proved lives in "
                     "`tests/test_knowledge.py`.",
    "session-version": "`cq components session --version` never reaches the session module's "
                        "own `--version` flag: the components pillar's `main` answers any argv "
                        "containing `--version` before the `session` subparser runs, so it "
                        "prints the components pillar's stamp (`skills <VERSION>`) and exits "
                        "0 rather than raising a routing error. The text this golden froze "
                        "(`session <VERSION>`) has no reachable `cq` invocation.",
    "skills-drift": "`drift` detected a legacy copy of one of the four pre-refactor scripts "
                     "left behind under a target's `.claude/hooks/` by an old install offer. "
                     "Task 10.1 of this same spec removed all four from the plugin, so there is "
                     "nothing left for the subcommand to compare an installed copy against, and "
                     "it was retired with it — `components/commands/cli.py` routes no `drift` "
                     "verb any more.",
    "skills-lint": "captured against the command surface as it stood before this spec's own "
                    "sections 7-9 restructured it (front renames, the `components` split into "
                    "`command`/`agent`/`hook`/`harness`, new commands minted since) — the finding "
                    "list this route now returns is a different, larger, CORRECT set for a "
                    "surface with a different shape, not a divergence to reconcile.",
    "skills-lint-one": "captured against `commands/docs/add.md`, which task 7.1 moved to "
                        "`commands/knowledge/add.md`; the golden's `sk-no-commands` refusal for "
                        "the (now nonexistent) old path is the correct answer for a path that no "
                        "longer resolves, not a route this suite can still exercise identically.",
    "skills-read-index": "reads `align/convergence.md`'s own section index — its `chars` per "
                          "heading counts the very citations this spec renamed inside that file "
                          "(`docs:align` → `knowledge:align` and the like), so the byte counts "
                          "shifted with the rename itself; the route is reachable, the content it "
                          "reads is not the content that was frozen.",
    "skills-read-section": "same cause as `skills-read-index`, one section of the same file: the "
                            "cited section's own prose now reads `cq knowledge validate` where the "
                            "golden froze the pre-refactor OKF validator script's name, because "
                            "task 8.x's citation sweep rewrote that section along with everything "
                            "else.",
    "skills-read-rules-only": "same cause as `skills-read-section`, filtered to the `<!-- rules "
                               "-->` half of the same renamed section.",
    "okf-hook-posttooluse": "the hook's own `sk-no-frontmatter` remedy text named the skill IDs "
                             "`quenching-docs-align`/`quenching-docs-add`; task 10.3 renamed them "
                             "to `quenching-knowledge-align`/`quenching-knowledge-add` alongside "
                             "the same fix in `knowledge/render.py`'s live source, so the frozen "
                             "hook-JSON response and the live one now differ by design.",
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

    def _matches_golden(self, result: dict) -> bool:
        golden_text, entry = self._golden_and_entry(result)
        return (result["stdout"] == golden_text
                and result["exit"] == entry["exit"]
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
                self.assertEqual(result["exit"], entry["exit"])
                self.assertEqual(result["stderr"], entry["stderr"])

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
