# Runs 4-6 reduction: Si inertness + first CNP cross-section (per-point I normalization)
from scipy.ndimage import gaussian_filter1d
SR0_GAIN = -1e6

fig, axs = plt.subplots(1, 3, figsize=(15, 4.2))
# Si surveys: drain current vs V_si
for i, lbl in ((4, "0 → +20 V"), (5, "+20 → −20 V")):
    g = run(i)
    axs[0].plot(g.col("dc205_smart_voltage"), np.abs(g.col("sr0_X") / SR0_GAIN) * 1e12,
                ".", ms=2, label=f"run {i}: {lbl}")
axs[0].set_title("Si survey: |I_drain| vs V_si (drive 10 mV)")
axs[0].set_xlabel("V_si (V)"); axs[0].set_ylabel("|I_drain| (pA)"); axs[0].legend()

# Run 6: normalized Rxx = sr_X / measured drain current
g = run(6)
v = g.col("k_2400_tg_volt")
i_dr = np.abs(g.col("sr0_X") / SR0_GAIN)
axs[1].plot(v, i_dr * 1e9, ".", ms=2)
axs[1].set_title("run 6: |I_drain| vs V_tg (drive 100 mV)")
axs[1].set_xlabel("V_tg (V)"); axs[1].set_ylabel("I (nA)")
for ch in ("sr1", "sr2", "sr3"):
    rx = g.col(f"{ch}_X") / i_dr
    axs[2].plot(v, rx / 1e3, ".", ms=2, label=ch)
    sm = gaussian_filter1d(rx, 3); pk = np.argmax(sm)
    print(f"run 6 {ch}: CNP V_tg={v[pk]:+.3f} V, R_peak={sm[pk]/1e3:.2f} kΩ, "
          f"flanks {sm[10]/1e3:.2f} / {sm[-10]/1e3:.2f} kΩ")
axs[2].set_title("run 6: Rxx = V/I_measured vs V_tg (V_bg=0)")
axs[2].set_xlabel("V_tg (V)"); axs[2].set_ylabel("Rxx (kΩ)"); axs[2].legend()
for ax in axs: ax.grid(alpha=0.3)
fig.tight_layout(); plt.show()
print(f"run 6 I_drain: med {np.median(i_dr)*1e9:.2f} nA (range {i_dr.min()*1e9:.2f}–{i_dr.max()*1e9:.2f})")
