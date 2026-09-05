"""The ``cq toolchain`` parser and its read-only floor verbs."""
from __future__ import annotations

import argparse

from quenching.common.front import build_parser as build_front_parser, resolve_root
from quenching.common.output import emit, refuse
from quenching.common.version import VERSION
from quenching.toolchain.doctor import doctor, inspect_toolchain


def build_parser() -> argparse.ArgumentParser:
    parser = build_front_parser(
        "cq toolchain", "probe and report a repository's toolchain surface",
        (("doctor", "probe applicability and report toolchain findings"),
         ("status", "read the toolchain applicability state")),
    )
    parser.add_argument("--version", action="store_true", help="print the toolchain version")
    return parser


def _root(value: str | None) -> str:
    return resolve_root(value)


def _human_doctor(payload: dict) -> str:
    state = payload["applicability"]["state"]
    artifacts = ", ".join(payload["applicability"]["artifacts"]) or "(none)"
    return f"toolchain doctor — {payload['root']} ({state}); artifacts: {artifacts}"


def _status_payload(payload: dict) -> dict:
    applicability = payload["applicability"]
    return {
        "root": payload["root"],
        "applicability": applicability,
        "findings": {},
        "ok": payload["ok"],
    }


def _human_status(payload: dict) -> str:
    state = payload["applicability"]["state"]
    return f"toolchain status — {payload['root']} ({state})"


def main(argv: list[str]) -> int:
    if "--version" in argv:
        print(f"cq toolchain {VERSION}")
        return 0
    parser = build_parser()
    args = parser.parse_args(argv)
    as_json = bool(getattr(args, "json", False))
    if not args.cmd:
        return refuse({"code": "tc-no-command", "message":
                       "choose `doctor` or `status`"}, as_json)
    root = _root(args.root)
    if args.cmd == "doctor":
        payload, err, code = doctor(root)
        if err:
            return refuse(err, as_json)
        assert payload is not None
        emit(as_json, payload, _human_doctor(payload))
        return code
    payload, err = inspect_toolchain(root)
    if err:
        return refuse(err, as_json)
    assert payload is not None
    summary = _status_payload(payload)
    emit(as_json, summary, _human_status(summary))
    return 0
