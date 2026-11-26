"""PreToolUse(Bash|PowerShell) warn-level git hygiene guard for /quenching-git. Two rules, one
process, because every shell call pays one interpreter start per hook entry:

* staging is the caller's decision, so `git add -A`, `--all` and `.` are flagged;
* the leak and identity gates live in git hooks, so a command that skips them — `--no-verify`,
  `git commit -n`, or `git -c core.hooksPath=...` — is flagged too.

The file keeps the name of its first rule: the deploy's settings merge finds its own entry by it.
Warns (exit 0 + context); never blocks. It is not a security boundary: it reads the command text,
so a hook path set through a variable, an alias or `git config` before the call goes unseen.

Each regex is a fast path; a hit is confirmed on the parsed command, so text that only mentions
a blanket `git add` or a bypass flag (an echo, a quoted message, a heredoc line that is not `git`)
stays silent. Lines are split on newlines when each parses alone, else the whole command is one
stream; input that is not JSON or does not tokenize keeps the regex's verdict.

Runs under Claude Code and the GitHub Copilot harness, from bash, PowerShell or cmd — the deploy
launches it through one polyglot `python -c` line. Fails open: any crash prints `{}`.
"""
import json
import re
import shlex
import sys

BLANKET = re.compile(r"git[^|;&\n]* add +(-A|--all|\.)([^A-Za-z0-9_./-]|$)")
BYPASS = re.compile(r"git[^\n]*(--no-verify|\s-[A-Za-z]*n|core\.hookspath=)", re.I)
ASSIGNMENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")
# git's global options that take their value as the next word; every other `-x`/`--x` is a flag.
GLOBAL_VALUE_OPTIONS = ("-C", "-c", "--git-dir", "--work-tree", "--namespace", "--super-prefix",
                        "--config-env")
# `git commit` short options that take a value: the rest of a cluster after one is that value.
COMMIT_VALUE_SHORT = "mCcFt"
# `-u[<mode>]` and `-S[<keyid>]` take their value attached only: the rest of the cluster is that value.
COMMIT_ATTACHED_SHORT = "uS"
COMMIT_VALUE_LONG = ("--message", "--file", "--reuse-message", "--reedit-message", "--template")
RULES = {
    "blanket": ("/quenching-git commit never stages with git add -A, --all or `.`",
                "Invariant of /quenching-git commit: do not run git add -A, git add --all or "
                "git add . ; commit only what is already staged."),
    "bypass": ("this command skips the repository's git hooks (--no-verify, commit -n or "
               "-c core.hooksPath=)",
               "The pre-commit and pre-push hooks run the leak and identity gates. Do not skip "
               "them: fix what the hook reports and run the command again without the bypass."),
}


def _tokens(text: str) -> list[str]:
    lexer = shlex.shlex(text, posix=True, punctuation_chars=True)
    lexer.whitespace_split = True
    return list(lexer) + [";"]


def _streams(command: str) -> list[list[str]]:
    try:
        return [_tokens(line) for line in command.splitlines()]
    except ValueError:
        return [_tokens(command)]


def _git_words(words: list[str]) -> tuple[list[str], list[str]] | None:
    """The config settings (`-c`, `--config-env`) and the subcommand words of one `git`
    invocation, else None. Any global option before the subcommand is skipped."""
    while words and ASSIGNMENT.match(words[0]):
        words = words[1:]
    if not words or words[0] != "git":
        return None
    rest, configs = words[1:], []
    while rest and rest[0].startswith("-"):
        option = rest[0]
        if option in GLOBAL_VALUE_OPTIONS:
            if option in ("-c", "--config-env") and len(rest) > 1:
                configs.append(rest[1])
            rest = rest[2:]
        elif option.startswith("-c") and not option.startswith("--"):
            configs.append(option[2:])
            rest = rest[1:]
        elif option.startswith("--config-env="):
            configs.append(option.split("=", 1)[1])
            rest = rest[1:]
        else:
            rest = rest[1:]
    return configs, rest


def _blanket(words: list[str]) -> bool:
    parsed = _git_words(words)
    if not parsed:
        return False
    rest = parsed[1]
    return bool(rest) and rest[0] == "add" and any(arg in ("-A", "--all", ".") for arg in rest[1:])


def _commit_skips_hooks(args: list[str]) -> bool:
    """`-n` alone or inside a short cluster (`-nm`, `-anm`), never inside an option's value."""
    skip = False
    for arg in args:
        if skip:
            skip = False
        elif arg == "--":
            return False
        elif arg == "--no-verify":
            return True
        elif arg.startswith("--"):
            skip = arg in COMMIT_VALUE_LONG
        elif arg.startswith("-") and len(arg) > 1:
            for index, letter in enumerate(arg[1:], 1):
                if letter == "n":
                    return True
                if letter in COMMIT_ATTACHED_SHORT:
                    break
                if letter in COMMIT_VALUE_SHORT:
                    skip = index == len(arg) - 1
                    break
    return False


def _bypass(words: list[str]) -> bool:
    parsed = _git_words(words)
    if not parsed:
        return False
    configs, rest = parsed
    if any(value.lower().startswith("core.hookspath=") for value in configs):
        return True
    if "--no-verify" in rest[1:]:
        return True
    return bool(rest) and rest[0] == "commit" and _commit_skips_hooks(rest[1:])


def _hits(raw: str) -> set[str]:
    fast = {name for name, pattern in (("blanket", BLANKET), ("bypass", BYPASS))
            if pattern.search(raw)}
    if not fast:
        return set()
    try:
        command = json.loads(raw)["tool_input"]["command"]
        streams = _streams(command)
    except (ValueError, KeyError, TypeError):
        return fast
    confirmed: set[str] = set()
    checks = {"blanket": _blanket, "bypass": _bypass}
    for tokens in streams:
        words: list[str] = []
        for token in tokens:
            if set(token) <= set(";&|()"):
                confirmed |= {name for name in fast if checks[name](words)}
                words = []
            else:
                words.append(token)
    return confirmed


def stages_everything(raw: str) -> bool:
    return "blanket" in _hits(raw)


def decide(raw: str) -> dict:
    hits = [RULES[name] for name in ("blanket", "bypass") if name in _hits(raw)]
    if not hits:
        return {}
    return {
        "systemMessage": "; ".join(message for message, _ in hits),
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "additionalContext": " ".join(context for _, context in hits),
        },
    }


def main() -> None:
    try:
        out = decide(sys.stdin.read())
    except Exception:
        out = {}
    print(json.dumps(out))


if __name__ == "__main__":
    main()
