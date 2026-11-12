# Run 6 — SdH spot check E (electron, n=+3.0e12, D=0, 8->0.7 T). Raw first.
r6 = open_run("data/6")
o6 = np.argsort(r6.col("magnet_field"))
B6 = r6.col("magnet_field")[o6]
R6 = {ch: (r6.col(ch) / I_BIAS20)[o6] for ch in ("sr1_X", "sr2_X", "sr3_X")}
print(f"run 6: {len(B6)} pts, B {B6.min():.2f}-{B6.max():.2f} T (taken descending), "
      f"T {r6.col('T_sample').min():.3f}-{r6.col('T_sample').max():.3f} K, "
      f"interrupted={r6.interrupted}")
print(f"leakage: |Itg|max={np.abs(r6.col('k_2400_tg_curr')).max():.2e}, "
      f"|Ibg|max={np.abs(r6.col('k_2400_bg_curr')).max():.2e}")

fig, axes = plt.subplots(1, 3, figsize=(15, 4))
for ax, ch in zip(axes, R6):
    ax.plot(B6, R6[ch], lw=0.5)
    ax.set_xlabel("B (T)")
    ax.set_ylabel("R (Ω)")
    ax.set_title(ch)
fig.suptitle("run 6 raw: electron n=+3.0e12, D=0, T=1.17 K, 20 nA")
fig.tight_layout()
plt.show()

# onset + FFT + peaks (same discipline as run 5)
from hera.analysis import sdh_onset
fig2, axes2 = plt.subplots(1, 2, figsize=(12, 4))
peak_tables6 = {}
for ax, ch in zip(axes2, ("sr1_X", "sr2_X")):
    on = sdh_onset(R6[ch], B6)
    print(f"{ch}: onset_b = {on.onset_b:.2f} T, consensus_freq = {on.consensus_freq:.1f} T")
    for mult, style in ((1.15, "-"), (1.3, "--"), (1.5, ":")):
        f, spec = sdh_fft(R6[ch][:, None], B6, b_range=(mult * on.onset_b, 8.0))
        ax.plot(f, spec[0], style, lw=0.9, label=f"cutoff {mult:.2f}×onset")
    peak_tables6[ch] = peaks_of(f, spec[0])
    ax.axvline(F_L5, color="r", lw=0.8)
    ax.text(F_L5, ax.get_ylim()[1] * 0.93, " F_L(nom)", color="r", fontsize=8)
    ax.set_xlim(0, 80)
    ax.set_xlabel("F (T)")
    ax.set_title(ch)
    ax.legend(fontsize=7)
fig2.suptitle("run 6: 1/B FFT, cutoff-stability overlay")
fig2.tight_layout()
plt.show()

for ch, tbl in peak_tables6.items():
    f0 = min(tbl, key=lambda t: -t[1])[0]
    print(f"\n{ch} peaks — strongest f0 = {f0:.2f} T (F_L nominal {F_L5:.1f}):")
    for fp_, amp in tbl:
        kh = fp_ / f0
        tag = f"~{round(kh)}×f0 (Δ={abs(fp_-round(kh)*f0):.2f})" if abs(kh - round(kh)) < 0.2 else "independent"
        print(f"  F={fp_:6.2f}  amp={amp:5.2f}  {tag}")
