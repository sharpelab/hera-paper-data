# cnp-and-dline-calibration on run 7 (scratch)
import numpy as np
from scipy.ndimage import gaussian_filter1d
from hera.analysis import open_run, GateCalibration
import scipy.constants as cst
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

E = cst.e; EPS0 = cst.epsilon_0
NFAST = 161
r = open_run("data/7")
vt = r.col("k_2400_tg_volt"); vb = r.col("k_2400_bg_volt")
i_dr = np.abs(r.col("sr0_X")) / 1e6

def grid(c): return c[:len(c) // NFAST * NFAST].reshape(-1, NFAST)
VT, VB, IDR = grid(vt), grid(vb), grid(i_dr)
nrows = VT.shape[0]
print(f"rows: {nrows}; I_drain over map: med {np.median(IDR)*1e9:.2f} nA, "
      f"min {IDR.min()*1e9:.2f}, max {IDR.max()*1e9:.2f}")

# --- Step 1-2: per-channel ridge extraction + robust fit ---
fits = {}
for ch in ("sr1", "sr2", "sr3"):
    R = grid(r.col(f"{ch}_X")) / IDR
    rows_v, ridge_v, kept = [], [], 0
    for j in range(nrows):
        sm = gaussian_filter1d(R[j], 3)
        k = int(np.argmax(sm))
        if k <= 5 or k >= NFAST - 6:          # edge-clipped row
            continue
        if sm[k] < 2 * np.median(sm):          # no clear ridge in this row
            continue
        rows_v.append(VB[j, 0]); ridge_v.append(VT[j, k])
    rows_v, ridge_v = np.array(rows_v), np.array(ridge_v)
    # iterative outlier rejection (2 sigma, 3 passes)
    m = np.ones(len(rows_v), bool)
    for _ in range(3):
        p = np.polyfit(rows_v[m], ridge_v[m], 1)
        res = ridge_v - np.polyval(p, rows_v)
        s = res[m].std()
        m = np.abs(res) < 2 * max(s, 1e-4)
    p = np.polyfit(rows_v[m], ridge_v[m], 1)
    res = (ridge_v - np.polyval(p, rows_v))[m]
    fits[ch] = dict(slope=p[0], intercept=p[1], rms=res.std(), nrows=int(m.sum()),
                    rows_v=rows_v[m], ridge_v=ridge_v[m])
    print(f"{ch}: slope {p[0]:+.4f}, intercept {p[1]:+.4f} V, rms {res.std()*1e3:.1f} mV, "
          f"rows kept {m.sum()}/{nrows}")

# axis orientation: ridge position is V_tg (fast) fitted against V_bg (rows)
# -> c_bg/c_tg = -slope  (recipe step 2 orientation statement)
sl = [fits[ch]["slope"] for ch in ("sr1", "sr3")]   # sr2 weak channel: report, don't drive
slope = float(np.mean(sl))
spread = abs(sl[0] - sl[1])
print(f"\ncross-channel: sr1 {sl[0]:+.4f} vs sr3 {sl[1]:+.4f} (spread {spread:.4f} "
      f"= {spread/abs(slope)*100:.1f}%; fit rms bound ~{max(fits['sr1']['rms'],fits['sr3']['rms'])/2.5*1e3:.0f} mV/2.5V)")

# --- Step 3: conversion. Anchor TG at its stack prior (single hBN dielectric). ---
c_tg = EPS0 * 3.0 / 14.9e-9
c_bg = -slope * c_tg
c_bg_geom = EPS0 * 3.0 / 21.4e-9
print(f"\nc_tg (anchor, geometry) = {c_tg*1e3:.3f} mF/m2")
print(f"c_bg (ratio-calibrated) = {c_bg*1e3:.3f} mF/m2  vs geometry {c_bg_geom*1e3:.3f} "
      f"({(c_bg/c_bg_geom-1)*100:+.1f}%)")
print(f"ratio c_bg/c_tg = {-slope:.4f} (geometry prior {c_bg_geom/c_tg:.4f})")

b = float(np.mean([fits[ch]["intercept"] for ch in ("sr1", "sr3")]))
cal0 = GateCalibration(c_tg, c_bg)
n_off = -float(cal0.density(b, 0.0))
cal = GateCalibration(c_tg, c_bg, n_offset=n_off, D_offset=0.0)
print(f"intercept b = {b:+.4f} V -> n_offset = {n_off:.3e} m^-2 ({n_off*1e-16:+.3f} x1e12 cm^-2)")
print("D_offset = 0 (stated assumption: no +/-D-symmetric feature identified yet)")

# closure: n along the fitted ridge
vv = np.linspace(-1.1, 1.15, 50)
n_res = cal.density(slope * vv + b, vv)
print(f"closure: max |n| residual along ridge = {np.abs(n_res).max()*1e-16:.4f} x1e12 cm^-2")

# --- Step 4: D=0 line designer + realized window (clip by dropping) ---
TG_L, BG_L = 0.8, 5.0
def gate_v(ns, D0=0.0):
    # invert: V_tg = (e*(n-n_off)/2 + eps0*D0) / c_tg ; V_bg = (e*(n-n_off)/2 - eps0*D0) / c_bg
    ns = np.asarray(ns, float)
    q = E * (ns - n_off) / 2.0
    Vt = (q + EPS0 * D0) / c_tg
    Vb = (q - EPS0 * D0) / c_bg
    m = (np.abs(Vt) <= TG_L) & (np.abs(Vb) <= BG_L)
    return Vt[m], Vb[m], ns[m]

ns = np.linspace(-2.5e16, 2.5e16, 2001)
Vt, Vb, nk = gate_v(ns, 0.0)
print(f"\nD=0 realized n-window: {nk.min()*1e-16:+.3f} .. {nk.max()*1e-16:+.3f} x1e12 cm^-2 "
      f"(V_tg {Vt.min():+.3f}..{Vt.max():+.3f}, V_bg {Vb.min():+.3f}..{Vb.max():+.3f})")
# roundtrip
nn, DD = cal.n_D(Vt, Vb)
print(f"roundtrip: max|D| = {np.abs(DD).max():.3e} V/m, n monotonic: {np.all(np.diff(nn)>0)}")

# F_L feasibility (investigation step 2) at the window edges
for ntag, nval in (("n_max_e", nk.max()), ("n_max_h", nk.min())):
    FL = cst.h * abs(nval) / (4 * E)
    print(f"{ntag} = {nval*1e-16:+.2f}e12: F_L = {FL:.1f} T; Nyquist d(1/B) <= {1/(3*FL):.2e} /T (1/3 rule)")

# overlay figure
fig, ax = plt.subplots(figsize=(6.5, 5))
R1 = grid(r.col("sr1_X")) / IDR
pm = ax.pcolormesh(VT, VB, R1 / 1e3, shading="nearest", cmap="inferno")
fig.colorbar(pm, ax=ax, label="sr1 Rxx (kOhm)")
for ch, c in (("sr1", "c"), ("sr3", "lime")):
    f = fits[ch]
    ax.plot(f["ridge_v"], f["rows_v"], ".", color=c, ms=3, label=f"{ch} ridge")
vv = np.linspace(-1.2, 1.2, 10)
ax.plot(slope * vv + b, vv, "w--", lw=1, label=f"fit: {slope:+.3f}·Vbg{b:+.3f}")
ax.plot(Vt, Vb, "b:", lw=1.5, label="D=0 line")
ax.set_xlabel("V_tg (V)"); ax.set_ylabel("V_bg (V)"); ax.legend(fontsize=7)
fig.tight_layout(); fig.savefig("hera_scratch/cnp_fit_overlay.png", dpi=110)
print("saved hera_scratch/cnp_fit_overlay.png")
