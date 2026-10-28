# jupyterlab-cell-index

A frontend-only JupyterLab 4 extension that renders two badges in the
notebook's left gutter:

- the cell's **stable 0-based model index** — the same index the lab's `nb`
  tool uses (`nb['cells'][i]`, counting all cells including markdown, in model
  order)
- the cell's **landing time**, read from `metadata.hera.appended_at` (stamped
  by `nb-collab` at append)

## Why

During live HERA/IRIS measurement sessions the agent cites notebook cells by
0-based index, but JupyterLab shows no cell numbers — the operator had to count
by hand to find "cell 18". This puts the number in the UI.

The landing time makes the notebook a review-at-a-glance surface for a human
catching up mid-session: the last few cells show *when* each step landed, so
"what has it been doing" is answerable without leaving the page.

## How it works

A small TypeScript plugin stamps `data-cell-index="<i>"` onto every cell node,
where `<i>` is the cell's position in `notebook.widgets` (one widget per model
cell, in model order). A CSS rule renders that attribute in the gutter via
`content: attr(data-cell-index)`.

The index is computed from the **model/widget order in JS**, never from DOM
order. This is what makes it correct under JupyterLab 4's windowed rendering
(`windowingMode: "full"`), where off-screen cells are detached from the DOM —
a CSS counter or any DOM-order scheme would miscount on scroll. Scrolling does
no work in this extension at all; only structural changes (insert / delete /
move) and cell-metadata changes trigger a re-stamp.

The time badge (`data-cell-time`) works the same way: **render-only** — the
extension reads `metadata.hera.appended_at` (ISO-8601 UTC) and never writes
metadata. It renders in the viewer's local timezone as `HH:MM`, date-prefixed
(`MM-DD HH:MM`) when the stamp is not from the current day. Cells without the
stamp (template cells, operator-typed cells) get no time badge. A per-cell
`metadataChanged` listener makes the badge appear live when `nb-collab` stamps
a freshly appended cell.

## Backlog

- Execution-time badge: executed cells carry kernel start/end times under
  `cell.metadata.execution` (`recordTiming` is a server-served default via
  `jupyter-config/`), and `nb-collab` stamps `metadata.hera.executed_at`.
  In practice execution follows append almost immediately, so a second badge
  doesn't earn its gutter space yet.

## Build

Requires Node + npm (build-time only; the shipped wheel needs neither).

```bash
jlpm install          # or: npm install
jlpm build:prod       # builds the federated labextension bundle
python -m build       # produces a py3-none-any wheel with the prebuilt assets
```

The resulting wheel installs cleanly into any environment with JupyterLab
4.5; JupyterLab discovers the prebuilt extension at launch with no Node
toolchain present.
