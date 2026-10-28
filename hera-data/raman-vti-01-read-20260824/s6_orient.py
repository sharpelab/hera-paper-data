#!/usr/bin/env python3
"""s6_orient.py — settle scan-raster orientation absolutely by registering
Raman Si-attenuation maps against the stage-registered video image.

For each flip hypothesis (none, flipX, flipY, flipXY) of each map's stored
raster, sample the video gray value at every Raman pixel's world coordinate
and correlate with Si_area (thicker carbon -> darker optical AND lower Si).
Positive correlation (bright optical <-> strong Si) = correct orientation.

Run: uv run --with numpy --with scipy --with matplotlib python s6_orient.py
Outputs: orient_results.txt, orient_overlay.png
"""
import numpy as np
from scipy.interpolate import RegularGridInterpolator
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

d = np.load("data.npz")
m = np.load("metrics.npz")
v = np.load("video_004.npz")
img, corners = v["img"], v["corners"]  # corners: (0,0),(sx,0),(sx,sy),(0,sy) in world

# Build video interpolator in *video model* coords, then map world->model.
# world = R S (model - m0) + w0  ->  model = S^-1 R^-1 (world - w0) + m0
# Reconstruct R, S from the stored transform (video 004: id 91).
R = np.array([[0.99995996, 0.00894877], [-0.00894877, 0.99995996]])
S = np.diag([0.04913493, -0.04913493])
w0 = np.array([-12095.18847656, 1325.4732666])
m0 = np.array([0.0, 0.0])
Ainv = np.linalg.inv(R @ S)

sy, sx = img.shape
interp = RegularGridInterpolator((np.arange(sy) + 0.5, np.arange(sx) + 0.5),
                                 img.astype(float), bounds_error=False,
                                 fill_value=np.nan)

def video_at(wx, wy):
    pts = np.stack([wx.ravel() - w0[0], wy.ravel() - w0[1]])
    model = (Ainv @ pts).T + m0
    return interp(np.stack([model[:, 1], model[:, 0]], axis=-1)).reshape(wx.shape)

lines = []
best = {}
for k in ["003", "005"]:
    wx, wy = d[f"wx_{k}"], d[f"wy_{k}"]
    si = m[f"{k}_Si_area"]
    opt = video_at(wx, wy)  # gray sampled at assumed world coords of stored (j,i)
    res = {}
    for fx in (False, True):
        for fy in (False, True):
            si_f = si[:, ::-1] if fx else si
            si_f = si_f[::-1] if fy else si_f
            ok = np.isfinite(opt) & np.isfinite(si_f)
            r = np.corrcoef(opt[ok], si_f[ok])[0, 1]
            res[(fx, fy)] = r
            lines.append(f"map {k} flipX={fx} flipY={fy}: r(optical, Si_area) = {r:.3f}")
    bk = max(res, key=lambda kk: res[kk])
    best[k] = bk
    lines.append(f"map {k} BEST: flipX={bk[0]} flipY={bk[1]} (r={res[bk]:.3f})")
txt = "\n".join(lines)
open("orient_results.txt", "w").write(txt + "\n")
print(txt)

# overlay: video + best-flip G_area contours
fig, axes = plt.subplots(1, 2, figsize=(16, 7))
for ax, k in zip(axes, ["003", "005"]):
    fx, fy = best[k]
    g = m[f"{k}_G_area"]
    g = g[:, ::-1] if fx else g
    g = g[::-1] if fy else g
    wx, wy = d[f"wx_{k}"], d[f"wy_{k}"]
    ax.imshow(img, cmap="gray",
              extent=[corners[0, 0], corners[1, 0], corners[2, 1], corners[0, 1]])
    ax.contour(wx, wy, g, levels=[2000], colors="r", linewidths=1)
    si = m[f"{k}_Si_area"]
    si = si[:, ::-1] if fx else si
    si = si[::-1] if fy else si
    ax.contour(wx, wy, si, levels=[8000], colors="c", linewidths=1)
    ax.set_xlim(wx.min() - 8, wx.max() + 8); ax.set_ylim(wy.min() - 8, wy.max() + 8)
    ax.set_title(f"map {k} best flipX={fx} flipY={fy} (red G=2000, cyan Si=8000)")
fig.savefig("orient_overlay.png", dpi=130, bbox_inches="tight")
print("wrote orient_overlay.png")
