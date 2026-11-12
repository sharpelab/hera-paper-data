# Local verification testbed

Standalone harness for eyeballing `jupyterlab-cell-index` on a long, windowed
notebook. Nothing here ships — the `.venv/` and generated `*.ipynb` are
gitignored; only `generate_notebook.py`, `launch.sh`, and this README are
tracked.

## Launch

```bash
./launch.sh            # builds the notebook if missing, serves on :8899, token off
# or pick a port:
./launch.sh 8900
```

Then open `long_notebook.ipynb` (it's passed on the command line, so it opens
automatically). The browser is on this machine.

## (Re)building the env from scratch

```bash
uv venv .venv --python 3.12
uv pip install --python .venv 'jupyterlab>=4.5,<4.6' \
  ../../../vendor/jupyterlab_cell_index-0.1.0-py3-none-any.whl
.venv/bin/python generate_notebook.py        # 400 cells, 300 code / 100 markdown
```

`jupyter labextension list` should show `jupyterlab-cell-index v0.1.0 enabled OK`.

## What to check

The gutter badge is a small muted number at the left of every cell.

- **Index correctness, freshly opened**: each cell embeds its own original index
  in its text ("cell N"). On open, the gutter number must equal that N for
  every cell, code and markdown alike, 0-based.
- **Correctness while scrolled (windowing)**: scroll deep into the notebook.
  JupyterLab detaches off-screen cells from the DOM; the badge must still read
  the true model index (e.g. cell 312 shows 312), not a DOM-relative count.
  Jump around with the scrollbar and Ctrl+End / Ctrl+Home.
- **Insert / delete mid-notebook**: select a cell partway down, press `a`/`b` to
  insert above/below, or `dd` to delete. Everything below must renumber
  immediately. (The embedded "cell N" labels stay put — only the gutter moves,
  which is the point: the badge follows the model, not the text.)
- **Performance**: scrolling should be perfectly smooth (the extension does zero
  work on scroll — the number is a data attribute the CSS renders). Insert/edit
  triggers one O(n) attribute pass; with 400 cells it should be imperceptible.
  Try a much larger notebook if you want to push it:
  `.venv/bin/python generate_notebook.py -n 2000 -o big.ipynb`.

## How it deploys to the rigs

The vendored wheel (`../../../vendor/jupyterlab_cell_index-*.whl`) is wired into
the project `pyproject.toml` as a dependency via `[tool.uv.sources]`. Rigs pick
it up at their next explicit maintenance-window `uv sync` — no Node toolchain
needed at install time, the wheel is prebuilt.
