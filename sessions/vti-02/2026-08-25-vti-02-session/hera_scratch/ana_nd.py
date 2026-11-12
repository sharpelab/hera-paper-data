"""Reproject the gate map into (n, D) with the cap ratio fitted, not assumed.

n and D are both linear in (V_tg, V_bg), so ANY constant-n locus must be a
straight line in gate space. Curvature in a tracked ridge therefore falsifies
"this ridge is a constant-n contour" -- test that explicitly here.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import scipy.constants as cst
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks

from hera.analysis import fan_grids, resistance_grids

BASE = "C:/Users/DGG/VTI_local_data/zack/20260825-vti-02/data"
SCRATCH = "C:/Users/DGG/VTI_local_data/zack/20260825-vti-02/hera_scratch"

fg = fan_grids(f"{BASE}/4")
def g(n): return fg.data[:, fg.cols.index(n)].reshape(fg.nrows, fg.nfast)
rg = resistance_grids(fg, channels=["sr1"])
R = np.abs(rg.R["sr1"]); tg = g("k_2400_tg_volt")[0]; vb = g("k_2400_bg_volt")[:, 0]
nrows, nfast = R.shape

# ---- track the two ridges with an explicit, auditable rule ----
def peaks(row, prom_frac=0.05, edge=3):
    y = gaussian_filter1d(row, 2.0)
    idx, pr = find_peaks(y, prominence=prom_frac * np.ptp(y))
    return [(tg[i], y[i], i) for i, p in zip(idx, pr["prominences"])
            if edge <= i < len(y) - edge]

B_pts, A_pts = [], []
for k in range(nrows):
    ps = peaks(R[k])
    if not ps:
        continue
    if vb[k] <= -0.32:                      # only ridge B exists here
        B_pts.append((vb[k], *ps[np.argmax([p[1] for p in ps])][:2]))
    elif vb[k] <= 0.02:                     # both resolved: B is the higher-V_tg one
        ps = sorted(ps)
        A_pts.append((vb[k], ps[0][0], ps[0][1]))
        if len(ps) > 1:
            B_pts.append((vb[k], ps[-1][0], ps[-1][1]))
    else:                                   # only ridge A, B has left the window
        A_pts.append((vb[k], *ps[np.argmax([p[1] for p in ps])][:2]))
B = np.array(B_pts); A = np.array(A_pts)
print(f"ridge B: {len(B)} pts, V_bg {B[:,0].min():+.3f}..{B[:,0].max():+.3f}")
print(f"ridge A: {len(A)} pts, V_bg {A[:,0].min():+.3f}..{A[:,0].max():+.3f}")

# ---- linearity test: is each ridge straight? ----
print("\n=== linearity test (a constant-n locus MUST be straight) ===")
for name, T in (("B", B), ("A", A)):
    x, y = T[:, 0], T[:, 1]
    c1 = np.polyfit(x, y, 1); r1 = y - np.polyval(c1, x)
    c2 = np.polyfit(x, y, 2); r2 = y - np.polyval(c2, x)
    # significance of the quadratic term vs the linear-fit scatter
    print(f"  ridge {name}: linear slope {c1[0]:+.4f}, rms {r1.std(ddof=1)*1e3:6.2f} mV | "
          f"quad coef {c2[0]:+.4f}, rms {r2.std(ddof=1)*1e3:6.2f} mV | "
          f"F-improve {r1.std(ddof=1)/max(r2.std(ddof=1),1e-9):.2f}x")
    if len(x) > 8:
        h = len(x) // 2
        s_lo = np.polyfit(x[:h], y[:h], 1)[0]
        s_hi = np.polyfit(x[h:], y[h:], 1)[0]
        print(f"      slope on the low-V_bg half {s_lo:+.4f}  vs high half {s_hi:+.4f}")

# ---- fit the ratio over the CAMPAIGN's operating window (near D=0) ----
WIN = 0.45     # |V_bg| window around 0 -- the recipe: fit where the campaign works
mB = np.abs(B[:, 0]) <= WIN
cB = np.polyfit(B[mB, 0], B[mB, 1], 1)
mA = np.abs(A[:, 0]) <= WIN
cA = np.polyfit(A[mA, 0], A[mA, 1], 1)
print(f"\n=== fits restricted to |V_bg| <= {WIN} (the operating window) ===")
print(f"  ridge B: slope {cB[0]:+.4f} -> c_bg/c_tg = {-cB[0]:.4f}  ({mB.sum()} pts), "
      f"V_tg intercept {cB[1]:+.4f}")
print(f"  ridge A: slope {cA[0]:+.4f} -> c_bg/c_tg = {-cA[0]:.4f}  ({mA.sum()} pts), "
      f"V_tg intercept {cA[1]:+.4f}")
print(f"  geometry prior c_bg/c_tg = {9.5/11:.4f}")

# ---- reproject with a chosen ratio ----
t_tg, t_bg, k_hbn = 9.5e-9, 11e-9, 3.0
c_tg = cst.epsilon_0 * k_hbn / t_tg
for label, ratio in (("geometry prior", 9.5 / 11), ("ridge-B operating-window fit", -cB[0])):
    c_bg = ratio * c_tg
    n = (c_tg * tg[None, :] + c_bg * vb[:, None]) / cst.e * 1e-16      # 1e12 cm^-2
    D = (c_tg * tg[None, :] - c_bg * vb[:, None]) / (2 * cst.epsilon_0) * 1e-9  # V/nm
    nB = (c_tg * B[:, 1] + c_bg * B[:, 0]) / cst.e * 1e-16
    DB = (c_tg * B[:, 1] - c_bg * B[:, 0]) / (2 * cst.epsilon_0) * 1e-9
    nA = (c_tg * A[:, 1] + c_bg * A[:, 0]) / cst.e * 1e-16
    DA = (c_tg * A[:, 1] - c_bg * A[:, 0]) / (2 * cst.epsilon_0) * 1e-9
    print(f"\n--- {label}: c_bg/c_tg = {ratio:.4f} ---")
    print(f"  ridge B: n spans {nB.min():+.3f}..{nB.max():+.3f} e12 (spread {np.ptp(nB):.3f}), "
          f"D spans {DB.min():+.4f}..{DB.max():+.4f} V/nm")
    print(f"  ridge A: n spans {nA.min():+.3f}..{nA.max():+.3f} e12 (spread {np.ptp(nA):.3f}), "
          f"D spans {DA.min():+.4f}..{DA.max():+.4f} V/nm")
    if label.startswith("ridge-B"):
        keep = (n, D, nB, DB, nA, DA, ratio)

n, D, nB, DB, nA, DA, ratio = keep
print(f"\nmap coverage: n {n.min():+.2f}..{n.max():+.2f} e12 cm^-2, "
      f"D {D.min():+.3f}..{D.max():+.3f} V/nm")

fig, axs = plt.subplots(1, 2, figsize=(14.5, 5.6))
ax = axs[0]
sc = ax.scatter(n.ravel(), D.ravel(), c=np.log10(R.ravel()), s=5, cmap="magma")
fig.colorbar(sc, ax=ax, label=r"$\log_{10} R_{xx}$")
ax.plot(nB, DB, "o", ms=4, mfc="none", mec="c", label="ridge B")
ax.plot(nA, DA, "s", ms=4, mfc="none", mec="lime", label="ridge A")
ax.axvline(0, color="w", lw=0.6, ls=":"); ax.axhline(0, color="w", lw=0.6, ls=":")
ax.set_xlabel(r"$n$ ($10^{12}$ cm$^{-2}$)"); ax.set_ylabel(r"$D$ (V/nm)")
ax.set_title(f"gate map in (n, D),  $c_{{bg}}/c_{{tg}}$ = {ratio:.3f}")
ax.legend(fontsize=8)

ax = axs[1]
ax.plot(DB, nB, "o-", ms=4, label="ridge B")
ax.plot(DA, nA, "s-", ms=4, label="ridge A")
ax.axhline(0, color="k", lw=0.6, ls=":"); ax.axvline(0, color="k", lw=0.6, ls=":")
ax.set_xlabel(r"$D$ (V/nm)"); ax.set_ylabel(r"ridge $n$ ($10^{12}$ cm$^{-2}$)")
ax.set_title("ridge density vs D\n(a constant-n CNP is a horizontal line)")
ax.grid(alpha=0.3); ax.legend(fontsize=8)
fig.tight_layout()
fig.savefig(f"{SCRATCH}/gatemap_nD.png", dpi=120)
print(f"wrote {SCRATCH}/gatemap_nD.png")
