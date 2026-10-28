"""Runs 6-7 raw: R_xx(B) from the TSV, gain-divided, full record + Nyquist-valid window."""
from hera.analysis import sdh_onset

I_BIAS = 10.0e-9                  # sr1 drive / 100 MOhm bias resistor
R_FS = 50e-6 / I_BIAS             # 5 kOhm full scale at the 50 uV sensitivity

SPOT = {6: dict(n=+3.20, label="electron", b_valid=1.00, sens=50e-6),
        7: dict(n=-1.20, label="hole",     b_valid=0.70, sens=50e-6)}

spot = {}
for rid, c in SPOT.items():
    r = run(rid)
    B = np.asarray(r.col("magnet_field"), float)
    R = np.asarray(r.col("sr1_X"), float) / I_BIAS            # sr1 gain = 1
    T = np.asarray(r.col("T_sample"), float)
    o = np.argsort(B)
    spot[rid] = dict(B=B[o], R=R[o], T=T[o], F_L=float(luttinger_frequency(abs(c["n"]) * 1e12 * 1e4)), **c)
    print(summarize_run(r))
    print(f"   R {R.min():.1f} .. {R.max():.1f} Ohm  (fill {np.abs(R).max()/R_FS:.3f} of {R_FS/1e3:.0f} kOhm FS)"
          f" | T_sample {T.min():.3f}-{T.max():.3f} K | F_L = {spot[rid]['F_L']:.2f} T\n")

fig, ax = plt.subplots(1, 2, figsize=(14, 4.2))
for a, rid in zip(ax, (6, 7)):
    s = spot[rid]
    m = s["B"] >= s["b_valid"]
    a.plot(s["B"], s["R"], lw=0.6, color="0.7", label="full record (coarse low-B leg)")
    a.plot(s["B"][m], s["R"][m], lw=0.8, color="C0", label=f"Nyquist-valid  B $\\geq$ {s['b_valid']:.2f} T")
    a.axhline(0, color="k", lw=0.5, ls=":")
    a.set_xlabel("B (T)"); a.set_ylabel(r"$R_{xx}$ ($\Omega$)"); a.legend(fontsize=8)
    a.set_title(f"run {rid} RAW — {s['label']}, n = {s['n']:+.2f}$\\times10^{{12}}$ cm$^{{-2}}$, D = 0, T = 1.2 K")
plt.tight_layout(); plt.show()
