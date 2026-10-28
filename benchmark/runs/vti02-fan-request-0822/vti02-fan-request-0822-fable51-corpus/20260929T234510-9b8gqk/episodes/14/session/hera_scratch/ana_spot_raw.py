"""Runs 6/7 — sdh-spot-check, raw first: R(B) per run (sr1 gain-divided), drain current, T_sample, gate currents."""
I_BIAS = 1e-8
fig, ax = plt.subplots(2, 3, figsize=(16, 7))
for row, rid in enumerate((6, 7)):
    r = run(rid); print(summarize_run(r))
    B = r.col("magnet_field"); R = r.col("sr1_X") / I_BIAS; I = r.col("sr0_X") / -1e6; T = r.col("T_sample")
    ax[row, 0].plot(B, R, lw=0.6); ax[row, 0].set_xlabel("B (T)"); ax[row, 0].set_ylabel("Rxx sr1 (Ohm)")
    ax[row, 0].set_title(f"run {rid}: {r.meta['comments'][1].split(';')[0]} — raw Rxx")
    ax[row, 1].plot(B, I * 1e9, lw=0.6, label="I drain (nA)"); ax[row, 1].set_xlabel("B (T)"); ax[row, 1].set_ylabel("I (nA)"); ax[row, 1].legend(loc="upper left")
    a2 = ax[row, 1].twinx(); a2.plot(B, T, "r", lw=0.6); a2.set_ylabel("T_sample (K)", color="r")
    ax[row, 2].plot(B, r.col("k_2400_tg_curr") * 1e12, lw=0.5, label="I_tg"); ax[row, 2].plot(B, r.col("k_2400_bg_curr") * 1e12, lw=0.5, label="I_bg")
    ax[row, 2].set_xlabel("B (T)"); ax[row, 2].set_ylabel("gate current (pA)"); ax[row, 2].legend()
    print(f"  R {R.min():.0f}..{R.max():.0f} Ohm (max {R.max()/(50e-6/I_BIAS)*100:.0f} % of 5 kOhm FS); I {I.min()*1e9:.2f}-{I.max()*1e9:.2f} nA; "
          f"T {T.min():.3f}-{T.max():.3f} K; |I_gate| max {max(abs(r.col('k_2400_tg_curr')).max(), abs(r.col('k_2400_bg_curr')).max())*1e12:.0f} pA")
fig.tight_layout(); plt.show()
