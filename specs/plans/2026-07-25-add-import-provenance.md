---
slug: add-import-provenance
title: Add provenance and idempotent re-ingestion to quenching-docs-import
verification: per-section
---

# Add provenance and idempotent re-ingestion to quenching-docs-import

## Problem

Deferred from the docs-verification-layer plan — source_uri plus a content hash so a changed source is detectable and a re-import enriches instead of duplicating

_(v1 backlog task — tags: ['docs', 'import', 'provenance'])_

`quenching-docs-import` mints docs from an external source but records nothing that identifies
**which** source, at **which** version. Re-running it against a changed page cannot tell an enrich
from a duplicate, so the MERGE-never-clobber rule has no mechanical basis — it depends on the
model recognizing prose it wrote earlier.

The shape considered was a `source_uri` frontmatter key plus a content hash of the fetched unit, so
a later run can classify each unit as unchanged, changed, or new.

**Deferred deliberately, not forgotten.** The `docs-verification-layer` proposal ruled it out of
scope because the import path shows no evidence of having run on this repository, and optimizing an
unexercised path is speculation. Revisit once a real import has happened and the duplicate-vs-enrich
question is observed rather than predicted.
