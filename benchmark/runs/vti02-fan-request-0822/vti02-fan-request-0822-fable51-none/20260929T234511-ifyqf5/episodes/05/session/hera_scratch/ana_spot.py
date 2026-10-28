"""sdh-spot-check read on runs 6 (electron, n=+3.2e12) and 7 (hole, n=-1.2e12), both D = 0 (run-5 cal).
Raw R(B), R(1/B) with minima, sdh_onset per tone, FFT in 1/B vs the Luttinger (full-density) frequency.
"""
import sys, warnings
import numpy as np
import scipy.constants as cst
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.signal import find_peaks, savgol_filter
from hera.analysis import open_run, sdh_fft, sdh_onset, luttinger_frequency

warnings.simplefilter("ignore")
RUNS = {6: +3.2e12, 7: -1.2e12}  # cm^-2 (run-5 cal, region A)
FS = 50e-6 / 10e-9               # sr1 50 uV at 10 nA -> 5 kOhm full scale

fig, axes = plt.subplots(3, 2, figsize=(14, 11))
for k, (rid, n_cm2) in enumerate(RUNS.items()):
    r = open_run(f"data/{rid}")
    print(f"\n=== run {rid}: cols = {r.cols}")
    B = r.col("magnet_field"); I = r.col("sr0_X") / r.meta["measurement_config"]["sr0_gain"]
    V = r.col("sr1_X") / 1.0; Rs = V / I; R = np.abs(Rs)
    Tm = r.col("T_sample")
    o = np.argsort(B); B, R, Rs, I, Tm = B[o], R[o], Rs[o], I[o], Tm[o]
    x = r.col("sr1_X"); q = np.diff(np.unique(x)); q = q[q > 0]
    print(f"I_bias {np.median(I)*1e9:.3f} nA; R sign {np.sign(np.median(Rs)):+.0f}; R range {R.min():.1f}-{R.max():.0f} Ohm; "
          f"T_sample {Tm.min():.3f}-{Tm.max():.3f} K; sr1_X quantum ~{q.min()*1e9:.2f} nV (= {q.min()/10e-9:.3f} Ohm), FS {FS:.0f} Ohm")
    n_si = abs(n_cm2) * 1e4
    F_L = float(luttinger_frequency(n_si))
    print(f"n = {n_cm2:+.2e} cm^-2 -> F_L (single 4-fold FS) = {F_L:.1f} T; nu = n h/(eB): nu(10 T) = {n_si*cst.h/(cst.e*10):.1f}")

    # minima / maxima in B > 1.5 T on a lightly smoothed trace
    sel = B > 1.5
    Rs_ = savgol_filter(R[sel], 7, 2); Bs_ = B[sel]
    mins, _ = find_peaks(-Rs_, prominence=8); maxs, _ = find_peaks(Rs_, prominence=8)
    nu_min = n_si * cst.h / (cst.e * Bs_[mins]); nu_max = n_si * cst.h / (cst.e * Bs_[maxs])
    print("minima  B (T) / R / nu(cal): " + ", ".join(f"{b:.2f}/{rr:.0f}/{v:.1f}" for b, rr, v in zip(Bs_[mins], Rs_[mins], nu_min)))
    print("maxima  B (T) / R / nu(cal): " + ", ".join(f"{b:.2f}/{rr:.0f}/{v:.1f}" for b, rr, v in zip(Bs_[maxs], Rs_[maxs], nu_max)))
    if len(mins) > 2:
        inv = 1 / Bs_[mins]; d = np.diff(inv)
        print(f"1/B spacing of minima: {np.round(d, 4)} -> local F = {np.round(1/d, 1)} T")

    # onset
    try:
        on = sdh_onset(R, B, b_lo=0.5, r_full_scale=FS)
        print(on.summary())
    except Exception as e:
        print("sdh_onset:", type(e).__name__, e)

    # FFT in 1/B over (b_lo, 10)
    for blo in (2.0, 3.0):
        f, sp = sdh_fft(R[:, None], B, b_range=(blo, B.max()), nfft=2048, bg_degree=3, log=False)
        sp = sp[0]; m = f > 2
        pk, _ = find_peaks(sp[m], prominence=0.1 * sp[m].max())
        top = sorted(zip(sp[m][pk], f[m][pk]), reverse=True)[:6]
        print(f"FFT b_range ({blo}, 10): resolution dF = {1/(1/blo - 1/B.max()):.1f} T; peaks F/amp: " + ", ".join(f"{ff:.1f}/{a:.2g}" for a, ff in top))
        if blo == 2.0: f2, sp2 = f, sp

    ax = axes[0, k]; ax.plot(B, R, lw=0.8); ax.set_xlabel("B (T)"); ax.set_ylabel("|Rxx| (Ohm)")
    ax.set_title(f"run {rid}: n = {n_cm2/1e12:+.1f}e12, D = 0 — raw R(B) (sr1 50 uV, FS {FS:.0f} Ohm)")
    ax.plot(Bs_[mins], Rs_[mins], "rv", ms=4); ax.plot(Bs_[maxs], Rs_[maxs], "g^", ms=4)
    ax = axes[1, k]; s2 = B > 1.0; ax.plot(1 / B[s2], R[s2], lw=0.8); ax.set_xlabel("1/B (1/T)"); ax.set_ylabel("|Rxx| (Ohm)")
    for b, v in zip(Bs_[mins], nu_min): ax.axvline(1 / b, color="r", lw=0.4, alpha=0.5); ax.text(1 / b, R[s2].max() * 0.95, f"{v:.0f}", fontsize=6, ha="center", color="r")
    ax.set_title("R vs 1/B; red = minima, label = nu from run-5 n (uncalibrated scale)")
    ax = axes[2, k]; ax.plot(f2, sp2 / sp2[f2 > 2].max(), lw=0.8); ax.set_xlim(0, 80); ax.set_xlabel("F (T)"); ax.set_ylabel("FFT amp (norm)")
    ax.axvline(F_L, color="k", ls="--", lw=0.8, label=f"F_L = {F_L:.1f} T (full n, 4-fold)")
    for frac, lab in ((0.5, "F_L/2"), (0.25, "F_L/4")): ax.axvline(F_L * frac, color="gray", ls=":", lw=0.7)
    ax.legend(fontsize=7); ax.set_title("SdH FFT in 1/B, B in (2, 10) T, cubic bg")
fig.tight_layout(); fig.savefig("hera_scratch/spot_runs67.png", dpi=110)
print("\nsaved hera_scratch/spot_runs67.png")
