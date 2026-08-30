# Ops front entry-point contract

<!-- rules -->

This file is self-contained: an ops align reads it to classify entry points and findings without
loading another front reference.

## Contents

`cq components read <this file>` returns the heading index; `--sections` addresses one.

## The seven rules

Every active entry point answers to these rules. `checked` is a property the verifier can decide
statically; `prose, with static proxy` is reported by the align because the full claim requires
running arbitrary target code.

| # | Rule | Kind |
| --- | --- | --- |
| 1 | Every entry point is reachable from the canonical router and named by the generated registry. | checked |
| 2 | Repository-root resolution, `sys.path`, and shared flags come from one bootstrap module. | checked |
| 3 | Exit codes are typed: `0` for success, `1` for findings, and `2` for misuse. | checked |
| 4 | Data goes to `stdout`, diagnostics go to `stderr`, and `--json` puts only data on `stdout`. | checked |
| 5 | An entry point that writes outside the repository is preview-first, armed by an explicit flag, and never armed by editing its source. | checked |
| 6 | `--help` carries a usage example. | prose, with static proxy |
| 7 | Every entry point declares one lifecycle: `active` or `archived`. | checked |

For rule 6, the verifier checks only the static proxy: a non-empty `description` or `epilog` on
the parser. The align reports that proxy and names the rule; it never claims to have proven the
runtime help output.

## The disabled-gate rule

A verification call commented out inside an entry point's control flow is a finding, not a
configuration. A repository that wants a check off declares that state explicitly; it never hides
the call behind `#`. The verifier detects the disabled call with Python's `tokenize` module beside
its AST pass: a `COMMENT` token whose text, after the leading `#` is removed, parses as a call
expression and sits by indentation inside AST-identified entry-point control flow.

## Finding codes

The verifier and align use these stable codes:

| Code | Meaning |
| --- | --- |
| `op-undocumented` | An active entry point exists but is not named by the generated registry. |
| `op-registry-stale` | The generated registry does not match the entry points reachable from the router. |
| `op-adhoc-root` | An entry point resolves the repository root outside the shared bootstrap module. |
| `op-untyped-exit` | An entry point returns an untyped or otherwise non-contractual exit status. |
| `op-unarmed-write` | An operation writes outside the repository without preview-first behaviour and an explicit arming flag. |
| `op-disabled-check` | A verification call is commented out inside an entry point's control flow. |
| `op-orphan` | An entry point is present in the operations tree but is not reachable from the canonical router. |
| `op-no-router` | The repository has no single declared router for its normalized operations surface. |

<!-- rationale -->

The `Kind` column prevents a static verifier from making a claim it cannot prove. Rules 1–5 and 7
describe structure or source-level behaviour; rule 6 would require executing target code merely to
read its help, so the static parser proxy is the honest boundary.

The disabled-gate rule is separate because a comment is invisible to the AST and therefore to the
ordinary call inventory. Pairing `tokenize` with the AST keeps the finding narrow enough to review:
it looks for a call-shaped comment in entry-point control flow, not every code-looking example in a
repository.
