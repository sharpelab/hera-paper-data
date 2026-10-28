"""sdh-spot-check read, runs 6 (n = +3.2e12) and 7 (n = -1.2e12), D = 0 (run-5 cal): raw R(B), R(1/B) + minima, onset, FFT vs F_L."""
import warnings
from scipy.signal import find_peaks, savgol_filter
warnings.simplefilter("ignore")

RUNS = {6: +3.2e12, 7: -1.2e12}     # cm^-2 (run-5 cal, region A; absolute scale = geometry prior)
FS = 50e-6 / 10e-9                  # sr1 50 uV at 10 nA -> 5 kOhm full scale
fig, axes = plt.subplots(3, 2, figsize=(14, 11))
for k, (rid, n_cm2) in enumerate(RUNS.items()):
    r = run(rid)
    B = r.col("magnet_field"); I = r.col("sr0_X") / r.meta["measurement_config"]["sr0_gain"]
    R = np.abs(r.col("sr1_X") / 1.0 / I); Tm = r.col("T_sample")
    o = np.argsort(B); B, R, I, Tm = B[o], R[o], I[o], Tm[o]
    n_si = abs(n_cm2) * 1e4; F_L = float(luttinger_frequency(n_si))
    print(f"=== run {rid}: n = {n_cm2/1e12:+.1f}e12 -> F_L = {F_L:.1f} T; I_bias {np.median(I)*1e9:.2f} nA; |R| {R.min():.1f}-{R.max():.0f} Ohm; "
          f"T_sample {Tm.min():.3f}-{Tm.max():.3f} K; nu(10 T) = {n_si*cst.h/(cst.e*10):.1f}")
    sel = B > 1.5; Rs_ = savgol_filter(R[sel], 7, 2); Bs_ = B[sel]
    mins, _ = find_peaks(-Rs_, prominence=8); maxs, _ = find_peaks(Rs_, prominence=8)
    nu_min = n_si * cst.h / (cst.e * Bs_[mins])
    print("  minima B/R/nu_cal: " + ", ".join(f"{b:.2f}/{rr:.0f}/{v:.1f}" for b, rr, v in zip(Bs_[mins], Rs_[mins], nu_min)))
    print("  1/B spacing of minima (1/T): " + ", ".join(f"{d:.3f}" for d in -np.diff(1 / Bs_[mins])))
    try:
        on = sdh_onset(R, B, b_lo=0.5, r_full_scale=FS); print(on.summary())
    except Exception as e:
        print("  sdh_onset:", type(e).__name__, e)
    f, sp = sdh_fft(R[:, None], B, b_range=(2.0, B.max()), nfft=2048, bg_degree=3, log=False); sp = sp[0]
    m = f > 2; pk, _ = find_peaks(sp[m], prominence=0.1 * sp[m].max())
    print(f"  FFT (2-10 T, dF {1/(1/2.0-1/B.max()):.1f} T) peaks: " + ", ".join(f"{ff:.1f} T" for _, ff in sorted(zip(sp[m][pk], f[m][pk]), reverse=True)[:5]))

    ax = axes[0, k]; ax.plot(B, R, lw=0.8); ax.plot(Bs_[mins], Rs_[mins], "rv", ms=4); ax.plot(Bs_[maxs], Rs_[maxs], "g^", ms=4)
    ax.set_xlabel("B (T)"); ax.set_ylabel("|Rxx| (Ohm)"); ax.set_title(f"run {rid}: n = {n_cm2/1e12:+.1f}e12, D = 0 — raw |Rxx|(B), sr1 50 uV (FS {FS:.0f} Ohm)")
    ax = axes[1, k]; s2 = B > 1.0; ax.plot(1 / B[s2], R[s2], lw=0.8); ax.set_xlabel("1/B (1/T)"); ax.set_ylabel("|Rxx| (Ohm)")
    for b, v in zip(Bs_[mins], nu_min):
        ax.axvline(1 / b, color="r", lw=0.4, alpha=0.5); ax.text(1 / b, R[s2].max() * 0.95, f"{v:.0f}", fontsize=6, ha="center", color="r")
    ax.set_title("Rxx vs 1/B — red: minima, label: nu from run-5 n (scale uncalibrated)")
    ax = axes[2, k]; ax.plot(f, sp / sp[m].max(), lw=0.8); ax.set_xlim(0, 80); ax.set_xlabel("F (T)"); ax.set_ylabel("FFT amp (norm)")
    ax.axvline(F_L, color="k", ls="--", lw=0.8, label=f"F_L = {F_L:.1f} T (full n, 4-fold)")
    for frac in (0.5, 0.25): ax.axvline(F_L * frac, color="gray", ls=":", lw=0.7)
    ax.legend(fontsize=7); ax.set_title("SdH FFT in 1/B, B in (2, 10) T, cubic B-space background")
fig.tight_layout(); plt.show()
