"""SdH spot checks, runs 6 (electron n=+3.2e12) and 7 (hole n=-1.2e12), D=0.
Onset + FFT read per sdh-spot-check.md Verify; tones vs F_L.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, sdh_onset, sdh_fft, SdhOnsetError, luttinger_frequency

BASE = "/home/hera/measurements/zack/20260822-vti-02/data"
OUT = "/home/hera/measurements/zack/20260822-vti-02/hera_scratch"

SR1_SENS = 50e-6      # 50 uV, both runs (measurement_config comments)

for fid, n_cm2, label in [(6, 3.2e12, "electron"), (7, -1.2e12, "hole")]:
    run = open_run(f"{BASE}/{fid}")
    cfg = run.meta["measurement_config"]
    B = run.col("magnet_field")
    # sort ascending in B (run 7 descends)
    idx = np.argsort(B)
    B = B[idx]
    Icur = run.col("sr0_X")[idx] / cfg["sr0_gain"]        # measured drain current, A (signed by gain)
    V1 = run.col("sr1_X")[idx]                            # Rxx voltage, gain 1
    Ib = abs(np.median(Icur))
    R = V1 / np.median(Icur)                              # signed; flip to positive Rxx
    if np.median(R) < 0:
        R = -R
    FL = float(luttinger_frequency(abs(n_cm2) * 1e4))
    print(f"=== run {fid} ({label}) n={n_cm2:+.2e} cm^-2, F_L={FL:.1f} T ===")
    print(f"B {B.min():.3f} -> {B.max():.3f} T, N={len(B)}, I_bias(med)={Ib*1e9:.3f} nA")
    print(f"R(B_min)={R[:5].mean():.1f} ohm, R range {R.min():.1f}..{R.max():.1f} ohm")
    r_fs = SR1_SENS / Ib   # positive full-scale resistance
    print(f"r_full_scale = {r_fs:.0f} ohm; max|V1|/sens = {np.abs(V1).max()/SR1_SENS:.2f}")

    try:
        on = sdh_onset(R, B, r_full_scale=r_fs)
        print(on.summary())
        onset = on.onset_b
    except SdhOnsetError as e:
        print("SdhOnsetError:", e)
        onset = None

    fig, ax = plt.subplots(3, 1, figsize=(9, 10))
    ax[0].plot(B, R, lw=0.7)
    ax[0].set(xlabel="B (T)", ylabel="Rxx (ohm)", title=f"run {fid} {label} raw")
    # bg-subtracted view
    cut = onset if onset else 1.0
    m = B >= max(0.5, cut * 0.7)
    p = np.polyfit(B[m], R[m], 5)
    ax[1].plot(B[m], R[m] - np.polyval(p, B[m]), lw=0.7)
    ax[1].set(xlabel="B (T)", ylabel="dRxx (ohm)", title=f"bg-sub (deg5, B>{max(0.5, cut*0.7):.2f})")
    if onset:
        for a in ax[:2]:
            a.axvline(onset, color="r", ls="--", lw=0.8)
    # FFT above onset, plus stability: two cutoffs
    for cutoff, c in [(cut, "C0"), (cut * 1.3, "C1")]:
        try:
            freqs, spec = sdh_fft(R[:, None], B, b_range=(cutoff, B.max()))
            ax[2].plot(freqs, spec[0], c, lw=0.9, label=f"cutoff {cutoff:.2f} T")
        except Exception as e:
            print("fft fail", cutoff, e)
    ax[2].axvline(FL, color="k", ls=":", label=f"F_L={FL:.1f} T")
    ax[2].set(xlabel="F (T)", ylabel="FFT amp (log)", xlim=(0, FL * 1.6))
    ax[2].legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(f"{OUT}/spot_run{fid}.png", dpi=110)
    print(f"saved {OUT}/spot_run{fid}.png")
    # peak list from the finer FFT
    freqs, spec = sdh_fft(R[:, None], B, b_range=(cut, B.max()))
    s = spec[0]
    pk = [i for i in range(2, len(s) - 2) if s[i] > s[i-1] and s[i] > s[i+1] and s[i] > s.max() * 0.15 and freqs[i] > 2]
    print("FFT peaks (F [T], amp, F/F_L):")
    for i in pk:
        print(f"  {freqs[i]:7.2f}  {s[i]:8.3f}  {freqs[i]/FL:.3f}")
    print()
