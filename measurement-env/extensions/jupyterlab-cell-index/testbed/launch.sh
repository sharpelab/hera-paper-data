#!/usr/bin/env bash
# Launch the local verification JupyterLab for jupyterlab-cell-index.
#
# Standalone env (JupyterLab 4.5 + the vendored extension wheel only) rooted at
# this testbed dir, opening the 400-cell mixed notebook. Windowing is on by
# default in JupyterLab 4, so off-screen cells are detached from the DOM — the
# condition the index scheme must survive.
set -euo pipefail
cd "$(dirname "$0")"

if [[ ! -d .venv ]]; then
  echo "No .venv here. Build it first:"
  echo "  uv venv .venv --python 3.12"
  echo "  uv pip install --python .venv 'jupyterlab>=4.5,<4.6' ../../../vendor/jupyterlab_cell_index-0.2.0-py3-none-any.whl"
  exit 1
fi

if [[ ! -f long_notebook.ipynb ]]; then
  .venv/bin/python generate_notebook.py
fi

PORT="${1:-8899}"
exec .venv/bin/jupyter lab \
  --port "$PORT" \
  --ServerApp.root_dir="$PWD" \
  --ServerApp.token='' \
  long_notebook.ipynb
