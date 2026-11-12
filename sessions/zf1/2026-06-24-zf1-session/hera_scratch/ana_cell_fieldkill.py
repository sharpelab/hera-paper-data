# Runs data/10-11 — Step 3 field-kill (Rxx vs B_perp) at the candidate, zero DC bias
def _fk(rid):
    g = run(rid)
    B = g.col_at(g.col_indices("magnet_field")[0]) * 1e3      # mT (controller)
    R = (g.col_at(g.col_indices("sr830_3_X")[0]) / 100.0) / 1e-9
    return B, R, g.col("T")
bA, rA, tA = _fk(10); bB, rB, tB = _fk(11)
print("T held at base: A[%.4f,%.4f] B[%.4f,%.4f] K" % (tA.min(), tA.max(), tB.min(), tB.max()))
print("Rxx far-field ~%.0f ohm; near controller-0 ~%.0f ohm (pristine zero-field dip was ~7 ohm)" %
      (np.median(np.concatenate([rA[bA > 40], rB[bB < -40]])), min(rA.min(), rB.min())))
fig, ax = plt.subplots(figsize=(9, 5))
ax.plot(bB, rB, ".-", ms=3, label="pass B (-50->0)")
ax.plot(bA, rA, ".-", ms=3, label="pass A (+50->0)")
ax.set_xlabel("controller B_perp (mT)"); ax.set_ylabel("4T Rxx (ohm)")
ax.set_title("data/10-11: field-kill at n=-0.55, D=-0.6 (zero DC bias)")
ax.legend(); ax.grid(alpha=0.3); plt.tight_layout(); plt.show()
