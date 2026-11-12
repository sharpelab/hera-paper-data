#!/usr/bin/env python3
"""Step 1 aux — export the three video images with stage-µm extents, the
two fast-scan intensity images, and the two Raman maps' mean spectra.
Registration only; no stacking metrics here."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import witio

HERE = Path(__file__).parent
proj = witio.read(str(HERE / "inputs" / "vti-01.wip"))
items = {k: d for k, d in enumerate(proj.data)}


def tag_child(tag, *names):
    t = tag
    for n in names:
        t = next(c for c in t.children if c.name == n)
    return t


def transform_params(d):
    vp = tag_child(d.payload, "ViewPort3D")
    origin = tag_child(vp, "WorldOrigin").data
    scale = tag_child(vp, "Scale").data.reshape(3, 3)
    rot = tag_child(vp, "Rotation").data.reshape(3, 3)
    model = tag_child(vp, "ModelOrigin").data
    return model, origin, scale, rot


def px_to_world(model, origin, scale, rot, px, py):
    v = np.stack([px - model[0], py - model[1], np.zeros_like(px)], -1)
    return (rot @ (scale @ v[..., None]))[..., :2, 0] + origin[:2]


# bitmap -> its transformation item index
BM = {19: 18, 24: 23, 32: 31}
fig, axes = plt.subplots(1, 3, figsize=(19, 6))
for ax, (kb, kt) in zip(axes, BM.items()):
    img = np.asarray(items[kb].array())
    model, origin, scale, rot = transform_params(items[kt])
    ny, nx = img.shape[1], img.shape[0]
    # witio bitmap array is (W, H, 3)? report both and use corners
    W, H = img.shape[0], img.shape[1]
    corners = px_to_world(model, origin, scale, rot,
                          np.array([0.0, W, W, 0.0]), np.array([0.0, 0.0, H, H]))
    print(f"item {kb}: {items[kb].caption} array {img.shape} corners:\n{corners}")
    ext = [corners[:, 0].min(), corners[:, 0].max(),
           corners[:, 1].min(), corners[:, 1].max()]
    # display: transpose to (H, W, 3); y axis decreasing scale -> origin upper
    ax.imshow(img.transpose(1, 0, 2) if img.shape[0] > img.shape[1] else img,
              extent=ext, origin="upper")
    ax.set_title(items[kb].caption, fontsize=9)
    ax.set_xlabel("stage x (µm)")
axes[0].set_ylabel("stage y (µm)")
# overlay scan footprints on each
scans = {22: ("map A (532)", "w"), 27: ("map B (532)", "y"),
         30: ("006 fast", "c"), 35: ("008 fast", "m")}
for ax in axes:
    for ks, (lab, col) in scans.items():
        meta = items[ks].measurement_metadata
        meta = meta() if callable(meta) else meta
        cx, cy = meta["scan_center_x_um"], meta["scan_center_y_um"]
        sx, sy = meta["scan_span_x_um"], meta["scan_span_y_um"]
        ax.add_patch(plt.Rectangle((cx - sx / 2, cy - sy / 2), sx, sy,
                                   fill=False, ec=col, lw=1.2))
        ax.annotate(lab, (cx - sx / 2, cy + sy / 2), color=col, fontsize=7)
fig.tight_layout()
fig.savefig(HERE / "fig_video_images.png", dpi=130)
print("wrote fig_video_images.png")

# fast scans as total-intensity images + Raman map mean spectra
fig2, axes2 = plt.subplots(2, 2, figsize=(13, 9))
for ax, ks in zip(axes2[0], (30, 35)):
    d = items[ks]
    arr = np.asarray(d.array())  # (?, ?, nspec)
    tot = arr.sum(axis=-1)
    meta = d.measurement_metadata
    meta = meta() if callable(meta) else meta
    sx, sy = meta["scan_size_x_px"], meta["scan_size_y_px"]
    print(f"item {ks}: {d.caption} arr {arr.shape} scan_size ({sx},{sy})")
    if tot.shape == (sx, sy):
        tot = tot.T
    cx, cy = meta["scan_center_x_um"], meta["scan_center_y_um"]
    wx, wy = meta["scan_span_x_um"], meta["scan_span_y_um"]
    ax.imshow(tot, extent=[cx - wx/2, cx + wx/2, cy - wy/2, cy + wy/2],
              origin="lower", cmap="gray")
    ax.set_title(f"{d.caption} total counts")
for ax, ks in zip(axes2[1], (22, 27)):
    d = items[ks]
    arr = np.asarray(d.array())
    xa = d.x_axis()
    wn = np.asarray(xa[0] if isinstance(xa, tuple) else xa, float).ravel()
    mean = arr.reshape(-1, arr.shape[-1]).mean(axis=0)
    order = np.argsort(wn)
    ax.plot(wn[order], mean[order], lw=0.7)
    ax.set_title(f"{d.caption} mean spectrum")
    ax.set_xlabel("rel. cm$^{-1}$")
    print(f"item {ks}: wn {wn.min():.1f}..{wn.max():.1f}, "
          f"mean counts min {mean.min():.0f} max {mean.max():.0f}")
fig2.tight_layout()
fig2.savefig(HERE / "fig_firstlook.png", dpi=130)
print("wrote fig_firstlook.png")
