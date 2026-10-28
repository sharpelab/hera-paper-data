"""Landau-fan read, constrained. Two independent estimators, cross-checked.

(1) SPACING estimator -- absolute lever arm, needs no filling-factor assignment.
    Within a row, consecutive minima are spaced dV = dnu * alpha * B. So the
    fundamental spacing is linear in B through the origin, and its slope gives
    alpha once dnu is named. Robust: a missed minimum shows up as a 2x outlier
    and is rejected, it does not bias the fundamental.

(2) RAY estimator -- CNP location, needs no lever arm.
    Every LL ray is V = V_CNP + nu*alpha*B, so ALL rays converge at B = 0 on
    V_CNP. Track minima across rows and extrapolate; the common intercept is
    the CNP, and TWO convergence points would mean two doping domains.

A free (V_CNP, alpha) integer-fit was tried first and overfitted -- with both
parameters floating it returned filling factors {5,7,10,11,...} with spacings
{1,2,3,6}, i.e. it will fit anything. Constrain, then cross-check.
"""
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import scipy.constants as cst
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks

from hera.analysis import fan_grids, resistance_grids, summarize_run, open_run

BASE = "C:/Users/DGG/VTI_local_data/zack/20260825-vti-02/data"
SCRATCH = "C:/Users/DGG/VTI_local_data/zack/20260825-vti-02/hera_scratch"
RID = int(sys.argv[1]) if len(sys.argv) > 1 else 5
DNU = 4                      # spin x valley; stated, and tested below
SENS = 5e-4

r = open_run(f"{BASE}/{RID}")
print(summarize_run(r))
fg = fan_grids(r)
def g(n): return fg.data[:, fg.cols.index(n)].reshape(fg.nrows, fg.nfast)
rg = resistance_grids(fg, channels=["sr1"])
R = np.abs(rg.R["sr1"]); tg = g("k_2400_tg_volt")[0]; B = g("magnet_field")[:, 0]
Vx = np.abs(g("sr1_X"))
dv = tg[1] - tg[0]


def minima(row, prom=0.05, edge=3):
    y = gaussian_filter1d(np.log10(np.maximum(row, 1e-2)), 1.5)
    idx, pr = find_peaks(-y, prominence=prom * np.ptp(y))
    out = []
    for i in idx:
        if not (edge <= i < len(y) - edge):
            continue
        y0, y1, y2 = y[i - 1], y[i], y[i + 1]
        d = y0 - 2 * y1 + y2
        out.append(tg[i] + (0.5 * (y0 - y2) / d if d else 0.0) * dv)
    return np.array(sorted(out))


mins, clipmax = {}, {}
for k in range(fg.nrows):
    ci = np.where(Vx[k] > 0.9 * SENS)[0]
    clipmax[k] = tg[ci.max()] if len(ci) else -0.30
    mins[k] = minima(R[k])

# ---------------- (1) spacing estimator ----------------
print("\n=== (1) fundamental LL spacing vs B (electron flank) ===")
print(f"{'B (T)':>7} {'n_min':>6} {'diffs (V)':>44} {'fundamental':>12} {'d/B':>8}")
sp = []
for k in range(fg.nrows):
    e = mins[k][mins[k] > clipmax[k] + 0.05]
    if len(e) < 3:
        continue
    d = np.diff(e)
    # fundamental = smallest cluster; reject ~2x multiples (a missed minimum)
    base = np.median(d[d < 1.6 * d.min()])
    keep = d[np.abs(d / base - np.round(d / base)) < 0.25]
    fund = np.median(keep / np.round(keep / base))
    sp.append((B[k], fund))
    print(f"{B[k]:>7.2f} {len(e):>6d} {' '.join(f'{x:.3f}' for x in d):>44} "
          f"{fund:>12.4f} {fund/B[k]:>8.4f}")
sp = np.array(sp)

if len(sp) >= 3:
    slope = np.sum(sp[:, 0] * sp[:, 1]) / np.sum(sp[:, 0] ** 2)     # through origin
    res = sp[:, 1] - slope * sp[:, 0]
    alpha = slope / DNU
    c_tg = cst.e ** 2 / (cst.h * alpha)
    c_prior = cst.epsilon_0 * 3.0 / 9.5e-9
    print(f"\n  dV/B = {slope:.5f} V/T  (rms resid {res.std(ddof=1)*1e3:.2f} mV), "
          f"assuming dnu = {DNU}")
    print(f"  alpha = {alpha:.5f} V/(T*nu)")
    print(f"  c_tg  = {c_tg:.4e} F/m^2   vs prior {c_prior:.4e}   "
          f"ratio {c_tg/c_prior:.3f}")
    print(f"  dn/dV_tg = {c_tg/cst.e*1e-4*1e-12:.4f} e12 cm^-2/V "
          f"(prior {c_prior/cst.e*1e-4*1e-12:.4f})")
    print(f"  implied top-gate hBN = {cst.epsilon_0*3.0/c_tg*1e9:.2f} nm (card 9.50 nm)")
    for alt in (2, 8):
        ca = cst.e ** 2 / (cst.h * slope / alt)
        print(f"    [if dnu were {alt}: c_tg = {ca:.3e}, hBN = "
              f"{cst.epsilon_0*3.0/ca*1e9:.1f} nm]")

# ---------------- (2) ray estimator ----------------
print("\n=== (2) ray convergence -> V_CNP (independent of the lever arm) ===")
# link minima row-to-row by nearest neighbour, walking up in B
rays = []
prev = [(B[k0], v) for k0 in range(fg.nrows) if B[k0] >= 1.0 for v in []]
start = min(k for k in range(fg.nrows) if B[k] >= 1.0)
active = [[(B[start], v)] for v in mins[start] if v > clipmax[start] + 0.05]
for k in range(start + 1, fg.nrows):
    cand = [v for v in mins[k] if v > clipmax[k] + 0.05]
    used = set()
    for ray in active:
        b0, v0 = ray[-1]
        # a ray moves outward roughly proportionally to B
        pred = v0 * (B[k] / b0) if b0 > 0 else v0
        near = [v for v in cand if v not in used and abs(v - pred) < 0.09]
        if near:
            v = min(near, key=lambda v: abs(v - pred))
            used.add(v); ray.append((B[k], v))
    for v in cand:
        if v not in used:
            active.append([(B[k], v)])
rays = [np.array(r_) for r_ in active if len(r_) >= 3]
print(f"  {len(rays)} rays with >= 3 rows")
icepts = []
for r_ in rays:
    c = np.polyfit(r_[:, 0], r_[:, 1], 1)
    icepts.append(c[1])
    print(f"    ray over B={r_[0,0]:.1f}..{r_[-1,0]:.1f} ({len(r_)} pts): "
          f"slope {c[0]:+.4f} V/T, B=0 intercept {c[1]:+.4f} V")
if icepts:
    icepts = np.array(icepts)
    print(f"\n  V_CNP from ray convergence = {np.median(icepts):+.4f} V "
          f"(spread {icepts.std(ddof=1) if len(icepts)>1 else 0:.4f} V, "
          f"{len(icepts)} rays)")
    print(f"  zero-field ridges: A -0.2032, B +0.1125")
    if len(icepts) > 2 and icepts.std(ddof=1) > 0.08:
        print("  !! intercepts do NOT agree -- inconsistent with a single CNP; "
              "check for two fan origins (two doping domains)")

# ---------------- (3) lever arm from RAY SLOPES (the good estimator) ----------------
# Each ray has slope = nu*alpha. Fit the single alpha that makes every observed
# slope a multiple of DNU*alpha. This needs no per-row spacing heuristic (which
# breaks when the ladder skips filling factors) and no absolute nu assignment --
# only that the rays are a degenerate ladder with a common step.
print("\n=== (3) lever arm from ray slopes ===")
slopes = np.array([np.polyfit(r_[:, 0], r_[:, 1], 1)[0] for r_ in rays])
slopes = np.sort(slopes[slopes > 0])
if len(slopes) >= 4:
    best = None
    for a in np.linspace(0.004, 0.040, 7201):
        m = slopes / (DNU * a)
        if np.round(m).min() < 1 or np.round(m).max() > 15:
            continue
        err = np.mean((m - np.round(m)) ** 2)
        if best is None or err < best[0]:
            best = (err, a)
    err, alpha_r = best
    mult = np.round(slopes / (DNU * alpha_r)).astype(int)
    # refine: least squares through origin on slope = (DNU*mult)*alpha
    x = DNU * mult
    alpha_r = float(np.sum(x * slopes) / np.sum(x * x))
    c_tg_r = cst.e ** 2 / (cst.h * alpha_r)
    c_prior = cst.epsilon_0 * 3.0 / 9.5e-9
    print(f"  ray slopes (V/T): {np.array2string(slopes, precision=4)}")
    print(f"  assigned nu:      {(DNU*mult).tolist()}")
    print(f"  slope/nu:         "
          f"{np.array2string(slopes/(DNU*mult), precision=5)}")
    print(f"  alpha = {alpha_r:.5f} V/(T*nu)   rms integer resid "
          f"{np.sqrt(err):.4f}")
    print(f"  c_tg  = {c_tg_r:.4e} F/m^2   ratio to prior {c_tg_r/c_prior:.3f}")
    print(f"  dn/dV_tg = {c_tg_r/cst.e*1e-4*1e-12:.4f} e12 cm^-2/V "
          f"(prior {c_prior/cst.e*1e-4*1e-12:.4f})")
    print(f"  implied top-gate hBN = {cst.epsilon_0*3.0/c_tg_r*1e9:.2f} nm (card 9.50)")
    if len(icepts):
        vcnp = float(np.median(icepts))
        print(f"\n  ==> CALIBRATION (V_bg = 0): CNP at V_tg = {vcnp:+.4f} V, "
              f"dn/dV_tg = {c_tg_r/cst.e*1e-4*1e-12:.3f}e12 cm^-2/V")
        print(f"      reachable n on this cut: "
              f"{(tg[0]-vcnp)*c_tg_r/cst.e*1e-4*1e-12:+.2f} .. "
              f"{(tg[-1]-vcnp)*c_tg_r/cst.e*1e-4*1e-12:+.2f} e12 cm^-2")

fig, ax = plt.subplots(1, 2, figsize=(14.5, 5.6))
pc = ax[0].pcolormesh(tg, B, np.log10(R), shading="nearest", cmap="magma")
fig.colorbar(pc, ax=ax[0], label=r"$\log_{10}R_{xx}$")
for r_ in rays:
    ax[0].plot(r_[:, 1], r_[:, 0], "w.-", lw=0.6, ms=3)
    c = np.polyfit(r_[:, 0], r_[:, 1], 1)
    ax[0].plot(np.polyval(c, B), B, "c-", lw=0.6, alpha=0.6)
if len(icepts):
    ax[0].axvline(np.median(icepts), color="lime", ls="--", lw=1.2)
ax[0].set_xlim(tg[0], tg[-1]); ax[0].set_ylim(B.min(), B.max())
ax[0].set_xlabel(r"$V_{tg}$ (V)"); ax[0].set_ylabel("B (T)")
ax[0].set_title("calibration fan — tracked LL rays")
if len(sp) >= 3:
    ax[1].plot(sp[:, 0], sp[:, 1], "o", ms=6)
    ax[1].plot([0, sp[:, 0].max()], [0, slope * sp[:, 0].max()], "-")
    ax[1].set_xlabel("B (T)"); ax[1].set_ylabel("fundamental LL spacing (V)")
    ax[1].set_title(f"spacing ∝ B  →  $c_{{tg}}$={c_tg:.3e} F/m² "
                    f"({c_tg/c_prior:.2f}× prior)")
    ax[1].grid(alpha=0.3)
fig.tight_layout(); fig.savefig(f"{SCRATCH}/fan2.png", dpi=120)
print(f"\nwrote {SCRATCH}/fan2.png")
