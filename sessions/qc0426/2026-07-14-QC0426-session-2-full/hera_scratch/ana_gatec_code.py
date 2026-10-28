# Gate C — raw traces + gate currents, runs 0-3
I_BIAS = 5e-9
SR0_GAIN = -1e6
LEGS = [(0, "TG 0->+3 V", "k_2400_tg_volt"), (1, "TG 0->-3 V", "k_2400_tg_volt"),
        (2, "BG 0->+4.5 V", "k_2400_bg_volt"), (3, "BG 0->-4.5 V", "k_2400_bg_volt")]

fig, axes = plt.subplots(3, 4, figsize=(16, 9), sharex="col")
for j, (rid, title, swept) in enumerate(LEGS):
    r = run(rid)
    v = r.col_at(r.col_indices(swept)[0])
    itg = r.col_at(r.col_indices("k_2400_tg_curr")[-1])
    ibg = r.col_at(r.col_indices("k_2400_bg_curr")[-1])
    i_drain = r.col_at(r.col_indices("sr0_X")[-1]) / SR0_GAIN

    axes[0, j].plot(v, i_drain * 1e9, lw=0.8, color="k")
    axes[0, j].set_title(f"run {rid}: {title}")
    axes[0, j].set_ylim(0, 6)

    for ch, lbl in (("sr1_X", "sr1 T3-T4"), ("sr2_X", "sr2 B4-B5"), ("sr3_X", "sr3 T5-B6 (xy)")):
        x = r.col_at(r.col_indices(ch)[-1])
        axes[1, j].plot(v, x / I_BIAS, lw=0.8, label=lbl)
    axes[1, j].set_yscale("symlog", linthresh=10)

    axes[2, j].plot(v, itg * 1e12, lw=0.8, label="I_tg")
    axes[2, j].plot(v, ibg * 1e12, lw=0.8, label="I_bg")
    axes[2, j].set_ylim(-150, 150)
    axes[2, j].set_xlabel("swept gate (V)")

    print(f"run {rid} {title}: I_drain {i_drain.min()*1e9:.2f}-{i_drain.max()*1e9:.2f} nA, "
          f"|I_tg|max {abs(itg).max()*1e12:.0f} pA, |I_bg|max {abs(ibg).max()*1e12:.0f} pA, "
          f"interrupted={r.interrupted}")

axes[0, 0].set_ylabel("I_drain (nA)")
axes[1, 0].set_ylabel("R = X/I_bias (Ohm)")
axes[1, 0].legend(fontsize=7)
axes[2, 0].set_ylabel("I_gate (pA)")
axes[2, 0].legend(fontsize=7)
fig.suptitle("Gate C liveness - runs 0-3 (B=0, T=1.15 K, I_bias=5 nA)")
fig.tight_layout()
