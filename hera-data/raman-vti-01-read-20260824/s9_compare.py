#!/usr/bin/env python3
"""s9_compare.py — side-by-side world-frame comparison: contrast-stretched
video vs G_area of maps 003 and 005, with shared axes; plus edge profiles
along fixed y-cuts to quantify any inter-map offset.

Run: uv run --with numpy --with scipy --with matplotlib python s9_compare.py
Outputs: compare_worldframe.png, edge_profiles.png
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

d = np.load("data.npz")
m = np.load("metrics.npz")
v = np.load("video_004.npz")
img, corners = v["img"], v["corners"]

XL, XR, YB, YT = -12082, -12020, 1262, 1306

fig, axes = plt.subplots(1, 3, figsize=(20, 7), sharex=True, sharey=True)
lo, hi = np.percentile(img, [5, 70])
axes[0].imshow(np.clip((img - lo) / (hi - lo), 0, 1), cmap="gray",
               extent=[corners[0, 0], corners[1, 0], corners[2, 1], corners[0, 1]])
axes[0].set_title("video 004, contrast-stretched")
for ax, k in zip(axes[1:], ["003", "005"]):
    wx, wy = d[f"wx_{k}"], d[f"wy_{k}"]
    g = m[f"{k}_G_area"]
    im = ax.pcolormesh(wx, wy, g, shading="nearest", cmap="viridis",
                       vmin=0, vmax=5500)
    ax.set_title(f"map {k} G_area")
for ax in axes:
    ax.set_xlim(XL, XR); ax.set_ylim(YB, YT); ax.set_aspect("equal")
    for yy in (1272, 1280, 1288, 1296):
        ax.axhline(yy, color="r", alpha=0.3, lw=0.6)
fig.savefig("compare_worldframe.png", dpi=130, bbox_inches="tight")
plt.close(fig)

# edge profiles along y-cuts
from scipy.interpolate import RegularGridInterpolator
R = np.array([[0.99995996, 0.00894877], [-0.00894877, 0.99995996]])
S = np.diag([0.04913493, -0.04913493])
w0 = np.array([-12095.18847656, 1325.4732666])
Ainv = np.linalg.inv(R @ S)
sy, sx = img.shape
vint = RegularGridInterpolator((np.arange(sy) + 0.5, np.arange(sx) + 0.5),
                               img.astype(float), bounds_error=False)
def video_line(xs, y):
    pts = np.stack([xs - w0[0], np.full_like(xs, y) - w0[1]])
    mod = (Ainv @ pts).T
    return vint(np.stack([mod[:, 1], mod[:, 0]], axis=-1))

fig, axes = plt.subplots(4, 1, figsize=(12, 11), sharex=True)
xs = np.linspace(XL, XR, 700)
for ax, yy in zip(axes, (1272, 1280, 1288, 1296)):
    optv = video_line(xs, yy)
    ax.plot(xs, (optv - np.nanmedian(optv)) * 0.02, "k", lw=0.8,
            label="optical (scaled)")
    for k, col in [("003", "tab:blue"), ("005", "tab:orange")]:
        wx, wy = d[f"wx_{k}"], d[f"wy_{k}"]
        g = m[f"{k}_G_area"]
        # nearest row to this y
        jrow = np.argmin(np.abs(wy.mean(1) - yy))
        if abs(wy.mean(1)[jrow] - yy) < 1.0:
            ax.plot(wx[jrow], g[jrow] / 2000, col, lw=1.0, marker=".",
                    ms=2, label=f"G {k} (row @y={wy.mean(1)[jrow]:.1f})")
    ax.set_title(f"y = {yy} µm cut"); ax.legend(fontsize=7)
axes[-1].set_xlabel("stage x (µm)")
fig.savefig("edge_profiles.png", dpi=130, bbox_inches="tight")
print("done")
