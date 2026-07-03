# Signature experience — make it iconic

The difference between docs people *tolerate* and docs people *remember*. This layer
is about making the reading experience memorable — **without ever sliding into empty
marketing**. Every element here is earned by substance.

## The eight signature elements
A site that lands has most of these. Design them deliberately.

| Element | What it is | Test |
| --- | --- | --- |
| **Central thesis** | one idea the whole site defends | the reader can restate it in a sentence |
| **Repeatable line** | a short, true phrase that sticks | it's quotable *and* accurate |
| **Controlled metaphor** | one metaphor, defined once, reused | the literal definition is given first |
| **First mental map** | the picture a newcomer forms early | it survives contact with the detail |
| **Primary visual flow** | the one diagram that explains the system | remove it and the site gets harder |
| **Landing promise** | a concrete promise, not an adjective | it names a real outcome |
| **60-second aha** | the payoff in the first minute | a skimmer "gets it" before scrolling far |
| **Reading progression** | each section raises the next's question | the site reads as one arc |

## How to find the thesis
Read the sources and finish this sentence: *"If the reader remembers one thing, it's
___."* That sentence becomes the landing's promise, the through-line of the nav, and
the anchor every page ties back to. If you can't write it, the diagnosis isn't done.

Example (this repo): *"An agent is only as good as its harness — and the harness is
yours to engineer."* Concrete, true, sourced, and it organizes everything.

## The repeatable line
One phrase, ≤ ~12 words, that a reader would quote. It must be **true and sourced**,
not a slogan. Prefer a line the sources already gave you ("Most agent failures are
configuration failures") over one you invent.

## The controlled metaphor rule
A metaphor is powerful *after* the literal definition, never instead of it:
> the **harness** — everything around the model (rule files, tools, hooks) — is the
> car, the road, and the traffic laws.

Define the literal term, *then* extend the metaphor, and reuse the *same* metaphor
site-wide. Never introduce a second competing metaphor for the same concept.

## The 60-second aha
Within the first fold + first section, the reader should hit the payoff: the problem
named, the promise made, and one concrete proof (a stat, a diagram, a two-line
example). Front-load it; don't bury the point under prerequisites.

## The hard rules (this layer's guardrails)
Beauty is the servant, never the master:

- **Beauty never replaces precision** — a lovely page that's vague scores 0 on
  density.
- **Image never replaces fact** — every fact also lives in text ([llm-readability.md](llm-readability.md)).
- **Slogan never replaces contract** — the repeatable line doesn't excuse a missing
  input/output spec.
- **Visual never replaces structure** — a hero doesn't fix a bad nav.

If a signature element can't pass the [quality rubric](quality-rubric.md) on
density, source, and structure, it isn't iconic — it's marketing. Cut it.

## Where this plugs into the cycle
Set the thesis + repeatable line during **IA** (phase 2); realize the landing
promise, mental map, and primary flow during **write/visual** (phases 3–4); the
**critic** (phase 6) rejects any signature element that's pretty but hollow.
