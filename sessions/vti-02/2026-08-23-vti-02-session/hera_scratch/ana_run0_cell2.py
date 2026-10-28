# Run 0: note sr0_X was stored already gain-divided (fp gain -1e6) — later runs store raw volts.
mc = g.meta["measurement_config"]
x = g.col("k_2400_tg_volt"); I = g.col("sr0_X"); R = g.col("sr1_X") / I
itg, ibg = g.col("k_2400_tg_curr"), g.col("k_2400_bg_curr")
dx = np.sign(np.diff(x)); legs = np.split(np.arange(len(x)), np.where(np.diff(dx) != 0)[0] + 1)
fig, ax = plt.subplots(2, 1, figsize=(9, 6), sharex=True)
for k, leg in enumerate(legs):
    if len(leg) > 5:
        ax[0].plot(x[leg], np.abs(R[leg]), lw=0.8, label=f"leg {k} ({'up' if dx[leg[0]] > 0 else 'down'})")
ax[0].set_ylabel("|Rxx| (Ω)"); ax[0].legend(fontsize=8); ax[0].set_title("run 0 — TG sweep at V_bg=0, B=0, 1.18 K")
ax[1].plot(x, itg * 1e12, lw=0.7, label="I_tg"); ax[1].plot(x, ibg * 1e12, lw=0.7, label="I_bg")
ax[1].set_ylabel("gate I (pA)"); ax[1].set_xlabel("V_tg (V)"); ax[1].legend()
print(f"I_drain med {np.median(I)*1e9:.2f} nA; |Rxx| med {np.median(np.abs(R)):.0f} Ω (min {np.abs(R).min():.0f}, max {np.abs(R).max():.0f})")
print(f"I_tg med {np.median(itg)*1e12:.0f} pA (std {np.std(itg)*1e12:.0f}); I_bg med {np.median(ibg)*1e12:.0f} pA (std {np.std(ibg)*1e12:.0f})")
