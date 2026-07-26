#!/usr/bin/env python3
"""skills.py — self-contained deterministic trail for the `.claude/` front.

Payload of the `claude-quenching` plugin, third sibling of `assets/bin/specs.py` and
`assets/hooks/okf-validate.py` and built in the same mold: stdlib-only, ZERO
dependencies (its own minimal frontmatter parser — no PyYAML), one script installed
alone into a target repo.

WHY A THIRD TOOL
----------------
`docs/` has `okf-validate.py`; `specs/` has `specs.py`; the `.claude/` front had a
sentence. Its convergence condition — the registry's GENERATED zone matching
`.claude/skills/` exactly, and every wrapper resolving to a skill — was hand-generated
by an LLM and hand-diffed by the same LLM, and every conformance rule the front
declares (the description cap, the trigger position, the body length, the bijection)
was checked by reading. This script is what the front branches on instead, so the
skills ramify on DATA (an exit code, a `--json` field), never on prose they infer.

Each front's align installs its OWN tool: folding these checks into `specs.py` or
`okf-validate.py` would make one front's align responsible for another front's
verifier — the exact coupling the three-front split exists to prevent.

THE SURFACE
-----------
A **surface root** is the directory that holds the two halves of an automation
surface. Two shapes are conformant and both resolve here:

    <target>/.claude/          # a target repo's local surface
      skills/<skill-name>/SKILL.md
      commands/<front>/[<object>/]<verb>.md

    plugins/<plugin-name>/     # a packaged plugin's surface (this repo's own shape)
      skills/<skill-name>/SKILL.md
      commands/<front>/[<object>/]<verb>.md

A wrapper's path IS its invocation: `commands/specs/plan/propose.md` is
`/specs:plan:propose`, one `:` per path segment. That mapping is mechanical, so the
bijection between skills and wrappers is decidable rather than argued about.

OUTPUT CONTRACT (uniform across every subcommand)
-------------------------------------------------
`--json` on every subcommand, and STRICT exit codes so the skill ramifies on data:
  0  ok
  1  findings (a check found something; a path did not resolve)
  2  refusal  (the tool declines to act — never merely "findings were found")

Findings carry a stable `sk-*` code, exactly as `docs/` reports OKF codes and
`specs/` reports `sp-*`, so the sweep, its conductor, and any status view name the
same defect the same way. ERRORS set the exit code; WARNINGS are reported and do
not — the same split `specs.py doctor` and `validate` already use.

SUBCOMMANDS
  lint [path]     per-skill conformance: the two description caps, trigger position,
                  the `Not for:` boundary, body length, a `**Done when:**` criterion
                  per numbered step, unscoped `Bash`, invocation-control coherence.
                  `path` accepts a SKILL.md, a skill folder, a skills/ directory, or
                  a surface root; it defaults to the resolved surface.
  doctor          the surface's shape: the bijection (orphan skill, dangling or
                  duplicated wrapper), kebab-case names, case-insensitive
                  collisions, and wrappers whose path does not mirror their skill.
                  Every finding carries a `remedy` the sweep applies.
  registry reindex [--registry PATH]
                  regenerate the registry's GENERATED zone from the surface's own
                  SKILL.md frontmatter, preserving every line of curated prose
                  outside the markers. Exits 1 when the repo carries no registry
                  doc or no zone markers — a table is never placed at a guessed
                  anchor inside prose a human wrote.
  budget [--ceiling N]
                  what the surface costs before anything fires: per skill and
                  summed, sorted by cost, against the ceiling. Reports; never
                  refuses.

SURFACE RESOLUTION
  --root PATH, else $SKILLS_ROOT, else walking up from cwd: the first directory
  holding `.claude/skills/` (that `.claude` is the root) or `skills/` (that directory
  is the root). Falls back to `<cwd>/.claude`.

INTERPRETER
  Invoked as `python3 skills.py` or `py skills.py`; on a machine where both resolve to
  a stub, the caller falls back to the real interpreter path and says so in its report
  — the same resolution the `specs/` skills already carry for `specs.py`.
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import re
import sys

VERSION = "1.2.0"  # lockstep with the plugin VERSION file, plugin.json, specs.py, okf-validate.py

SKILL_FILE = "SKILL.md"
SKILLS_DIR = "skills"
COMMANDS_DIR = "commands"
CLAUDE_DIR = ".claude"

FRONTMATTER_FENCE = "---"
# the style decides folding; the chomping indicator and explicit indent are accepted
# and ignored, since a trailing newline never changes a description's character cost
BLOCK_SCALAR_RE = re.compile(r"^([|>])(?:[+-]?)(?:\d*)\s*$")
# a wrapper names its skill in a backticked reference: `plugin:skill-name` or `skill-name`
WRAPPER_SKILL_RE = re.compile(r"`(?:([A-Za-z0-9_.-]+):)?([a-z0-9]+(?:-[a-z0-9]+)*)`")

# conformance thresholds — the normative statement of the front's mechanical rules.
# `doctrine.md` and `taxonomy.md` cite the sk-* codes rather than restating these numbers,
# so the tool and the doctrine cannot drift apart.
#
# Every character count here is taken on the PARSED value, never on the YAML source.
# A description written as a folded `>-` block costs its folded string — the block
# indentation and the newlines are syntax the parser removes before Claude Code ever
# sees the field. Counting the source lines instead inflates a description by roughly
# two characters per line, which is enough to invent a cap violation that the model
# never pays for.
CAP_METADATA = 1536             # description + when_to_use; Claude Code truncates past it
CAP_DESCRIPTION_PORTABLE = 1024  # the Agent Skills standard's hard limit
CAP_BODY_LINES = 500
TRIGGER_SENTENCE_MAX = 2        # triggers live by the second sentence, so truncation keeps them
BOUNDARY_MARKER = "Not for:"
DONE_WHEN_MARKER = "**Done when:**"
UNSCOPED_TOOLS = ("Bash",)      # granting the whole shell for the turn

# The surface-wide always-on ceiling. Set to this plugin's own measured baseline —
# every skill's description + when_to_use plus every wrapper's description, taken on
# parsed values — so the number is one a run produced rather than one somebody picked.
# It is REVISED, never guessed: raise it only from a measurement, and `--ceiling`
# overrides it for a surface with its own budget.
DEFAULT_CEILING = 36503
CHARS_PER_TOKEN = 4             # a rule of thumb for the report, never a tokenizer count

# the registry's derived zone — markers, cells, and location, per the automation mold
REGISTRY_RELPATH = ("docs", "documentation", "reference", "automation.md")
ZONE_BEGIN = "<!-- GENERATED:BEGIN -->"
ZONE_END = "<!-- GENERATED:END -->"
NO_WRAPPER = "—"
EMPTY_CELL = "—"

KEBAB_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
QUOTED_RE = re.compile(r"[\"“]([^\"”]{2,}?)[\"”]")
HEADING_RE = re.compile(r"^#{1,6}\s")
STEP_HEADING_RE = re.compile(r"^#{2,6}\s+\d+[.)]\s")
STEP_ITEM_RE = re.compile(r"^\d+[.)]\s")
WORKFLOW_MARKER_RE = re.compile(r"^(?:\*\*Steps\*\*|#{1,6}\s+(?:Steps|Workflow)\b)", re.IGNORECASE)
DONE_WHEN_RE = re.compile(re.escape(DONE_WHEN_MARKER))


# --------------------------------------------------------------------------- #
# minimal frontmatter parser (deliberately duplicated from specs.py so each
# script stays self-contained — no shared module)
#
# One deliberate extension over specs.py's copy: BLOCK SCALARS (`>`, `>-`, `|`,
# `|-`). Every SKILL.md writes its description as a folded `>-` block, and a
# parser that skipped them would read the field as the literal string ">-" and
# report a 2-character description on every skill in the surface.
# --------------------------------------------------------------------------- #
def parse_frontmatter(text: str) -> dict:
    """Top-level `key: value` pairs of a leading `---` block. Block scalars are folded
    (`>`: lines joined with spaces, blank line = paragraph break) or kept literal
    (`|`), list values are returned as Python lists for inline `[a, b]` and block
    `- item` forms, and scalars as strings with surrounding quotes stripped. Empty
    dict when there is no block."""
    if not text.startswith(FRONTMATTER_FENCE):
        return {}
    lines = text.splitlines()
    if lines[0].strip() != FRONTMATTER_FENCE:
        return {}
    close = None
    for i in range(1, len(lines)):
        if lines[i].strip() == FRONTMATTER_FENCE:
            close = i
            break
    if close is None:
        return {}
    body = lines[1:close]
    fm: dict = {}
    j = 0
    while j < len(body):
        raw = body[j]
        if not raw.strip() or raw.lstrip().startswith("#") or raw[:1] in (" ", "\t"):
            j += 1
            continue
        if ":" not in raw:
            j += 1
            continue
        key, _, val = raw.partition(":")
        key = key.strip()
        val = val.strip()
        block = BLOCK_SCALAR_RE.match(val)
        if block:
            fm[key], j = _read_block_scalar(body, j + 1, block.group(1))
            continue
        val = val.split("#", 1)[0].strip() if "#" in val else val
        if val == "":
            items = []
            k = j + 1
            while k < len(body) and body[k][:1] in (" ", "\t") and body[k].lstrip().startswith("- "):
                items.append(body[k].lstrip()[2:].strip().strip("'\""))
                k += 1
            if items:
                fm[key] = items
                j = k
                continue
            fm[key] = ""
            j += 1
            continue
        if val.startswith("[") and val.endswith("]"):
            inner = val[1:-1].strip()
            fm[key] = [x.strip().strip("'\"") for x in inner.split(",") if x.strip()] if inner else []
        else:
            if len(val) >= 2 and val[0] == val[-1] and val[0] in ("'", '"'):
                val = val[1:-1]
            fm[key] = val
        j += 1
    return fm


def _read_block_scalar(body: list[str], start: int, style: str) -> tuple[str, int]:
    """Consume the indented run at `start` and return (value, index after it).

    `>` folds: consecutive non-empty lines join with a single space and a blank line
    becomes a newline — which is what Claude Code ultimately reads, so a character
    count taken here is the count the model pays for. `|` keeps the newlines."""
    raw: list[str] = []
    j = start
    while j < len(body) and (not body[j].strip() or body[j][:1] in (" ", "\t")):
        raw.append(body[j])
        j += 1
    while raw and not raw[-1].strip():
        raw.pop()
    if not raw:
        return "", j
    indent = min(len(ln) - len(ln.lstrip()) for ln in raw if ln.strip())
    stripped = [ln[indent:] if len(ln) >= indent else ln.lstrip() for ln in raw]
    if style == "|":
        return "\n".join(stripped), j
    out: list[str] = []
    for ln in stripped:
        if not ln.strip():
            out.append("\n")
        elif out and out[-1] != "\n":
            out.append(" " + ln.rstrip())
        else:
            out.append(ln.rstrip())
    return "".join(out).strip(), j


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def read_text(path: str) -> str | None:
    try:
        return pathlib.Path(path).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None


def plural(n: int, noun: str) -> str:
    return f"{n} {noun}" if n == 1 else f"{n} {noun}s"


def rel(path: str, base: str) -> str:
    try:
        return os.path.relpath(path, base).replace(os.sep, "/")
    except ValueError:      # different drives on Windows
        return path.replace(os.sep, "/")


def body_after_frontmatter(text: str) -> str:
    if not text.startswith(FRONTMATTER_FENCE):
        return text
    lines = text.splitlines()
    if lines[0].strip() != FRONTMATTER_FENCE:
        return text
    for i in range(1, len(lines)):
        if lines[i].strip() == FRONTMATTER_FENCE:
            return "\n".join(lines[i + 1:])
    return text


def find_surface_root(root_arg: str | None) -> str:
    """The directory holding `skills/` and `commands/`. `.claude/` wins over a bare
    `skills/` at the same level, so a repo root carrying both a target surface and a
    packaged plugin resolves to the target's."""
    if root_arg:
        return os.path.abspath(root_arg)
    env = os.environ.get("SKILLS_ROOT")
    if env:
        return os.path.abspath(env)
    d = os.path.abspath(os.getcwd())
    while True:
        if os.path.isdir(os.path.join(d, CLAUDE_DIR, SKILLS_DIR)):
            return os.path.join(d, CLAUDE_DIR)
        if os.path.isdir(os.path.join(d, SKILLS_DIR)):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            break
        d = parent
    return os.path.join(os.path.abspath(os.getcwd()), CLAUDE_DIR)


# --------------------------------------------------------------------------- #
# the surface model — what every subcommand reads
# --------------------------------------------------------------------------- #
def discover_skills(skills_dir: str) -> list[dict]:
    """Every `<skills_dir>/<name>/SKILL.md`, sorted by folder name. `name` is the
    FOLDER's name, not the frontmatter's — the folder is what Claude Code loads, and a
    disagreement between the two is itself a finding (`lint`, `sk-name-mismatch`)."""
    if not os.path.isdir(skills_dir):
        return []
    out = []
    for name in sorted(os.listdir(skills_dir)):
        path = os.path.join(skills_dir, name, SKILL_FILE)
        if not os.path.isfile(path):
            continue
        text = read_text(path) or ""
        body = body_after_frontmatter(text)
        out.append({
            "name": name,
            "path": path,
            "frontmatter": parse_frontmatter(text),
            "body": body,
            "bodyLines": len(body.splitlines()),
        })
    return out


def command_invocation(relpath: str) -> str:
    """`specs/plan/propose.md` -> `/specs:plan:propose` — one `:` per path segment."""
    return "/" + ":".join(relpath[:-3].split("/"))


def discover_wrappers(commands_dir: str) -> list[dict]:
    """Every `<commands_dir>/**/*.md`, sorted by invocation. `invokes` is the skill
    name the wrapper's body references, or None when it names none."""
    if not os.path.isdir(commands_dir):
        return []
    out = []
    for dirpath, _dirnames, filenames in os.walk(commands_dir):
        for fn in sorted(filenames):
            if not fn.endswith(".md"):
                continue
            path = os.path.join(dirpath, fn)
            relpath = rel(path, commands_dir)
            text = read_text(path) or ""
            out.append({
                "command": command_invocation(relpath),
                "path": path,
                "relpath": relpath,
                "frontmatter": parse_frontmatter(text),
                "invokes": wrapper_target(body_after_frontmatter(text)),
            })
    return sorted(out, key=lambda w: w["command"])


def wrapper_target(body: str) -> str | None:
    """The skill a wrapper invokes, read from the first backticked reference in its
    body (`plugin:skill-name` or a bare `skill-name`). None when the body names no
    skill at all — a dangling wrapper `doctor` reports rather than guesses at."""
    m = WRAPPER_SKILL_RE.search(body)
    return m.group(2) if m else None


def wrappers_by_skill(surface: dict) -> dict:
    """skill name -> the wrapper that invokes it. First wrapper wins in invocation
    order; a second one claiming the same skill is `doctor`'s sk-duplicate-wrapper,
    not something the derived views silently pick between."""
    out: dict = {}
    for w in surface["wrappers"]:
        if w["invokes"] and w["invokes"] not in out:
            out[w["invokes"]] = w
    return out


def load_surface(root: str) -> dict:
    return {
        "root": root,
        "skillsDir": os.path.join(root, SKILLS_DIR),
        "commandsDir": os.path.join(root, COMMANDS_DIR),
        "skills": discover_skills(os.path.join(root, SKILLS_DIR)),
        "wrappers": discover_wrappers(os.path.join(root, COMMANDS_DIR)),
    }


# --------------------------------------------------------------------------- #
# registration — each subcommand section below declares its own arguments and
# handler, so adding one never edits a table at the far end of the file
# --------------------------------------------------------------------------- #
SUBCOMMANDS: dict = {}   # name -> argument registrar
DISPATCH: dict = {}      # name -> handler(args, root) -> exit code


def register(name: str, add_args, handler) -> None:
    SUBCOMMANDS[name] = add_args
    DISPATCH[name] = handler


def finding(code: str, severity: str, message: str, **extra) -> dict:
    f = {"code": code, "severity": severity, "message": message}
    f.update(extra)
    return f


def exit_for(findings: list[dict]) -> int:
    """Errors are findings the exit code reports; warnings are reported and do not
    fail the run — the same split `specs.py doctor` and `validate` already use, so a
    conductor can gate on an exit code without a severity table of its own."""
    return 1 if any(f["severity"] == "error" for f in findings) else 0


def report_findings(args, header: str, payload: dict, findings: list[dict],
                    label_key: str = "skill") -> int:
    errors = sum(1 for f in findings if f["severity"] == "error")
    if args.json:
        print(json.dumps({"ok": errors == 0, **payload, "findings": findings},
                         indent=2, ensure_ascii=False))
    else:
        print(f"{header} ({errors} error(s), {len(findings) - errors} warning(s))")
        for f in findings:
            print(f"  [{f['severity']:<5}] {f.get(label_key, '-')}: {f['message']}  ({f['code']})")
        if not findings:
            print("  OK — no findings.")
    return exit_for(findings)


# --------------------------------------------------------------------------- #
# lint — the per-skill conformance checks
#
# Every check here is decidable FROM THE FILE. The doctrine's remaining tests —
# the no-op test, sediment, sprawl, positive prescription — stay a human read in
# `quenching-skill-align-and-update` Stage 2, because each needs a claim about
# behaviour that no parser can make. Adding a heuristic for one of them would move
# the plugin's anti-fabrication boundary, not the tool's coverage.
# --------------------------------------------------------------------------- #
def _split_sentences(text: str) -> list[str]:
    return [s for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s]


def _quoted_phrases(text: str) -> list[str]:
    return [m.group(1).strip() for m in QUOTED_RE.finditer(text) if m.group(1).strip()]


def _split_tools(spec: str) -> list[str]:
    """Split `Read, Bash(git add:*, git commit:*), Edit` on top-level commas only — a
    scoped grant may carry commas inside its parentheses."""
    out, depth, cur = [], 0, ""
    for ch in spec:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth = max(0, depth - 1)
        if ch == "," and depth == 0:
            out.append(cur.strip())
            cur = ""
        else:
            cur += ch
    out.append(cur.strip())
    return [t for t in out if t]


def _numbered_steps(body: str) -> list[str]:
    """The workflow's numbered steps: `### N. Title` headings, and top-level `N. …`
    list items once a `**Steps**` / `## Steps` / `## Workflow` marker has opened the
    workflow. Numbered prose lists elsewhere in the body are NOT steps — counting them
    would report a criterion missing from a list that never promised one."""
    steps, in_workflow = [], False
    for line in body.splitlines():
        if STEP_HEADING_RE.match(line):
            steps.append(line.strip())
            in_workflow = False
        elif WORKFLOW_MARKER_RE.match(line):
            in_workflow = True
        elif in_workflow and STEP_ITEM_RE.match(line):
            steps.append(line.strip())
        elif in_workflow and HEADING_RE.match(line):
            in_workflow = False
    return steps


def _step_criteria(body: str) -> tuple[int, int]:
    """(steps, steps carrying a `**Done when:**` criterion). A criterion belongs to the
    step it follows, so the body is walked once and each marker credited to the step
    most recently opened."""
    steps = _numbered_steps(body)
    if not steps:
        return 0, 0
    opened = set(steps)
    covered, current = set(), None
    for line in body.splitlines():
        stripped = line.strip()
        if stripped in opened:
            current = stripped
        elif current and DONE_WHEN_RE.search(line):
            covered.add(current)
    return len(steps), len(covered)


def lint_skill(skill: dict, base: str) -> list[dict]:
    name, fm, body = skill["name"], skill["frontmatter"], skill["body"]
    where = {"skill": name, "path": rel(skill["path"], base)}
    if not fm:
        return [finding("sk-no-frontmatter", "error",
                        "SKILL.md has no YAML frontmatter — Claude Code cannot load it", **where)]
    out: list[dict] = []

    declared = str(fm.get("name", "")).strip()
    if not declared:
        out.append(finding("sk-no-name", "error", "frontmatter has no `name`", **where))
    elif declared != name:
        out.append(finding("sk-name-mismatch", "error",
                           f"frontmatter name `{declared}` differs from the folder `{name}` — "
                           "the folder is what Claude Code loads", **where))

    description = str(fm.get("description", "")).strip()
    when_to_use = str(fm.get("when_to_use", "")).strip()
    if not description:
        out.append(finding("sk-no-description", "error",
                           "no `description` — the skill can never be selected", **where))
        return out

    always_on = len(description) + len(when_to_use)
    if always_on > CAP_METADATA:
        out.append(finding("sk-metadata-cap", "error",
                           f"description + when_to_use is {always_on} characters, over the "
                           f"{CAP_METADATA} cap — Claude Code truncates the tail, which is where "
                           "the `Not for:` boundary lives",
                           characters=always_on, cap=CAP_METADATA, **where))
    if len(description) > CAP_DESCRIPTION_PORTABLE:
        out.append(finding("sk-description-portable", "warn",
                           f"description is {len(description)} characters, over the "
                           f"{CAP_DESCRIPTION_PORTABLE} limit of the Agent Skills standard — the "
                           "skill is not portable outside Claude Code",
                           characters=len(description), cap=CAP_DESCRIPTION_PORTABLE, **where))

    triggers = _quoted_phrases(description)
    if not triggers:
        out.append(finding("sk-trigger-position", "warn",
                           "the description quotes no trigger phrase — no user wording routes to "
                           "this skill", **where))
    elif not _quoted_phrases(" ".join(_split_sentences(description)[:TRIGGER_SENTENCE_MAX])):
        out.append(finding("sk-trigger-position", "warn",
                           f"the first trigger phrase appears after sentence "
                           f"{TRIGGER_SENTENCE_MAX} — a truncated description loses it", **where))
    if BOUNDARY_MARKER not in description:
        out.append(finding("sk-no-boundary", "warn",
                           f"the description states no `{BOUNDARY_MARKER}` boundary — the routing "
                           "story is missing from the only text always in context", **where))

    if skill["bodyLines"] > CAP_BODY_LINES:
        out.append(finding("sk-body-length", "error",
                           f"body is {skill['bodyLines']} lines, over the {CAP_BODY_LINES} cap — "
                           "push shared procedure into references/",
                           lines=skill["bodyLines"], cap=CAP_BODY_LINES, **where))

    steps, covered = _step_criteria(body)
    if steps and covered < steps:
        out.append(finding("sk-step-criterion", "warn",
                           f"{steps - covered} of {steps} numbered steps carry no "
                           f"`{DONE_WHEN_MARKER}` criterion — a step with no observable end state "
                           "can be claimed done early", steps=steps, covered=covered, **where))

    for bare in (t for t in _split_tools(str(fm.get("allowed-tools", ""))) if t in UNSCOPED_TOOLS):
        out.append(finding("sk-unscoped-bash", "warn",
                           f"`{bare}` is granted unscoped — scope it to the commands the workflow "
                           "runs, or state the reason in the body", tool=bare, **where))

    out.extend(_lint_invocation(fm, where))
    return out


def _lint_invocation(fm: dict, where: dict) -> list[dict]:
    """`user-invocable: false` alone is conformant — it is how every skill behind a
    command wrapper hides from the `/` menu. The incoherence worth an error is the
    combination that leaves NO caller: the menu off and the model blocked."""
    out, values = [], {}
    for key in ("user-invocable", "disable-model-invocation"):
        if key not in fm:
            continue
        raw = str(fm[key]).strip().lower()
        if raw in ("true", "false"):
            values[key] = raw == "true"
        else:
            out.append(finding("sk-invocation-value", "warn",
                               f"`{key}: {fm[key]}` is not a boolean — Claude Code reads an "
                               "unparsable value as unset", **where))
    if values.get("user-invocable") is False and values.get("disable-model-invocation") is True:
        out.append(finding("sk-unreachable", "error",
                           "`user-invocable: false` with `disable-model-invocation: true` leaves "
                           "no way to invoke the skill — neither the menu nor the model", **where))
    return out


def resolve_lint_targets(path_arg: str | None, root: str) -> tuple[str, list[dict]]:
    """(base, skills). Accepts a single SKILL.md, one skill folder, a skills/ directory,
    or a surface root — so `lint skills`, `lint .claude`, and
    `lint skills/quenching-docs-add` all mean what they read like."""
    if not path_arg:
        return root, discover_skills(os.path.join(root, SKILLS_DIR))
    target = os.path.abspath(path_arg)
    if os.path.isfile(target):
        target = os.path.dirname(target)
    if os.path.isfile(os.path.join(target, SKILL_FILE)):
        parent = os.path.dirname(target)
        return parent, [s for s in discover_skills(parent) if s["name"] == os.path.basename(target)]
    if os.path.isdir(os.path.join(target, SKILLS_DIR)):
        return target, discover_skills(os.path.join(target, SKILLS_DIR))
    return target, discover_skills(target)


def cmd_lint(args, root: str) -> int:
    base, skills = resolve_lint_targets(args.path, root)
    if not skills:
        return report_findings(args, f"skills lint — {base}", {"root": base, "skillCount": 0},
                               [finding("sk-no-skills", "error",
                                        f"no SKILL.md found under {base}", skill="-")])
    findings: list[dict] = []
    for skill in skills:
        findings.extend(lint_skill(skill, base))
    return report_findings(args, f"skills lint — {base} ({plural(len(skills), 'skill')})",
                           {"root": base, "skillCount": len(skills)}, findings)


register("lint", lambda sp: sp.add_argument(
    "path", nargs="?",
    help="a SKILL.md, a skill folder, a skills/ directory, or a surface root"), cmd_lint)


# --------------------------------------------------------------------------- #
# doctor — the surface's shape: the bijection, names, and mirroring
#
# `lint` judges one skill against the doctrine; `doctor` judges the surface as a
# whole, which is where the front's convergence condition actually lives. Every
# finding carries a `remedy` the sweep applies rather than invents, the same
# contract `specs.py doctor` already gives the specs/ front.
# --------------------------------------------------------------------------- #
def mirrored_name(relpath: str) -> str:
    """`specs/plan/propose.md` -> `specs-plan-propose`: the flattened path a mirrored
    skill's name ends with."""
    return "-".join(relpath[:-3].split("/"))


def cmd_doctor(args, root: str) -> int:
    surface = load_surface(root)
    skills, wrappers = surface["skills"], surface["wrappers"]
    findings: list[dict] = []

    if not os.path.isdir(surface["skillsDir"]):
        findings.append(finding("sk-no-surface", "error",
                                f"no {SKILLS_DIR}/ under {root}", skill="-",
                                remedy="point --root at the surface, or scaffold "
                                       f"{SKILLS_DIR}/ and {COMMANDS_DIR}/"))
        return report_findings(args, f"skills doctor — {root}", {"root": root}, findings)

    by_name = {s["name"]: s for s in skills}
    seen_lower: dict[str, str] = {}
    for skill in skills:
        if not KEBAB_RE.match(skill["name"]):
            findings.append(finding("sk-non-canonical-name", "error",
                                    f"`{skill['name']}` is not kebab-case", skill=skill["name"],
                                    remedy="rename the skill folder to kebab-case, then mirror "
                                           "its wrapper (gate a code-coupled rename on its own)"))
        clash = seen_lower.setdefault(skill["name"].lower(), skill["name"])
        if clash != skill["name"]:
            findings.append(finding("sk-name-collision", "error",
                                    f"`{skill['name']}` collides with `{clash}` on a "
                                    "case-insensitive filesystem", skill=skill["name"],
                                    remedy="rename one of the two skills"))

    claimed: dict[str, list[str]] = {}
    for w in wrappers:
        target = w["invokes"]
        if target is None:
            findings.append(finding("sk-wrapper-no-target", "warn",
                                    f"{w['command']} names no skill in its body", skill="-",
                                    command=w["command"], path=w["relpath"],
                                    remedy="add the `Use the Skill tool to invoke "
                                           "`<skill-name>`` line from the command mold"))
            continue
        if target not in by_name:
            findings.append(finding("sk-dangling-wrapper", "error",
                                    f"{w['command']} invokes `{target}`, which is not a skill "
                                    f"under {SKILLS_DIR}/", skill=target,
                                    command=w["command"], path=w["relpath"],
                                    remedy="create the skill, repoint the wrapper, or delete the "
                                           "wrapper once a human states it is obsolete"))
            continue
        claimed.setdefault(target, []).append(w["command"])
        if not target.endswith(mirrored_name(w["relpath"])):
            findings.append(finding("sk-path-mismatch", "warn",
                                    f"{w['command']} does not mirror `{target}` — a wrapper's path "
                                    "is its skill's flattened name", skill=target,
                                    command=w["command"], path=w["relpath"],
                                    remedy="move the wrapper to the mirrored path, or record the "
                                           "exception in the naming standard"))

    for skill in skills:
        if skill["name"] not in claimed:
            findings.append(finding("sk-orphan-skill", "error",
                                    f"`{skill['name']}` has no command wrapper",
                                    skill=skill["name"],
                                    remedy=f"create a wrapper under {COMMANDS_DIR}/ from the "
                                           "command mold, at the path that flattens to this "
                                           "skill's name (the namespace prefix, if the surface "
                                           "uses one, is not part of the path)"))
        elif len(claimed[skill["name"]]) > 1:
            findings.append(finding("sk-duplicate-wrapper", "error",
                                    f"`{skill['name']}` is invoked by "
                                    f"{', '.join(claimed[skill['name']])}", skill=skill["name"],
                                    remedy="keep the mirrored wrapper and delete the others"))

    payload = {"root": root,
               "bijection": {"skills": len(skills), "wrappers": len(wrappers),
                             "paired": len(claimed), "holds": len(skills) == len(wrappers) == len(claimed)}}
    return report_findings(args, f"skills doctor — {root} "
                                 f"({len(skills)} ↔ {len(wrappers)})", payload, findings)


register("doctor", lambda sp: None, cmd_doctor)


# --------------------------------------------------------------------------- #
# registry reindex — this tool OWNS the GENERATED zone format
#
# Until now `taxonomy.md` described the row format and two skills reproduced it by
# hand, which asked one LLM to both generate a derived table and verify its own
# output. The zone is now derived here, exactly as `specs.py backlog reindex` owns
# the backlog's, and `taxonomy.md` cites this instead of restating it.
# --------------------------------------------------------------------------- #
def registry_rows(surface: dict) -> list[dict]:
    """One row per skill, derived exclusively from the surface's own SKILL.md
    frontmatter plus the wrapper that invokes it. Commands contributed by installed
    plugins are not part of the surface and never reach the zone."""
    wrapper_for = wrappers_by_skill(surface)
    rows = []
    for skill in surface["skills"]:
        w = wrapper_for.get(skill["name"])
        folder = os.path.dirname(w["relpath"]) if w else ""
        triggers = _quoted_phrases(str(skill["frontmatter"].get("description", "")))
        rows.append({
            "command": w["command"] if w else NO_WRAPPER,
            "skill": skill["name"],
            "serves": f"{folder}/" if folder else "generic",
            "trigger": triggers[0] if triggers else "",
        })
    # by Command in byte order, wrapperless rows last and ordered by Skill
    return sorted(rows, key=lambda r: (r["command"] == NO_WRAPPER,
                                       r["skill"] if r["command"] == NO_WRAPPER else r["command"]))


def _cell(value: str) -> str:
    """A pipe inside a trigger phrase would end the cell early."""
    return value.replace("|", "\\|")


def render_registry_zone(rows: list[dict]) -> str:
    lines = ["| Command | Skill | Serves | Typical trigger |", "| --- | --- | --- | --- |"]
    for r in rows:
        trigger = f'"{_cell(r["trigger"])}"' if r["trigger"] else EMPTY_CELL
        lines.append(f"| {_cell(r['command'])} | {r['skill']} | {_cell(r['serves'])} | {trigger} |")
    return "\n".join(lines)


def find_registry(registry_arg: str | None, root: str) -> str | None:
    if registry_arg:
        return os.path.abspath(registry_arg)
    d = root
    while True:
        cand = os.path.join(d, *REGISTRY_RELPATH)
        if os.path.isfile(cand):
            return cand
        parent = os.path.dirname(d)
        if parent == d:
            return None
        d = parent


def cmd_registry(args, root: str) -> int:
    surface = load_surface(root)
    path = find_registry(args.registry, root)
    if path is None or not os.path.isfile(path):
        return report_findings(
            args, f"skills registry — {root}", {"root": root},
            [finding("sk-no-registry", "error",
                     f"no registry at {'/'.join(REGISTRY_RELPATH)} above {root}", skill="-",
                     remedy="install it from assets/templates/automation/registry.md, then rerun")])
    text = read_text(path)
    if text is None:
        return report_findings(args, f"skills registry — {path}", {"root": root},
                               [finding("sk-no-registry", "error",
                                        f"{path} is unreadable", skill="-",
                                        remedy="check the file's encoding and permissions")])
    begin, end = text.find(ZONE_BEGIN), text.find(ZONE_END)
    if begin == -1 or end == -1 or end < begin:
        return report_findings(
            args, f"skills registry — {path}", {"root": root},
            [finding("sk-no-zone", "error",
                     f"the registry carries no `{ZONE_BEGIN}` … `{ZONE_END}` zone", skill="-",
                     remedy="add the markers from assets/templates/automation/registry.md — the "
                            "table is never placed at a guessed anchor inside curated prose")])
    rows = registry_rows(surface)
    new = f"{text[:begin + len(ZONE_BEGIN)]}\n{render_registry_zone(rows)}\n{text[end:]}"
    changed = new != text
    if changed:
        pathlib.Path(path).write_text(new, encoding="utf-8")
    payload = {"ok": True, "path": rel(path, root), "changed": changed, "rows": len(rows)}
    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(f"skills registry — {path}")
        print(f"  {'rewrote' if changed else 'already current —'} "
              f"{plural(len(rows), 'row')} in the GENERATED zone")
    return 0


register("registry",
         lambda sp: (sp.add_argument("registry_cmd", choices=["reindex"]),
                     sp.add_argument("--registry", help="path to the registry doc "
                                                        "(default: nearest "
                                                        f"{'/'.join(REGISTRY_RELPATH)} upward)")),
         cmd_registry)


# --------------------------------------------------------------------------- #
# budget — what the surface costs before a single skill fires
#
# `lint` catches ONE skill over ONE cap. This is the number no per-skill check can
# see: every description and when_to_use, plus every wrapper description, are in
# context on every session whether or not anything fires. It REPORTS and never
# refuses — a surface may legitimately be large, and the decision to cut is the
# human's, so exit 2 is never reached from here.
# --------------------------------------------------------------------------- #
def budget_rows(surface: dict) -> list[dict]:
    """Per skill: its own always-on metadata plus the wrapper description that
    listing the command costs. `argument-hint` is deliberately excluded — it totals
    a few dozen characters across a whole surface and is not carried in the listing."""
    wrapper_for = wrappers_by_skill(surface)
    rows = []
    for skill in surface["skills"]:
        fm = skill["frontmatter"]
        w = wrapper_for.get(skill["name"])
        description = len(str(fm.get("description", "")))
        when_to_use = len(str(fm.get("when_to_use", "")))
        wrapper = len(str(w["frontmatter"].get("description", ""))) if w else 0
        rows.append({"skill": skill["name"], "command": w["command"] if w else NO_WRAPPER,
                     "description": description, "whenToUse": when_to_use, "wrapper": wrapper,
                     "total": description + when_to_use + wrapper})
    return sorted(rows, key=lambda r: (-r["total"], r["skill"]))


def cmd_budget(args, root: str) -> int:
    surface = load_surface(root)
    rows = budget_rows(surface)
    # a wrapper naming no skill, or naming one that is not here, is still listed and
    # still paid for — doctor reports it, and the total must not pretend it is free
    known = {s["name"] for s in surface["skills"]}
    orphan_wrappers = sum(len(str(w["frontmatter"].get("description", "")))
                          for w in surface["wrappers"] if w["invokes"] not in known)
    total = sum(r["total"] for r in rows) + orphan_wrappers
    ceiling = args.ceiling if args.ceiling is not None else DEFAULT_CEILING
    findings = []
    if total > ceiling:
        findings.append(finding("sk-budget-ceiling", "error",
                                f"the surface's always-on metadata is {total} characters, over "
                                f"the {ceiling} ceiling — every session pays it before a skill "
                                "fires", characters=total, ceiling=ceiling, skill="-"))
    payload = {"root": root, "total": total, "ceiling": ceiling,
               "approxTokens": round(total / CHARS_PER_TOKEN),
               "breakdown": {"skills": sum(r["description"] + r["whenToUse"] for r in rows),
                             "wrappers": sum(r["wrapper"] for r in rows) + orphan_wrappers},
               "skills": rows}
    if args.json:
        print(json.dumps({"ok": not findings, **payload, "findings": findings},
                         indent=2, ensure_ascii=False))
        return exit_for(findings)
    print(f"skills budget — {root} ({plural(len(rows), 'skill')})")
    print(f"  {'total':>6}  {'desc':>5} {'wtu':>5} {'wrap':>5}  skill")
    for r in rows:
        print(f"  {r['total']:>6}  {r['description']:>5} {r['whenToUse']:>5} {r['wrapper']:>5}"
              f"  {r['skill']}")
    print(f"\n  {total} characters always on (~{payload['approxTokens']} tokens), "
          f"ceiling {ceiling}")
    for f in findings:
        print(f"  [{f['severity']:<5}] {f['message']}  ({f['code']})")
    return exit_for(findings)


register("budget",
         lambda sp: sp.add_argument("--ceiling", type=int,
                                    help=f"characters the surface may cost (default: "
                                         f"{DEFAULT_CEILING}, this plugin's measured baseline)"),
         cmd_budget)


# --------------------------------------------------------------------------- #
# dispatch
# --------------------------------------------------------------------------- #
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="skills.py",
                                description="deterministic trail for the .claude/ front")
    p.add_argument("--root", help="the surface root holding skills/ and commands/ "
                                  "(default: nearest .claude/ or skills/ upward)")
    sub = p.add_subparsers(dest="cmd", required=True)
    for name, add_args in SUBCOMMANDS.items():
        sp = sub.add_parser(name)
        add_args(sp)
        sp.add_argument("--json", action="store_true", help="machine-readable output")
    return p


def _force_utf8_output() -> None:
    """Skill descriptions are prose — em-dashes, arrows, accented words — and a Windows
    console defaults to cp1252, where printing one raises UnicodeEncodeError AFTER the
    write already landed. That turns a clean report into a traceback and a nonzero exit,
    which the exit-code contract (0 ok / 1 findings / 2 refusal) reads as a finding.
    Encode output as UTF-8 and never let a glyph decide the exit code."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, OSError, ValueError):
            pass


def main(argv: list[str]) -> int:
    _force_utf8_output()
    if "--version" in argv:
        print(f"skills {VERSION}")
        return 0
    args = build_parser().parse_args(argv)
    if not hasattr(args, "json"):
        args.json = False
    return DISPATCH[args.cmd](args, find_surface_root(args.root))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
