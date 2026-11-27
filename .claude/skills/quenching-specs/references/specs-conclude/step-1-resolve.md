# /quenching-specs conclude — step 1: Resolve the spec, the outcome, and what already happened

Resolve `specs_*`, `git_*` and `components_*` per
[align/tool-resolution.md](.agents/quenching/references/align/tool-resolution.md)
§Resolving the tool. Branch on the **exit code** (0 ok · 1 findings · 2 refusal) and the `--json`,
never on prose. The layout and the gates live in
[specs-develop/spec-driven.md](.agents/quenching/references/specs-develop/spec-driven.md)
§The spec document §The gates and the stage-scoped explicit-none rule; the tool surface in
[specs-surface.md](.agents/quenching/references/specs-develop/specs-surface.md)
§The `.agents/quenching/bin/cq specs` tool surface.

**Doctrine of this step.**

- **The outcome is stated, never inferred.** `done` and `abandoned` are opposite claims about the
  same file, and nothing — not task progress, not staleness, not a sweep — may decide which was
  meant. If the human has not said, ask — under `autonomous`, refuse instead.
- **Concluding as `done` refuses to lie.** Open `- [ ]` boxes with `--outcome done` is exit 2 with
  the list. `--force` exists for the case where the human knows why — the work was descoped, or
  proven elsewhere — and says so.

**Resuming.** Each stage has one durable signal; a stage whose signal is already set is **reported
and skipped**, not repeated (the signal is in each step). Here: *already merged* — the work ref is in
`origin/<base>`, or a `merge` record exists, or the `pr` record's PR is merged → the hand-off is
done, run only step 8; *archived* — the spec is in `archive/` with `outcome:` stamped → report it
closed, nothing is left to run. `merge` and `pr` are read only to answer those rows, and for
`abandoned` from the base checkout.

**Under `autonomous`.**

| Where it would ask | The answer |
| --- | --- |
| the outcome | taken **only** from the input's `--outcome`; absent → `needs-human`. `autonomous` never supplies an outcome |
| which spec (several marked ids, or no marking) | `needs-human` |
| open tasks under `done` | `needs-human`; never `--force`, never a switch to `abandoned` |

An ID in the input → use it. **No ID given → try auto-discovery first**, off the current
branch's own marking:
[auto-discover.md](.agents/quenching/references/specs-conclude/auto-discover.md)
§Reading the marking §Filtering to valid IDs §Resolving what remains, cited rather than
restated. One valid id resolves it silently, naming the marking as the source; more than one asks
which, on a decision sheet. No valid marking → §The fallback there measures the diff and always
asks whether to materialize a minimal spec — accepted, its new id is used from here on exactly
like a marked one. **Declined, headless completion — closing with no spec file at all — is not
built**: say so, record it with `specs_write(verb="discover")`, and fall back to `specs_read(verb="list")` and
ask. Establish the outcome — **ask if it was not stated**, on a
decision sheet: *done* (it shipped) or *abandoned* (it will not be built). Under `autonomous`,
every question of this run is answered by the `autonomous` answers of the steps (index); elsewhere a sub-agent does not ask:
return `STATE: blocked` with `NOTE: needs-human:` carrying the decision sheet.
```text
specs_read(verb="status", spec=<id>)
```
**First close what is already merged:** `specs_write(verb="reconcile", write=true)` archives every
spec of the front whose work is merged and whose `## Outcome` is written, this one included. A row
for this spec with `action: archived` → report it closed and run only step 8's worktree release; a
`needs-human` row is carried to the report. Then read task progress, the `## Outcome` state, and the
records — `branch`, `reviewed`, `merge`, `pr`, `outcome` — from that payload. Then, for the `## Discoveries` lines themselves, the one body this
step needs: `specs_read(verb="section", spec=<id>, headings="Discoveries")`. Then read git: the
current branch, whether the work branch exists, and whether it is already merged. Announce the
outcome and, per the Resuming signals, which stages this run will actually perform.

Open tasks under a `done` outcome are surfaced **now**, before anything is written, so the human
can choose between finishing them, forcing, or switching to `abandoned`.

**Renew the build's reservation** — the review, the distillation and the gate can outlast it:
`specs_external(verb="claim_renew", claim_id=<id>)`. Exit 0, `reason: absent` or exit 2 → go on (report exit 2).
`reason: not-holder` → another machine holds the lease: **stop** with `held-by: <holder>` and
write nothing; taking it back is the human's call (`.agents/quenching/bin/cq specs claim take`), never this run's.
