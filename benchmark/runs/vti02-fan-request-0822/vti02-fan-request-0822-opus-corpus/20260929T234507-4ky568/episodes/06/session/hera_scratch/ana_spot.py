"""SdH spot-check read, runs 6 (electron n=+3.2e12) and 7 (hole n=-1.2e12):
raw R(B), background-subtracted dR(1/B), sdh_onset tone table, sdh_fft spectrum vs F_L."""
import sys, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, sdh_onset, sdh_fft, luttinger_frequency, SdhOnsetError

RUNS = {6: ("electron", +3.20e12), 7: ("hole", -1.20e12)}
I_BIAS = 10.0e-9          # sr1 drive / 100 MOhm, from metadata measurement_config
R_FS = 50e-6 / I_BIAS     # 50 uV sensitivity -> 5 kOhm full scale

fig, axes = plt.subplots(3, 2, figsize=(13, 10))
out = {}
for j, (rid, (side, n_cm2)) in enumerate(RUNS.items()):
    r = open_run(f"data/{rid}")
    B = r.col("magnet_field")
    R = r.col("sr1_X") / 1.0 / I_BIAS      # sr1_gain = 1 (device card)
    o = np.argsort(B); B, R = B[o], R[o]
    n_si = n_cm2 * 1e4                      # cm^-2 -> m^-2
    F_L = float(luttinger_frequency(abs(n_si)))
    print(f"\n===== run {rid} ({side}, n = {n_cm2:+.2e} cm^-2)  F_L = {F_L:.1f} T =====")
    print(f"  B {B.min():.2f}-{B.max():.2f} T, {len(B)} pts; R {R.min():.1f}-{R.max():.1f} Ohm "
          f"(full scale {R_FS:.0f} Ohm, max/fs = {R.max()/R_FS:.3f})")
    print(f"  T_sample {r.col('T_sample').min():.3f}-{r.col('T_sample').max():.3f} K")

    ax = axes[0, j]
    ax.plot(B, R, lw=0.7)
    ax.set_xlabel("B (T)"); ax.set_ylabel(r"$R_{xx}$ ($\Omega$)")
    ax.set_title(f"run {rid} raw — {side}, n = {n_cm2:+.2f}e12, $F_L$ = {F_L:.1f} T")

    try:
        on = sdh_onset(R, B, r_full_scale=R_FS)
        print(on.summary())
        out[rid] = on
        b_cut = on.onset_b
    except SdhOnsetError as e:
        print(f"  SdhOnsetError: {e}")
        out[rid] = None
        b_cut = 1.0

    # background-subtracted trace vs 1/B over the usable window
    hi = min(B.max(), out[rid].clip_high_b if out[rid] and out[rid].clip_high_b else B.max())
    m = (B >= b_cut) & (B <= hi)
    bg = np.polyval(np.polyfit(B[m], R[m], 5), B[m])
    ax = axes[1, j]
    ax.plot(1.0 / B[m], R[m] - bg, lw=0.8)
    ax.set_xlabel("1/B (1/T)"); ax.set_ylabel(r"$\Delta R_{xx}$ ($\Omega$)")
    ax.set_title(f"background removed, B $\\geq$ {b_cut:.2f} T")

    # FFT at a couple of cutoffs (stability)
    ax = axes[2, j]
    for cut, sty in ((b_cut, "-"), (max(b_cut * 1.5, b_cut + 0.5), "--")):
        if cut >= hi - 0.5:
            continue
        f, spec = sdh_fft(R[:, None], B, b_range=(cut, hi), bg_degree=5, nfft=2048, log=False)
        s = spec[0]
        ax.plot(f, s / s.max(), sty, lw=0.9, label=f"B > {cut:.2f} T")
        k = (f > 3) & (f < 3 * F_L)
        pk = f[k][np.argsort(s[k])[::-1]][:6]
        amp = np.sort(s[k])[::-1][:6]
        print(f"  FFT cut {cut:.2f}-{hi:.2f} T: top peaks (T) "
              + ", ".join(f"{p:.1f}[{a/amp[0]:.2f}]" for p, a in zip(pk, amp))
              + f"   | f/F_L = " + ", ".join(f"{p/F_L:.3f}" for p in pk))
    ax.axvline(F_L, color="k", ls=":", label=r"$F_L$")
    for frac, lab in ((0.72, "0.72"), (0.28, "0.28")):
        ax.axvline(frac * F_L, color="r", ls=":", lw=0.8)
    ax.set_xlim(0, 2.2 * F_L); ax.set_xlabel("F (T)"); ax.set_ylabel("|FFT| (norm)")
    ax.legend(fontsize=7); ax.set_title("1/B FFT vs $F_L$ (red: ABAB 0.72/0.28)")

fig.tight_layout()
fig.savefig("hera_scratch/spot_runs67.png", dpi=110)
print("\nwrote hera_scratch/spot_runs67.png")
