# Run 1 — TG leg @ 0.5 nA: drive validation + TG leakage to -7 V.
g1 = run(1)
print(summarize_run(g1))
mc1 = g1.meta["measurement_config"]; Ib1 = mc1["bias_voltage_1"]/mc1["bias_resistor"]
vtg = g1.col_at(g1.col_indices("k_tg_volt")[-1])
R3 = (g1.col("sr830_3_X")/mc1["sr3_gain"])/Ib1      # 4T Rxx
itg = np.abs(g1.col("k_tg_curr")); ibg = np.abs(g1.col("k_bg_curr"))
away = vtg < -2
print(f"4T Rxx: med(away) {np.median(R3[away]):.1f} Ω, noise floor ~{np.std(np.diff(R3[away]))/np.sqrt(2):.1f} Ω")
print(f"leakage |I_tg|max {itg.max()*1e12:.0f} pA @ k_tg={vtg[itg.argmax()]:+.2f} V")

fig, ax = plt.subplots(1, 2, figsize=(11, 4))
fig.suptitle(f"Run 1 — TG leg @ {Ib1*1e9:.1f} nA — 4T Rxx & leakage vs k_tg (k_bg=0, B~0)")
ax[0].plot(vtg, R3, ".-", ms=3, color="C2"); ax[0].axhline(0, color="k", lw=0.5)
ax[0].set(xlabel="k_tg (V)", ylabel="4T Rxx (Ω)", title="sr3 30-31: ~24 Ω metal, noise floor ~2.6 Ω")
ax[1].plot(vtg, itg*1e12, ".-", ms=3, label="|I_tg|"); ax[1].plot(vtg, ibg*1e12, ".-", ms=3, label="|I_bg|")
ax[1].axhline(100, color="r", ls=":", label="100 pA watch")
ax[1].set(xlabel="k_tg (V)", ylabel="leakage (pA)", title=f"|I_tg|max {itg.max()*1e12:.0f} pA @ −7 V — safe"); ax[1].legend(fontsize=8)
plt.tight_layout(); plt.show()
