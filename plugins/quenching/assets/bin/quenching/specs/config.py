"""Where the workspace is, and what `.claude/quenching.json` declares about it.

Moved verbatim out of the pre-refactor specs script. `AZ_SPEC_TYPE` is imported INSIDE the two
functions that read it: it belongs to `quenching.specs.backends.azure`, which
imports this module at its top, so a module-level edge would close a cycle."""
from __future__ import annotations

import json
import os
import sys

from quenching.common.git import _git
from quenching.common.io import read_text
from quenching.specs.parse.spec import PHASE_DIRS, PHASES


def find_specs_root(root_arg: str | None) -> str:
    if root_arg:
        return os.path.abspath(root_arg)
    env = os.environ.get("SPECS_ROOT")
    if env:
        return os.path.abspath(env)
    cur = os.path.abspath(os.getcwd())
    if os.path.basename(cur) == ".specs":
        return cur
    d = cur
    while True:
        cand = os.path.join(d, ".specs")
        if os.path.isdir(cand):
            return cand
        parent = os.path.dirname(d)
        if parent == d:
            break
        d = parent
    return os.path.join(cur, ".specs")   # default (created by `new`)


def is_root_too_high(root: str) -> bool:
    """True when `root` is the CONTAINER sitting one level above a phased `.specs/` workspace,
    rather than the workspace itself — the mis-levelled `--root`/`SPECS_ROOT` that today reads
    as merely empty. `root` must hold none of `PHASE_DIRS` itself (that is the correctly
    levelled case `_holds_phase_folder` already answers, `specs/worktree.py:190-191`) AND
    `root/.specs` must hold at least one — the same phase-folder idea reused rather than
    reimplemented a third time.

    Only ever true over an EXPLICIT `--root`/`SPECS_ROOT`. The default nearest-upward search in
    `find_specs_root` above stops the moment it finds a directory literally named `.specs`, so
    the root it returns already IS that directory — it can never be the container this predicate
    looks for, by construction, with no extra branch needed to keep the default search exempt."""
    if any(os.path.isdir(os.path.join(root, p)) for p in PHASE_DIRS):
        return False
    nested = os.path.join(root, ".specs")
    return any(os.path.isdir(os.path.join(nested, p)) for p in PHASE_DIRS)


ROOT_TOO_HIGH_REMEDY = "point --root at the .specs/ directory itself"


def root_too_high_message(root: str) -> str:
    """The one message text for `sp-root-too-high`, written here and cited by both call sites
    (`open_backend`'s refusal, `doctor`'s finding) rather than duplicated at each."""
    return (f"'{root}' has no phase folder of its own, but "
            f"'{os.path.join(root, '.specs')}' does — this --root/SPECS_ROOT points at the "
            f"workspace's container, not the workspace itself")


CONFIG_FILE = os.path.join(".claude", "quenching.json")
LEGACY_CONFIG_FILE = "config.json"
CONFIG_KEYS = ("backend", "specsBranch", "worktreeSetup", "azureStates",
               "hooks", "profiles",
               "azurePlacement", "azureColumns", "subjects", "tagCatalog",
               "workItemTypes", "fanoutMinComplexity")
BACKENDS = ("github", "azure-boards")
# Mirrors `schema.py`'s declared `priority.complexity` levels. Redeclared rather than imported —
# `config.py` and `schema.py` do not import each other today, and a four-word tuple does not earn
# that coupling.
DEFAULT_FANOUT_MIN_COMPLEXITY = "medium"
COMPLEXITY_LEVELS = ("low", "medium", "high", "xhigh")
# `azurePlacement`'s recognised sub-keys. Only `areaPath` is required, and its absence is a
# REFUSAL rather than a default — the same argument `azureStates` already carries, applied to
# where a spec is born rather than what state it reads as. `open_azure_backend` is where that
# refusal lives; this tuple only says which sub-keys `load_config` keeps.
AZURE_PLACEMENT_KEYS = ("areaPath", "workItemType", "discoveryTag", "team",
                        "iterationPath", "boardColumn", "defaultSubject", "repository")
# `discoveryTag`'s default. Unlike `areaPath`, this name is the TOOL's, not the project's —
# same argument `specsBranch` already carries — so it defaults rather than refuses;
# configurable only to resolve a collision with a tag the project already uses.
AZ_DEFAULT_DISCOVERY_TAG = "quenching-spec"
DEFAULT_BACKEND = None
DEFAULT_SPECS_BRANCH = "specs"
# Unlike `specsBranch`, these two default to `None` in `load_config`'s own return — never
# to the literal "develop"/"main" below. The base-inference chain
# (`infer_base_branch`) must tell "declared" from "not declared" to know whether it may
# skip `origin/HEAD`; baking the default into `load_config` would erase that distinction
# for every repo that never opted into the develop/main flow. Callers that need an actual
# branch name once a value IS missing — `cq specs release` among them — apply these two
# constants themselves, at the point of use.
DEFAULT_INTEGRATION_BRANCH = "develop"
DEFAULT_RELEASE_BRANCH = "main"
# `azureStates` has NO default, and that is the decision rather than an omission. GitHub's
# open/closed is universal, so `github` needs no such key; an Azure Boards state is defined
# by the project's PROCESS — Basic says To Do/Doing/Done, Agile says New/Active/Resolved/
# Closed, Scrum says New/…/Done/Removed, and a customised process says whatever it likes.
# Guessing would not fail loudly: it would read every archived spec as active in half the
# projects it ran against.

# `hooks` defaults to {} — an absent key declares no events, and that is the normal case.
# The shape is checked at the read: an event must map to a list of hook objects each
# carrying a non-empty string `command`; anything else is left out of the read. One filter
# rides on that shape check — `enabled: false` never leaves here, per extension-points.md —
# and `condition` is carried along untouched, never evaluated by anything in this tool.

# `profiles` has NO default — an absent key declares nothing, which install-profiles.md reads
# as "all three fronts installed", the ordinary case. Like `hooks`, its shape is checked at
# the read (`installed` must be a list of non-empty strings) and its content is never
# interpreted: what a front is, and what the list means, is the standard's, not the loader's.

# The backends that ship without ever having run against a real target. Empty now:
# `azure-boards` was the one name here, and the provar-e-posicionar-o-backend-azure-boards
# plan's §6 ran it end to end against a real Azure DevOps project (org unicredbr, team "Diretoria
# Risco") — `new --subject`, every `section --write`, `record`, `task --check`, `status`,
# `show` and `promote --outcome done`, each compared against `files` for the same state and
# matching, plus the board's own column tracking the de-para through every transition. This
# tuple losing the name is what retires the caveat everywhere at once: the doctor finding
# and the write-time line (`announce_unproved`) both go quiet together.
UNPROVED_BACKENDS = ()

_UNPROVED_ANNOUNCED: set[str] = set()


def announce_unproved(name: str) -> None:
    """One line on stderr, once per process, before an unproved backend's first WRITE.

    THE DECISION IS "WARN, BUT NOT ON EVERY OPERATION". A line per operation is honest and
    becomes a per-call tax on the agent reading this CLI, paid forever for a fact that never
    changes between calls. Silence is not defensible either, because the unproved paths do
    not all fail the same way: a wrong `AZ_SPEC_TYPE` fails LOUDLY — `az` answers with an
    API error and the transport turns it into an exit-2 refusal — but a field that accepts a
    value and silently coerces it to another fails QUIETLY, and a write that fails halfway
    leaves work items behind on somebody's real board. So the line lands on the
    writes, where an unproved path can cost something that does not announce itself, and
    reads — the overwhelming majority of a build loop's calls — stay silent. The permanent,
    zero-noise half of the same answer is `sp-backend-unproved` in `doctor`.

    stderr and never stdout: every caller branches on the `--json` payload, and a warning
    printed into it would break the parse it is trying to inform."""
    if name not in UNPROVED_BACKENDS or name in _UNPROVED_ANNOUNCED:
        return
    _UNPROVED_ANNOUNCED.add(name)
    print(f"warning: backend '{name}' ships without an end-to-end run against a real "
          f"target — its writes have never seen a live response, so this one may fail, or "
          f"half-succeed and leave items behind. `tests/test_specs_backends.py`'s "
          f"`BackendEquivalence` proves the five primitives and their refusals for "
          f"`files`/`memory`; nothing proves this call.", file=sys.stderr)


def find_repo_root(specs_root: str) -> str:
    """The target repo's root — where `.claude/` lives.

    Git's own top level first, because it is the answer that survives being invoked from a
    subdirectory. Falling back to the specs workspace's parent, which is the repo root by
    construction: `/.specs/` sits beside `.claude/`, never below it.

    The git call is skipped outright when `specs_root` does not exist. `_git` falls back to
    running from `.` when its `cwd` is missing, so calling it on a path built to be absent —
    `load_config`'s own selftest fixture — would silently answer with whatever repo this
    process happens to be running from instead of "no git facts here", handing back a real
    `.claude/quenching.json` the fixture exists specifically to avoid."""
    top = _git(specs_root, "rev-parse", "--show-toplevel").strip() if os.path.isdir(specs_root) else ""
    return top or os.path.dirname(os.path.abspath(specs_root))


def _remote_host(remote: str) -> str:
    host = remote.strip().split("#", 1)[0]
    if "://" in host:
        host = host.split("://", 1)[1]
    host = host.rsplit("@", 1)[-1]
    return host.split("/", 1)[0].split(":", 1)[0].lower()


def detect_provider(root: str) -> tuple[str | None, str | None]:
    """Derive the external provider from the repository's origin URL."""
    repo = find_repo_root(root)
    remote = _git(repo, "remote", "get-url", "origin").strip()
    if not remote:
        return None, None
    host = _remote_host(remote)
    if host == "github.com" or host.endswith(".github.com"):
        return "github", host
    if (host == "dev.azure.com" or host.endswith(".dev.azure.com")
            or host == "visualstudio.com" or host.endswith(".visualstudio.com")):
        return "azure-boards", host
    return None, host


def load_config(root: str) -> dict:
    """`.claude/quenching.json` — the plugin's declared parameters, read as data and never
    as a refusal.

    THE FILE MOVED, AND THE MOVE IS THE POINT. It used to be `/.specs/config.json`, at the
    root of the specs workspace, holding one key. Two things broke that home: a repo whose
    backend is external may have no `/.specs/` folder at all, so a config that lives inside
    the workspace cannot say where the workspace is; and the config stopped being the specs
    front's alone. `.claude/` is the one directory every front already shares.

    A leftover `/.specs/config.json` comes back as `legacyPath` rather than being read. Merging
    the two silently would leave a repo with a config that half-works and no way to tell which
    file won; `doctor` names it instead.

    Absent file, absent key, malformed JSON: all yield the defaults, because a repo that
    declares nothing is the normal case and must cost nothing. Every way the file can be
    *wrong* — an unrecognised key, an unrecognised backend, unparseable JSON — comes back as
    a field rather than as a finding, so `doctor` decides what each is worth and every other
    caller is spared the question.

    Whether `worktreeSetup` actually resolves is deliberately NOT answered here: it is judged
    relative to the freshly created worktree, whose path this tool never learns.
    `/quenching:specs:execute`'s inline isolation offer runs it there and reports the exit code."""
    repo = find_repo_root(root)
    path = os.path.join(repo, CONFIG_FILE)
    legacy = os.path.join(root, LEGACY_CONFIG_FILE)
    provider, provider_host = detect_provider(root)
    out = {"path": path, "present": os.path.isfile(path), "unparseable": None,
           "unknownKeys": [], "backend": provider, "provider": provider,
           "unknownProvider": provider_host if provider is None else None,
           "unknownBackend": None,
           "specsBranch": DEFAULT_SPECS_BRANCH, "worktreeSetup": None,
           "azureStates": None, "hooks": {}, "profiles": None,
           "azurePlacement": {}, "azureColumns": {}, "subjects": {}, "tagCatalog": {},
           "workItemTypes": {},
           "fanoutMinComplexity": DEFAULT_FANOUT_MIN_COMPLEXITY, "unknownFanoutMinComplexity": None,
           "legacyPath": legacy if os.path.isfile(legacy) else None}
    if not out["present"]:
        return out
    try:
        obj = json.loads(read_text(path) or "")
    except json.JSONDecodeError as e:
        out["unparseable"] = str(e)
        return out
    if not isinstance(obj, dict):
        out["unparseable"] = f"top level is {type(obj).__name__}, not an object"
        return out
    out["unknownKeys"] = sorted(k for k in obj if k not in CONFIG_KEYS)

    backend = obj.get("backend")
    if isinstance(backend, str) and backend.strip() and backend.strip() not in BACKENDS:
        out["unknownBackend"] = backend.strip()

    branch = obj.get("specsBranch")
    if isinstance(branch, str) and branch.strip():
        out["specsBranch"] = branch.strip()

    val = obj.get("worktreeSetup")
    if isinstance(val, str) and val.strip():
        out["worktreeSetup"] = val.strip()

    fanout_floor = obj.get("fanoutMinComplexity")
    if isinstance(fanout_floor, str) and fanout_floor.strip():
        if fanout_floor.strip() in COMPLEXITY_LEVELS:
            out["fanoutMinComplexity"] = fanout_floor.strip()
        else:
            # Same shape as `unknownBackend` above: the declared value is kept, not discarded,
            # and the effective floor stays at the default rather than at no floor at all.
            out["unknownFanoutMinComplexity"] = fanout_floor.strip()

    # Both phases or neither. A half-declared mapping is worse than none: it would archive a
    # spec into a state the project has and then fail to recognise it on the way back.
    states = obj.get("azureStates")
    if isinstance(states, dict):
        named = {p: str(states.get(p, "")).strip() for p in PHASES}
        if all(named.values()):
            out["azureStates"] = named

    events = obj.get("hooks")
    if isinstance(events, dict):
        parsed: dict[str, list[dict]] = {}
        for event, entries in events.items():
            if not isinstance(entries, list):
                continue
            kept: list[dict] = []
            for hook in entries:
                if not isinstance(hook, dict):
                    continue
                command = hook.get("command")
                if not (isinstance(command, str) and command.strip()):
                    continue
                if hook.get("enabled") is False:
                    # extension-points.md: filtered at the read, never announced.
                    continue
                row: dict = {"command": command.strip()}
                for field, kind in (("optional", bool), ("condition", str), ("prompt", str)):
                    value = hook.get(field)
                    if isinstance(value, kind):
                        row[field] = value
                kept.append(row)
            if kept:
                parsed[event] = kept
        out["hooks"] = parsed

    profiles = obj.get("profiles")
    if isinstance(profiles, dict):
        installed = profiles.get("installed")
        if (isinstance(installed, list)
                and all(isinstance(front, str) and front.strip() for front in installed)):
            out["profiles"] = {"installed": [front.strip() for front in installed]}
    # `azurePlacement` describes the PROJECT, not the backend — `subjects` and `tagCatalog`
    # apply equally to `github`, so they are read here unconditionally, the same as
    # `azurePlacement` and `azureColumns` themselves; a repository on `files` or `github`
    # simply never has anything ask for them. Every sub-key is independently optional at this
    # layer — `areaPath`'s absence is a REFUSAL, but that refusal belongs to
    # `open_azure_backend`, which is the one caller in a position to say no spec was read or
    # written; `load_config` only ever reports.
    placement_raw = obj.get("azurePlacement")
    if isinstance(placement_raw, dict):
        out["azurePlacement"] = {k: placement_raw[k].strip()
                                 for k in AZURE_PLACEMENT_KEYS
                                 if isinstance(placement_raw.get(k), str)
                                 and placement_raw[k].strip()}

    # A board-state → lane de-para, consulted by the backend and never derived by it. Any
    # subset is legal — `boardColumn` in `azurePlacement` is the declared fallback for a
    # state absent from this table, so the table itself carries no all-or-nothing rule.
    columns_raw = obj.get("azureColumns")
    if isinstance(columns_raw, dict):
        out["azureColumns"] = {str(k): v.strip() for k, v in columns_raw.items()
                               if isinstance(k, str) and k.strip()
                               and isinstance(v, str) and v.strip()}

    # One entry per subject a spec may be born under. `name` and `description` are required
    # for an entry to exist at all — a nameless or description-less subject cannot be
    # proposed to a human, which is the whole point of declaring one — `parent` (the Feature
    # id a human already created) and `tags` (fixed tags applied at creation) are optional.
    subjects_raw = obj.get("subjects")
    if isinstance(subjects_raw, dict):
        subjects: dict[str, dict] = {}
        for key, val in subjects_raw.items():
            if not (isinstance(key, str) and key.strip() and isinstance(val, dict)):
                continue
            name = val.get("name")
            description = val.get("description")
            if not (isinstance(name, str) and name.strip()
                    and isinstance(description, str) and description.strip()):
                continue
            entry = {"name": name.strip(), "description": description.strip()}
            parent = val.get("parent")
            if isinstance(parent, int) and not isinstance(parent, bool):
                entry["parent"] = parent
            tags = val.get("tags")
            if isinstance(tags, list):
                entry["tags"] = [t.strip() for t in tags if isinstance(t, str) and t.strip()]
            subjects[key.strip()] = entry
        out["subjects"] = subjects

    # A catalogue of tag → description, read by an agent to PROPOSE a tag at creation time —
    # the description is prompt material, never documentation, which is why an empty one is
    # dropped rather than kept as a nameless tag nobody could ever choose correctly.
    catalog_raw = obj.get("tagCatalog")
    if isinstance(catalog_raw, dict):
        out["tagCatalog"] = {tag.strip(): desc.strip() for tag, desc in catalog_raw.items()
                             if isinstance(tag, str) and tag.strip()
                             and isinstance(desc, str) and desc.strip()}

    # The abstract key a spec's `workItemType:` and `--type` carry — `{description, azure,
    # github, default}`. `description` is prompt material exactly like a `tagCatalog` value,
    # so an entry without one cannot be proposed and is dropped at the read, same as there.
    # `azure`/`github` are each independently optional: an entry may name only one backend
    # without breaking the other. `default` marks the repo's fallback entry.
    types_raw = obj.get("workItemTypes")
    if isinstance(types_raw, dict):
        types: dict[str, dict] = {}
        for key, val in types_raw.items():
            if not (isinstance(key, str) and key.strip() and isinstance(val, dict)):
                continue
            description = val.get("description")
            if not (isinstance(description, str) and description.strip()):
                continue
            entry = {"description": description.strip()}
            for backend_key in ("azure", "github"):
                name = val.get(backend_key)
                if isinstance(name, str) and name.strip():
                    entry[backend_key] = name.strip()
            if val.get("default") is True:
                entry["default"] = True
            types[key.strip()] = entry
        out["workItemTypes"] = types
    return out


def infer_base_branch(cfg: dict, origin_head: str | None, init_default: str | None) -> str:
    """An unstamped spec's `base`, stopping at the first that answers — the chain
    /.knowledge/standards/workflows/plan-git-record.md declares once its own `branch.base`
    record is absent, and the caller's own git facts (`origin_head`, `init_default`)
    already resolved: this function decides only the ORDER, never runs git itself.

    `origin/HEAD` leads: under the PR-on-the-primary flow it resolves to the branch the
    repository publishes to, which is where an unstamped spec's work belongs. `cfg` is
    kept for the callers that pass it; no declared key enters the chain any more."""
    if origin_head:
        return origin_head
    if init_default:
        return init_default
    return "main"


def resolve_subject(cfg: dict, key: str | None) -> tuple[dict | None, dict]:
    """`subjects.<key>` — explicit or `azurePlacement.defaultSubject` — or the refusal
    `## Open Decisions` names for each way it can fail. Generic over every backend: `subjects`
    describes the PROJECT, not `azure-boards` alone (`plugin-configuration.md` §The recognised
    keys), so `github`'s `create_spec` calls this too, for the fixed tags a subject carries
    even where there is no parent to apply them alongside.

    `subjects` undeclared is NOT a refusal WHEN NOTHING WAS ASKED FOR — the feature is simply
    not in use, the same `## Absence is the normal case` every other key in this file gets. An
    EXPLICIT `--subject` still refuses against nothing declared: a human typed a key on
    purpose, and silently ignoring it would build the spec they did not ask for. Declaring
    subjects at all is what makes an unresolved one — explicit or defaulted — a refusal
    instead: a spec born with no resolved subject fails the team's own checklist (no Parent),
    and `## Open Decisions` calls refusing the only honest end."""
    subjects = cfg.get("subjects") or {}
    if key is None and not subjects:
        return None, {}
    resolved_key = key or (cfg.get("azurePlacement") or {}).get("defaultSubject")
    if not resolved_key:
        return None, {
            "code": "sp-no-subject", "exit": 2,
            "message": f"subjects are declared in {CONFIG_FILE} but none resolved — pass "
                       f"`--subject <key>`, or declare `azurePlacement.defaultSubject`; "
                       f"declared: {', '.join(sorted(subjects))}",
        }
    if resolved_key not in subjects:
        return None, {
            "code": "sp-subject-unknown", "exit": 2, "subject": resolved_key,
            "message": f"subject '{resolved_key}' is not declared in {CONFIG_FILE}'s "
                       f"`subjects` — declared: {', '.join(sorted(subjects))}",
        }
    return subjects[resolved_key], {}


def resolve_work_item_type(cfg: dict, frontmatter_type: str | None) -> str:
    """The `azure-boards` create's `--type`, first link that answers: the frontmatter's own
    `workItemType:` key, the catalog's `default` entry, or `AZ_SPEC_TYPE` as the floor. Never
    `azurePlacement.workItemType` — that key is the same fact said worse (§Design), retired
    from this chain and read only by its own aposentada-key finding.

    An entry that exists but names no `azure` type is treated exactly like an unresolved
    key — a repository that only translated a key for `github` still reaches the floor,
    because `azure-boards`'s create REQUIRES a `--type` and has nowhere else to fall."""
    from quenching.specs.backends.azure import AZ_SPEC_TYPE   # deferred: see the module docstring
    types = cfg.get("workItemTypes") or {}
    entry = types.get(frontmatter_type) if frontmatter_type else None
    if entry and entry.get("azure"):
        return entry["azure"]
    for candidate in types.values():
        if candidate.get("default") and candidate.get("azure"):
            return candidate["azure"]
    return AZ_SPEC_TYPE


def resolve_type_key(cfg: dict, key: str | None) -> tuple[str | None, dict]:
    """`--type <key>` against `workItemTypes` — the same two refusals `resolve_subject`
    already carries for `--subject`: an explicit key against an entry the catalog does not
    have, declared or not. Omitted is never a refusal — a spec born with no `workItemType:`
    still resolves one at build time, through `resolve_work_item_type`'s own default/floor
    chain, so there is no `defaultSubject`-shaped fallback to ask for here."""
    types = cfg.get("workItemTypes") or {}
    if key is None:
        return None, {}
    if key not in types:
        return None, {
            "code": "sp-type-unknown", "exit": 2, "type": key,
            "message": f"type '{key}' is not declared in {CONFIG_FILE}'s `workItemTypes`" + (
                f" — declared: {', '.join(sorted(types))}" if types
                else " — nothing is declared there"),
        }
    return key, {}


def azure_workitemtype_retirement(cfg: dict, frontmatter_type: str | None) -> dict | None:
    """`azurePlacement.workItemType` is retired from `resolve_work_item_type`'s chain but
    stays recognised in `AZURE_PLACEMENT_KEYS`, so a repository that declared it gets a
    graduated signal rather than the generic unknown-key finding.

    Declared beside a catalog that already resolves a type, the old key is dead
    configuration — the same fact said better now lives in `workItemTypes`, and ignoring
    the old key changes nothing a create would write. Declared as the only entry that WOULD
    have answered, ignoring it changes the item a create writes, so this refuses instead of
    silently substituting `AZ_SPEC_TYPE` for what a human actually declared."""
    from quenching.specs.backends.azure import AZ_SPEC_TYPE   # deferred: see the module docstring
    old = (cfg.get("azurePlacement") or {}).get("workItemType")
    if not old:
        return None
    resolved = resolve_work_item_type(cfg, frontmatter_type)
    types = cfg.get("workItemTypes") or {}
    entry = types.get(frontmatter_type) if frontmatter_type else None
    answered_by_catalog = bool(entry and entry.get("azure")) or any(
        c.get("default") and c.get("azure") for c in types.values())
    if answered_by_catalog:
        return {
            "code": "sp-az-workitemtype-retired-unused", "severity": "warn", "exit": 0,
            "message": f"{CONFIG_FILE}'s `azurePlacement.workItemType` ('{old}') is retired "
                       f"and unread — `workItemTypes` already resolves '{resolved}' for this "
                       f"create; dead configuration, changing nothing",
        }
    return {
        "code": "sp-az-workitemtype-only-answer", "severity": "error", "exit": 2,
        "message": f"{CONFIG_FILE}'s `azurePlacement.workItemType` ('{old}') is retired and "
                   f"was the only declared answer for this create's type — migrate it into "
                   f"a `workItemTypes` entry (`default: true`, or matching `--type`); "
                   f"writing '{AZ_SPEC_TYPE}' in its place would not be what was declared",
    }
