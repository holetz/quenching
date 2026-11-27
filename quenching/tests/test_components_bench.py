import contextlib
import io
import json
import pathlib
import tempfile
import unittest
from types import SimpleNamespace

import _paths  # noqa: F401
from quenching.components import bench, bench_cycle
from quenching.components.commands.bench import cmd_bench
from quenching.components.commands.cli import DISPATCH, build_parser

REPO = pathlib.Path(__file__).resolve().parents[2]


def write(path: pathlib.Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def target(duplicate: bool = False, dead_citation: bool = False) -> pathlib.Path:
    root = pathlib.Path(tempfile.mkdtemp())
    write(root / "CLAUDE.md", "x" * 400)
    write(root / ".claude/skills/alfa/SKILL.md", "---\nname: alfa\ndescription: " + "d" * 100 + "\n---\nbody\n")
    if duplicate:
        write(root / ".agents/skills/alfa/SKILL.md", "---\nname: alfa\ndescription: dup\n---\nbody\n")
    write(root / ".claude/agents/ag.md", "---\nname: ag\ndescription: agente\n---\nbody\n")
    write(root / ".agents/quenching/references/x/rules.md", "## Rule\n\nBinding rule.\n\n## Story\n\nWhy.\n")
    section = "Missing" if dead_citation else "Rule"
    write(root / ".agents/skills/quenching-specs/SKILL.md", "---\nname: quenching-specs\ndescription: r\n---\nrouter\n")
    for flow in bench.FLOWS:
        write(root / f".agents/skills/quenching-specs/references/{flow}.md",
              f"# {flow}\n\nSee [r](.agents/quenching/references/x/rules.md) §{section}\n")
    return root


class Superficie(unittest.TestCase):
    def test_superficie_measures_each_harness_in_tokens(self):
        payload, findings = bench.measure(target(), ("claude", "copilot"))
        claude = payload["harnesses"]["claude"]
        self.assertEqual(claude["tokens"]["instructions"], 100)
        self.assertEqual(claude["skillCount"], 1)
        self.assertEqual(claude["agentCount"], 1)
        self.assertEqual(claude["tokens"]["mcp"], 0)
        self.assertEqual(claude["total"], sum(claude["tokens"].values()))
        self.assertEqual(findings, [])
        self.assertEqual(set(payload["flows"]), set(bench.FLOWS))

    def test_superficie_flow_ceiling_adds_router_flow_and_cited_sections(self):
        payload, _ = bench.measure(target(), ("claude",))
        row = payload["flows"]["develop"]
        self.assertEqual(row["citedBytes"], len("Binding rule.".encode()))
        self.assertEqual(row["tokens"], bench.tokens(row["routerBytes"] + row["flowBytes"] + row["citedBytes"]))

    def test_superficie_split_flow_ceiling_is_its_most_expensive_stage(self):
        root = target()
        refs = ".agents/skills/quenching-specs/references"
        write(root / f"{refs}/create.md",
              f"# create\n\n### 1. One\n\nLoad [s]({refs}/specs-create/step-1-one.md)\n\n"
              f"### 2. Two\n\nLoad [s]({refs}/specs-create/step-2-two.md)\n")
        write(root / f"{refs}/specs-create/step-1-one.md", "small\n")
        write(root / f"{refs}/specs-create/step-2-two.md",
              "See [r](.agents/quenching/references/x/rules.md) §Rule\n" + "y" * 4000)
        payload, findings = bench.measure(root, ("claude",))
        row = payload["flows"]["create"]
        self.assertEqual(findings, [])
        self.assertEqual(set(row["stages"]), {"step-1-one", "step-2-two"})
        self.assertEqual(row["tokens"], max(row["stages"].values()))
        self.assertGreater(row["stages"]["step-2-two"], row["stages"]["step-1-one"])
        # the index is not charged for the step files it links
        self.assertLess(row["flowBytes"] + row["citedBytes"], 1000)

    def test_superficie_missing_stage_file_is_a_finding(self):
        root = target()
        refs = ".agents/skills/quenching-specs/references"
        write(root / f"{refs}/create.md", f"# create\n\nLoad [s]({refs}/specs-create/step-1-gone.md)\n")
        _, findings = bench.measure(root, ("claude",))
        self.assertIn("ct-cost-no-reference", {f["code"] for f in findings})

    def test_superficie_budget_over_is_a_finding(self):
        budget = {"prefix": {"claude": 1}, "flow": {"develop": 1}}
        _, findings = bench.measure(target(), ("claude",), bench.load_budget_dict(budget))
        codes = {f["code"] for f in findings}
        self.assertIn("ct-bench-prefix-over", codes)
        self.assertIn("ct-bench-flow-over", codes)

    def test_superficie_sub_step_is_measured_with_its_step(self):
        root = target()
        link = ".agents/skills/quenching-specs/references/specs-execute/"
        write(root / ".agents/skills/quenching-specs/references/execute.md",
              f"# execute\n\n[one]({link}step-1-one.md)\n")
        write(root / ".agents/skills/quenching-specs/references/specs-execute/step-1-one.md",
              f"one body\n\n[a]({link}step-1a-sub.md)\n")
        write(root / ".agents/skills/quenching-specs/references/specs-execute/step-1a-sub.md", "sub\n")
        payload, _ = bench.measure(root, ("claude",))
        stages = payload["flows"]["execute"]["stages"]
        self.assertEqual(set(stages), {"step-1-one", "step-1a-sub"})
        self.assertGreaterEqual(stages["step-1a-sub"], stages["step-1-one"])

    def test_superficie_within_budget_is_clean(self):
        _, findings = bench.measure(target(), bench.HARNESSES)
        self.assertEqual([f for f in findings if f["severity"] == "error"], [])

    def test_superficie_citation_that_does_not_resolve_is_a_finding(self):
        _, findings = bench.measure(target(dead_citation=True), ("claude",))
        self.assertIn("ct-cost-no-section", {f["code"] for f in findings})

    def test_superficie_duplicate_skill_is_reported_for_the_harness_that_reads_both(self):
        payload, findings = bench.measure(target(duplicate=True), bench.HARNESSES)
        self.assertEqual(payload["harnesses"]["claude"]["duplicateSkills"], {})
        self.assertIn("alfa", payload["harnesses"]["opencode"]["duplicateSkills"])
        dupes = [f for f in findings if f["code"] == "ct-bench-skill-duplicate"]
        self.assertTrue(dupes and all(f["severity"] == "warning" for f in dupes))

    def test_superficie_mcp_catalog_counts_only_where_the_harness_registers_it(self):
        root = target()
        write(root / ".mcp.json", json.dumps({"mcpServers": {"quenching": {
            "command": "python3", "args": [".agents/quenching/bin/cq", "mcp", "--only", "components"]}}}))
        payload, _ = bench.measure(root, ("claude", "opencode"))
        self.assertGreater(payload["harnesses"]["claude"]["tokens"]["mcp"], 0)
        self.assertEqual(payload["harnesses"]["opencode"]["tokens"]["mcp"], 0)

    def test_conclude_is_split_per_step_and_every_stage_fits_the_ceiling(self):
        payload, _ = bench.measure(REPO, ("claude",))
        row = payload["flows"]["conclude"]
        self.assertEqual(len(row["stages"]), 9)
        self.assertEqual(bench.DEFAULT_BUDGET["flow"]["conclude"], 15_000)
        self.assertLessEqual(row["tokens"], 15_000)

    def test_superficie_budget_file_overrides_key_by_key(self):
        root = pathlib.Path(tempfile.mkdtemp())
        path = root / "b.json"
        path.write_text(json.dumps({"flow": {"develop": 7}}), encoding="utf-8")
        budget = bench.load_budget(str(path))
        self.assertEqual(budget["flow"]["develop"], 7)
        self.assertEqual(budget["flow"]["create"], bench.DEFAULT_BUDGET["flow"]["create"])
        self.assertEqual(budget["prefix"], bench.DEFAULT_BUDGET["prefix"])


class EstagiosDoDevelop(unittest.TestCase):
    def test_every_develop_stage_of_this_repository_fits_15k_tokens(self):
        payload, findings = bench.measure(REPO, ("claude",))
        self.assertEqual(bench.DEFAULT_BUDGET["flow"]["develop"], 15_000)
        row = payload["flows"]["develop"]
        self.assertTrue(row["stages"])
        self.assertLessEqual(row["tokens"], 15_000)
        self.assertEqual([f for f in findings if f["code"] == "ct-bench-flow-over"], [])


class Ciclo(unittest.TestCase):
    def test_ciclo_closes_on_a_throwaway_fixture_and_removes_it(self):
        payload, findings = bench_cycle.measure(REPO)
        self.assertTrue(payload["closed"], findings)
        self.assertEqual(set(payload["flows"]), {"create", "develop", "execute", "conclude"})
        self.assertEqual([f for f in findings if f["severity"] == "error"], [])
        self.assertIsNone(payload["fixture"])

    def test_ciclo_keep_fixture_leaves_the_path(self):
        payload, _ = bench_cycle.measure(REPO, keep=True)
        try:
            self.assertTrue(pathlib.Path(payload["fixture"]).is_dir())
        finally:
            import shutil
            shutil.rmtree(payload["fixture"], ignore_errors=True)


def run(**kw) -> tuple[int, dict]:
    args = SimpleNamespace(layers=("superficie",), harness=bench.HARNESSES, budget=None, target=None,
                           keep_fixture=False, json=True)
    for key, value in kw.items():
        setattr(args, key, value)
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        status = cmd_bench(args, "")
    return status, json.loads(out.getvalue())


class Verb(unittest.TestCase):
    def test_bench_is_registered(self):
        self.assertIn("bench", DISPATCH)
        self.assertEqual(build_parser().parse_args(["bench", "--layers", "superficie,ciclo"]).layers,
                         ("superficie", "ciclo"))

    def test_bench_exits_1_over_budget_and_0_within(self):
        root = target()
        low = root / "low.json"
        low.write_text(json.dumps({"prefix": {"claude": 1}}), encoding="utf-8")
        status, payload = run(target=str(root), budget=str(low))
        self.assertEqual((status, payload["ok"]), (1, False))
        status, payload = run(target=str(root))
        self.assertEqual((status, payload["ok"]), (0, True))

    def test_bench_refuses_a_missing_target_and_an_unreadable_budget(self):
        self.assertEqual(run(target="/nonexistent-bench-target")[0], 2)
        self.assertEqual(run(target=str(target()), budget="/nonexistent.json")[0], 2)

    def test_bench_default_budget_holds_on_this_repository(self):
        status, payload = run(target=str(REPO))
        self.assertEqual(status, 0, [f for f in payload["findings"] if f["severity"] == "error"])


if __name__ == "__main__":
    unittest.main()
