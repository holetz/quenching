# Vendored libraries & upstream attribution

`okf-visualize.py` produces a **self-contained, offline** HTML diagram by inlining the
two libraries below directly into the output file (in place of the CDN `<script src>`
tags the upstream viewer used). Both are MIT-licensed; their copyright banners are kept
verbatim at the top of the minified files. This directory ships the pinned copies.

## Cytoscape.js — 3.30.2 (MIT)

- Source: <https://github.com/cytoscape/cytoscape.js> · <https://cdnjs.com/libraries/cytoscape>
- Copyright (c) 2016–2024, The Cytoscape Consortium.
- File: `cytoscape.min.js` (full license text is embedded in the file header).

## marked — 12.0.2 (MIT)

- Source: <https://github.com/markedjs/marked>
- Copyright (c) 2011–2024, Christopher Jeffrey. (MIT Licensed)
- Copyright (c) 2018+, MarkedJS (<https://github.com/markedjs/>)
- File: `marked.min.js` (license banner embedded in the file header).

## The MIT License (applies to both libraries above)

```
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## Upstream attribution — the viewer this is adapted from

`okf-visualize.py` and the `viewer/` shell (`viz.html`, `viz.css`, `viz.js`) are
**adapted from** the OKF reference implementation's `visualize` command —
`okf/src/reference_agent/viewer/` in
**[GoogleCloudPlatform/knowledge-catalog](https://github.com/GoogleCloudPlatform/knowledge-catalog)**,
licensed **Apache License 2.0**.

Adaptations in this plugin:

- the upstream `OKFDocument` parser is replaced by this plugin's own zero-dependency
  frontmatter parser and the exact link resolver `okf-validate.py` uses (so the graph's
  edges are the same within-bundle link graph the validator models);
- the CDN `<script src>` tags are replaced by the inlined vendored libraries above for an
  offline, air-gapped output file;
- the node palette is keyed on the OKF v0.1 `type` vocabulary;
- only Cytoscape's built-in layouts are used (no vendored layout extension).

The Apache-2.0 license requires preserving attribution and noting changes; this file and
the header comments in `okf-visualize.py` / `viz.*` satisfy that. A copy of the upstream
license is at <https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/LICENSE.md>.
