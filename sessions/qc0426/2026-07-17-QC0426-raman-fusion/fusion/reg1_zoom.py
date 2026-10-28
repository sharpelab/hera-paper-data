"""Full-res zooms of both video images in the stage frame, for arm counting."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import witio

OUT = "/tmp/qc0426-fusion"
p = witio.read("/data/sharpelab/hera-data/raman-qc0426/06_3LGr-device.wip")
items = {d.caption: d for d in p.data}

for vcap, tag in [("Video Image--000", "v000"), ("Video Image--003", "v003")]:
    d = items[vcap]
    arr = np.asarray(d.array())          # (2240, 1680, 3): axis0 = x, axis1 = y
    g = d.position_grid
    g = np.asarray(g() if callable(g) else g)
    X, Y = g[0], g[1]                    # same shape as arr[:, :, 0]
    rgb = np.clip(arr[..., :3].astype(float) / 255.0 * 1.4, 0, 1)
    # transpose to rows = y, cols = x for imshow
    img = rgb.transpose(1, 0, 2)
    xs = X[:, 0]; ys = Y[0, :]
    print(vcap, "x", xs[0], "->", xs[-1], "y", ys[0], "->", ys[-1])
    origin = "upper" if ys[0] > ys[-1] else "lower"
    extent = [xs[0], xs[-1], min(ys[0], ys[-1]), max(ys[0], ys[-1])]
    for xlim, ylim, name in [((-30, 30), (-25, 20), "full"),
                             ((-16, 14), (-14, 10), "mesa"),
                             ((-13, 13), (-3, 10), "top"),
                             ((-13, 13), (-14, 1), "bottom")]:
        fig, ax = plt.subplots(figsize=(16, 12))
        ax.imshow(img, extent=extent, origin=origin, aspect="equal")
        ax.set_xlim(*xlim); ax.set_ylim(*ylim)
        ax.set_xticks(np.arange(np.ceil(xlim[0]), xlim[1] + 1, 2))
        ax.set_yticks(np.arange(np.ceil(ylim[0]), ylim[1] + 1, 2))
        ax.grid(True, color="w", alpha=0.3, lw=0.5)
        ax.set_xlabel("stage x (um)"); ax.set_ylabel("stage y (um)")
        ax.set_title(f"{vcap} — {name}")
        fig.savefig(f"{OUT}/{tag}_{name}.png", dpi=110, bbox_inches="tight")
        plt.close(fig)
print("done")
