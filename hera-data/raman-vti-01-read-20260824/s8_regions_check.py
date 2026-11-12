#!/usr/bin/env python3
"""s8_regions_check.py — region-averaged spectra: hBN 1366 check + optical
contrast per region + Si attenuation ratios.

Regions:
  A  arc sheet          = 003 graphene px OUTSIDE tombstone bbox
  T  tombstone graphene = 005 graphene px
  S  dark strip         = 005 px with x > -12035.5, G_area < 500, optical dark
  BG substrate          = 003 px with G_area < 200 outside everything

Run: uv run --with numpy --with scipy --with matplotlib python s8_regions_check.py
Outputs: region_avg_spectra.png, hbn_zoom.png, region_stats.txt
"""
import numpy as np
from scipy.signal import medfilt
from scipy.interpolate import RegularGridInterpolator
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

d = np.load("data.npz")
m = np.load("metrics.npz")
EXC = float(d["exc_nm"])
v = np.load("video_004.npz")
img = v["img"]

R = np.array([[0.99995996, 0.00894877], [-0.00894877, 0.99995996]])
S = np.diag([0.04913493, -0.04913493])
w0 = np.array([-12095.18847656, 1325.4732666])
Ainv = np.linalg.inv(R @ S)
sy, sx = img.shape
vinterp = RegularGridInterpolator((np.arange(sy) + 0.5, np.arange(sx) + 0.5),
                                  img.astype(float), bounds_error=False,
                                  fill_value=np.nan)
def video_at(wx, wy):
    pts = np.stack([wx.ravel() - w0[0], wy.ravel() - w0[1]])
    model = (Ainv @ pts).T
    return vinterp(np.stack([model[:, 1], model[:, 0]], axis=-1)).reshape(wx.shape)

def despike_cube(c):
    return np.apply_along_axis(lambda s: medfilt(s, 3), 2, c)

regions = {}
# tombstone bbox in world coords (from 005 G map)
TB = dict(x0=-12047, x1=-12030, y0=1264, y1=1297)

wx3, wy3 = d["wx_003"], d["wy_003"]
g3 = m["003_G_area"]
in_tb3 = (wx3 > TB["x0"]) & (wx3 < TB["x1"]) & (wy3 > TB["y0"]) & (wy3 < TB["y1"])
regions["A_arc"] = ("003", (g3 > 2000) & ~in_tb3)
regions["BG_substrate"] = ("003", (g3 < 200) & ~in_tb3 & (m["003_Si_area"] > 12000))

wx5, wy5 = d["wx_005"], d["wy_005"]
g5 = m["005_G_area"]
regions["T_tombstone"] = ("005", g5 > 2000)
regions["S_darkstrip"] = ("005", (g5 < 500) & (wx5 > -12035.5) & (wx5 < -12030.5)
                          & (wy5 > 1267) & (wy5 < 1290))

stats, avspecs = [], {}
for name, (k, mask) in regions.items():
    cube = d[f"cube_{k}"]
    wx, wy = d[f"wx_{k}"], d[f"wy_{k}"]
    spec = cube[mask].mean(axis=0)
    spec = medfilt(spec, 3)
    avspecs[name] = (k, spec, mask.sum())
    opt = video_at(wx, wy)
    si = m[f"{k}_Si_area"]
    stats.append(f"{name}: n={mask.sum()}  optical_gray={np.nanmean(opt[mask]):.1f}"
                 f"  Si_area={np.nanmedian(si[mask]):.0f}  G_area={np.nanmedian(m[f'{k}_G_area'][mask]):.0f}")

bg_si = np.nanmedian(m["003_Si_area"][regions["BG_substrate"][1]])
stats.append(f"substrate Si_area ref (003): {bg_si:.0f}")
for name, (k, mask) in regions.items():
    si = np.nanmedian(m[f"{k}_Si_area"][mask])
    stats.append(f"{name}: Si ratio vs substrate = {si / bg_si:.3f}")

open("region_stats.txt", "w").write("\n".join(stats) + "\n")
print("\n".join(stats))

fig, axes = plt.subplots(2, 1, figsize=(12, 9))
for name, (k, spec, n) in avspecs.items():
    rs = 1e7 * (1 / EXC - 1 / d[f"lam_{k}"])
    axes[0].plot(rs, spec, lw=0.9, label=f"{name} (n={n})")
    sel = (rs > 1250) & (rs < 1500)
    base = np.median(spec[(rs > 1250) & (rs < 1300)])
    axes[1].plot(rs[sel], spec[sel] - base, lw=1.2, label=name)
axes[0].set_yscale("log"); axes[0].legend(fontsize=8)
axes[0].set_xlabel("Raman shift (1/cm)")
axes[1].axvline(1366, color="k", alpha=0.3)
axes[1].set_xlabel("Raman shift (1/cm)"); axes[1].legend(fontsize=8)
axes[1].set_title("zoom: D/hBN window (1366 = hBN E2g)")
fig.savefig("region_avg_spectra.png", dpi=130, bbox_inches="tight")
print("wrote region_avg_spectra.png")
