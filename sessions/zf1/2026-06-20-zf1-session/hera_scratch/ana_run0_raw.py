# Run 0 — Gate C liveness. Raw re-form from TSV with device-card arithmetic:
# current = sr1_X / sr1_gain ; R = (srN_X / gain) / I_bias ; I_bias = bias_V / bias_R.
g = run(0)
print(summarize_run(g))
mc = g.meta["measurement_config"]
Ibias = mc["bias_voltage_1"] / mc["bias_resistor"]
vbg = g.col_at(g.col_indices("k_bg_volt")[-1])      # readback (last occurrence)
i_sr1 = g.col("sr830_1_X") / mc["sr1_gain"]
R2 = (g.col("sr830_2_X") / mc["sr2_gain"]) / Ibias   # 5-4  (2-terminal)
R3 = (g.col("sr830_3_X") / mc["sr3_gain"]) / Ibias   # 30-31 (4-terminal Rxx)
itg, ibg = g.col("k_tg_curr"), g.col("k_bg_curr")

fig, ax = plt.subplots(2, 2, figsize=(11, 7))
fig.suptitle(f"Run 0 — Gate C liveness — k_bg @ k_tg=0, B~0, T=34mK, I_bias={Ibias*1e12:.0f}pA")
ax[0,0].plot(vbg, i_sr1*1e12, ".-", ms=3); ax[0,0].axhline(Ibias*1e12, color="r", ls=":")
ax[0,0].set(xlabel="k_bg (V)", ylabel="I sr830_1 (pA)", title="current 5-4 — pinned at I_bias (alive)")
ax[0,1].plot(vbg, R2/1e3, ".-", ms=3)
ax[0,1].set(xlabel="k_bg (V)", ylabel="R 2T (kΩ)", title="sr830_2 5-4 (2T) — CNP peak ~+0.1 V")
ax[1,0].plot(vbg, R3, ".-", ms=3, color="C2"); ax[1,0].axhline(0, color="k", lw=0.5)
ax[1,0].set(xlabel="k_bg (V)", ylabel="R 4T Rxx (Ω)", title="sr830_3 30-31 (4T Rxx) — CNP 657Ω @ k_bg~0")
ax[1,1].plot(vbg, np.abs(itg)*1e12, ".-", ms=3, label="|I_tg|")
ax[1,1].plot(vbg, np.abs(ibg)*1e12, ".-", ms=3, label="|I_bg|")
ax[1,1].axhline(100, color="r", ls=":", label="100 pA watch")
ax[1,1].set(xlabel="k_bg (V)", ylabel="leakage (pA)", title="gate leakage (nplci=10) — <45 pA"); ax[1,1].legend(fontsize=8)
plt.tight_layout(); plt.show()
