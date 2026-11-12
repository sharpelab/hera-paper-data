"""Step 3 read: SdH spot checks runs 6 (electron n=+3.2e12) and 7 (hole n=-1.2e12).
Onset (hera.analysis.sdh_onset), 1/B FFT, tone set vs F_L and the tetralayer model."""
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, sdh_onset, sdh_fft, luttinger_frequency

sys.path.insert(0, "/home/hera/measurement_env/hera/models/tetralayer_fs_count")
import fs_count_b0 as m

I_BIAS = 10e-9          # A (drive/100 MOhm); sr1 gain = 1
R_FS = 50e-6 / I_BIAS   # 5 kOhm full scale at sr1 sens 50 uV

SPOTS = {6: +3.2, 7: -1.2}   # file_id -> n (1e12 cm^-2)

fig, axes = plt.subplots(3, 2, figsize=(13, 11))

for col, (rid, n12) in enumerate(SPOTS.items()):
    run = open_run(f"data/{rid}")
    B = run.col("magnet_field")
    I = run.col("sr0_X") / run.meta["measurement_config"]["sr0_gain"]
    R = run.col("sr1_X") / I            # sr1 gain = 1 (device card)
    R = np.abs(R)
    o = np.argsort(B); B, R = B[o], R[o]

    n_si = n12 * 1e12 * 1e4              # cm^-2 -> m^-2
    F_L = float(luttinger_frequency(n_si))
    print(f"\n{'='*70}\nrun {rid}: n = {n12:+.2f}e12 cm^-2, F_L = {F_L:.2f} T")
    print(f"  R range {R.min():.1f}-{R.max():.1f} Ohm (full scale {R_FS:.0f} Ohm, "
          f"max {100*R.max()/R_FS:.1f} % FS); {len(B)} pts, B {B.min():.2f}-{B.max():.2f} T")

    # --- model expectation at this density ---
    try:
        _, orbs = m.abab_fs(n12)
        ms = m.abab_mstar(n12)
        print(f"  model ABAB orbits: " + ", ".join(f"F={f:.2f} T (m*={mm:.3f})" for (f, _), (_, mm) in zip(orbs, ms)))
        tot = sum(f for f, _ in orbs)
        print(f"    sum {tot:.2f} T vs F_L {F_L:.2f} T; partition "
              + " / ".join(f"{f/F_L:.3f}" for f, _ in orbs))
    except Exception as e:
        print("  ABAB model:", e)
    try:
        Fa, ma = m.abca_mstar(n12)
        print(f"  model ABCA: F = {Fa:.2f} T (m* = {ma:.3f}), F/F_L = {Fa/F_L:.3f}")
    except Exception as e:
        print("  ABCA model:", e)

    # --- onset ---
    try:
        on = sdh_onset(R, B, r_full_scale=R_FS)
        print("  " + on.summary().replace("\n", "\n  "))
        onset_b = on.onset_b
    except Exception as e:
        print("  sdh_onset FAILED:", type(e).__name__, e)
        onset_b = None

    # --- FFT over a few low-B cutoffs (stability) ---
    ax = axes[0, col]
    ax.plot(B, R, lw=0.7)
    ax.set_xlabel("B (T)"); ax.set_ylabel(r"$R_{xx}$ ($\Omega$)")
    ax.set_title(f"run {rid}: raw  n = {n12:+.2f}e12, D = 0")
    if onset_b:
        ax.axvline(onset_b, color="r", ls="--", lw=1, label=f"onset {onset_b:.2f} T")
        ax.legend(fontsize=8)

    ax = axes[1, col]
    for cut in (0.5, 1.0, 1.5, 2.0):
        sel = B >= cut
        if sel.sum() < 30:
            continue
        f, spec = sdh_fft(R[sel][:, None], B[sel], bg_degree=5, nfft=4096)
        s = spec[0] / spec[0].max()
        ax.plot(f, s, lw=0.9, label=f"B > {cut} T ({sel.sum()} pts)")
        pk = [(f[i], s[i]) for i in range(2, len(f) - 2)
              if s[i] > s[i-1] and s[i] > s[i+1] and s[i] > 0.12 and f[i] > 1.0]
        pk.sort(key=lambda t: -t[1])
        print(f"  FFT B>{cut} T: peaks " + ", ".join(f"{fq:.1f} T ({a:.2f})" for fq, a in pk[:6])
              + f" | dF = {1/(1/cut - 1/B.max()):.2f} T")
    ax.axvline(F_L, color="k", ls="--", lw=1, label=f"$F_L$ = {F_L:.1f} T")
    ax.set_xlim(0, max(60, 1.6 * F_L)); ax.set_xlabel("F (T)"); ax.set_ylabel("|FFT| (norm)")
    ax.legend(fontsize=7); ax.set_title(f"run {rid}: 1/B FFT, cutoff ladder")

    # --- background-subtracted trace vs 1/B ---
    ax = axes[2, col]
    cut = onset_b or 1.0
    sel = B >= cut
    bg = np.polyval(np.polyfit(B[sel], R[sel], 5), B[sel])
    ax.plot(1 / B[sel], R[sel] - bg, lw=0.7)
    ax.set_xlabel("1/B (1/T)"); ax.set_ylabel(r"$\Delta R_{xx}$ ($\Omega$)")
    ax.set_title(f"run {rid}: background-subtracted, B > {cut:.2f} T")

plt.tight_layout()
plt.savefig("hera_scratch/spot_runs67.png", dpi=110)
print("\nwrote hera_scratch/spot_runs67.png")
