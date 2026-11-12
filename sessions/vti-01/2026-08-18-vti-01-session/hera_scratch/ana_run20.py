# Run 20 — tau=300ms ML descent: the ML pocket confirmed at n = -1.74
g = run(20)
print(summarize_run(g))
plot_raw(g)

B = g.col("magnet_field")
i_dr = np.abs(g.col("sr0_X")) / 1e6
fig, ax = plt.subplots(figsize=(8, 4.2))
for ch, off in (("sr1", 0), ("sr3", 1.1)):
    R = (g.col(f"{ch}_X") / i_dr)[:, None]
    f, s = sdh_fft(R, B, b_range=(0.9, 5.0), bg_degree=5)
    ax.plot(f, s[0] / s[0].max() + off, lw=1, label=f"{ch} (bg5)")
    f, s = sdh_fft(R, B, b_range=(0.9, 5.0), bg_degree=6)
    ax.plot(f, s[0] / s[0].max() + off, lw=0.8, ls="--", label=f"{ch} (bg6)")
for v, lbl in ((4.4, "f_ML"), (12.0, "f_BL−f_ML"), (16.4, "f_BL = A"), (8.35, "A/2 mod")):
    ax.axvline(v, color="gray", ls=":", lw=0.7)
    ax.text(v, 2.25, lbl, rotation=90, fontsize=7, ha="right")
ax.axvline(1.14 * 18.03, color="r", ls="--", lw=0.8)   # 1.14*F_L(1.74)
ax.text(1.14 * 18.03, 2.25, "1.14·F_L", rotation=90, fontsize=7, color="r", ha="right")
ax.set_xlim(0, 30); ax.set_xlabel("F (T)"); ax.set_ylabel("FFT (norm, offset)")
ax.legend(fontsize=7); ax.grid(alpha=0.3)
ax.set_title("run 20 (τ=300 ms, δF=0.72 in this window): ML pocket resolved at n=−1.74")
plt.show()
print("4.4 + 16.4 = 20.8 ≈ 1.14·F_L(1.74) = 20.6  — Luttinger closes with the pair")
print("16.4−4.4 = 12.0 (mixing line). Breakdown-sum reading of 16.4 excluded by its")
print("measured mass 0.049 < m_ML+m_BL (a sum orbit cannot be lighter than a parent).")
