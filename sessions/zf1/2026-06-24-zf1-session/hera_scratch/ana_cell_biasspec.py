# Run data/9 — Step 2 bias spectroscopy at the candidate (n=-0.55, D=-0.6)
g9 = run(9); print(summarize_run(g9))
vdc = g9.col_at(g9.col_indices("dc205_1_voltage")[0])
idc = vdc / 1e8 * 1e9                                  # nA  (I_dc = V_dc / 100 MOhm)
dvdi = (g9.col_at(g9.col_indices("sr830_3_X")[0]) / 100.0) / 1e-9   # 4T dV/dI [ohm]
half = len(vdc) // 2
floor = np.median(np.sort(dvdi)[:10]); norm = np.median(dvdi[np.abs(idc) > 120])
thr = floor + 0.5 * (norm - floor)
f_idc, f_r = idc[:half], dvdi[:half]
def _ic(mask):
    ii = np.abs(f_idc[mask]); rr = f_r[mask]; o = np.argsort(ii)
    ii, rr = ii[o], rr[o]
    return ii[np.argmax(rr > thr)] if (rr > thr).any() else np.nan
ic_p, ic_n = _ic(f_idc > 0), _ic(f_idc < 0)
print(f"zero-bias dV/dI = {dvdi[np.argmin(np.abs(idc))]:.2f} ohm; normal ~ {norm:.1f} ohm; Ic+ ~ {ic_p:.1f} nA, Ic- ~ {ic_n:.1f} nA")
fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(idc[:half], dvdi[:half], ".-", ms=3, label="fwd (-150->+150 nA)")
ax.plot(idc[half:], dvdi[half:], ".-", ms=3, alpha=0.6, label="bwd")
for s in (ic_p, -ic_n):
    ax.axvline(s, color="g", ls=":", lw=1)
ax.set_xlabel("I_dc (nA)"); ax.set_ylabel("dV/dI 4T (ohm)")
ax.set_title("data/9: dV/dI vs I_dc @ n=-0.55, D=-0.6 (zero-bias dip + switching peaks at +/-Ic)")
ax.legend(); ax.grid(alpha=0.3); plt.tight_layout(); plt.show()
