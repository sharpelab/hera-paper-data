"""SdH spot-check read: runs 6 (electron n=+3.2e12) and 7 (hole n=-1.2e12), D=0.
Onset via hera.analysis.sdh_onset, tones via sdh_fft; compare vs F_L and the
tetralayer model's F(n) table (fs_count_b0)."""
import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, sdh_onset, sdh_fft, SdhOnsetError

I_BIAS_R = 100e6  # bias resistor
SENS = 50e-6      # sr1 sensitivity both runs

runs = {}
for fid, nlabel, FL in ((6, "electron n=+3.2e12", 33.1), (7, "hole n=-1.2e12", 12.4)):
    r = open_run(f"data/{fid}")
    B = r.col("magnet_field")
    # gain-divided Rxx: sr1 unity gain, I_bias = drive amplitude / 100 MOhm
    amp = r.meta.get("measurement_config", {})
    x = r.col("sr1_X")
    # I_bias from sr0 (drain current) median as ground truth
    i_drain = np.abs(r.col("sr0_X") / -1e6)  # sr0_gain = -1E6
    i_med = np.median(i_drain)
    Rxx = x / i_med
    order = np.argsort(B)
    B, Rxx = B[order], Rxx[order]
    runs[fid] = (B, Rxx, nlabel, FL, i_med)
    print(f"run {fid}: {nlabel}  I_drain med = {i_med*1e9:.3f} nA, "
          f"R(B~0) = {np.median(Rxx[:10]):.1f} Ohm, R(max B) = {Rxx[-1]:.1f} Ohm, "
          f"Rxx range [{Rxx.min():.1f}, {Rxx.max():.1f}]")
    print(f"  T_sample: {r.col('T_sample').min():.3f}-{r.col('T_sample').max():.3f} K")
    print(f"  leakage |I_tg| max {np.abs(r.col('k_2400_tg_curr')).max()*1e12:.0f} pA, "
          f"|I_bg| max {np.abs(r.col('k_2400_bg_curr')).max()*1e12:.0f} pA")
    # full-scale check
    fs_frac = np.abs(x).max() / SENS
    print(f"  sr1 |X| max = {np.abs(x).max()*1e6:.2f} uV of {SENS*1e6:.0f} uV FS ({fs_frac*100:.0f}%)")

for fid in (6, 7):
    B, Rxx, nlabel, FL, i_med = runs[fid]
    print(f"\n===== run {fid} ({nlabel}), F_L = {FL} T =====")
    try:
        on = sdh_onset(Rxx, B, r_full_scale=SENS / i_med)
        print(on.summary())
        onset = on.onset_b
    except SdhOnsetError as e:
        print("SdhOnsetError:", e)
        onset = None
    if onset is None:
        continue
    # FFT above onset (and stability: two cutoffs, two bg degrees)
    for cutoff in (onset, min(onset * 1.3, onset + 0.5)):
        for deg in (3, 5):
            m = (B >= cutoff)
            freqs, spec = sdh_fft(Rxx[:, None], B, b_range=(cutoff, B.max()), bg_degree=deg)
            s = spec[0]
            s = s / s.max()
            # peak list: local maxima above 5% of max, f > 1 T
            pk = [
                (freqs[i], s[i])
                for i in range(1, len(s) - 1)
                if s[i] > s[i - 1] and s[i] > s[i + 1] and s[i] > 0.05 and freqs[i] > 1.0
            ]
            pk.sort(key=lambda t: -t[1])
            top = ", ".join(f"{f:.2f} T ({a:.2f})" for f, a in pk[:6])
            print(f"  cutoff {cutoff:.2f} T, bg_deg {deg}: peaks {top}")

# figures: raw + bg-subtracted + FFT
fig, axes = plt.subplots(3, 2, figsize=(12, 10))
for j, fid in enumerate((6, 7)):
    B, Rxx, nlabel, FL, i_med = runs[fid]
    axes[0, j].plot(B, Rxx, lw=0.6)
    axes[0, j].set_title(f"run {fid} raw Rxx — {nlabel}")
    axes[0, j].set_xlabel("B (T)"); axes[0, j].set_ylabel("Rxx (Ohm)")
    on = sdh_onset(Rxx, B, r_full_scale=SENS / i_med)
    cutoff = on.onset_b
    m = B >= cutoff
    p = np.polyfit(B[m], Rxx[m], 5)
    dR = Rxx[m] - np.polyval(p, B[m])
    axes[1, j].plot(1 / B[m], dR, lw=0.6)
    axes[1, j].set_title(f"dRxx vs 1/B (cutoff {cutoff:.2f} T)")
    axes[1, j].set_xlabel("1/B (1/T)"); axes[1, j].set_ylabel("dRxx (Ohm)")
    freqs, spec = sdh_fft(Rxx[:, None], B, b_range=(cutoff, B.max()), bg_degree=5)
    axes[2, j].plot(freqs, spec[0] / spec[0].max(), lw=0.8)
    axes[2, j].axvline(FL, color="r", ls="--", label=f"F_L = {FL} T")
    axes[2, j].set_xlim(0, FL * 1.6)
    axes[2, j].set_xlabel("F (T)"); axes[2, j].set_ylabel("FFT (norm)")
    axes[2, j].legend()
fig.tight_layout()
fig.savefig("hera_scratch/spot_checks_67.png", dpi=110)
print("\nsaved hera_scratch/spot_checks_67.png")
