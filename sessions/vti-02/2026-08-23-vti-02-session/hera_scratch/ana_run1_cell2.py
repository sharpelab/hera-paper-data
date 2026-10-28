mc = g.meta["measurement_config"]
x = g.col("k_2400_bg_volt"); I = g.col("sr0_X") / mc["sr0_gain"]; R = g.col("sr1_X") / I
dx = np.sign(np.diff(x)); legs = np.split(np.arange(len(x)), np.where(np.diff(dx) != 0)[0] + 1)
fig, ax = plt.subplots(figsize=(9, 4))
for k, leg in enumerate(legs):
    if len(leg) > 5:
        ax.plot(x[leg], np.abs(R[leg]), lw=0.8, label=f"leg {k} ({'up' if dx[leg[0]] > 0 else 'down'})")
ax.set_xlabel("V_bg (V)"); ax.set_ylabel("|Rxx| (Ω)"); ax.legend(fontsize=8)
ax.set_title("run 1 — BG sweep at V_tg = 0, B = 0, 1.18 K")
from scipy.signal import find_peaks
leg = legs[1]; xs, rs = x[leg], np.abs(R[leg])
pk, _ = find_peaks(rs, prominence=15)
for p in pk:
    print(f"peak at V_bg = {xs[p]:+.3f} V: {rs[p]:.0f} Ω")
    ax.axvline(xs[p], color="k", lw=0.5, ls="--")
print(f"I_drain med {np.median(I)*1e9:.2f} nA; |Rxx| range {np.abs(R).min():.0f}–{np.abs(R).max():.0f} Ω; hysteresis (up-down) med |ΔR| = "
      f"{np.median(np.abs(np.interp(x[legs[0]], xs[::-1], rs[::-1]) - np.abs(R[legs[0]]))):.1f} Ω")
