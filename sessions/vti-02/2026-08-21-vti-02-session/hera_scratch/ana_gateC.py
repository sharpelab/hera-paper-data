# Gate C — gate-current-sanity-check, runs 0-3 (TG 0->+1, 0->-0.3; BG 0->+2, 0->-1.3 V; other gate 0, Si 0, B 0, 10 nA)
# Raw first: per leg, Rxx (sr1, unity gain, / I_bias), drain current (sr0 / gain), gate currents.
ids = [0, 1, 2, 3]
fig, axs = plt.subplots(len(ids), 3, figsize=(14, 11), squeeze=False)
summary = {}
for row, i in enumerate(ids):
    r = run(i)
    mc = r.meta["measurement_config"]
    gain = float(mc["sr0_gain"])
    ib = float(r.meta["instruments"]["sr1"]["snapshot"]["parameters"]["amplitude"]["value"]) / float(mc["bias_resistor"])
    x = r.col(r.swept_axis)
    rxx = r.col("sr1_X") / ib
    i0 = r.col("sr0_X") / gain
    itg, ibg = r.col("k_2400_tg_curr"), r.col("k_2400_bg_curr")
    summary[i] = dict(axis=r.swept_axis, vpk=float(x[np.argmax(rxx)]), rpk=float(rxx.max()), rmin=float(rxx.min()),
                      i0=(float(i0.min()), float(i0.max())), itg=float(np.abs(itg).max()), ibg=float(np.abs(ibg).max()),
                      dt=float(np.median(np.diff(r.col("time")))), T=(float(r.col("T_sample").min()), float(r.col("T_sample").max())))
    a = axs[row]
    a[0].plot(x, rxx); a[0].set_ylabel("R_xx sr1 [Ω]"); a[0].set_title(f"run {i}: {r.swept_axis}  (I_bias {ib*1e9:.0f} nA)")
    a[1].plot(x, i0 * 1e9); a[1].set_ylabel("I_drain sr0 [nA]")
    a[2].plot(x, itg * 1e12, label="I_tg"); a[2].plot(x, ibg * 1e12, label="I_bg"); a[2].set_ylabel("gate I [pA]"); a[2].legend()
    for ax in a: ax.set_xlabel(r.swept_axis + " [V]")
plt.tight_layout(); plt.show()
for i, d in summary.items():
    print(f"run {i} {d['axis']}: R_xx {d['rmin']:.0f}..{d['rpk']:.0f} Ω, peak at {d['vpk']:+.3f} V | I_drain {d['i0'][0]*1e9:.2f}..{d['i0'][1]*1e9:.2f} nA | "
          f"|I_tg|max {d['itg']*1e12:.0f} pA, |I_bg|max {d['ibg']*1e12:.0f} pA | {d['dt']:.2f} s/pt (NPLC 10 + 1 s) | T {d['T'][0]:.3f}-{d['T'][1]:.3f} K")
# CNP offset on the geometry prior from the two single-gate maxima (V_bg = 0 / V_tg = 0):
n_tg = cal.density(summary[1]["vpk"], 0.0); n_bg = cal.density(0.0, summary[3]["vpk"])
print(f"n at the R_xx maxima (geometry prior): TG-leg {n_tg*1e-16:+.2f}e12, BG-leg {n_bg*1e-16:+.2f}e12 cm^-2 -> n_offset ≈ {-(n_tg+n_bg)/2*1e-16:+.2f}e12 (to be replaced by the gatemap ridge fit)")
