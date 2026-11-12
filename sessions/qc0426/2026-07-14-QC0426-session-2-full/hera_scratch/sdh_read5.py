"""Run 5 (hole spot check) — onset + FFT read vs F_L."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, sdh_onset, sdh_fft, luttinger_frequency

run = open_run("data/5")
B = run.col("magnet_field")
I = 20e-9
R = {ch: run.col_at(run.col_indices(f"{ch}_X")[-1]) / I for ch in ("sr1", "sr2", "sr3")}

n_target = 6.0e16  # m^-2 (hole side, |n|)
F_L = luttinger_frequency(n_target)
print(f"F_L(|n|=6e12) = {float(F_L):.1f} T")

res = {}
for ch in ("sr1", "sr2"):
    o = sdh_onset(R[ch], B)
    print(f"{ch}: onset_b = {o.onset_b:.3f} T, clip_high_b = {o.clip_high_b:.3f} T, "
          f"consensus_freq = {o.consensus_freq:.1f} T")
    res[ch] = o

fig, axes = plt.subplots(2, 2, figsize=(14, 8))
for j, ch in enumerate(("sr1", "sr2")):
    o = res[ch]
    cut = max(o.onset_b * 1.2, o.onset_b + 0.1)
    axes[0, j].plot(B, R[ch], lw=0.6)
    axes[0, j].axvline(o.onset_b, color="r", ls="--", lw=0.8, label=f"onset {o.onset_b:.2f} T")
    axes[0, j].set_title(f"{ch} raw R(B)"); axes[0, j].set_xlabel("B (T)"); axes[0, j].legend()
    for cutoff, lbl in ((cut, f"cut {cut:.2f} T"), (cut * 1.4, f"cut {cut*1.4:.2f} T")):
        fr, mag = sdh_fft(R[ch], B, b_range=(cutoff, 8.0))
        axes[1, j].plot(fr, mag / mag.max(), lw=0.8, label=lbl)
    for k in (1, 2):
        axes[1, j].axvline(float(F_L) * k, color="k", ls=":" if k > 1 else "--", lw=0.8)
    axes[1, j].set_xlim(0, 160); axes[1, j].set_xlabel("F (T)")
    axes[1, j].set_title(f"{ch} FFT in 1/B (F_L dashed, 2F_L dotted)"); axes[1, j].legend(fontsize=8)
fig.suptitle("run 5 - hole side n=-6e12, D=0: onset + SdH FFT vs F_L")
fig.tight_layout(); fig.savefig("hera_scratch/sdh5_fft.png", dpi=110)

# peak table, sr1, main cut
o = res["sr1"]; cut = max(o.onset_b * 1.2, o.onset_b + 0.1)
fr, mag = sdh_fft(R["sr1"], B, b_range=(cut, 8.0))
from scipy.signal import find_peaks
pk, props = find_peaks(mag, height=mag.max() * 0.06, distance=5)
print("sr1 peaks (F [T], rel amp):")
for p in pk:
    print(f"  {fr[p]:7.2f}  {mag[p]/mag.max():.3f}")
print("saved hera_scratch/sdh5_fft.png")
