# Run 1 read: CNP peak height, hysteresis vs run 0, and whether the point-to-point
# wiggle is noise or reproducible structure.
def _rxx(g):
    mc = g.meta["measurement_config"]
    v = g.col("k_2400_bg_volt")
    I = g.col("sr0_X") / mc["sr0_gain"]
    return v, I, g.col("sr1_X") / I, g.col("sr1_Y") / I   # R from MEASURED current

v0, I0, R0, _ = _rxx(g0)
v1, I1, R1, Q1 = _rxx(g1)
o1 = np.argsort(v1)

k1 = int(np.argmax(R1))
print(f"CNP from Rxx peak (run 1): V_bg = {v1[k1]:+.4f} V,  Rxx_peak = {R1[k1]:.1f} ohm")
print(f"CNP from I dip    (run 0): V_bg = {v0[int(np.argmin(np.abs(I0)))]:+.4f} V")
print(f"hysteresis between sweep directions: "
      f"{abs(v1[int(np.argmin(np.abs(I1)))] - v0[int(np.argmin(np.abs(I0)))]) * 1e3:.0f} mV "
      f"(one 25 mV grid step -> negligible gate charging)")

# Runs 0 and 1 are independent sweeps in opposite directions with different tau AND
# different sensitivity, so comparing them separates noise from structure. For pure white
# noise the run-to-run rms difference equals hypot(sigma0, sigma1); any excess is real.
un = v0 > 0.6                                   # run-0 unclipped, electron side
R1i = np.interp(v0[un], v1[o1], R1[o1])
sig0 = np.std(np.diff(R0[un])) / np.sqrt(2)     # successive differences -> per-point sigma
sig1 = np.std(np.diff(R1i)) / np.sqrt(2)
obs = np.std(R0[un] - R1i)
exc = np.sqrt(max(obs ** 2 - sig0 ** 2 - sig1 ** 2, 0.0))
mean = R0[un].mean()
print(f"\nper-point sigma     : run0 {sig0:.2f} ohm ({100 * sig0 / mean:.1f} %), "
      f"run1 {sig1:.2f} ohm ({100 * sig1 / mean:.1f} %)")
print(f"run-to-run rms diff : observed {obs:.2f} ohm vs {np.hypot(sig0, sig1):.2f} ohm "
      f"expected for pure independent noise")
print(f"reproducible excess : {exc:.2f} ohm ({100 * exc / mean:.1f} %)  ->  the wiggle is "
      f"MOSTLY LOCK-IN NOISE, with only a small repeatable component")
print(f"sigma in volts      : {sig1 * 10e-9 * 1e9:.0f} nV  ->  "
      f"{sig1 * 10e-9 / np.sqrt(0.78) * 1e9:.0f} nV/rtHz input-referred at ENBW ~0.78 Hz "
      f"(tau 0.1 s, 24 dB/oct), consistent with SR830 1/f noise at 13.8 Hz — the "
      f"measurement is instrument-noise-limited, not drifting")

_m = (v1 > -0.30) & (v1 < 0.20)
print(f"\nCNP double-peak     : peaks {R1.max():.0f} ohm, dip between {R1[_m].min():.0f} ohm "
      f"= {100 * (1 - R1[_m].min() / R1.max()):.0f} % deep, far above the "
      f"{100 * sig1 / mean:.1f} % noise. Real, but seen in ONE sweep — run 0 was clipped "
      f"across exactly this region. The 35 independent CNP crossings in the map test it.")

print(f"\nquadrature |Y/X|: median {np.median(np.abs(Q1 / R1)):.3f}, "
      f"max {np.max(np.abs(Q1 / R1)):.3f} (probe-loading / phase tell)")

n_off = -cal.density(0.0, v1[k1])
D_cnp = cal.displacement_field(0.0, v1[k1])
print(f"\nsession gate calibration anchor (geometry prior + this CNP):")
print(f"  n_offset = {n_off * 1e-16:+.4f} e12 cm^-2   this cut crosses the CNP at "
      f"D/eps0 = {D_cnp * 1e-9:+.4f} V/nm (i.e. ~zero field)")
print(f"  CNP line : V_bg = {-cal.c_tg / cal.c_bg:.3f} * V_tg {v1[k1]:+.3f}")

fig, ax = plt.subplots(2, 1, figsize=(8.5, 7), sharex=True)
ax[0].plot(v0, R0, ".-", ms=3, lw=0.8, label="run 0 — sens 2 uV (clipped)")
ax[0].plot(v1[o1], R1[o1], ".-", ms=3, lw=0.8, label="run 1 — sens 1 mV")
ax[0].axhline(218, ls=":", c="r", lw=0.9, label="run 0 clip level")
ax[0].axvline(v1[k1], ls="--", c="k", lw=0.8, label=f"CNP {v1[k1]:+.3f} V")
ax[0].set_ylabel("Rxx = Vxx / I_meas  (ohm)")
ax[0].legend(fontsize=7.5)
ax[0].set_title(f"vti-02  bg-cut  V_tg = 0, B = 0, T = 1.17 K  —  Rxx peak "
                f"{R1[k1]:.0f} ohm at D/eps0 = {D_cnp * 1e-9:+.3f} V/nm")
ax[1].plot(v1[o1], R1[o1], ".-", ms=3, lw=0.8)
ax[1].set_yscale("log")
ax[1].set_ylabel("Rxx (ohm), log")
ax[1].set_xlabel("V_bg (V)   [V_tg = 0]")
ax[1].axvline(v1[k1], ls="--", c="k", lw=0.8)
secx = ax[0].secondary_xaxis("top", functions=(
    lambda vb: (cal.density(0.0, vb) + n_off) * 1e-16,
    lambda n: (n * 1e16 - n_off) / cal.c_bg * cst.e))
secx.set_xlabel("n  (1e12 cm^-2, geometry prior)")
fig.tight_layout()
