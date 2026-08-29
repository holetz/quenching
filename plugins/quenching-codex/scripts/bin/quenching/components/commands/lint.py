"""lint — the per-command conformance checks, and the citation form a plugin's prose must use.

Moved verbatim out of the pre-refactor components script.

Every check here is decidable FROM THE FILE. The doctrine's remaining tests — the no-op test,
sediment, sprawl, positive prescription — stay a human read in `quenching-components-align` Stage 2, because
each needs a claim about behaviour that no parser can make. Adding a heuristic for one of them
would move the plugin's anti-fabrication boundary, not the tool's coverage.
"""
from __future__ import annotations

import os
import re

from quenching.common.output import finding, report_findings
from quenching.components.hooks import hook_ladder_findings
from quenching.components.surface import (COMMANDS_DIR, REFERENCES_DIR, SURFACE_MISSING,
                                          _quoted_phrases, discover_commands,
                                          discover_references, plugin_prefix, plural, rel)

# conformance thresholds — the normative statement of the front's mechanical rules.
# `doctrine.md` and `taxonomy.md` cite the sk-* codes rather than restating these numbers,
# so the tool and the doctrine cannot drift apart.
#
# Every character count here is taken on the PARSED value, never on the YAML source.
# A description written as a folded `>-` block costs its folded string — the block
# indentation and the newlines are syntax the parser removes before Codex ever
# sees the field. Counting the source lines instead inflates a description by roughly
# two characters per line, which is enough to invent a cap violation that the model
# never pays for.
CAP_METADATA = 1536             # the description; Codex truncates past it
CAP_DESCRIPTION_PORTABLE = 1024  # the Agent Skills standard's hard limit
CAP_BODY_LINES = 500
TRIGGER_SENTENCE_MAX = 2        # triggers live by the second sentence, so truncation keeps them
BOUNDARY_MARKER = "Not for:"
DONE_WHEN_MARKER = "**Done when:**"
UNSCOPED_TOOLS = ("Bash",)      # granting the whole shell for the turn
EFFORT_VALUES = ("low", "medium", "high", "xhigh", "max")

# A slash citation carrying at least one `:` — `quenching-knowledge-add`,
# `quenching-knowledge-documentation-build`. The lookbehind rejects a citation already
# prefixed by a path or a scheme (`https://`, `../../…`), and requiring a
# segment after the `:` keeps a bare namespace (`quenching-components-`) out: naming the
# namespace is not citing a command.
CITATION_RE = re.compile(r"(?<![\w:/-])/([a-z0-9-]+(?::[a-z0-9-]+)+)")
CITATION_SAMPLE = 3      # examples carried in the message; the count carries the rest

HEADING_RE = re.compile(r"^#{1,6}\s")
STEP_HEADING_RE = re.compile(r"^#{2,6}\s+\d+[.)]\s")
STEP_ITEM_RE = re.compile(r"^\d+[.)]\s")
WORKFLOW_MARKER_RE = re.compile(r"^(?:\*\*Steps\*\*|#{1,6}\s+(?:Steps|Workflow)\b)", re.IGNORECASE)
DONE_WHEN_RE = re.compile(re.escape(DONE_WHEN_MARKER))


def _split_sentences(text: str) -> list[str]:
    return [s for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s]


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


FENCE_RE = re.compile(r"^\s*(```|~~~)")


def unscoped_marker(tool: str) -> str:
    """The one literal line a body writes to price an unscoped grant, for `tool`.

    Parameterised by the name rather than written out, so the marker cannot drift from
    `UNSCOPED_TOOLS`: adding a second unscoped tool gets its marker for free."""
    return f"**Why `{tool}` is unrestricted here.**"


def marker_present(body: str, tool: str) -> bool:
    """Does the body carry `tool`'s marker as a line of its own, outside a fence?

    A BOOLEAN, and deliberately nothing more. It does not read the reason, judge whether it
    is good, or count how long it is — the finding stays reported either way, and what the
    marker buys is a reader who can tell a deliberate grant from an unexamined one.

    The fence state is why this is a walk rather than a `in body` test: a body that QUOTES
    the marker inside a fenced example — this repo's own moulds do exactly that — would
    otherwise price itself by showing what pricing looks like."""
    marker, fenced = unscoped_marker(tool), False
    for line in body.splitlines():
        if FENCE_RE.match(line):
            fenced = not fenced
            continue
        if not fenced and line.strip().startswith(marker):
            return True
    return False


SKILL_TOOL_RE = re.compile(r"[*`_]*Skill[*`_]*\s+tool", re.I)
SKILL_TOOL_WINDOW = 1           # lines either side of the name, so a wrapped sentence counts

# The shape of a command's registry path, `specs:develop` or a one-segment `align` — the
# same generic-form-then-membership pattern CITATION_RE above uses, and for the same
# reason: one regex over each body, never one regex per target name repeated for every
# caller. `*` rather than `+` because the path IS the identity and a command sitting at
# the root of `commands/` has exactly one segment.
NAME_SHAPE = r"([a-z0-9-]+(?::[a-z0-9-]+)*)"


def named_by_bodies(commands: list[dict], prefix: str) -> dict[str, set[str]]:
    """Which commands another command's BODY reaches BY NAME — derived from disk, never
    from a hand-kept list, so a mass rename moves the paths and the check still holds.

    Frontmatter is not read. A `Not for: X -> /other` boundary names a neighbour it is
    steering AWAY from, and counting it would put most of the surface in this set.

    Two conventions are in use, and only the first is unambiguous on its own:

      A. the BARE registry form, `prefix:docs:align` — what you actually hand the Skill
         tool. The same name written `/prefix:docs:align` is a human-facing citation, so
         a leading slash disqualifies it;
      B. any form of the name on a line whose neighbourhood says "Skill tool" — which is
         how a body that writes "chain into `quenching-specs-conclude` (the `Skill` tool)"
         says the same thing.

    The union is deliberately the WIDER read. The two errors are not symmetric: a false
    positive costs a command its place in the typed-only class, which is an argument; a
    false negative lets a real conductor stage be flagged typed-only and go silently
    inert, which is the failure this check exists to prevent.

    Each body is read ONCE, for names of the generic shape, and every name found is decided
    by membership in the surface's own set — never one regex per target name re-run for
    every caller, which cost the square of the surface's size."""
    by_name = {c["command"].lstrip("/"): c["command"] for c in commands}
    esc = re.escape(prefix)
    registry_re = re.compile(rf"(?<![\w:/-]){esc}:{NAME_SHAPE}(?![\w:-])")
    adjacent_re = re.compile(rf"(?<![\w:-])/?({esc}:)?{NAME_SHAPE}(?![\w:-])")

    out: dict[str, set[str]] = {}
    for caller in commands:
        lines = caller["body"].splitlines()
        skill_lines = [i for i, _ in enumerate(lines)
                       if SKILL_TOOL_RE.search("\n".join(
                           lines[max(0, i - SKILL_TOOL_WINDOW): i + SKILL_TOOL_WINDOW + 1]))]
        found = {m.group(1) for m in registry_re.finditer(caller["body"])}
        for i in skill_lines:
            for m in adjacent_re.finditer(lines[i]):
                # Both readings of the optional prefix the adjacent form allows: `foo:bar`
                # is the command `bar` reached through plugin `foo`, and is also the name
                # of a command `foo:bar` on a surface whose own tree starts with `foo/`.
                found.add(m.group(2))
                if m.group(1):
                    found.add(m.group(1) + m.group(2))
        found.discard(caller["command"].lstrip("/"))
        for cand in found:
            if cand in by_name:
                out.setdefault(by_name[cand], set()).add(caller["command"])
    return out


def description_is_resident(fm: dict) -> bool:
    """Is this command's `description` in every session's context?

    THE one place that answers it. `lint` scopes its two routing codes by it, so
    the routing codes and residency can never disagree about the same surface — two
    copies of this condition is the shape that diverges in silence.

    `disable-model-invocation: true` is the only field that makes the answer no.
    Measured, not assumed: Codex drops the description from the listing AND
    refuses the command by name through the Skill tool — row 7 of
    `/docs/external/tools/claude-code-skill-command-mechanics.md`, Codex 2.1.220.
    The description is still read by a human, in the file and in the `/` menu; it is
    residency it loses, never content."""
    return str(fm.get("disable-model-invocation", "")).strip().lower() != "true"


def lint_command(cmd: dict, base: str, named_by: set[str] | None = None) -> list[dict]:
    """`named_by` is the set of commands whose bodies reach THIS one by name. It is a
    property of the whole surface, so only a caller holding one can supply it — and a
    surface with no plugin manifest has no registry form to be reached by, which is why
    `None` (the check does not apply) is a legitimate state rather than a skipped one."""
    fm, body = cmd["frontmatter"], cmd["body"]
    where = {"command": cmd["command"], "path": rel(cmd["path"], base)}
    if not fm:
        return [finding("sk-no-frontmatter", "error",
                        "the command file has no YAML frontmatter — Codex cannot load it",
                        **where)]
    out: list[dict] = []

    # BEFORE any content check, so a parse failure is never presented as a content
    # gap. A `description` truncated at a `#` used to surface as `sk-no-description`,
    # which names a missing part rather than the truncation that removed it.
    for a in cmd.get("anomalies", []):
        out.append(finding("sk-frontmatter-unparsed", "warn",
                           f"`{a['key']}`: {a['detail']}", kind=a["kind"], key=a["key"], **where))

    # `name` is not checked: the command's path IS its name, so there is no second
    # spelling that could disagree with it. `sk-no-name` and `sk-name-mismatch` are
    # deleted with the pair rather than reinterpreted.
    description = str(fm.get("description", "")).strip()
    if not description:
        out.append(finding("sk-no-description", "error",
                           "no `description` — the command can never be selected", **where))
        return out

    # one file, one description — `when_to_use` went with the skill half
    always_on = len(description)
    if always_on > CAP_METADATA:
        out.append(finding("sk-metadata-cap", "error",
                           f"description is {always_on} characters, over the "
                           f"{CAP_METADATA} cap — Codex truncates the tail, which is where "
                           "the `Not for:` boundary lives",
                           characters=always_on, cap=CAP_METADATA, **where))
    if len(description) > CAP_DESCRIPTION_PORTABLE:
        out.append(finding("sk-description-portable", "warn",
                           f"description is {len(description)} characters, over the "
                           f"{CAP_DESCRIPTION_PORTABLE} limit of the Agent Skills standard — the "
                           "command is not portable outside Codex",
                           characters=len(description), cap=CAP_DESCRIPTION_PORTABLE, **where))

    # Both codes below judge ROUTING FROM PROSE, so both are scoped to a description
    # that is actually in context. For a typed-only command there is no listing for a
    # trigger phrase to sit in and no neighbour for a boundary to discriminate against
    # — the human reaches it by typing the name. Reporting it as badly written for a
    # routing that cannot happen is `lint` penalizing a description nothing routes from.
    if description_is_resident(fm):
        triggers = _quoted_phrases(description)
        if not triggers:
            out.append(finding("sk-trigger-position", "warn",
                               "the description quotes no trigger phrase — no user wording routes "
                               "to this command", **where))
        elif not _quoted_phrases(" ".join(_split_sentences(description)[:TRIGGER_SENTENCE_MAX])):
            out.append(finding("sk-trigger-position", "warn",
                               f"the first trigger phrase appears after sentence "
                               f"{TRIGGER_SENTENCE_MAX} — a truncated description loses it",
                               **where))
        if BOUNDARY_MARKER not in description:
            out.append(finding("sk-no-boundary", "warn",
                               f"the description states no `{BOUNDARY_MARKER}` boundary — the "
                               "routing story is missing from the only text always in context",
                               **where))

    if cmd["bodyLines"] > CAP_BODY_LINES:
        out.append(finding("sk-body-length", "error",
                           f"body is {cmd['bodyLines']} lines, over the {CAP_BODY_LINES} cap — "
                           "push shared procedure into a bundled reference and cite it by "
                           "absolute path",
                           lines=cmd["bodyLines"], cap=CAP_BODY_LINES, **where))

    steps, covered = _step_criteria(body)
    if steps and covered < steps:
        out.append(finding("sk-step-criterion", "warn",
                           f"{steps - covered} of {steps} numbered steps carry no "
                           f"`{DONE_WHEN_MARKER}` criterion — a step with no observable end state "
                           "can be claimed done early", steps=steps, covered=covered, **where))

    # BOTH cases are reported, and that is the point: the grant is still the whole shell for
    # the turn either way. What the marker changes is the REMEDY — the unpriced message asks
    # for something the reader can do, instead of pointing at a body this check never read.
    for bare in (t for t in _split_tools(str(fm.get("allowed-tools", ""))) if t in UNSCOPED_TOOLS):
        priced = marker_present(body, bare)
        message = (f"`{bare}` is granted unscoped and the body prices it — the grant is still "
                   "the whole shell for the turn" if priced else
                   f"`{bare}` is granted unscoped — scope it to the commands the workflow runs, "
                   f"or open a line with `{unscoped_marker(bare)}` and state the reason there")
        out.append(finding("sk-unscoped-bash", "warn", message,
                           tool=bare, priced=priced, **where))

    out.extend(_lint_invocation(fm, where, named_by))
    out.extend(_lint_frontmatter_hooks(cmd, where))
    out.extend(_lint_profile(fm, where))
    return out


def _lint_profile(fm: dict, where: dict) -> list[dict]:
    """The execution profile's mechanically decidable slice. `context: fork` runs the
    command in a forked context that CANNOT present a mid-flow question, so a fork beside
    an `AskUserQuestion` grant is incoherent by construction — the one profile combination
    that is an error rather than a judgment. Unparseable `context`/`effort` values are
    warned: Codex reads them as unset, so the command silently runs without the
    profile its author thought it had."""
    out: list[dict] = []
    context = str(fm.get("context", "")).strip().lower()
    if context and context != "fork":
        out.append(finding("sk-profile-value", "warn",
                           f"`context: {fm['context']}` is not a value Codex reads — "
                           "the only supported value is `fork`", **where))
    effort = str(fm.get("effort", "")).strip().lower()
    if effort and effort not in EFFORT_VALUES:
        out.append(finding("sk-profile-value", "warn",
                           f"`effort: {fm['effort']}` is not one of "
                           f"{'/'.join(EFFORT_VALUES)} — Codex reads it as unset",
                           **where))
    if context == "fork":
        tools = _split_tools(str(fm.get("allowed-tools", "")))
        if any(t == "AskUserQuestion" or t.startswith("AskUserQuestion(") for t in tools):
            out.append(finding("sk-fork-gate", "error",
                               "`context: fork` beside an `AskUserQuestion` grant — a forked "
                               "context cannot present a mid-flow question, so one of the two "
                               "is a lie", **where))
    return out


def _lint_invocation(fm: dict, where: dict, named_by: set[str] | None = None) -> list[dict]:
    """Both keys are optional and default invocation is the norm — a collapsed command
    is typable at `/` AND reachable by name, which is what lets a conductor invoke a
    stage. The incoherence worth an error is the combination that leaves NO caller:
    the menu off and the model blocked.

    The second incoherence is narrower and was invisible until it was measured: a
    command another body reaches BY NAME cannot also be typed-only, because the Skill
    tool refuses it (row 7 of the mechanics reference). Nothing else on this surface
    catches it — `doctor` still counts it as present, and the conductor does not
    fail, it simply does nothing."""
    out, values = [], {}
    for key in ("user-invocable", "disable-model-invocation"):
        if key not in fm:
            continue
        raw = str(fm[key]).strip().lower()
        if raw in ("true", "false"):
            values[key] = raw == "true"
        else:
            out.append(finding("sk-invocation-value", "warn",
                               f"`{key}: {fm[key]}` is not a boolean — Codex reads an "
                               "unparsable value as unset", **where))
    if values.get("user-invocable") is False and values.get("disable-model-invocation") is True:
        out.append(finding("sk-unreachable", "error",
                           "`user-invocable: false` with `disable-model-invocation: true` leaves "
                           "no way to invoke the command — neither the menu nor the model",
                           **where))
    if values.get("disable-model-invocation") is True and named_by:
        callers = ", ".join(sorted(named_by))
        out.append(finding("sk-inert-stage", "error",
                           f"`disable-model-invocation: true` on a command reached by name from "
                           f"{callers} — the Skill tool refuses the call, so that body runs and "
                           "this stage silently does nothing",
                           namedBy=sorted(named_by), **where))

    return out


def _lint_frontmatter_hooks(cmd: dict, where: dict) -> list[dict]:
    """The scope ladder's narrowest rung. A frontmatter hook fires only while this command
    runs, which is why it is the default rung — but "narrow" is about SCOPE, not about cost:
    an unmatched matcher here still taxes every tool call the command makes, so the same two
    ladder codes apply, from the same implementation `settings.json` uses."""
    out: list[dict] = []
    if not cmd.get("hooksParsed", True):
        out.append(finding("sk-hook-unparseable", "warn",
                           "the frontmatter `hooks:` block does not match the mold's shape, so "
                           "the ladder checks could not read it — it is NOT reported as clean",
                           **where,
                           remedy="rewrite it in the shape of "
                                  "assets/templates/automation/hook.md shape 1 (quenching-components-hook-new)"))
    out.extend(hook_ladder_findings(cmd.get("hooks") or {},
                                    where_in=f"{where['path']} frontmatter", where=where))
    return out


def bare_citations(body: str, invocations: set[str]) -> list[str]:
    """The bare `/front:verb` citations in `body` that name a command of THIS surface, in
    order of appearance and without repeats.

    `body` is the text after the frontmatter, so a citation inside `description:` cannot
    reach here — the boundary is the parse, never a pattern that has to be kept in step
    with one."""
    seen: list[str] = []
    for m in CITATION_RE.finditer(body):
        cite = "/" + m.group(1)
        if cite in invocations and cite not in seen:
            seen.append(cite)
    return seen


def lint_citations(prefix: str, body: str, invocations: set[str], where: dict) -> list[dict]:
    """One finding per file, never one per citation: a surface mid-sweep carries hundreds,
    and a report nobody can read is a report nobody acts on."""
    bare = bare_citations(body, invocations)
    if not bare:
        return []
    shown = ", ".join(f"`{c}`" for c in bare[:CITATION_SAMPLE])
    more = f" (+{len(bare) - CITATION_SAMPLE} more)" if len(bare) > CITATION_SAMPLE else ""
    return [finding("sk-bare-citation", "warn",
                    f"{plural(len(bare), 'bare command citation')} in the body — {shown}{more}. "
                    f"These commands come from the `{prefix}` plugin, so the form that resolves "
                    f"is `{prefix}:<front>:<verb>` for the Skill tool and "
                    f"`/{prefix}:<front>:<verb>` for a human; the bare form resolves only where "
                    "the command file lives in the target repo's own .agents/skills/",
                    citations=bare, **where)]


def resolve_lint_targets(path_arg: str | None, root: str) -> tuple[str, list[dict], list[dict]]:
    """(base, commands, references). Accepts a single command file, a commands/ directory,
    or a surface root — so `lint commands`, `lint .claude`, and `lint commands/docs/add.md`
    all mean what they read like.

    The references ride along only when the base IS a surface root: linting one file, or a
    bare `commands/` directory, is a scope the caller named and this never widens it."""
    if not path_arg:
        return (root, discover_commands(os.path.join(root, COMMANDS_DIR)),
                discover_references(os.path.join(root, REFERENCES_DIR)))
    target = os.path.abspath(path_arg)
    if os.path.isfile(target):
        parent = os.path.dirname(target)
        return parent, [c for c in discover_commands(parent)
                        if os.path.abspath(c["path"]) == target], []
    if os.path.isdir(os.path.join(target, COMMANDS_DIR)):
        return (target, discover_commands(os.path.join(target, COMMANDS_DIR)),
                discover_references(os.path.join(target, REFERENCES_DIR)))
    return target, discover_commands(target), []


def cmd_lint(args, root: str) -> int:
    base, commands, references = resolve_lint_targets(args.path, root)
    if not commands:
        return report_findings(args.json, f"skills lint — {base}",
                               {"root": base, "commandCount": 0},
                               [finding("sk-no-commands", "error",
                                        f"no command file found under {base}",
                                        command=SURFACE_MISSING)], "skill")
    prefix = plugin_prefix(root)
    # Same surface-versus-scope rule as the citations below, and for the same reason: the
    # body that names a stage is usually NOT the file being linted, so deriving this from
    # `commands` would make `lint <one file>` blind to the conductor that reaches it.
    surface_commands = (commands if base == root
                        else discover_commands(os.path.join(root, COMMANDS_DIR)))
    named_by = named_by_bodies(surface_commands, prefix) if prefix else {}

    findings: list[dict] = []
    for cmd in commands:
        findings.extend(lint_command(cmd, base,
                                     named_by.get(cmd["command"]) if prefix else None))

    if prefix:
        invocations = {c["command"] for c in surface_commands}
        for cmd in commands:
            findings.extend(lint_citations(prefix, cmd["body"], invocations,
                                           {"command": cmd["command"],
                                            "path": rel(cmd["path"], base)}))
        for ref in references:
            findings.extend(lint_citations(prefix, ref["body"], invocations,
                                           {"command": SURFACE_MISSING,
                                            "path": rel(ref["path"], base)}))

    header = f"skills lint — {base} ({plural(len(commands), 'command')}"
    header += f", {plural(len(references), 'reference')})" if references else ")"
    return report_findings(args.json, header,
                           {"root": base, "commandCount": len(commands),
                            "referenceCount": len(references)}, findings, "skill")
