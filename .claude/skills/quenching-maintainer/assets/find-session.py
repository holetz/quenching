#!/usr/bin/env python3
"""Locate a quenching-management session log by its AI title — robustly.

Solves the two failure modes of the old inline grep recipe:

  1. Current-session leak. The old guard `${CLAUDE_SESSION_ID:-__none__}` silently
     resolved to "__none__" when the env var was unset, so the *current*
     retrospective session leaked into the candidate list and had to be excluded
     by hand. Here the current session is detected from `CLAUDE_CODE_SESSION_ID`
     (the harness env var's real name — the old recipe read the non-existent
     `CLAUDE_SESSION_ID`), falling back to the newest-mtime `.jsonl` whose internal
     `cwd` == the invocation cwd. It is flagged CURRENT and never recommended.

  2. Blind ranking. The old recipe printed `file :: aiTitle` with no metadata, so
     telling the genuine applied run from a same-titled locate/retrospective run
     meant a second manual grep pass for cwd / branch / launch markers. Here every
     match is enriched (cwd, branch, quenching-launch?, exact-vs-substring title,
     line count, span) and ranked, with a single RECOMMENDED pick — while still
     listing all matches so the maintainer makes the final call.

Read-only. Touches nothing under ~/.claude/; only reads the logs.

Usage:
    python3 find-session.py "<title substring>" [--pwd <dir>] [--json]

    --pwd   Working dir used to identify the current session (default: $PWD).
    --json  Emit machine-readable JSON instead of the human table.

Exit code: 0 if >=1 non-current match (exact OR broadened), 3 only if none even
after broadening (so callers can branch). Matching is on aiTitle only — never
prompt text.

Resourceful fallback (do not dead-stop): the history sometimes labels a section
with a timestamp placeholder like "Quenching 2026-07-02 15:09" that equals no real
aiTitle. Rather than exit 3, this broadens to the salient (non date/time) title
token(s) — still aiTitle only — and, when the name embeds a date/time, ranks the
survivors by proximity of that timestamp (read as LOCAL wall-clock → UTC) to each
candidate's span, as a tie-breaker among equal-score genuine candidates.
"""
import os
import re
import sys
import json
import glob
import datetime

TITLE_RE = re.compile(r'"aiTitle":"((?:[^"\\]|\\.)*)"')
SID_RE   = re.compile(r'"sessionId":"([^"]+)"')
CWD_RE   = re.compile(r'"cwd":"((?:[^"\\]|\\.)*)"')
BRANCH_RE= re.compile(r'"gitBranch":"((?:[^"\\]|\\.)*)"')
TS_RE    = re.compile(r'"timestamp":"([^"]+)"')

LAUNCH_MARKER = "/claude-quenching:quenching-management"
RETRO_MARKER  = "quenching-retrospective"


def unescape(s):
    try:
        return json.loads('"' + s + '"')
    except Exception:
        return s


def parse_iso(ts):
    if not ts:
        return None
    try:
        return datetime.datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except Exception:
        return None


def salient_tokens(name):
    """The title words of a query, dropping date/time/pure-number noise."""
    s = re.sub(r"\d{4}-\d{2}-\d{2}", " ", name)
    s = re.sub(r"\b\d{1,2}:\d{2}\b", " ", s)
    return [t.lower() for t in re.split(r"[^0-9A-Za-z]+", s) if t and not t.isdigit()]


def query_dt_utc(name):
    """A date/time embedded in the query (history labels sections `<date> <time>`),
    read as LOCAL wall-clock and converted to UTC so it can rank UTC log spans."""
    dm = re.search(r"\d{4}-\d{2}-\d{2}", name)
    tm = re.search(r"\b(\d{1,2}):(\d{2})\b", name)
    if not dm and not tm:
        return None
    now = datetime.datetime.now()
    if dm:
        y, mo, da = (int(x) for x in dm.group(0).split("-"))
    else:
        y, mo, da = now.year, now.month, now.day
    hh, mm = (int(tm.group(1)), int(tm.group(2))) if tm else (0, 0)
    local_tz = now.astimezone().tzinfo
    try:
        naive = datetime.datetime(y, mo, da, hh, mm, tzinfo=local_tz)
    except ValueError:
        return None
    return naive.astimezone(datetime.timezone.utc)


def gap(r, qdt):
    """Seconds between the query datetime and the candidate's [first,last] span
    (0 if inside). Neutral (0) when the query carries no timestamp."""
    if qdt is None:
        return 0.0
    lo = parse_iso(r["first_ts"])
    hi = parse_iso(r["last_ts"])
    if lo is None and hi is None:
        return 9e18
    lo = lo or hi
    hi = hi or lo
    if lo <= qdt <= hi:
        return 0.0
    return min(abs((qdt - lo).total_seconds()), abs((qdt - hi).total_seconds()))


def scan(path):
    """Cheap single-pass scan — string search per line, JSON only on the bits we need."""
    last_title = None
    session_id = None
    cwd = branch = None
    first_ts = last_ts = None
    lines = 0
    is_launch = is_retro = False
    try:
        with open(path, "r", errors="replace") as fh:
            for ln in fh:
                lines += 1
                if '"aiTitle"' in ln:
                    m = TITLE_RE.search(ln)
                    if m:
                        last_title = unescape(m.group(1))
                    s = SID_RE.search(ln)
                    if s:
                        session_id = s.group(1)
                if cwd is None and '"cwd"' in ln:
                    m = CWD_RE.search(ln)
                    if m:
                        cwd = unescape(m.group(1))
                    b = BRANCH_RE.search(ln)
                    if b:
                        branch = unescape(b.group(1))
                if '"timestamp"' in ln:
                    m = TS_RE.search(ln)
                    if m:
                        if first_ts is None:
                            first_ts = m.group(1)
                        last_ts = m.group(1)
                if not is_launch and LAUNCH_MARKER in ln:
                    is_launch = True
                if not is_retro and RETRO_MARKER in ln:
                    is_retro = True
    except OSError:
        return None
    if session_id is None:
        session_id = os.path.splitext(os.path.basename(path))[0]
    return {
        "file": path,
        "title": last_title,
        "session_id": session_id,
        "cwd": cwd,
        "branch": branch,
        "first_ts": first_ts,
        "last_ts": last_ts,
        "lines": lines,
        "is_launch": is_launch,
        "is_retro": is_retro,
        "mtime": os.path.getmtime(path),
    }


def main():
    args = [a for a in sys.argv[1:]]
    as_json = "--json" in args
    args = [a for a in args if a != "--json"]
    pwd = os.getcwd()
    if "--pwd" in args:
        i = args.index("--pwd")
        pwd = args[i + 1]
        del args[i:i + 2]
    if not args:
        print("usage: find-session.py \"<title substring>\" [--pwd <dir>] [--json]",
              file=sys.stderr)
        return 2
    name = args[0]
    name_lc = name.lower()

    root = os.path.expanduser("~/.claude/projects")
    files = glob.glob(os.path.join(root, "**", "*.jsonl"), recursive=True)
    recs = [r for r in (scan(f) for f in files) if r]

    # --- identify the current session ---
    # Primary: the harness env var (its real name is CLAUDE_CODE_SESSION_ID — the
    # old recipe read the non-existent CLAUDE_SESSION_ID, which is why the current
    # session leaked in). Fallback: newest-mtime log whose internal cwd == pwd, so
    # detection still works if the env var is ever absent.
    env_sid = (os.environ.get("CLAUDE_CODE_SESSION_ID")
               or os.environ.get("CLAUDE_SESSION_ID"))
    current = None
    if env_sid:
        for r in recs:
            if r["session_id"] == env_sid or env_sid in r["file"]:
                current = r["file"]
                break
    if current is None:
        here = [r for r in recs if r["cwd"] == pwd]
        if here:
            current = max(here, key=lambda r: r["mtime"])["file"]

    # --- title matches (aiTitle only — NEVER prompt text) ---
    matches = [r for r in recs if r["title"] and name_lc in r["title"].lower()]

    # Resourceful fallback: a placeholder / timestamp-style name (e.g.
    # "Quenching 2026-07-02 15:09") rarely equals a real aiTitle. Rather than
    # dead-stop, broaden to the salient (non date/time) title token(s) — still
    # aiTitle only — and let any embedded timestamp rank the survivors.
    broadened = False
    toks = salient_tokens(name)
    if not matches and toks:
        matches = [r for r in recs
                   if r["title"] and all(t in r["title"].lower() for t in toks)]
        broadened = bool(matches)
    qdt = query_dt_utc(name)   # name's local wall-clock -> UTC, for ranking

    def score(r):
        s = 0
        if r["file"] == current:
            s -= 1000
        if r["is_launch"]:
            s += 100
        if r["is_retro"] and not r["is_launch"]:
            s -= 50          # a locate/retrospective session, not an application
        if r["title"] and r["title"].lower() == name_lc:
            s += 40          # exact title beats substring
        else:
            s += 10
        if r["cwd"] and r["cwd"] != pwd:
            s += 20          # ran on a target repo, not the method repo
        return s

    # Strongest signals first (launch on a target repo), then the timestamp as a
    # TIE-BREAKER among equal-score genuine candidates — robust to tz assumptions,
    # since it only decides between same-title applied runs where proximity is real.
    matches.sort(key=lambda r: r["last_ts"] or "", reverse=True)
    matches.sort(key=lambda r: (r["file"] == current, -score(r), gap(r, qdt)))
    non_current = [r for r in matches if r["file"] != current]
    recommended = non_current[0]["file"] if non_current else None

    if as_json:
        out = {
            "query": name,
            "pwd": pwd,
            "broadened": broadened,
            "salient": toks,
            "query_datetime_utc": (qdt.strftime("%Y-%m-%dT%H:%M:%SZ") if qdt else None),
            "current_session": current,
            "recommended": recommended,
            "matches": [
                {k: v for k, v in r.items() if k != "mtime"} | {
                    "is_current": r["file"] == current,
                    "is_recommended": r["file"] == recommended,
                    "exact_title": bool(r["title"] and r["title"].lower() == name_lc),
                    "ts_gap_seconds": (None if qdt is None else round(gap(r, qdt))),
                }
                for r in matches
            ],
        }
        print(json.dumps(out, indent=2, ensure_ascii=False))
        return 0 if non_current else 3

    if not matches:
        hint = (f"broadened to {toks}" if toks
                else "no non-date/time title token to broaden on — pass a title word")
        print(f"ZERO aiTitle matches for {name!r} across {len(files)} logs "
              f"({hint}) — report it and stop (never fall back to prompt-text matches).")
        return 3

    print(f"Query {name!r} · scanned {len(files)} logs · "
          f"current session: {current or '(undetermined)'}\n")
    if broadened:
        rank = (f" · ranked by proximity to {qdt:%Y-%m-%d %H:%M} UTC (name's local "
                f"time → UTC)" if qdt else "")
        print(f"No exact-title match — broadened to salient token(s) {toks} "
              f"(aiTitle only, never prompt text){rank}.\n"
              "Confirm the ★ pick with the maintainer before replaying.\n")
    for i, r in enumerate(matches, 1):
        tag = "  CURRENT (excluded)" if r["file"] == current else \
              (" ★ RECOMMENDED" if r["file"] == recommended else "")
        kind = "quenching-launch" if r["is_launch"] else \
               ("retrospective/locate" if r["is_retro"] else "other")
        exact = "exact" if (r["title"] and r["title"].lower() == name_lc) else "substring"
        print(f"[{i}]{tag}")
        print(f"    title  : {r['title']!r}  ({exact})")
        print(f"    project: {r['cwd']}  ({r['branch']})")
        print(f"    kind   : {kind} · {r['lines']} lines · {r['first_ts']} -> {r['last_ts']}")
        if qdt is not None:
            g = gap(r, qdt)
            gtxt = "within span" if g == 0 else f"{int(round(g / 60))} min from span"
            print(f"    ts-gap : {gtxt}")
        print(f"    file   : {r['file']}\n")

    if broadened or len(non_current) > 1:
        print("Confirm the RECOMMENDED pick with the maintainer before replaying "
              "(one session per invocation — never silently merge).")
    return 0 if non_current else 3


if __name__ == "__main__":
    sys.exit(main())
