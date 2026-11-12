# Run 3 (clean) raw — run 2 clipped >4T at sens 1e-5, superseded
g3 = run(3)
print(summarize_run(g3))
B = g3.col("magnet_field"); i = g3.col("sr0_X") / (-1e6)
R1 = g3.col("sr1_X") / i; R2 = g3.col("sr2_X") / i
o = np.argsort(B); B, R1, R2 = B[o], R1[o], R2[o]
print(f"Rxx sr1 {R1.min():.0f}..{R1.max():.0f} ohm ; max|V|={(np.abs(R1)*np.abs(i)).max()*1e6:.1f} uV (FS=100, no clip)")
plt.figure(figsize=(7, 4))
plt.plot(B, R1, ".-", ms=3, lw=0.7, label="sr1 T3-T4")
plt.plot(B, R2, ".-", ms=3, lw=0.7, label="sr2 B4-B5")
plt.xlabel("B [T]"); plt.ylabel("Rxx [ohm]"); plt.legend()
plt.title("Run 3 raw Rxx(B) - HOLE n=-3.5e12, D=0 (clean sens 1e-4)")
plt.show()
