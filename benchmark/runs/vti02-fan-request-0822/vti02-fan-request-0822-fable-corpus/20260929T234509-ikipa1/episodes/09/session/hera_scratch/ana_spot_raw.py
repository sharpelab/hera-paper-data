# Runs 6-7 (`sdh-spot-check`, D = 0, run-5 cal): raw Rxx(B) per side. Raw first — no detrend, no FFT.
I_BIAS = 10e-9  # sr1 gain 1, 100 MOhm bias resistor at 1 V drive
fig, ax = plt.subplots(2, 2, figsize=(12, 7))
for row, (i, side, n12) in enumerate(((6, "electron", +3.2), (7, "hole", -1.2))):
    r = run(i)
    B, R = r.col("magnet_field"), r.col("sr1_X") / I_BIAS
    o = np.argsort(B); B, R = B[o], R[o]
    itg, ibg = r.col("k_2400_tg_curr") * 1e12, r.col("k_2400_bg_curr") * 1e12
    print(f"run {i} ({side}, n = {n12:+.1f}e12, D = 0): B {B.min():.2f}->{B.max():.2f} T, {len(B)} pts, "
          f"R {R.min():.0f}-{R.max():.0f} Ohm (max {R.max()/5e3:.0%} of the 5 kOhm FS at 50 uV), "
          f"I_tg med {np.median(itg):+.0f} pA, I_bg med {np.median(ibg):+.0f} pA, "
          f"T {r.col('T_sample').mean():.3f} K, interrupted={r.interrupted}")
    ax[row, 0].plot(B, R, lw=0.7)
    ax[row, 0].set(xlabel="B (T)", ylabel="Rxx B_1-B_2 (Ohm)",
                   title=f"run {i} — {side}, n = {n12:+.1f}e12 cm$^{{-2}}$")
    m = B > 2.0
    ax[row, 1].plot(1 / B[m], R[m], lw=0.7)
    ax[row, 1].set(xlabel="1/B (1/T)", ylabel="Rxx (Ohm)", title=f"run {i} — 1/B view, B > 2 T")
fig.suptitle("sdh-spot-check raw: vti-02 Rxx(B) at D = 0 (runs 6-7, sr1 50 uV, T = 1.17 K)")
fig.tight_layout(); plt.show()
