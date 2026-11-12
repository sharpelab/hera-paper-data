# Runs data/5-8 — Step 1 locate: constant-D n-linecuts -> candidate
from sharpelab_nb.gates import stack_capacitance, calc_nD
c_tg = stack_capacitance([(23.6,3)]); c_bg = c_tg*1.1833
n_off = -calc_nD(0.1634, 0.0, c_tg, c_bg)[0]
cuts = {5:-0.7, 6:-0.6, 7:-0.5, 8:+0.5}
fig, ax = plt.subplots(figsize=(9,5))
for rid, D0 in cuts.items():
    g = run(rid)
    vtg = g.col_at(g.col_indices("k_tg_volt")[0]); vbg = g.col_at(g.col_indices("k_bg_volt")[0])
    R4 = (g.col_at(g.col_indices("sr830_3_X")[0]) / 100.0) / 1e-9
    n, D = calc_nD(vtg, vbg, c_tg, c_bg, n_offset=n_off)
    o = np.argsort(n)
    ax.plot(n[o], R4[o], ".-", ms=3, label=f"D={D0:+.2f} (run {rid})")
    if abs(D0+0.6) < 1e-6:
        k = int(np.argmin(R4)); print(f"D=-0.60 dip: R4={R4[k]:.2f} ohm at n={n[k]:.3f}e12 cm^-2 (Vtg={vtg[k]:.2f} Vbg={vbg[k]:.2f})")
ax.axvspan(-0.6, -0.4, color="k", alpha=0.07, label="prior n band")
ax.set_xlabel("n (1e12 cm^-2)"); ax.set_ylabel("4T Rxx (ohm)")
ax.set_title("Step-1 locate: constant-D n-linecuts (note D=-0.6 dip vs D=+0.5 peak)")
ax.legend(); ax.grid(alpha=0.3); ax.set_ylim(0, 220); plt.tight_layout(); plt.show()
