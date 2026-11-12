# Answer-key analysis — `after-0T-gatemap`

Provenance for the figures in `../figures/`.

## `render_maps.py`

Self-contained reproduction of Qingrui's analysis convention (the device's
`analysis.ipynb`, cells 24-26 / 55 / 62-65) **without** the `sweep` package: it
reads `data.tsv.gz` + `metadata.json` directly, re-forms `Rxx = sr{1,2,3}_X /
(sr0_X / sr0_gain)`, and renders the two gate maps plus the D = 0 Landau fans.
The convention block and `render_fan()` are identical to the sibling
`after-density-cut/analysis/render_fans.py`; the new piece is `render_gatemap()`,
which reshapes a `megasweep` (flat slow/fast setpoint lists — slow = `k_bg`,
197 pts; fast = `DC_bias`, 281 pts) over the recorded gate columns and overlays
the CNP D-line fit `Vtg = −1.3·Vbg + 0.06`.

Run it from anywhere (it points `SRC` at the source measurement dir):
```bash
python3 render_maps.py
```

## Figures produced

| File | Run | Cut role | What |
|---|---|---|---|
| `ana_26_gatemap_3T.png` | 26 | **latest result** (pre-cut) | finite-field B = 3 T `Rxx(Vtg, Vbg)` gate map — the perception-layer target (`reading.md`) |
| `ana_25_gatemap_0T.png` | 25 | context (allowlisted) | the complete 0 T TG-BG gate map where the −1.3 CNP slope was fit |
| `ana_27_fan_D0.png` | 27 | **answer key** (post-cut) | the D = 0 B-n Landau fan, 0 → 8 T — the next move |
| `ana_31_fan_D0_13T.png` | 31 | **answer key** (post-cut) | the D = 0 fan extended to 13 T (also sets Si = +60 V — the next frontier) |

## Caveats

- The post-cut fans (27, 31) are **not** in the fixture `data/` (they are the
  answer key); `render_maps.py` reads them from the source measurement dir to
  generate the answer-key figures at build time. The two gate maps (25, 26) *are*
  in the served allowlist.
- The gate maps are plotted in raw gate volts `(Vtg = DC_bias, Vbg = k_bg)` — the
  faithful "TG-BG map" view — with the CNP diagonal overlaid; `(n, D)` follow from
  the same `calc_nD` affine transform if a density/field view is wanted.
- `Rxx` is plotted from `sr1` (longitudinal) for a single consistent panel; the
  device's notebook separates `r_xx = ['sr1','sr2']` / `r_xy = ['sr3']`. At the
  VTI's ~1.2 K the fans stay CNP-dominated with only faint, washed-out
  Landau-level striations — faithful to the run (too warm for a definitive
  ABA/ABC call).
- Run 24 (the aborted first 0 T map, ~1.2k/55k points) is allowlisted but not
  rendered; run 25 is the complete 0 T map used for context.
