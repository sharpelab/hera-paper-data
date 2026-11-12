#!/usr/bin/env python3
"""s7_spots.py — full-range mean spectra at named world-coordinate spots
(3x3 pixel average), map 003 unless noted. Sanity-check what each optical
object actually is.

Run: uv run --with numpy --with scipy --with matplotlib python s7_spots.py
Output: spots.png, spots_2d.png
"""
import numpy as np
from scipy.signal import medfilt
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

d = np.load("data.npz")
EXC = float(d["exc_nm"])

SPOTS = [  # (label, map, world x, world y)
    ("dark tall flake ctr", "003", -12071.0, 1293.0),
    ("dark tall flake low", "003", -12073.0, 1285.0),
    ("arc middle",          "003", -12055.0, 1288.0),
    ("arc lower",           "003", -12050.0, 1278.0),
    ("tombstone mid (003)", "003", -12040.0, 1280.0),
    ("tombstone mid (005)", "005", -12040.0, 1280.0),
    ("tombstone dark strip","005", -12034.0, 1278.0),
    ("white blob",          "003", -12073.0, 1265.5),
    ("substrate",           "003", -12030.0, 1297.0),
]

def spot_spec(k, x0, y0):
    cube = d[f"cube_{k}"]; wx, wy = d[f"wx_{k}"], d[f"wy_{k}"]
    dist = (wx - x0) ** 2 + (wy - y0) ** 2
    j, i = np.unravel_index(np.argmin(dist), dist.shape)
    j0, j1 = max(j - 1, 0), min(j + 2, cube.shape[0])
    i0, i1 = max(i - 1, 0), min(i + 2, cube.shape[1])
    spec = cube[j0:j1, i0:i1].mean(axis=(0, 1))
    return medfilt(spec, 3), (j, i)

fig, axes = plt.subplots(len(SPOTS), 1, figsize=(11, 2.1 * len(SPOTS)), sharex=True)
fig2, ax2 = plt.subplots(figsize=(9, 6))
for ax, (lab, k, x0, y0) in zip(axes, SPOTS):
    rs = 1e7 * (1 / EXC - 1 / d[f"lam_{k}"])
    spec, (j, i) = spot_spec(k, x0, y0)
    ax.plot(rs, spec, lw=0.7)
    ax.set_ylabel("cts", fontsize=7)
    ax.set_title(f"{lab} [map {k} px ({j},{i}) @ ({x0},{y0})]", fontsize=9)
    sel = (rs > 2500) & (rs < 2900)
    base = np.median(spec[(rs > 2450) & (rs < 2550)])
    ax2.plot(rs[sel], (spec[sel] - base), lw=1.2, label=lab)
axes[-1].set_xlabel("Raman shift (rel. 1/cm), 532.338 nm exc.")
fig.savefig("spots.png", dpi=130, bbox_inches="tight")
ax2.legend(fontsize=8); ax2.set_xlabel("Raman shift (1/cm)"); ax2.set_title("2D band at spots")
fig2.savefig("spots_2d.png", dpi=130, bbox_inches="tight")
print("done")
