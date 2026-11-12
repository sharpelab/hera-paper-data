# Gate C — liveness (gate-current-sanity-check), runs 0-3. Raw first.
LEGS = [
    (0, "TG 0→+3 V", "k_2400_tg_volt"),
    (1, "TG 0→−3 V", "k_2400_tg_volt"),
    (2, "BG 0→+4.5 V", "k_2400_bg_volt"),
    (3, "BG 0→−4.5 V", "k_2400_bg_volt"),
]
I_BIAS = 1e-9  # 0.1 V drive / 100 MOhm (liveness current)

fig, axes = plt.subplots(2, 4, figsize=(16, 6), sharey="row")
for j, (fid, label, sweptcol) in enumerate(LEGS):
    r = open_run(f"data/{fid}")
    v = r.col(sweptcol)
    axes[0, j].plot(v, r.col("k_2400_tg_curr") * 1e12, lw=0.8, label="I_tg")
    axes[0, j].plot(v, r.col("k_2400_bg_curr") * 1e12, lw=0.8, label="I_bg")
    axes[0, j].set_title(f"run {fid}: {label}")
    axes[0, j].set_ylabel("I_gate (pA)")
    axes[0, j].legend(fontsize=7)
    for ch, nm in ((r.col("sr1_X"), "sr1 T3-T4"), (r.col("sr2_X"), "sr2 B4-B5"),
                   (r.col("sr3_X"), "sr3 T5-B6 (xy)")):
        axes[1, j].plot(v, ch / I_BIAS, lw=0.8, label=nm)
    axes[1, j].set_xlabel(f"{sweptcol} (V)")
    axes[1, j].set_ylabel("R = X/I_bias (Ω)")
    axes[1, j].set_yscale("symlog", linthresh=10)
    axes[1, j].legend(fontsize=7)
    itg, ibg = r.col("k_2400_tg_curr"), r.col("k_2400_bg_curr")
    print(f"run {fid} {label}: |Itg|max={np.abs(itg).max():.2e} A, "
          f"|Ibg|max={np.abs(ibg).max():.2e} A, "
          f"I_drain med={np.median(np.abs(r.col('sr0_X')/-1e6))*1e12:.0f} pA, "
          f"interrupted={r.interrupted}")
fig.suptitle("Gate C liveness: runs 0-3, drive ~1 nA @ 13 Hz, B=0.003 T, T=1.17 K")
fig.tight_layout()
plt.show()
