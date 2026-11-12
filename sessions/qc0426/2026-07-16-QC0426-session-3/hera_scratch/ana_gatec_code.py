# Gate C raw: R = X/I_bias per channel + gate currents, all four legs (runs 0-3)
I_BIAS = 5e-9
LEGS = [0, 1, 2, 3]
fig, axes = plt.subplots(2, 4, figsize=(15, 6), sharex="col")
for j, rid in enumerate(LEGS):
    r = run(rid)
    v = r.col_at(1)
    axR, axI = axes[0, j], axes[1, j]
    for ch, lbl in [("sr1_X", "sr1 T3-T4"), ("sr2_X", "sr2 B4-B5"), ("sr3_X", "sr3 T5-B6 (xy)")]:
        axR.plot(v, r.col(ch) / I_BIAS, label=lbl, lw=0.8)
    axR.set_yscale("symlog", linthresh=10)
    axR.set_ylabel("R = X/I (Ω)")
    axR.set_title(f"run {rid}: {r.cols[1]}", fontsize=8)
    axR.legend(fontsize=6)
    axI.plot(v, r.col("k_2400_tg_curr") * 1e12, label="I_tg (pA)", lw=0.8)
    axI.plot(v, r.col("k_2400_bg_curr") * 1e12, label="I_bg (pA)", lw=0.8)
    axI.set_ylabel("I_gate (pA)")
    axI.set_xlabel(r.cols[1])
    axI.legend(fontsize=6)
fig.suptitle("QC0426 gate C — runs 0–3 (B=0, T≈1.17 K, 5 nA @ 13 Hz)")
fig.tight_layout()
