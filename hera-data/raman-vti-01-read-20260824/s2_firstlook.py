#!/usr/bin/env python3
"""s2_firstlook.py — mean spectra per map + basic band maps; resolves the
006/008 excitation-tag anomaly and the DataFieldInverted orientation by
cross-checking overlapping maps.

Run: uv run --with numpy --with matplotlib --with scipy python s2_firstlook.py
Outputs: firstlook_spectra.png, firstlook_maps.png, orientation_check.txt
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

d = np.load("data.npz")
EXC = float(d["exc_nm"])
KEYS = ["003", "005", "006", "008"]

def shift_axis(lam):
    return 1e7 * (1 / EXC - 1 / lam)

fig, axes = plt.subplots(2, 1, figsize=(11, 8), sharex=True)
for k in KEYS:
    cube, lam = d[f"cube_{k}"], d[f"lam_{k}"]
    rs = shift_axis(lam)
    mean = cube.mean(axis=(0, 1))
    axes[0].plot(rs, mean, label=f"map {k} (mean)", lw=0.8)
    p90 = np.percentile(cube.reshape(-1, cube.shape[2]), 90, axis=0)
    axes[1].plot(rs, p90, label=f"map {k} (p90)", lw=0.8)
axes[0].set_ylabel("mean CCD cts"); axes[1].set_ylabel("p90 CCD cts")
axes[1].set_xlabel("Raman shift (rel. 1/cm), assuming 532.338 nm excitation")
for ax in axes:
    ax.legend(fontsize=8)
    for x in (520.7, 1366, 1582, 2700):
        ax.axvline(x, color="k", alpha=0.15, lw=0.7)
axes[0].set_yscale("log")
fig.savefig("firstlook_spectra.png", dpi=140, bbox_inches="tight")
plt.close(fig)

def band(cube, rs, lo, hi, blo, bhi):
    """Integrated counts in [lo,hi] minus linear baseline from flanks."""
    sel = (rs >= lo) & (rs <= hi)
    bg1 = (rs >= blo) & (rs < lo)
    bg2 = (rs > hi) & (rs <= bhi)
    base = 0.5 * (cube[:, :, bg1].mean(2) + cube[:, :, bg2].mean(2))
    return cube[:, :, sel].sum(2) - base * sel.sum()

fig, axes = plt.subplots(4, 3, figsize=(15, 14))
bands = [("G 1540-1620", 1540, 1620, 1480, 1680),
         ("2D 2620-2780", 2620, 2780, 2540, 2860),
         ("Si 500-540", 500, 540, 440, 600)]
for r, k in enumerate(KEYS):
    cube, lam = d[f"cube_{k}"], d[f"lam_{k}"]
    rs = shift_axis(lam)
    wx, wy = d[f"wx_{k}"], d[f"wy_{k}"]
    for c, (title, lo, hi, blo, bhi) in enumerate(bands):
        m = band(cube, rs, lo, hi, blo, bhi)
        ax = axes[r, c]
        im = ax.pcolormesh(wx, wy, m, shading="nearest", cmap="viridis")
        ax.set_aspect("equal")
        ax.set_title(f"map {k}: {title}", fontsize=9)
        fig.colorbar(im, ax=ax, shrink=0.8)
fig.savefig("firstlook_maps.png", dpi=120, bbox_inches="tight")
plt.close(fig)

# ---- orientation check: compare G-band maps of 003 vs 005 in overlap ----
# Sample map 003's G image at map 005's pixel world coords, for stored order
# vs Y-flipped order of each; report correlations.
from scipy.interpolate import RegularGridInterpolator

def gmap(k):
    cube, lam = d[f"cube_{k}"], d[f"lam_{k}"]
    rs = shift_axis(lam)
    return band(cube, rs, 1540, 1620, 1480, 1680)

lines = []
for ka, kb in [("003", "005"), ("003", "006"), ("003", "008"), ("005", "006")]:
    ga, gb = gmap(ka), gmap(kb)
    wxa, wya = d[f"wx_{ka}"], d[f"wy_{ka}"]
    wxb, wyb = d[f"wx_{kb}"], d[f"wy_{kb}"]
    for flip_a in (False, True):
        for flip_b in (False, True):
            ga_ = ga[::-1] if flip_a else ga
            gb_ = gb[::-1] if flip_b else gb
            # build interpolator on map a's approx rectilinear grid (use row/col means)
            xs, ys = wxa.mean(0), wya.mean(1)
            order = np.argsort(ys)
            interp = RegularGridInterpolator(
                (ys[order], np.sort(xs)),
                ga_[order][:, np.argsort(xs)],
                bounds_error=False, fill_value=np.nan)
            samp = interp(np.stack([wyb, wxb], axis=-1))
            ok = np.isfinite(samp)
            if ok.sum() < 50:
                continue
            cc = np.corrcoef(samp[ok].ravel(), gb_[ok].ravel())[0, 1]
            lines.append(f"{ka}(flip={flip_a}) vs {kb}(flip={flip_b}): r={cc:.3f} n={ok.sum()}")
txt = "\n".join(lines)
open("orientation_check.txt", "w").write(txt + "\n")
print(txt)
