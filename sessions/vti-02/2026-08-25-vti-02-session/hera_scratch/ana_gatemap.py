"""Gate map -> CNP-line extraction and (n, D) calibration.

recipe: device-init/cnp-and-dline-calibration.md, steps 1-4.

Per-row ridge extraction with the recipe's three guards (edge-clipped rows,
competing maxima via continuity, railed/glitch rows via robust refit), then a
per-ridge linear fit, then the ratio / offsets / closure check.
"""
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks

from hera.analysis import fan_grids, resistance_grids, summarize_run, open_run

BASE = "C:/Users/DGG/VTI_local_data/zack/20260825-vti-02/data"
SCRATCH = "C:/Users/DGG/VTI_local_data/zack/20260825-vti-02/hera_scratch"
RID = int(sys.argv[1]) if len(sys.argv) > 1 else 4
SENS1 = 5e-4

r = open_run(f"{BASE}/{RID}")
print(summarize_run(r))
fg = fan_grids(r)
rg = resistance_grids(fg, channels=["sr1"])
def grid(name):
    """fg.data is (nrows*nfast, ncols); reshape one column to (nrows, nfast)."""
    return fg.data[:, fg.cols.index(name)].reshape(fg.nrows, fg.nfast)


R = np.abs(rg.R["sr1"])                     # (nrows, nfast)
Vtg = grid("k_2400_tg_volt")                # (nrows, nfast)
Vbg = grid("k_2400_bg_volt")[:, 0]          # (nrows,)
Itg = grid("k_2400_tg_curr")
Ibg = grid("k_2400_bg_curr")
Vxx = grid("sr1_X")
nrows, nfast = R.shape
tg = Vtg[0]
print(f"grid {nrows} rows x {nfast} fast;  V_bg {Vbg[0]:+.3f}..{Vbg[-1]:+.3f};  "
      f"V_tg {tg[0]:+.3f}..{tg[-1]:+.3f}")
print(f"R_xx  {R.min():.1f} .. {R.max():.1f} ohm")

# --- health: railing and leakage ---
R_CEIL = SENS1 / np.abs(rg.current).mean()
load = np.abs(Vxx) / SENS1
railed_rows = np.where(load.max(axis=1) > 0.90)[0]
print(f"sr1 ceiling ~{R_CEIL:.0f} ohm;  max load {load.max():.3f};  "
      f"railed rows: {railed_rows.tolist() if len(railed_rows) else 'none'}")
# common-mode vs differential gate current
# Decompose the gate currents. Pickup appears on both gates together (the SUM
# carries it); a TG<->BG leak is equal and opposite (the DIFFERENCE carries it).
# Compare the scatter of each after removing the per-gate baseline.
dtg = Itg - np.median(Itg)
dbg = Ibg - np.median(Ibg)
s_sum, s_dif = (dtg + dbg).std(), (dtg - dbg).std()
print(f"gate current: |I_tg| max {np.abs(Itg).max()*1e12:.0f} pA, "
      f"|I_bg| max {np.abs(Ibg).max()*1e12:.0f} pA")
print(f"  scatter: common-mode (I_tg+I_bg) {s_sum*1e12:.0f} pA vs "
      f"differential (I_tg-I_bg) {s_dif*1e12:.0f} pA  ->  "
      f"{'PICKUP dominates' if s_sum > s_dif else 'DIFFERENTIAL dominates - possible TG-BG leak'}")
# the real leakage trend: per-row median I_tg vs V_tg, baseline-subtracted
tg_trend = np.median(Itg, axis=0) - np.median(Itg[:, tg < 0.4])
print(f"  I_tg trend vs V_tg (row-median, baseline-subtracted): "
      f"{tg_trend[tg < 0.4].max()*1e12:+.0f} pA below 0.4 V, "
      f"{tg_trend[tg > 0.9].max()*1e12:+.0f} pA above 0.9 V")

# ---------------- Step 1: per-row ridge extraction ----------------
SMOOTH = 2.0
PROM_FRAC = 0.04
EDGE = 2          # rows whose peak sits within EDGE points of the window edge


def row_peaks(y):
    ysm = gaussian_filter1d(y, SMOOTH)
    idx, props = find_peaks(ysm, prominence=PROM_FRAC * np.ptp(ysm))
    out = []
    for i, p in zip(idx, props["prominences"]):
        if 0 < i < len(ysm) - 1:
            y0, y1, y2 = ysm[i - 1], ysm[i], ysm[i + 1]
            d = y0 - 2 * y1 + y2
            shift = 0.5 * (y0 - y2) / d if d else 0.0
        else:
            shift = 0.0
        out.append(dict(i=i, v=tg[i] + shift * (tg[1] - tg[0]), r=ysm[i], prom=p,
                        edge=(i < EDGE or i > len(ysm) - 1 - EDGE)))
    return out


rows = [row_peaks(R[k]) for k in range(nrows)]
print("\nper-row peaks (V_tg of each ridge; * = edge-clipped, excluded from fit)")
for k in range(nrows):
    tags = "  ".join(f"{p['v']:+.4f}({p['r']:.0f}Ω){'*' if p['edge'] else ''}" for p in rows[k])
    print(f"  V_bg={Vbg[k]:+.4f}  {tags if tags else '(no peak)'}")

# ---------------- track ridges by continuity ----------------
# Walk OUTWARD from the row nearest V_bg = 0 (where Gate C gives both
# intercepts independently), matching each ridge to the nearest peak to its
# own previous-row position. No prior slope is imposed — seeding on a predicted
# slope is what made the first version splice ridge B's peaks onto ridge A.
# Mutual exclusion: within a row, two ridges may not claim the same peak.
SEEDS = {"A": -0.2152, "B": +0.1121}     # V_tg at V_bg = 0, from Gate C
TOL = 0.10                     # V, max row-to-row movement of a ridge

k0 = int(np.argmin(np.abs(Vbg)))
pos = {}
for name, v0 in SEEDS.items():
    cands = [p for p in rows[k0] if abs(p["v"] - v0) < TOL]
    pos[name] = min(cands, key=lambda p: abs(p["v"] - v0))["v"] if cands else v0
print(f"\nseed row k={k0} (V_bg={Vbg[k0]:+.4f}): "
      + ", ".join(f"{n}={pos[n]:+.4f}" for n in SEEDS))

pts = {n: [] for n in SEEDS}
for direction in (+1, -1):
    cur = dict(pos)
    k = k0
    while 0 <= k < nrows:
        claimed = set()
        # order by how confident we are: closest match first
        order = sorted(SEEDS, key=lambda n: min(
            [abs(p["v"] - cur[n]) for p in rows[k] if not p["edge"]] or [9e9]))
        for name in order:
            cands = [p for p in rows[k]
                     if not p["edge"] and abs(p["v"] - cur[name]) < TOL
                     and p["i"] not in claimed]
            if cands:
                p = min(cands, key=lambda p: abs(p["v"] - cur[name]))
                claimed.add(p["i"])
                cur[name] = p["v"]
                if not (direction == -1 and k == k0):   # don't double-count seed row
                    pts[name].append((Vbg[k], p["v"], p["r"], k))
        k += direction

tracks = {}
for name in SEEDS:
    arr = np.array(sorted(pts[name])) if pts[name] else np.empty((0, 4))
    tracks[name] = arr
    if len(arr):
        print(f"ridge {name}: {len(arr)} rows tracked (of {nrows}); "
              f"V_bg {arr[0,0]:+.3f}..{arr[-1,0]:+.3f}; "
              f"V_tg {arr[:,1].min():+.3f}..{arr[:,1].max():+.3f}")
    else:
        print(f"ridge {name}: no rows tracked")

# separation between the two ridges where both are resolved
if all(len(tracks[n]) for n in SEEDS):
    common = sorted(set(tracks["A"][:, 3]).intersection(tracks["B"][:, 3]))
    if common:
        ia = {int(r[3]): r[1] for r in tracks["A"]}
        ib = {int(r[3]): r[1] for r in tracks["B"]}
        print("\nridge separation where both resolved (parallel => constant):")
        for k in common:
            k = int(k)
            print(f"  V_bg={Vbg[k]:+.4f}  A={ia[k]:+.4f}  B={ib[k]:+.4f}  "
                  f"sep={ib[k]-ia[k]:+.4f} V")

# ---------------- Step 2: robust fit per ridge ----------------
def robust_fit(x, y, nsig=2.0, iters=3):
    keep = np.ones(len(x), bool)
    for _ in range(iters):
        c = np.polyfit(x[keep], y[keep], 1)
        res = y - np.polyval(c, x)
        s = res[keep].std(ddof=1)
        if s == 0:
            break
        new = np.abs(res) < nsig * s
        if (new == keep).all():
            break
        keep = new
    c = np.polyfit(x[keep], y[keep], 1)
    res = y[keep] - np.polyval(c, x[keep])
    return c, keep, res


print("\n" + "=" * 74)
print("Step 2 — ridge fits  (fast axis V_tg vs slow axis V_bg;  c_bg/c_tg = -slope)")
print("=" * 74)
fits = {}
for name, t in tracks.items():
    if len(t) < 4:
        print(f"  ridge {name}: too few rows to fit")
        continue
    x, y = t[:, 0], t[:, 1]
    c, keep, res = robust_fit(x, y)
    fits[name] = dict(slope=c[0], icept=c[1], keep=keep, res=res, track=t)
    print(f"  ridge {name}: V_tg = {c[0]:+.4f}*V_bg {c[1]:+.4f}   "
          f"c_bg/c_tg = {-c[0]:.4f}   rms resid {res.std(ddof=1)*1e3:.2f} mV   "
          f"{keep.sum()}/{len(x)} rows kept")

if len(fits) == 2:
    sA, sB = fits["A"]["slope"], fits["B"]["slope"]
    rA = fits["A"]["res"].std(ddof=1)
    rB = fits["B"]["res"].std(ddof=1)
    # slope uncertainty ~ resid / (sigma_x * sqrt(N))
    def slope_err(f):
        x = f["track"][:, 0][f["keep"]]
        return f["res"].std(ddof=1) / (x.std(ddof=1) * np.sqrt(len(x)))
    eA, eB = slope_err(fits["A"]), slope_err(fits["B"])
    d = abs(sA - sB); sd = np.hypot(eA, eB)
    print(f"\n  slope A = {sA:+.4f} +/- {eA:.4f}")
    print(f"  slope B = {sB:+.4f} +/- {eB:.4f}")
    print(f"  |dA-dB| = {d:.4f}  ({d/sd:.1f} sigma)  -> "
          f"{'PARALLEL (consistent)' if d < 2*sd else 'NOT parallel'}")
    print(f"  geometry prior c_bg/c_tg = {9.5/11:.4f}")
    print(f"  density offset between ridges at fixed D: "
          f"delta n = c_tg*|icept_A - icept_B|/e = "
          f"{1.745*abs(fits['A']['icept']-fits['B']['icept']):.3f}e12 cm^-2")

np.save(f"{SCRATCH}/gatemap_R.npy", R)
np.save(f"{SCRATCH}/gatemap_Vbg.npy", Vbg)
np.save(f"{SCRATCH}/gatemap_Vtg.npy", tg)

# ---------------- figures ----------------
fig, axs = plt.subplots(1, 2, figsize=(14, 5.6))
ax = axs[0]
pc = ax.pcolormesh(tg, Vbg, R, shading="nearest", cmap="viridis",
                   vmax=np.percentile(R, 99))
fig.colorbar(pc, ax=ax, label=r"$R_{xx}$ ($\Omega$)")
for name, col in (("A", "w"), ("B", "r")):
    if name in tracks and len(tracks[name]):
        t = tracks[name]
        ax.plot(t[:, 1], t[:, 0], ".", ms=4, color=col, label=f"ridge {name}")
    if name in fits:
        f = fits[name]
        ax.plot(np.polyval([f["slope"], f["icept"]], Vbg), Vbg, "-", lw=1.2, color=col)
ax.set_xlabel(r"$V_{tg}$ (V)"); ax.set_ylabel(r"$V_{bg}$ (V)")
ax.set_title("gate map — $R_{xx}$ with fitted CNP lines")
ax.legend(fontsize=8)

ax = axs[1]
pc = ax.pcolormesh(tg, Vbg, np.log10(R), shading="nearest", cmap="magma")
fig.colorbar(pc, ax=ax, label=r"$\log_{10} R_{xx}$")
ax.set_xlabel(r"$V_{tg}$ (V)"); ax.set_ylabel(r"$V_{bg}$ (V)")
ax.set_title("log scale")
fig.tight_layout()
fig.savefig(f"{SCRATCH}/gatemap.png", dpi=120)
print(f"\nwrote {SCRATCH}/gatemap.png")
