"""Spot-check analysis: runs 6 (electron, n=+3.2e12) & 7 (hole, n=-1.2e12).
Raw R(B), sdh_onset, FFT in 1/B, tones vs tetralayer fs_count model."""
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, sdh_onset, sdh_fft, SdhOnsetError, luttinger_frequency

sys.path.insert(0, "/home/hera/measurement_env/hera/models/tetralayer_fs_count")
import fs_count_b0 as M

RUNS = {
    6: dict(n=+3.2e16, label="electron  n=+3.2e12 cm^-2", fs=50e-6),
    7: dict(n=-1.2e16, label="hole      n=-1.2e12 cm^-2", fs=50e-6),
}
I_BIAS = 10e-9

fig, axes = plt.subplots(2, 3, figsize=(15, 8))
results = {}
for row, (rid, info) in enumerate(RUNS.items()):
    run = open_run(f"data/{rid}")
    B = run.col("magnet_field")
    R = run.col("sr1_X") / I_BIAS  # sr1 gain 1
    order = np.argsort(B)
    B, R = B[order], R[order]
    r_fs = info["fs"] / I_BIAS

    ax = axes[row, 0]
    ax.plot(B, R, lw=0.5)
    ax.set_xlabel("B (T)"); ax.set_ylabel("Rxx (Ohm)")
    ax.set_title(f"run {rid} raw — {info['label']}")

    # onset
    try:
        onset = sdh_onset(R, B, r_full_scale=r_fs)
        results[rid] = onset
        print(f"run {rid}: onset_b = {onset.onset_b:.3f} T")
        for t in onset.tones:
            print(f"   tone f={t.freq:7.2f} T  onset={t.onset_b:5.2f} T "
                  f"censored={t.censored} marginal={t.marginal} "
                  f"harm_of={t.harmonic_of} snr_max={np.max(t.snr):.1f} n_per={t.n_periods:.1f}")
        if onset.untracked:
            print(f"   untracked: {onset.untracked}")
        if getattr(onset, "clip_high_b", None):
            print(f"   CLIP above B={onset.clip_high_b}")
    except SdhOnsetError as e:
        print(f"run {rid}: SdhOnsetError: {e}")
        results[rid] = None

    # background-subtracted trace above 1.5 T
    m = B > 1.5
    bg = np.polyval(np.polyfit(B[m], R[m], 5), B[m])
    ax = axes[row, 1]
    ax.plot(B[m], R[m] - bg, lw=0.5)
    ax.set_xlabel("B (T)"); ax.set_ylabel("dRxx (Ohm)")
    ax.set_title(f"run {rid} bg-subtracted (deg5, B>1.5T)")

    # FFT (single column) over the usable window
    b_lo = results[rid].onset_b if results[rid] else 1.5
    freqs, spec = sdh_fft(R[:, None], B, b_range=(max(b_lo, 1.0), B.max()),
                          nfft=4096, log=False)
    ax = axes[row, 2]
    ax.plot(freqs, spec[0], lw=0.8)
    F_L = luttinger_frequency(info["n"])
    ax.axvline(abs(float(F_L)), color="r", ls="--", label=f"F_L={abs(float(F_L)):.1f} T")
    ax.set_xlim(0, 1.6 * abs(float(F_L)))
    ax.set_xlabel("F (T)"); ax.set_ylabel("|FFT|")
    ax.set_title(f"run {rid} FFT, B in [{max(b_lo,1.0):.2f},{B.max():.1f}] T")
    ax.legend()
    # top FFT peaks
    from scipy.signal import find_peaks
    pk, props = find_peaks(spec[0], height=0.05 * spec[0].max())
    top = sorted(zip(props["peak_heights"], freqs[pk]), reverse=True)[:8]
    print(f"run {rid}: FFT peaks (h, F): " +
          ", ".join(f"({h:.3g}, {f:.2f} T)" for h, f in top))
    print(f"run {rid}: F_L = {abs(float(F_L)):.2f} T")

# model expectations at the two densities
for rid, info in RUNS.items():
    n = info["n"]
    try:
        ab = M.abab_fs(n); ab_m = M.abab_mstar(n)
        print(f"run {rid} model ABAB: F = {ab}, m* = {ab_m}")
    except Exception as e:
        print(f"run {rid} model ABAB: {e}")
    try:
        ac = M.abca_fs(n); ac_m = M.abca_mstar(n)
        print(f"run {rid} model ABCA: F = {ac}, m* = {ac_m}")
    except Exception as e:
        print(f"run {rid} model ABCA: {e}")

fig.tight_layout()
fig.savefig("hera_scratch/spots_67.png", dpi=110)
print("saved hera_scratch/spots_67.png")
