#!/usr/bin/env python3
"""Step 0c — full-resolution crops of the flake from each in-file video image
(stage µm frame), with the scan footprints outlined. For the imagery-based
stage inference and the thickness-contrast read.

Writes figures/f0c_crop_<k>.png and figures/f0c_crops.png.
Run: uv run --no-project --with numpy --with matplotlib python3 s0c_video_crops.py
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parent
INT, FIG = HERE / "intermediates", HERE / "figures"
CROP = (-12082, -12018, 1262, 1306)   # x0, x1, y0, y1 stage µm
maps = {k: np.load(INT / f"map_{k}.npz") for k in (22, 27, 30, 35)}
cols = {22: "C1", 27: "C3", 30: "C2", 35: "C4"}

fig, axes = plt.subplots(1, 3, figsize=(21, 6))
for ax, k in zip(axes, (19, 24, 32)):
    z = np.load(INT / f"video_{k}.npz")
    rgb, ext, meta = z["rgb"], z["extent"], json.loads(str(z["meta"]))
    x0, x1, y0, y1 = ext
    nx, ny = rgb.shape[1], rgb.shape[0]
    xs = np.linspace(x0, x1, nx); ys = np.linspace(y0, y1, ny)
    mx = (xs >= CROP[0]) & (xs <= CROP[1]); my = (ys >= CROP[2]) & (ys <= CROP[3])
    sub = rgb[np.ix_(my, mx)]
    # contrast stretch for thickness read
    sub = np.clip((sub.astype(float) - 60) * 1.6, 0, 255).astype(np.uint8)
    ax.imshow(sub, extent=[xs[mx].min(), xs[mx].max(), ys[my].min(), ys[my].max()],
              origin="lower" if ys[my][0] < ys[my][-1] else "upper")
    for km, zz in maps.items():
        X, Y = zz["X"], zz["Y"]
        ax.plot([X.min(), X.max(), X.max(), X.min(), X.min()],
                [Y.min(), Y.min(), Y.max(), Y.max(), Y.min()], cols[km], lw=1.2,
                label=f"[{km}] {json.loads(str(zz['meta']))['laser_wavelength_nm']:.0f} nm {meta and ''}")
    ax.set_title(f"[{k}] {str(z['caption'])} {meta['trace_creation_time_local'][11:19]}")
    ax.set_xlabel("stage x (µm)"); ax.set_ylabel("stage y (µm)"); ax.legend(fontsize=7, loc="lower left")
    ax.grid(alpha=.2)
    f2, a2 = plt.subplots(figsize=(12, 8.5))
    a2.imshow(sub, extent=[xs[mx].min(), xs[mx].max(), ys[my].min(), ys[my].max()],
              origin="lower" if ys[my][0] < ys[my][-1] else "upper")
    a2.set_title(f"[{k}] {str(z['caption'])} {meta['trace_creation_time_local']}")
    a2.set_xlabel("stage x (µm)"); a2.set_ylabel("stage y (µm)"); a2.grid(alpha=.25)
    f2.tight_layout(); f2.savefig(FIG / f"f0c_crop_{k}.png", dpi=110); plt.close(f2)
fig.tight_layout(); fig.savefig(FIG / "f0c_crops.png", dpi=110)
