#!/usr/bin/env python3
"""s10_calib.py — inter-map spectral calibration check using in-band anchors:
the Rayleigh line (0 rel. 1/cm) and the Si 520.7 1/cm phonon, fitted per map
(and per cluster subset) on averaged spectra.

Run: uv run --with numpy --with scipy python s10_calib.py
Output: calib_check.txt
"""
import numpy as np
from scipy.optimize import least_squares

d = np.load("data.npz")
m = np.load("metrics.npz")
EXC = float(d["exc_nm"])

def fit_peak(rs, spec, lo, hi):
    sel = (rs > lo) & (rs < hi)
    x, y = rs[sel], spec[sel]
    base = y.min()
    p0 = [y.max() - base, x[np.argmax(y)], 8.0, base]
    def lor(p):
        return p[0] / (1 + ((x - p[1]) / (p[2] / 2)) ** 2) + p[3] - y
    r = least_squares(lor, p0)
    return r.x[1], r.x[2]

lines = []
for k in ["003", "005"]:
    rs = 1e7 * (1 / EXC - 1 / d[f"lam_{k}"])
    cube = d[f"cube_{k}"]
    g = m[f"{k}_G_area"]
    sub = cube[(g < 200)].mean(axis=0)        # substrate: strong Si, Rayleigh
    ray_c, ray_w = fit_peak(rs, sub, -60, 60)
    si_c, si_w = fit_peak(rs, sub, 490, 550)
    lines.append(f"map {k} substrate: Rayleigh {ray_c:+.2f} (w {ray_w:.1f}), "
                 f"Si {si_c:.2f} (w {si_w:.1f})")
    gr = cube[(g > 3000) & (g < 6500)].mean(axis=0)
    si_c2, _ = fit_peak(rs, gr, 490, 550)
    gc, gw = fit_peak(rs, gr, 1540, 1620)
    lines.append(f"map {k} graphene-avg: Si {si_c2:.2f}, G {gc:.2f} (w {gw:.1f})")
print("\n".join(lines))
open("calib_check.txt", "w").write("\n".join(lines) + "\n")
