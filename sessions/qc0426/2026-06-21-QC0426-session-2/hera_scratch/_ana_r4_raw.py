# Run 4 (electron) raw + bg-sub vs 1/B
g4 = run(4)
print(summarize_run(g4))
B = g4.col("magnet_field"); i = g4.col("sr0_X") / (-1e6)
R1 = g4.col("sr1_X") / i; R2 = g4.col("sr2_X") / i
o = np.argsort(B); B, R1, R2 = B[o], R1[o], R2[o]
print(f"Rxx sr1 {R1.min():.0f}..{R1.max():.0f} ohm ; max|V|={(np.abs(R1)*np.abs(i)).max()*1e6:.1f} uV (FS=100, no clip)")
fig, ax = plt.subplots(1, 2, figsize=(13, 4.5))
ax[0].plot(B, R1, ".-", ms=3, lw=0.7, label="sr1 T3-T4"); ax[0].plot(B, R2, ".-", ms=3, lw=0.7, label="sr2 B4-B5")
ax[0].set_xlabel("B [T]"); ax[0].set_ylabel("Rxx [ohm]"); ax[0].legend()
ax[0].set_title("Run 4 raw Rxx(B) ELECTRON n=+3.5e12 D=0")
for ch, R, c in [("sr1", R1, "C0"), ("sr2", R2, "C1")]:
    m = B >= 1.5
    coef = np.polyfit(B[m], R[m], 4); dR = R[m] - np.polyval(coef, B[m])
    ax[1].plot(1/B[m], dR, ".-", ms=3, lw=0.8, color=c, label=ch)
ax[1].set_xlabel("1/B [1/T]"); ax[1].set_ylabel("dRxx [ohm]"); ax[1].legend(); ax[1].grid(alpha=0.3)
ax[1].set_title("bg-sub vs 1/B (B>1.5T) — clean periodic SdH")
plt.show()
