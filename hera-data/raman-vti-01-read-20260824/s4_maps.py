#!/usr/bin/env python3
"""s4_maps.py — metric maps for 003/005 with robust color scales; identify
graphene pixels and thickness terraces.

Run: uv run --with numpy --with matplotlib python s4_maps.py
Outputs: metric_maps.png, histograms.png
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

d = np.load("data.npz")
m = np.load("metrics.npz")
KEYS = ["003", "005"]

METRICS = ["G_area", "TD_area", "Si_area", "TD_fwhm", "TD_center",
           "G_fwhm", "G_center", "D_area", "TD_skew"]

fig, axes = plt.subplots(len(KEYS), len(METRICS), figsize=(4.2 * len(METRICS), 8))
for r, k in enumerate(KEYS):
    wx, wy = d[f"wx_{k}"], d[f"wy_{k}"]
    gmask = m[f"{k}_G_area"] > 300
    for c, met in enumerate(METRICS):
        a = m[f"{k}_{met}"].copy()
        if met in ("TD_fwhm", "TD_center", "G_fwhm", "G_center", "TD_skew"):
            a[~gmask] = np.nan
        lo, hi = np.nanpercentile(a, [2, 98])
        ax = axes[r, c]
        im = ax.pcolormesh(wx, wy, a, shading="nearest", cmap="viridis",
                           vmin=lo, vmax=hi)
        ax.set_aspect("equal")
        ax.set_title(f"{k}: {met}", fontsize=9)
        fig.colorbar(im, ax=ax, shrink=0.75)
fig.savefig("metric_maps.png", dpi=110, bbox_inches="tight")
plt.close(fig)

fig, axes = plt.subplots(2, 4, figsize=(18, 7))
for r, k in enumerate(KEYS):
    gmask = m[f"{k}_G_area"] > 300
    axes[r, 0].hist(m[f"{k}_G_area"].ravel(), bins=80)
    axes[r, 0].set_title(f"{k}: G_area (all px)"); axes[r, 0].set_yscale("log")
    axes[r, 1].hist(m[f"{k}_Si_area"][gmask].ravel(), bins=60)
    axes[r, 1].set_title(f"{k}: Si_area (graphene px)")
    axes[r, 2].hist(m[f"{k}_TD_fwhm"][gmask].ravel(), bins=60, range=(20, 120))
    axes[r, 2].set_title(f"{k}: 2D FWHM (graphene px)")
    ratio = m[f"{k}_TD_area"] / m[f"{k}_G_area"]
    axes[r, 3].hist(ratio[gmask].ravel(), bins=60, range=(0, 10))
    axes[r, 3].set_title(f"{k}: 2D/G area ratio (graphene px)")
fig.savefig("histograms.png", dpi=110, bbox_inches="tight")
plt.close(fig)
print("graphene px:", {k: int((m[f'{k}_G_area'] > 300).sum()) for k in KEYS})
