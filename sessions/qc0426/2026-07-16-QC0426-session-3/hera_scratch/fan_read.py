# Landau-fan step-5 read: per-column FFT -> F(n) branches -> Luttinger partition
# + Onsager forward-model overlay (|n| <= 3.5e12 clamp).
# usage: menv python hera_scratch/fan_read.py <run_id> [b_lo_fft]
import sys
import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
import scipy.constants as cst
from hera.analysis import open_run, fan_grids, resistance_grids, sdh_fft

RID = int(sys.argv[1]) if len(sys.argv) > 1 else 9
B_LO_FFT = float(sys.argv[2]) if len(sys.argv) > 2 else 1.8

C_TG = cst.epsilon_0 * 3.0 / 15.6e-9
RATIO, N_OFF = 1.2839, -2.407e14
FL_PER_N12 = cst.h / (4 * cst.e) * 1e16  # F_L per 1e12 cm^-2 = 10.34 T

fan = fan_grids(open_run(f"data/{RID}"))
rg = resistance_grids(fan)
B = fan.slow[: fan.nrows]
vtg = fan.grid("k_2400_tg_volt")[0]
vbg = fan.grid("k_2400_bg_volt")[0]
n12 = ((C_TG * vtg + RATIO * C_TG * vbg) / cst.e + N_OFF) * 1e-16
print(f"fan run {RID}: {fan.nrows}/101 rows, B {B.min():.2f}..{B.max():.2f} T, n {n12[0]:.2f}..{n12[-1]:.2f}e12")

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# (a) raw fan map (sr1, log|R|)
R1 = np.abs(rg.R["sr1"])[: fan.nrows]
pm = axes[0, 0].pcolormesh(n12, B, np.log10(np.clip(R1, 1, None)), shading="auto", cmap="inferno")
axes[0, 0].set_xlabel("n (1e12 cm$^{-2}$)"); axes[0, 0].set_ylabel("B (T)")
axes[0, 0].set_title(f"run {RID}: log10 R_sr1 (raw fan)")
plt.colorbar(pm, ax=axes[0, 0])

# (b) per-column FFT map (sr1) + branch peaks
freqs, spec = sdh_fft(R1, B, b_range=(B_LO_FFT, B.max()), bg_degree=5)
spec_n = spec / (spec.max(axis=1, keepdims=True) + 1e-30)
pm = axes[0, 1].pcolormesh(n12, freqs, spec_n.T, shading="auto", cmap="viridis", vmax=1.0)
axes[0, 1].plot(n12, FL_PER_N12 * np.abs(n12), "w--", lw=1, label="F_L nominal")
axes[0, 1].set_ylim(0, 110); axes[0, 1].set_xlabel("n (1e12)"); axes[0, 1].set_ylabel("F (T)")
axes[0, 1].set_title("per-column FFT (sr1), norm per column")
axes[0, 1].legend(fontsize=7)

# branch extraction per column: strongest peaks
fML, fBL, fSUM = np.full(len(n12), np.nan), np.full(len(n12), np.nan), np.full(len(n12), np.nan)
for j in range(len(n12)):
    a = spec_n[j]
    m = freqs > 3
    pk, pr = find_peaks(a[m], height=0.15, prominence=0.08)
    fp, hp = freqs[m][pk], pr["peak_heights"]
    if len(fp) == 0:
        continue
    FLn = FL_PER_N12 * abs(n12[j])
    # f_BL: strongest peak in (0.5, 1.05)*F_L; f_ML: strongest below 0.45*F_L;
    # f_SUM: strongest within 15% of f_ML+f_BL (only if both exist)
    selB = (fp > 0.5 * FLn) & (fp < 1.05 * FLn)
    selM = fp < 0.45 * FLn
    if selB.any():
        fBL[j] = fp[selB][np.argmax(hp[selB])]
    if selM.any():
        fML[j] = fp[selM][np.argmax(hp[selM])]
    if np.isfinite(fML[j]) and np.isfinite(fBL[j]):
        tgt = fML[j] + fBL[j]
        selS = np.abs(fp - tgt) < 0.15 * tgt
        if selS.any():
            fSUM[j] = fp[selS][np.argmax(hp[selS])]
axes[0, 1].plot(n12, fML, "c.", ms=3, label="f_ML")
axes[0, 1].plot(n12, fBL, "r.", ms=3, label="f_BL")
axes[0, 1].plot(n12, fSUM, "y.", ms=2, label="f_sum")

# (c) Luttinger partition: (f_ML+f_BL) vs F_L with one global scale
ok = np.isfinite(fML) & np.isfinite(fBL)
lam = np.nansum((fML[ok] + fBL[ok]) * np.abs(n12[ok])) / np.nansum(FL_PER_N12 * n12[ok] ** 2)
print(f"global density rescale lambda = {lam:.4f} (plausible band 0.8-1.2)")
axes[1, 0].plot(np.abs(n12[ok]), fML[ok] + fBL[ok], "ko", ms=4, label="f_ML+f_BL")
nn = np.linspace(0, max(6.2, np.nanmax(np.abs(n12))), 50)
axes[1, 0].plot(nn, FL_PER_N12 * nn, "b--", lw=1, label="F_L nominal")
axes[1, 0].plot(nn, lam * FL_PER_N12 * nn, "r-", lw=1, label=f"F_L × λ={lam:.3f}")
resid = (fML[ok] + fBL[ok]) - lam * FL_PER_N12 * np.abs(n12[ok])
print(f"partition residual: rms {np.sqrt(np.nanmean(resid**2)):.2f} T over {ok.sum()} columns")
axes[1, 0].set_xlabel("|n| (1e12)"); axes[1, 0].set_ylabel("F (T)")
axes[1, 0].set_title(f"Luttinger partition: rms resid {np.sqrt(np.nanmean(resid**2)):.2f} T")
axes[1, 0].legend(fontsize=7)

# (d) Onsager overlay, |n| <= 3.5e12 (model clamp), density axis rescaled by lambda
try:
    sys.path.insert(0, r"C:\Users\DGG\measurement_env\hera\models\trilayer_fs_count")
    import fs_count_b0 as fsm

    n_model = np.linspace(0.5e16, 3.5e16, 25)
    aba_F = [sorted(F for F, _ in fsm.aba_fs(nm)[1]) for nm in n_model]
    abc_F = [fsm.abc_fs(nm)[4] for nm in n_model]
    nm12 = n_model * 1e-16
    aba_lo = [f[0] if len(f) > 1 else np.nan for f in aba_F]
    aba_hi = [f[-1] for f in aba_F]
    axes[1, 1].plot(nm12, aba_lo, "c-", lw=1.5, label="ABA ML (model)")
    axes[1, 1].plot(nm12, aba_hi, "r-", lw=1.5, label="ABA BL (model)")
    axes[1, 1].plot(nm12, abc_F, "g-", lw=1.5, label="ABC single (model)")
except Exception as exc:
    print("model overlay failed:", exc)
sel = ok & (np.abs(n12) <= 3.5 / lam)
axes[1, 1].plot(np.abs(n12[sel]) * lam, fML[sel], "c.", ms=5)
axes[1, 1].plot(np.abs(n12[sel]) * lam, fBL[sel], "r.", ms=5)
axes[1, 1].set_xlabel("|n| × λ (1e12, rescaled)"); axes[1, 1].set_ylabel("F (T)")
axes[1, 1].set_title("Onsager overlay (|n| ≤ 3.5e12 clamp), data rescaled by λ")
axes[1, 1].legend(fontsize=7)

fig.suptitle(f"Fan run {RID} — step-5 read (rows {fan.nrows}/101, FFT window {B_LO_FFT}–{B.max():.1f} T)")
fig.tight_layout()
out = f"hera_scratch/fan_read_{RID}_{fan.nrows}rows.png"
fig.savefig(out, dpi=120)
print("saved", out)
