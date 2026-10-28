# Run 0 — derived Rxx = V / I_bias, CNP peak per channel, gate leakage
i = g.col("sr0_X") / (-1e6)          # A (Ithaco gain -1e6)
Ibias = np.median(i)
R1, R2 = v1 / i, v2 / i
for nm, R in [("sr1 T3-T4", R1), ("sr2 B4-B5", R2)]:
    k = np.argmax(R)
    print(f"{nm}: CNP peak {R[k]:.0f} ohm at V_bg={vbg[k]:.3f} V | min {R.min():.0f} ohm")
print(f"I_bias = {Ibias*1e9:.2f} nA (current-bias, stable through CNP)")
for c in ("k_2400_curr", "k_2410_curr"):
    print(f"{c} |max| = {np.abs(g.col(c)).max()*1e9:.2f} nA (1uA-range noise floor)")
plt.figure(figsize=(7, 4))
plt.plot(vbg, R1, label="sr1 Rxx (T3-T4)")
plt.plot(vbg, R2, label="sr2 Rxx (B4-B5)")
plt.axvline(vbg[np.argmax(R1)], ls=":", c="k", lw=0.8, label=f"CNP {vbg[np.argmax(R1)]:.2f} V")
plt.xlabel("V_bg [V]"); plt.ylabel("R [ohm]"); plt.legend()
plt.title("Run 0 - Rxx(V_bg) @ TG=0 (pure-BG cut, finite small D)")
plt.show()
