"""Runs 6 & 7 — SdH spot checks (sdh-spot-check step 6 read).
Electron n=+3.2e12 (run 6, B 0->10 T) and hole n=-1.2e12 (run 7, B 10->0.3 T), D=0.
Outputs: raw MR, onset (hera.analysis.sdh_onset), 1/B FFT vs F_L, and the
fan-design numbers (B_lo, dF, Nyquist d(1/B)).
"""
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, sdh_onset, sdh_fft, luttinger_frequency, SdhOnsetError

I_BIAS = 1.0 / 100e6           # sr1 amplitude 1.0 V / 100 MOhm bias resistor
SR1_GAIN = 1.0
R_FS = 50e-6 / I_BIAS          # 5 kOhm full scale at sr1 sens 50 uV

SPOTS = {6: ("electron", +3.2), 7: ("hole", -1.2)}

fig, axes = plt.subplots(2, 3, figsize=(16, 8))

for row, (fid, (side, n12)) in enumerate(SPOTS.items()):
    run = open_run(f"data/{fid}")
    B = np.asarray(run.col("magnet_field"), float)
    R = np.asarray(run.col("sr1_X"), float) / SR1_GAIN / I_BIAS
    T = np.asarray(run.col("T_sample"), float)
    itg = np.abs(np.asarray(run.col("k_2400_tg_curr"), float))
    ibg = np.abs(np.asarray(run.col("k_2400_bg_curr"), float))
    o = np.argsort(B); B, R = B[o], R[o]

    F_L = float(luttinger_frequency(abs(n12) * 1e12))
    print(f"\n{'='*70}\nrun {fid} — {side}, n = {n12:+.2f}e12, F_L = {F_L:.2f} T")
    print(f"  N = {len(B)}, B {B.min():.3f} -> {B.max():.3f} T")
    print(f"  R: min {R.min():.1f}  max {R.max():.1f} Ohm   (full scale {R_FS:.0f}) "
          f"-> peak {100*R.max()/R_FS:.1f} % FS")
    print(f"  T_sample {T.min():.3f}-{T.max():.3f} K ; |I_tg|max {itg.max():.2e} A, |I_bg|max {ibg.max():.2e} A")

    # raw
    ax = axes[row, 0]
    ax.plot(B, R, lw=0.7)
    ax.axhline(R_FS, color="r", ls=":", label="sens full scale")
    ax.set(xlabel="B (T)", ylabel=r"$R_{xx}$ ($\Omega$)",
           title=f"run {fid} raw — {side} n={n12:+.1f}e12")
    ax.legend(fontsize=7)

    # onset
    try:
        on = sdh_onset(R, B, b_lo=max(0.3, B.min()), r_full_scale=R_FS)
        print("  --- sdh_onset ---")
        print("   " + on.summary().replace("\n", "\n   "))
        onset_b = on.onset_b
        tones = [(t.freq, t.onset_b, getattr(t, "censored", None), getattr(t, "marginal", None),
                  getattr(t, "harmonic_of", None)) for t in on.tones]
    except SdhOnsetError as e:
        print(f"  --- sdh_onset FAILED: {e}")
        on, onset_b, tones = None, None, []

    # background-subtracted trace above onset
    b0 = onset_b if onset_b else max(0.5, B.min())
    b_hi = on.clip_high_b if (on is not None and on.clip_high_b) else B.max()
    m = (B >= b0) & (B <= b_hi)
    bg = np.polyval(np.polyfit(B[m], R[m], 5), B[m])
    ax = axes[row, 1]
    ax.plot(1.0 / B[m], R[m] - bg, lw=0.8)
    ax.set(xlabel="1/B (1/T)", ylabel=r"$\Delta R_{xx}$ ($\Omega$)",
           title=f"run {fid} bg-subtracted, {b0:.2f}-{b_hi:.2f} T")

    # FFT
    ax = axes[row, 2]
    for cut in sorted({round(b0, 2), round(max(b0, 1.5), 2), round(max(b0, 2.5), 2)}):
        if cut >= b_hi - 0.5:
            continue
        f, spec = sdh_fft(R[:, None], B, b_range=(cut, b_hi), bg_degree=5, log=False)
        s = spec[0]
        ax.plot(f, s / s.max(), lw=1.0, label=f"cut {cut} T")
        k = f > 2.0
        pk = f[k][np.argsort(s[k])[::-1][:6]]
        print(f"  FFT cut {cut:.2f}-{b_hi:.2f} T: top peaks (T) = "
              + ", ".join(f"{p:.1f}" for p in sorted(pk))
              + f"   | dF = {1.0/(1.0/cut - 1.0/b_hi):.2f} T")
    ax.axvline(F_L, color="k", ls="--", label=f"$F_L$={F_L:.1f} T")
    for frac, lbl in ((0.724, "0.72"), (0.276, "0.28")):
        ax.axvline(frac * F_L, color="g", ls=":", lw=0.8)
    ax.set(xlabel="F (T)", ylabel="norm. amp", xlim=(0, max(1.6 * F_L, 60)),
           title=f"run {fid} 1/B FFT vs $F_L$")
    ax.legend(fontsize=7)

    # design numbers
    print("  --- fan design numbers from this spot ---")
    print(f"   Nyquist d(1/B) <= 1/(2 F_L) = {1/(2*F_L):.5f} 1/T  (prefer {1/(3*F_L):.5f})")
    if onset_b:
        for bmax in (8.0, 9.0, 10.0):
            print(f"   dF(onset {onset_b:.2f} -> {bmax:.0f} T) = "
                  f"{1.0/(1.0/onset_b - 1.0/bmax):.2f} T")

plt.tight_layout()
plt.savefig("hera_scratch/spot_checks.png", dpi=110)
print("\nwrote hera_scratch/spot_checks.png")
