# Run 0 read: CNP from the drain-current dip; leakage sanity; the clipping that
# motivated re-ranging sr1.
mc0 = g0.meta["measurement_config"]
vbg0 = g0.col("k_2400_bg_volt")
I0 = g0.col("sr0_X") / mc0["sr0_gain"]
Vx0 = g0.col("sr1_X")
itg0, ibg0 = g0.col("k_2400_tg_curr"), g0.col("k_2400_bg_curr")

SENS0 = 2e-6                                  # sr1 sensitivity during run 0
k0 = int(np.argmin(np.abs(I0)))
frac_clip = np.mean(np.abs(Vx0) > 0.95 * SENS0)
print(f"CNP from min|I|      : V_bg = {vbg0[k0]:+.4f} V")
print(f"I modulation         : {I0.max()*1e9:.3f} -> {I0.min()*1e9:.3f} nA "
      f"({100*(1-I0.min()/I0.max()):.2f} % dip)")
print(f"implied dR_2T        : {(1/I0.min() - 1/I0.max())/1e3:.0f} kOhm "
      f"(R_bias = {mc0['bias_resistor']:.0f} ohm sets dI/I = -dR_2T/R_bias)")
print(f"sr1 clipped fraction : {frac_clip:.1%} of points at >0.95 full scale")
print(f"leakage TG / BG      : {itg0.min()*1e12:+.0f}..{itg0.max()*1e12:+.0f} pA / "
      f"{ibg0.min()*1e12:+.0f}..{ibg0.max()*1e12:+.0f} pA")

fig, ax = plt.subplots(3, 1, figsize=(8, 8.5), sharex=True)
ax[0].plot(vbg0, I0 * 1e9, ".-", ms=3, lw=0.8)
ax[0].axvline(vbg0[k0], ls="--", c="r", lw=0.8, label=f"CNP {vbg0[k0]:+.3f} V")
ax[0].set_ylabel("I_drain (nA)"); ax[0].legend(fontsize=8)
ax[0].set_title("run 0 — gatec-liveness, V_tg = 0, B = 0, T = 1.17 K")
ax[1].plot(vbg0, Vx0 * 1e6, ".-", ms=3, lw=0.8)
ax[1].axhline(SENS0 * 1e6, ls=":", c="r", lw=0.9, label="sr1 full scale (2 uV)")
ax[1].set_ylabel("sr1 X (uV)"); ax[1].legend(fontsize=8)
ax[2].plot(vbg0, itg0 * 1e12, ".-", ms=3, lw=0.8, label="TG")
ax[2].plot(vbg0, ibg0 * 1e12, ".-", ms=3, lw=0.8, label="BG")
ax[2].set_ylabel("gate leakage (pA)"); ax[2].set_xlabel("V_bg (V)"); ax[2].legend(fontsize=8)
for a in ax:
    a.axvline(vbg0[k0], ls="--", c="r", lw=0.6)
fig.tight_layout()
