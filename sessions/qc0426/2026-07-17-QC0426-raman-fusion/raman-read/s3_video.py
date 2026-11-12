"""Render video images in the stage frame with scan outlines + Spot1."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import witio

OUT = "/tmp/qc0426-raman-read"
p = witio.read("/data/sharpelab/hera-data/raman-qc0426/06_3LGr-device.wip")

items = {d.caption: d for d in p.data}
boxes = {}
for cap, tag in [("Scan LA--002--Spec.Data 1", "scan002 (61x61, partial)"),
                 ("Scan LA--004--Spec.Data 1", "scan004 (51x51)")]:
    g = items[cap].position_grid
    g = np.asarray(g() if callable(g) else g)
    boxes[tag] = g

fig, axs = plt.subplots(1, 2, figsize=(18, 8), constrained_layout=True)
for ax, vcap in zip(axs, ["Video Image--000", "Video Image--003"]):
    d = items[vcap]
    arr = np.asarray(d.array())
    g = d.position_grid
    g = np.asarray(g() if callable(g) else g)
    print(vcap, "array", arr.shape, arr.dtype, "grid", g.shape)
    X, Y = g[0], g[1]
    if arr.ndim == 3 and arr.shape[-1] in (3, 4):
        rgb = arr[..., :3].astype(float)
        rgb /= rgb.max()
        # pcolormesh cannot do RGB with 2D coords pre-3.8? use quadmesh color trick:
        pc = ax.pcolormesh(X, Y, np.zeros(X.shape), shading="nearest")
        pc.set_array(None)
        pc.set_facecolor(rgb[:-0 or None, :, :].reshape(-1, 3) if rgb.shape[:2] == X.shape else rgb.reshape(-1, 3))
    else:
        ax.pcolormesh(X, Y, arr.astype(float), shading="nearest", cmap="gray")
    for (tag, g2), col in zip(boxes.items(), ["deepskyblue", "orange"]):
        xs = [g2[0, 0, 0], g2[0, -1, 0], g2[0, -1, -1], g2[0, 0, -1], g2[0, 0, 0]]
        ys = [g2[1, 0, 0], g2[1, -1, 0], g2[1, -1, -1], g2[1, 0, -1], g2[1, 0, 0]]
        ax.plot(xs, ys, color=col, lw=1.5, label=tag)
        # acquired part of scan002: b index < 21
        if "002" in tag:
            xs = [g2[0, 0, 0], g2[0, -1, 0], g2[0, -1, 20], g2[0, 0, 20], g2[0, 0, 0]]
            ys = [g2[1, 0, 0], g2[1, -1, 0], g2[1, -1, 20], g2[1, 0, 20], g2[1, 0, 0]]
            ax.plot(xs, ys, color=col, lw=1.2, ls="--", label=tag + " acquired")
    ax.plot([11.2], [-4.3], "r+", ms=14, mew=2, label="Spot1 (11.2, -4.3)")
    ax.set_title(vcap)
    ax.set_aspect("equal")
    ax.set_xlabel("stage x (µm)"); ax.set_ylabel("stage y (µm)")
    ax.legend(loc="lower right", fontsize=8)
    ax.set_xlim(-30, 30); ax.set_ylim(-25, 20)
fig.savefig(f"{OUT}/video_images_scanboxes.png", dpi=110)
print("written")
