# Ladder v2 — floor-truncation sensitivity of the LK fits (answers the >30 K BL/FL divergence question)
# The post-minimum rise of a dead tone's LSQ amplitude is extraction floor, not signal.
# Fit each tone only on heated rungs up to its amplitude minimum; compare with the untruncated fit.
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from hera.analysis import open_run

I_BIAS = 20e-9
kB, hbar, e_ch, me = 1.380649e-23, 1.0545718e-34, 1.602177e-19, 9.109384e-31
B_eff = 2.0 / (1 / 2.8 + 1 / 6.0)
FREQS = [13.4, 55.2, 66.3]
LABELS = ["ML", "BL", "FL"]

def tone_amps(B, R, bg_deg=5):
    x = 1.0 / B
    cols = [B**k for k in range(bg_deg + 1)]
    for F in FREQS:
        cols += [np.cos(2 * np.pi * F * x), np.sin(2 * np.pi * F * x)]
    M = np.vstack(cols).T
    c, *_ = np.linalg.lstsq(M, R, rcond=None)
    return [np.hypot(c[bg_deg + 1 + 2 * i], c[bg_deg + 2 + 2 * i]) for i in range(3)]

amps = {ch: {k: [] for k in LABELS} for ch in ("sr1", "sr2")}
Ts = []
for rid in range(16, 23):
    r = open_run(f"data/{rid}")
    B = r.col_at(4); o = np.argsort(B)
    Ts.append(float(np.mean(r.col("T_sample"))))
    for ch in ("sr1", "sr2"):
        R = np.abs(r.col(f"{ch}_X"))[o] / I_BIAS
        for k, a in zip(LABELS, tone_amps(B[o], R)):
            amps[ch][k].append(a)
Ts = np.array(Ts)

def lk(T, A0, m):
    X = 2 * np.pi**2 * kB * T * (m * me) / (hbar * e_ch * B_eff)
    return A0 * X / np.sinh(X)

print(f"rungs: {np.round(Ts, 2)}   B_eff = {B_eff:.2f} T")
print("fit on heated rungs; 'trunc' drops each tone's post-minimum (floor) tail:\n")
for ch in ("sr1", "sr2"):
    res = {}
    for k in LABELS:
        An = np.array(amps[ch][k]); An = An / An[0]
        for mode in ("full", "trunc"):
            use = Ts >= 9.5
            if mode == "trunc":
                cut = int(np.argmin(An)) + 1
                use &= np.arange(len(Ts)) < cut
            p, cov = curve_fit(lk, Ts[use], An[use], p0=[1.5, 0.04],
                               bounds=([0.05, 0.005], [30, 0.3]), maxfev=20000)
            res[(k, mode)] = (p[1], np.sqrt(np.diag(cov))[1], use.sum())
    for mode in ("full", "trunc"):
        s = res[("ML", mode)][0] + res[("BL", mode)][0]
        ss = np.hypot(res[("ML", mode)][1], res[("BL", mode)][1])
        fl, sfl, npts = res[("FL", mode)]
        d = fl - s
        print(f"{ch} {mode:5s}: ML {res[('ML',mode)][0]:.4f}  BL {res[('BL',mode)][0]:.4f}  "
              f"FL {fl:.4f}±{sfl:.4f} ({npts}p)  | Σ(ML+BL) {s:.4f}±{ss:.4f}  FL−Σ {d:+.4f} ({d/np.hypot(sfl,ss):+.1f}σ)")
    print()
