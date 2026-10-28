"""Landau-fan design arithmetic + dual model overlay (ABAB vs trilayer ML+BL).

Design-time check that the fan window separates the template families, plus
the landau-fan step-1 numbers: B_lo (measured onset), Nyquist on both axes,
delta_F, N_B/N_n, wall-clock, gate spans, dynamic range.
"""
import sys
import json

import numpy as np
import scipy.constants as cst

sys.path.insert(0, "/home/hera/measurement_env/hera/models/tetralayer_fs_count")
import fs_count_b0 as M4  # noqa: E402

sys.path.insert(0, "/home/hera/measurement_env/hera/models/trilayer_fs_count")
del sys.modules["fs_count_b0"]
import fs_count_b0 as M3  # noqa: E402

h, e = cst.h, cst.e
FL = lambda n12: abs(n12) * 1e16 * h / (4 * e)  # noqa: E731   n12 in 1e12 cm^-2

# ---- session calibration (run 5) and the measured global scale from run 6
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
F_MEAS = (7.11, 22.26)                 # run-6 resolved pair, nominal n = +3.20e12
SUM = sum(F_MEAS)
SCALE = SUM / FL(3.20)                 # global density rescale pinned on the pair
print(f"run 6 pair {F_MEAS} T, sum {SUM:.2f} T, F_L(nom 3.20) {FL(3.20):.2f} T")
print(f"  -> global density scale = {SCALE:.3f}  (in the 0.8-1.2 plausible band)")
print(f"  measured partition  f_l/sum = {F_MEAS[0]/SUM:.3f}, ratio f_h/f_l = {F_MEAS[1]/F_MEAS[0]:.3f}")
print(f"  intermod bookkeeping: 2f_l = {2*F_MEAS[0]:.2f} (seen 14.22), f_h-f_l = "
      f"{F_MEAS[1]-F_MEAS[0]:.2f} (seen 15.46), f_h+f_l = {SUM:.2f} (seen 29.37 ~ F_L*scale)")

# ---- fan window (nominal calibration units)
N_LO, N_HI = 2.00, 3.20
B_LO, B_MAX = 0.60, 10.0
print(f"\n=== dual overlay over the fan window, nominal n {N_LO}..{N_HI} (true = scale x nominal) ===")
print("nom n | true n | F_L,nom |  ABAB(4L) f_l   f_h  ratio | ABC-tri(3L) f_s  f_b ratio | ABCA f")
for nn in np.linspace(N_LO, N_HI, 7):
    nt = SCALE * nn
    n_si = nt * 1e16
    _, o4 = M4.abab_fs(n_si)
    f4 = sorted(x[0] for x in o4)
    try:
        _, o3 = M3.aba_fs(n_si)
        f3 = sorted(x[0] for x in o3)
        s3 = f"{f3[0]:6.2f} {f3[-1]:6.2f} {f3[-1]/f3[0]:6.2f}" if len(f3) > 1 else f"{f3}"
    except Exception as ex:
        s3 = f"ERR {ex}"[:28]
    print(f"{nn:5.2f} | {nt:6.2f} | {FL(nn):7.2f} | {f4[0]:6.2f} {f4[-1]:6.2f} "
          f"{f4[-1]/f4[0]:6.2f} | {s3} | {FL(nt):6.2f}")

# ---- design numbers
print("\n=== landau-fan step 1 design numbers ===")
F_fast = FL(N_HI)                              # fastest tone the grid must not alias
F_harm2 = 2 * F_MEAS[1]                        # 2nd harmonic of the measured heavy tone
dinvB_nyq2 = 1 / (2 * F_fast)
dinvB_harm = 1 / (2 * F_harm2)
span = 1 / B_LO - 1 / B_MAX
print(f"F_L(n_max nominal {N_HI}) = {F_fast:.2f} T; 2*f_heavy(measured) = {F_harm2:.2f} T")
print(f"Nyquist d(1/B): on F_L {dinvB_nyq2:.5f}; on 2*f_heavy {dinvB_harm:.5f} 1/T")
for N_B in (105, 130, 157, 175):
    d = span / (N_B - 1)
    print(f"  N_B={N_B:4d}: d(1/B)={d:.5f} -> F_Nyq={1/(2*d):6.1f} T "
          f"({'OK' if 1/(2*d) > F_harm2 else 'FOLDS 2f_h'})")
N_B = 157
dinvB = span / (N_B - 1)
dF = 1 / span
print(f"chosen N_B={N_B}, d(1/B)={dinvB:.5f}, F_Nyq={1/(2*dinvB):.1f} T")
print(f"1/B span = {span:.4f} 1/T  ->  delta_F = {dF:.3f} T")

dn_ray = 4 * (e / h) * B_LO * 1e-16
print(f"\nray spacing at B_lo={B_LO} T: dn = {dn_ray:.4f}e12 -> Nyquist dn <= {dn_ray/2:.4f}e12")
for N_n in (42, 44, 47):
    d = (N_HI - N_LO) / (N_n - 1)
    print(f"  N_n={N_n}: dn={d:.4f}e12 -> {dn_ray/d:.2f} pts/ray ({'OK' if dn_ray/d >= 2 else 'UNDER'})")
N_n = 44
dn = (N_HI - N_LO) / (N_n - 1)

print(f"\nlight-tone period count (measured-scaled f_l = 1.15 x model):")
for nn in (N_LO, 2.2, 2.5, 2.8, N_HI):
    _, o4 = M4.abab_fs(SCALE * nn * 1e16)
    fl_model = sorted(x[0] for x in o4)[0]
    fl = 1.15 * fl_model
    print(f"  nominal n={nn:.2f}: f_l_model={fl_model:5.2f} -> expect {fl:5.2f} T, "
          f"periods over the record = {fl*span:5.2f}, f_l/delta_F = {fl/dF:5.2f}")

# ---- B-window split (mandatory F_L-tone origin Verify)
inv_mid = 0.5 * (1 / B_LO + 1 / B_MAX)
B_mid = 1 / inv_mid
half_span = 1 / B_LO - inv_mid
print(f"\nB-window split at 1/B midpoint: B_mid = {B_mid:.2f} T; each half 1/B span "
      f"{half_span:.3f} -> delta_F_half = {1/half_span:.2f} T")
print(f"  heavy(22.26) vs F_L-tone(29.37) separation {29.37-22.26:.2f} T vs 2*delta_F_half "
      f"{2/half_span:.2f} T -> {'resolvable' if (29.37-22.26) > 2/half_span else 'NOT resolvable'}")

# ---- gate axis
sys.path.insert(0, "/home/hera/measurement_env")
from sharpelab_nb.gates import calc_gate_voltages, calc_nD  # noqa: E402

ns = np.linspace(N_HI, N_LO, N_n)      # descend n: start at the run-6 spot (top column)
Vtg, Vbg = calc_gate_voltages(ns, 0.0 * ns, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
print(f"\ngate axis: Vtg {Vtg.min():+.4f}..{Vtg.max():+.4f} (limits -0.3/+1.0), "
      f"Vbg {Vbg.min():+.4f}..{Vbg.max():+.4f} (limits -1.3/+2.0)")
print(f"  spans: dVtg {np.ptp(Vtg):.4f} V, dVbg {np.ptp(Vbg):.4f} V; step {np.ptp(Vtg)/(N_n-1)*1e3:.1f} / "
      f"{np.ptp(Vbg)/(N_n-1)*1e3:.1f} mV")
print(f"  flyback at 5 mV/6 ms: {np.ptp(Vbg)/0.005*0.006:.2f} s (bg, the longer axis)")
nchk, Dchk = calc_nD(Vtg, Vbg, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
print(f"  roundtrip: n {nchk.min():+.3f}..{nchk.max():+.3f}, |D| max {np.abs(Dchk).max():.2e} V/nm")

# ---- wall clock
FAST_DELAY, SLOW_DELAY = 1.8, 3.0
t_read = 1.172 - 1.0                   # run-5 gatemap: 1.172 s/pt at fast_delay 1.0
t_pt = FAST_DELAY + t_read
grid = N_B * N_n * t_pt
B_vec = 1.0 / np.linspace(1 / B_LO, 1 / B_MAX, N_B)
ramp = np.abs(np.diff(B_vec)).sum() / 0.137 * 60 + B_LO / 0.137 * 60
settle = N_B * 3.0
turn = N_B * (np.ptp(Vbg) / 0.005 * 0.006 + SLOW_DELAY)
tot = grid + ramp + settle + turn
print(f"\n=== wall clock (t_pt = {t_pt:.3f} s from run-5 1.172 s/pt at fast_delay 1.0) ===")
print(f"  grid      {N_B} x {N_n} x {t_pt:.2f} s = {grid/3600:5.2f} h")
print(f"  field ramp (0 -> {B_LO} then {B_LO} -> {B_MAX} T at 0.137 T/min) = {ramp/3600:5.2f} h")
print(f"  per-row driver settle (3 s)                                    = {settle/3600:5.2f} h")
print(f"  row turnaround (flyback + slow_delay {SLOW_DELAY} s)              = {turn/3600:5.2f} h")
print(f"  TOTAL {tot/3600:.2f} h  -> quote {tot*1.10/3600:.2f} h with the +10% session bias")
print(f"  B rows: {B_vec[0]:.3f} .. {B_vec[-1]:.3f} T; coarsest dB = {np.abs(np.diff(B_vec)).max():.4f} T "
      f"(at high B), finest {np.abs(np.diff(B_vec)).min():.4f} T")

# ---- dynamic range: worst corner = n_min x B_max
print("\n=== dynamic range (fixed sr1 sensitivity) ===")
print("  R(B=0, D=0) from run 5:  n=+1.85e12 -> 79 Ohm;  n=+3.20e12 -> 56 Ohm")
print("  spot-check high-B maxima: run 6 (n=+3.20) 530 Ohm = 10.5% of 5 kOhm FS;")
print("                            run 7 (n=-1.20, R0=105) 587 Ohm = 11.6% FS")
print("  worst-corner estimate n=+1.85e12 @ 10 T: 79 x ~12 (MR/QH factor) ~ 950 Ohm")
print("  sr1 50 uV -> R_FS = 50e-6/9.9e-9 = %.0f Ohm -> ~%.1fx headroom" % (50e-6/9.9e-9, (50e-6/9.9e-9)/950))

json.dump(dict(N_B=N_B, N_n=N_n, B_LO=B_LO, B_MAX=B_MAX, N_LO=N_LO, N_HI=N_HI,
               dinvB=dinvB, dF=dF, dn=dn, scale=SCALE, hours=tot/3600),
          open("hera_scratch/fan_design.json", "w"), indent=1)
