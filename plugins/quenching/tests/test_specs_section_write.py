"""The multi-section write — the stream splitter, and the write path over it.

`cq specs section <slug> "<H1>,<H2>" --write` used to refuse (`sp-write-plural`) because stdin is
one stream and nothing said where one section's body ended. The delimiter chosen is the document's
own `## <Heading>` line, which is the exact form the plural READ already prints — so the two
round-trip and no second grammar was invented.

Every case below runs against the function that ships. `split_section_stream` takes its candidate
set as an argument for precisely that reason, the way `resolve_heading_name` already does:
`/docs/standards/code/canonical-set-parsing.md` §A case must exercise the production function,
not a copy of its rule is what this file is answering to. The write path's own cases go through
`cmd_section` itself over a real files-backend workspace, never through a second reading of its
refusal ladder written here.
"""
import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest import mock

import _paths  # noqa: F401  — must precede the `quenching` import; see its docstring
from quenching.specs.backends.memory import MemoryBackend
from quenching.specs.commands import granular as granular_module
from quenching.specs.commands import validate as validate_module
from quenching.specs.commands.granular import cmd_section
from quenching.specs.commands.output import Emitter
from quenching.specs.parse.edit import split_section_stream
from quenching.specs.schema import canonical_headings

CANON = canonical_headings()

# One row per shape a stdin stream can take. `expected` is what the SHIPPED splitter must return:
# `[]` is the claim "this stream is one raw body", which is what every caller had before the
# plural write existed and what the singular form must keep meaning.
SPLIT_CASES = (
    ("a raw body is not a stream",
     "corpo cru\nmais corpo", []),
    ("two blocks, in the order the stream carries them",
     "## Proposal\n\nA\n\n## Risks\n\nB\n", [("Proposal", "A"), ("Risks", "B")]),
    ("a fenced `## ` is content, never a cut",
     "## Proposal\n\n```\n## Risks\n```\n\nA\n",
     [("Proposal", "```\n## Risks\n```\n\nA")]),
    ("a stream that does not OPEN on a canonical heading is one raw body",
     "## Nao Canonico\n\nX\n", []),
    ("prose before the first heading is one raw body too",
     "preambulo\n\n## Proposal\n\nA\n", []),
    ("an unresolved heading AFTER the stream declared itself is a finding, not prose",
     "## Proposal\n\nA\n\n## Nao Canonico\n\nX\n", [("Proposal", "A"), (None, "X")]),
    ("a repeated heading survives as two blocks — the repeat is the finding",
     "## Proposal\n\nA\n\n## Proposal\n\nB\n", [("Proposal", "A"), ("Proposal", "B")]),
    ("a unique prefix resolves, exactly as it does on the command line",
     "## Out of\n\nA\n", [("Out of Scope", "A")]),
    ("an empty stream carries nothing",
     "", []),
    ("a heading with an empty body keeps the block",
     "## Proposal\n\n", [("Proposal", "")]),
    ("a level-3 heading belongs to its parent block",
     "## Impact\n\n### Product code this spec expects to touch\n\n- `a.py`\n",
     [("Impact", "### Product code this spec expects to touch\n\n- `a.py`")]),
)


class TheStreamSplitter(unittest.TestCase):
    """The cut rule, proved against `split_section_stream` itself."""

    def test_every_case_holds_for_the_shipped_splitter(self):
        for label, stream, expected in SPLIT_CASES:
            with self.subTest(label):
                self.assertEqual(split_section_stream(stream, CANON), expected)

    def test_the_candidate_set_is_an_argument_and_narrows_the_cut(self):
        """Handed a narrower set, the same stream stops resolving — which is what proves the
        cut reads the set it was given rather than a canonical list baked into the body."""
        stream = "## Proposal\n\nA\n\n## Risks\n\nB\n"
        self.assertEqual(split_section_stream(stream, ["Proposal"]),
                         [("Proposal", "A"), (None, "B")])


SPEC = """---
title: Alpha
date: 2026-08-15
---

# Alpha

## Problem

O problema.
"""

# The six `build` sections plus a `## Handoff` already split into its evergreen block and one block
# per `### N.`, over a `## Tasks` whose section 1 is closed and whose section 2 is open — so
# `current_handoff_section` answers 2 and the block a reader must NEVER be handed is section 1's.
HANDOFF_SPEC = """---
title: Alpha
date: 2026-08-15
---

# Alpha

## Proposal

A proposta.

## Out of Scope

Fora.

## Impact

O impacto.

## Design

O desenho.

## Handoff

O bloco evergreen.

### 1. Primeira seção

Fechada — nenhum leitor deve receber isto.

### 2. Segunda seção

O que a seção corrente precisa.

## Tasks

### 1. Primeira seção

- [x] 1.1 Feita

### 2. Segunda seção

- [ ] 2.1 Aberta
"""

GLOBAL_BLOCK = "O bloco evergreen."
CURRENT_BLOCK = "### 2. Segunda seção\n\nO que a seção corrente precisa."


class _Args:
    """`cmd_section`'s argparse namespace, with the defaults the parser gives it."""

    def __init__(self, **kw):
        self.json = True
        self.moment = None
        self.write = False
        self.scope = None
        self.heading = None
        self.spec = 1
        self.__dict__.update(kw)


class _Workspace(unittest.TestCase):
    """An in-memory provider fixture holding ONE spec for both read and write cases."""

    spec_text = SPEC

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = self.tmp.name
        self.backend = MemoryBackend()
        self._open_granular = mock.patch.object(
            granular_module, "open_backend", lambda _root: (self.backend, {}))
        self._open_validate = mock.patch.object(
            validate_module, "open_backend", lambda _root: (self.backend, {}))
        self._open_granular.start()
        self._open_validate.start()
        self.addCleanup(self._open_granular.stop)
        self.addCleanup(self._open_validate.stop)
        self.write_spec(self.spec_text)

    def write_spec(self, text):
        # `MemoryBackend` allocates 1 for the first spec, which is what `_Args.spec`
        # defaults to — the fixture holds exactly one, so the ID is knowable rather than
        # threaded through every case.
        if self.backend.docs:
            info, error = self.backend.read_spec(1)
            self.assertFalse(error, error)
            self.backend.write_spec(info, text)
        else:
            self.backend.create_spec("plans", text)

    def run_section(self, stdin=None, **kw):
        """`cmd_section` as the CLI calls it, returning (exit code, parsed payload).

        `stdin=None` is a tty — the shape the command reads as "no body given" — so a read
        case and a write case differ only in what this helper is handed."""
        buf, stream = io.StringIO(), io.StringIO(stdin or "")
        stream.isatty = lambda: stdin is None
        with mock.patch("sys.stdin", stream), redirect_stdout(buf):
            code = cmd_section(_Args(**kw), self.root, Emitter())
        return code, json.loads(buf.getvalue())

    def state(self, heading):
        return self.run_section(heading=heading)[1]["sections"][0]["state"]


class TheWritePath(_Workspace):
    """The command over a files-backend workspace — the whole ladder, refusals included."""

    def test_two_sections_land_in_one_call_and_read_back(self):
        code, obj = self.run_section(heading="Proposal,Risks", write=True,
                                     stdin="## Proposal\n\nA\n\n## Risks\n\nB\n")
        self.assertEqual(code, 0, obj)
        self.assertEqual(obj["sections"], [{"heading": "Proposal", "action": "created"},
                                           {"heading": "Risks", "action": "created"}])
        code, read = self.run_section(heading="Proposal,Risks")
        self.assertEqual(code, 0, read)
        self.assertEqual([s["body"].strip() for s in read["sections"]], ["A", "B"])

    def test_canonical_position_survives_a_plural_write(self):
        """`## Proposal` arrives second in the stream and still lands before `## Risks`. The
        splice stays `upsert_section`'s; a plural write must not become a second placement
        rule, and it is the re-derivation between splices that keeps it from becoming one."""
        self.run_section(heading="Risks,Proposal", write=True,
                         stdin="## Risks\n\nB\n\n## Proposal\n\nA\n")
        text = self.read_spec_text()
        self.assertLess(text.index("## Proposal"), text.index("## Risks"))

    def read_spec_text(self):
        info, error = self.backend.read_spec(1)
        self.assertFalse(error, error)
        return info["text"]

    def test_the_singular_form_is_untouched(self):
        """A raw body under one heading writes what it always wrote, and the payload keeps
        `heading`/`action` flat — `sections` is what the PLURAL form adds, and only it."""
        code, obj = self.run_section(heading="Proposal", write=True,
                                     stdin="corpo cru\nmais corpo\n")
        self.assertEqual(code, 0, obj)
        self.assertEqual((obj["heading"], obj["action"]), ("Proposal", "created"))
        self.assertNotIn("sections", obj)
        self.assertEqual(self.run_section(heading="Proposal")[1]["body"].strip(),
                         "corpo cru\nmais corpo")

    def test_a_set_mismatch_refuses_and_writes_nothing(self):
        code, obj = self.run_section(heading="Proposal,Risks", write=True,
                                     stdin="## Proposal\n\nA\n")
        self.assertEqual(code, 2)
        self.assertEqual(obj["code"], "sp-write-set-mismatch")
        self.assertEqual((obj["declared"], obj["stream"]),
                         (["Proposal", "Risks"], ["Proposal"]))
        self.assertEqual(self.state("Proposal"), "absent")

    def test_a_repeated_heading_refuses(self):
        code, obj = self.run_section(heading="Proposal", write=True,
                                     stdin="## Proposal\n\nA\n\n## Proposal\n\nB\n")
        self.assertEqual(code, 2)
        self.assertEqual(obj["code"], "sp-write-duplicate-heading")
        self.assertEqual(self.state("Proposal"), "absent")

    def test_an_unresolved_heading_inside_a_declared_stream_refuses(self):
        code, obj = self.run_section(heading="Proposal", write=True,
                                     stdin="## Proposal\n\nA\n\n## Nao Canonico\n\nX\n")
        self.assertEqual(code, 2)
        self.assertEqual(obj["code"], "sp-stray-heading")
        self.assertEqual(obj["unresolvedBlocks"], [2])
        self.assertEqual(self.state("Proposal"), "absent")

    def test_scope_refuses_beyond_one_heading(self):
        code, obj = self.run_section(heading="Handoff,Proposal", write=True, scope="global",
                                     stdin="## Handoff\n\nA\n\n## Proposal\n\nB\n")
        self.assertEqual(code, 2)
        self.assertEqual(obj["code"], "sp-scope-not-handoff")

    def test_an_empty_body_still_gets_the_heading_s_guidance(self):
        """The rule the singular form already had, carried into a block of the stream."""
        code, obj = self.run_section(heading="Proposal,Risks", write=True,
                                     stdin="## Proposal\n\nA\n\n## Risks\n")
        self.assertEqual(code, 0, obj)
        self.assertEqual(self.state("Risks"), "empty")


class TheScopedRead(_Workspace):
    """`--scope` on the READ path — the cut `/quenching:specs:execute` step 4 depends on.

    The write side is singular by what it means and takes `## Handoff` alone; the read side
    composes with everything else asked for, because step 4 is ONE call over the whole `build`
    moment and splitting it in two would pay a turn to save tokens."""

    spec_text = HANDOFF_SPEC

    def handoff(self, **kw):
        return self.run_section(heading="Handoff", **kw)[1]["body"]

    def test_current_carries_the_global_block_and_only_the_open_section_s(self):
        self.assertEqual(self.handoff(scope="current"),
                         f"{GLOBAL_BLOCK}\n\n{CURRENT_BLOCK}")

    def test_global_carries_the_evergreen_block_alone(self):
        self.assertEqual(self.handoff(scope="global"), GLOBAL_BLOCK)

    def test_no_scope_still_returns_the_whole_raw_body(self):
        """The regression that matters: an audit read, and every caller written before this,
        must still see the closed section's block."""
        body = self.handoff()
        self.assertIn("### 1. Primeira seção", body)
        self.assertIn("Fechada", body)

    def test_a_plural_read_scopes_handoff_and_returns_its_neighbours_whole(self):
        code, obj = self.run_section(heading="Design,Handoff", scope="current")
        self.assertEqual(code, 0, obj)
        self.assertEqual([s["heading"] for s in obj["sections"]], ["Design", "Handoff"])
        self.assertEqual(obj["sections"][0]["body"].strip(), "O desenho.")
        self.assertEqual(obj["sections"][1]["body"], f"{GLOBAL_BLOCK}\n\n{CURRENT_BLOCK}")

    def test_the_build_moment_is_still_one_call_and_arrives_already_cut(self):
        """What the whole spec is for: step 4 reads the six `build` sections in ONE call and
        the closed section's Handoff block never enters the executor's context."""
        code, obj = self.run_section(moment="build", scope="current")
        self.assertEqual(code, 0, obj)
        bodies = {s["heading"]: s["body"] for s in obj["sections"]}
        self.assertEqual(bodies["Handoff"], f"{GLOBAL_BLOCK}\n\n{CURRENT_BLOCK}")
        self.assertNotIn("### 1. Primeira seção", bodies["Handoff"])
        self.assertIn("A proposta.", bodies["Proposal"])
        self.assertIn("- [x] 1.1 Feita", bodies["Tasks"])

    def test_the_payload_says_the_body_came_cut(self):
        """Mirroring the write's own `scope` key, so a caller knows without comparing sizes."""
        self.assertEqual(self.run_section(heading="Handoff", scope="current")[1]["scope"],
                         "current")
        self.assertIsNone(self.run_section(heading="Handoff")[1]["scope"])

    def test_a_read_without_handoff_among_its_headings_refuses(self):
        code, obj = self.run_section(heading="Design,Proposal", scope="current")
        self.assertEqual(code, 2)
        self.assertEqual(obj["code"], "sp-scope-not-handoff")
        self.assertEqual(obj["declared"], ["Design", "Proposal"])

    def test_no_current_section_degrades_to_the_global_block(self):
        """A spec with no `## Tasks` has nothing to scope to — the same no-op the write side
        already treats as "nothing to target", read as the evergreen block alone."""
        self.write_spec(HANDOFF_SPEC[:HANDOFF_SPEC.index("## Tasks")])
        self.assertEqual(self.handoff(scope="current"), GLOBAL_BLOCK)


if __name__ == "__main__":
    unittest.main()
