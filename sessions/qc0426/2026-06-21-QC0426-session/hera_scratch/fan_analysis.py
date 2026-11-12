import os, sys, numpy as np, hera.analysis as a
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
sys.path.insert(0, os.path.expanduser("~/measurement_env/hera/models/trilayer_fs_count"))
import fs_count_b0 as fsc

MDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCR = os.path.join(MDIR, "hera_scratch")
run = a.open_run(os.path.join(MDIR, "data", "4"))
fg = a.fan_grids(run)
B = np.asarray(fg.slow)                       # (rows,) descending
rg = a.resistance_grids(fg)
R1 = rg.R["sr1"]; R2 = rg.R["sr2"]; Rxy = rg.R["sr3"]   # (rows, 100)
nrows, ncol = R1.shape
print(f"fan grid: {nrows} B-rows x {ncol} n-cols; B[{B.min():.2f},{B.max():.2f}]")

# n-axis (designed; could also derive from gate columns via calc_nD)
ns_cm = np.linspace(-0.7, -2.5, ncol)          # 1e12 cm^-2
n_si = np.abs(ns_cm) * 1e16                     # m^-2 (|n|)
FL = np.array([float(a.luttinger_frequency(n)) for n in n_si])   # F_L(n)

# Per-column SdH FFT. sdh_fft FFTs each column of the (rows, ncol) grid.
B_lo = max(0.4, B.min())
freqs, mag = a.sdh_fft(R1, B, b_range=(B_lo, min(7.9, B.max())), bg_degree=5)  # mag (ncol, nfreq)
print(f"FFT: freqs {freqs.min():.1f}-{freqs.max():.1f}T over B [{B_lo:.2f},{min(7.9,B.max()):.2f}]")

# Extract up to 2 dominant tones per column (freq > 4 T, prominence-gated)
F1 = np.full(ncol, np.nan); F2 = np.full(ncol, np.nan)
for c in range(ncol):
    m = mag[c]; sel = freqs > 4
    f, mm = freqs[sel], m[sel]
    if mm.max() <= 0: continue
    pk, _ = find_peaks(mm, prominence=mm.max()*0.15)
    if len(pk) == 0: continue
    order = pk[np.argsort(mm[pk])[::-1]]
    tops = sorted(f[order[:2]])
    F1[c] = tops[0]
    if len(tops) > 1: F2[c] = tops[1]

# Forward-model predicted F(n) curves over the n-range (|n|, hole=electron by symmetry in model)
aba_lo = np.full(ncol, np.nan); aba_hi = np.full(ncol, np.nan); abc_F = np.full(ncol, np.nan)
for c in range(ncol):
    try:
        _, fs = fsc.aba_fs(n_si[c]); fr = sorted(F for F, _ in fs)
        aba_lo[c] = fr[0]; aba_hi[c] = fr[-1] if len(fr) > 1 else fr[0]
        _, _, _, _, Ft = fsc.abc_fs(n_si[c]); abc_F[c] = Ft
    except Exception:
        pass

# Partition test: sum of the two extracted tones vs F_L
both = np.isfinite(F1) & np.isfinite(F2)
summ = F1 + F2
print(f"\ncolumns with 2 tones: {both.sum()}/{ncol}")
if both.sum():
    ratio = summ[both]/FL[both]
    print(f"(f1+f2)/F_L: median={np.nanmedian(ratio):.2f} (ABA expects ~1.0)")
print(f"single-tone columns: F1/F_L median={np.nanmedian((F1/FL)[np.isfinite(F1)&~both]):.2f} (ABC expects ~1.0)")

# --- Plots ---
fig, ax = plt.subplots(1, 3, figsize=(17, 5))
# (a) fan map Rxx(n,B)
Bs = B if B[0] < B[-1] else B[::-1]
R1p = R1 if B[0] < B[-1] else R1[::-1]
im = ax[0].pcolormesh(ns_cm, Bs, np.log10(np.abs(R1p)), shading="auto", cmap="inferno")
plt.colorbar(im, ax=ax[0], label="log10 Rxx (Ω)"); ax[0].set_xlabel("n (1e12 cm⁻²)"); ax[0].set_ylabel("B (T)"); ax[0].set_title("sr1 Rxx(n,B)")
# (b) F(n) extracted + model + F_L
ax[1].plot(ns_cm, FL, "k--", label="F_L = h|n|/4e")
ax[1].plot(ns_cm, aba_hi, "b-", lw=1, label="ABA f_BL (model)")
ax[1].plot(ns_cm, aba_lo, "c-", lw=1, label="ABA f_ML (model)")
ax[1].plot(ns_cm, abc_F, "g:", lw=2, label="ABC single (model)")
ax[1].scatter(ns_cm, F1, s=18, c="r", label="extracted F1")
ax[1].scatter(ns_cm, F2, s=18, c="orange", label="extracted F2")
ax[1].set_xlabel("n (1e12 cm⁻²)"); ax[1].set_ylabel("F (T)"); ax[1].set_title("F(n): data vs ABA/ABC"); ax[1].legend(fontsize=7)
# (c) partition test
ax[2].plot(ns_cm, FL, "k--", label="F_L")
ax[2].scatter(ns_cm[both], summ[both], s=18, c="purple", label="f1+f2")
ax[2].scatter(ns_cm[np.isfinite(F1)&~both], F1[np.isfinite(F1)&~both], s=18, c="r", label="single F1")
ax[2].set_xlabel("n (1e12 cm⁻²)"); ax[2].set_ylabel("Σf (T)"); ax[2].set_title("Luttinger partition: Σf vs F_L"); ax[2].legend(fontsize=7)
fig.suptitle(f"Run 4 Landau fan — hole D=0 — F(n) partition test  [{nrows}/250 rows]")
fig.tight_layout(); out = os.path.join(SCR, "run4_fan_Fn.png"); fig.savefig(out, dpi=110); print("saved", out)
