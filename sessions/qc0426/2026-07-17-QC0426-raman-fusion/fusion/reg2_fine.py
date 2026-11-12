"""Fine zooms + color segmentation of v003 to identify leads, arms, and materials."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import witio

OUT = "/tmp/qc0426-fusion"
p = witio.read("/data/sharpelab/hera-data/raman-qc0426/06_3LGr-device.wip")
items = {d.caption: d for d in p.data}
d = items["Video Image--003"]
arr = np.asarray(d.array())
g = d.position_grid
g = np.asarray(g() if callable(g) else g)
X, Y = g[0], g[1]
rgb = arr[..., :3].astype(float) / 255.0
img = rgb.transpose(1, 0, 2)
xs = X[:, 0]; ys = Y[0, :]
origin = "upper" if ys[0] > ys[-1] else "lower"
extent = [xs[0], xs[-1], min(ys[0], ys[-1]), max(ys[0], ys[-1])]

# color masks
R, G, B = rgb[..., 0], rgb[..., 1], rgb[..., 2]
gold = (R > 0.75) & (G > 0.6) & (B < 0.55)
# mesa/stack blue: blue channel dominant over red
blue = (B > R + 0.08) & (B > 0.35) & ~gold

fig, axs = plt.subplots(1, 2, figsize=(20, 9), constrained_layout=True)
axs[0].imshow(np.clip(img*1.4,0,1), extent=extent, origin=origin)
seg = np.zeros(rgb.shape[:2] + (3,))
seg[gold] = [1, 0.85, 0.2]
seg[blue] = [0.2, 0.5, 1.0]
axs[1].imshow(seg.transpose(1, 0, 2), extent=extent, origin=origin)
for ax in axs:
    ax.set_xlim(-16, 14); ax.set_ylim(-14, 10)
    ax.set_xticks(np.arange(-16, 15, 2)); ax.set_yticks(np.arange(-14, 11, 2))
    ax.grid(True, color="w", alpha=0.3, lw=0.4)
    ax.set_aspect("equal")
axs[0].set_title("v003 mesa"); axs[1].set_title("gold / stack-blue segmentation")
fig.savefig(f"{OUT}/v003_seg.png", dpi=100, bbox_inches="tight")
plt.close(fig)

# fine zooms with 1-um grid
for xlim, ylim, name in [((-9, 0), (-12, -3), "botL"), ((-1, 10), (-14, -4), "botR"),
                         ((-13, -3), (0, 8), "topL"), ((-3, 11), (0, 8), "topR"),
                         ((-18, -5), (-9, -2), "leftlead")]:
    fig, ax = plt.subplots(figsize=(14, 12))
    ax.imshow(np.clip(img*1.5,0,1), extent=extent, origin=origin, aspect="equal")
    ax.set_xlim(*xlim); ax.set_ylim(*ylim)
    ax.set_xticks(np.arange(xlim[0], xlim[1] + 1, 1))
    ax.set_yticks(np.arange(ylim[0], ylim[1] + 1, 1))
    ax.grid(True, color="w", alpha=0.35, lw=0.5)
    ax.set_title(f"v003 — {name}")
    fig.savefig(f"{OUT}/v003_{name}.png", dpi=100, bbox_inches="tight")
    plt.close(fig)
print("done")
