---
type: standard
title: An explicit --root override must refuse when mis-levelled
description: An explicit --root/SPECS_ROOT that resolves to the CONTAINER of a phased workspace, rather than the workspace itself, must refuse (exit 2, sp-root-too-high) instead of reading as merely empty or writing to the wrong place — one shared predicate, one shared refusal idiom, and the one exception a diagnostic verb takes, reporting the same condition as a finding rather than refusing
resource: plugins/quenching/assets/bin/quenching/specs/config.py, plugins/quenching/assets/bin/quenching/specs/backends/__init__.py, plugins/quenching/assets/bin/quenching/specs/commands/doctor.py
tags: [code, cli, validation, root-resolution, findings, refusals]
timestamp: 2026-08-12
audience: both
authority: current
source: spec plan/refuse-a-mis-levelled-specs-root (tasks 1.1-2.2) — proved against this repository's own `cq specs --root .` invocation, measured on 2026-08-02 with 58 specs silently reading back as "no specs" before the fix
maintainer: quenching
---

# An explicit `--root` override must refuse when mis-levelled

**A false-empty answer and a true-empty answer must never share one exit code.** An explicit
`--root`/`SPECS_ROOT` that names the *container* one level above a phased workspace — the parent
of `.specs/`, rather than `.specs/` itself — used to read back exactly like a genuinely empty
workspace: `list` printed "no specs", `validate` passed having opened nothing, and `new` wrote a
spec into `./plans/` beside the container instead of inside `.specs/plans/`, silently, at exit 0.
The mistake is not hypothetical: it is one `--root .` away from the correct answer, typed from the
one directory up the tree from where it should be typed, and nothing about the tool's output told
the difference from a fresh, unpopulated install.

## The predicate, in one place

`is_root_too_high(root)` ([config.py:38](../../../plugins/quenching/assets/bin/quenching/specs/config.py#L38))
answers the structural question directly: `root` holds none of `PHASE_DIRS` itself, **and**
`root/.specs` holds at least one. Both conditions matter — a root that already qualifies as the
workspace returns `False` even when some unrelated `.specs/` sits nested deeper inside it, and a
genuinely fresh, unpopulated directory returns `False` too, because `## Out of Scope` protects the
one legitimate reason a workspace reads empty: nobody has run `new`/`align` against it yet.

The predicate reuses the same phase-folder idea `_holds_phase_folder` already answers for a
neighbouring problem (`worktree.py:190-191`) rather than reimplementing it a third time, and it is
**only ever true over an explicit override**. The default nearest-upward search
(`find_specs_root`'s own fallback, same file) stops the moment it finds a directory literally named
`.specs`, so the root it returns can never be the container this predicate looks for — no separate
branch is needed to keep the default search exempt; the construction already guarantees it.

## One refusal idiom, one message, two call sites

The refusal lives where the ~19 verbs that read or write the spec tree already converge —
`open_backend`'s `files` branch ([backends/__init__.py:49](../../../plugins/quenching/assets/bin/quenching/specs/backends/__init__.py#L49))
— so one call site covers every one of them for free, following the idiom already in use beside it
(`{"code": ..., "exit": 2, ...}`, the same shape as `sp-backend-unavailable` in the same file):

```python
if is_root_too_high(root):
    return None, {
        "code": "sp-root-too-high", "exit": 2, "root": root,
        "message": root_too_high_message(root), "remedy": ROOT_TOO_HIGH_REMEDY,
    }
```

The message and the remedy are written **once**, beside the predicate
(`root_too_high_message`/`ROOT_TOO_HIGH_REMEDY`, `config.py`), and every caller cites them rather
than restating the text — a second call site that composed its own wording would drift from the
first the moment either was edited alone.

## The diagnostic exception

`doctor` never calls `open_backend`, and its own contract is to always complete and report,
never to refuse — that is already the shape of its `sp-no-workspace` finding. The same predicate
therefore enters `doctor` as a **finding**, not a refusal
([doctor.py:177](../../../plugins/quenching/assets/bin/quenching/specs/commands/doctor.py#L177)),
returning early exactly as `sp-no-workspace` already does — so the harmless `sp-missing-phase`
warnings for `plans/`/`archive/` never also fire over the same mis-levelled root, which would
describe the workspace as new rather than misaddressed.

> **A tool that reads or writes real data refuses on this condition. A tool whose whole job is to
> report on the tree completes and names it as a finding instead.** The two are the same fact,
> answered differently on purpose — never the same answer reused by copy.

## Generalising this rule

This is a **narrow instance of a wider shape**: any `--root`/config-path override that resolves to
a directory *measurably different* from the target the caller actually meant should refuse, rather
than silently substitute the wrong directory and let the symptom look like ordinary emptiness. The
identical hole exists one pillar over — `find_surface_root`
(`plugins/quenching/assets/bin/quenching/components/surface.py:88`) takes an explicit `--root`/
`SKILLS_ROOT` with the same unguarded shortcut (`if root_arg: return os.path.abspath(root_arg)`)
and no check that it actually lands on a surface. Fixing it changes a different pillar's own
contract and its own subcommands, so it is not folded into this spec — parked instead as a
discovery for whoever closes that gap — but when it is fixed, this is the contract to follow: a
shared predicate, a refusal at the write/read choke point, and a finding (never a refusal) at the
diagnostic that must keep completing.
