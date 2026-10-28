# Gate C — runs 0-3 (gate-current-sanity-check). Raw first: R = (sr1_X/gain)/I_drain per point, gate currents.
from hera.analysis import resolve_channels
fig, ax = plt.subplots(2, 2, figsize=(11, 7))
peaks = {}
for i in range(4):
    r = run(i)
    ch = {c.cid: c for c in resolve_channels(r.meta)}
    V = r.col(r.swept_axis)
    I = r.col("sr0_X") / ch["sr0"].gain
    R = np.abs((r.col("sr1_X") / ch["sr1"].gain) / I)
    i_tg, i_bg = r.col("k_2400_tg_curr"), r.col("k_2400_bg_curr")
    gate = r.swept_axis.replace("_volt", "")
    k = np.argmax(R); peaks[i] = (gate, V[k], R[k])
    print(f"run {i} {gate} {V[0]:+.2f}->{V[-1]:+.2f} V: R {R.min():.0f}-{R.max():.0f} Ohm (max at {V[k]:+.3f} V), "
          f"I_drain {I.min()*1e9:.2f}-{I.max()*1e9:.2f} nA, I_tg {i_tg.min()*1e12:+.0f}..{i_tg.max()*1e12:+.0f} pA, "
          f"I_bg {i_bg.min()*1e12:+.0f}..{i_bg.max()*1e12:+.0f} pA, T {r.col('T_sample').mean():.3f} K, interrupted={r.interrupted}")
    a = ax[0, 0] if "tg" in gate else ax[0, 1]
    a.plot(V, R, ".-", ms=3, label=f"run {i}"); a.set_xlabel(gate + " (V)"); a.set_ylabel("|Rxx| B_1-B_2 (Ohm)"); a.legend()
    b = ax[1, 0] if "tg" in gate else ax[1, 1]
    b.plot(V, i_tg * 1e12, ".-", ms=3, label=f"I_tg run {i}"); b.plot(V, i_bg * 1e12, ".-", ms=3, label=f"I_bg run {i}")
    b.set_xlabel(gate + " (V)"); b.set_ylabel("gate current (pA)"); b.legend(fontsize=7)
fig.suptitle("vti-02 gate C: gate-current-sanity-check, runs 0-3 (B = 0, Vsi = 0, other gate 0, T = 1.17 K)")
fig.tight_layout(); plt.show()
