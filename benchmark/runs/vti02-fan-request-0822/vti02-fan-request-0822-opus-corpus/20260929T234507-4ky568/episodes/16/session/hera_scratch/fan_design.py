"""Landau-fan design arithmetic for the stacking call (investigation Step 4).
Scratch: grid, Nyquist, delta-F, dynamic range, wall-clock.
"""
import numpy as np
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
from hera.analysis import open_run, luttinger_frequency

CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
TG = (-0.3, 1.0); BG = (-1.3, 2.0)

N_HI, N_LO = 3.20, 1.20          # 1e12 cm^-2
B_LO, B_MID, B_HI = 1.0, 3.0, 10.0
DINV_A, DINV_B = 0.0101, 0.0040  # 1/T

h, e = 6.62607015e-34, 1.602176634e-19

# ---------- fast axis ----------
dn_ray = 4 * e / h * B_LO / 1e4 / 1e12     # 1e12 cm^-2 per ray at B_LO
N_n = int(np.ceil((N_HI - N_LO) / (dn_ray / 2))) + 1
ns = np.linspace(N_HI, N_LO, N_n)
Vtg, Vbg = calc_gate_voltages(ns, 0.0 * ns, CAL["c_tg"], CAL["c_bg"],
                              CAL["n_offset"], CAL["D_offset"])
print(f"ray spacing at B_lo={B_LO} T: dn = {dn_ray:.4f}e12 cm^-2")
print(f"N_n = {N_n}, dn_grid = {(N_HI-N_LO)/(N_n-1):.4f}e12 "
      f"({dn_ray/((N_HI-N_LO)/(N_n-1)):.2f} pts/ray at {B_LO} T)")
print(f"V_tg {Vtg.max():+.4f} .. {Vtg.min():+.4f} V (limits {TG});  "
      f"V_bg {Vbg.max():+.4f} .. {Vbg.min():+.4f} V (limits {BG})")
print(f"  headroom: TG {TG[1]-Vtg.max():+.4f} V to cap, BG {BG[1]-Vbg.max():+.4f} V")
assert Vtg.min() >= TG[0] and Vtg.max() <= TG[1]
assert Vbg.min() >= BG[0] and Vbg.max() <= BG[1]
print(f"  roundtrip n,D at ends: {calc_nD(Vtg[0], Vbg[0], CAL['c_tg'], CAL['c_bg'], CAL['n_offset'], CAL['D_offset'])}"
      f" / {calc_nD(Vtg[-1], Vbg[-1], CAL['c_tg'], CAL['c_bg'], CAL['n_offset'], CAL['D_offset'])}")
dVtg = abs(Vtg[0] - Vtg[-1]); dVbg = abs(Vbg[0] - Vbg[-1])
print(f"  flyback: dV_tg {dVtg:.3f} V, dV_bg {dVbg:.3f} V at 5 mV/6 ms -> "
      f"{max(dVtg, dVbg)/0.005*0.006:.2f} s")

# ---------- slow axis ----------
invA = np.arange(1 / B_LO, 1 / B_MID - 1e-12, -DINV_A)
invB = np.arange(1 / B_MID, 1 / B_HI - 1e-12, -DINV_B)
inv = np.concatenate([invA, invB, [1 / B_HI]])
B_vec = np.sort(1 / inv)
N_B = len(B_vec)
print(f"\nB grid: {N_B} rows, {B_vec[0]:.3f} -> {B_vec[-1]:.3f} T "
      f"(leg A {len(invA)} rows <= {B_MID} T, leg B {N_B-len(invA)} rows)")
print(f"  dB at low edge {np.diff(B_vec)[0]*1e3:.1f} mT, at high edge {np.diff(B_vec)[-1]*1e3:.0f} mT")
F_L_hi = float(luttinger_frequency(N_HI * 1e16))
print(f"  F_L(n_hi) = {F_L_hi:.1f} T -> Nyquist needs d(1/B) <= {1/(2*F_L_hi):.4f}, "
      f"1/3 -> {1/(3*F_L_hi):.4f}; leg A uses {DINV_A}")
print(f"  leg A Nyquist ceiling {1/(2*DINV_A):.0f} T; leg B {1/(2*DINV_B):.0f} T")
span = 1 / B_LO - 1 / B_HI
print(f"  1/B span {span:.3f} 1/T -> dF = {1/span:.2f} T (half-record {2/span:.2f} T)")
for f, lbl in ((7.3, "partner"), (22.3, "heavy"), (29.4, "F_L-band")):
    print(f"    {lbl} {f} T: {f*span:.1f} periods in record")
# partner resolvability across the n window (5 periods)
f_par_min = 5 / span
print(f"  5-period floor: F_partner >= {f_par_min:.1f} T -> with partner ~0.22 F_L, "
      f"n >= {f_par_min/0.22/ (F_L_hi/N_HI):.2f}e12")

# ---------- dynamic range ----------
r5 = open_run("data/5")
vtg5 = np.asarray(r5.col("k_2400_tg_volt"), float)
vbg5 = np.asarray(r5.col("k_2400_bg_volt"), float)
R5 = np.asarray(r5.col("sr1_X"), float) / (np.asarray(r5.col("sr0_X"), float) / -1e6)
n5, D5 = calc_nD(vtg5, vbg5, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
print("\nR(B=0) along D=0 from run 5 (|D| < 0.01 V/nm):")
mD = np.abs(D5) < 0.01
for nq in (1.2, 1.6, 2.0, 2.6, 3.2):
    sel = mD & (np.abs(n5 - nq) < 0.08)
    if sel.sum():
        print(f"   n={nq:+.2f}e12: R = {np.median(R5[sel]):7.1f} Ohm  (N={sel.sum()})")

r6 = open_run("data/6")
B6 = np.asarray(r6.col("magnet_field"), float)
R6 = np.asarray(r6.col("sr1_X"), float) / (np.asarray(r6.col("sr0_X"), float) / -1e6)
lo = np.abs(B6) < 0.1; hi = B6 > 9.0
print(f"run 6 (n=3.2e12) MR: R(B~0) {np.median(R6[lo]):.1f} -> R(B>9T) max {R6[hi].max():.1f} "
      f"Ohm  (x{R6[hi].max()/np.median(R6[lo]):.1f})")
r7 = open_run("data/7")
B7 = np.asarray(r7.col("magnet_field"), float)
R7 = np.asarray(r7.col("sr1_X"), float) / (np.asarray(r7.col("sr0_X"), float) / -1e6)
lo7 = B7 < 0.5; hi7 = B7 > 9.0
print(f"run 7 (n=-1.2e12) MR: R(0.3T) {np.median(R7[lo7]):.1f} -> R(>9T) max {R7[hi7].max():.1f} "
      f"Ohm  (x{R7[hi7].max()/np.median(R7[lo7]):.1f})")

# ---------- wall clock ----------
TAU, DWELL = 0.10, 1.0
per_pt = DWELL + 0.10
row_meas = N_n * per_pt
flyback = max(dVtg, dVbg) / 0.005 * 0.006
SLOW_DELAY = 1.0
settle = 3.0
ramp = (B_HI - B_LO) / 0.137
pos = (B_LO - 0.0) / 0.137
total = pos + ramp + N_B * (row_meas + flyback + SLOW_DELAY + settle) / 60
print(f"\nwall clock: per-pt {per_pt:.2f} s, row {row_meas:.0f} s meas + "
      f"{flyback+SLOW_DELAY+settle:.1f} s turnaround/settle")
print(f"  position 0->{B_LO} T {pos:.0f} min + ramp {ramp:.0f} min + "
      f"rows {N_B*(row_meas+flyback+SLOW_DELAY+settle)/60:.0f} min = {total:.0f} min "
      f"= {total//60:.0f} h {total%60:.0f} m")
print(f"  +10% margin -> {total*1.1//60:.0f} h {total*1.1%60:.0f} m")
print(f"  grid {N_B} x {N_n} = {N_B*N_n} points")
