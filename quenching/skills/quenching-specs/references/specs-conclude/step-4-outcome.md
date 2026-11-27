# /quenching-specs conclude — step 4: Write `## Outcome`

**Doctrine of this step.** *Abandoning is always allowed*: `--outcome abandoned` never refuses and
never needs `--force`. *Everything `abandoned` writes lands in the checkout holding `<base>`, never
this branch* — see
[specs-conclude/abandoned.md](.agents/quenching/references/specs-conclude/abandoned.md)
§Locating the checkout and writing into it. *A `done` spec is archived after its merge, never
before*: the spec store is a git ref, so an archive is visible to every reader the moment it is
written while the PR can still stall or be closed; `specs_write(verb="promote", spec=<id>,
to="archive", outcome="done")` refuses while the work ref is not in `origin/<base>`, and `--force`
does not reach that refusal.

**Resuming.** Signal: the `## Outcome` section is filled → skip the draft; go to distil. `outcome`
is `writeOnce: true`: if it is already set and reality disagrees, that is a **finding to report**,
never a value to overwrite.
**Under `autonomous`.** The `## Outcome` draft is written unconfirmed; for `abandoned`, an exit 2
from `promote` → `needs-human` with the refusal quoted, never `--force`.

**First preserve observed build cost, with provenance.** This is independent of the derived
`specs_read(verb="estimate")` reading heuristic. Inspect `records.buildCost` from step 1: a valid measured
record already covers the build and survives a resumed conclude; do not replace it with missing
telemetry. New evidence may replace `unavailable`, with every field written together so an old
reason or measurement cannot survive the re-stamp. An abandoned, unbuilt spec also reports
unavailable rather than inventing an execute cost.

Use the existing meter **only** when the briefing identifies an explicit **build-only** Claude
Code subagents directory and the agent ids belonging to this spec's execute runs:

```text
components_read(verb="session_cost", transcript=<explicit-build-only-subagents-directory>)
```

**Never infer** that scope from the latest session, the source spec's branch, transcript mtime,
prompt prose or a directory containing unrelated workers. Missing/ambiguous scope, native **Codex**
usage that was not measured, a meter refusal, missing requests or parse findings are unavailable;
exit 1 is partial evidence, never silently a complete measurement. Preserve the reason and scope
in the report. Do not invent usage from context capacity, file sizes or model memory.

On exit 0 with exact attribution and known models, retain the meter's `byModel` totals **per model**:
`model`, `requests`, `input`, `cacheRead`, `cacheWrite`, `output`. For each model, add
`maxRequestExposureTokens` as the maximum `groups[].maxWindow` for that model. That existing
meter field is reported request exposure, **never a context peak**: executor iterations can
aggregate in top-level usage. State that limitation in `source`; no iteration-peak coverage is
claimed. Keep the array compact as one JSON scalar, with no sum across tiers and no monetary cost.
Set `source` to runtime, explicit directory/agent ids, measurement command/exit and coverage;
`measurements` contains only observed values, and `reason` is empty. An unknown model/agent
attribution does not justify a measured whole-build claim.

Write the conclude-owned record **before `## Outcome`**, through the generic record writer:

```text
specs_write(verb="record", spec=<id>, name="buildCost", fields={"status": "measured", "date": "<today>", "source": "<runtime; exact build scope; command/exit; request-exposure limitation>", "measurements": "<compact per-model JSON array from the observed payload>", "reason": ""})
```

For unavailable evidence write no numeric stand-in; an empty scalar is absence, not zero:

```text
specs_write(verb="record", spec=<id>, name="buildCost", fields={"status": "unavailable", "date": "<today>", "source": "<runtime and any explicitly known scope>", "measurements": "", "reason": "<why the build was not measured>"})
```

Read the write's exit code; retry a transport failure with backoff, and read an exit-2 refusal
without repeating it blindly. A failed write stops this step before `## Outcome`. Report the record's
status, provenance, per-model values or unavailable reason; calibration is future evidence work,
not an inference this conclude makes.

`## Outcome` is the archive gate — the post-merge close cannot archive without it, so it is written
now, while the run still knows what shipped. Draft it, confirm it (under `autonomous`, the `autonomous` answer of this step), write it:
```text
specs_write(verb="section_write", spec=<id>, heading="Outcome", body=<body>)
```
For `done`: what shipped, what was left out, what the next reader needs — **reviewed, distilled,
ready for merge**; name neither a merge strategy nor a PR. **Do not archive it here** — the spec
stays in `plans/` until step 8 runs after the merge.

For `abandoned`: the reason it will not be built is the whole content, and nothing will merge, so
the archive happens now:
```text
specs_write(verb="promote", spec=<id>, to="archive", outcome="abandoned")
```
A refusal (exit 2) lists exactly what is missing — surface it verbatim and let the human decide;
**never pass `--force` on your own initiative.**
