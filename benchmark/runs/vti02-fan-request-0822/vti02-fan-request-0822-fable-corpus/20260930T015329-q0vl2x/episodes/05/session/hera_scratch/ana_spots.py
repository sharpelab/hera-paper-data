# Runs 6-7 sdh-spot-check analysis: raw -> FFT -> tones vs F_L and model
import sys
import numpy as np
import matplotlib.pyplot as plt
from hera.analysis import open_run, sdh_onset, sdh_fft, luttinger_frequency
sys.path.insert(0, "/home/hera/measurement_env/hera/models/tetralayer_fs_count")
from fs_count_b0 import abab_fs

I_BIAS = 10e-9
runs = {6: ("electron", +3.2e12), 7: ("hole", -1.2e12)}
fig, axes = plt.subplots(2, 3, figsize=(16, 8))
tone_sets = {}
for row, (rid, (side, n_cm2)) in enumerate(runs.items()):
    r = open_run(f"data/{rid}")
    B = r.col("magnet_field"); R = r.col("sr1_X") / I_BIAS  # sr1 gain 1
    o = np.argsort(B); B, R = B[o], R[o]
    F_L = float(luttinger_frequency(abs(n_cm2) * 1e4))

    ax = axes[row, 0]  # raw FIRST
    ax.plot(B, R, lw=0.5)
    ax.set(xlabel="B (T)", ylabel="Rxx (Ω)", title=f"run {rid} raw — {side} n={n_cm2/1e12:+.1f}e12")

    onset = sdh_onset(R, B, b_lo=0.3)
    tone_sets[rid] = onset
    fr, amp = sdh_fft(R[:, None], B, b_range=(1.0, float(B.max())), nfft=4096, log=False)
    a = np.asarray(amp).reshape(-1, len(fr))[0]
    ax = axes[row, 1]
    ax.plot(fr, a, lw=0.8)
    ax.axvline(F_L, color="k", ls="--", label=f"F_L = {F_L:.1f} T")
    _, orbs = abab_fs(n_cm2 * 1e4)
    for F, _kf in orbs:
        ax.axvline(F, color="C3", ls=":", alpha=0.8)
    ax.set(xlim=(0, 1.6 * F_L), xlabel="F (T)", title=f"run {rid} FFT 1–{B.max():.0f} T (red: model ABAB)")
    ax.legend(fontsize=8)

    ax = axes[row, 2]  # B-window split: breakdown/mixing tones strengthen with B
    Bmax = float(B.max()); Bmid = 0.5 * (1.0 + Bmax)
    for (b1, b2), c in [((1.0, Bmid), "C0"), ((Bmid, Bmax), "C1")]:
        fr2, amp2 = sdh_fft(R[:, None], B, b_range=(b1, b2), nfft=4096, log=False)
        a2 = np.asarray(amp2).reshape(-1, len(fr2))[0]
        ax.plot(fr2, a2 / a2.max(), lw=0.8, color=c, label=f"{b1:.1f}–{b2:.1f} T")
    ax.axvline(F_L, color="k", ls="--")
    ax.set(xlim=(0, 1.6 * F_L), xlabel="F (T)", title=f"run {rid} B-window split (norm)")
    ax.legend(fontsize=8)

    print(f"run {rid} ({side}, n={n_cm2/1e12:+.1f}e12): F_L={F_L:.2f} T, onset_b={onset.onset_b:.2f} T")
    for t in onset.tones:
        print(f"  f={t.freq:6.2f} T  onset={t.onset_b:5.2f} T  censored={t.censored}  f/F_L={t.freq/F_L:.3f}")

fig.tight_layout(); plt.show()

# Luttinger + partition, electron pair (7.11, 22.08) and hole pair (4.72, 6.59)
for rid, (f1, f2) in {6: (7.11, 22.08), 7: (4.72, 6.59)}.items():
    n = runs[rid][1]; F_L = float(luttinger_frequency(abs(n) * 1e4))
    print(f"run {rid}: f1+f2 = {f1+f2:.2f} T vs F_L = {F_L:.2f} -> scale {(f1+f2)/F_L:.3f}; "
          f"partition {f1/(f1+f2):.3f}/{f2/(f1+f2):.3f}")
