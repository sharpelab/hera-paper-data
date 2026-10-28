# Run 7 — sdh-spot-check, hole side: n = -1.2e12 cm^-2, D = 0, B 10 -> 0.3 T (20 mT, ride-down), sr1 50 uV
from hera.analysis import sdh_onset

r = run(7)
print(summarize_run(r))
I_bias = 1.0 / r.meta["measurement_config"]["bias_resistor"]  # 10 nA
B = r.col("magnet_field"); o = np.argsort(B); B = B[o]
R = r.col("sr1_X")[o] / I_bias

# --- raw first ---
fig, ax = plt.subplots(figsize=(10, 3.5))
ax.plot(B, R, lw=0.6)
ax.set_xlabel("B (T)"); ax.set_ylabel("Rxx B_1-B_2 (Ohm)")
ax.set_title(f"run 7 raw: Rxx(B) at n = -1.2e12, D = 0, T = {r.col('T_sample').mean():.2f} K")
plt.show()

# --- onset ---
on = sdh_onset(R, B, r_full_scale=50e-6 / I_bias)
print(on.summary())

# --- FFT + model overlay (fs_count_b0, n = -1.2e12: ABAB pair 5.86/6.54 T, ABCA 12.41 T with m* = 1.1 -> LK-dead at T_e ~ 8 K) ---
F_L = float(luttinger_frequency(1.2e16))
fig, ax = plt.subplots(figsize=(10, 3.5))
for co, deg, sty in ((on.onset_b, 5, "-"), (on.onset_b * 1.3, 5, "--"), (on.onset_b, 7, ":")):
    f, s = sdh_fft(R[:, None], B, b_range=(co, B.max()), bg_degree=deg)
    norm = s[0][f > 3].max()
    ax.plot(f, s[0] / norm, sty, lw=1, label=f"cutoff {co:.2f} T, deg {deg}")
for x, lab in ((5.86, "ABAB heavy 5.86"), (6.54, "ABAB light 6.54"), (F_L, f"F_L / ABCA {F_L:.1f}")):
    ax.axvline(x, color="k", lw=0.7, alpha=0.5); ax.text(x, 1.02, f" {lab}", rotation=90, va="bottom", fontsize=7)
ax.set_xlim(0, 20); ax.set_ylim(0, 1.6)
ax.set_xlabel("F (T)"); ax.set_ylabel("FFT amp (norm to f > 3 T max)"); ax.legend(fontsize=8, loc="upper right")
ax.set_title("run 7 SdH FFT vs model tones (fs_count_b0 at n = -1.2e12)")
plt.show()
