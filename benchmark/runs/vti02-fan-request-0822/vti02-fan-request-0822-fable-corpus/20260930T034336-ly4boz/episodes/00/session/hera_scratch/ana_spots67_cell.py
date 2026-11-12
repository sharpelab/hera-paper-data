# === Runs 6 & 7 — SdH spot checks at D = 0 (`sdh-spot-check`): raw first, onsets, FFT vs fs_count model ===
import sys
import numpy as np
import matplotlib.pyplot as plt
from hera.analysis import open_run, sdh_onset, sdh_fft, luttinger_frequency

if "/home/hera/measurement_env/hera/models/tetralayer_fs_count" not in sys.path:
    sys.path.insert(0, "/home/hera/measurement_env/hera/models/tetralayer_fs_count")
import fs_count_b0 as M

I_BIAS = 10e-9
R_FS = 50e-6 / I_BIAS          # fixed sr1 sensitivity, both runs
SPOTS = {6: ("electron", +3.2e16), 7: ("hole", -1.2e16)}   # n in m^-2

fig, axes = plt.subplots(2, 3, figsize=(15, 8))
for row, (rid, (side, n_si)) in enumerate(SPOTS.items()):
    run = open_run(f"data/{rid}")
    assert not run.interrupted, f"run {rid} interrupted"
    B, R = run.col("magnet_field"), run.col("sr1_X") / I_BIAS
    o = np.argsort(B)
    B, R = B[o], R[o]
    F_L = float(abs(luttinger_frequency(n_si)))

    # 0. raw FIRST
    ax = axes[row, 0]
    ax.plot(B, R, lw=0.5, color="k")
    ax.set(xlabel="B (T)", ylabel="Rxx (Ohm)",
           title=f"run {rid} raw — {side}, n = {n_si/1e16:+.1f}e12")

    # 1. tone onsets (canonical helper; censored = persists to record edge)
    onset = sdh_onset(R, B, r_full_scale=R_FS)
    print(f"run {rid} ({side}): onset_b = {onset.onset_b:.2f} T, F_L = {F_L:.1f} T")
    for t in sorted(onset.tones, key=lambda t: t.freq):
        print(f"   tone F = {t.freq:6.2f} T  onset = {t.onset_b:.2f} T  "
              f"censored={t.censored}  harmonic_of={t.harmonic_of}  "
              f"SNR_max={float(np.max(t.snr)):.0f}  F/F_L={t.freq/F_L:.3f}")
    if onset.untracked:
        print(f"   untracked: {onset.untracked}")

    # 2. background-subtracted trace above onset (deg-5 poly in B)
    m = B >= max(onset.onset_b, 0.3)
    dR = R[m] - np.polyval(np.polyfit(B[m], R[m], 5), B[m])
    ax = axes[row, 1]
    ax.plot(B[m], dR, lw=0.5)
    ax.set(xlabel="B (T)", ylabel="dRxx (Ohm)",
           title=f"run {rid} bg-subtracted, B > {max(onset.onset_b, 0.3):.2f} T")

    # 3. FFT in 1/B over the usable window, with model tones overlaid
    freqs, spec = sdh_fft(R[:, None], B,
                          b_range=(max(onset.onset_b, 0.3), float(B.max())),
                          nfft=4096, log=False)
    ax = axes[row, 2]
    ax.plot(freqs, spec[0], lw=0.8, color="k")
    ab_pair = M.abab_fs(n_si)[1]              # [(F, kF), ...] light, heavy
    F_abca = M.abca_fs(n_si)[4]
    for i, (F_ab, _) in enumerate(ab_pair):
        ax.axvline(F_ab, color="C0", ls=":", label="ABAB pair (model)" if i == 0 else None)
    ax.axvline(F_abca, color="C2", ls=":", label="ABCA (model)")
    ax.axvline(F_L, color="r", ls="--", label=f"F_L = {F_L:.1f} T")
    ax.set(xlim=(0, 1.4 * F_L), xlabel="F (T)", ylabel="|FFT|",
           title=f"run {rid} FFT in 1/B")
    ax.legend(fontsize=8)
    print(f"   model ABAB pair: {' + '.join(f'{F:.2f}' for F, _ in ab_pair)} T "
          f"(sum {sum(F for F, _ in ab_pair):.2f}); ABCA: {F_abca:.2f} T")

fig.tight_layout()
plt.show()
