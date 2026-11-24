"""`cq specs claim acquire|renew|release|take|list` — a build's reservation of a spec on the
`origin`, compared and swapped by the server (`quenching.specs.claims`).

Exit 0 ok · 1 held by another machine, or the compare-and-swap lost · 2 refusal (a bad id, git
could not answer).
"""
from __future__ import annotations

from quenching.specs import claims
from quenching.specs.commands.output import Emitter


def _terminal(root: str, ids: list[str]) -> dict[str, bool]:
    """`{id: terminal}`: archived, or carrying an `outcome` or `merge` record. A backend that does
    not open, or an id it does not resolve, reads as not terminal."""
    if not ids:
        return {}
    try:
        from quenching.specs.backends import open_backend
        backend, err = open_backend(root)
        infos = {} if err else backend.read_specs(ids)
    except Exception:  # noqa: BLE001 — the lease stays authoritative when the store cannot answer
        infos = {}
    out = {}
    for i in ids:
        info = infos.get(str(i)) or {}
        front = info.get("frontmatter") or {}
        out[str(i)] = info.get("phase") == "archive" or bool(front.get("outcome")) \
            or bool(front.get("merge"))
    return out


def _line(v: dict) -> str:
    state = "terminal" if v["terminal"] else "expired" if v["expired"] else "live"
    label = f" ({v['label']})" if v.get("label") else ""
    mine = " · mine" if v["mine"] else ""
    return f"{v['spec']}: {v['holder']}{label} · {state} · expires {v['expires']}{mine}"


def cmd_claim(args, root: str, out: Emitter) -> int:
    action = args.claim_action
    try:
        store = claims.Store(root, args.remote)
        me = claims.holder_of(claims.machine_id(root), claims.session_id(args.session))
        if action == "list":
            return _list(args, root, store, me, out)
        spec_id = str(args.claim_id or "")
        if not claims.valid_id(spec_id):
            return out.emit_err(args.json, {"code": "sp-claim-id", "exit": 2,
                                            "message": f"not a spec id: {spec_id!r}"})
        return _change(args, root, store, me, spec_id, out)
    except claims.ClaimError as e:
        return out.emit_err(args.json, {"code": "sp-claim-git", "exit": 2, "message": str(e)})


def _list(args, root, store, me, out) -> int:
    found = store.read_all()
    at = claims.now()
    terminal = _terminal(root, sorted(found))
    rows = [claims.view({**lease, "spec": i}, me, at, terminal.get(i, False))
            for i, (_, lease) in sorted(found.items())]
    payload = {"ok": True, "action": "list", "scope": store.scope, "holder": me, "claims": rows}
    out.emit(args.json, payload, "\n".join(_line(r) for r in rows) or "no claims")
    return 0


def _change(args, root, store, me, spec_id, out) -> int:
    action = args.claim_action
    at = claims.now()
    sha, lease = store.read(spec_id)
    terminal = _terminal(root, [spec_id]).get(spec_id, False) if sha else False
    current = claims.view(lease, me, at, terminal) if sha else None
    base = {"action": action, "spec": spec_id, "scope": store.scope, "holder": me}

    def held(reason: str, lease_view: dict | None) -> int:
        payload = {"ok": False, **base, "reason": reason, "heldBy": lease_view}
        who = lease_view["holder"] if lease_view else "nobody"
        out.emit(args.json, payload, f"{spec_id}: {reason} — held by {who}")
        return 1

    if action == "release":
        if sha is None:
            out.emit(args.json, {"ok": True, **base, "released": False, "reason": "absent"},
                     f"{spec_id}: no claim to release")
            return 0
        if not current["mine"]:
            return held("not-holder", current)
        if not store.swap(spec_id, None, sha):
            return held("lost", _reread(store, spec_id, me, root))
        out.emit(args.json, {"ok": True, **base, "released": True}, f"{spec_id}: released")
        return 0

    if action == "renew" and (sha is None or not current["mine"]):
        return held("absent" if sha is None else "not-holder", current)
    if action == "acquire" and current and current["live"] and not current["mine"]:
        return held("held", current)

    keep = current["acquired"] if current and current["mine"] else None
    lease_new = claims.new_lease(spec_id, me, args.label, claims.claim_minutes(root), at,
                                 acquired=keep)
    if not store.swap(spec_id, store.make(lease_new), sha):
        return held("lost", _reread(store, spec_id, me, root))
    payload = {"ok": True, **base, "lease": claims.view(lease_new, me, at)}
    if action == "take" and current and not current["mine"]:
        payload["taken"] = current
    if action == "acquire":
        payload["replaced"] = None if current is None or current["mine"] else current
    verb = {"acquire": "acquired", "renew": "renewed", "take": "taken"}[action]
    out.emit(args.json, payload, f"{spec_id}: {verb} until {lease_new['expires']} ({store.scope})")
    return 0


def _reread(store, spec_id, me, root) -> dict | None:
    sha, lease = store.read(spec_id)
    if sha is None:
        return None
    return claims.view(lease, me, claims.now(), _terminal(root, [spec_id]).get(spec_id, False))


def add_parser(sub, add_json) -> None:
    sp = sub.add_parser("claim", help="a build's reservation of a spec on the origin "
                                      "(refs/quenching/claims/<id>, compare-and-swap)")
    csub = sp.add_subparsers(dest="claim_action", required=True)
    for action, text in (("acquire", "reserve the spec; a live lease of another machine is exit 1"),
                         ("renew", "push the expiry forward; only the holder's machine"),
                         ("release", "delete the lease; only the holder's machine"),
                         ("take", "replace a live lease of another machine (a human's call)"),
                         ("list", "every lease, with live, mine, expired and terminal")):
        cp = add_json(csub.add_parser(action, help=text))
        if action != "list":
            cp.add_argument("claim_id", metavar="ID", help="the spec id")
        cp.add_argument("--remote", default="origin")
        cp.add_argument("--session", help="the session id (default: OPENCODE_SESSION_ID or "
                                          "CLAUDE_SESSION_ID)")
        if action in ("acquire", "take", "renew"):
            cp.add_argument("--label", help="an optional label the user declares; never inferred")
