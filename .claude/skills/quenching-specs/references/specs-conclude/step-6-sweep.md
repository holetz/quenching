# /quenching-specs conclude — step 6: Sweep the flow itself, and capture what it owes

**Resuming.** No record — offered once per conclude; the specs it captured are their own
evidence: read the front for the captured ids and report them; re-sweep only when this run revealed
a new defect.
**Under `autonomous`.** `done` and `abandoned`: every evidenced candidate is captured unasked with
`specs_write(verb="create")`, one spec per candidate, its `## Problem` carrying the inputs; none is
developed, and the ids are named in the report.

The change is finished; the way it was made is evidence too. **Read the session first, once:**
`components_read(verb="session_digest", cap=5)` counts the corrections, the repeated
reads and shells and the anomalies from the transcript, so the judgment below does not rest on
memory. A non-zero exit (no transcript on this host) is neither retried nor reported: go on and
judge from the conversation, with no further read and no fallback. This step judges the run itself — the
skills, flow references, agents, standards, harness and deploy surface that carried it — and turns
each real defect into a spec of its own, captured with the problem and the evidence it needs, for
another session to develop. The project's automation evolves because its runs leave the defects
written down instead of carrying them to the next session's memory.

**A candidate is a defect of the project's own automation, evidenced by this run.** All three must
hold:

1. it is about **how the work was carried**, not what it delivered — the delivered change is the
   branch's and is already handled here;
2. this run produced the evidence, quotable: a step that had to be improvised, a reference that
   contradicted another, a gate that could not see a class of defect, a command whose failure the
   flow does not anticipate, a rule the run had to invent because no standard had it, or a figure
   of the session digest (a human correction, a repeated read or shell, an anomaly) with its
   number and its quoted turn;
3. no open spec already covers it — check the front first
   (`specs_read(verb="list")`, matched on the title and on the defect it names)
   and add a `## Discoveries` line there instead of opening a duplicate.

**What does not qualify matters as much**: a defect of the delivered product, a nit in one file, a
preference of this session, or an improvement no fact from this run supports. Zero is a valid
result only when neither the digest nor the run evidences a defect; a sweep that finds something
every time is inventing.

**One spec per candidate, captured and not designed** — the design costs a session, and the session
that takes it should be the one that argues with the defect — one `specs_write(verb="create")` that carries
`## Problem`:

```text
specs_write(verb="create", name="<the defect, in one line>", complexity="medium", sections=[{"heading": "Problem", "body": "<the body below>"}])
```

The `## Problem` body:

```markdown
<what happened, in this run's own facts: the step, the command and its output, the file:line of the
reference that misled, the spec and the date — and what the improvement has to make impossible>

Minimal fix proposed: <the smallest fix that fits the defect, in one line>

**Insumos**

- <path:line of the reference, the standard, the agent definition>
- <the command that failed, with its exit code and its output quoted>
- <the spec id and the step of this run where it happened>
```

A fix that would need a new layer, a new step in a command body or tokens with no measured return is
not proposed in the spec: it is one line in the report, as a decision for the human. The problem carries the **inputs** — the paths, the command and its output, the spec id — because
the session that develops it will not have this conversation. **Never develop the captured spec
here**: its design and its go belong to whoever takes it, unless the human asks for that improvement
in this same run, and then it is a new `create` and not a task of this spec.

**Where the improvement lives decides what the spec says.** A defect of a `quenching-*` skill, flow,
agent or runtime is fixed in the quenching checkout and reaches the repository by `cq deploy`, so
the `## Problem` names the source path in that checkout and the deploy step, never the generated
copy in this repository. A defect of this repository's own skill, standard, harness or script is
fixed here, and the spec says so.

Present the candidates as ONE plan and take one confirmation (under `autonomous`, the `autonomous` answer of this step answers it): each candidate with its evidence, and for each the choice between
capturing it now — the default — and declining it. A declined candidate is named in the report with
its reason, never silently dropped, and a resumed run re-reads the front instead of opening a second
spec for the same defect.

For `abandoned`, the sweep is about how the flow carried a spec nobody built; most abandonments
teach nothing, and that is the correct result.
