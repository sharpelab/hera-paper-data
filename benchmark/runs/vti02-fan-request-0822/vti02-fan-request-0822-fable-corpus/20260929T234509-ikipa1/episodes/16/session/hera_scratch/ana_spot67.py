# === Runs 6 + 7 — SdH spot checks (`sdh-spot-check`), D = 0: raw, onset, FFT vs F_L + model ===
import sys, warnings
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from hera.analysis import open_run, summarize_run, sdh_onset, sdh_fft, luttinger_frequency

sys.path.insert(0, str(Path.home() / "measurement_env/hera/models/tetralayer_fs_count"))
from fs_count_b0 import abab_fs

SPOTS = {6: +3.2e16, 7: -1.2e16}   # m^-2
SR0_GAIN = -1e6                     # device card
onsets = {}

# --- raw first: R = sr1_X / I_measured, per run ---
fig, axs = plt.subplots(2, 2, figsize=(12, 6.5))
for row, (rid, n_m2) in enumerate(SPOTS.items()):
    run = open_run(f"data/{rid}")
    print(summarize_run(run))
    o = np.argsort(run.col("magnet_field"))
    B = run.col("magnet_field")[o]
    I = run.col("sr0_X")[o] / SR0_GAIN
    R = run.col("sr1_X")[o] / I
    r_fs = 50e-6 / np.nanmedian(np.abs(I))    # sr1 sens 50 uV over measured I
    axs[row, 0].plot(B, R, lw=0.6, color="C0")
    axs[row, 0].set(xlabel="B (T)", ylabel="Rxx (Ω)",
                    title=f"run {rid}: n = {n_m2/1e16:+.1f}e12, raw (I_med {np.nanmedian(np.abs(I))*1e9:.1f} nA)")
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        on = sdh_onset(R, B, r_full_scale=r_fs)
    for wi in w: print(f"  [run {rid}] {wi.message}")
    print(on.summary())
    onsets[rid] = on
    # bg-subtracted vs 1/B above the well-sampled cut (1 T: run 6's sub-1 T leg is 50 mT — undersampled for the 7.1 T tone)
    cut = 1.0
    m = B >= cut
    dR = R[m] - np.polyval(np.polyfit(B[m], R[m], 5), B[m])
    axs[row, 1].plot(1 / B[m], dR, lw=0.5, color="C1")
    axs[row, 1].set(xlabel="1/B (1/T)", ylabel="ΔRxx (Ω)", title=f"run {rid}: bg-subtracted (B ≥ {cut} T)")
plt.tight_layout(); plt.show()

# --- FFT in 1/B vs F_L and the fs_count model tones ---
fig, axs = plt.subplots(1, 2, figsize=(12, 4))
for col, (rid, n_m2) in enumerate(SPOTS.items()):
    run = open_run(f"data/{rid}")
    o = np.argsort(run.col("magnet_field"))
    B = run.col("magnet_field")[o]
    I = run.col("sr0_X")[o] / SR0_GAIN
    R = run.col("sr1_X")[o] / I
    F_L = luttinger_frequency(abs(n_m2))
    for cut, ls in ((1.0, "-"), (1.5, ":")):     # stability: window change — real peaks hold, artifacts wander
        freqs, spec = sdh_fft(R[:, None], B, b_range=(cut, B.max()), bg_degree=5)
        axs[col].plot(freqs, spec[0] / spec[0].max(), ls, lw=0.9, label=f"cut {cut:.1f} T")
    axs[col].axvline(F_L, color="k", ls="--", lw=1, label=f"F_L = {F_L:.1f} T")
    _, orbs = abab_fs(n_m2)
    for F, _kF in orbs:
        axs[col].axvline(F, color="C3", ls="-.", lw=0.8)
    axs[col].plot([], [], "-.", color="C3", label=f"model ABAB {', '.join(f'{F:.1f}' for F, _ in orbs)} T")
    axs[col].set(xlabel="F (T)", ylabel="FFT (norm)", xlim=(0, 1.4 * F_L),
                 title=f"run {rid}: FFT in 1/B, n = {n_m2/1e16:+.1f}e12")
    axs[col].legend(fontsize=7)
plt.tight_layout(); plt.show()

for rid, on in onsets.items():
    print(f"run {rid}: onset_b = {on.onset_b:.2f} T "
          f"({'CENSORED at record edge' if any(t.censored for t in on.tones) else 'measured'})")
