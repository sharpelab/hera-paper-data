"""Arm/lead census: blue-arm crossings on cut lines, gold finger tip positions."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import ndimage
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
R, G, B = rgb[..., 0], rgb[..., 1], rgb[..., 2]
gold = (R > 0.75) & (G > 0.6) & (B < 0.55)
blue = (B > R + 0.08) & (B > 0.35) & ~gold
xs = X[:, 0]; ys = Y[0, :]

def cut_segments(mask, ycut, xmin, xmax):
    j = np.argmin(np.abs(ys - ycut))
    row = mask[:, j] & (xs >= xmin) & (xs <= xmax)
    lab, n = ndimage.label(row)
    segs = []
    for k in range(1, n + 1):
        sel = xs[lab == k]
        if np.ptp(sel) > 0.15:  # >150 nm wide
            segs.append((sel.min(), sel.max(), 0.5 * (sel.min() + sel.max())))
    return segs

print("=== blue-arm crossings ===")
for ycut in [3.0, 2.5, 2.0]:
    segs = cut_segments(blue, ycut, -9, 12)
    print(f"y={ycut:+.1f}: {len(segs)} segs:", [f"{c:.1f}" for a, b, c in segs])
for ycut in [-5.8, -6.5, -7.0]:
    segs = cut_segments(blue, ycut, -9, 12)
    print(f"y={ycut:+.1f}: {len(segs)} segs:", [f"{c:.1f}" for a, b, c in segs])

# gold connected components and their tips near the mesa
lab, n = ndimage.label(gold)
print("\n=== gold components (area > 2000 px) ===")
tips_top, tips_bot = [], []
for k in range(1, n + 1):
    m = lab == k
    npx = m.sum()
    if npx < 2000:
        continue
    gx, gy = X[m], Y[m]
    # tip toward the mesa: for components mostly above y=0 -> min-y point; below -> max-y
    cy = gy.mean()
    if cy > 0:
        i = np.argmin(gy)
        tips_top.append((gx[i], gy[i], npx))
    else:
        i = np.argmax(gy)
        tips_bot.append((gx[i], gy[i], npx))
tips_top.sort(); tips_bot.sort()
print("top-side tips (x, y, area):")
for t in tips_top: print(f"  ({t[0]:+.2f}, {t[1]:+.2f})  area={t[2]}")
print("bottom-side tips (x, y, area):")
for t in tips_bot: print(f"  ({t[0]:+.2f}, {t[1]:+.2f})  area={t[2]}")
