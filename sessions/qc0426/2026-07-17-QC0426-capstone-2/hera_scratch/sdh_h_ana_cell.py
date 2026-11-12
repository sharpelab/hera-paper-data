# Run 5 — SdH spot check H (hole, n=-3.0e12, D=0, 0.7->8 T). Raw first.
I_BIAS20 = 20e-9
r5 = open_run("data/5")
B5 = r5.col("magnet_field")
R5 = {ch: r5.col(ch) / I_BIAS20 for ch in ("sr1_X", "sr2_X", "sr3_X")}
print(f"run 5: {len(B5)} pts, B {B5.min():.2f}-{B5.max():.2f} T, "
      f"T {r5.col('T_sample').min():.3f}-{r5.col('T_sample').max():.3f} K "
      f"(high-B rise ~ Cernox magnetoresistance, rig card), interrupted={r5.interrupted}")
print(f"leakage pA-clean: |Itg|max={np.abs(r5.col('k_2400_tg_curr')).max():.2e}, "
      f"|Ibg|max={np.abs(r5.col('k_2400_bg_curr')).max():.2e}")

fig, axes = plt.subplots(1, 3, figsize=(15, 4))
for ax, ch in zip(axes, R5):
    ax.plot(B5, R5[ch], lw=0.5)
    ax.set_xlabel("B (T)")
    ax.set_ylabel("R (Ω)")
    ax.set_title(ch)
axes[0].axhline(2.5e3, color="r", lw=0.5, ls=":")
axes[0].text(1, 2.55e3, "sr1 nominal sens ceiling (soft-clip zone above)", fontsize=7, color="r")
fig.suptitle("run 5 raw: hole n=-3.0e12, D=0, T=1.17 K, 20 nA")
fig.tight_layout()
plt.show()
