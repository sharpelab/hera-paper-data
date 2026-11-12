# Run 4 — 0 T gatemap: raw re-formed maps (TSV, not plot.png)
I_BIAS5 = 5e-9
r4 = open_run("data/4")
n_slow = n_fast = 101
VBG4 = r4.col("k_2400_bg_volt").reshape(n_slow, n_fast)[:, 0]
VTG4 = r4.col_at(2).reshape(n_slow, n_fast)[0, :]

fig, axes = plt.subplots(1, 4, figsize=(18, 4.5))
for ax, ch in zip(axes[:3], ("sr1_X", "sr2_X", "sr3_X")):
    R = (r4.col(ch) / I_BIAS5).reshape(n_slow, n_fast)
    pm = ax.pcolormesh(VTG4, VBG4, np.log10(np.clip(np.abs(R), 1, None)), shading="auto")
    plt.colorbar(pm, ax=ax, label="log10 |R| (Ω)")
    ax.set_title(ch)
    ax.set_xlabel("V_tg (V)")
axes[0].set_ylabel("V_bg (V)")
# gate leakage over the whole map
itg, ibg = r4.col("k_2400_tg_curr"), r4.col("k_2400_bg_curr")
axes[3].hist(itg * 1e12, bins=80, alpha=0.6, label=f"I_tg (max {np.abs(itg).max()*1e12:.0f} pA)")
axes[3].hist(ibg * 1e12, bins=80, alpha=0.6, label=f"I_bg (max {np.abs(ibg).max()*1e12:.0f} pA)")
axes[3].set_xlabel("I_gate (pA)")
axes[3].legend(fontsize=8)
axes[3].set_title("gate currents, all 10201 pts")
fig.suptitle("run 4 — 0 T gatemap, raw (5 nA bias, T = 1.17 K)")
fig.tight_layout()
plt.show()
print(f"interrupted={r4.interrupted}; T range {r4.col('T_sample').min():.3f}-{r4.col('T_sample').max():.3f} K")
