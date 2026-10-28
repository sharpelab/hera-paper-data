# Runs 6-7: SdH spot checks at D = 0 -- raw, onset, windowed FFT vs model tones
import sys
import numpy as np
import matplotlib.pyplot as plt
from hera.analysis import open_run, sdh_onset, sdh_fft, summarize_run

sys.path.insert(0, "/home/hera/measurement_env/hera/models/tetralayer_fs_count")
from fs_count_b0 import abab_fs, abca_mstar

I_BIAS = 10e-9                       # sr1 drive / 100 MOhm
R_FS = 50e-6 / I_BIAS                # 5 kOhm full scale
h_e, e_e = 6.62607015e-34, 1.602176634e-19

fig, axes = plt.subplots(3, 2, figsize=(13, 11))
for j, (fid, n12) in enumerate(((6, 3.2), (7, -1.2))):
    run = open_run(f"data/{fid}")
    print(summarize_run(run))
    B = run.col("magnet_field"); R = run.col("sr1_X") / I_BIAS
    o = np.argsort(B); B, R = B[o], R[o]
    F_L = h_e / (4 * e_e) * abs(n12) * 1e16
    on = sdh_onset(R, B, r_full_scale=R_FS)
    print(on.summary()); print()

    # raw (no detrend, no log)
    axes[0, j].plot(B, R, lw=0.6)
    axes[0, j].set(xlabel="B (T)", ylabel="Rxx (Ohm)",
                   title=f"run {fid}: n = {n12:+.1f}e12, D = 0 (raw)")

    # background-subtracted vs 1/B, window above onset (cutoff raised 25%)
    cut = max(on.onset_b * 1.25, 0.38)
    msk = B >= cut
    dR = R[msk] - np.polyval(np.polyfit(B[msk], R[msk], 7), B[msk])
    axes[1, j].plot(1 / B[msk], dR, lw=0.6)
    axes[1, j].set(xlabel="1/B (1/T)", ylabel="dRxx (Ohm)",
                   title=f"detrended (deg 7, B > {cut:.2f} T)")

    # FFT in 1/B + model markers
    freqs, spec = sdh_fft(R[:, None], B, b_range=(cut, B.max()), bg_degree=7)
    sp = spec[0] / spec[0].max()
    axes[2, j].plot(freqs, sp, lw=0.9)
    _, orbs = abab_fs(n12 * 1e16)
    for F, _kf in orbs:
        axes[2, j].axvline(F, color="g", ls=":", alpha=0.8)
    axes[2, j].axvline(F_L, color="r", ls="--")
    axes[2, j].axvline(abca_mstar(n12 * 1e16)[0], color="m", ls="-.", alpha=0.6)
    axes[2, j].set(xlim=(0, 1.35 * F_L), xlabel="F (T)", ylabel="FFT (norm)",
                   title=f"FFT: green=ABAB model, red=F_L={F_L:.1f} T, magenta=ABCA")
fig.tight_layout(); plt.show()
print("Take: electron side carries the fan (censored onset <= 0.30 T, tones to 29.5 T);"
      " hole side = low-|n| exception regime, capped at 1.27e12. Fan: e-side, D = 0.")
