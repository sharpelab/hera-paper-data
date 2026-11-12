# nb — Jupyter notebook navigator

Read and slice notebooks without dragging multi-MB base64 outputs into context.
Source at `src/tools/nb.py`; installed as `nb` console script via `uv sync`.
Stdlib only. Cell indices are 0-based.

## When to use

Reach for `nb` whenever the user points at a `.ipynb` — especially measurement
notebooks (often hundreds of cells, MBs of embedded plot PNGs). Reading the
file directly works for tiny notebooks but blows context on real ones.

## Workflow

Almost always: **stats → sections → summary → cells → extract** (only if you
actually need pixels).

```bash
# 0. Six-line overview: cell counts, empties, total source lines, output bytes.
#    Cheap orientation before you decide to summary/sections.
uv run nb stats <file.ipynb>

# 1. One line per cell. Code-cell preview surfaces add_comment("...") strings
#    when present (strong intent signal — measurement sessions often annotate
#    each sweep this way); else the first non-import non-comment line.
#    Markdown previews are first non-blank line. Optional range argument
#    (same syntax as `cells`) slices the notebook — preferred over piping to
#    head/sed for long notebooks.
uv run nb summary <file.ipynb>
uv run nb summary <file.ipynb> 30-80
uv run nb summary <file.ipynb> 5,12,30-

# 2. Markdown-header TOC. Best way to navigate a long measurement notebook —
#    running sessions are typically organized by `##` sections that mark
#    phases of the run.
uv run nb sections <file.ipynb>

# 3. Read specific cells. Outputs OFF by default — pass --outputs to include
#    them (images come back as one-line placeholders, not base64).
uv run nb cells <file.ipynb> 5
uv run nb cells <file.ipynb> 5-10
uv run nb cells <file.ipynb> 5,8,12
uv run nb cells <file.ipynb> 5-10,15-     # trailing-open
uv run nb cells <file.ipynb> 5 --outputs

# 4. Find by regex.
uv run nb grep <file.ipynb> "plot_sweep"
uv run nb grep <file.ipynb> -i --type code "TODO"

# 5. Extract images to disk. Only when you actually need to see the picture.
#    Files are named cell005_out0.png and printed to stdout.
uv run nb extract <file.ipynb> 5 --out /tmp/nb/
uv run nb extract <file.ipynb> 5,15,21 --out /tmp/nb/
```

## Defaults and gotchas

- **0-indexed cells.** Matches `nb['cells'][i]` in the raw JSON.
- **`cells` outputs default off.** Don't pass `--outputs` unless the user asked
  about a specific output or you genuinely need to see what ran.
- **`extract` is the only path to actual image bytes.** `cells --outputs` shows
  placeholders; never try to pull base64 directly out of the notebook JSON.
- **Range syntax**: `N`, `N-M`, `N-` (to end), `N,M,...`, mixed. Out-of-range
  indices silently clamp.

## Don't

- Don't `cat`/`Read` notebooks directly — even "small" measurement notebooks
  embed plot PNGs that explode context.
- Don't ask for `--outputs` on a wide range. Prefer reading source first,
  then re-running `cells <one-cell> --outputs` only when needed.
- Don't extract images speculatively. Look at the placeholder dims/bytes from
  `cells --outputs` first; extract only if you need pixels.
