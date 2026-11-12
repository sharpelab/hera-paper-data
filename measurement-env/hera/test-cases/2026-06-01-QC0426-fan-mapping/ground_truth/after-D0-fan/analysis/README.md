# Answer-key analysis — `after-D0-fan`

Provenance for the figures in `../figures/`.

## `render_fans.py`

Self-contained reproduction of Qingrui's analysis convention (the device's
`analysis.ipynb`, cells 24-26 / 55 / 62-65) **without** the `sweep` package: it
reads `data.tsv.gz` + `metadata.json` directly, re-forms `Rxx = sr{1,2,3}_X /
(sr0_X / sr0_gain)`, computes `(n, D)` from the gate-line via the capacitance
helper (`t_bg = 12 nm`, `t_bgSiO2 = 0`, `t_tg = 1.3·t_bg`, `κ_hBN = 3`), and
renders the served fan plus the "introduce the Si gate" answer key. It reuses the
same `calc_nD` / `load` / `Rxx` / `render_fan` convention as the
`after-density-cut` renderer, with two added map renderers (`render_tgsi_map`,
`render_vsi_map`) for the 2D Si-gate maps.

Run it from anywhere (it points `SRC` at the source measurement dir):
```bash
python3 render_fans.py
```

## Figures produced

| File | Run | Cut role | What |
|---|---|---|---|
| `ana_27_fan_D0.png` | 27 | **latest result** (allowlisted) | the D = 0 Landau fan to 8 T — the perception-layer target (`reading.md`); washed out at ~1.2 K |
| `ana_28_tgsi-map.png` | 28 | **answer key** (post-cut) | TG-Si gate map `Rxx(V_TG, V_Si)` at B = 8 T, BG = −4 V — the literal "try Si gate" move; CNP near-vertical (Si is a weak lever) |
| `ana_31_fan_D0_Si60.png` | 31 | **answer key** | Si-screened D = 0 fan, Si = +60 V, to 13 T — cleaner LL structure than run 27 |
| `ana_33_vsi-n-map.png` | 33 | **answer key** | VSi-n map `Rxx(n, V_Si)` at D = 0 (negative-Si branch) — the Si-gate leverage on neutrality |

## Caveats

- The post-cut runs (28, 31, 33) are **not** in the fixture `data/` (they are the
  answer key); `render_fans.py` reads them from the source measurement dir at
  build time to generate the answer-key figures.
- `Rxx` is plotted from `sr1` for a single consistent panel; the device's notebook
  separates `r_xx = ['sr1','sr2']` / `r_xy = ['sr3']`. The longitudinal structure
  is the point here. (Run 33 logged only `sr0`/`sr1`, so `sr1` is the only choice.)
- The TG-Si map (run 28) has no back-gate column (BG fixed at −4 V) and steps the
  Si gate, so it is rendered in raw gate volts (V_TG vs V_Si), the natural axes for
  that map. The VSi-n map (run 33) computes `n` from the TG/BG gate-line only
  (SiO₂ term zeroed), so the Si-gate's own carrier contribution is not folded into
  the n-axis — the apparent slight CNP shift with V_Si reflects exactly that
  un-accounted Si doping.
- The fans reshape row-major as `(n_slow = B, n_fast = gate-line)`; the maps as
  `(slow = V_Si, fast = gate-line/TG)`. Interrupted sweeps are reshaped over their
  complete slow-rows only.
