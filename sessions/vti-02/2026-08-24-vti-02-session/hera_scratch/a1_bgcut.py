"""Run 1 (bg-cut, sr1 re-ranged) vs run 0 (clipped): CNP position, Rxx peak height,
hysteresis, noise floor at the metallic end."""
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import scipy.constants as cst

from hera.analysis import open_run, GateCalibration

here = Path(__file__).resolve().parent.parent
r0, r1 = open_run(here / "data" / "0"), open_run(here / "data" / "1")

cal = GateCalibration.from_thicknesses(9.5e-9, 11e-9, 0.0)
print(f"c_tg = {cal.c_tg:.4g} F/m^2  -> {cal.c_tg / cst.e * 1e-16:.4g} e12 cm^-2 per V")
print(f"c_bg = {cal.c_bg:.4g} F/m^2  -> {cal.c_bg / cst.e * 1e-16:.4g} e12 cm^-2 per V")
print(f"CNP-line slope dVbg/dVtg = {-cal.c_tg / cal.c_bg:.4f}")


def get(r):
    mc = r.meta["measurement_config"]
    v = r.col("k_2400_bg_volt")
    I = r.col("sr0_X") / mc["sr0_gain"]
    Vx, Vy = r.col("sr1_X"), r.col("sr1_Y")
    return v, I, Vx / I, Vy / I     # R from the MEASURED current, not nominal bias


v0, I0, R0, Q0 = get(r0)
v1, I1, R1, Q1 = get(r1)
o1 = np.argsort(v1)                      # run 1 was swept in reverse

print(f"\nrun 0 (sens 2 uV, tau 0.3 s): Rxx {R0.min():.1f} .. {R0.max():.1f} ohm  "
      f"[CLIPPED above ~218]")
print(f"run 1 (sens 1 mV, tau 0.1 s): Rxx {R1.min():.1f} .. {R1.max():.1f} ohm")

k1 = int(np.argmax(R1))
print(f"\nCNP from Rxx peak (run 1) : V_bg = {v1[k1]:+.4f} V, Rxx_peak = {R1[k1]:.1f} ohm")
k0i = int(np.argmin(np.abs(I0)))
print(f"CNP from I dip     (run 0) : V_bg = {v0[k0i]:+.4f} V")
k1i = int(np.argmin(np.abs(I1)))
print(f"CNP from I dip     (run 1) : V_bg = {v1[k1i]:+.4f} V  -> hysteresis "
      f"{abs(v1[k1i] - v0[k0i]) * 1e3:.0f} mV between up- and down-sweeps")

# metallic-end noise: high-|n| plateau, run 1 vs run 0
for tag, v, R in (("run 0", v0, R0), ("run 1", v1, R1)):
    m = v > 1.5
    print(f"{tag} metallic end (V_bg>1.5): Rxx = {R[m].mean():.2f} +/- {R[m].std():.2f} ohm "
          f"({100 * R[m].std() / R[m].mean():.2f} % scatter, n={m.sum()})")

# quadrature -> probe-loading / phase check
print(f"\nrun 1 quadrature: |Y/X| median {np.median(np.abs(Q1 / R1)):.4f}, "
      f"max {np.max(np.abs(Q1 / R1)):.4f}  (phase drift near the CNP would show here)")

n1 = cal.density(0.0, v1) * 1e-16                      # 1e12 cm^-2, before offset
n_off = -cal.density(0.0, v1[k1]) * 1e-16
print(f"\nn_offset from the Rxx peak: {n_off:+.4f} e12 cm^-2 (intrinsic doping at V=0)")
D_cnp = cal.displacement_field(0.0, v1[k1]) * 1e-9
print(f"D at this CNP crossing    : {D_cnp:+.4f} V/nm  (this cut crosses the CNP at ~zero D)")

fig, ax = plt.subplots(3, 1, figsize=(8.5, 9.5), sharex=True)
ax[0].plot(v0, R0, ".-", ms=3, lw=0.8, label="run 0  sens 2 uV (clipped)")
ax[0].plot(v1[o1], R1[o1], ".-", ms=3, lw=0.8, label="run 1  sens 1 mV")
ax[0].axhline(218, ls=":", c="r", lw=0.8, label="run 0 clip level")
ax[0].axvline(v1[k1], ls="--", c="k", lw=0.8, label=f"CNP {v1[k1]:+.3f} V")
ax[0].set_ylabel("Rxx = Vxx / I_meas  (ohm)"); ax[0].legend(fontsize=7)
ax[0].set_title(f"vti-02  bg-cut  V_tg=0, B=0, T=1.17 K   —   Rxx peak {R1[k1]:.0f} ohm at D~0")

ax[1].plot(v1[o1], R1[o1], ".-", ms=3, lw=0.8)
ax[1].set_yscale("log"); ax[1].set_ylabel("Rxx (ohm), log")
ax[1].axvline(v1[k1], ls="--", c="k", lw=0.8)

ax[2].plot(v0, I0 * 1e9, ".-", ms=3, lw=0.8, label="run 0")
ax[2].plot(v1[o1], I1[o1] * 1e9, ".-", ms=3, lw=0.8, label="run 1")
ax[2].set_ylabel("I_drain (nA)"); ax[2].set_xlabel("V_bg (V)  [V_tg = 0]")
ax[2].axvline(v1[k1], ls="--", c="k", lw=0.8); ax[2].legend(fontsize=7)

secx = ax[0].secondary_xaxis("top", functions=(
    lambda vb: cal.density(0.0, vb) * 1e-16 + n_off,
    lambda n: (n - n_off) * 1e16 / cal.c_bg * cst.e))
secx.set_xlabel("n  (1e12 cm^-2, geometry prior)")

fig.tight_layout()
out = here / "hera_scratch" / "a1_bgcut.png"
fig.savefig(out, dpi=110)
print(f"\nwrote {out}")
