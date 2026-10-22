"""`validate_spec` warns on a task that runs a generator but declares no `files:`.

The verifier fails the scope of whatever such a task writes, so the omission is cheaper to
name at definition time. The rule is a heuristic over the task title and `verify:`: a warning,
never an error."""
import unittest

import _paths  # noqa: F401  — must precede the `quenching` import; see its docstring
from quenching.specs.backends.memory import MemoryBackend
from quenching.specs.commands.validate import validate_spec
from quenching.specs.schema import capture_form

CODE = "sp-generator-no-files"


def _findings(tasks_body: str) -> list[dict]:
    doc = (capture_form().replace("<SLUG>", "alpha").replace("<TITLE>", "Alpha")
           .replace("<DATE>", "2026-01-01").replace("<VERIFICATION>", "per-task"))
    doc += "\n## Tasks\n\n### 1. Build\n\n" + tasks_body + "\n"
    b = MemoryBackend()
    b.create_spec("plans", doc)
    return [f for f in validate_spec(b, b.list_specs()[0]) if f["code"] == CODE]


class GeneratorWithoutFiles(unittest.TestCase):
    def test_a_generator_title_with_no_files_is_flagged_as_a_warning(self):
        found = _findings("- [ ] 1.1 Regenerar os espelhos pelos geradores\n")
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0]["severity"], "warn")
        self.assertEqual(found[0]["task"], "1.1")

    def test_a_generator_in_verify_with_empty_files_is_flagged(self):
        found = _findings("- [ ] 1.1 Atualizar\n      files: []\n"
                          "      verify: python3 scripts/generate_plugin_modules.py\n")
        self.assertEqual(len(found), 1)

    def test_declared_files_clear_the_warning(self):
        found = _findings("- [ ] 1.1 Regenerar os espelhos\n      files: plugins/a.md\n")
        self.assertEqual(found, [])

    def test_a_task_that_runs_no_generator_is_not_flagged(self):
        self.assertEqual(_findings("- [ ] 1.1 Rodar o gate\n"), [])


if __name__ == "__main__":
    unittest.main()
