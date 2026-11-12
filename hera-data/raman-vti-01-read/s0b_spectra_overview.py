#!/usr/bin/env python3
"""Step 0b — what is in each scan: mean / max-pixel spectra per map, in rel. cm⁻¹
and in absolute nm (the CCD window is identical for all four scans), so the
1064 nm-labelled scans can be judged for content.

Writes figures/f0b_spectra_overview.png and prints band-presence facts.
Run: uv run --no-project --with numpy --with scipy --with matplotlib python3 s0b_spectra_overview.py
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parent
INT = HERE / "intermediates"
FIG = HERE / "figures"

fig, axes = plt.subplots(4, 2, figsize=(14, 13))
for row, k in enumerate((22, 27, 30, 35)):
    z = np.load(INT / f"map_{k}.npz")
    wn, cube, meta = z["wn"], z["cube"].astype(float), json.loads(str(z["meta"]))
    lam = meta["laser_wavelength_nm"]
    nm = 1.0 / (1.0 / lam - wn * 1e-7)          # absolute wavelength of each CCD pixel
    flat = cube.reshape(-1, cube.shape[-1])
    mean = flat.mean(axis=0)
    med = np.median(flat, axis=0)
    hi = flat[np.argmax(flat.max(axis=1))]
    # brightest pixel in the 2D window, if the axis is 532-referenced
    ax = axes[row, 0]
    ax.plot(wn, mean, label="mean"); ax.plot(wn, med, label="median"); ax.plot(wn, hi, label="max-count pixel", alpha=.6)
    ax.set_title(f"[{k}] {str(z['caption'])}  λ={lam:.1f} nm  t={meta['integration_time_s']*1e3:.0f} ms")
    ax.set_xlabel("rel. cm⁻¹ (as stored)"); ax.legend(fontsize=7); ax.set_yscale("log")
    ax = axes[row, 1]
    ax.plot(nm, mean); ax.plot(nm, med); ax.plot(nm, hi, alpha=.6)
    ax.set_xlabel("absolute nm (CCD window)"); ax.set_yscale("log")
    print(f"[{k}] λ={lam:.1f} nm  CCD window {nm.min():.1f}–{nm.max():.1f} nm  "
          f"counts min/median/max {flat.min():.0f}/{np.median(flat):.0f}/{flat.max():.0f}")
    if lam < 600:
        for name, lo, hi_ in (("Si 520", 505, 535), ("G", 1560, 1620), ("2D", 2600, 2760), ("D", 1320, 1380)):
            m = (wn > lo) & (wn < hi_)
            print(f"    {name:6s} mean-spec peak {mean[m].max():.0f} @ {wn[m][mean[m].argmax()]:.1f}  "
                  f"max over px {flat[:, m].max():.0f}")
    else:
        # where would 532-excited lines fall in this CCD window?
        for name, shift in (("Si520", 520.5), ("G", 1582), ("2D", 2690)):
            lam_line = 1.0 / (1.0 / 532.338 - shift * 1e-7)
            j = np.argmin(np.abs(nm - lam_line))
            m = slice(max(j - 8, 0), j + 8)
            print(f"    532-ref {name} would sit at {lam_line:.1f} nm (px {j}): mean {mean[m].max():.0f} "
                  f"vs local floor {np.median(mean[max(j-60,0):j-20]):.0f}")
fig.tight_layout(); fig.savefig(FIG / "f0b_spectra_overview.png", dpi=120)
