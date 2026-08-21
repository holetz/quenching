"""The specs pillar's parsing contracts: slugs, config resolution, spec resolution and its
receipt, `## Tasks`/`## Handoff` sectioning.

Migrated from the pre-refactor specs script's `_failures()` suites — `slug_case_failures`,
`base_inference_failures`, `subject_resolution_failures`, `resolution_failures`,
`announcement_failures`, `handoff_block_failures`, `files_parse_failures`,
`handoff_write_failures`. Records and fields live in `test_specs_records.py`;
`canonical_case_failures` lives in `test_frontmatter.py`; `section_case_failures` lives in
`test_sections.py`.
"""
import argparse
import ast
import contextlib
import inspect
import io
import json
import os
import tempfile
import unittest
from unittest import mock

import _paths  # noqa: F401  — must precede the `quenching` import; see its docstring
from quenching.common.text import slugify
from quenching.specs.backends.memory import MemoryBackend
from quenching.specs.commands import read as read_module
from quenching.specs.commands import validate as validate_module
from quenching.specs.commands.cli import DISPATCH, build_parser, main
from quenching.specs.commands.output import Emitter
from quenching.specs.config import infer_base_branch, load_config, resolve_subject
from quenching.specs.parse.derive import derive_info
from quenching.specs.parse.edit import write_handoff_block
from quenching.specs.parse.handoff import current_handoff_section, parse_handoff
from quenching.specs.parse.spec import resolve_one
from quenching.specs.parse.tasks import _files_bad_annotation, parse_tasks
from quenching.specs.parse.text import body_after_frontmatter
from quenching.specs.schema import capture_form


class Slugify(unittest.TestCase):
    """UNICODE IS NORMALISED AND STRIPPED FIRST: without it `[^a-z0-9]+` treats every
    accented letter as a separator, so `criação` becomes `cria-o` instead of `criacao` — an
    identity key that is neither readable nor guessable, in a repo whose harness language is
    pt-BR. These rows are what the identity key of every spec captured in pt-BR runs
    through."""

    CASES = (
        ("Avaliar o fluxo de criação de specs", "avaliar-o-fluxo-de-criacao-de-specs"),
        ("Ação e Manutenção", "acao-e-manutencao"),
        ("Sessão — tokens", "sessao-tokens"),
        ("session tokens", "session-tokens"),
        ("  Trim  --  Me  ", "trim-me"),
        ("JÁ-EM-CAIXA-ALTA", "ja-em-caixa-alta"),
    )

    def test_every_case_folds_to_its_documented_slug(self):
        for given, want in self.CASES:
            with self.subTest(given=given):
                self.assertEqual(slugify(given), want)


class InferBaseBranch(unittest.TestCase):
    """The chain `plan-git-record.md` declares once a spec's own `branch.base` record is
    absent: `origin_head`, then `init_default`, then the literal `main` — the primary
    branch, where an unstamped spec's work belongs. `cfg` is passed for signature stability
    (the callers still hand it in) and has no effect on the chain."""

    CASES = (
        ({}, "origin-main", "init-main", "origin-main"),
        ({}, None, "init-main", "init-main"),
        ({}, None, None, "main"),
    )

    def test_every_case_resolves_to_its_documented_base(self):
        for cfg, origin_head, init_default, want in self.CASES:
            with self.subTest(cfg=cfg, origin_head=origin_head, init_default=init_default):
                self.assertEqual(infer_base_branch(cfg, origin_head, init_default), want)


class LoadConfigFanoutMinComplexity(unittest.TestCase):
    """`fanoutMinComplexity` — the fan-out floor `redefinir-o-que-complexity-mede-e-configurar-o-limiar-do-fan-out`
    adds beside `backend`/`unknownBackend`, same shape: absent or invalid falls back to the
    default (`medium`, today's fixed cutoff) rather than to no floor at all, and an invalid
    declared value is kept, not discarded, so `doctor` can quote it back."""

    def _load(self, declared: dict) -> dict:
        with tempfile.TemporaryDirectory() as tmp:
            os.makedirs(os.path.join(tmp, ".claude"))
            with open(os.path.join(tmp, ".claude", "quenching.json"), "w") as f:
                json.dump(declared, f)
            return load_config(os.path.join(tmp, ".specs"))

    def test_absent_falls_back_to_the_default_floor(self):
        cfg = self._load({})
        self.assertEqual(cfg["fanoutMinComplexity"], "medium")
        self.assertIsNone(cfg["unknownFanoutMinComplexity"])

    def test_a_declared_level_reflects(self):
        cfg = self._load({"fanoutMinComplexity": "low"})
        self.assertEqual(cfg["fanoutMinComplexity"], "low")
        self.assertIsNone(cfg["unknownFanoutMinComplexity"])

    def test_a_value_outside_the_four_levels_keeps_the_default_and_is_quoted_back(self):
        cfg = self._load({"fanoutMinComplexity": "yolo"})
        self.assertEqual(cfg["fanoutMinComplexity"], "medium")
        self.assertEqual(cfg["unknownFanoutMinComplexity"], "yolo")


class ResolveSubject(unittest.TestCase):
    """The two refusals `## Open Decisions` names, and the one non-refusal that keeps
    `subjects` optional for a repository that never declared any."""

    ENGINEERING = {"name": "Engenharia", "description": "d", "tags": ["Vertical: Eng"]}

    CASES = (
        ({"subjects": {}}, None, None, None,
         "no subjects declared, nothing asked, is not a refusal"),
        ({"subjects": {}}, "eng", None, "sp-subject-unknown",
         "an explicit key against nothing declared still refuses"),
        ({"subjects": {"eng": ENGINEERING}}, "eng", ENGINEERING, None,
         "an explicit key that exists resolves it"),
        ({"subjects": {"eng": ENGINEERING}, "azurePlacement": {"defaultSubject": "eng"}},
         None, ENGINEERING, None, "no explicit key falls back to defaultSubject"),
        ({"subjects": {"eng": ENGINEERING}}, None, None, "sp-no-subject",
         "no key and no default refuses"),
        ({"subjects": {"eng": ENGINEERING}}, "ghost", None, "sp-subject-unknown",
         "a declared key that does not exist refuses"),
    )

    def test_every_case_resolves_or_refuses_as_documented(self):
        for cfg, key, want_subject, want_code, label in self.CASES:
            with self.subTest(label=label):
                subject, err = resolve_subject(cfg, key)
                self.assertEqual(subject, want_subject, label)
                self.assertEqual(err.get("code"), want_code, label)


class ResolveOne(unittest.TestCase):
    """The four rungs of `resolve_one`, over a fixed listing — pure over the listing, no
    backend, no store, so "every backend refuses the same way" is a property of this
    function rather than a claim re-tested per target."""

    LISTING = [
        {"phase": "plans", "folder": "plans", "legacy": False,
         "file": "avaliar-o-fluxo-de-criacao-de-specs.md", "path": "x",
         "slug": "avaliar-o-fluxo-de-criacao-de-specs"},
        {"phase": "plans", "folder": "plans", "legacy": False,
         "file": "fechar-vazamentos-do-backend-files.md", "path": "y",
         "slug": "fechar-vazamentos-do-backend-files"},
    ]
    TITLES = {"avaliar-o-fluxo-de-criacao-de-specs":
              "Avaliar o fluxo de criação de specs, sobretudo no backend github",
              "fechar-vazamentos-do-backend-files":
              "Fechar os vazamentos do backend files"}

    def test_the_exact_slug_resolves_and_announces_nothing_because_nothing_was_inferred(self):
        spec, err = resolve_one(self.LISTING, "avaliar-o-fluxo-de-criacao-de-specs", self.TITLES)
        self.assertEqual(err, {})
        self.assertEqual(spec["slug"], "avaliar-o-fluxo-de-criacao-de-specs")
        self.assertIsNone(spec.get("resolvedBy"))

    def test_the_exact_title_folded_for_case_and_accents_resolves_by_title(self):
        # A fragment copied straight out of an issue.
        spec, err = resolve_one(
            self.LISTING,
            "AVALIAR O FLUXO DE CRIACAO DE SPECS, SOBRETUDO NO BACKEND GITHUB",
            self.TITLES)
        self.assertEqual(err, {})
        self.assertEqual(spec["slug"], "avaliar-o-fluxo-de-criacao-de-specs")
        self.assertEqual(spec.get("resolvedBy"), "title")

    def test_a_slug_with_a_typo_resolves_approximately_and_says_so(self):
        spec, err = resolve_one(
            self.LISTING, "avaliar-o-fluxo-de-criacao-de-spec", self.TITLES)
        self.assertEqual(err, {})
        self.assertEqual(spec["slug"], "avaliar-o-fluxo-de-criacao-de-specs")
        self.assertEqual(spec.get("resolvedBy"), "approximate")

    def test_two_specs_sharing_a_slug_refuse_ambiguous_and_name_both(self):
        dup = self.LISTING + [dict(self.LISTING[0], file="outro.md",
                                   phase="archive", folder="archive")]
        spec, err = resolve_one(dup, "avaliar-o-fluxo-de-criacao-de-specs", self.TITLES)
        self.assertIsNone(spec)
        self.assertEqual(err.get("code"), "sp-ambiguous-slug")
        self.assertEqual(err.get("exit"), 2)

    def test_something_genuinely_absent_refuses_rather_than_resolving_to_the_nearest_spec(self):
        # The rung that must NOT fire — this is what FUZZY_MATCH_THRESHOLD is for.
        spec, err = resolve_one(self.LISTING, "algo-completamente-diferente", self.TITLES)
        self.assertIsNone(spec)
        self.assertEqual(err.get("code"), "sp-unknown-slug")
        self.assertEqual(err.get("exit"), 1)


class EmitterReceipt(unittest.TestCase):
    """The receipt of an inexact resolution, carried by `Emitter` instead of the module
    global `_RESOLUTION` the pre-refactor specs script used to reset by hand. `resolved()` is
    the same call
    `read_one` makes, so these exercise the real API rather than a private re-implementation."""

    def test_a_command_that_resolved_no_slug_announces_nothing(self):
        out = Emitter()
        self.assertEqual(out.announced({"ok": True}), {"ok": True})
        self.assertEqual(out.receipt_line(), "")

    def test_an_exact_resolution_carries_both_keys_as_null_but_says_nothing_to_a_human(self):
        out = Emitter()
        out.resolved({"resolvedBy": None, "resolvedFrom": None})
        payload = out.announced({"ok": True})
        self.assertIsNone(payload.get("resolvedBy"))
        self.assertIn("resolvedFrom", payload)
        self.assertEqual(out.receipt_line(), "")

    def test_an_approximate_resolution_reaches_both_the_payload_and_the_human_receipt(self):
        out = Emitter()
        out.resolved({"resolvedBy": "approximate", "resolvedFrom": "o titulo inteiro"})
        payload = out.announced({"ok": True})
        self.assertEqual(payload.get("resolvedBy"), "approximate")
        self.assertEqual(payload.get("resolvedFrom"), "o titulo inteiro")
        human = out.receipt_line()
        self.assertIn("approximate", human)
        self.assertIn("o titulo inteiro", human)


def _resolves_directly(src: str) -> bool:
    """True where a verb's source calls `<backend>.read_spec(args.spec)` itself — the exact
    bypass that would resolve the human's own slug correctly while announcing nothing.
    PARSED, never string-matched, so a remedy sentence naming the call it forbids cannot
    flag itself."""
    return any(
        isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
        and n.func.attr == "read_spec" and n.args
        and isinstance(n.args[0], ast.Attribute) and n.args[0].attr == "spec"
        and isinstance(n.args[0].value, ast.Name) and n.args[0].value.id == "args"
        for n in ast.walk(ast.parse(src)))


def _dispatches_a_fresh_emitter(src: str) -> bool:
    """True where `main` builds its own `Emitter()` and hands that SAME object into the
    `DISPATCH` call — the structural replacement for the old `_RESOLUTION = None` reset: an
    object built here and dropped when `main` returns cannot let one command's receipt ride
    out on the next one's payload, with nothing left for an author to remember."""
    tree = ast.parse(src)
    emitter_names = {
        t.id for n in ast.walk(tree) if isinstance(n, ast.Assign)
        and isinstance(n.value, ast.Call) and isinstance(n.value.func, ast.Name)
        and n.value.func.id == "Emitter"
        for t in n.targets if isinstance(t, ast.Name)
    }
    return any(
        isinstance(n, ast.Call) and isinstance(n.func, ast.Subscript)
        and isinstance(n.func.value, ast.Name) and n.func.value.id == "DISPATCH"
        and n.args and isinstance(n.args[-1], ast.Name) and n.args[-1].id in emitter_names
        for n in ast.walk(tree))


class EveryVerbAnnouncesThroughTheEmitter(unittest.TestCase):
    """The meta-property `announcement_failures` existed to hold: the receipt reaches EVERY
    dispatched verb. Checked against `DISPATCH` — the registry a new verb has to join to
    exist at all — rather than a list of verb names a future verb could be added without
    updating."""

    def test_no_dispatched_verb_bypasses_read_one_for_the_humans_own_slug(self):
        sources = {name: inspect.getsource(fn) for name, fn in DISPATCH.items()}
        for name, src in sorted(sources.items()):
            with self.subTest(verb=name):
                self.assertFalse(_resolves_directly(src),
                                 f"`{name}` calls read_spec(args.spec) directly, bypassing "
                                 f"read_one and the emitter's receipt")

    def test_main_hands_dispatch_a_freshly_built_emitter(self):
        self.assertTrue(_dispatches_a_fresh_emitter(inspect.getsource(main)))


# The canonical case list for the `## Handoff` section-block rule — the pre-refactor specs
# script's own contract, not duplicated in the components or OKF validator scripts.
HANDOFF_BLOCK_FIXTURE = """## Handoff

Global block: still true no matter which section is being built.

### 1. Primeiro grupo

Bloco fechado da seção 1 — não muda mais depois que a última task da seção commitou.

### 2. Segundo grupo

Bloco aberto da seção 2 — é o que uma task desta seção recebe hoje.
"""


class ParseHandoff(unittest.TestCase):
    def test_text_before_the_first_numbered_heading_is_the_global_block(self):
        got = parse_handoff(HANDOFF_BLOCK_FIXTURE)
        self.assertIn("Global block: still true", got["global"])
        self.assertNotIn("Primeiro grupo", got["global"])
        self.assertNotIn("Segundo grupo", got["global"])

    def test_each_numbered_heading_opens_a_block_matched_by_its_own_leading_numeral(self):
        # Never by encounter order and never by title text.
        got = parse_handoff(HANDOFF_BLOCK_FIXTURE)
        blocks = {b["section"]: b["body"] for b in got["blocks"]}
        self.assertIn("Bloco fechado da seção 1", blocks[1])
        self.assertNotIn("Segundo grupo", blocks[1])
        self.assertIn("Bloco aberto da seção 2", blocks[2])
        self.assertNotIn("Primeiro grupo", blocks[2])

    def test_a_section_that_closed_with_no_block_of_its_own_does_not_shift_a_later_number(self):
        # Section 1 has no block at all here; encounter order would mislabel the lone
        # `### 3.` block as section 1.
        text = "## Handoff\n\nGlobal.\n\n### 3. Terceira seção\n\nBloco da seção 3.\n"
        got = parse_handoff(text)
        self.assertIn("Global.", got["global"])
        self.assertEqual([b["section"] for b in got["blocks"]], [3])
        self.assertIn("Bloco da seção 3.", got["blocks"][0]["body"])

    def test_no_numbered_heading_at_all_reads_as_one_global_block_and_no_per_section_blocks(self):
        # Today's flat format — nothing existing needs to migrate.
        text = "## Handoff\n\nTodo o texto de hoje, sem nenhuma sub-seção.\n"
        got = parse_handoff(text)
        self.assertIn("Todo o texto de hoje", got["global"])
        self.assertEqual(got["blocks"], [])

    def test_a_spec_with_no_handoff_heading_at_all_reads_as_empty(self):
        # The ordinary state before a spec's first build.
        got = parse_handoff("## Problem\n\nsomething else\n")
        self.assertEqual(got["global"], "")
        self.assertEqual(got["blocks"], [])


FILES_PARSE_CASES = [
    ("a comma inside parentheses belongs to the same entry — the split that invented "
     "`revertido ao fim)` out of a comment",
     "## Tasks\n\n### 1. X\n\n- [ ] 1.1 t\n      files: a.md (x, y), b.ts (new)\n",
     ["a.md (x, y)", "b.ts (new)"]),
    ("the canonical template example splits at the SEPARATOR commas only",
     "## Tasks\n\n### 1. X\n\n- [ ] 1.1 t\n"
     "      files: src/middleware/auth.ts, src/config/limits.ts (new)\n",
     ["src/middleware/auth.ts", "src/config/limits.ts (new)"]),
    ("the repro of the original defect reads as ONE entry, never two",
     "## Tasks\n\n### 1. X\n\n- [ ] 1.1 t\n"
     "      files: plugins/quenching/commands/zzprobe.md (descartável, revertido ao fim)\n",
     ["plugins/quenching/commands/zzprobe.md (descartável, revertido ao fim)"]),
    ("nested parentheses keep the whole nesting one entry",
     "## Tasks\n\n### 1. X\n\n- [ ] 1.1 t\n      files: x (a (b), c), y\n",
     ["x (a (b), c)", "y"]),
    ("an unbalanced `(` keeps the rest of the line one entry rather than splitting "
     "mid-string",
     "## Tasks\n\n### 1. X\n\n- [ ] 1.1 t\n      files: foo(bar, baz.ts\n",
     ["foo(bar, baz.ts"]),
    ("empty pieces (a trailing comma, a doubled one) are dropped, as before",
     "## Tasks\n\n### 1. X\n\n- [ ] 1.1 t\n      files: a.ts, b.ts,\n",
     ["a.ts", "b.ts"]),
    ("a single plain path is untouched",
     "## Tasks\n\n### 1. X\n\n- [ ] 1.1 t\n      files: src/a.ts\n",
     ["src/a.ts"]),
]

FILES_ANNOTATION_CASES = [
    ("a.md (x, y)", True, "a comma-carrying comment is an annotation, not a path"),
    ("plugins/quenching/commands/zzprobe.md (descartável, revertido ao fim)", True,
     "the original repro's comment is refused whole — never split, never kept as part of "
     "the path"),
    ("src/(old)/x.py", False,
     "parentheses in the MIDDLE of a path are not an annotation — only a trailing "
     "parenthetical is"),
    ("src/a.py (new)", False,
     "`(new)` is the one reserved annotation — the path it names is about to be created"),
    ("c/dir/", False, "a plain path is never an annotation"),
]


class FilesParsing(unittest.TestCase):
    """`files:` reads back entry-for-entry and refuses what it must not interpret. A comma
    inside parentheses must never split a path, and a trailing parenthetical that is not
    `(new)` must never reach an executor as if it were a path — both are the same silence,
    closed at the parse."""

    def test_files_entries_split_on_the_documented_boundary(self):
        for why, text, want in FILES_PARSE_CASES:
            with self.subTest(why=why):
                got = parse_tasks(text)
                files = got[0]["files"] if got else []
                self.assertEqual(files, want, why)

    def test_annotation_refusal_matches_the_reserved_new_marker_exactly(self):
        for entry, want_bad, why in FILES_ANNOTATION_CASES:
            with self.subTest(entry=entry):
                note = _files_bad_annotation(entry)
                self.assertEqual(note is not None, want_bad, why)


HANDOFF_WRITE_FIXTURE = """---
slug: x
title: X
date: 2026-08-04
---

## Tasks

### 1. Primeira seção

- [x] 1.1 feito

### 2. Segunda seção

- [ ] 2.1 aberto
- [ ] 2.2 aberto

### 3. Terceira seção

- [ ] 3.1 aberto
"""


class WriteHandoffBlock(unittest.TestCase):
    """`write_handoff_block` is stateful across a build — each write reads the PRIOR write's
    output — so it is proved as one sequential scenario rather than a table of independent
    inputs, the same shape the pre-refactor specs script proved it in."""

    SPEC = {"slug": "x", "phase": "plans"}

    def test_the_sequential_scenario(self):
        info = derive_info(self.SPEC, HANDOFF_WRITE_FIXTURE)
        text, _ = write_handoff_block(info, "global", "Fato evergreen.")
        info = derive_info(self.SPEC, text)

        # Section 1's one task is already checked, so the first scoped write lands
        # directly on section 2 — proving the write side of the same gap ParseHandoff
        # proves on read.
        self.assertEqual(current_handoff_section(info["tasks"]), 2)

        text, _ = write_handoff_block(info, "current", "Bloco da seção 2, em progresso.")
        info = derive_info(self.SPEC, text)
        parsed = parse_handoff(body_after_frontmatter(text))
        self.assertEqual([b["section"] for b in parsed["blocks"]], [2])
        self.assertIn("2. Segunda seção", parsed["blocks"][0]["title"])

        # A second `current` write updates section 2 in place rather than duplicating it.
        text, _ = write_handoff_block(info, "current", "Bloco da seção 2, atualizado.")
        parsed = parse_handoff(body_after_frontmatter(text))
        self.assertEqual(len(parsed["blocks"]), 1)
        self.assertIn("atualizado", parsed["blocks"][0]["body"])

        # Crossing into section 3 leaves section 2's block frozen.
        info = derive_info(
            self.SPEC,
            text.replace("- [ ] 2.1 aberto", "- [x] 2.1 aberto")
                .replace("- [ ] 2.2 aberto", "- [x] 2.2 aberto"))
        text, _ = write_handoff_block(info, "current", "Bloco da seção 3.")
        parsed = parse_handoff(body_after_frontmatter(text))
        self.assertEqual([b["section"] for b in parsed["blocks"]], [2, 3])


class PhaseCutsListAndValidate(unittest.TestCase):
    """`--phase` on `list` and `validate` narrows the sweep to one phase — the fix for the
    measured session that received 140 rows and 7 foreign findings when it wanted `plans/`
    alone. `getattr(args, "phase", None)` is what lets a caller built before the flag existed
    (no `phase` attribute at all) keep behaving exactly as it always did."""

    def _write(self, root, phase_dir, slug):
        doc = (capture_form().replace("<SLUG>", slug).replace("<TITLE>", slug.title())
               .replace("<DATE>", "2026-01-01").replace("<VERIFICATION>", "per-task"))
        self.backend.create_spec(phase_dir, f"{slug}.md", doc)

    def _workspace(self, root):
        self.backend = MemoryBackend()
        self._write(root, "plans", "alpha")
        self._write(root, "archive", "beta")

    def _dispatch(self, verb, root, args):
        buf = io.StringIO()
        module = read_module if verb == "list" else validate_module
        with mock.patch.object(module, "open_backend", lambda _root: (self.backend, {})), \
                contextlib.redirect_stdout(buf):
            DISPATCH[verb](args, root, Emitter())
        return json.loads(buf.getvalue())

    def test_list_phase_cuts_the_row_count(self):
        with tempfile.TemporaryDirectory() as root:
            self._workspace(root)
            everyone = self._dispatch("list", root, argparse.Namespace(json=True, phase=None))
            plans_only = self._dispatch("list", root,
                                        argparse.Namespace(json=True, phase="plans"))
            self.assertEqual(everyone["count"], 2)
            self.assertEqual(plans_only["count"], 1)
            self.assertEqual(plans_only["specs"][0]["slug"], "alpha")

    def test_validate_phase_excludes_findings_from_the_other_phase(self):
        with tempfile.TemporaryDirectory() as root:
            self._workspace(root)
            everyone = self._dispatch(
                "validate", root, argparse.Namespace(json=True, spec=None, phase=None))
            plans_only = self._dispatch(
                "validate", root, argparse.Namespace(json=True, spec=None, phase="plans"))
            self.assertIn("beta", [f.get("spec") for f in everyone["findings"]])
            self.assertNotIn("beta", [f.get("spec") for f in plans_only["findings"]])
            self.assertIn("alpha", [f.get("spec") for f in plans_only["findings"]])

    def test_a_caller_built_before_the_flag_existed_is_unaffected(self):
        with tempfile.TemporaryDirectory() as root:
            self._workspace(root)
            listed = self._dispatch("list", root, argparse.Namespace(json=True))
            validated = self._dispatch(
                "validate", root, argparse.Namespace(json=True, spec=None))
            self.assertEqual(listed["count"], 2)
            self.assertIn("beta", [f.get("spec") for f in validated["findings"]])


class ListDropsLegacyOverview(unittest.TestCase):
    """Old documents remain readable, but the retired section is not part of the listing API."""

    def test_a_legacy_overview_is_ignored_by_the_json_projection(self):
        with tempfile.TemporaryDirectory() as root:
            backend = MemoryBackend()
            backend.create_spec(
                "plans", "legacy.md",
                "---\nslug: legacy\ntitle: Legacy\ndate: 2026-01-01\n---\n\n"
                "# Legacy\n\n## Overview\n\nTexto antigo.\n\n"
                "## Problem\n\nO problema.\n")
            buf = io.StringIO()
            with mock.patch.object(read_module, "open_backend",
                                   lambda _root: (backend, {})), \
                    contextlib.redirect_stdout(buf):
                DISPATCH["list"](argparse.Namespace(json=True, phase=None), root, Emitter())
            row = json.loads(buf.getvalue())["specs"][0]
            self.assertNotIn("overview", row)
            self.assertEqual(row["summary"], None)
            findings = validate_module.validate_spec(backend, backend.list_specs()[0])
            self.assertNotIn("sp-stray-heading", [f["code"] for f in findings])


class ParserContract(unittest.TestCase):
    """The two surfaces of this pillar's CLI name exactly the same subcommands.

    THE FORM OF A PARTIAL REVERT. `argparse` decides what a human may type and `DISPATCH`
    decides what runs; a subcommand registered in only one of them is a verb that parses and
    dies on a `KeyError`, or a handler nothing can ever reach. The old selftest asserted the
    specific case it had been bitten by (`sp-plans-subcommand-back`) and that assertion is gone
    — a specific case only ever catches the failure that already happened once.

    Read off the parser's own `_actions` rather than off what `build_parser` returns, in the
    mold `test_session.py::ParserContract` uses for the `session` pillar: what argparse
    actually registered is the surface a human meets, and a function free to return something
    else is exactly the drift worth not trusting."""

    def _choices(self) -> dict:
        parser, _sub = build_parser()
        subparsers = [a for a in parser._actions
                      if isinstance(a, argparse._SubParsersAction)]
        self.assertEqual(len(subparsers), 1,
                         "the pillar registers no subparsers action, or more than one — the "
                         "comparison below would measure the wrong surface")
        return subparsers[0].choices

    def test_the_parser_and_dispatch_name_exactly_the_same_subcommands(self):
        choices = self._choices()
        self.assertTrue(choices, "no subcommands registered — the comparison would pass "
                                 "vacuously against an empty DISPATCH")
        self.assertEqual(set(choices), set(DISPATCH))


if __name__ == "__main__":
    unittest.main()
