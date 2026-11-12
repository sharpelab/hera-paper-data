# Answer-key analysis — `after-density-cut`

Provenance for the figures in `../figures/`.

## `render_fans.py`

Self-contained reproduction of Qingrui's analysis convention (the device's
`analysis.ipynb`, cells 24-26 / 55 / 62-65) **without** the `sweep` package: it
reads `data.tsv.gz` + `metadata.json` directly, re-forms `Rxx = sr{1,2,3}_X /
(sr0_X / sr0_gain)`, computes `(n, D)` from the gate-line via the capacitance
helper (`t_bg = 12 nm`, `t_bgSiO2 = 0`, `t_tg = 1.3·t_bg`, `κ_hBN = 3`), and
renders the density cut + the Landau fans.

Run it from anywhere (it points `SRC` at the source measurement dir):
```bash
python3 render_fans.py
```

## Figures produced

| File | Run | Cut role | What |
|---|---|---|---|
| `ana_79_density-cut_D0p25.png` | 79 | **latest result** (pre-cut) | 0-field `Rxx(n)` density cut at D = 0.25 — the perception-layer target (`reading.md`) |
| `ana_27_fan_D0.png` | 27 | context (allowlisted) | the D = 0 Landau fan established earlier in the campaign |
| `ana_80_fan_D0p25.png` | 80 | **answer key** (post-cut) | Landau fan at D = 0.25 (the density cut, fielded) |
| `ana_81_fan_D1.png` | 81 | **answer key** | Landau fan at D = 1 |
| `ana_82_fan_Dm1.png` | 82 | **answer key** | Landau fan at D = −1 (cleanest LL diagonals) |
| `ana_83_fan_Dm0p25.png` | 83 | **answer key** | Landau fan at D = −0.25 |
| `ana_84_fan_Dm0p5.png` | 84 | **answer key** | Landau fan at D = −0.5 — **interrupted** (79/161 B-steps) |

## Caveats

- The post-cut fans (80-84) are **not** in the fixture `data/` (they are the
  answer key); `render_fans.py` reads them from the source measurement dir to
  generate the answer-key figures at build time.
- `Rxy` (`sr3`) is plotted as `Rxx` (`sr1`) in the fan renders for a single
  consistent panel; the device's notebook separates `r_xx = ['sr1','sr2']` /
  `r_xy = ['sr3']`. The longitudinal fan structure is the point here.
- The fans reshape row-major as `(n_slow=B, n_fast=gate-line)`; interrupted fans
  are reshaped over their complete B-rows only.
