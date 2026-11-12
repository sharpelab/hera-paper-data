# Ladder v2 (runs 16-22): multi-cosine LSQ amplitudes -> LK masses; v1 comparison
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

def collect(run_ids):
    amps = {ch: {k: [] for k in LABELS} for ch in ("sr1", "sr2")}
    Ts = []
    for rid in run_ids:
        r = open_run(f"data/{rid}")
        B = r.col_at(4); o = np.argsort(B)
        Ts.append(float(np.mean(r.col("T_sample"))))
        for ch in ("sr1", "sr2"):
            R = np.abs(r.col(f"{ch}_X"))[o] / I_BIAS
            for k, a in zip(LABELS, tone_amps(B[o], R)):
                amps[ch][k].append(a)
    return np.array(Ts), amps

def lk(T, A0, m):
    X = 2 * np.pi**2 * kB * T * (m * me) / (hbar * e_ch * B_eff)
    return A0 * X / np.sinh(X)

T2, A2 = collect(range(16, 23))
T1, A1 = collect(range(10, 16))
print(f"v2 rungs: {np.round(T2, 2)}")

fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
fits = {}
for ax, ch in zip(axes, ("sr1", "sr2")):
    for k in LABELS:
        A = np.array(A2[ch][k]); An = A / A[0]
        hi = T2 >= 9.5
        p, cov = curve_fit(lk, T2[hi], An[hi], p0=[1.5, 0.04],
                           bounds=([0.05, 0.005], [30, 0.3]), maxfev=20000)
        fits[(ch, k)] = (p[1], np.sqrt(np.diag(cov))[1])
        ax.semilogy(T2, An, "o", ms=5, label=f"{k}: m*={p[1]:.4f}±{np.sqrt(np.diag(cov))[1]:.4f}")
        Tf = np.linspace(1, 52, 120)
        ax.semilogy(Tf, lk(Tf, *p), lw=0.8)
        # v1 comparison points (matched acquisition, coarser sens)
        A1n = np.array(A1[ch][k]) / A1[ch][k][0]
        ax.semilogy(T1, A1n, "x", ms=4, alpha=0.5)
    ax.set_xlabel("T lattice (K)"); ax.set_title(f"{ch}  (o = v2, x = v1)")
    ax.legend(fontsize=7)
axes[0].set_ylabel("amp (norm to base rung)")
fig.suptitle(f"LK ladder v2 (runs 16-22, X-designed top, multi-cosine amplitudes), B_eff={B_eff:.2f} T")
fig.tight_layout(); plt.show()

for ch in ("sr1", "sr2"):
    mml, sml = fits[(ch, "ML")]; mbl, sbl = fits[(ch, "BL")]; mfl, sfl = fits[(ch, "FL")]
    ssum = np.hypot(sml, sbl)
    print(f"{ch}: ML {mml:.4f}±{sml:.4f}  BL {mbl:.4f}±{sbl:.4f}  FL {mfl:.4f}±{sfl:.4f}  "
          f"| parents' sum {mml+mbl:.4f}±{ssum:.4f}  (FL - sum = {mfl-(mml+mbl):+.4f}, {(mfl-(mml+mbl))/np.hypot(sfl,ssum):+.1f}σ)")
