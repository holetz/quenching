"""`migrate --to git` — move the specs of a tracker backend onto the `quenching` branch.

Dry run unless `--write`. The whole front is read from the configured tracker backend (every
continuation part included, because `read_spec` reassembles the document), written under the
SAME IDs in ONE commit — open specs in `specs/`, closed ones in `specs/archive/` — and the
specs-axis configuration is copied into the branch's `quenching.json`. The command prints the
change the human applies to `.claude/quenching.json`; it never edits that file.

The check that makes the move trustworthy is an equality, not a promise: after the commit the
`git` store's listing must equal the source's modulo locator, and every difference is reported.
Closed tracker items are never touched (the history stays where it is); `--thin-open-cards`
rewrites only the OPEN ones to the thin card, after the commit has landed.
"""
from __future__ import annotations

import json

from quenching.common.config import load_config as load_envelope, namespace
from quenching.common.frontmatter import parse_frontmatter
from quenching.specs.backends import open_backend
from quenching.specs.backends.base import BackendRefusal
from quenching.specs.backends.git import open_git_backend
from quenching.specs.commands.output import Emitter
from quenching.specs.config import BRANCH_CONFIG_KEYS, CONFIG_FILE, load_config
from quenching.specs.parse import FIELD_KEYS, derive_info
from quenching.specs.parse.fields import set_frontmatter_key
from quenching.specs.parse.records import spec_records
from quenching.specs.parse.tasks import task_progress


# The config the branch gains from the source repository: the specs-axis keys the loader lets
# the branch own, minus the ones that are ABOUT the card or the language and are decided apart.
CARRIED_KEYS = tuple(k for k in BRANCH_CONFIG_KEYS
                     if k not in ("card", "cardAt", "artifactLanguage"))


def reassemble(info: dict) -> str:
    """The canonical document with the fields a tracker stores natively put back into its
    frontmatter. A tracker backend keeps `tags`/`assignee`/`start`/`target` in native fields
    and strips them from the stored text, so the text alone is not the whole spec; the git
    store has no native fields and holds all of it in the one file."""
    text = info["text"]
    held = parse_frontmatter(text)
    for key in FIELD_KEYS:
        value = (info.get("frontmatter") or {}).get(key)
        if value in (None, "", []) or key in held:
            continue
        if isinstance(value, list):
            value = "[" + ", ".join(json.dumps(v, ensure_ascii=False) for v in value) + "]"
        text = set_frontmatter_key(text, key, str(value))
    return text


def comparable(info: dict) -> dict:
    """What `list --json` says about a spec, minus the locator — the equality's unit."""
    checked, blocked, total = task_progress(info["tasks"])
    fm = info["frontmatter"]
    return {"id": info["id"], "phase": info["phase"], "date": info["date"],
            "title": fm.get("title", ""), "stage": info["stage"],
            "outcome": fm.get("outcome") or None, "records": spec_records(fm),
            "tasks": {"checked": checked, "blocked": blocked, "total": total}}


def read_front(backend) -> tuple[list[dict], list[dict]]:
    """`(infos, unreadable)` for the whole front, in listing order."""
    infos, unreadable = [], []
    for row in backend.list_specs():
        info, err = backend.read_spec(row["id"])
        if err or info is None:
            unreadable.append({"id": row["id"], "code": (err or {}).get("code")})
        else:
            infos.append(info)
    return infos, unreadable


def diff_fronts(source: list[dict], target: list[dict]) -> list[dict]:
    """Every difference between two fronts, modulo locator."""
    left = {i["id"]: comparable(i) for i in source}
    right = {i["id"]: comparable(i) for i in target}
    diffs = []
    for spec_id in sorted(set(left) | set(right)):
        if spec_id not in right:
            diffs.append({"id": spec_id, "kind": "missing-in-target"})
        elif spec_id not in left:
            diffs.append({"id": spec_id, "kind": "extra-in-target"})
        elif left[spec_id] != right[spec_id]:
            diffs.append({"id": spec_id, "kind": "differs",
                          "fields": sorted(k for k in left[spec_id]
                                           if left[spec_id][k] != right[spec_id][k])})
    return diffs


def migration_config(source_namespace: dict, held: dict, provider: str) -> dict:
    """The branch's `specs` namespace after the move: what it already holds wins over what
    the source declares, so a re-run never undoes a hand edit on the branch."""
    config = {k: v for k, v in source_namespace.items() if k in CARRIED_KEYS}
    config["card"] = {"provider": provider, "at": "capture"}
    config.update(held)
    return config


def migrate(source, target, source_namespace: dict, *, write: bool,
            thin_cards: bool = False, card_client=None) -> dict:
    """Run (or preview) the move; returns the report `cmd_migrate` prints."""
    from quenching.specs import cards
    infos, unreadable = read_front(source)
    items = [(int(i["id"]), i["phase"], reassemble(i)) for i in infos]
    provider = {"github": "github", "azure-boards": "azure-boards"}.get(source.name, "none")
    config = migration_config(source_namespace, target.read_config(), provider)
    open_ids = [i for i, phase, _ in items if phase == "plans"]
    report = {"ok": True, "from": source.name, "to": "git", "dryRun": not write,
              "count": len(items), "open": len(open_ids),
              "closed": len(items) - len(open_ids), "unreadable": unreadable,
              "ids": [i for i, _, _ in items], "branchConfig": config,
              "configChange": {"file": CONFIG_FILE, "set": {"backend": "git"},
                               "card": config["card"],
                               "note": "the card and the specs-axis keys now live on the "
                                       "branch; remove them from the specs namespace here "
                                       "once the branch is pushed"},
              "thinOpenCards": open_ids if thin_cards else []}
    rebuilt = [derive_info(i, text) for i, (_, _, text) in zip(infos, items)]
    if not write:
        report["diffs"] = diff_fronts(infos, rebuilt)
        report["ok"] = not report["diffs"] and not unreadable
        return report
    report["written"] = target.import_specs(items, config=config)
    after, _ = read_front(target)
    report["diffs"] = diff_fronts(infos, after)
    report["identical"] = all(target.read_spec(i)[0]["text"] == t for i, _, t in items)
    report["ok"] = not report["diffs"] and not unreadable and report["identical"]
    report["cardErrors"] = []
    if thin_cards:
        client = card_client or cards.client_for_backend(source, source_namespace)
        by_id = {i["id"]: i for i in after}
        for spec_id in open_ids:
            try:
                client.update(spec_id, cards.card_state(by_id[spec_id]))
            except BackendRefusal as exc:
                report["cardErrors"].append({"id": spec_id, "message": exc.err.get("message")})
        report["ok"] = report["ok"] and not report["cardErrors"]
    return report


def cmd_migrate(args, root: str, out: Emitter) -> int:
    cfg = load_config(root)
    if not getattr(args, "to", None):
        return out.emit_err(args.json, {
            "code": "sp-local-backend-removed", "exit": 2,
            "backend": cfg.get("provider") or cfg.get("backend"),
            "message": "`cq specs migrate` needs a destination: `--to git` moves the specs of "
                       "a tracker backend onto the `quenching` branch (the removed local "
                       "files backend has no migration)"})
    if cfg.get("backend") == "git":
        return out.emit_err(args.json, {
            "code": "sp-migrate-already-git", "exit": 2,
            "message": "the repository already uses the `git` store; there is no tracker "
                       "front to migrate from"})
    if args.thin_open_cards and not args.write:
        return out.emit_err(args.json, {
            "code": "sp-migrate-thin-needs-write", "exit": 2,
            "message": "--thin-open-cards rewrites tracker items and only runs with --write"})
    source, err = open_backend(root)
    if err:
        return out.emit_err(args.json, err)
    target, err = open_git_backend(root)
    if err:
        return out.emit_err(args.json, err)
    report = migrate(source, target, dict(namespace(load_envelope(root), "specs")),
                     write=args.write, thin_cards=args.thin_open_cards)
    if args.json:
        out.emit(True, report, "")
        return 0 if report["ok"] else 1
    verb = "migrated" if args.write else "dry run — would migrate"
    lines = [f"{verb} {report['count']} specs ({report['open']} open, {report['closed']} "
             f"archived) from {report['from']} to the `quenching` branch"]
    lines += [f"  unreadable: {u['id']} ({u['code']})" for u in report["unreadable"]]
    lines += [f"  diff: {d['id']} {d['kind']} {d.get('fields', '')}" for d in report["diffs"]]
    lines += [f"  card error: {e['id']}: {e['message']}" for e in report.get("cardErrors", [])]
    lines.append("equality: " + ("list --json matches the source modulo locator"
                                 if not report["diffs"]
                                 else f"{len(report['diffs'])} difference(s)"))
    lines.append(f"apply in {CONFIG_FILE}: " + json.dumps(report["configChange"]["set"])
                 + f" (card: {json.dumps(report['configChange']['card'])})")
    if not args.write:
        lines.append("nothing was written — pass --write to commit the batch")
    out.emit(False, report, "\n".join(lines))
    return 0 if report["ok"] else 1
