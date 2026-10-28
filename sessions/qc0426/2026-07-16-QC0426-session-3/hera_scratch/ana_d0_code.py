# Run 5 — D=0 designed-line cut: raw R(n) per channel
import scipy.constants as cst

r5 = run(5)
C_TG = cst.epsilon_0 * 3.0 / 15.6e-9
RATIO, N_OFF = 1.2839, -2.407e14
vtg5, vbg5 = r5.col_at(1), r5.col_at(2)
n5 = ((C_TG * vtg5 + RATIO * C_TG * vbg5) / cst.e + N_OFF) * 1e-16  # 1e12 cm^-2

fig, ax = plt.subplots(figsize=(9, 4.5))
for ch, lbl in [("sr1_X", "sr1 T3-T4"), ("sr2_X", "sr2 B4-B5"), ("sr3_X", "sr3 T5-B6 (xy)")]:
    ax.plot(n5, r5.col(ch) / 5e-9, lw=0.9, label=lbl)
ax.set_yscale("symlog", linthresh=10)
ax.set_xlabel("n (1e12 cm$^{-2}$) along D = 0")
ax.set_ylabel("R = X/I (Ω)")
ax.legend()
ax.set_title("Run 5 — D = 0 line cut, B = 0 (run-4 calibration)")
fig.tight_layout()
for tgt in (-6, -3, 3, 6):
    j = np.argmin(np.abs(n5 - tgt))
    print(f"n={tgt:+d}e12: sr1 {r5.col('sr1_X')[j]/5e-9:6.1f} Ω, sr2 {r5.col('sr2_X')[j]/5e-9:6.1f} Ω")
j1 = np.argmax(np.abs(r5.col("sr1_X"))); j2 = np.argmax(np.abs(r5.col("sr2_X")))
print(f"sr1 peak at n={n5[j1]:+.2f}e12 ({abs(r5.col('sr1_X')[j1])/5e-9:.0f} Ω); "
      f"sr2 peak at n={n5[j2]:+.2f}e12 ({abs(r5.col('sr2_X')[j2])/5e-9:.0f} Ω)")
