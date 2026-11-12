# SdH spot check H (run 5) — onset + 1/B FFT read (scratch iteration)
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from hera.analysis import open_run, sdh_onset, sdh_fft

I_BIAS = 20e-9
RUN = 5
r = open_run(f"data/{RUN}")
B = r.col("magnet_field")
chans = {"sr1_X": "sr1 T3-T4", "sr2_X": "sr2 B4-B5", "sr3_X": "sr3 T5-B6 (xy)"}
R = {ch: r.col(ch) / I_BIAS for ch in chans}
print(f"run {RUN}: B {B.min():.3f}-{B.max():.3f} T, {len(B)} pts, "
      f"T {r.col('T_sample').min():.3f}-{r.col('T_sample').max():.3f} K, "
      f"interrupted={r.interrupted}")
print(f"leakage: |Itg|max={np.abs(r.col('k_2400_tg_curr')).max():.2e}, "
      f"|Ibg|max={np.abs(r.col('k_2400_bg_curr')).max():.2e}")

# raw traces
fig, axes = plt.subplots(1, 3, figsize=(15, 4))
for ax, (ch, nm) in zip(axes, chans.items()):
    ax.plot(B, R[ch], lw=0.5)
    ax.set_xlabel("B (T)")
    ax.set_ylabel("R (Ohm)")
    ax.set_title(nm)
fig.suptitle(f"run {RUN} raw: hole n=-3.0e12, D=0, T=1.17 K, 20 nA")
fig.tight_layout()
fig.savefig("hera_scratch/sdh_h_raw.png", dpi=110)

# onset per Rxx channel
F_L = 31.02
for ch in ("sr1_X", "sr2_X"):
    on = sdh_onset(R[ch], B)
    print(f"{ch}: onset_b={on.onset_b}, clip_high_b={on.clip_high_b}, "
          f"consensus_freq={on.consensus_freq}")

# FFT above onset (start with cutoff = onset; stability vs cutoff below)
fig2, axes2 = plt.subplots(1, 2, figsize=(12, 4))
for ax, ch in zip(axes2, ("sr1_X", "sr2_X")):
    on = sdh_onset(R[ch], B)
    cut = on.onset_b if on.onset_b else 1.0
    for c_mult, style in ((1.0, "-"), (1.25, "--"), (1.5, ":")):
        f, spec = sdh_fft(R[ch][:, None], B, b_range=(cut * c_mult, B.max()))
        ax.plot(f, spec[0], style, lw=0.9, label=f"cutoff {cut*c_mult:.2f} T")
    ax.axvline(F_L, color="r", lw=0.8, alpha=0.6)
    ax.text(F_L, ax.get_ylim()[1] * 0.95, " F_L", color="r", fontsize=8)
    ax.set_xlim(0, 80)
    ax.set_xlabel("F (T)")
    ax.set_title(f"{ch} FFT (onset {on.onset_b})")
    ax.legend(fontsize=7)
fig2.suptitle(f"run {RUN}: 1/B FFT vs F_L={F_L:.1f} T (hole n=-3.0e12)")
fig2.tight_layout()
fig2.savefig("hera_scratch/sdh_h_fft.png", dpi=110)
print("saved hera_scratch/sdh_h_raw.png, sdh_h_fft.png")
