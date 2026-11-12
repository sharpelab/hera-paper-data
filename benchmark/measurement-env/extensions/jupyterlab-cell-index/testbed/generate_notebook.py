#!/usr/bin/env python3
"""Generate a long, mixed code/markdown notebook for exercising jupyterlab-cell-index.

The notebook is long enough (default 400 cells) that JupyterLab's windowed
renderer (windowingMode: "full") detaches off-screen cells from the DOM — the
condition under which a DOM-order index scheme would miscount.

Each cell embeds its *original* 0-based index in its own source, so the gutter
badge can be checked by eye: on a freshly-opened notebook the gutter number must
equal the "cell N" written inside the cell. After you insert or delete cells,
the gutter renumbers to live model order while the embedded labels stay put —
that divergence is exactly what you're verifying (the badge follows the model,
not the text).

Most cells also carry a `metadata.hera.appended_at` stamp (what nb-collab
writes at append) so the time badge can be checked by eye: stamps count back
seven minutes per cell from generation time (400 cells span ~2 days), so the
tail of the notebook shows recent HH:MM times and the head falls on prior
days — exercising the `MM-DD HH:MM` date-prefixed form. Every 5th cell is
left unstamped to verify the no-badge case.

nbformat 4.5 with explicit cell IDs, matching the repo's template convention.
"""
from __future__ import annotations

import argparse
import json
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path


def _cell_id() -> str:
    # Deterministic-ish unique IDs without Date/random dependence at import time.
    return uuid.uuid4().hex[:8]


def hera_metadata(i: int, n: int) -> dict:
    """`metadata.hera` for cell i of n, or {} for the unstamped case."""
    if i % 5 == 0:
        return {}
    stamp = datetime.now(timezone.utc) - timedelta(minutes=7 * (n - 1 - i))
    return {"hera": {"v": "v0", "appended_at": stamp.isoformat()}}


def make_code_cell(i: int, n: int) -> dict:
    # Vary height so windowing has uneven cells to virtualize.
    body_lines = [f"# cell {i} (code)"]
    for k in range((i % 5) + 1):
        body_lines.append(f"x{k} = {i} * {k} + {k}")
    body_lines.append(f"print('this is cell', {i})")
    return {
        "cell_type": "code",
        "id": _cell_id(),
        "metadata": hera_metadata(i, n),
        "execution_count": None,
        "outputs": [],
        "source": "\n".join(body_lines),
    }


def make_markdown_cell(i: int, n: int) -> dict:
    level = "#" * ((i % 3) + 2)
    return {
        "cell_type": "markdown",
        "id": _cell_id(),
        "metadata": hera_metadata(i, n),
        "source": (
            f"{level} cell {i} (markdown)\n\n"
            f"Gutter badge for this cell should read **{i}** when freshly opened."
        ),
    }


def build(n: int) -> dict:
    cells = []
    for i in range(n):
        # Roughly 1 markdown for every 3 code cells, interleaved.
        if i % 4 == 0:
            cells.append(make_markdown_cell(i, n))
        else:
            cells.append(make_code_cell(i, n))
    return {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {"name": "python"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("-n", "--cells", type=int, default=400, help="number of cells (default 400)")
    p.add_argument(
        "-o",
        "--out",
        default=str(Path(__file__).parent / "long_notebook.ipynb"),
        help="output path",
    )
    args = p.parse_args()
    nb = build(args.cells)
    out = Path(args.out)
    out.write_text(json.dumps(nb, indent=1), encoding="utf-8")
    n_md = sum(1 for c in nb["cells"] if c["cell_type"] == "markdown")
    n_code = len(nb["cells"]) - n_md
    print(f"wrote {out}  ({len(nb['cells'])} cells: {n_code} code, {n_md} markdown)")


if __name__ == "__main__":
    main()
