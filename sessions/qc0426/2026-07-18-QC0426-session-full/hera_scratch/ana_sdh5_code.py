# run 5: raw traces, onset, FFT on the unclipped window
import numpy as np
import matplotlib.pyplot as plt
from hera.analysis import open_run, sdh_onset, sdh_fft, SdhOnsetError

run = open_run("data/5")
B = run.col_at(4)               # measured field (col 1 is the setpoint instance)
I_BIAS = 20e-9
SENS = {"sr1": 2e-6, "sr2": 1e-6, "sr3": 5e-5}

fig, axes = plt.subplots(3, 1, figsize=(11, 8), sharex=True)
onsets = {}
for ax, ch in zip(axes, ("sr1", "sr2", "sr3")):
    R = np.abs(run.col(f"{ch}_X")) / I_BIAS
    ax.plot(B, R, lw=0.5)
    rfs = SENS[ch] / I_BIAS
    ax.axhline(rfs, color="r", ls=":", lw=0.8)
    ax.set_ylabel(f"{ch} |R| (Ω)")
    try:
        on = sdh_onset(R, B, r_full_scale=rfs)
        onsets[ch] = on
        print(f"=== {ch} ===")
        print(on.summary())
    except SdhOnsetError as e:
        print(f"=== {ch} === no usable oscillations: {e}")
axes[-1].set_xlabel("B (T)")
fig.suptitle("run 5 raw: electron n=+6e12 D=0 (red dotted = sensitivity full scale)")
fig.tight_layout(); plt.show()

fig2, ax2 = plt.subplots(figsize=(10, 4.5))
for ch in ("sr1", "sr2"):
    on = onsets[ch]
    R = np.abs(run.col(f"{ch}_X")) / I_BIAS
    b_hi = on.clip_high_b if on.clip_high_b else B.max()
    freqs, spec = sdh_fft(R[:, None], B, b_range=(max(on.onset_b, 0.9), b_hi))
    ax2.plot(freqs, spec[0], lw=1, label=f"{ch} [{max(on.onset_b,0.9):.2f}–{b_hi:.2f} T]")
ax2.axvline(62.0, color="k", ls="--", lw=1, label="F_L = 62 T (geometry-prior scale)")
ax2.set_xlim(0, 120); ax2.set_xlabel("F (T)"); ax2.set_ylabel("FFT amp"); ax2.legend(fontsize=8)
fig2.suptitle("run 5 FFT (clip-truncated window — δF 2.5–5 T, preliminary only)")
fig2.tight_layout(); plt.show()

# free lever-arm cross-check from the Hall channel (low field, before QH structure)
m = (B > 0.5) & (B < 1.5)
Rxy = np.abs(run.col("sr3_X")) / I_BIAS
p = np.polyfit(B[m], Rxy[m], 1)
n_hall = 1 / (1.602e-19 * p[0]) * 1e-16
print(f"\nHall slope (0.5–1.5 T): {p[0]:.1f} Ω/T -> n_Hall = {n_hall:.2f} e12 cm^-2 (target +6.0; geometry-prior scale check)")
