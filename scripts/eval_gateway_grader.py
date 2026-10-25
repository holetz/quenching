#!/usr/bin/env python3
"""Ask one chat model behind a Unity Gateway-style endpoint to grade, and print its answer.

The endpoint and the credential come only from the environment (`EVAL_GATEWAY_URL`, the base up to
`/v1`, and `EVAL_GATEWAY_TOKEN`); nothing about the workspace is stored in the repository. Exits
non-zero, with the reason on stderr, when the answer cannot be trusted as complete: a missing
variable, an output ceiling under the floor, an HTTP failure, or `finish_reason` `length`. The
runner records any non-zero exit as `unknown`, so such an answer never counts as an approval.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request

MIN_OUTPUT_TOKENS = 16000


def fail(message: str, code: int = 2) -> int:
    print(f"eval_gateway_grader: {message}", file=sys.stderr)
    return code


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--model", required=True)
    p.add_argument("--max-tokens", type=int, default=MIN_OUTPUT_TOKENS)
    p.add_argument("--prompt-file", required=True)
    p.add_argument("--timeout", type=int, default=600)
    args = p.parse_args(argv)
    if args.max_tokens < MIN_OUTPUT_TOKENS:
        return fail(f"--max-tokens {args.max_tokens} is under the {MIN_OUTPUT_TOKENS} floor")
    url, token = os.environ.get("EVAL_GATEWAY_URL"), os.environ.get("EVAL_GATEWAY_TOKEN")
    missing = [n for n, v in (("EVAL_GATEWAY_URL", url), ("EVAL_GATEWAY_TOKEN", token)) if not v]
    if missing:
        return fail(f"missing {', '.join(missing)} in the environment")
    with open(args.prompt_file, encoding="utf-8") as handle:
        prompt = handle.read()
    body = json.dumps({"model": args.model, "temperature": 0, "max_tokens": args.max_tokens,
                       "messages": [{"role": "user", "content": prompt}]}).encode()
    request = urllib.request.Request(url.rstrip("/") + "/chat/completions", data=body, method="POST",
                                     headers={"Content-Type": "application/json",
                                              "Authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(request, timeout=args.timeout) as response:
            payload = json.load(response)
    except urllib.error.HTTPError as exc:
        return fail(f"HTTP {exc.code} from the gateway", 3)
    except (urllib.error.URLError, OSError, json.JSONDecodeError) as exc:
        return fail(f"the gateway call failed: {type(exc).__name__}", 3)
    try:
        choice = payload["choices"][0]
        text = choice["message"]["content"]
    except (KeyError, IndexError, TypeError):
        return fail("the answer has no choices[0].message.content", 3)
    if choice.get("finish_reason") == "length":
        return fail("finish: length - the answer was cut at the output ceiling", 4)
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
