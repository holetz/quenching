"""Contract: the definition pass plans the process surface as tasks — never edits it.

`/quenching-specs develop` may be asked, in the input's own words or with `--with-surface`, to
refine the workflow, a skill or a reference alongside the spec's objective. What it does is PLAN
that surface as `### 1. Process surface`, the first group of `## Tasks`; `/quenching-specs execute`
writes it. Seven files carry the contract, and each section below pins
the anchor the citing prose addresses with `§X` — the reader resolves a heading, so a rename here
is an orphaned citation there.
"""

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[2]

QUESTIONS = "quenching/references/specs-develop/questions.md"
ARTIFACTS = "quenching/references/specs-develop/artifacts.md"
DEVELOP = "quenching/skills/quenching-specs/references/develop.md"
ROUTER = "quenching/skills/quenching-specs/SKILL.md"
EVIDENCE = "quenching/references/align/evidence-doctrine.md"
LIFECYCLE = "docs/standards/workflows/plan-lifecycle.md"
AGENTS = "docs/standards/automation/agents.md"

GROUP = "### 1. Process surface"


def text(rel):
    """The file, markup collapsed: a phrase wrapped across a line still matches."""
    return re.sub(r"\s+", " ", (ROOT / rel).read_text(encoding="utf-8"))


def heading(rel, name):
    """True when the file carries `name` as a heading of its own line."""
    body = (ROOT / rel).read_text(encoding="utf-8")
    return re.search(rf"^{re.escape(name)}$", body, re.MULTILINE) is not None


class QuestionsTests(unittest.TestCase):
    """`questions.md` §Surface refinement — the trigger, the plan-not-edit rule, the grammar."""

    def test_the_section_exists(self):
        self.assertTrue(heading(QUESTIONS, "## Surface refinement"))

    def test_the_input_accepts_the_surface_flag(self):
        self.assertIn("--with-surface", text(QUESTIONS))

    def test_the_trigger_is_never_an_inference(self):
        self.assertIn("input, never a reading of the state", text(QUESTIONS))

    def test_it_plans_and_does_not_edit(self):
        self.assertIn("It plans; it does not edit", text(QUESTIONS))

    def test_it_names_the_task_group(self):
        self.assertIn(GROUP, text(QUESTIONS))

    def test_it_names_the_stop_condition(self):
        self.assertIn(
            "**Stop when** every declared surface path is named by a task carrying "
            "`files:` and `verify:`, `.agents/quenching/bin/cq specs parallel --spec <id>` "
            "exits 0, and nothing outside the spec was written.",
            text(QUESTIONS),
        )

    def test_the_process_surface_is_always_parked(self):
        self.assertIn("**Park the process surface, always.**", text(QUESTIONS))

    def test_a_cost_finding_carries_a_counted_figure(self):
        self.assertIn("it carries a counted figure", text(QUESTIONS))

    def test_the_figure_comes_from_measured_context(self):
        self.assertIn("read from `cq components session context`", text(QUESTIONS))


class ImpactTests(unittest.TestCase):
    """`artifacts.md` — the fourth `## Impact` sub-heading, unparsed, every path gets a task."""

    def test_the_fourth_sub_heading_is_documented(self):
        self.assertTrue(heading(ARTIFACTS, "### Process surface this spec expects to touch"))

    def test_it_declares_four_sub_headings(self):
        self.assertIn("Four sub-headings", text(ARTIFACTS))

    def test_the_sub_heading_is_unparsed(self):
        self.assertIn("It is **unparsed**", text(ARTIFACTS))

    def test_every_declared_path_gets_a_task(self):
        self.assertIn("Every path it names gets a task", text(ARTIFACTS))


class DevelopTests(unittest.TestCase):
    """`develop.md` — step 3, `### 3d`, steps 6–8, and the invariant that replaced the old one."""

    def test_the_step_exists(self):
        self.assertTrue(heading(DEVELOP, "### 3d. Enumerate the surface refinement"))

    def test_the_body_names_the_ask(self):
        self.assertIn("--with-surface", text(DEVELOP))

    def test_the_body_names_the_group(self):
        self.assertIn(GROUP, text(DEVELOP))

    def test_the_pass_writes_only_the_spec(self):
        self.assertIn("Never edit anything but the spec", text(DEVELOP))

    def test_the_old_implementation_only_invariant_is_absent(self):
        self.assertNotIn("NEVER edit implementation code", text(DEVELOP))


class RouterTests(unittest.TestCase):
    """`SKILL.md` — the `develop` row is picked when the input carries the ask."""

    def test_the_develop_row_names_the_surface_ask(self):
        body = (ROOT / ROUTER).read_text(encoding="utf-8")
        row = next(line for line in body.splitlines() if line.startswith("| `develop` |"))
        self.assertIn("surface refinement", re.sub(r"\s+", " ", row))


class EvidenceTests(unittest.TestCase):
    """`evidence-doctrine.md` §3 — a web source is cited, dated, and never the rule alone."""

    def test_the_section_exists(self):
        self.assertTrue(
            heading(EVIDENCE, "## 3. A web source is cited, dated, and never the rule alone"))

    def test_it_requires_the_publication_date(self):
        self.assertIn("publication date", text(EVIDENCE))

    def test_it_requires_the_retrieval_date(self):
        self.assertIn("retrieval date", text(EVIDENCE))

    def test_a_web_source_cannot_ground_a_binding_rule_alone(self):
        self.assertIn("A web source may not ground a binding rule alone", text(EVIDENCE))


class LifecycleTests(unittest.TestCase):
    """`plan-lifecycle.md` — the surface is the spec's work on the ask, a parked line without it."""

    def test_the_section_exists(self):
        self.assertTrue(heading(LIFECYCLE, "### Refining the process surface alongside a spec"))

    def test_it_names_the_group(self):
        self.assertIn(GROUP, text(LIFECYCLE))

    def test_without_an_ask_it_parks_a_discoveries_line(self):
        self.assertIn(
            "Without an ask it is a follow-up like any other, and the table above applies: "
            "one `## Discoveries` line carrying `path:line` and the consequence",
            text(LIFECYCLE),
        )


class ResearchProfileTests(unittest.TestCase):
    """The profile ships with the payload; `agents.md` is this repo's projection of it."""

    def test_the_distributed_reference_owns_the_profile(self):
        self.assertIn("**The research profile.**", text(QUESTIONS))

    def test_the_distributed_profile_is_read_only(self):
        self.assertIn("`Read`, `Grep`, `Glob`, `WebSearch`, `WebFetch`", text(QUESTIONS))
        self.assertIn("never `Edit`, `Write`, `NotebookEdit` or `Bash`", text(QUESTIONS))

    def test_the_standard_is_a_projection_of_the_reference(self):
        self.assertIn("This standard is the repo-side projection of it", text(AGENTS))

    def test_the_section_exists(self):
        self.assertTrue(heading(AGENTS, "## The research profile"))

    def test_the_profile_can_search_and_fetch_web_sources(self):
        self.assertIn("WebSearch, WebFetch", text(AGENTS))

    def test_the_profile_never_writes_or_decides(self):
        self.assertIn("Never writes and never decides", text(AGENTS))


if __name__ == "__main__":
    unittest.main()
