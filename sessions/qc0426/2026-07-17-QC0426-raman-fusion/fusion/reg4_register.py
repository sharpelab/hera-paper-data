"""Final registration: frame-offset check, spine/arm junctions, annotated artifact."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from scipy import ndimage
import witio

OUT = "/tmp/qc0426-fusion"
p = witio.read("/data/sharpelab/hera-data/raman-qc0426/06_3LGr-device.wip")
items = {d.caption: d for d in p.data}

def load(cap):
    d = items[cap]
    arr = np.asarray(d.array())
    g = d.position_grid
    g = np.asarray(g() if callable(g) else g)
    return arr[..., :3].astype(float) / 255.0, g[0], g[1]

rgb0, X0, Y0 = load("Video Image--000")
rgb3, X3, Y3 = load("Video Image--003")

# --- (a) absolute-frame feature offset between the two video images ---
# sample both on a common absolute grid over the mesa
gx = np.arange(-12, 12, 0.05)
gy = np.arange(-12, 8, 0.05)
def sample(rgb, X, Y, gx, gy):
    xs, ys = X[:, 0], Y[0, :]
    ix = np.clip(np.searchsorted(xs, gx), 0, len(xs) - 1)
    # ys descending
    iy = np.clip(len(ys) - 1 - np.searchsorted(ys[::-1], gy), 0, len(ys) - 1)
    im = rgb[..., 2][np.ix_(ix, iy)]  # blue channel
    return im
im0 = sample(rgb0, X0, Y0, gx, gy)
im3 = sample(rgb3, X3, Y3, gx, gy)
im0 -= im0.mean(); im3 -= im3.mean()
corr = np.fft.irfft2(np.fft.rfft2(im0) * np.conj(np.fft.rfft2(im3)))
pk = np.unravel_index(np.argmax(corr), corr.shape)
sh = [(s if s <= n // 2 else s - n) for s, n in zip(pk, corr.shape)]
print(f"v000 vs v003 absolute-frame feature offset: dx={sh[0]*0.05:+.2f} um, dy={sh[1]*0.05:+.2f} um")

# --- (b) masks on v003 ---
R, G, B = rgb3[..., 0], rgb3[..., 1], rgb3[..., 2]
gold = (R > 0.75) & (G > 0.6) & (B < 0.55)
blue = (B > R + 0.08) & (B > 0.35) & ~gold
xs, ys = X3[:, 0], Y3[0, :]

def runs_at_y(ycut, xmin=-9, xmax=12):
    j = np.argmin(np.abs(ys - ycut))
    row = blue[:, j] & (xs >= xmin) & (xs <= xmax)
    lab, n = ndimage.label(row)
    out = []
    for k in range(1, n + 1):
        sel = xs[lab == k]
        if np.ptp(sel) > 0.15:
            out.append((0.5 * (sel.min() + sel.max()), np.ptp(sel)))
    return out

# spine centerline: for x columns, find blue run centers in y, pick widest run (spine ~1.5um)
spine_pts = []
for xc in np.arange(-5.0, 8.6, 0.25):
    i = np.argmin(np.abs(xs - xc))
    col = blue[i, :]
    lab, n = ndimage.label(col)
    best = None
    for k in range(1, n + 1):
        sel = ys[lab == k]
        w = np.ptp(sel)
        yc = 0.5 * (sel.min() + sel.max())
        # spine y roughly -0.3*x - 0.8, within +-2
        if abs(yc - (-0.30 * xc - 0.8)) < 2.0 and w > 0.9:
            if best is None or w > best[1]:
                best = (yc, w)
    if best:
        spine_pts.append((xc, best[0], best[1]))
spine_pts = np.array(spine_pts)
cf = np.polyfit(spine_pts[:, 0], spine_pts[:, 1], 1)
print(f"spine centerline: y = {cf[0]:+.3f} x {cf[1]:+.3f}  (n={len(spine_pts)}, "
      f"rms={np.std(spine_pts[:,1]-np.polyval(cf, spine_pts[:,0])):.2f} um), "
      f"median thickness {np.median(spine_pts[:,2]):.2f} um")

# arm lines: fit tip + run centers at several cuts, intersect with spine
def arm_junctions(cuts, tips, tol=0.9):
    juncs = []
    for xt, yt in tips:
        pts = [(xt, yt)]
        cexp = xt
        for ycut in cuts:
            rr = runs_at_y(ycut, xmax=13)
            cands = [c for c, w in rr if abs(c - cexp) < tol and w < 1.9]
            if cands:
                c = min(cands, key=lambda v: abs(v - cexp))
                pts.append((c, ycut))
                cexp = c
        pts = np.array(pts)
        a = np.polyfit(pts[:, 1], pts[:, 0], 1)  # x = a0*y + a1
        xj = (a[0] * cf[1] + a[1]) / (1 - a[0] * cf[0])
        yj = np.polyval(cf, xj)
        juncs.append((xj, yj))
    return juncs

top_tips = [(-1.90, 6.38), (-0.57, 5.80), (1.20, 5.37), (3.37, 4.80),
            (5.39, 4.03), (7.36, 3.46), (9.6, 2.6)]
tj = arm_junctions([3.5, 2.5, 1.5, 0.5], top_tips)
bot_tips = [(-7.34, -6.30), (-5.22, -7.07), (-3.50, -7.69), (-1.43, -8.36),
            (1.14, -9.22), (3.40, -10.04), (5.72, -10.90), (8.38, -12.06)]
bj = arm_junctions([-5.2, -5.8, -6.4, -7.0], bot_tips)

# T1 and T7 arm fits are unreliable (tip census point off-arm / matching failure);
# override with geometric estimates: T1 arm parallel to T2's, T7 = right-lead landing arm.
tj[0] = (-4.3, np.polyval(cf, -4.3))
tj[6] = (6.9, np.polyval(cf, 6.9))
print("\nT junctions on spine (label: tip -> junction; T1/T7 geometric estimates):")
for i, (t, j) in enumerate(zip(top_tips, tj), 1):
    print(f"  T{i}: tip ({t[0]:+.1f},{t[1]:+.1f}) -> junction ({j[0]:+.2f},{j[1]:+.2f})")
print("B junctions on spine (fan L->R = B1..B8):")
for i, (t, j) in enumerate(zip(bot_tips, bj), 1):
    print(f"  B{i}: tip ({t[0]:+.1f},{t[1]:+.1f}) -> junction ({j[0]:+.2f},{j[1]:+.2f})")

np.savez(f"{OUT}/registration.npz", spine=cf, tj=np.array(tj), bj=np.array(bj),
         top_tips=np.array(top_tips), bot_tips=np.array(bot_tips))

# --- (c) annotated artifact ---
img = np.clip(rgb3 * 1.45, 0, 1).transpose(1, 0, 2)
origin = "upper" if ys[0] > ys[-1] else "lower"
extent = [xs[0], xs[-1], min(ys[0], ys[-1]), max(ys[0], ys[-1])]
fig, ax = plt.subplots(figsize=(17, 13))
ax.imshow(img, extent=extent, origin=origin, aspect="equal")

# Raman regions (result.md)
regions = {
    "R1 (spine, ABA strong)": ((-7, -4.5), 15, 5.0, "lime"),
    "R2 (upper arms, ABA strong)": ((-9.5, 0.5), 17.5, 6.0, "cyan"),
    "R3 (lower arms, ABA strong)": ((-8.5, -11.5), 17, 7.0, "orange"),
}
for name, ((x0, y0), w, h, col) in regions.items():
    ax.add_patch(Rectangle((x0, y0), w, h, fill=False, ec=col, lw=2.2, ls="-"))
    ax.text(x0 + 0.2, y0 + h - 0.55, name, color=col, fontsize=11, weight="bold")
# scan windows
ax.add_patch(Rectangle((-9.5, -12.5), 19.8, 19.8, fill=False, ec="w", lw=1.2, ls=":"))
ax.text(-9.3, 7.6, "scan004 window", color="w", fontsize=10)
ax.add_patch(Rectangle((-11.4, 2.2), 19.9, 6.6, fill=False, ec="violet", lw=1.4, ls="--"))
ax.text(-11.2, 9.0, "scan002 acquired stripe (R5, defocused)", color="violet", fontsize=10)
ax.plot([11.2], [-4.3], "r+", ms=16, mew=2.5)
ax.text(11.5, -4.1, "Spot1 (substrate)", color="red", fontsize=10)

# contact labels
for i, (t, j) in enumerate(zip(top_tips, tj), 1):
    ax.annotate(f"T{i}", xy=(j[0], j[1]), xytext=(t[0] + 0.3, t[1] + 0.9),
                color="yellow", fontsize=13, weight="bold",
                arrowprops=dict(arrowstyle="-", color="yellow", lw=0.8, alpha=0.6))
for i, (t, j) in enumerate(zip(bot_tips, bj), 1):
    ax.annotate(f"B{i}", xy=(j[0], j[1]), xytext=(t[0] - 0.2, t[1] - 1.6),
                color="yellow", fontsize=13, weight="bold",
                arrowprops=dict(arrowstyle="-", color="yellow", lw=0.8, alpha=0.6))
ax.text(-13.5, 4.7, "BG lead\n(graphite tab)", color="w", fontsize=10, ha="center")
ax.text(-14.5, -7.6, "wide left lead\n(B-indexing fork:\nB1 end-contact or gate lead)",
        color="w", fontsize=9, ha="center")

# channel segments on spine
xx = np.linspace(tj[2][0], tj[3][0], 20)
ax.plot(xx, np.polyval(cf, xx) + 0.55, color="red", lw=5, alpha=0.9)
ax.text(np.mean(xx) - 1.2, np.polyval(cf, np.mean(xx)) + 1.0, "sr1 = T3-T4",
        color="red", fontsize=12, weight="bold")
xx = np.linspace(bj[3][0], bj[4][0], 20)
ax.plot(xx, np.polyval(cf, xx) - 0.55, color="magenta", lw=5, alpha=0.9)
ax.text(np.mean(xx) - 1.4, np.polyval(cf, np.mean(xx)) - 1.5, "sr2 = B4-B5",
        color="magenta", fontsize=12, weight="bold")
# sr3 Hall cross-section
ax.plot([tj[4][0], bj[5][0]], [tj[4][1], bj[5][1]], color="deepskyblue", lw=3, alpha=0.9)
ax.text(tj[4][0] + 0.3, tj[4][1] + 0.4, "sr3 = T5-B6 (Hall)", color="deepskyblue",
        fontsize=11, weight="bold")
# source/drain
ax.annotate("source T2", xy=(tj[1][0], tj[1][1]), xytext=(tj[1][0] - 4.4, tj[1][1] + 1.6),
            color="orangered", fontsize=11, weight="bold",
            arrowprops=dict(arrowstyle="->", color="orangered", lw=1.2))
ax.annotate("drain B7", xy=(bj[6][0], bj[6][1]), xytext=(bj[6][0] + 2.6, bj[6][1] - 1.2),
            color="orangered", fontsize=11, weight="bold",
            arrowprops=dict(arrowstyle="->", color="orangered", lw=1.2))

ax.set_xlim(-17, 15); ax.set_ylim(-14.5, 10.5)
ax.set_xlabel("stage x (um)"); ax.set_ylabel("stage y (um)")
ax.set_title("QC0426 registration — video v003 (map-time), Raman regions, transport channels\n"
             "T1-T7 top arc L->R (6 fan + right lead); B1-B8 bottom fan L->R (primary indexing)")
fig.savefig(f"{OUT}/registration_artifact.png", dpi=110, bbox_inches="tight")
print("\nartifact written")
