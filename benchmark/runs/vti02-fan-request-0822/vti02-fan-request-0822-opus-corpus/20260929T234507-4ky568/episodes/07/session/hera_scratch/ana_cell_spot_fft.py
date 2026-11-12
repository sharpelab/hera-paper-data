"""Runs 6-7 read: per-tone onset, 1/B FFT with a cutoff x bg_degree stability sweep,
peak set against F_L and the ABAB 0.28/0.72 template."""
import warnings

fig, ax = plt.subplots(2, 2, figsize=(14, 8.5))
tone_tbl = {}
for col, rid in enumerate((6, 7)):
    s = spot[rid]
    m = s["B"] >= s["b_valid"]
    Bv, Rv, F_L = s["B"][m], s["R"][m], s["F_L"]
    dB = np.median(np.diff(Bv))
    print(f"===== run {rid} ({s['label']}, n = {s['n']:+.2f}e12, F_L = {F_L:.2f} T) "
          f"| window B {Bv[0]:.2f}-{Bv[-1]:.1f} T, {len(Bv)} pts, dB {dB*1e3:.0f} mT "
          f"-> F_nyq {Bv[0]**2/(2*dB):.1f} T")

    # --- onset: per-tone, statistical (5-sigma-style) walk down from high B ---
    with warnings.catch_warnings(record=True) as wl:
        warnings.simplefilter("always")
        on = sdh_onset(Rv, Bv, b_lo=s["b_valid"], r_full_scale=R_FS)
    for w in wl:
        print("  ⚠", w.message)
    print(on.summary())
    tone_tbl[rid] = on

    # --- deg-5 background-subtracted trace in 1/B (raw-adjacent view) ---
    a = ax[0, col]
    a.plot(1 / Bv, Rv - np.polyval(np.polyfit(Bv, Rv, 5), Bv), lw=0.8)
    a.set_xlabel("1/B (1/T)"); a.set_ylabel(r"$\Delta R_{xx}$ ($\Omega$)")
    a.set_title(f"run {rid} — deg-5 B-space background removed")

    # --- FFT stability sweep: low-B cutoff x bg_degree ---
    a = ax[1, col]
    print("  FFT peaks  (F [T] | F/F_L | rel amp):")
    for cut in (s["b_valid"], 1.5, 2.0, 3.0):
        for deg in (3, 5, 7):
            f, spec = sdh_fft(Rv[:, None], Bv, b_range=(cut, Bv[-1]), bg_degree=deg,
                              log=False, nfft=4096)
            sp = spec[0]
            if deg == 5:
                a.plot(f, sp / sp.max(), lw=1.0, label=f"cutoff {cut:.2f} T")
            pk = [(round(float(f[i]), 1), round(float(f[i] / F_L), 3), round(float(sp[i] / sp.max()), 2))
                  for i in range(2, len(f) - 2)
                  if sp[i] > sp[i-1] and sp[i] > sp[i+1] and sp[i] > 0.15 * sp.max() and f[i] > 2]
            print(f"    cutoff {cut:>4.2f} T, bg_degree {deg}: {pk}")
    a.axvline(F_L, color="k", ls="--", lw=1.3, label=f"$F_L$ = {F_L:.1f} T")
    a.axvline(0.72 * F_L, color="r", ls=":", lw=1.1, label="ABAB 0.72 / 0.28 $F_L$")
    a.axvline(0.28 * F_L, color="r", ls=":", lw=1.1)
    a.set_xlim(0, 1.8 * F_L); a.set_xlabel("F (T)"); a.set_ylabel("|FFT| (normalised)")
    a.legend(fontsize=8); a.set_title(f"run {rid} — 1/B FFT vs $F_L$")
    print()
plt.tight_layout(); plt.show()

# --- model expectation at the electron spot, for the read below ---
print("model (hera/models/tetralayer_fs_count README key table, interpolated to n = +3.2e12):")
print("   ABAB  F = 7.2 / 25.9 T  (fractions 0.217 / 0.783; m* 0.027 / 0.060 m_e)")
print("   ABCA  F = 33.1 T = F_L  (singleton; m* 0.076 m_e)")
print(f"   record resolution dF = 1/(1/1.0 - 1/10.0) = {1/(1/1.0-1/10.0):.2f} T")
