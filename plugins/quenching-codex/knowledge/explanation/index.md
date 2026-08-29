# `explanation/` — explanation

Understanding-oriented pages that explain how and why the product works, for the reader of
the documentation site (the Diátaxis **explanation** quadrant). Each page carries
`type: explanation`.

**Boundary:** a concept page here is part of the **published site** for product users.
Internal team understanding — mental models and learnings — belongs in the `concepts/` home. The
root glossary remains canonical there and publishes itself — [glossary.md](../glossary.md) is
inside `docs_dir`, so readers reach the source rather than a derived copy.

## How to organize

The repo decides which concept pages exist — the skeleton ships none. Standalone pages live
as `.md` files here; group by subject into subfolders with their own `index.md`.
