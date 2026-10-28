# Runs 6-7: onset + 1/B FFT vs F_L and the model F(n) templates.
import sys
sys.path.insert(0, "/home/hera/measurement_env/hera/models/tetralayer_fs_count")
import numpy as np
import matplotlib.pyplot as plt
from hera.analysis import sdh_onset, sdh_fft
from fs_count_b0 import abab_fs, abab_mstar, abca_mstar

fig, ax = plt.subplots(1, 2, figsize=(12, 4))
for j, fid in enumerate((6, 7)):
    B, Rxx, i_med, lab, FL = spots[fid]
    m = B >= (1.0 if fid == 6 else 0.3)          # run 6: 10 mT segment only (Nyquist)
    on = sdh_onset(Rxx[m], B[m], r_full_scale=50e-6 / i_med)
    print(f"===== run {fid} ({lab}), F_L = {FL} T =====")
    print(on.summary())
    cutoff = max(on.onset_b, 1.0 if fid == 6 else 0.93)  # run 7: raise above onset until slow tones stabilize
    freqs, spec = sdh_fft(Rxx[m][:, None], B[m], b_range=(cutoff, B.max()), bg_degree=5)
    s = spec[0] / spec[0].max()
    ax[j].plot(freqs, s, lw=0.8)
    ax[j].axvline(FL, color="r", ls="--", label=f"F_L = {FL} T")
    ax[j].set_xlim(0, 45); ax[j].set_xlabel("F (T)"); ax[j].set_ylabel("FFT (norm)")
    ax[j].set_title(f"run {fid} FFT, cutoff {cutoff:.2f} T")
    ax[j].legend()
fig.tight_layout()

# Model templates at the two spot densities (fs_count_b0; n in m^-2)
print("\nmodel F(n) [T] at the spot densities:")
for n12 in (3.2, -1.2):
    ms = abab_mstar(n12 * 1e16)
    Ft, mt = abca_mstar(n12 * 1e16)
    print(f"  n = {n12:+.1f}e12: ABAB " + ", ".join(f"{F:.2f} (m*{m:.3f})" for F, m in ms)
          + f"  |  ABCA {Ft:.2f} (m*{mt:.3f})")
