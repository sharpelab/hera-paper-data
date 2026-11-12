"""Run 5 electron SdH spot check: onset + FFT read (scratch)."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, sdh_onset, sdh_fft, SdhOnsetError, luttinger_frequency

run = open_run("data/5")
cols = list(run.cols)
B = run.col_at(4)               # measured magnet_field (fp'd instance; index 1 is setpoint)
I_BIAS = 20e-9
SENS = {"sr1": 2e-6, "sr2": 1e-6, "sr3": 5e-5}
FL = 62.0

fig, axes = plt.subplots(3, 1, figsize=(11, 9), sharex=True)
tones_all = {}
for ax, ch in zip(axes, ("sr1", "sr2", "sr3")):
    R = np.abs(run.col(f"{ch}_X")) / I_BIAS
    ax.plot(B, R, lw=0.5)
    ax.set_ylabel(f"{ch} |R| (Ohm)")
    rfs = SENS[ch] / I_BIAS
    ax.axhline(rfs, color="r", ls=":", lw=0.8)
    try:
        on = sdh_onset(R, B, r_full_scale=rfs)
        print(f"=== {ch} ===")
        print(on.summary())
        tones_all[ch] = on
    except SdhOnsetError as e:
        print(f"=== {ch} === no usable oscillations: {e}")
axes[-1].set_xlabel("B (T)")
fig.suptitle("run 5: electron spot check n=+6e12, D=0 (raw R vs B; red dotted = full scale)")
fig.tight_layout(); fig.savefig("hera_scratch/sdh_e_raw.png", dpi=110)

# FFT on the usable (unclipped, above-onset) window per channel
fig2, ax2 = plt.subplots(figsize=(10, 5))
for ch in ("sr1", "sr2"):
    if ch not in tones_all:
        continue
    on = tones_all[ch]
    R = np.abs(run.col(f"{ch}_X")) / I_BIAS
    b_hi = on.clip_high_b if on.clip_high_b else B.max()
    cut = max(on.onset_b, 0.9)
    freqs, spec = sdh_fft(R[:, None], B, b_range=(cut, b_hi))
    ax2.plot(freqs, spec[0], lw=1, label=f"{ch} [{cut:.2f}-{b_hi:.2f} T]")
ax2.axvline(FL, color="k", ls="--", lw=1, label=f"F_L = {FL:.0f} T (n=+6e12, geometry-prior scale)")
ax2.set_xlabel("F (T)"); ax2.set_ylabel("FFT amp (log-detrended)")
ax2.set_xlim(0, 120); ax2.legend(fontsize=8)
fig2.suptitle("run 5: SdH FFT in 1/B vs F_L")
fig2.tight_layout(); fig2.savefig("hera_scratch/sdh_e_fft.png", dpi=110)
print("saved figs")
